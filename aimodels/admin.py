from django.contrib import admin
from django.utils.html import format_html
from django.db.models import F
from .models import AIModel, UserModel
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import User
from django.utils import timezone

@receiver(post_save, sender=User)
def create_user_model(sender, instance, created, **kwargs):
    """当新用户创建时，自动创建对应的用户模型配置"""
    if created:
        UserModel.objects.create(user=instance)

@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('get_index', 'get_model_name_link', 'get_model_id', 'model_type', 'platform', 'is_active', 'weight_control')
    list_filter = ('model_type', 'platform', 'is_active')
    search_fields = ('model_name',)
    ordering = ('weight',)
    readonly_fields = ('weight', 'original_model_name', 'model_type', 'platform')
    
    # 只允许修改状态
    list_editable = ('is_active',)
    
    def get_model_id(self, obj):
        """自定义ID列的显示名称"""
        return format_html(
            '<span style="color: #666;">{}</span>',
            obj.id
        )
    get_model_id.short_description = '模型ID'
    get_model_id.admin_order_field = 'id'
    
    def get_model_name_link(self, obj):
        """自定义模型名称列，使其可点击并链接到编辑页面"""
        return format_html(
            '<a href="{}/change/">{}</a>',
            obj.id,
            obj.model_name
        )
    get_model_name_link.short_description = '模型名称'
    get_model_name_link.admin_order_field = 'model_name'
    
    def get_index(self, obj):
        """获取连续序号（基于当前页面的排序）"""
        request = getattr(self, 'request', None)
        if request:
            queryset = self.get_queryset(request)
            # 使用format_html返回纯文本
            return format_html(
                '<span style="color: #666;">{}</span>',
                list(queryset).index(obj) + 1
            )
        return format_html('<span>0</span>')
    get_index.short_description = '序号'
    # 移除admin_order_field以禁用排序
    get_index.admin_order_field = None

    def changelist_view(self, request, extra_context=None):
        # 保存request对象以供get_index使用
        self.request = request
        return super().changelist_view(request, extra_context)

    def weight_control(self, obj):
        """自定义权重控制列"""
        return format_html(
            '<div style="white-space:nowrap">'
            '<span style="margin-right:10px">{}</span>'
            '<a href="#" onclick="return handleWeightChange({}, \'up\')" style="margin-right:5px">'
            '<i class="fas fa-arrow-up"></i></a>'
            '<a href="#" onclick="return handleWeightChange({}, \'down\')">'
            '<i class="fas fa-arrow-down"></i></a>'
            '</div>',
            obj.weight, obj.id, obj.id
        )
    weight_control.short_description = '模型权重'
    weight_control.allow_tags = True

    class Media:
        css = {
            'all': ('admin/css/forms.css',)
        }
        js = (
            'admin/js/vendor/jquery/jquery.min.js',
            'admin/js/jquery.init.js',
            'admin/js/core.js',
        )

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('change-weight/<int:model_id>/<str:direction>/',
                 self.admin_site.admin_view(self.change_weight),
                 name='aimodel-change-weight'),
        ]
        return custom_urls + urls

    def change_weight(self, request, model_id, direction):
        """处理权重变更的视图"""
        from django.http import JsonResponse
        from django.db import transaction
        
        try:
            with transaction.atomic():  # 使用事务确保数据一致性
                model = AIModel.objects.select_for_update().get(id=model_id)
                current_weight = model.weight
                
                if direction == 'up' and current_weight > 1:
                    # 获取权重比当前小1的模型
                    swap_model = AIModel.objects.select_for_update().filter(
                        weight=current_weight - 1
                    ).first()
                    
                    if swap_model:
                        # 使用临时权重值来避免唯一键冲突
                        temp_weight = -1  # 使用一个不可能存在的临时权重值
                        
                        # 先将当前模型设置为临时权重
                        AIModel.objects.filter(id=model.id).update(
                            weight=temp_weight
                        )
                        
                        # 更新另一个模型的权重
                        AIModel.objects.filter(id=swap_model.id).update(
                            weight=current_weight
                        )
                        
                        # 最后设置当前模型的目标权重
                        AIModel.objects.filter(id=model.id).update(
                            weight=current_weight - 1
                        )
                
                elif direction == 'down':
                    # 获取权重比当前大1的模型
                    swap_model = AIModel.objects.select_for_update().filter(
                        weight=current_weight + 1
                    ).first()
                    
                    if swap_model:
                        # 使用临时权重值来避免唯一键冲突
                        temp_weight = -1  # 使用一个不可能存在的临时权重值
                        
                        # 先将当前模型设置为临时权重
                        AIModel.objects.filter(id=model.id).update(
                            weight=temp_weight
                        )
                        
                        # 更新另一个模型的权重
                        AIModel.objects.filter(id=swap_model.id).update(
                            weight=current_weight
                        )
                        
                        # 最后设置当前模型的目标权重
                        AIModel.objects.filter(id=model.id).update(
                            weight=current_weight + 1
                        )
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # 禁用添加和删除按钮
    def has_add_permission(self, request):
        return False
        
    def has_delete_permission(self, request, obj=None):
        return False
    
    # 允许编辑
    def has_change_permission(self, request, obj=None):
        return True
    
    # 只允许修改特定字段
    def get_readonly_fields(self, request, obj=None):
        if obj:  # 编辑时
            return ('id', 'model_type', 'platform')  # 这些字段不可修改
        return []
    
    def get_fieldsets(self, request, obj=None):
        """动态生成 fieldsets"""
        return (
            ('基本信息', {
                'fields': ('model_type', 'model_name', 'platform', 'is_active', 'weight', 'original_model_name'),
                'description': '模型基本信息配置，类型、平台和原始模型名称不可修改'
            }),
            ('配置信息', {
                'fields': ('config',),
                'classes': ('wide',),
                'description': self.get_config_description(obj) if obj else '请根据不同平台要求填写对应的配置信息'
            }),
        )

    def get_config_description(self, obj):
        """根据平台返回对应的配置说明"""
        if not obj:
            return ''
            
        if obj.platform == 'bigmodel':
            return ('智谱AI平台配置说明：<br>'
                   '- ZHIPU_API_KEY：智谱AI平台的API密钥<br><br>'
                   '配置示例：<br>'
                   '<pre>{\n'
                   '    "ZHIPU_API_KEY": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxx"\n'
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
                   '    "SILICON_API_KEY": "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"\n'
                   '}</pre>')
        return ''

    def save_model(self, request, obj, form, change):
        # 根据平台类型设置配置模板
        if not obj.config:
            if obj.platform == 'bigmodel':
                obj.config = {'ZHIPU_API_KEY': settings.ZHIPU_API_KEY}
            elif obj.platform == 'qianfan':
                obj.config = {
                    'QIANFAN_ACCESS_KEY': settings.QIANFAN_ACCESS_KEY,
                    'QIANFAN_SECRET_KEY': settings.QIANFAN_SECRET_KEY
                }
            elif obj.platform == 'spark':
                obj.config = {
                    'SPARK_APPID': settings.SPARK_APPID,
                    'SPARK_API_KEY': settings.SPARK_API_KEY,
                    'SPARK_API_SECRET': settings.SPARK_API_SECRET
                }
            elif obj.platform == 'silicon':
                obj.config = {'SILICON_API_KEY': settings.SILICON_API_KEY}
        super().save_model(request, obj, form, change)

@admin.register(UserModel)
class UserModelAdmin(admin.ModelAdmin):
    list_display = ('get_index', 'get_user_email', 'get_models_display', 'updated_at')
    readonly_fields = ('user', 'updated_at')
    search_fields = ('user__email',)
    ordering = ('-updated_at',)

    def get_index(self, obj):
        """获取序号"""
        request = getattr(self, 'request', None)
        if request:
            queryset = self.get_queryset(request)
            return list(queryset).index(obj) + 1
        return 0
    get_index.short_description = '序号'

    def get_user_email(self, obj):
        """获取用户邮箱"""
        return obj.user.email
    get_user_email.short_description = '用户邮箱'
    get_user_email.admin_order_field = 'user__email'

    def get_models_display(self, obj):
        """获取模型显示"""
        return obj.get_models_display()
    get_models_display.short_description = '模型ID'

    def get_fieldsets(self, request, obj=None):
        """自定义字段集"""
        return (
            ('基本信息', {
                'fields': ('user', 'updated_at'),
                'description': '用户基本信息（只读）'
            }),
            ('模型配置', {
                'fields': ('use_all_models', 'models'),
                'description': '选择用户可用的模型'
            }),
        )

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """自定义多对多字段的表单字段"""
        if db_field.name == "models":
            kwargs["widget"] = admin.widgets.FilteredSelectMultiple(
                "模型", False, attrs={'style': 'width: 100%;'}
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """保存时更新编辑时间"""
        if change:  # 只在编辑时更新时间
            obj.updated_at = timezone.now()
        super().save_model(request, obj, form, change)