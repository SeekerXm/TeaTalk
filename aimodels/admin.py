from django.contrib import admin
from .models import AIModel

@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'model_name', 'model_type', 'platform', 'is_active', 'weight')
    list_filter = ('model_type', 'platform', 'is_active')
    search_fields = ('model_name',)
    ordering = ('weight',)
    
    # 禁用添加和删除按钮
    def has_add_permission(self, request):
        return False
        
    def has_delete_permission(self, request, obj=None):
        return False
    
    # 只允许修改特定字段
    def get_readonly_fields(self, request, obj=None):
        if obj:  # 编辑时
            return ('id', 'model_type', 'platform')  # 这些字段不可修改
        return []
    
    fieldsets = (
        ('基本信息', {
            'fields': ('model_type', 'model_name', 'platform', 'is_active', 'weight')
        }),
        ('配置信息', {
            'fields': ('config',),
            'classes': ('collapse',),
            'description': '请按照模型平台要求填写配置信息'
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