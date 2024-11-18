from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from .forms import RegisterForm, LoginForm, ResetPasswordForm
from .models import User
from .utils import generate_email_code, send_verification_code, validate_email_domain
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from announcements.models import Announcement

def index(request):
    """首页视图"""
    # 生成验证码
    hashkey = CaptchaStore.generate_key()
    image_url = captcha_image_url(hashkey)
    
    context = {
        'hashkey': hashkey,
        'image_url': image_url,
    }
    return render(request, 'base.html', context)

@require_POST
def verify_captcha(request):
    """验证人机验证码"""
    captcha_key = request.POST.get('captcha_key')
    captcha_value = request.POST.get('captcha_value')
    try:
        CaptchaStore.objects.get(
            response=captcha_value.lower(),
            hashkey=captcha_key,
            expiration__gt=timezone.now()
        ).delete()
        return JsonResponse({'valid': True})
    except CaptchaStore.DoesNotExist:
        return JsonResponse({'valid': False})

@require_POST
def send_email_code(request):
    """发送邮箱验证码"""
    email = request.POST.get('email')
    if not email or not validate_email_domain(email):
        return JsonResponse({'success': False, 'message': '无效的邮箱地址'})
    
    code = generate_email_code()
    if send_verification_code(email, code):
        user, _ = User.objects.get_or_create(email=email)
        user.set_email_verification_code(code)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'message': '发送验证码失败'})

@require_POST
def register(request):
    """注册处理"""
    form = RegisterForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
            if not user.check_email_verification_code(form.cleaned_data['email_code']):
                return JsonResponse({'success': False, 'message': '邮箱验证码无效'})
            
            user.set_password(form.cleaned_data['password1'])
            user.email_verified = True
            user.save()
            login(request, user)
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': '注册失败'})
    return JsonResponse({'success': False, 'errors': form.errors})

@require_POST
def user_login(request):
    """登录处理"""
    form = LoginForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                login(request, user)
                return JsonResponse({'success': True})
        except User.DoesNotExist:
            pass
    return JsonResponse({'success': False, 'message': '邮箱或密码错误'})

@require_POST
def reset_password(request):
    """重置密码处理"""
    form = ResetPasswordForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
            if not user.check_email_verification_code(form.cleaned_data['email_code']):
                return JsonResponse({'success': False, 'message': '邮箱验证码无效'})
            
            user.set_password(form.cleaned_data['password1'])
            user.save()
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': '用户不存在'})
    return JsonResponse({'success': False, 'errors': form.errors})

def user_logout(request):
    """退出登录"""
    logout(request)
    return redirect('index')

@staff_member_required
def home(request):
    """后台首页视图"""
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