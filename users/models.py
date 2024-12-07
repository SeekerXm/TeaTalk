from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from datetime import timedelta

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """创建普通用户"""
        if not email:
            raise ValueError('邮箱地址是必需的')
        email = self.normalize_email(email)
        
        # 设置默认值
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('email_verified', True)
        extra_fields.setdefault('status', 'normal')
        extra_fields.setdefault('user_type', 'user')
        
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """创建超级用户"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')
        extra_fields.setdefault('status', 'normal')
        extra_fields.setdefault('email_verified', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('超级用户必须设置 is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('超级用户必须设置 is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    STATUS_CHOICES = (
        ('normal', '正常'),
        ('warning', '警告'),
        ('banned', '封禁'),
    )
    USER_TYPE_CHOICES = (
        ('admin', '管理员'),
        ('user', '普通用户'),
    )
    
    # 基本字段
    email = models.EmailField(unique=True, verbose_name='邮箱')
    username = models.CharField(max_length=150, blank=True, null=True, verbose_name='用户名')
    
    # 状态字段
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='normal', verbose_name='状态')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='user', verbose_name='用户类型')
    ban_until = models.DateTimeField(null=True, blank=True, verbose_name='封禁截止时间')
    
    # 权限字段
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    is_staff = models.BooleanField(default=False, verbose_name='是否为管理员')
    
    # 时间字段
    date_joined = models.DateTimeField(default=timezone.now, verbose_name='注册时间')
    last_login = models.DateTimeField(null=True, blank=True, verbose_name='最后登录时间')
    
    # 邮箱验证字段
    email_verified = models.BooleanField(default=False, verbose_name='邮箱已验证')
    email_verification_code = models.CharField(max_length=6, null=True, blank=True, verbose_name='邮箱验证码')
    email_verification_code_expires = models.DateTimeField(null=True, blank=True, verbose_name='验证码过期时间')
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        swappable = 'AUTH_USER_MODEL'
        
    def __str__(self):
        if self.username and self.user_type == 'admin':
            return f"{self.username} ({self.email})"
        return self.email
    
    def save(self, *args, **kwargs):
        # 如果是管理员用户，必须有用户名
        if self.user_type == 'admin' and not self.username:
            self.username = self.email.split('@')[0]  # 使用邮箱前缀作为默认用户名
        elif self.user_type == 'user':
            self.username = None  # 普通用户不能有用户名
        super().save(*args, **kwargs)
    
    def set_email_verification_code(self, code):
        """设置邮箱验证码"""
        self.email_verification_code = code
        self.email_verification_code_expires = timezone.now() + timedelta(minutes=5)
        self.save()
    
    def check_email_verification_code(self, code):
        """检查邮箱验证码"""
        if not self.email_verification_code or not self.email_verification_code_expires:
            return False
        if timezone.now() > self.email_verification_code_expires:
            return False
        return self.email_verification_code == code
    
    def is_banned(self):
        """检查用户是否被封禁"""
        if self.status != 'banned':
            return False
        if not self.ban_until:  # 永久封禁
            return True
        return timezone.now() < self.ban_until  # 检查临时封禁是否过期
    
    def get_ban_status(self):
        """获取封禁状态信息"""
        if not self.is_banned():
            return None
        if not self.ban_until:
            return "永久封禁"
        return f"封禁至 {self.ban_until.strftime('%Y-%m-%d %H:%M')}"
