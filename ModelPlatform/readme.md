# AI 模型统一调用平台

## 项目简介

本项目提供了一个统一的接口来调用多个 AI 平台的各种模型，包括文本对话和图像生成功能。目前支持以下平台：

1. 智谱 AI 大模型开放平台
2. 百度千帆大模型平台
3. 讯飞星火大模型
4. SiliconCloud 平台

## 项目结构

```
ModelPlatform/
├── config/ # 配置管理
│ ├── init.py
│ ├── config_manager.py # 配置管理类
│ └── platform_config.yaml # 平台配置文件
├── base_platform.py # 平台基类
├── platform_factory.py # 平台工厂类
├── zhipuai_platform.py # 智谱AI平台实现
├── qianfan_platform.py # 千帆平台实现
├── spark_platform.py # 讯飞星火平台实现
├── silicon_platform.py # SiliconCloud平台实现
└── main.py # 测试程序
```

## 支持的模型

### 1. 智谱 AI 平台

- 文本模型：
  - glm-4-flash

### 2. 百度千帆平台

- 文本模型：
  - Yi-34B-Chat
- 图像理解模型：
  - Fuyu-8B

### 3. 讯飞星火平台

- 文本模型：
  - Spark-Lite

### 4. SiliconCloud 平台

- 文本模型：
  - THUDM/chatglm3-6b
  - Qwen/Qwen2-7B-Instruct
  - Qwen/Qwen2.5-7B-Instruct
  - meta-llama/Meta-Llama-3-8B-Instruct
  - google/gemma-2-9b-it
  - 01-ai/Yi-1.5-6B-Chat
  - THUDM/glm-4-9b-chat
  - Qwen/Qwen2-1.5B-Instruct
  - Qwen/Qwen2.5-Coder-7B-Instruct
  - meta-llama/Meta-Llama-3.1-8B-Instruct
  - 01-ai/Yi-1.5-9B-Chat-16K
  - meta-llama/Meta-Llama-3-8B-Instruct
- 图像生成模型：
  - stabilityai/stable-diffusion-2-1
  - stabilityai/stable-diffusion-3-medium
  - black-forest-labs/FLUX.1-schnell
  - stabilityai/stable-diffusion-xl-base-1.0

## 使用方法

### 1. 配置

在 `config/platform_config.yaml` 中配置各平台的 API 密钥和可用模型：

```
zhipuai:
api_key: "your_api_key"
# ...
qianfan:
access_key: "your_access_key"
secret_key: "your_secret_key"
# ...
spark:
app_id: "your_app_id"
api_key: "your_api_key"
api_secret: "your_api_secret"
# ...
silicon:
api_key: "your_api_key"
# ...
```

### 2. 代码调用示例

`from ModelPlatform.platform_factory import PlatformFactory`

创建工厂实例
factory = PlatformFactory()
创建平台实例
platform = factory.create_platform('platform_name')
文本对话
messages = [{"role": "user", "content": "你好"}]
response = platform.chat_completion(
messages=messages,
model="model_name"
)
图像生成（仅支持的平台）
image_response = platform.image_generation(
prompt="a beautiful landscape",
model="model_name",
image_size="512x512"
)


### 3. 响应格式
所有平台的响应都被统一为以下格式：
```
{
'status': 'success/error',
'data': response_data,
'error': error_message
}
```

## Web 开发注意事项

1. 认证和授权

   - 实现用户认证系统
   - 管理用户的 API 密钥
   - 控制用户对不同平台和模型的访问权限

2. 请求限制

   - 实现请求频率限制
   - 监控 API 使用配额
   - 处理并发请求

3. 错误处理

   - 统一的错误处理机制
   - 友好的错误提示
   - 错误日志记录

4. 缓存策略

   - 实现响应缓存
   - 管理会话状态
   - 优化性能

5. 前端交互

   - 实现模型切换功能
   - 显示加载状态
   - 支持多轮对话
   - 支持图片上传和预览

6. 安全考虑
   - 保护 API 密钥
   - 输入验证和清理
   - 防止恶意请求
