from ModelPlatform import SparkApi
from django.conf import settings

class SparkPlatform:
    def __init__(self):
        self.appid = None
        self.api_key = None
        self.api_secret = None
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
            if not all([self.appid, self.api_key, self.api_secret]):
                raise Exception("星火AI配置不完整")

            # 添加用户消息到对话历史
            self.text.append({"role": "user", "content": message})
            
            # 检查并控制对话历史长度
            while self.get_length(self.text) > 8000:
                del self.text[1]
            
            # 调用星火API
            SparkApi.answer = ""
            try:
                SparkApi.main(
                    self.appid,
                    self.api_key,
                    self.api_secret,
                    self.spark_url,
                    self.domain,
                    self.text
                )
                response = SparkApi.answer
                if not response:
                    raise Exception("未获取到有效响应")
                
                # 添加助手响应到对话历史
                self.text.append({"role": "assistant", "content": response})
                return response
                
            except Exception as api_error:
                print(f"星火API调用失败: {str(api_error)}")
                if "Ensure" in str(api_error):  # 处理 WebSocket 配置错误
                    raise Exception("网络连接错误，请稍后重试")
                raise Exception(f"星火API调用失败: {str(api_error)}")
            
        except Exception as e:
            print(f"星火AI调用出错: {str(e)}")
            raise Exception(f"AI服务暂时不可用: {str(e)}")
    
    def get_length(self, text):
        """计算文本总长度"""
        total_length = 0
        for item in text:
            if isinstance(item, dict) and "content" in item:
                total_length += len(item["content"])
        return total_length 