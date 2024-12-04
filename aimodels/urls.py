from django.urls import path
from . import views

app_name = 'aimodels'

urlpatterns = [
    path('available-models/', views.get_available_models, name='available-models'),
] 