from ModelPlatform.base_platform import BasePlatform
import websocket  # 这里使用的是websocket-client包
import ssl
import json
import _thread as thread
import time
import hmac
import base64
from urllib.parse import urlencode, quote
from datetime import datetime
from time import mktime
from wsgiref.handlers import format_date_time

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
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        
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
        data = json.loads(message)
        code = data['header']['code']
        if code != 0:
            print(f'请求错误: {code}, {data}')
            ws.close()
        else:
            choices = data["payload"]["choices"]
            status = choices["status"]
            content = choices["text"][0]["content"]
            self.answer += content
            if status == 2:
                ws.close()
    
    def on_error(self, ws, error):
        """处理错误"""
        print("错误:", error)
    
    def on_close(self, ws, *args):
        """连接关闭"""
        pass
    
    def on_open(self, ws):
        """连接建立时发送数据"""
        def run(*args):
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
                        "text": self.messages
                    }
                }
            }
            ws.send(json.dumps(data))
        thread.start_new_thread(run, ())
    
    def chat_completion(self, messages, **kwargs):
        """星火文本对话实现"""
        try:
            self.messages = messages  # 保存消息记录
            self.answer = ""  # 清空上次的回答
            
            # 创建WebSocket连接
            ws = websocket.WebSocketApp(
                self.create_url(),
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open
            )
            ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
            
            # 返回处理后的响应
            return self.handle_response({
                'content': self.answer
            })
            
        except Exception as e:
            return self.handle_error(e)
    
    def image_generation(self, prompt, **kwargs):
        """星火平台暂不支持图像生成"""
        raise NotImplementedError("星火平台暂不支持图像生成")