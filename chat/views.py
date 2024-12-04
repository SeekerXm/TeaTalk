from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from aimodels.models import AIModel  # 导入 AIModel
from ModelPlatform.zhipu import ZhipuPlatform
from zhipuai import ZhipuAI  # 添加这行导入
from ModelPlatform.spark import SparkPlatform
from ModelPlatform.qianfan import QianfanPlatform
from ModelPlatform.silicon import SiliconPlatform  # 修改这里，使用基础平台类
import os

@login_required
def send_message(request):
    """处理发送消息的请求"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': '请先登录'
        }, status=403)
    
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
            platform = ZhipuPlatform()
            platform.client = ZhipuAI(api_key=model.config.get('ZHIPU_API_KEY'))
            response = platform.chat(message)  # 智谱AI只需要message参数
        elif model.platform == 'spark':
            platform = SparkPlatform()
            platform.appid = model.config.get('SPARK_APPID')
            platform.api_key = model.config.get('SPARK_API_KEY')
            platform.api_secret = model.config.get('SPARK_API_SECRET')
            response = platform.chat(message)  # 星火AI只需要message参数
        elif model.platform == 'qianfan':
            platform = QianfanPlatform()
            os.environ["QIANFAN_ACCESS_KEY"] = model.config.get('QIANFAN_ACCESS_KEY')
            os.environ["QIANFAN_SECRET_KEY"] = model.config.get('QIANFAN_SECRET_KEY')
            response = platform.chat(message, messages)  # 千帆AI需要message和messages参数
        elif model.platform == 'silicon':
            platform = SiliconPlatform()  # 使用基础平台类
            platform.api_key = model.config.get('SILICON_API_KEY')
            response = platform.chat(message)  # SiliconCloud只需要message参数
        else:
            return JsonResponse({
                'success': False,
                'message': '不支持的模型平台'
            })
        
        return JsonResponse({
            'success': True,
            'response': response
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }) 