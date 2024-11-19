"""
Django settings for TeaTalk project.

Generated by 'django-admin startproject' using Django 4.2.16.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-oz#n%1%+eu#)#zz5_zs542n!d=lq9sdbd(cc#y7&ga-9juj!g#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'simpleui',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users.apps.UsersConfig',
    'announcements.apps.AnnouncementsConfig',
    'captcha',
    'mdeditor',
    'chat.apps.ChatConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'TeaTalk.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'TeaTalk.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ai_chat_assistant',
        'USER': 'root',
        'PASSWORD': 'mxm123456',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 邮箱配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'seekerxm@163.com'
EMAIL_HOST_PASSWORD = 'BYj37SAmu7MQWtHx'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

AUTH_USER_MODEL = 'users.User'

# Simple UI 配置
SIMPLEUI_CONFIG = {
    'system_keep': False,
    'menu_display': ['用户管理', '公告管理'],
    'dynamic': False,
    'menus': [{
        'name': '用户管理',
        'icon': 'fas fa-users',
        'models': [{
            'name': '用户列表',
            'icon': 'fas fa-user',
            'url': '/admin/users/user/',
            'add_url': None,
            'add_button': False,
            'icon_actions': []
        }]
    }, {
        'name': '公告管理',
        'icon': 'fas fa-bullhorn',
        'models': [{
            'name': '公告列表',
            'icon': 'fas fa-scroll',
            'url': '/admin/announcements/announcement/'
        }]
    }]
}

# Simple UI 其他设置
SIMPLEUI_DEFAULT_THEME = 'admin.lte.css'
SIMPLEUI_LOGO = '/static/images/favicon.png'
SIMPLEUI_TITLE = 'TeaTalk AI 聊天助手'
SIMPLEUI_HOME_INFO = False
SIMPLEUI_ANALYSIS = False
SIMPLEUI_HOME_QUICK = False
SIMPLEUI_HOME_ACTION = False
SIMPLEUI_STATIC_OFFLINE = True
SIMPLEUI_ICON = {
    '用户管理': 'fas fa-users',
    '公告管理': 'fas fa-bullhorn',
    '用户列表': 'fas fa-user',
    '公告列表': 'fas fa-scroll'
}

# 禁用所有快速操作按钮
SIMPLEUI_QUICK_BUTTON = False
SIMPLEUI_IMPORT_EXPORT_BUTTON = False
SIMPLEUI_ADD_BUTTON = False

# 添加以下配置
SIMPLEUI_ACTION_ITEMS = []
SIMPLEUI_QUICK_ACTIONS = []

# 认证后端配置
AUTHENTICATION_BACKENDS = [
    'users.backends.EmailOrUsernameModelBackend',  # 自定义的认证后端
    'django.contrib.auth.backends.ModelBackend',  # 保留默认的认证后端作为备用
]

# 自定义首页
SIMPLEUI_HOME_PAGE = '/admin/home/'  # 自定义首页URL
SIMPLEUI_HOME_TITLE = '系统概览'  # 首页标题
SIMPLEUI_HOME_ICON = 'fa fa-dashboard'  # 首页图标
SIMPLEUI_CUSTOM_DASHBOARD = True  # 启用自定义仪表盘

# 添加 Captcha 配置
CAPTCHA_LENGTH = 4  # 验证码长度
CAPTCHA_TIMEOUT = 5  # 验证码过期时间（分钟）
CAPTCHA_IMAGE_SIZE = (100, 30)  # 验证码图片大小
CAPTCHA_FONT_SIZE = 28  # 验证码字体大小

# Markdown编辑器配置
MDEDITOR_CONFIGS = {
    'default': {
        'width': '100%',  # 编辑器宽度
        'height': 500,    # 编辑器高度
        'toolbar': ["undo", "redo", "|",
                   "bold", "del", "italic", "quote", "ucwords", "uppercase", "lowercase", "|",
                   "h1", "h2", "h3", "h5", "h6", "|",
                   "list-ul", "list-ol", "hr", "|",
                   "link", "reference-link", "image", "code", "preformatted-text", "code-block", "table", "datetime",
                   "emoji", "html-entities", "pagebreak", "goto-line", "|",
                   "help", "info",
                   "||", "preview", "watch", "fullscreen"],
        'upload_image_formats': ["jpg", "jpeg", "gif", "png", "bmp", "webp"],  # 图片上传格式类型
        'image_folder': 'editor',  # 图片保存文件夹名称
        'theme': 'default',  # 编辑器主题
        'preview_theme': 'default',  # 预览区域主题
        'editor_theme': 'default',  # edit区域主题
        'toolbar_autofixed': True,  # 工具栏是否吸顶
        'search_replace': True,  # 是否开启查找替换
        'emoji': True,  # 是否开启表情功能
        'tex': True,  # 是否开启 tex 图表功能
        'flow_chart': True,  # 是否开启流程图功能
        'sequence': True,  # 是否开启序列图功能
        'watch': True,  # 实时预览
        'lineWrapping': False,  # 自动换行
        'lineNumbers': True  # 显示行号
    }
}
