from django import forms
from django.core.exceptions import ValidationError
from captcha.fields import CaptchaField
from .models import User
from .utils import validate_password_strength, validate_email_domain

class RegisterForm(forms.Form):
    email = forms.EmailField(label='邮箱')
    password1 = forms.CharField(label='密码', widget=forms.PasswordInput)
    password2 = forms.CharField(label='确认密码', widget=forms.PasswordInput)
    captcha = CaptchaField(label='验证码')
    email_code = forms.CharField(label='邮箱验证码', max_length=6)
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if not validate_email_domain(email):
            raise ValidationError('仅支持QQ邮箱、网易邮箱、新浪邮箱和126邮箱')
        if User.objects.filter(email=email).exists():
            raise ValidationError('该邮箱已被注册')
        return email
    
    def clean_password1(self):
        password = self.cleaned_data['password1']
        if not validate_password_strength(password):
            raise ValidationError('密码需要包含小写字母、大写字母、数字、特殊字符中的至少三类')
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('两次输入的密码不一致')
        return cleaned_data

class LoginForm(forms.Form):
    email = forms.EmailField(label='邮箱')
    password = forms.CharField(label='密码', widget=forms.PasswordInput)

class ResetPasswordForm(forms.Form):
    email = forms.EmailField(label='邮箱')
    email_code = forms.CharField(label='邮箱验证码', max_length=6)
    password1 = forms.CharField(label='新密码', widget=forms.PasswordInput)
    password2 = forms.CharField(label='确认新密码', widget=forms.PasswordInput)
    
    def clean_password1(self):
        password = self.cleaned_data['password1']
        if not validate_password_strength(password):
            raise ValidationError('密码需要包含小写字母、大写字母、数字、特殊字符中的至少三类')
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('两次输入的密码不一致')
        return cleaned_data 