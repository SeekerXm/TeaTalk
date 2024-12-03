"""
URL configuration for TeaTalk project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from users import views as user_views
from chat import views as chat_views

admin.site.site_header = 'TeaTalk AI 聊天助手'
admin.site.site_title = 'TeaTalk AI 聊天助手'
admin.site.index_title = '管理后台'

urlpatterns = [
    path('', user_views.index, name='index'),
    path('verify-captcha/', user_views.verify_captcha, name='verify_captcha'),
    path('send-email-code/', user_views.send_email_code, name='send_email_code'),
    path('register/', user_views.register, name='register'),
    path('login/', user_views.user_login, name='login'),
    path('logout/', user_views.user_logout, name='logout'),
    path('reset-password/', user_views.reset_password, name='reset_password'),
    path('captcha/', include('captcha.urls')),
    path('admin/home/', user_views.home, name='admin_home'),
    path('admin/', admin.site.urls),
    path('captcha/refresh/', user_views.refresh_captcha, name='captcha-refresh'),
    path('announcement/<int:announcement_id>/', user_views.get_announcement, name='get-announcement'),
    path('mark-announcement-read/<int:announcement_id>/', user_views.mark_announcement_read, name='mark-announcement-read'),
    path('mdeditor/', include('mdeditor.urls')),
    path('change-password/', user_views.change_password, name='change-password'),
    path('delete-account/', user_views.delete_account, name='delete-account'),
    path('chat/send/', chat_views.send_message, name='send_message'),
    path('api/', include('aimodels.urls')),
    path('', include('users.urls')),
    path('users/', include('users.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
