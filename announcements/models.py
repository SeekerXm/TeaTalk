from django.db import models
from django.utils import timezone

class Announcement(models.Model):
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    show_popup = models.BooleanField(default=False, verbose_name='是否弹出显示')
    
    class Meta:
        verbose_name = '公告'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class UserAnnouncementRead(models.Model):
    """用户公告阅读记录"""
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, verbose_name='公告')
    read_at = models.DateTimeField(auto_now_add=True, verbose_name='阅读时间')

    class Meta:
        verbose_name = '公告阅读记录'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'announcement'] 