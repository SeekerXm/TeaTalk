# 邮件配置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.163.com'
EMAIL_PORT = 465  # 使用SSL
EMAIL_HOST_USER = 'seekerxm@163.com'  # 修正邮箱地址格式
EMAIL_HOST_PASSWORD = 'BYj37SAmu7MQWtHx'  # 授权码
EMAIL_USE_SSL = True  # 使用SSL
EMAIL_USE_TLS = False  # 不使用TLS
DEFAULT_FROM_EMAIL = 'TeaTalk <seekerxm@163.com>'  # 添加发件人名称