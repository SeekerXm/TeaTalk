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
import json
from django.core.exceptions import ValidationError
from django import forms
from ModelPlatform.spark import SparkPlatform

@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    """AI模型管理"""
    list_display = ['model_name', 'get_platform_display', 'get_version_display', 'is_active', 'weight', 'created_at']
    list_filter = ['platform', 'is_active']
    search_fields = ['model_name']
    ordering = ['weight', '-created_at']
    readonly_fields = ['platform', 'version', 'model_type']
    
    fieldsets = (
        ('基本信息', {
            'fields': (
                'model_type',
                'platform',
                'version',
                'model_name',
                'is_active',
                'weight'
            ),
            'description': '基本信息一旦创建后，模型类型、模型平台、模型版本和模型权重将无法修改'
        }),
        ('模型配置', {
            'fields': ('config',),
            'classes': ('collapse',),
            'description': '请根据选择的平台填写对应的配置信息'
        })
    )

    class Media:
        js = ('js/aimodel_admin.js',)

    def get_readonly_fields(self, request, obj=None):
        """获取只读字段"""
        if obj:  # 编辑页面
            return self.readonly_fields
        return []  # 添加页面

    def get_form(self, request, obj=None, **kwargs):
        """自定义表单"""
        form = super().get_form(request, obj, **kwargs)
        
        if obj:  # 编辑现有模型时
            # 设置配置字段
            form.base_fields['config'].widget = forms.Textarea(attrs={
                'rows': 10,
                'class': 'form-control json-editor',
                'style': 'font-family: monospace; background-color: #f9fafb;',
                'spellcheck': 'false',
                'autocomplete': 'off'
            })
            form.base_fields['config'].error_messages = {
                'required': '请填写模型配置',
                'invalid': '请输入有效的JSON格式'
            }

            # 设置只读字段
            readonly_fields = self.get_readonly_fields(request, obj)
            for field_name in readonly_fields:
                if field_name in form.base_fields:
                    form.base_fields[field_name].disabled = True

        else:  # 添加新模型时
            # 设置版本字段的初始选项
            form.base_fields['version'].widget = forms.Select(choices=[('', '请选择版本')])
            form.base_fields['version'].error_messages = {
                'required': '请选择模型版本',
                'invalid_choice': '请选择有效的模型版本'
            }
            
            # 设置配置字段的初始状态
            form.base_fields['config'].widget = forms.Textarea(attrs={
                'rows': 10,
                'class': 'form-control json-editor',
                'style': 'font-family: monospace; background-color: #f9fafb;',
                'spellcheck': 'false',
                'autocomplete': 'off',
                'placeholder': '请选择平台后，将自动填充配置模板'
            })
        
        return form

    def save_model(self, request, obj, form, change):
        try:
            if not change:  # 添加新模型时
                # 获取当前最大权重值
                max_weight = AIModel.objects.aggregate(models.Max('weight'))['weight__max']
                obj.weight = 1 if max_weight is None else max_weight + 1
            
            # 验证配置格式
            if isinstance(obj.config, str):
                try:
                    obj.config = json.loads(obj.config)
                except json.JSONDecodeError:
                    raise ValidationError('配置格式错误，请输入有效的JSON格式')
            
            # 验证配置字段
            if not isinstance(obj.config, dict):
                raise ValidationError('配置必须是一个有效的JSON象')
            
            # 根据平台验证必要的配置字段
            if obj.platform == 'spark':
                required_fields = ['SPARK_APPID', 'SPARK_API_KEY', 'SPARK_API_SECRET']
            else:
                required_fields = []

            for field in required_fields:
                if field not in obj.config:
                    raise ValidationError(f'{obj.get_platform_display()}配置缺少必要字段：{field}')
            
            # 验证版本是否有效
            valid_versions = [v[0] for v in AIModel.PLATFORM_VERSIONS.get(obj.platform, [])]
            if obj.version and obj.version not in valid_versions and not change:  # 只在添加时验证版本
                raise ValidationError(f'无效的{obj.get_platform_display()}版本：{obj.version}')
            
            super().save_model(request, obj, form, change)
            
        except ValidationError as e:
            raise e
        except Exception as e:
            raise ValidationError(f'保存失败：{str(e)}')

    def delete_model(self, request, obj):
        """
        删除模型时的处理逻辑
        """
        try:
            # 检查是否有用户在使用这个模型
            users_using_model = UserModel.objects.filter(models=obj)
            if users_using_model.exists():
                # 从用户的可用模型列表中移除该模型
                for user_model in users_using_model:
                    user_model.models.remove(obj)
            
            # 删除模型
            obj.delete()
            
            # 重新排序剩余模型的权重
            models = AIModel.objects.order_by('weight')
            for index, model in enumerate(models, start=1):
                if model.weight != index:
                    model.weight = index
                    model.save(update_fields=['weight'])
                    
        except Exception as e:
            raise ValidationError(f'删除失败：{str(e)}')

    def has_delete_permission(self, request, obj=None):
        """
        检查是否有删除权限
        """
        return request.user.is_superuser  # 只允许超级管理员删除模型

@admin.register(UserModel)
class UserModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'use_all_models', 'get_models_display', 'updated_at']
    list_filter = ['use_all_models']
    search_fields = ['user__email']
    filter_horizontal = ['models']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # 编辑时
            return ['user']
        return []  # 新建时没有只读字段

    def save_model(self, request, obj, form, change):
        if change:  # 只在修改时更新时间
            obj.updated_at = timezone.now()
        super().save_model(request, obj, form, change)