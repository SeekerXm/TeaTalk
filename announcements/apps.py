from django.apps import AppConfig

class AnnouncementsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'announcements'
    verbose_name = '公告管理'
    icon = 'fas fa-bullhorn'  # Font Awesome 图标 