import requests
import json
from django.conf import settings

class SiliconPlatform:
    def __init__(self):
        self.url = "https://api.siliconflow.cn/v1/chat/completions"
        self.api_key = settings.SILICON_API_KEY
        self.messages = [
            {
                "role": "system",
                "content": "你好，我是Qwen2.5-Coder-7B-Instruct模型AI小助手，我擅长写代码，请问有什么可以帮助您吗？"
            }
        ]

    def chat(self, message):
        """
        发送消息到SiliconCloud并获取响应
        :param message: 用户消息文本
        :return: AI响应的文本内容
        """
        try:
            # 添加用户消息
            self.messages.append({
                "role": "user",
                "content": message
            })
            
            payload = {
                "model": "Qwen/Qwen2.5-Coder-7B-Instruct",
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
                
                # 添加AI响应到消息历史
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