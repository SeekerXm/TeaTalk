import os
import yaml
from typing import Dict, Any

class ConfigManager:
    """配置管理类"""
    
    def __init__(self):
        self.config_path = os.path.join(
            os.path.dirname(__file__),
            'platform_config.yaml'
        )
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise Exception(f"Failed to load config file: {e}")
    
    def get_platform_config(self, platform_name: str) -> Dict[str, Any]:
        """获取指定平台的配置"""
        if platform_name not in self.config:
            raise ValueError(f"Platform {platform_name} not found in config")
        return self.config[platform_name]
    
    def get_available_models(self, platform_name: str, model_type: str) -> list:
        """获取指定平台指定类型的可用模型列表"""
        platform_config = self.get_platform_config(platform_name)
        return platform_config['available_models'].get(model_type, []) 