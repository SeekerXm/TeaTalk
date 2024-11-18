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
    
    # 添加调试日志
    print(f"验证码验证 - Key: {captcha_key}, Value: {captcha_value}")
    
    try:
        CaptchaStore.objects.get(
            response=captcha_value.lower(),
            hashkey=captcha_key,
            expiration__gt=timezone.now()
        ).delete()
        print("验证码验证成功")
        return JsonResponse({'valid': True})
    except CaptchaStore.DoesNotExist:
        print("验证码验证失败")
        return JsonResponse({'valid': False})

@require_POST
def send_email_code(request):
    """发送邮箱验证码"""
    try:
        email = request.POST.get('email')
        print(f"收到发送验证码请求 - Email: {email}")
        
        if not email:
            return JsonResponse({'success': False, 'message': '请输入邮箱地址'})
            
        if not validate_email_domain(email):
            return JsonResponse({'success': False, 'message': '不支持的邮箱域名'})
        
        code = generate_email_code()
        print(f"生成验证码: {code}")
        
        if send_verification_code(email, code):
            user, created = User.objects.get_or_create(email=email)
            user.set_email_verification_code(code)
            print(f"验证码发送成功 - Email: {email}, Code: {code}")
            return JsonResponse({'success': True})
        else:
            print(f"验证码发送失败")
            return JsonResponse({'success': False, 'message': '邮件发送失败，请稍后重试'})
            
    except Exception as e:
        print(f"发送验证码时出错: {str(e)}")
        return JsonResponse({'success': False, 'message': '服务器错误，请稍后重试'})

@require_POST
def register(request):
    """注册处理"""
    try:
        print("开始处理注册请求")
        print(f"POST数据: {request.POST}")
        
        form = RegisterForm(request.POST)
        if form.is_valid():
            print("表单验证通过")
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                print(f"找到已存在用户: {email}")
                # 如果用户存在但未验证邮箱
                if not user.email_verified:
                    if user.check_email_verification_code(form.cleaned_data['email_code']):
                        user.set_password(form.cleaned_data['password1'])
                        user.email_verified = True
                        user.save()
                        print("未验证用户注册成功")
                        return JsonResponse({
                            'success': True,
                            'message': '注册成功！请使用您的邮箱和密码登录。',
                            'email': email
                        })
                    print("邮箱验证码无效")
                    return JsonResponse({
                        'success': False,
                        'message': '邮箱验证码无效'
                    })
                # 如果用户已存在且已验证
                print("邮箱已被注册")
                return JsonResponse({
                    'success': False,
                    'message': '该邮箱已被注册'
                })
            except User.DoesNotExist:
                print(f"创建新用户: {email}")
                # 创建新用户
                try:
                    user = User.objects.create_user(
                        email=email,
                        password=form.cleaned_data['password1']
                    )
                    if user.check_email_verification_code(form.cleaned_data['email_code']):
                        user.email_verified = True
                        user.save()
                        print("新用户注册成功")
                        return JsonResponse({
                            'success': True,
                            'message': '注册成功！请使用您的邮箱和密码登录。',
                            'email': email
                        })
                    print("邮箱验证码无效")
                    return JsonResponse({
                        'success': False,
                        'message': '邮箱验证码无效'
                    })
                except Exception as e:
                    print(f"创建用户时出错: {str(e)}")
                    return JsonResponse({
                        'success': False,
                        'message': '创建用户失败，请稍后重试'
                    })
        else:
            print(f"表单验证失败: {form.errors}")
            # 获取第一个错误信息
            first_error = next(iter(form.errors.values()))[0]
            return JsonResponse({
                'success': False,
                'message': str(first_error)
            })
            
    except Exception as e:
        print(f"注册处理时出错: {str(e)}")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误详情: {e.args}")
        return JsonResponse({
            'success': False,
            'message': '服务器错误，请稍后重试'
        })

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

def refresh_captcha(request):
    """刷新验证码"""
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        new_key = CaptchaStore.generate_key()
        new_image_url = captcha_image_url(new_key)
        return JsonResponse({
            'key': new_key,
            'image_url': new_image_url
        })
    return JsonResponse({'status': 'error'}, status=400) 