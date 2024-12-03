from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('reset-password/', views.reset_password, name='reset-password'),
    path('verify-captcha/', views.verify_captcha, name='verify-captcha'),
    path('send-email-code/', views.send_email_code, name='send-email-code'),
    path('captcha/refresh/', views.refresh_captcha, name='captcha-refresh'),
    path('announcement/<int:announcement_id>/', views.get_announcement, name='get-announcement'),
    path('mark-announcement-read/<int:announcement_id>/', views.mark_announcement_read, name='mark-announcement-read'),
    path('change_password/', views.change_password, name='change_password'),
] 