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
    
    # 基本信息
    model_type = models.CharField('模型类型', max_length=10, choices=MODEL_TYPES)
    model_name = models.CharField('模型名称', max_length=50)
    platform = models.CharField('模型平台', max_length=20, choices=PLATFORMS)
    is_active = models.BooleanField('模型状态', default=True, choices=STATUS_CHOICES)
    weight = models.IntegerField('模型权重', unique=True, null=True, blank=True)
    config = models.JSONField('模型配置', default=dict)
    original_model_name = models.CharField('原始模型名称', max_length=100, blank=True, null=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True, editable=False)
    updated_at = models.DateTimeField('更新时间', auto_now=True, editable=False)

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