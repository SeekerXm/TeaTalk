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

def get_image_size_options(model_name):
    """获取不同模型支持的图像尺寸选项"""
    if model_name == 'stabilityai/stable-diffusion-2-1':
        return {
            '1': '512x512',
            '2': '512x1024',
            '3': '768x512',
            '4': '768x1024',
            '5': '1024x576',
            '6': '576x1024'
        }
    elif model_name == 'stabilityai/stable-diffusion-3-medium':
        return {
            '1': '1024x1024',
            '2': '960x1280',
            '3': '768x1024',
            '4': '720x1440',
            '5': '1024x576',
            '6': '720x1280'
        }
    elif model_name == 'stabilityai/stable-diffusion-xl-base-1.0':
        return {
            '1': '1024x1024',
            '2': '512x1024',
            '3': '768x1024',
            '4': '720x1440',
            '5': '720x1280'
        }
    else:  # FLUX.1-schnell
        return {
            '1': '1024x1024',
            '2': '512x1024',
            '3': '768x512',
            '4': '768x1024',
            '5': '1024x576',
            '6': '576x1024'
        }

def get_model_default_params(model_name):
    """获取不同模型的默认参数"""
    if model_name == 'stabilityai/stable-diffusion-2-1':
        return {
            'batch_size': 1,
            'num_inference_steps': 20,
            'guidance_scale': 7.5
        }
    elif model_name == 'stabilityai/stable-diffusion-3-medium':
        return {
            'batch_size': 1,
            'num_inference_steps': 20,
            'guidance_scale': 7.5
        }
    elif model_name == 'stabilityai/stable-diffusion-xl-base-1.0':
        return {
            'batch_size': 1,
            'num_inference_steps': 20,
            'guidance_scale': 7.5
        }
    else:  # FLUX.1-schnell
        return {
            'batch_size': 1,
            'num_inference_steps': 50,
            'guidance_scale': 50
        }

def handle_image_generation(platform_name, model_name, platform):
    """处理图像生成模型的交互"""
    print(f"\n=== 正在使用 {platform_name} 平台的 {model_name} 模型 ===")
    print("这是一个图像生成模型，请按提示输入参数")
    print("输入 'exit' 退出，输入 'switch' 切换模型\n")
    
    while True:
        # 1. 获取正向prompt
        prompt = input("请输入英文正向prompt (必填): ").strip()
        if prompt.lower() == 'exit':
            return False
        elif prompt.lower() == 'switch':
            return True
        elif not prompt:
            print("错误: 正向prompt不能为空")
            continue
        
        # 2. 获取负向prompt
        negative_prompt = input("请输入英文负向prompt (选填，直接回车跳过): ").strip()
        if negative_prompt.lower() == 'exit':
            return False
        elif negative_prompt.lower() == 'switch':
            return True
        
        # 3. 显示并获取image_size选项
        print("\n可用的图像尺寸选项:")
        size_options = get_image_size_options(model_name)
        for num, size in size_options.items():
            print(f"{num}. {size}")
        
        size_choice = input("请选择图像尺寸编号 (必填): ").strip()
        if size_choice.lower() == 'exit':
            return False
        elif size_choice.lower() == 'switch':
            return True
        elif size_choice not in size_options:
            print("错误: 无效的尺寸选项")
            continue
        
        # 获取默认参数
        default_params = get_model_default_params(model_name)
        print("\n其他参数将使用默认值:")
        print(f"batch_size: {default_params['batch_size']}")
        print(f"num_inference_steps: {default_params['num_inference_steps']}")
        print(f"guidance_scale: {default_params['guidance_scale']}")
        
        try:
            with LoadingAnimation("正在生成图片"):
                response = platform.image_generation(
                    prompt=prompt,
                    model=model_name,
                    negative_prompt=negative_prompt if negative_prompt else None,
                    image_size=size_options[size_choice],
                    **default_params
                )
            
            if response['status'] == 'success':
                print("\n图片生成成功！")
                if 'data' in response['data']:
                    print(f"图片数据: {response['data']['data'][0]}")
                else:
                    print(f"图片数据: {response['data']}")
            else:
                print(f"\n错误: {response['error']}")
        
        except Exception as e:
            print(f"\n错误: {str(e)}")
        
        # 询问是否继续生成
        continue_gen = input("\n是否继续生成图片？(y/n): ").strip().lower()
        if continue_gen != 'y':
            break
    
    return True

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
        
        all_models = []  # 存储所有模型
        
        if text_models:
            print("文本模型：")
            for i, model in enumerate(text_models, 1):
                print(f"{i}. {model}")
                all_models.append(('text', model))
        
        if image_models:
            print("\n图像模型：")
            for i, model in enumerate(image_models, len(text_models) + 1):
                print(f"{i}. {model}")
                all_models.append(('image', model))
        
        # 选择模型
        model_choice = input("\n请选择模型编号 (输入'back'返回平台选择): ")
        if model_choice.lower() == 'back':
            continue
        
        try:
            model_idx = int(model_choice)
            if 1 <= model_idx <= len(all_models):
                model_type, model_name = all_models[model_idx - 1]
                print(f"\n模型信息: {model_name} ({model_type}模型)")
                
                if model_type == 'image':
                    # 区分图像生成模型和图像理解模型
                    if platform_name == 'qianfan' and model_name == 'Fuyu-8B':
                        # 图像理解模型
                        print(f"\n=== 正在使用 {platform_name} 平台的 {model_name} 模型 ===")
                        print("这是一个图像理解模型，您可以输入图片路径和问题")
                        print("输入 'exit' 退出对话，输入 'switch' 切换模型\n")
                        
                        while True:
                            # 获取图片路径
                            image_path = input("请输入图片路径 (输入'exit'退出, 'switch'切换模型): ")
                            if image_path.lower() in ['exit', 'switch']:
                                break
                            
                            if not os.path.exists(image_path):
                                print("错误: 图片文件不存在\n")
                                continue
                            
                            # 获取问题
                            question = input("请输入您的问题: ")
                            
                            # 调用图像理解接口
                            with LoadingAnimation("正在分析图片"):
                                response = platform.image_chat(image_path, question)
                            
                            if response['status'] == 'success':
                                ai_message = response['data']['choices'][0]['message']
                                print(f"AI: {ai_message['content']}\n")
                            else:
                                print(f"错误: {response['error']}\n")
                    else:
                        # 使用新的图像生成处理函数
                        if not handle_image_generation(platform_name, model_name, platform):
                            break
                    continue
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
