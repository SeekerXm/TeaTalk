from ModelPlatform import SparkApi
from django.conf import settings

class SparkPlatform:
    def __init__(self):
        self.appid = settings.SPARK_APPID
        self.api_key = settings.SPARK_API_KEY
        self.api_secret = settings.SPARK_API_SECRET
        self.domain = "lite"
        self.spark_url = "wss://spark-api.xf-yun.com/v1.1/chat"
        self.text = [
            {"role": "system", "content": "你是星火小助手！你的任务是详细回答用户的问题。"}
        ]

    def chat(self, message):
        """
        发送单条消息到星火AI并获取响应
        :param message: 用户消息文本
        :return: AI响应的文本内容
        """
        try:
            # 添加用户消息到对话历史
            self.text.append({"role": "user", "content": message})
            
            # 检查并控制对话历史长度
            while self.get_length(self.text) > 8000:
                del self.text[0]
            
            # 调用星火API
            SparkApi.answer = ""
            SparkApi.main(
                self.appid,
                self.api_key,
                self.api_secret,
                self.spark_url,
                self.domain,
                self.text
            )
            
            # 获取响应
            response = SparkApi.answer
            
            # 添加助手响应到对话历史
            self.text.append({"role": "assistant", "content": response})
            
            return response
            
        except Exception as e:
            print(f"星火AI调用出错: {str(e)}")
            raise Exception(f"AI服务暂时不可用: {str(e)}")
    
    def get_length(self, text):
        """计算对话历史的总长度"""
        length = 0
        for content in text:
            temp = content["content"]
            length += len(temp)
        return length 