from django.db import models

class AIModel(models.Model):
    MODEL_TYPES = [
        ('chat', '对话'),
        ('image', '图像'),
    ]
    
    PLATFORMS = [
        ('bigmodel', 'BigModel'),
        ('qianfan', '百度千帆'),
        ('spark', '讯飞星火'),
        ('silicon', 'SiliconCloud'),
    ]
    
    STATUS_CHOICES = [
        (True, '启用'),
        (False, '停用'),
    ]
    
    model_type = models.CharField('模型类型', max_length=10, choices=MODEL_TYPES)
    model_name = models.CharField('模型名称', max_length=50)
    platform = models.CharField('模型平台', max_length=20, choices=PLATFORMS)
    is_active = models.BooleanField('模型状态', default=True, choices=STATUS_CHOICES)
    weight = models.IntegerField('模型权重', unique=True)
    config = models.JSONField('模型配置', default=dict)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    original_model_name = models.CharField('原始模型名称', max_length=100, blank=True)

    class Meta:
        verbose_name = '模型管理'
        verbose_name_plural = verbose_name
        ordering = ['weight']

    def __str__(self):
        return f"{self.get_platform_display()} - {self.model_name}" 