"""
LangGraph智能体工具集

这个模块包含了AI旅行规划智能体使用的所有搜索工具，包括：
- 目的地信息搜索
- 天气信息查询
- 景点发现
- 酒店搜索
- 餐厅查找
- 当地贴士获取
- 预算信息分析

适用于大模型技术初级用户：
这个模块展示了如何为AI智能体创建专门的工具，
每个工具都有特定的功能和搜索策略，通过DuckDuckGo
搜索引擎获取实时信息。
"""

import asyncio
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from duckduckgo_search import DDGS
import json
import re
from datetime import datetime

# 直接定义工具函数，不使用类包装
@tool
def search_destination_info(query: str) -> str:
    """
    使用DuckDuckGo搜索目的地信息

    这个工具专门用于搜索旅行目的地的综合信息，
    包括景点、旅游指南、文化背景等。

    参数：
    - query: 搜索查询字符串（目的地名称）

    返回：格式化的搜索结果字符串

    功能说明：
    1. 构建专门的搜索查询
    2. 使用DuckDuckGo进行搜索
    3. 格式化结果供智能体理解
    4. 处理搜索错误和异常情况
    """
    try:
        # 使用DuckDuckGo搜索引擎
        with DDGS() as ddgs:
            # 构建搜索查询，添加旅游相关关键词
            results = list(ddgs.text(
                query + " 旅游目的地指南景点",  # 中文搜索关键词
                max_results=5,  # 最大结果数
                region="cn-zh",            # 搜索区域
                safesearch="moderate"     # 安全搜索级别
            ))

            # 检查是否有搜索结果
            if not results:
                return f"未找到目的地搜索结果: {query}"

            # 格式化结果供智能体使用
            formatted_results = []
            for i, result in enumerate(results[:5], 1):  # 取前5个结果
                formatted_results.append(
                    f"{i}. {result.get('title', '无标题')}\n"
                    f"   {result.get('body', '无描述')}\n"
                    f"   来源: {result.get('href', '无URL')}\n"
                )

            return "\n".join(formatted_results)
    except Exception as e:
        return f"搜索目的地信息时出错: {str(e)}"

@tool
def search_weather_info(destination: str, dates: str = "") -> str:
    """
    搜索目的地天气信息

    这个工具专门用于搜索特定目的地的天气预报信息，
    包括气候条件、最佳旅行时间等。

    参数：
    - destination: 目的地名称
    - dates: 日期信息（可选）

    返回：格式化的天气信息字符串
    """
    try:
        weather_query = f"{destination} 天气预报 {dates} 旅行气候"
        with DDGS() as ddgs:
            results = list(ddgs.text(
                weather_query,
                max_results=5,
                region="cn-zh",
                safesearch="moderate"
            ))

            if not results:
                return f"未找到{destination}的天气信息"

            weather_info = []
            for result in results[:3]:
                weather_info.append(
                    f"• {result.get('title', '天气信息')}\n"
                    f"  {result.get('body', '无详细信息')}\n"
                )

            return f"{destination}的天气信息:\n" + "\n".join(weather_info)
    except Exception as e:
        return f"搜索天气信息时出错: {str(e)}"

@tool
def search_attractions(destination: str, interests: str = "") -> str:
    """
    搜索目的地景点和活动

    这个工具专门用于搜索特定目的地的热门景点、
    活动和必游之地，可以根据兴趣进行筛选。

    参数：
    - destination: 目的地名称
    - interests: 兴趣关键词（可选）

    返回：格式化的景点信息字符串
    """
    try:
        attraction_query = f"{destination} 热门景点 活动 {interests} 必游之地"
        with DDGS() as ddgs:
            results = list(ddgs.text(
                attraction_query,
                max_results=8,
                region="cn-zh",
                safesearch="moderate"
            ))

            if not results:
                return f"未找到{destination}的景点信息"

            attractions = []
            for i, result in enumerate(results[:6], 1):
                attractions.append(
                    f"{i}. {result.get('title', '景点')}\n"
                    f"   {result.get('body', '无描述')[:200]}...\n"
                )

            return f"{destination}的热门景点:\n" + "\n".join(attractions)
    except Exception as e:
        return f"搜索景点信息时出错: {str(e)}"

@tool
def search_hotels(destination: str, budget: str = "中等预算") -> str:
    """
    搜索酒店信息和价格

    这个工具专门用于搜索特定目的地的酒店选择，
    包括住宿选项、价格信息和最佳住宿地点。

    参数：
    - destination: 目的地名称
    - budget: 预算范围（默认"中等预算"）

    返回：格式化的酒店信息字符串
    """
    try:
        hotel_query = f"{destination} 酒店 {budget} 最佳住宿 住宿推荐"
        with DDGS() as ddgs:
            results = list(ddgs.text(
                hotel_query,
                max_results=6,
                region="cn-zh",
                safesearch="moderate"
            ))

            if not results:
                return f"未找到{destination}的酒店信息"

            hotels = []
            for i, result in enumerate(results[:4], 1):
                hotels.append(
                    f"{i}. {result.get('title', '酒店')}\n"
                    f"   {result.get('body', '无详细信息')[:180]}...\n"
                )

            return f"{destination}的酒店选择 ({budget}预算):\n" + "\n".join(hotels)
    except Exception as e:
        return f"搜索酒店信息时出错: {str(e)}"

@tool
def search_restaurants(destination: str, cuisine: str = "") -> str:
    """
    搜索餐厅和用餐选择

    这个工具专门用于搜索特定目的地的餐厅推荐，
    包括当地美食、特色菜系和用餐地点。

    参数：
    - destination: 目的地名称
    - cuisine: 菜系类型（可选）

    返回：格式化的餐厅推荐字符串
    """
    try:
        restaurant_query = f"{destination} 最佳餐厅 {cuisine} 当地美食 用餐推荐"
        with DDGS() as ddgs:
            results = list(ddgs.text(
                restaurant_query,
                max_results=6,
                region="cn-zh",
                safesearch="moderate"
            ))

            if not results:
                return f"未找到{destination}的餐厅信息"

            restaurants = []
            for i, result in enumerate(results[:4], 1):
                restaurants.append(
                    f"{i}. {result.get('title', '餐厅')}\n"
                    f"   {result.get('body', '无详细信息')[:180]}...\n"
                )

            return f"{destination}的餐厅推荐:\n" + "\n".join(restaurants)
    except Exception as e:
        return f"搜索餐厅信息时出错: {str(e)}"

@tool
def search_local_tips(destination: str) -> str:
    """
    搜索当地贴士、文化和内部信息

    这个工具专门用于搜索目的地的当地文化、
    礼仪习俗和内部旅行贴士。

    参数：
    - destination: 目的地名称

    返回：格式化的当地贴士字符串
    """
    try:
        tips_query = f"{destination} 当地贴士 旅行指南 文化礼仪 注意事项"
        with DDGS() as ddgs:
            results = list(ddgs.text(
                tips_query,
                max_results=5,
                region="cn-zh",
                safesearch="moderate"
            ))

            if not results:
                return f"未找到{destination}的当地贴士"

            tips = []
            for result in results[:3]:
                tips.append(
                    f"• {result.get('title', '当地贴士')}\n"
                    f"  {result.get('body', '无详细信息')[:200]}...\n"
                )

            return f"{destination}的当地贴士:\n" + "\n".join(tips)
    except Exception as e:
        return f"搜索当地贴士时出错: {str(e)}"

@tool
def search_budget_info(destination: str, duration: str = "") -> str:
    """
    搜索预算和费用信息

    这个工具专门用于搜索目的地的旅行预算、
    日常开销和费用估算信息。

    参数：
    - destination: 目的地名称
    - duration: 旅行时长（可选）

    返回：格式化的预算信息字符串
    """
    try:
        budget_query = f"{destination} 旅行预算 费用 日常开销 {duration} 花费"
        with DDGS() as ddgs:
            results = list(ddgs.text(
                budget_query,
                max_results=5,
                region="cn-zh",
                safesearch="moderate"
            ))

            if not results:
                return f"未找到{destination}的预算信息"

            budget_info = []
            for result in results[:3]:
                budget_info.append(
                    f"• {result.get('title', '预算信息')}\n"
                    f"  {result.get('body', '无详细信息')[:200]}...\n"
                )

            return f"{destination}的预算信息:\n" + "\n".join(budget_info)
    except Exception as e:
        return f"搜索预算信息时出错: {str(e)}"

# List of all available tools
ALL_TOOLS = [
    search_destination_info,
    search_weather_info,
    search_attractions,
    search_hotels,
    search_restaurants,
    search_local_tips,
    search_budget_info
]
