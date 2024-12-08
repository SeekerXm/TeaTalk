from django.contrib import admin
from django.db import transaction
from django.contrib import messages
from .models import ChatSettings, ChatConversation, ChatMessage, ChatDeletionLog

@admin.register(ChatSettings)
class ChatSettingsAdmin(admin.ModelAdmin):
    """对话设置管理"""
    list_display = ['setting_type', 'duration_display', 'max_records', 'is_enabled', 'updated_at']
    list_filter = ['setting_type', 'is_enabled']
    search_fields = ['description']
    readonly_fields = ['created_by', 'updated_by']
    
    def duration_display(self, obj):
        if obj.is_permanent:
            return '永久'
        
        duration_parts = []
        if obj.duration_days:
            duration_parts.append(f'{obj.duration_days}天')
        if obj.duration_hours:
            duration_parts.append(f'{obj.duration_hours}小时')
        if obj.duration_minutes:
            duration_parts.append(f'{obj.duration_minutes}分钟')
            
        return ' '.join(duration_parts) if duration_parts else '未设置'
    duration_display.short_description = '保存时长'

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        # 如果当前设置被启用
        if obj.is_enabled:
            # 禁用同类型的其他设置
            ChatSettings.objects.filter(
                setting_type=obj.setting_type,
                is_enabled=True
            ).exclude(
                id=obj.id if obj.id else None
            ).update(is_enabled=False)
            
            # 添加提示消息
            messages.info(request, f'已自动禁用其他同类型的{obj.get_setting_type_display()}设置')
        
        # 设置创建人和更新人
        if not change:  # 创建时
            obj.created_by = request.user
        obj.updated_by = request.user
        
        super().save_model(request, obj, form, change)


@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):
    """对话记录管理"""
    list_display = ['title', 'user', 'conversation_type', 'status', 'expire_time', 'created_at']
    list_filter = ['conversation_type', 'status', 'model']
    search_fields = ['title', 'user__email']
    readonly_fields = ['user', 'model', 'created_at', 'updated_at']
    
    def has_add_permission(self, request):
        return False  # 禁手动添加对话记录


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """对话消息管理"""
    list_display = ['conversation', 'role', 'message_type', 'content_preview', 'created_at']
    list_filter = ['role', 'message_type']
    search_fields = ['content', 'conversation__title']
    readonly_fields = ['conversation', 'role', 'content', 'message_type', 'metadata', 'created_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '内容预览'
    
    def has_add_permission(self, request):
        return False  # 禁止手动添加消息


@admin.register(ChatDeletionLog)
class ChatDeletionLogAdmin(admin.ModelAdmin):
    """删除日志管理"""
    list_display = ['user', 'deletion_type', 'deleted_at']
    list_filter = ['deletion_type', 'deleted_at']
    search_fields = ['user__email']
    readonly_fields = ['conversation', 'user', 'deletion_type', 'deleted_at']
    
    def has_add_permission(self, request):
        return False  # 禁止手动添加删除日志 