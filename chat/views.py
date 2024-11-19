from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ModelPlatform.zhipu import ZhipuPlatform

@login_required
def send_message(request):
    """处理发送消息的请求"""
    try:
        message = request.POST.get('message')
        
        if not message:
            return JsonResponse({
                'success': False,
                'message': '消息不能为空'
            })
        
        # 调用智谱AI获取响应
        platform = ZhipuPlatform()
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