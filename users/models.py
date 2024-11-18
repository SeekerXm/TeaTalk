from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from datetime import timedelta

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """创建普通用户，只需要邮箱"""
        if not email:
            raise ValueError('邮箱是必填项')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password=None, **extra_fields):
        """创建超级管理员，需要用户名和邮箱"""
        if not email:
            raise ValueError('邮箱是必填项')
        if not username:
            raise ValueError('用户名是必填项')
            
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')
            
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractUser):
    STATUS_CHOICES = (
        ('normal', '正常'),
        ('warning', '警告'),
        ('banned', '封禁'),
    )
    USER_TYPE_CHOICES = (
        ('admin', '管理员'),
        ('user', '普通用户'),
    )
    
    email = models.EmailField(unique=True, verbose_name='邮箱')
    username = models.CharField(
        max_length=150, 
        unique=True, 
        null=True, 
        blank=True, 
        default='', 
        verbose_name='用户名'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='normal', verbose_name='状态')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='user', verbose_name='用户类型')
    ban_until = models.DateTimeField(null=True, blank=True, verbose_name='封禁截止时间')
    last_login = models.DateTimeField(default=timezone.now, verbose_name='最后登录时间')
    email_verified = models.BooleanField(default=False, verbose_name='邮箱已验证')
    email_verification_code = models.CharField(max_length=6, null=True, blank=True, verbose_name='邮箱验证码')
    email_verification_code_expires = models.DateTimeField(null=True, blank=True, verbose_name='验证码过期时间')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # 创建超级用户时需要用户名
    
    objects = CustomUserManager()
    
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
        if self.user_type == 'admin':
            if not self.username:
                raise ValueError('管理员用户必须设置用户名')
        else:
            # 如果是普通用户，不能有用户名
            self.username = None
            self.user_type = 'user'
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