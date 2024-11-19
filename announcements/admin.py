from django.contrib import admin
from django.utils.html import format_html
from .models import Announcement, UserAnnouncementRead

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at', 'show_popup', 'is_active')
    list_filter = ('is_active', 'show_popup')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'show_popup', 'is_active')
        }),
    )

    class Media:
        css = {
            'all': (
                'admin/css/changelists.css',  # 先加载系统默认样式
                'css/announcement_admin.css',  # 再加载自定义样式
            )
        }

    def changelist_view(self, request, extra_context=None):
        """添加自定义 CSS 类到 changelist 视图"""
        extra_context = extra_context or {}
        extra_context['extra_css_class'] = 'announcement-changelist'
        return super().changelist_view(request, extra_context)

@admin.register(UserAnnouncementRead)
class UserAnnouncementReadAdmin(admin.ModelAdmin):
    list_display = ('user', 'announcement', 'read_at')
    list_filter = ('read_at',)
    search_fields = ('user__email', 'announcement__title')
    date_hierarchy = 'read_at'
    
    def has_add_permission(self, request):
        return False