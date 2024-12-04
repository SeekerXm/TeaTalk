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

@receiver(post_save, sender=User)
def create_user_model(sender, instance, created, **kwargs):
    """当新用户创建时，自动创建对应的用户模型配置"""
    if created:
        UserModel.objects.create(user=instance)

@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ['model_name', 'platform', 'version', 'is_active', 'weight', 'created_at']
    list_filter = ['platform', 'is_active']
    search_fields = ['model_name']
    ordering = ['weight']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('model_type', 'model_name', 'platform', 'is_active', 'weight')
        }),
        ('模型配置', {
            'fields': ('version', 'config'),
            'classes': ('collapse',),
            'description': '请根据选择的平台填写对应的配置信息'
        })
    )

    class Media:
        js = ('js/aimodel_admin.js',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # 添加动态版本选项的处理
        if obj and obj.platform:
            form.base_fields['version'].choices = AIModel.PLATFORM_VERSIONS.get(obj.platform, [])
        
        # 设置配置字段的widget
        form.base_fields['config'].widget = forms.Textarea(attrs={
            'rows': 10,
            'style': 'width: 100%; font-family: monospace;'
        })
        
        return form

    def save_model(self, request, obj, form, change):
        try:
            # 验证配置格式
            if not isinstance(obj.config, dict):
                obj.config = json.loads(obj.config)
            
            # 根据平台验证必要的配置字段
            if obj.platform == 'spark':
                required_fields = ['SPARK_APPID', 'SPARK_API_KEY', 'SPARK_API_SECRET']
            elif obj.platform == 'bigmodel':
                required_fields = ['ZHIPU_API_KEY']
            elif obj.platform == 'qianfan':
                required_fields = ['QIANFAN_ACCESS_KEY', 'QIANFAN_SECRET_KEY']
            elif obj.platform == 'silicon':
                required_fields = ['SILICON_API_KEY']
            else:
                required_fields = []

            for field in required_fields:
                if field not in obj.config:
                    raise ValidationError(f'{obj.get_platform_display()}配置缺少必要字段: {field}')
            
            # 验证版本是否有效
            valid_versions = [v[0] for v in AIModel.PLATFORM_VERSIONS.get(obj.platform, [])]
            if obj.version not in valid_versions:
                raise ValidationError(f'无效的{obj.get_platform_display()}版本: {obj.version}')
            
            super().save_model(request, obj, form, change)
            
        except json.JSONDecodeError:
            raise ValidationError('配置必须是有效的JSON格式')
        except Exception as e:
            raise ValidationError(f'保存失败: {str(e)}')

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