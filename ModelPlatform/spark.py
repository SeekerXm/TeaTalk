import json
import _thread as thread
import websocket
import datetime
import hmac
import base64
from urllib.parse import urlparse, quote
import hashlib
from time import mktime
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import logging

logger = logging.getLogger(__name__)

class SparkPlatform:
    """星火认知大模型平台适配器"""
    
    # 定义版本和URL的映射关系
    API_VERSIONS = {
        'lite': {
            'url': 'wss://spark-api.xf-yun.com/v1.1/chat',
            'domain': 'lite',
            'description': 'Spark Lite版本'
        },
        'pro': {
            'url': 'wss://spark-api.xf-yun.com/v3.1/chat',
            'domain': 'generalv3',
            'description': 'Spark Pro版本'
        },
        'pro-128k': {
            'url': 'wss://spark-api.xf-yun.com/chat/pro-128k',
            'domain': 'pro-128k',
            'description': 'Spark Pro-128K版本'
        },
        'max': {
            'url': 'wss://spark-api.xf-yun.com/v3.5/chat',
            'domain': 'generalv3.5',
            'description': 'Spark Max版本'
        },
        'max-32k': {
            'url': 'wss://spark-api.xf-yun.com/chat/max-32k',
            'domain': 'max-32k',
            'description': 'Spark Max-32K版本'
        },
        'ultra': {
            'url': 'wss://spark-api.xf-yun.com/v4.0/chat',
            'domain': '4.0Ultra',
            'description': 'Spark 4.0 Ultra版本'
        }
    }
    
    def __init__(self):
        self.appid = None
        self.api_key = None
        self.api_secret = None
        self.version = 'lite'  # 修改默认版本为 lite
        self.temperature = 0.5
        self.max_tokens = 4096
        self.top_k = 4
        self.messages = []
        self._reset_answer()
    
    @property
    def chat_url(self):
        """根据版本获取对应的URL"""
        return self.API_VERSIONS[self.version]['url']
    
    @property
    def domain(self):
        """根据版本获取对应的domain"""
        return self.API_VERSIONS[self.version]['domain']

    def _reset_answer(self):
        """重置回答"""
        SparkApi.answer = ""

    def _create_url(self):
        """生成鉴权URL"""
        try:
            # 生成RFC1123格式的时间戳
            now = datetime.now()
            date = format_date_time(mktime(now.timetuple()))
            
            # 解析URL
            host = urlparse(self.chat_url).netloc
            path = urlparse(self.chat_url).path
            
            # 拼接待加密字符串
            signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
            
            # 使用hmac-sha256进行加密
            signature_sha = hmac.new(
                self.api_secret.encode('utf-8'),
                signature_origin.encode('utf-8'),
                digestmod=hashlib.sha256
            ).digest()
            
            # Base64编码
            signature_sha_base64 = base64.b64encode(signature_sha).decode()
            authorization_origin = f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
            authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode()
            
            # URL 参数编码
            authorization = quote(authorization)
            date = quote(date)
            host = quote(host)
            
            # 拼接最终URL
            url = f'{self.chat_url}?authorization={authorization}&date={date}&host={host}'
            return url
        except Exception as e:
            logger.error(f"生成鉴权URL失败: {str(e)}")
            raise Exception("生成鉴权URL失败") from e

    def _prepare_messages(self, message):
        """准备发送的消息"""
        # 添加用户消息
        self.messages.append({"role": "user", "content": message})
        
        # 控制对话长度，保留最近的10轮对话
        if len(self.messages) > 20:
            self.messages = self.messages[-20:]
            
        return self.messages

    def _generate_params(self, messages):
        """生成请求参数，根据不同版本可能有不同的参数结构"""
        # 获取版本配置
        version_config = self.API_VERSIONS.get(self.version)
        if not version_config:
            raise ValueError(f"不支持的版本: {self.version}")

        params = {
            "header": {
                "app_id": self.appid,
                "uid": "user_default"
            },
            "parameter": {
                "chat": {
                    "domain": version_config['domain'],
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                    "top_k": self.top_k,
                    "chat_id": datetime.now().strftime("%Y%m%d%H%M%S"),
                }
            },
            "payload": {
                "message": {
                    "text": messages
                }
            }
        }
        
        # 根据版本添加特定参数
        if self.version in ['pro', 'pro-128k', 'max', 'max-32k', 'ultra']:
            params['parameter']['chat'].update({
                'auditing': 'default',
            })
            
        # 如果是长文本版本，增加最大token数
        if self.version in ['pro-128k']:
            params['parameter']['chat']['max_tokens'] = 128000
        elif self.version in ['max-32k']:
            params['parameter']['chat']['max_tokens'] = 32000
        
        return params

    def chat(self, message):
        """
        发送消息到星火平台并获取响应
        :param message: 用户消息文本
        :return: AI响应的文本内容
        """
        try:
            # 验证配置
            if not all([self.appid, self.api_key, self.api_secret]):
                raise ValueError("星火AI配置不完整，请检查appid、api_key和api_secret")

            # 准备消息
            messages = self._prepare_messages(message)
            
            # 重置回答
            self._reset_answer()
            
            # 创建WebSocket连接
            ws = websocket.WebSocketApp(
                self._create_url(),
                on_message=SparkApi.on_message,
                on_error=SparkApi.on_error,
                on_close=SparkApi.on_close,
                on_open=SparkApi.on_open
            )
            
            # 设置当前会话的参数
            SparkApi.params = self._generate_params(messages)
            
            # 运行WebSocket连接
            ws.run_forever()
            
            # 获取响应
            response = SparkApi.answer.strip()
            if not response:
                raise Exception("未获取到有效响应")
            
            # 添加助手响应到对话历史
            self.messages.append({"role": "assistant", "content": response})
            
            return response
            
        except ValueError as ve:
            logger.error(f"参数错误: {str(ve)}")
            raise
        except websocket.WebSocketException as we:
            logger.error(f"WebSocket连接错误: {str(we)}")
            raise Exception("网络连接错误，请稍后重试") from we
        except Exception as e:
            logger.error(f"星火AI调用出错: {str(e)}")
            raise Exception(f"AI服务暂时不可用: {str(e)}") from e

class SparkApi:
    """星火WebSocket API处理类"""
    
    answer = ""
    params = None

    @staticmethod
    def on_error(ws, error):
        """处理WebSocket错误"""
        logger.error(f"WebSocket错误: {str(error)}")
        if hasattr(error, 'status_code'):
            logger.error(f"状态码: {error.status_code}")
        if hasattr(error, 'headers'):
            logger.error(f"响应头: {error.headers}")
        if hasattr(error, 'response'):
            logger.error(f"响应内容: {error.response}")

    @staticmethod
    def on_close(ws, close_status_code, close_reason):
        """处理WebSocket关闭"""
        logger.info(f"WebSocket连接关闭: {close_status_code} - {close_reason}")

    @staticmethod
    def on_open(ws):
        """处理WebSocket连接打开"""
        def run():
            data = json.dumps(SparkApi.params)
            logger.debug(f"发送数据: {data}")
            ws.send(data)
        thread.start_new_thread(run, ())

    @staticmethod
    def on_message(ws, message):
        """处理WebSocket消息"""
        try:
            data = json.loads(message)
            logger.debug(f"收到消息: {data}")
            
            code = data['header']['code']
            if code != 0:
                logger.error(f"请求错误: {code}, {data}")
                ws.close()
                return
                
            choices = data["payload"]["choices"]
            status = choices["status"]
            content = choices["text"][0]["content"]
            
            SparkApi.answer += content
            
            if status == 2:
                ws.close()
                
        except Exception as e:
            logger.error(f"处理消息时出错: {str(e)}")
            if isinstance(e, json.JSONDecodeError):
                logger.error(f"原始消息: {message}")
            ws.close()