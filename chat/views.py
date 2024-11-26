from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from aimodels.models import AIModel  # 导入 AIModel
from ModelPlatform.zhipu import ZhipuPlatform
from ModelPlatform.spark import SparkPlatform
from ModelPlatform.qianfan import QianfanPlatform
from ModelPlatform.silicon import (
    SiliconCoderPlatform, 
    SiliconChatPlatform, 
    SiliconGLMPlatform,
    SiliconGemmaPlatform
)

@login_required
def send_message(request):
    """处理发送消息的请求"""
    try:
        message = request.POST.get('message')
        model_id = request.POST.get('model')  # 获取模型ID
        messages = request.POST.get('messages')
        
        if not message:
            return JsonResponse({
                'success': False,
                'message': '消息不能为空'
            })
        
        # 从数据库获取模型配置
        try:
            model = AIModel.objects.get(id=model_id, is_active=True)
        except AIModel.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '模型不存在或已停用'
            })
        
        # 根据模型平台调用相应的AI服务
        platform = None
        if model.platform == 'bigmodel':
            platform = ZhipuPlatform(api_key=model.config.get('ZHIPU_API_KEY'))
        elif model.platform == 'spark':
            platform = SparkPlatform(
                app_id=model.config.get('SPARK_APPID'),
                api_key=model.config.get('SPARK_API_KEY'),
                api_secret=model.config.get('SPARK_API_SECRET')
            )
        elif model.platform == 'qianfan':
            platform = QianfanPlatform(
                access_key=model.config.get('QIANFAN_ACCESS_KEY'),
                secret_key=model.config.get('QIANFAN_SECRET_KEY')
            )
        elif model.platform == 'silicon':
            platform = SiliconPlatform(api_key=model.config.get('SILICON_API_KEY'))
        
        if not platform:
            return JsonResponse({
                'success': False,
                'message': '不支持的模型平台'
            })
        
        response = platform.chat(message, messages)
        
        return JsonResponse({
            'success': True,
            'response': response
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }) 