from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
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
from announcements.models import Announcement, UserAnnouncementRead

def index(request):
    """首页视图"""
    # 生成验证码
    hashkey = CaptchaStore.generate_key()
    image_url = captcha_image_url(hashkey)
    
    # 获取启用的公告列表
    announcements = Announcement.objects.filter(is_active=True).order_by('-created_at')
    print(f"获取到的公告列表: {announcements}")
    
    # 获取需要弹出显示的公告
    popup_announcement = None
    if request.user.is_authenticated:
        print(f"当前用户: {request.user.email}")
        # 获取用户未读的弹出公告
        popup_announcement = announcements.filter(
            show_popup=True,
            is_active=True
        ).exclude(
            userannouncementread__user=request.user
        ).first()
        print(f"已登录用户的弹出公告: {popup_announcement}")
    else:
        print("未登录用户")
        # 获取最新的弹出公告
        latest_popup = announcements.filter(
            show_popup=True,
            is_active=True
        ).first()
        
        if latest_popup:
            # 获取session中存储的已读公告ID列表
            read_announcements = request.session.get('read_announcements', [])
            print(f"未登录用户的已读公告列表: {read_announcements}")
            
            # 如果最新公告未被读过，则显示
            if latest_popup.id not in read_announcements:
                popup_announcement = latest_popup
                print(f"未登录用户的弹出公告: {popup_announcement}")
    
    print(f"最终弹出公告: {popup_announcement}")
    
    context = {
        'hashkey': hashkey,
        'image_url': image_url,
        'announcements': announcements,
        'popup_announcement': popup_announcement,
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
    try:
        print("开始处理登录请求")
        print(f"POST数据: {request.POST}")
        
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            print(f"表单验证通过 - Email: {email}")
            
            # 使用 authenticate 进行用户验证
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                # 检查用户是否被封禁
                if user.status == 'banned':
                    if user.ban_until:
                        ban_time = user.ban_until.strftime('%Y-%m-%d %H:%M')
                        return JsonResponse({
                            'success': False,
                            'message': f'该账号已被封禁至 {ban_time}'
                        })
                    else:
                        return JsonResponse({
                            'success': False,
                            'message': '该账号已被永久封禁'
                        })
                
                if not user.email_verified:
                    print("邮箱未验证")
                    return JsonResponse({
                        'success': False,
                        'message': '请先验证您的邮箱'
                    })
                
                print("登录成功")
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'message': '登录成功'
                })
            else:
                print("用户验证失败")
                return JsonResponse({
                    'success': False,
                    'message': '邮箱或密码错误'
                })
        else:
            # 添加这个分支处理表单验证失败的情况
            print(f"表单验证失败: {form.errors}")
            return JsonResponse({
                'success': False,
                'message': '邮箱或密码式错误'
            })
                
    except Exception as e:
        print(f"登录处理时出错: {str(e)}")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误详情: {e.args}")
        return JsonResponse({
            'success': False,
            'message': '服务器错误，请稍后重试'
        })

@require_POST
def reset_password(request):
    """重置密码处理"""
    try:
        print("开始处理重置密码请求")
        print(f"POST数据: {request.POST}")
        
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                if not user.check_email_verification_code(form.cleaned_data['email_code']):
                    print("邮箱验证码无效")
                    return JsonResponse({
                        'success': False,
                        'message': '邮箱验证码无效'
                    })
                
                # 检查用户状态
                if user.status == 'banned':
                    if user.ban_until:
                        ban_time = user.ban_until.strftime('%Y-%m-%d %H:%M')
                        return JsonResponse({
                            'success': False,
                            'message': f'该账号已被封禁至 {ban_time}，无法重置密'
                        })
                    else:
                        return JsonResponse({
                            'success': False,
                            'message': '该账号已被永久封禁，无法重置密码'
                        })
                
                # 重置密码
                user.set_password(form.cleaned_data['password1'])
                user.save()
                print(f"密码重置成功 - Email: {email}")
                return JsonResponse({
                    'success': True,
                    'message': '密码重置成功！请使用新密码登录。',
                    'email': email
                })
            except User.DoesNotExist:
                print("用户不存在")
                return JsonResponse({
                    'success': False,
                    'message': '该邮箱未注册'
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
        print(f"重置密码时出错: {str(e)}")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误详情: {e.args}")
        return JsonResponse({
            'success': False,
            'message': '服务器错误，请稍后重试'
        })

def user_logout(request):
    """退出登录"""
    logout(request)
    return redirect('index')

@staff_member_required
def home(request):
    """后台首页视图"""
    # 获取用户计信息
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

def get_announcement(request, announcement_id):
    """获取公告详情"""
    try:
        announcement = Announcement.objects.get(id=announcement_id, is_active=True)
        return JsonResponse({
            'success': True,
            'title': announcement.title,
            'content': announcement.content,
            'created_at': announcement.created_at.strftime('%Y-%m-%d %H:%M')
        })
    except Announcement.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '公告不存在'
        })

@require_POST
def mark_announcement_read(request, announcement_id):
    """标记公告为已读"""
    try:
        announcement = Announcement.objects.get(id=announcement_id, is_active=True)
        
        if request.user.is_authenticated:
            # 已登录用户：创建阅读记录
            UserAnnouncementRead.objects.get_or_create(
                user=request.user,
                announcement=announcement
            )
            print(f"已登录用户 {request.user.email} 标记公告 {announcement_id} 为已读")
        else:
            # 未登录用户：在session记录已读状态
            read_announcements = request.session.get('read_announcements', [])
            if announcement_id not in read_announcements:
                read_announcements.append(announcement_id)
                request.session['read_announcements'] = read_announcements
                request.session.modified = True
                print(f"未登录用户标记公告 {announcement_id} 为已读")
        
        return JsonResponse({'success': True})
    except Announcement.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': '公告不存在'
        })

@require_POST
def change_password(request):
    """修改密码"""
    print("收到修改密码请求")  # 调试日志
    print(f"请求方法: {request.method}")  # 调试日志
    print(f"POST数据: {request.POST}")  # 调试日志
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': '请先登录'
        })
    
    old_password = request.POST.get('old_password')
    new_password1 = request.POST.get('new_password1')
    new_password2 = request.POST.get('new_password2')
    
    print(f"当前用户: {request.user.email}")  # 调试日志
    print(f"旧密码验证结果: {request.user.check_password(old_password)}")  # 调试日志
    
    # 验证当前密码
    if not request.user.check_password(old_password):
        return JsonResponse({
            'success': False,
            'message': '当前密码错误'
        })
    
    # 验证新密码
    if new_password1 != new_password2:
        return JsonResponse({
            'success': False,
            'message': '两次输入的新密码不一致'
        })
    
    if len(new_password1) < 8:
        return JsonResponse({
            'success': False,
            'message': '新密码长度至少为8个字符'
        })
    
    # 验证密码强度
    categories = 0
    if any(c.islower() for c in new_password1): categories += 1
    if any(c.isupper() for c in new_password1): categories += 1
    if any(c.isdigit() for c in new_password1): categories += 1
    if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in new_password1): categories += 1
    
    if categories < 3:
        return JsonResponse({
            'success': False,
            'message': '新密码需要包含小写字母、大写字母、数字、特殊字符中的至少三类'
        })
    
    try:
        # 修改密码
        request.user.set_password(new_password1)
        request.user.save()
        print("密码修改成功")  # 调试日志
        
        # 更新会话，避免用户被登出
        update_session_auth_hash(request, request.user)
        
        return JsonResponse({
            'success': True,
            'message': '密码修改成功'
        })
    except Exception as e:
        print(f"修改密码时出错: {str(e)}")  # 调试日志
        return JsonResponse({
            'success': False,
            'message': '修改密码失败，请稍后重试'
        })

@require_POST
def delete_account(request):
    """注销账号"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': '请先登录'
        })
    
    password = request.POST.get('password')
    
    # 验证密码
    if not request.user.check_password(password):
        return JsonResponse({
            'success': False,
            'message': '密码错误'
        })
    
    try:
        # 删除用户及相关数据
        request.user.delete()
        logout(request)
        return JsonResponse({
            'success': True,
            'message': '账号已注销'
        })
    except Exception as e:
        print(f"注销账号时出错: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': '注销账号失败，请稍后重试'
        }) 