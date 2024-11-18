import random
import string
from django.core.mail import send_mail
from django.conf import settings

def generate_email_code():
    """生成6位数字验证码"""
    return ''.join(random.choices(string.digits, k=6))

def send_verification_code(email, code):
    """发送邮箱验证码"""
    subject = 'TeaTalk 验证码'
    message = f'您的验证码是：{code}，有效期为5分钟。'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    
    try:
        send_mail(subject, message, from_email, recipient_list)
        return True
    except Exception as e:
        print(f"发送邮件失败: {e}")
        return False

def validate_password_strength(password):
    """验证密码强度"""
    categories = 0
    # 检查小写字母
    if any(c.islower() for c in password):
        categories += 1
    # 检查大写字母
    if any(c.isupper() for c in password):
        categories += 1
    # 检查数字
    if any(c.isdigit() for c in password):
        categories += 1
    # 检查特殊字符
    special_chars = set('!@#$%^&*()_+-=[]{}|;:,.<>?')
    if any(c in special_chars for c in password):
        categories += 1
    
    return categories >= 3

def validate_email_domain(email):
    """验证邮箱域名"""
    allowed_domains = ["qq.com", "163.com", "sina.com", "126.com"]
    domain = email.split('@')[-1].lower()
    return domain in allowed_domains 