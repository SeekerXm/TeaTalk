import requests
import json
from django.conf import settings

class SiliconBasePlatform:
    """SiliconCloud 基础平台类"""
    def __init__(self, model_name, system_message):
        self.url = "https://api.siliconflow.cn/v1/chat/completions"
        self.api_key = settings.SILICON_API_KEY
        self.model_name = model_name
        self.messages = [
            {
                "role": "system",
                "content": system_message
            }
        ]

    def chat(self, message):
        try:
            self.messages.append({
                "role": "user",
                "content": message
            })
            
            payload = {
                "model": self.model_name,
                "messages": self.messages
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(self.url, json=payload, headers=headers)
            
            if response.status_code == 200:
                response_data = response.json()
                ai_response = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                self.messages.append({
                    "role": "assistant",
                    "content": ai_response
                })
                
                return ai_response
            else:
                raise Exception(f"API请求失败: {response.status_code} - {response.text}")
            
        except Exception as e:
            print(f"SiliconCloud调用出错: {str(e)}")
            raise Exception(f"AI服务暂时不可用: {str(e)}")

class SiliconCoderPlatform(SiliconBasePlatform):
    """Qwen2.5-Coder-7B 模型"""
    def __init__(self):
        super().__init__(
            model_name="Qwen/Qwen2.5-Coder-7B-Instruct",
            system_message="你好，我是Qwen2.5-Coder-7B-Instruct模型AI小助手，我擅长写代码，请问有什么可以帮助您吗？"
        )

class SiliconChatPlatform(SiliconBasePlatform):
    """Qwen2.5-7B 模型"""
    def __init__(self):
        super().__init__(
            model_name="Qwen/Qwen2.5-7B-Instruct",
            system_message="你好，我是Qwen2.5-7B-Instruct模型AI小助手，请问有什么可以帮助您吗？"
        ) 