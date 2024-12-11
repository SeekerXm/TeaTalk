from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('send/', views.send_message, name='send_message'),
    path('available-models/', views.get_available_models, name='available_models'),
    path('create-conversation/', views.create_conversation, name='create_conversation'),
    path('conversations/', views.get_conversations, name='get_conversations'),
    path('delete-conversation/<int:conversation_id>/', views.delete_conversation, name='delete_conversation'),
]