import os
import qianfan
from django.conf import settings
import json

class QianfanPlatform:
    def __init__(self):
        # 设置环境变量
        os.environ["QIANFAN_ACCESS_KEY"] = settings.QIANFAN_ACCESS_KEY
        os.environ["QIANFAN_SECRET_KEY"] = settings.QIANFAN_SECRET_KEY
        self.chat_comp = qianfan.ChatCompletion()

    def chat(self, message, messages=None):
        """
        发送消息到千帆AI并获取响应
        :param message: 用户消息文本
        :param messages: 完整的消息历史
        :return: AI响应的文本内容
        """
        try:
            # 处理消息历史
            if messages:
                # 将消息历史字符串转换为列表
                messages = json.loads(messages)
            else:
                messages = []

            # 确保消息列表以用户消息开始
            if not messages or messages[0]['role'] != 'user':
                messages = [{"role": "user", "content": message}]
            
            # 确保消息数量为奇数
            if len(messages) % 2 == 0:
                messages = messages[:-1]  # 移除最后一条消息
            
            # 调用千帆API
            resp = self.chat_comp.do(
                model="Yi-34B-Chat", 
                messages=messages
            )
            
            # 提取AI响应
            if "body" in resp and "result" in resp["body"]:
                return resp["body"]["result"]
            else:
                raise Exception("API响应格式错误")
            
        except Exception as e:
            print(f"千帆AI调用出错: {str(e)}")
            raise Exception(f"AI服务暂时不可用: {str(e)}") 