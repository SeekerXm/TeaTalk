from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ModelPlatform.zhipu import ZhipuPlatform
from ModelPlatform.spark import SparkPlatform

@login_required
def send_message(request):
    """处理发送消息的请求"""
    try:
        message = request.POST.get('message')
        model = request.POST.get('model', 'glm-4-flash')  # 默认使用智谱AI
        
        if not message:
            return JsonResponse({
                'success': False,
                'message': '消息不能为空'
            })
        
        # 根据选择的模型调用相应的AI平台
        if model == 'glm-4-flash':
            platform = ZhipuPlatform()
        elif model == 'spark-lite':
            platform = SparkPlatform()
        else:
            return JsonResponse({
                'success': False,
                'message': '不支持的模型类型'
            })
        
        response = platform.chat(message)
        
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