from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import User

class AIModel(models.Model):
    """AI模型表"""
    MODEL_TYPES = [
        ('chat', '对话'),
        ('image', '图像'),
    ]
    
    PLATFORMS = [
        ('spark', '讯飞星火'),
        ('bigmodel', 'BigModel'),
        ('qianfan', '百度千帆'),
        ('silicon', 'SiliconCloud'),
    ]
    
    STATUS_CHOICES = [
        (True, '启用'),
        (False, '停用'),
    ]
    
    # 各平台的版本选项
    PLATFORM_VERSIONS = {
        'spark': [
            ('lite', 'Spark Lite (基础版)'),
            ('pro', 'Spark Pro (专业版)'),
            ('pro-128k', 'Spark Pro-128K (长文本版)'),
            ('max', 'Spark Max (高级版)'),
            ('max-32k', 'Spark Max-32K (长文本高级版)'),
            ('ultra', 'Spark 4.0 Ultra (旗舰版)')
        ],
        'bigmodel': [
            ('glm-4', 'GLM-4'),
            ('glm-4-vision', 'GLM-4-Vision'),
            ('glm-3-turbo', 'GLM-3-Turbo'),
        ],
        'qianfan': [
            ('yi-34b-chat', 'Yi-34B-Chat'),
            ('llama2-70b-chat', 'Llama2-70B-Chat'),
            ('llama2-13b-chat', 'Llama2-13B-Chat'),
        ],
        'silicon': [
            ('qwen-turbo', 'Qwen-Turbo'),
            ('qwen-plus', 'Qwen-Plus'),
            ('qwen-max', 'Qwen-Max'),
        ]
    }
    
    # 各平台的配置说明
    PLATFORM_CONFIG_HELP = {
        'spark': """
        星火平台配置示例：
        {
            "SPARK_APPID": "xxxxxxxx",
            "SPARK_API_KEY": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "SPARK_API_SECRET": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        }
        """,
        'bigmodel': """
        智谱平台配置示例：
        {
            "ZHIPU_API_KEY": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        }
        """,
        'qianfan': """
        千帆平台配置示例：
        {
            "QIANFAN_ACCESS_KEY": "xxxxxxxxxxxxxxxxxxxxxxxx",
            "QIANFAN_SECRET_KEY": "xxxxxxxxxxxxxxxxxxxxxxxx"
        }
        """,
        'silicon': """
        SiliconCloud平台配置示例：
        {
            "SILICON_API_KEY": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        }
        """
    }
    
    # 基本信息
    model_type = models.CharField('模型类型', max_length=10, choices=MODEL_TYPES)
    model_name = models.CharField('模型名称', max_length=50)
    platform = models.CharField('模型平台', max_length=20, choices=PLATFORMS)
    is_active = models.BooleanField('模型状态', default=True, choices=STATUS_CHOICES)
    weight = models.IntegerField('模型权重', unique=True, null=True, blank=True)
    version = models.CharField('模型版本', max_length=20)
    config = models.JSONField('模型配置', default=dict)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '模型管理'
        verbose_name_plural = verbose_name
        ordering = ['weight']

    def __str__(self):
        return f"{self.get_platform_display()} - {self.model_name}"

class UserModel(models.Model):
    """用户模型配置表"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='user_models',
        verbose_name='用户'
    )
    use_all_models = models.BooleanField('使用所有模型', default=True)
    updated_at = models.DateTimeField('编辑时间', null=True, blank=True)
    models = models.ManyToManyField('AIModel', blank=True, verbose_name='可用模型')

    class Meta:
        verbose_name = '用户模型'
        verbose_name_plural = verbose_name
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user.email} 的模型配置"

    def get_models_display(self):
        if self.use_all_models:
            return "所有"
        return ", ".join([f"#{m.id}" for m in self.models.all()])

    def get_models_detail_display(self):
        if self.use_all_models:
            return "所有"
        return ", ".join([f"#{m.id}-{m.model_name}" for m in self.models.all()])

@receiver(post_save, sender=User)
def create_user_model(sender, instance, created, **kwargs):
    """当新用户创建时，自动创建对应的用户模型配置"""
    if created and instance.email_verified:  # 只在新用户创建且邮箱已验证时执行
        UserModel.objects.get_or_create(
            user=instance,
            defaults={
                'use_all_models': True,
                'updated_at': None
            }
        ) 