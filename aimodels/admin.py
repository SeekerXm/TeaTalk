from django.contrib import admin
from django.utils.html import format_html
from django.db.models import F
from .models import AIModel

@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('get_index', 'get_model_id', 'model_name', 'model_type', 'platform', 'is_active', 'weight_control')
    list_filter = ('model_type', 'platform', 'is_active')
    search_fields = ('model_name',)
    ordering = ('weight',)
    readonly_fields = ('weight',)
    
    # 只允许修改状态
    list_editable = ('is_active',)
    
    def get_model_id(self, obj):
        """自定义ID列的显示名称"""
        return obj.id
    get_model_id.short_description = '模型ID'
    get_model_id.admin_order_field = 'id'
    
    def get_index(self, obj):
        """获取连续序号（基于当前页面的排序）"""
        request = getattr(self, 'request', None)
        if request:
            queryset = self.get_queryset(request)
            index = list(queryset).index(obj) + 1
            return index
        return 0
    get_index.short_description = '序号'
    get_index.admin_order_field = 'weight'

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
    
    # 自定义表单布局
    fieldsets = (
        ('基本信息', {
            'fields': ('model_type', 'model_name', 'platform', 'is_active', 'weight'),
            'description': '模型基本信息配置，类型和平台不可修改'
        }),
        ('配置信息', {
            'fields': ('config',),
            'classes': ('wide',),
            'description': '请按照模型平台要求填写配置信息：<br>'
                         'BigModel: ZHIPU_API_KEY = ""<br>'
                         '百度千帆: QIANFAN_ACCESS_KEY = "", QIANFAN_SECRET_KEY = ""<br>'
                         '讯飞星火: SPARK_APPID = "", SPARK_API_KEY = "", SPARK_API_SECRET = ""<br>'
                         'SiliconCloud: SILICON_API_KEY = ""'
        }),
    )

    def save_model(self, request, obj, form, change):
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