from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
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
        model = request.POST.get('model', 'glm-4-flash')
        messages = request.POST.get('messages')  # 获取消息历史
        
        if not message:
            return JsonResponse({
                'success': False,
                'message': '消息不能为空'
            })
        
        # 根据选择的模型调用相应的AI平台
        if model == 'glm-4-flash':
            platform = ZhipuPlatform()
            response = platform.chat(message)
        elif model == 'spark-lite':
            platform = SparkPlatform()
            response = platform.chat(message)
        elif model == 'yi-34b':
            platform = QianfanPlatform()
            response = platform.chat(message, messages)  # 传递消息历史
        elif model == 'qwen-coder':
            platform = SiliconCoderPlatform()
            response = platform.chat(message)
        elif model == 'qwen-chat':
            platform = SiliconChatPlatform()
            response = platform.chat(message)
        elif model == 'chatglm3':
            platform = SiliconGLMPlatform()
            response = platform.chat(message)
        elif model == 'gemma-it':
            platform = SiliconGemmaPlatform()
            response = platform.chat(message)
        else:
            return JsonResponse({
                'success': False,
                'message': '不支持的模型类型'
            })
        
        return JsonResponse({
            'success': True,
            'response': response
        })
        
    except Exception as e:
        print(f"发送消息失败: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }) 