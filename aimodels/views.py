from django.http import JsonResponse
from .models import AIModel

def get_models(request):
    """获取已启用的模型列表"""
    models = AIModel.objects.filter(is_active=True).order_by('weight')
    model_list = [{
        'id': model.id,
        'name': model.model_name,
        'type': model.model_type,
        'platform': model.platform,
        'weight': model.weight
    } for model in models]
    
    return JsonResponse({'models': model_list}) 