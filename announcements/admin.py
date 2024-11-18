from django.contrib import admin
from django.utils.html import format_html
from .models import Announcement

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at', 'show_modal_tag', 'is_active_tag')
    list_filter = ('show_modal', 'is_active')
    search_fields = ('title', 'content')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('title', 'content')
        }),
        ('显示设置', {
            'fields': ('show_modal', 'is_active'),
            'classes': ('collapse',)
        }),
    )
    
    def show_modal_tag(self, obj):
        return format_html(
            '<span class="el-tag el-tag--{}">{}</span>',
            'success' if obj.show_modal else 'info',
            '是' if obj.show_modal else '否'
        )
    show_modal_tag.short_description = '弹出公告'
    
    def is_active_tag(self, obj):
        return format_html(
            '<span class="el-tag el-tag--{}">{}</span>',
            'success' if obj.is_active else 'info',
            '启用' if obj.is_active else '停用'
        )
    is_active_tag.short_description = '状态'