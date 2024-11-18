import requests
from ModelPlatform.base_platform import BasePlatform

class SiliconPlatform(BasePlatform):
    """SiliconCloud平台实现类"""
    
    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.base_url = "https://api.siliconflow.cn/v1"
        
    def chat_completion(self, messages, **kwargs):
        """
        SiliconCloud文本对话实现
        支持多个模型，通过kwargs['model']指定
        """
        model = kwargs.get('model', 'THUDM/chatglm3-6b')  # 默认使用chatglm3-6b
        
        # 打印请求信息，用于调试
        print(f"\nDebug - Request Info:")
        print(f"Model: {model}")
        print(f"Messages: {messages}")
        
        # 添加模型参数
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2048,
            "stream": False
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            # 所有模型都使用统一的chat/completions端点
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers
            )
            
            # 打印响应信息，用于调试
            print(f"\nDebug - Response Info:")
            print(f"Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")
            
            # 检查HTTP响应状态
            if response.status_code != 200:
                return self.handle_error(Exception(f"HTTP error {response.status_code}: {response.text}"))
            
            # 解析响应
            response_data = response.json()
            
            # 检查响应格式
            if 'choices' not in response_data or not response_data['choices']:
                return self.handle_error(Exception("Invalid response format"))
            
            # 返回处理后的响应
            return self.handle_response(response_data)
            
        except Exception as e:
            return self.handle_error(e)
    
    def image_generation(self, prompt, **kwargs):
        """
        SiliconCloud图像生成实现
        支持多个模型，通过kwargs['model']指定
        """
        model = kwargs.get('model', 'stabilityai/stable-diffusion-2-1')
        image_size = kwargs.get('image_size', '512x512')
        
        payload = {
            "model": model,
            "prompt": prompt,
            "negative_prompt": kwargs.get('negative_prompt', ''),
            "image_size": image_size,
            "batch_size": kwargs.get('batch_size', 1),
            "num_inference_steps": kwargs.get('num_inference_steps', 20),
            "guidance_scale": kwargs.get('guidance_scale', 7.5)
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/images/generations",
                json=payload,
                headers=headers
            )
            
            # 检查HTTP响应状态
            if response.status_code != 200:
                return self.handle_error(Exception(f"HTTP error {response.status_code}: {response.text}"))
            
            return self.handle_response(response.json())
            
        except Exception as e:
            return self.handle_error(e) 