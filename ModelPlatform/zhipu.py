from zhipuai import ZhipuAI
from django.conf import settings

class ZhipuPlatform:
    def __init__(self):
        self.client = ZhipuAI(api_key=settings.ZHIPU_API_KEY)
        self.default_system_message = {
            "role": "system", 
            "content": "你是智谱AI助手，你的任务是详细回答用户的问题。"
        }

    def chat(self, message):
        """
        发送单条消息到智谱AI并获取响应
        :param message: 用户消息文本
        :return: AI响应的文本内容
        """
        try:
            messages = [
                self.default_system_message,
                {"role": "user", "content": message}
            ]
            
            response = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=messages
            )
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"智谱AI调用出错: {str(e)}")
            raise Exception(f"AI服务暂时不可用: {str(e)}") 