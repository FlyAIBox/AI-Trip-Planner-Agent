"""
天气服务模块

这个模块负责获取和处理天气数据，包括：
- 当前天气信息获取
- 多日天气预报
- 天气数据的格式化和验证
- 模拟天气数据（当API不可用时）

适用于大模型技术初级用户：
这个模块展示了如何与外部API进行交互，
包括错误处理、数据转换和回退机制。
"""

import requests
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from ..config.api_config import api_config
from ..data.models import Weather

class WeatherService:
    """
    天气数据获取服务类

    这个类负责从OpenWeather API获取天气信息，包括：
    1. 当前天气状况查询
    2. 多日天气预报获取
    3. 天气数据的处理和格式化
    4. API错误处理和模拟数据回退

    适用于大模型技术初级用户：
    这个类展示了如何设计一个外部API服务的包装器，
    包含错误处理、数据验证和用户友好的接口。
    """

    def __init__(self):
        """
        初始化天气服务

        设置API密钥、基础URL和HTTP会话，
        为后续的天气数据请求做准备。
        """
        self.api_key = api_config.OPENWEATHER_API_KEY  # OpenWeather API密钥
        self.base_url = api_config.WEATHER_BASE_URL    # API基础URL
        self.session = requests.Session()              # HTTP会话对象，提高请求效率

    def get_current_weather(self, city: str) -> Optional[Weather]:
        """
        获取指定城市的当前天气

        从OpenWeather API获取实时天气数据，包括温度、
        天气描述、湿度、风速等信息。

        参数：
        - city: 城市名称（中文或英文）

        返回：Weather对象或None（如果获取失败）

        功能说明：
        1. 构建API请求参数
        2. 发送HTTP请求获取数据
        3. 解析JSON响应
        4. 创建Weather对象
        5. 错误处理和回退到模拟数据
        """
        try:
            # 构建API请求URL和参数
            url = f"{self.base_url}/weather"
            params = {
                'q': city,              # 城市名称
                'appid': self.api_key,  # API密钥
                'units': 'metric'       # 使用摄氏度
            }

            # 发送HTTP请求
            response = self.session.get(url, params=params)
            response.raise_for_status()  # 检查HTTP错误
            data = response.json()       # 解析JSON响应

            # 创建Weather对象
            return Weather(
                temperature=data['main']['temp'],                    # 温度
                description=data['weather'][0]['description'].title(), # 天气描述
                humidity=data['main']['humidity'],                   # 湿度
                wind_speed=data['wind'].get('speed', 0),            # 风速
                feels_like=data['main']['feels_like'],              # 体感温度
                date=datetime.now().strftime('%Y-%m-%d')            # 日期
            )

        except Exception as e:
            print(f"获取当前天气时出错: {e}")
            return self._get_mock_weather()  # 回退到模拟数据
    
    def get_weather_forecast(self, city: str, days: int = 5) -> List[Weather]:
        """
        获取多日天气预报

        从OpenWeather API获取指定天数的天气预报数据，
        包括每日的温度、天气状况、湿度等信息。

        参数：
        - city: 城市名称（中文或英文）
        - days: 预报天数（默认5天，最多5天）

        返回：Weather对象列表，每个对象代表一天的天气

        功能说明：
        1. 构建预报API请求
        2. 处理3小时间隔的预报数据
        3. 提取每日代表性天气
        4. 避免重复日期
        5. 错误处理和模拟数据回退
        """
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'q': city,                      # 城市名称
                'appid': self.api_key,          # API密钥
                'units': 'metric',              # 使用摄氏度
                'cnt': min(days * 8, 40)        # 每天8个预报（3小时间隔），最多40个
            }

            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            daily_forecasts = []
            processed_dates = set()  # 避免重复日期

            # 处理预报数据列表
            for item in data['list']:
                date_str = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')

                # 如果这个日期还没有处理过
                if date_str not in processed_dates:
                    weather = Weather(
                        temperature=item['main']['temp'],                    # 温度
                        description=item['weather'][0]['description'].title(), # 天气描述
                        humidity=item['main']['humidity'],                   # 湿度
                        wind_speed=item['wind'].get('speed', 0),            # 风速
                        feels_like=item['main']['feels_like'],              # 体感温度
                        date=date_str                                       # 日期
                    )
                    daily_forecasts.append(weather)
                    processed_dates.add(date_str)

                # 如果已经获取了足够的天数，停止处理
                if len(daily_forecasts) >= days:
                    break

            return daily_forecasts

        except Exception as e:
            print(f"获取天气预报时出错: {e}")
            return self._get_mock_forecast(days)
    
    def _get_mock_weather(self) -> Weather:
        """
        当API失败时返回模拟天气数据

        这个方法提供一个合理的默认天气数据，
        确保应用程序在API不可用时仍能正常运行。

        返回：包含模拟数据的Weather对象
        """
        return Weather(
            temperature=22.0,                                    # 温度：22°C
            description="多云",                                   # 天气描述
            humidity=65,                                         # 湿度：65%
            wind_speed=5.2,                                      # 风速：5.2 m/s
            feels_like=24.0,                                     # 体感温度：24°C
            date=datetime.now().strftime('%Y-%m-%d')             # 当前日期
        )

    def _get_mock_forecast(self, days: int) -> List[Weather]:
        """
        当API失败时返回模拟预报数据

        这个方法生成指定天数的模拟天气预报，
        包含变化的温度和不同的天气状况。

        参数：
        - days: 需要生成的预报天数

        返回：包含模拟预报数据的Weather对象列表
        """
        forecasts = []
        base_date = datetime.now()

        # 天气状况循环列表
        weather_conditions = ["晴朗", "多云", "阴天", "小雨"]

        for i in range(days):
            date_str = (base_date + timedelta(days=i)).strftime('%Y-%m-%d')
            temp = 20 + (i % 10)  # 变化的温度（20-29°C循环）

            weather = Weather(
                temperature=float(temp),                         # 温度
                description=weather_conditions[i % 4],           # 循环的天气状况
                humidity=60 + (i % 20),                         # 变化的湿度（60-79%）
                wind_speed=3.0 + (i % 5),                       # 变化的风速（3-7 m/s）
                feels_like=float(temp + 2),                     # 体感温度（比实际温度高2°C）
                date=date_str                                   # 日期
            )
            forecasts.append(weather)

        return forecasts
    
    def get_weather_summary(self, forecasts: List[Weather]) -> Dict[str, Any]:
        """
        生成旅行天气摘要

        这个方法分析天气预报数据，生成有用的统计信息
        和旅行建议，帮助用户做好旅行准备。

        参数：
        - forecasts: 天气预报列表

        返回：包含天气统计和建议的字典
        """
        if not forecasts:
            return {}

        temps = [w.temperature for w in forecasts]

        return {
            'avg_temperature': round(sum(temps) / len(temps), 1),    # 平均温度
            'min_temperature': min(temps),                           # 最低温度
            'max_temperature': max(temps),                           # 最高温度
            'conditions': [w.description for w in forecasts],        # 天气状况列表
            'rainy_days': len([w for w in forecasts if '雨' in w.description]), # 下雨天数
            'recommendations': self._get_weather_recommendations(forecasts)      # 旅行建议
        }

    def _get_weather_recommendations(self, forecasts: List[Weather]) -> List[str]:
        """
        根据天气生成旅行建议

        这个方法分析天气预报，生成实用的旅行建议，
        帮助用户准备合适的衣物和装备。

        参数：
        - forecasts: 天气预报列表

        返回：旅行建议字符串列表
        """
        recommendations = []
        temps = [w.temperature for w in forecasts]
        avg_temp = sum(temps) / len(temps)

        # 温度建议
        if avg_temp < 10:
            recommendations.append("建议携带保暖衣物 - 天气会比较寒冷！")
        elif avg_temp > 30:
            recommendations.append("建议携带轻薄透气的衣物 - 天气会比较炎热！")

        # 降雨建议
        rainy_days = len([w for w in forecasts if '雨' in w.description])
        if rainy_days > 0:
            recommendations.append(f"建议携带雨伞 - 预计有{rainy_days}天会下雨")

        # 风力建议
        if any(w.wind_speed > 10 for w in forecasts):
            recommendations.append("预计会有大风天气 - 请注意固定随身物品")

        return recommendations
