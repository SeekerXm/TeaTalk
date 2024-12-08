from django.db import models
from django.utils import timezone
from django.conf import settings

class ChatSettings(models.Model):
    """对话设置表"""
    SETTING_TYPE_CHOICES = [
        ('history', '历史记录'),
        ('temporary', '临时记录'),
    ]
    
    setting_type = models.CharField(
        max_length=20,
        choices=SETTING_TYPE_CHOICES,
        unique=True,
        verbose_name='设置类型'
    )
    duration_days = models.IntegerField(
        default=0,
        verbose_name='持续时间(天)'
    )
    duration_hours = models.IntegerField(
        default=0,
        verbose_name='持续时间(小时)'
    )
    duration_minutes = models.IntegerField(
        default=0,
        verbose_name='持续时间(分钟)'
    )
    is_permanent = models.BooleanField(
        default=False,
        verbose_name='是否永久保存'
    )
    max_records = models.IntegerField(
        verbose_name='最大保存记录数'
    )
    is_enabled = models.BooleanField(
        default=True,
        verbose_name='是否启用'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='设置说明'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_chat_settings',
        verbose_name='创建人'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='updated_chat_settings',
        verbose_name='更新人'
    )

    class Meta:
        verbose_name = '对话设置'
        verbose_name_plural = verbose_name
        db_table = 'chat_settings'

    def __str__(self):
        return f"{self.get_setting_type_display()}" 


class ChatConversation(models.Model):
    """对话主表"""
    CONVERSATION_TYPE_CHOICES = [
        ('history', '历史记录'),
        ('temporary', '临时记录'),
    ]
    
    STATUS_CHOICES = [
        ('active', '活跃'),
        ('deleted', '已删除'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations',
        verbose_name='用户'
    )
    title = models.CharField(
        max_length=255,
        verbose_name='对话标题'
    )
    conversation_type = models.CharField(
        max_length=20,
        choices=CONVERSATION_TYPE_CHOICES,
        verbose_name='对话类型'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='状态'
    )
    expire_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='过期时间'
    )
    model = models.ForeignKey(
        'aimodels.AIModel',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='AI模型'
    )
    last_message_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='最后消息时间'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        verbose_name = '对话记录'
        verbose_name_plural = verbose_name
        db_table = 'chat_conversations'
        indexes = [
            models.Index(fields=['user', 'conversation_type']),
            models.Index(fields=['expire_time']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.title[:30]}"


class ChatMessage(models.Model):
    """对话消息表"""
    ROLE_CHOICES = [
        ('user', '用户'),
        ('assistant', 'AI助手'),
    ]
    
    MESSAGE_TYPE_CHOICES = [
        ('text', '文本'),
        ('image', '图片'),
        ('code', '代码'),
    ]
    
    conversation = models.ForeignKey(
        ChatConversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='对话'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        verbose_name='发送者角色'
    )
    content = models.TextField(
        verbose_name='消息内容'
    )
    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPE_CHOICES,
        default='text',
        verbose_name='消息类型'
    )
    metadata = models.JSONField(
        null=True,
        blank=True,
        verbose_name='额外元数据'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        verbose_name = '对话消息'
        verbose_name_plural = verbose_name
        db_table = 'chat_messages'
        indexes = [
            models.Index(fields=['conversation', 'role', 'created_at']),
        ]

    def __str__(self):
        return f"{self.conversation.title[:20]} - {self.role}"


class ChatDeletionLog(models.Model):
    """对话删除记录表"""
    DELETION_TYPE_CHOICES = [
        ('user_initiated', '用户删除'),
        ('system_auto', '系统自动删除'),
    ]
    
    conversation = models.ForeignKey(
        ChatConversation,
        on_delete=models.CASCADE,
        verbose_name='对话'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='用户'
    )
    deletion_type = models.CharField(
        max_length=20,
        choices=DELETION_TYPE_CHOICES,
        verbose_name='删除类型'
    )
    deleted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='删除时间'
    )

    class Meta:
        verbose_name = '删除日志'
        verbose_name_plural = verbose_name
        db_table = 'chat_deletion_logs'
        indexes = [
            models.Index(fields=['user', 'deleted_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.get_deletion_type_display()}"