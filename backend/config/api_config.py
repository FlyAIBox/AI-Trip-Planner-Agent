"""
外部服务API配置

这个模块管理所有外部API服务的配置，包括：
- OpenWeather API：天气数据获取
- Google Places API：地点和景点信息
- Exchange Rate API：货币汇率转换
- 备用免费API：无需密钥的替代服务

适用于大模型技术初级用户：
这个模块展示了如何安全地管理API密钥和配置，
使用环境变量来保护敏感信息。
"""

import os
from typing import Optional

# 天气API配置
# OpenWeather API用于获取准确的天气预报数据
OPENWEATHER_API_KEY: Optional[str] = os.getenv('OPENWEATHER_API_KEY')  # 从环境变量获取API密钥
WEATHER_BASE_URL: str = "http://api.openweathermap.org/data/2.5"       # OpenWeather API基础URL

# Google Places API配置
# 用于搜索景点、餐厅、酒店等地点信息
GOOGLE_PLACES_API_KEY: Optional[str] = os.getenv('GOOGLE_PLACES_API_KEY')  # Google Places API密钥
PLACES_BASE_URL: str = "https://maps.googleapis.com/maps/api/place"        # Google Places API基础URL

# 货币汇率API配置
# 用于获取实时汇率进行货币转换
EXCHANGERATE_API_KEY: Optional[str] = os.getenv('EXCHANGERATE_API_KEY')     # 汇率API密钥
EXCHANGE_RATE_URL: str = "https://api.exchangerate-api.com/v4/latest"      # 汇率API基础URL

# 备用免费API（无需密钥）
# 当主要API不可用时的替代方案
FREE_WEATHER_URL: str = "https://api.open-meteo.com/v1/forecast"           # 免费天气API
FREE_EXCHANGE_URL: str = "https://api.exchangerate-api.com/v4/latest"      # 免费汇率API

def get_api_status() -> dict:
    """
    检查哪些API具有有效的密钥

    这个函数检查所有API密钥的可用性，
    帮助系统决定使用哪些服务。

    返回：包含各API状态的字典

    适用于大模型技术初级用户：
    这个函数展示了如何检查配置的完整性，
    确保系统能够优雅地处理缺失的配置。
    """
    return {
        'weather': bool(OPENWEATHER_API_KEY),      # 天气API是否可用
        'places': bool(GOOGLE_PLACES_API_KEY),     # 地点API是否可用
        'exchange': bool(EXCHANGERATE_API_KEY)     # 汇率API是否可用
    }

# 创建API配置对象供导入使用
class APIConfig:
    """
    API配置类

    这个类将所有API配置封装在一个对象中，
    便于其他模块导入和使用。

    适用于大模型技术初级用户：
    这种设计模式叫做"配置对象"，它将相关的
    配置项组织在一起，提供清晰的接口。
    """
    OPENWEATHER_API_KEY = OPENWEATHER_API_KEY      # OpenWeather API密钥
    WEATHER_BASE_URL = WEATHER_BASE_URL            # 天气API基础URL
    GOOGLE_PLACES_API_KEY = GOOGLE_PLACES_API_KEY  # Google Places API密钥
    PLACES_BASE_URL = PLACES_BASE_URL              # 地点API基础URL
    EXCHANGERATE_API_KEY = EXCHANGERATE_API_KEY    # 汇率API密钥
    EXCHANGE_RATE_URL = EXCHANGE_RATE_URL          # 汇率API基础URL

# 全局实例供导入使用
api_config = APIConfig()