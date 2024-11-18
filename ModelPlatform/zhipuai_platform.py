from ModelPlatform.base_platform import BasePlatform
from zhipuai import ZhipuAI

class ZhipuAIPlatform(BasePlatform):
    """智谱AI平台实现类"""
    
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.client = ZhipuAI(api_key=api_key)
    
    def chat_completion(self, messages, **kwargs):
        """
        智谱AI文本对话实现
        默认使用glm-4-flash模型，可通过kwargs传入其他模型
        """
        model = kwargs.get('model', 'glm-4-flash')
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages
            )
            # 将响应对象转换为字典
            response_dict = {
                'choices': [{
                    'message': {
                        'content': response.choices[0].message.content
                    }
                }]
            }
            return self.handle_response(response_dict)
        except Exception as e:
            return self.handle_error(e)
    
    def image_generation(self, prompt, **kwargs):
        """智谱AI目前不支持图像生成"""
        raise NotImplementedError("智谱AI平台暂不支持图像生成")