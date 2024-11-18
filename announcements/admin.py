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
            'fields': ('title', 'content')
        }),
        ('设置', {
            'fields': ('show_popup', 'is_active'),
            'classes': ('collapse',)
        })
    )

    class Media:
        css = {
            'all': ('css/announcement_admin.css',)
        }

@admin.register(UserAnnouncementRead)
class UserAnnouncementReadAdmin(admin.ModelAdmin):
    list_display = ('user', 'announcement', 'read_at')
    list_filter = ('read_at',)
    search_fields = ('user__email', 'announcement__title')
    date_hierarchy = 'read_at'
    
    def has_add_permission(self, request):
        return False