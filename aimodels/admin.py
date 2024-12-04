from django.contrib import admin
from django.utils.html import format_html
from django.db.models import F
from .models import AIModel, UserModel
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import User
from django.utils import timezone
from django.db import models
from django.http import JsonResponse
from django.urls import path
from django.db import transaction

@receiver(post_save, sender=User)
def create_user_model(sender, instance, created, **kwargs):
    """当新用户创建时，自动创建对应的用户模型配置"""
    if created:
        UserModel.objects.create(user=instance)

@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'model_name', 'model_type', 'platform', 'is_active', 'weight', 'created_at', 'updated_at']
    list_filter = ['model_type', 'platform', 'is_active']
    search_fields = ['model_name']
    ordering = ['weight']
    
    def has_add_permission(self, request):
        """允许添加新模型"""
        return True
    
    def get_fieldsets(self, request, obj=None):
        """根据是否是编辑页面返回不同的字段集"""
        if obj:  # 编辑页面
            return [
                ('基本信息', {
                    'fields': ['model_type', 'model_name', 'platform', 'original_model_name']
                }),
                ('控制选项', {
                    'fields': ['is_active', 'weight']
                }),
                ('配置信息', {
                    'fields': ['config'],
                    'description': '请根据选择的平台填写对应的配置信息',
                    'classes': ['collapse']
                }),
                ('时间信息', {
                    'fields': ('created_at', 'updated_at'),
                    'description': '系统自动记录的时间信息'
                })
            ]
        else:  # 添加页面
            return [
                ('基本信息', {
                    'fields': ['model_type', 'model_name', 'platform', 'original_model_name']
                }),
                ('控制选项', {
                    'fields': ['is_active']
                }),
                ('配置信息', {
                    'fields': ['config'],
                    'description': '请根据选择的平台填写对应的配置信息',
                    'classes': ['collapse']
                })
            ]
    
    def get_readonly_fields(self, request, obj=None):
        """设置只读字段"""
        if obj:  # 编辑时
            return ['weight', 'created_at', 'updated_at']  # 权重和时间字段设为只读
        return []  # 新增时没有只读字段
    
    def save_model(self, request, obj, form, change):
        """保存模型时的处理"""
        if not change:  # 新增时
            # 获取最大权重值
            max_weight = AIModel.objects.aggregate(max_weight=models.Max('weight'))['max_weight']
            # 设置新模型的权重为最大权重+1
            obj.weight = (max_weight or 0) + 1
            
            # 根据平台类型设置配置模板
            if not obj.config:
                if obj.platform == 'bigmodel':
                    obj.config = {'ZHIPU_API_KEY': ''}
                elif obj.platform == 'qianfan':
                    obj.config = {
                        'QIANFAN_ACCESS_KEY': '',
                        'QIANFAN_SECRET_KEY': ''
                    }
                elif obj.platform == 'spark':
                    obj.config = {
                        'SPARK_APPID': '',
                        'SPARK_API_KEY': '',
                        'SPARK_API_SECRET': ''
                    }
                elif obj.platform == 'silicon':
                    obj.config = {'SILICON_API_KEY': ''}
        
        super().save_model(request, obj, form, change)
    
    def get_config_description(self, obj):
        """根据平台返对应的配置说明"""
        if not obj:
            return ''
            
        if obj.platform == 'bigmodel':
            return ('智谱AI平台配置说明：<br>'
                   '- ZHIPU_API_KEY：智谱AI平台的API密钥<br><br>'
                   '配置示例：<br>'
                   '<pre>{\n'
                   '    "ZHIPU_API_KEY": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"\n'
                   '}</pre>')
        elif obj.platform == 'qianfan':
            return ('百度千帆平台配置说明：<br>'
                   '- QIANFAN_ACCESS_KEY：访问密钥<br>'
                   '- QIANFAN_SECRET_KEY：安全密钥<br><br>'
                   '配置示例：<br>'
                   '<pre>{\n'
                   '    "QIANFAN_ACCESS_KEY": "xxxxxxxxxxxxxxxxxxxxxxxx",\n'
                   '    "QIANFAN_SECRET_KEY": "xxxxxxxxxxxxxxxxxxxxxxxx"\n'
                   '}</pre>')
        elif obj.platform == 'spark':
            return ('讯飞星火平台配置说明：<br>'
                   '- SPARK_APPID：应用ID<br>'
                   '- SPARK_API_KEY：API密钥<br>'
                   '- SPARK_API_SECRET：安全密钥<br><br>'
                   '配置示例：<br>'
                   '<pre>{\n'
                   '    "SPARK_APPID": "xxxxxxxx",\n'
                   '    "SPARK_API_KEY": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",\n'
                   '    "SPARK_API_SECRET": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"\n'
                   '}</pre>')
        elif obj.platform == 'silicon':
            return ('SiliconCloud平台配置说明：<br>'
                   '- SILICON_API_KEY：API密钥<br><br>'
                   '配置示例：<br>'
                   '<pre>{\n'
                   '    "SILICON_API_KEY": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"\n'
                   '}</pre>')
        return ''

    class Media:
        js = ('admin/js/aimodel_admin.js',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('change-weight/<int:model_id>/<str:direction>/',
                 self.admin_site.admin_view(self.change_weight),
                 name='aimodel_change_weight'),
        ]
        return custom_urls + urls

    def change_weight(self, request, model_id, direction):
        """处理权重调整请求"""
        try:
            with transaction.atomic():  # 使用事务确保原子性
                model = AIModel.objects.select_for_update().get(id=model_id)
                current_weight = model.weight

                if direction == 'up' and current_weight > 1:
                    # 获取上一个权重的模型
                    other_model = AIModel.objects.select_for_update().filter(
                        weight=current_weight - 1
                    ).first()
                    if other_model:
                        # 使用临时权重避免唯一键冲突
                        temp_weight = -current_weight
                        model.weight = temp_weight
                        model.save()
                        
                        other_model.weight = current_weight
                        other_model.save()
                        
                        model.weight = current_weight - 1
                        model.save()

                elif direction == 'down':
                    # 获取下一个权重的模型
                    other_model = AIModel.objects.select_for_update().filter(
                        weight=current_weight + 1
                    ).first()
                    if other_model:
                        # 使用临时权重避免唯一键冲突
                        temp_weight = -current_weight
                        model.weight = temp_weight
                        model.save()
                        
                        other_model.weight = current_weight
                        other_model.save()
                        
                        model.weight = current_weight + 1
                        model.save()

            return JsonResponse({'success': True})
            
        except AIModel.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': '模型不存在'
            }, status=404)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

@admin.register(UserModel)
class UserModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'use_all_models', 'get_models_display', 'updated_at']
    list_filter = ['use_all_models']
    search_fields = ['user__email']
    filter_horizontal = ['models']
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """自定义多对多字段的表单字段"""
        if db_field.name == "models":
            # 只显示已启用的模型
            kwargs["queryset"] = AIModel.objects.filter(is_active=True)
        return super().formfield_for_manytomany(db_field, request, **kwargs)
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # 编辑时
            return ['user']
        return []  # 新建时没有只读字段

    def save_model(self, request, obj, form, change):
        if change:  # 只在修改时更新时间
            obj.updated_at = timezone.now()
        super().save_model(request, obj, form, change)