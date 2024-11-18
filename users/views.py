from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from .models import User
from announcements.models import Announcement

@staff_member_required
def home(request):
    # 获取用户统计信息
    total_users = User.objects.filter(user_type='user').count()
    active_users = User.objects.filter(user_type='user', status='normal').count()
    warned_users = User.objects.filter(user_type='user', status='warning').count()
    banned_users = User.objects.filter(user_type='user', status='banned').count()
    
    # 获取最新公告
    latest_announcements = Announcement.objects.filter(
        is_active=True
    ).order_by('-created_at')[:5]
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'warned_users': warned_users,
        'banned_users': banned_users,
        'latest_announcements': latest_announcements,
    }
    
    return render(request, 'admin/home.html', context) 