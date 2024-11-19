import os
import sys
import threading
import time
from itertools import cycle

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from ModelPlatform.platform_factory import PlatformFactory


class LoadingAnimation:
    """加载动画类"""
    
    def __init__(self, desc="AI思考中"):
        self.desc = desc
        self.animation = cycle(['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷'])
        self.running = False
        self.animation_thread = None
    
    def __enter__(self):
        self.start()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
    
    def start(self):
        """开始动画"""
        self.running = True
        self.animation_thread = threading.Thread(target=self._animate)
        self.animation_thread.start()
    
    def stop(self):
        """停止动画"""
        self.running = False
        if self.animation_thread is not None:
            self.animation_thread.join()
        # 清除动画
        sys.stdout.write('\r' + ' ' * (len(self.desc) + 10) + '\r')
        sys.stdout.flush()
    
    def _animate(self):
        """动画循环"""
        while self.running:
            sys.stdout.write(f'\r{self.desc} {next(self.animation)}')
            sys.stdout.flush()
            time.sleep(0.1)

def main():
    # 创建平台工厂实例
    factory = PlatformFactory()
    
    while True:
        # 显示可用平台列表
        print("\n=== 可用的AI平台 ===")
        platforms = {
            "1": "zhipuai",
            "2": "qianfan",
            "3": "spark",
            "4": "silicon"
        }
        for num, name in platforms.items():
            print(f"{num}. {name}")
        
        # 选择平台
        choice = input("\n请选择平台编号 (输入'exit'退出): ")
        if choice.lower() == 'exit':
            break
        
        if choice not in platforms:
            print("无效的选择，请重试")
            continue
        
        platform_name = platforms[choice]
        platform = factory.create_platform(platform_name)
        
        # 显示可用模型
        print(f"\n=== {platform_name}平台可用模型 ===\n")
        text_models = factory.config_manager.get_available_models(platform_name, 'text')
        image_models = factory.config_manager.get_available_models(platform_name, 'image')
        
        if text_models:
            print("文本模型：")
            for i, model in enumerate(text_models, 1):
                print(f"{i}. {model}")
        
        if image_models:
            print("\n图像模型：")
            for i, model in enumerate(image_models, 1):
                print(f"{i}. {model}")
        
        # 选择模型
        model_choice = input("\n请选择模型编号 (输入'back'返回平台选择): ")
        if model_choice.lower() == 'back':
            continue
        
        try:
            model_idx = int(model_choice)
            if 1 <= model_idx <= len(text_models):
                model_name = text_models[model_idx - 1]
                print(f"\n模型信息: {model_name}")
            else:
                print("模型编号无效")
                continue
        except ValueError:
            print("无效的输入")
            continue
        
        # 开始对话
        print(f"\n=== 正在使用 {platform_name} 平台的 {model_name} 模型 ===")
        print("这是一个文本对话模型，您可以开始对话了")
        print("输入 'exit' 退出对话，输入 'switch' 切换模型\n")
        
        messages = []
        while True:
            # 获取用户输入
            user_input = input("用户: ")
            if user_input.lower() == 'exit':
                break
            if user_input.lower() == 'switch':
                break
            
            # 添加用户消息
            messages.append({"role": "user", "content": user_input})
            
            # 获取AI回复
            with LoadingAnimation():
                response = platform.chat_completion(messages)
            
            if response['status'] == 'success':
                ai_message = response['data']['choices'][0]['message']
                print(f"AI: {ai_message['content']}\n")
                messages.append(ai_message)
            else:
                print(f"错误: {response['error']}\n")
                # 移除失败的消息
                messages.pop()
            
            # 清理控制台输出
            sys.stdout.flush()

if __name__ == "__main__":
    main()
