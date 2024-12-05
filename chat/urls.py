from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('send/', views.send_message, name='send_message'),
    path('available-models/', views.get_available_models, name='available_models'),
]