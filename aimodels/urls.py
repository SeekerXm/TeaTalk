from django.urls import path
from . import views

app_name = 'aimodels'

urlpatterns = [
    path('models/', views.get_models, name='get_models'),
] 