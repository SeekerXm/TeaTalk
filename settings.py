# 邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 465  # 使用SSL
EMAIL_HOST_USER = 'seekerxm@163.com'  # 修正邮箱地址格式
EMAIL_HOST_PASSWORD = 'BYj37SAmu7MQWtHx'  # 授权码
EMAIL_USE_SSL = True  # 使用SSL
EMAIL_USE_TLS = False  # 不使用TLS
DEFAULT_FROM_EMAIL = 'TeaTalk <seekerxm@163.com>'  # 添加发件人名称

# 认证配置
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # 默认的认证后端
]

# 自定义用户模型
AUTH_USER_MODEL = 'users.User'  # 确保这行配置正确

SIMPLEUI_CONFIG = {
    'system_keep': True,
    'menu_display': ['用户管理', '公告管理'],
    'dynamic': False,
    'menus': [
        {
            'name': '系统概览',
            'icon': 'fas fa-home',
            'url': '/admin/home/',
        },
        {
            'name': '用户管理',
            'icon': 'fas fa-users',
            'models': [
                {
                    'name': '用户列表',
                    'url': '/admin/users/user/',
                    'icon': 'fas fa-user'
                }
            ]
        },
        {
            'name': '公告管理',
            'icon': 'fas fa-bullhorn',
            'models': [
                {
                    'name': '公告列表',
                    'url': '/admin/announcements/announcement/',
                    'icon': 'fas fa-scroll'
                }
            ]
        }
    ]
}