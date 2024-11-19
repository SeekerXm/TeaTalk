from ModelPlatform.base_platform import BasePlatform
from websocket import create_connection
from websocket._app import WebSocketApp
import ssl
import json
import time
import base64
import hmac
import _thread as thread
from datetime import datetime
from urllib.parse import urlencode, quote
from email.utils import formatdate
from time import mktime

class SparkPlatform(BasePlatform):
    """讯飞星火平台实现类"""
    
    def __init__(self, app_id, api_key, api_secret):
        super().__init__()
        self.app_id = app_id
        self.api_key = api_key
        self.secret_key = api_secret
        self.base_url = "wss://spark-api.xf-yun.com/v1.1/chat"
        self.domain = "lite"  # 默认使用lite版本
        self.answer = ""  # 存储回答
    
    def create_url(self):
        """生成鉴权url"""
        # 生成RFC1123格式的时间戳
        date = formatdate(timeval=None, localtime=False, usegmt=True)
        
        # 拼接字符串
        signature_origin = "host: spark-api.xf-yun.com\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v1.1/chat" + " HTTP/1.1"
        
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(
            self.secret_key.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod='SHA256'
        ).digest()
        
        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')
        
        authorization_origin = f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "spark-api.xf-yun.com"
        }
        
        # 拼接鉴权参数
        url = self.base_url + '?' + urlencode(v)
        return url
    
    def on_message(self, ws, message):
        """处理服务器返回的消息"""
        try:
            data = json.loads(message)
            code = data['header']['code']
            if code != 0:
                ws.close()
            else:
                choices = data["payload"]["choices"]
                status = choices["status"]
                content = choices["text"][0]["content"]
                self.answer += content
                
                # 当status为2时，表示响应完成
                if status == 2:
                    self.response_complete = True
                    ws.close()
        except Exception as e:
            ws.close()
    
    def on_error(self, ws, error):
        """处理错误"""
        self.answer = ""  # 清空回答
        self.ws_closed = True
        self.response_complete = False
        ws.close()
    
    def on_close(self, ws, *args):
        """连接关闭"""
        self.ws_closed = True
    
    def on_open(self, ws):
        """连接建立时发送数据"""
        try:
            # 将消息列表转换为适合星火API的格式
            formatted_messages = []
            for msg in self.messages:
                formatted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            data = {
                "header": {
                    "app_id": self.app_id,
                    "uid": "1234"
                },
                "parameter": {
                    "chat": {
                        "domain": self.domain,
                        "temperature": 0.5,
                        "max_tokens": 2048
                    }
                },
                "payload": {
                    "message": {
                        "text": formatted_messages
                    }
                }
            }
            ws.send(json.dumps(data))
        except Exception as e:
            ws.close()
    
    def chat_completion(self, messages, **kwargs):
        """星火文本对话实现"""
        try:
            self.messages = messages  # 保存消息记录
            self.answer = ""  # 清空上次的回答
            self.ws_connected = False  # 添加连接状态标志
            self.ws_closed = False    # 添加关闭状态标志
            self.response_complete = False  # 添加响应完成标志
            
            # 创建WebSocket连接
            ws = WebSocketApp(
                self.create_url(),
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open
            )
            
            # 启动WebSocket连接并等待完成
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            
            # 如果有回答，返回结果
            if self.answer:
                return self.handle_response({
                    'choices': [{
                        'message': {
                            'role': 'assistant',
                            'content': self.answer
                        }
                    }]
                })
            else:
                return self.handle_error(Exception("模型未返回有效回复"))
            
        except Exception as e:
            return self.handle_error(e)
    
    def image_generation(self, prompt, **kwargs):
        """星火平台暂不支持图像生成"""
        raise NotImplementedError("星火平台暂不支持图像生成")