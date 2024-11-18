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


class ModelTester:
    def __init__(self):
        self.factory = PlatformFactory()
        self.config_manager = self.factory.config_manager
        self.current_platform = None
        self.current_model = None
        self.loading = LoadingAnimation()  # 添加加载动画实例
    
    def clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_platforms(self):
        """显示所有可用平台"""
        self.clear_screen()
        print("\n=== 可用的AI平台 ===")
        platforms = {
            '1': 'zhipuai',
            '2': 'qianfan',
            '3': 'spark',
            '4': 'silicon'
        }
        
        for num, platform in platforms.items():
            print(f"{num}. {platform}")
        
        return platforms
    
    def display_models(self, platform_name: str):
        """显示指定平台的所有可用模型"""
        self.clear_screen()
        print(f"\n=== {platform_name}平台可用模型 ===")
        
        # 获取文本模型
        text_models = self.config_manager.get_available_models(platform_name, 'text')
        print("\n文本模型：")
        for i, model in enumerate(text_models, 1):
            print(f"{i}. {model}")
        
        # 获取图像模型
        image_models = self.config_manager.get_available_models(platform_name, 'image')
        if image_models:
            print("\n图像模型：")
            for i, model in enumerate(image_models, len(text_models) + 1):
                print(f"{i}. {model}")
        
        return text_models + image_models
    
    def get_image_size_options(self, model):
        """获取不同模型支持的图像尺寸选项"""
        if model == 'stabilityai/stable-diffusion-2-1':
            return {
                '1': '512x512',
                '2': '512x1024',
                '3': '768x512',
                '4': '768x1024',
                '5': '1024x576',
                '6': '576x1024'
            }
        elif model == 'stabilityai/stable-diffusion-3-medium':
            return {
                '1': '1024x1024',
                '2': '960x1280',
                '3': '768x1024',
                '4': '720x1440',
                '5': '1024x576',
                '6': '720x1280'
            }
        elif model == 'stabilityai/stable-diffusion-xl-base-1.0':
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
    
    def get_model_default_params(self, model):
        """获取不同模型的默认参数"""
        if model == 'stabilityai/stable-diffusion-2-1':
            return {
                'batch_size': 1,
                'num_inference_steps': 20,
                'guidance_scale': 7.5
            }
        elif model == 'stabilityai/stable-diffusion-3-medium':
            return {
                'batch_size': 1,
                'num_inference_steps': 20,
                'guidance_scale': 7.5
            }
        elif model == 'stabilityai/stable-diffusion-xl-base-1.0':
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
    
    def handle_image_generation(self, platform, model):
        """处理图像生成模型的交互"""
        print(f"\n=== 正在使用 {platform} 平台的 {model} 模型 ===")
        print("这是一个图像生成模型，请按提示输入参数")
        print("输入 'exit' 退出对话，输入 'switch' 切换模型")
        
        while True:
            # 1. 获取正向prompt
            prompt = input("\n请输入英文正向prompt (必填): ").strip()
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
            size_options = self.get_image_size_options(model)
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
            default_params = self.get_model_default_params(model)
            print("\n其他参数将使用默认值:")
            print(f"batch_size: {default_params['batch_size']}")
            print(f"num_inference_steps: {default_params['num_inference_steps']}")
            print(f"guidance_scale: {default_params['guidance_scale']}")
            
            try:
                with self.loading:  # 使用加载动画
                    response = self.current_platform.image_generation(
                        prompt=prompt,
                        model=model,
                        negative_prompt=negative_prompt if negative_prompt else None,
                        image_size=size_options[size_choice],
                        **default_params
                    )
                
                if isinstance(response, dict):
                    if response.get('status') == 'error':
                        print(f"错误: {response.get('error')}")
                        continue
                    
                    data = response.get('data', {})
                    if 'data' in data and len(data['data']) > 0:
                        print("\n图片生成成功！")
                        print(f"图片数据: {data['data'][0]}")
                    else:
                        print("错误: 图片生成失败")
            
            except Exception as e:
                print(f"错误: {str(e)}")
            
            # 询问是否继续生成
            continue_gen = input("\n是否继续生成图片？(y/n): ").strip().lower()
            if continue_gen != 'y':
                break
        
        return False
    
    def chat_loop(self, platform, model):
        """聊天循环"""
        self.clear_screen()
        
        # 检查是否是图像生成模型
        if platform == 'silicon' and model in self.config_manager.get_available_models(platform, 'image'):
            return self.handle_image_generation(platform, model)
        
        # Fuyu-8B模型的处理逻辑...
        elif model == 'Fuyu-8B':
            print(f"\n=== 正在使用 {platform} 平台的 {model} 模型 ===")
            print("这是一个图像理解模型，上传图片后将自动分析图片内容")
            print("输入 'exit' 退出对话，输入 'switch' 切换模型")
            
            while True:
                # 获取图片路径
                image_path = input("\n请输入图片路径 (输入'exit'退出, 'switch'切换模型): ").strip()
                
                if image_path.lower() == 'exit':
                    break
                elif image_path.lower() == 'switch':
                    return True
                elif not image_path:
                    continue
                
                if not os.path.exists(image_path):
                    print("错误: 图片文件不存在")
                    continue
                
                try:
                    with self.loading:  # 使用加载动画
                        response = self.current_platform.image_chat(
                            image_path=image_path
                        )
                    
                    if isinstance(response, dict):
                        if response.get('status') == 'error':
                            print(f"错误: {response.get('error')}")
                            continue
                        
                        result = response.get('data', {}).get('result', '')
                        if result:
                            print(f"AI: {result}")
                        else:
                            print("错误: 模型没有返回有效回复")
                
                except Exception as e:
                    print(f"错误: {str(e)}")
            
            return False
        
        # 普通文本对话模型的处理逻辑...
        else:
            print(f"\n=== 正在使用 {platform} 平台的 {model} 模型 ===")
            print("这是一个文本对话模型，您可以开始对话了")
            print("输入 'exit' 退出对话，输入 'switch' 切换模型")
            
            messages = []
            while True:
                user_input = input("\n用户: ").strip()
                
                if user_input.lower() == 'exit':
                    break
                elif user_input.lower() == 'switch':
                    return True
                elif not user_input:
                    continue
                
                messages.append({"role": "user", "content": user_input})
                
                try:
                    with self.loading:  # 使用加载动画
                        response = self.current_platform.chat_completion(
                            messages=messages,
                            model=self.current_model
                        )
                    
                    if isinstance(response, dict):
                        if response.get('status') == 'error':
                            print(f"错误: {response.get('error')}")
                            continue
                        
                        data = response.get('data', {})
                        
                        # 处理不同平台的响应格式
                        if platform == 'zhipuai':
                            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                        elif platform == 'qianfan':
                            content = data.get('result', '')
                        elif platform == 'spark':
                            content = data.get('content', '')
                        elif platform == 'silicon':
                            content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                        else:
                            content = str(data)
                    else:
                        content = str(response)
                    
                    if content:
                        print(f"AI: {content}")
                        messages.append({"role": "assistant", "content": content})
                    else:
                        print("错误: 模型没有返回有效回复")
                
                except Exception as e:
                    print(f"错误: {str(e)}")
            
            return False
    
    def get_model_info(self, platform_name: str, model_name: str) -> str:
        """获取模型的详细信息"""
        if platform_name == 'silicon':
            # SiliconCloud平台的模型信息
            model_info = {
                # 文本生成模型
                'THUDM/chatglm3-6b': "清华大学开源的对话模型，支持多轮对话",
                'google/gemma-2-9b-it': "Google开源的Gemma系列9B指令模型",
                'THUDM/glm-4-9b-chat': "清华大学的GLM系列9B对话模型",
                'internlm/internlm2_5-7b-chat': "书生浦语2.5系列7B对话模型",
                'meta-llama/Meta-Llama-3.1-8B-Instruct': "Meta最新的Llama3.1系列8B指令模型",
                'meta-llama/Meta-Llama-3-8B-Instruct': "Meta最新的Llama3系列8B指令模型",
                'Qwen/Qwen2.5-7B-Instruct': "通义千问2.5系列7B指令微调模型",
                'Qwen2.5-Coder-7B': "通义千问2.5系列7B代码专用模型",
                'Qwen/Qwen2-1.5B-Instruct': "通义千问2.0系列1.5B指令微调模型",
                'Qwen/Qwen2-7B-Instruct': "通义千问2.0系列7B指令微调模型",
                '01-ai/Yi-1.5-6B-Chat': "零一万物开源的Yi系列6B对话模型",
                '01-ai/Yi-1.5-9B-Chat-16K': "零一万物开源的Yi系列9B长文本对话模型",
                # 图像生成模型
                'black-forest-labs/FLUX.1-schnell': "Black Forest的FLUX系列图像生成模型",
                'stabilityai/stable-diffusion-2-1': "Stability AI的SD2.1图像生成模型",
                'stabilityai/stable-diffusion-3-medium': "Stability AI的SD3图像生成模型",
                'stabilityai/stable-diffusion-xl-base-1.0': "Stability AI的SDXL图像生成模型"
            }
            return model_info.get(model_name, "未知模型")
        return "未知模型"
    
    def run(self):
        """运行测试程序"""
        while True:
            # 显示平台选择
            platforms = self.display_platforms()
            platform_choice = input("\n请选择平台编号 (输入'exit'退出): ").strip()
            
            if platform_choice.lower() == 'exit':
                break
            
            if platform_choice not in platforms:
                print("无效的平台选择！")
                continue
            
            platform_name = platforms[platform_choice]
            
            while True:
                # 显示模型选择
                available_models = self.display_models(platform_name)
                if not available_models:
                    print("该平台没有可用的模型！")
                    break
                
                model_choice = input("\n请选择模型编号 (输入'back'返回平台选择): ").strip()
                
                if model_choice.lower() == 'back':
                    break
                
                try:
                    model_index = int(model_choice) - 1
                    if 0 <= model_index < len(available_models):
                        # 创建平台实例
                        self.current_platform = self.factory.create_platform(platform_name)
                        self.current_model = available_models[model_index]
                        
                        # 显示模型信息
                        model_info = self.get_model_info(platform_name, self.current_model)
                        print(f"\n模型信息: {model_info}")
                        
                        # 进入聊天循环
                        switch_model = self.chat_loop(platform_name, self.current_model)
                        if not switch_model:
                            break
                    else:
                        print("无效的模型编号！")
                except ValueError:
                    print("请输入有效的数字！")


if __name__ == "__main__":
    tester = ModelTester()
    tester.run()
