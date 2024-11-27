import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode, urlparse
from wsgiref.handlers import format_date_time
import websocket

answer = ""

class SparkApi:
    def __init__(self, appid, api_key, api_secret, spark_url, domain):
        self.appid = appid
        self.api_key = api_key
        self.api_secret = api_secret
        self.spark_url = spark_url
        self.domain = domain
        self.host = urlparse(spark_url).netloc
        self.path = urlparse(spark_url).path

    # 生成url
    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                               digestmod=hashlib.sha256).digest()
        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的头信息配置到字典中
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接url
        url = self.spark_url + '?' + urlencode(v)
        return url

    # 收到websocket错误的处理
    def on_error(self, ws, error):
        print("### error:", error)

    # 收到websocket关闭的处理
    def on_close(self, ws, one, two):
        print(" ")

    # 收到websocket连接建立的处理
    def on_open(self, ws):
        thread.start_new_thread(self.run, (ws,))

    def run(self, ws, *args):
        data = json.dumps(self.gen_params())
        ws.send(data)

    # 收到websocket消息的处理
    def on_message(self, ws, message):
        data = json.loads(message)
        code = data['header']['code']
        if code != 0:
            print(f'请求错误: {code}, {data}')
            ws.close()
        else:
            choices = data["payload"]["choices"]
            status = choices["status"]
            content = choices["text"][0]["content"]
            global answer
            answer += content
            if status == 2:
                ws.close()

    def gen_params(self):
        """
        通过appid和用户的提问来生成请参数
        """
        data = {
            "header": {
                "app_id": self.appid,
                "uid": "1234"
            },
            "parameter": {
                "chat": {
                    "domain": self.domain,
                    "temperature": 0.8,
                    "max_tokens": 2048,
                    "top_k": 5,
                    "auditing": "default"
                }
            },
            "payload": {
                "message": {
                    "text": self.text
                }
            }
        }
        return data

    def create_connection(self):
        websocket.enableTrace(False)
        wsUrl = self.create_url()
        ws = websocket.WebSocketApp(wsUrl,
                                  on_message=self.on_message,
                                  on_error=self.on_error,
                                  on_close=self.on_close,
                                  on_open=self.on_open)
        ws.appid = self.appid
        ws.text = self.text
        return ws

def main(appid, api_key, api_secret, spark_url, domain, text):
    global answer
    answer = ""

    spark = SparkApi(appid, api_key, api_secret, spark_url, domain)
    spark.text = text

    ws = spark.create_connection()
    
    # 移除 ping_timeout 和 ping_interval 参数，使用默认配置
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})  # 只保留 SSL 配置