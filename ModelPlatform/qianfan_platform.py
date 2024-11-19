import os
import qianfan
import base64
from ModelPlatform.base_platform import BasePlatform

class QianFanPlatform(BasePlatform):
    """百度千帆平台实现类"""
    
    def __init__(self, access_key, secret_key):
        super().__init__()
        self.api_key = access_key
        self.secret_key = secret_key
        os.environ["QIANFAN_ACCESS_KEY"] = access_key
        os.environ["QIANFAN_SECRET_KEY"] = secret_key
        self.chat_client = qianfan.ChatCompletion()
        self.image_client = qianfan.Image2Text()
    
    def chat_completion(self, messages, **kwargs):
        """
        千帆文本对话实现
        默认使用Yi-34B-Chat模型，可通过kwargs传入其他模型
        """
        model = kwargs.get('model', 'Yi-34B-Chat')
        
        # 如果是Fuyu-8B模型，需要特殊处理
        if model == 'Fuyu-8B':
            return self.handle_error(Exception("Fuyu-8B是图像理解模型，请使用image_chat方法"))
            
        try:
            response = self.chat_client.do(
                model=model,
                messages=messages
            )
            
            # 转换千帆的响应格式为统一格式
            return self.handle_response({
                'choices': [{
                    'message': {
                        'role': 'assistant',
                        'content': response.get('result', '')
                    }
                }]
            })
            
        except Exception as e:
            return self.handle_error(e)
    
    def image_chat(self, image_path, prompt=None, **kwargs):
        """
        千帆图像对话实现
        专门用于Fuyu-8B等图像理解模型
        :param image_path: 图片路径
        :param prompt: 问题文本
        """
        try:
            # 读取并编码图片
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
            
            # 调用图像理解接口
            response = self.image_client.do(
                model="Fuyu-8B",
                prompt=prompt,
                image=encoded_string
            )
            
            # 转换响应格式
            return self.handle_response({
                'choices': [{
                    'message': {
                        'role': 'assistant',
                        'content': response.get('result', '')
                    }
                }]
            })
            
        except Exception as e:
            return self.handle_error(e)
    
    def image_generation(self, prompt, **kwargs):
        """千帆平台暂不支持图像生成"""
        raise NotImplementedError("千帆平台暂不支持图像生成")