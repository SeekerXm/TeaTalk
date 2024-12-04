from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from aimodels.models import AIModel
from ModelPlatform.spark import SparkPlatform

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
            platform.appid = model.config.get('SPARK_APPID')
            platform.api_key = model.config.get('SPARK_API_KEY')
            platform.api_secret = model.config.get('SPARK_API_SECRET')
            platform.version = model.version  # 设置版本
            
            # 调用AI接口
            response = platform.chat(message)
            return JsonResponse({'success': True, 'response': response})
            
        else:
            return JsonResponse({'success': False, 'message': '不支持的模型平台'})
            
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'发送失败: {str(e)}'}) 