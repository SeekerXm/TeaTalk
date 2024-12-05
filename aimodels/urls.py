from django.urls import path
from . import views

app_name = 'aimodels'

urlpatterns = [
    path('models/available/', views.get_available_models, name='available-models'),
    path('models/change-weight/<int:model_id>/<str:direction>/', views.change_model_weight, name='change-model-weight'),
]