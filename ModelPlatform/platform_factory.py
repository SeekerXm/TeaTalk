from ModelPlatform.config.config_manager import ConfigManager
from ModelPlatform.zhipuai_platform import ZhipuAIPlatform
from ModelPlatform.qianfan_platform import QianFanPlatform
from ModelPlatform.spark_platform import SparkPlatform
from ModelPlatform.silicon_platform import SiliconPlatform
from ModelPlatform.base_platform import BasePlatform

class PlatformFactory:
    """AI平台工厂类"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
    
    def create_platform(self, platform_type: str) -> BasePlatform:
        """
        创建平台实例
        :param platform_type: 平台类型 ('zhipuai', 'qianfan', 'spark', 'silicon')
        :return: 平台实例
        """
        config = self.config_manager.get_platform_config(platform_type)
        
        if platform_type == 'zhipuai':
            return ZhipuAIPlatform(api_key=config['api_key'])
        
        elif platform_type == 'qianfan':
            return QianFanPlatform(
                access_key=config['access_key'],
                secret_key=config['secret_key']
            )
        
        elif platform_type == 'spark':
            return SparkPlatform(
                app_id=config['app_id'],
                api_key=config['api_key'],
                api_secret=config['api_secret']
            )
        
        elif platform_type == 'silicon':
            return SiliconPlatform(api_key=config['api_key'])
        
        else:
            raise ValueError(f"Unsupported platform type: {platform_type}") 