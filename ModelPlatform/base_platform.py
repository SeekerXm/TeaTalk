from abc import ABC, abstractmethod
from typing import Any, Dict, Union

class BasePlatform(ABC):
    """AI平台基类"""
    
    def __init__(self):
        self.api_key = None
        self.secret_key = None
        self.base_url = None
        self.model_name = None
        self.messages = []
    
    @abstractmethod
    def chat_completion(self, messages, **kwargs):
        """文本对话接口"""
        pass
    
    @abstractmethod
    def image_generation(self, prompt, **kwargs):
        """图像生成接口"""
        pass
    
    def handle_response(self, response: Any) -> Dict[str, Any]:
        """统一处理响应"""
        try:
            if hasattr(response, 'json'):  # 处理requests响应
                data = response.json()
            else:  # 处理其他类型响应
                data = response
                
            return {
                'status': 'success',
                'data': data,
                'error': None
            }
        except Exception as e:
            return self.handle_error(e)
    
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """统一处理错误"""
        return {
            'status': 'error',
            'data': None,
            'error': str(error)
        } 