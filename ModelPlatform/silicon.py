from django.conf import settings
import requests

class SiliconPlatform:
    def __init__(self):
        self.api_key = None
        self.base_url = "https://api.siliconflow.cn/v1"
        self.headers = None

    def _update_headers(self):
        """更新请求头"""
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def chat(self, message):
        """
        发送消息到 SiliconCloud 并获取响应
        :param message: 用户消息文本
        :return: AI响应的文本内容
        """
        try:
            if not self.api_key:
                raise Exception("SiliconCloud API密钥未配置")

            self._update_headers()
            
            # 构建请求数据
            data = {
                "model": "Qwen/Qwen2.5-Coder-32B-Instruct",
                "messages": [
                    {"role": "system", "content": "你是 SiliconCloud AI 助手，你的任务是详细回答用户的问题。"},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.7,
                "max_tokens": 2000,
                "stream": False
            }

            # 发送请求
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=30
            )

            # 检查响应状态
            if response.status_code != 200:
                error_msg = response.json().get('error', {}).get('message', '未知错误')
                raise Exception(f"API请求失败: {error_msg}")

            # 解析响应
            result = response.json()
            if not result.get('choices'):
                raise Exception("API响应格式错误")

            return result['choices'][0]['message']['content']

        except requests.exceptions.RequestException as e:
            print(f"SiliconCloud API请求错误: {str(e)}")
            raise Exception(f"网络请求失败: {str(e)}")
        except Exception as e:
            print(f"SiliconCloud调用出错: {str(e)}")
            raise Exception(f"AI服务暂时不可用: {str(e)}") 