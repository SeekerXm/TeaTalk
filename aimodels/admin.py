from django.contrib import admin
from django.utils.html import format_html
from .models import AIModel

@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('display_id', 'get_model_name_link', 'model_type', 'platform', 'is_active', 'weight')
    list_filter = ('model_type', 'platform', 'is_active')
    search_fields = ('model_name',)
    ordering = ('weight',)
    
    @admin.display(description='ID', ordering='id')
    def display_id(self, obj):
        """将ID显示为纯文本，禁用链接"""
        return obj.id
    
    def get_model_name_link(self, obj):
        """自定义模型名称列，使其可点击并链接到编辑页面"""
        return format_html(
            '<a href="{}/change/">{}</a>',
            obj.id,
            obj.model_name
        )
    get_model_name_link.short_description = '模型名称'
    get_model_name_link.admin_order_field = 'model_name'
    
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
    
    # 在列表页面可直接编辑的字段
    list_editable = ('is_active', 'weight')
    
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
    
    class Media:
        css = {
            'all': ('admin/css/forms.css',)
        }
        js = ('admin/js/core.js',)