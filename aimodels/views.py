from django.http import JsonResponse
from .models import AIModel

def get_available_models(request):
    """获取可用的模型列表"""
    try:
        models = AIModel.objects.filter(
            is_active=True,
            platform='spark'  # 目前只返回星火平台的模型
        ).order_by('weight')
        
        model_list = [{
            'id': model.id,
            'name': model.model_name,
            'platform': model.get_platform_display()
        } for model in models]
        
        return JsonResponse({
            'success': True,
            'models': model_list
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }) 