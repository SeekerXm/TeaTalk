from django.http import JsonResponse
from .models import AIModel

def get_models(request):
    """获取已启用的模型列表"""
    # 定义类型映射字典
    TYPE_MAPPING = {
        'chat': '对话',
        'image': '图像'
    }
    
    # 定义平台映射字典
    PLATFORM_MAPPING = {
        'bigmodel': 'BigModel',
        'qianfan': '百度千帆',
        'spark': '讯飞星火',
        'silicon': 'SiliconCloud'
    }
    
    models = AIModel.objects.filter(is_active=True).order_by('weight')
    model_list = [{
        'id': model.id,
        'name': model.model_name,
        'type': TYPE_MAPPING.get(model.model_type, model.model_type),  # 转换为中文显示
        'platform': PLATFORM_MAPPING.get(model.platform, model.platform),  # 使用映射的平台名称
        'weight': model.weight
    } for model in models]
    
    return JsonResponse({'models': model_list}) 