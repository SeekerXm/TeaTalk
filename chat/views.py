from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from aimodels.models import AIModel
from ModelPlatform.spark import SparkPlatform

def get_available_models(request):
    """获取可用的模型列表"""
    try:
        # 获取所有已启用的模型
        models = AIModel.objects.filter(is_active=True)
        
        # 准备基本的模型信息
        models_data = [{
            'id': model.id,
            'name': model.model_name,
            'platform': model.get_platform_display(),
            'version': model.get_version_display(),
            'type': model.model_type
        } for model in models]
        
        # 如果用户已登录，检查用户特定的权限
        if request.user.is_authenticated:
            user_model = request.user.user_models
            if not user_model.use_all_models:
                # 过滤出用户可用的模型
                allowed_model_ids = user_model.models.values_list('id', flat=True)
                models_data = [model for model in models_data if model['id'] in allowed_model_ids]
        
        return JsonResponse({
            'success': True,
            'models': models_data,
            'is_authenticated': request.user.is_authenticated
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'获取模型列表失败: {str(e)}'
        })

@login_required
def send_message(request):
    """处理发送消息的请求"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': '仅支持POST请求'})
        
    try:
        message = request.POST.get('message', '').strip()
        model_id = request.POST.get('model')
        
        if not message:
            return JsonResponse({'success': False, 'message': '消息不能为空'})
            
        # 获取模型配置
        try:
            model = AIModel.objects.get(id=model_id, is_active=True)
        except AIModel.DoesNotExist:
            return JsonResponse({'success': False, 'message': '选择的模型不可用'})
            
        # 根据平台创建对应的实例
        if model.platform == 'spark':
            platform = SparkPlatform()
            # 从配置中获取密钥信息
            config = model.config or {}
            platform.appid = config.get('SPARK_APPID', '').strip()
            platform.api_key = config.get('SPARK_API_KEY', '').strip()
            platform.api_secret = config.get('SPARK_API_SECRET', '').strip()
            
            # 验证配置完整性
            if not all([platform.appid, platform.api_key, platform.api_secret]):
                return JsonResponse({'success': False, 'message': '模型配置不完整，请检查APPID和密钥信息'})
            
            # 设置正确的版本（不带v前缀）
            platform.version = model.version
            
            try:
                # 调用AI接口
                response = platform.chat(message)
                return JsonResponse({'success': True, 'response': response})
            except Exception as e:
                return JsonResponse({'success': False, 'message': f'调用AI接口失败: {str(e)}'})
            
        else:
            return JsonResponse({'success': False, 'message': '不支持的模型平台'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'发送失败: {str(e)}'})