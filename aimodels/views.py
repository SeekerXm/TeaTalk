from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import AIModel, UserModel

@login_required
def get_available_models(request):
    """获取当前用户可用的模型列表"""
    try:
        # 获取所有启用的模型
        active_models = AIModel.objects.filter(is_active=True).order_by('weight')
        
        # 如果用户已登录，检查用户特定的模型权限
        if request.user.is_authenticated:
            user_models = UserModel.objects.filter(user=request.user).first()
            
            if user_models and not user_models.use_all_models:
                # 如果用户没有使用所有模型的权限，则过滤出允许使用的模型
                allowed_model_ids = [model.id for model in user_models.allowed_models.all()]
                active_models = active_models.filter(id__in=allowed_model_ids)
        
        # 添加调试日志
        print(f"获取到的活动模型数量: {active_models.count()}")
        
        models_data = [{
            'id': model.id,
            'name': model.model_name,
            'type': model.model_type,
            'platform': model.get_platform_display(),
            'weight': model.weight,
            'original_name': model.original_model_name or model.model_name
        } for model in active_models]
        
        # 添加调试日志
        print(f"返回的模型数据: {models_data}")
        
        return JsonResponse({
            'success': True,
            'models': models_data
        })
        
    except Exception as e:
        print(f"获取模型列表时出错: {str(e)}")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误详情: {e.args}")
        return JsonResponse({
            'success': False,
            'message': '获取模型列表失败'
        }, status=500) 