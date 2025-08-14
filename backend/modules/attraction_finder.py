"""
景点、餐厅和活动查找模块

这个模块负责查找和推荐旅行相关的各种场所和活动，包括：
- 旅游景点发现和评估
- 餐厅推荐和筛选
- 娱乐活动搜索
- 价格估算和预算匹配
- Google Places API集成和模拟数据回退

适用于大模型技术初级用户：
这个模块展示了如何与外部API集成，处理不同类型的数据，
以及如何根据用户预算和偏好进行智能推荐。
"""

import requests
import json
from typing import List, Dict, Any, Optional
import random
from ..data.models import Attraction
from ..config.api_config import api_config
from ..config.app_config import app_config

class AttractionFinder:
    """
    景点和活动查找服务类

    这个类负责查找和推荐各种旅行相关的场所和活动，包括：
    1. 旅游景点的搜索和筛选
    2. 餐厅的发现和推荐
    3. 娱乐活动的查找
    4. 基于预算的价格估算
    5. API集成和数据处理

    主要功能：
    - Google Places API集成
    - 智能预算匹配
    - 多类型场所搜索
    - 模拟数据回退机制

    适用于大模型技术初级用户：
    这个类展示了如何设计一个复杂的推荐系统，
    包含API集成、数据处理和智能筛选功能。
    """

    def __init__(self):
        """
        初始化景点查找服务

        设置API配置、价格映射和成本估算规则，
        为各种类型的场所搜索做准备。
        """
        # API配置
        self.api_key = api_config.GOOGLE_PLACES_API_KEY  # Google Places API密钥
        self.base_url = api_config.PLACES_BASE_URL       # API基础URL
        self.session = requests.Session()                # HTTP会话对象

        # 不同预算范围的价格映射
        self.budget_price_mapping = {
            '经济型': {'min': 0, 'max': 2, 'multiplier': 0.7},    # 经济型：价格较低
            '中等预算': {'min': 1, 'max': 3, 'multiplier': 1.0},   # 中等：标准价格
            '豪华型': {'min': 2, 'max': 4, 'multiplier': 1.5}     # 豪华：价格较高
        }

        # 不同类型场所的成本估算（基础费用，人民币）
        self.cost_estimates = {
            'attraction': {'经济型': 100, '中等预算': 180, '豪华型': 320},  # 景点门票
            'restaurant': {'经济型': 150, '中等预算': 280, '豪华型': 560}, # 餐厅用餐
            'activity': {'经济型': 200, '中等预算': 420, '豪华型': 840}   # 娱乐活动
        }
    
    def find_attractions(self, trip_details: Dict[str, Any]) -> List[Attraction]:
        """
        根据旅行详情查找旅游景点

        这个方法负责搜索和推荐适合的旅游景点，包括：
        1. 使用Google Places API搜索实际景点
        2. 根据用户预算和偏好筛选
        3. 提供模拟数据作为回退方案
        4. 返回排序后的景点列表

        参数：
        - trip_details: 包含目的地、预算等信息的旅行详情字典

        返回：Attraction对象列表，按推荐度排序

        功能说明：
        1. 构建搜索查询
        2. 尝试API调用获取真实数据
        3. 处理和筛选搜索结果
        4. 回退到模拟数据（如果需要）
        """
        try:
            attractions = []
            query = f"{trip_details['destination']} 旅游景点"  # 中文搜索查询

            # 首先尝试API调用
            if self.api_key:
                places_data = self._search_places(query, 'tourist_attraction')
                attractions = self._process_places_data(places_data, 'attraction', trip_details)

            # 如果API失败或无密钥，回退到模拟数据
            if not attractions:
                attractions = self._get_mock_attractions(trip_details)

            # 返回限定数量的景点
            return attractions[:app_config.MAX_ATTRACTIONS]

        except Exception as e:
            print(f"查找景点时出错: {e}")
            return self._get_mock_attractions(trip_details)
    
    def find_restaurants(self, trip_details: Dict[str, Any]) -> List[Attraction]:
        """
        根据旅行详情查找餐厅

        这个方法负责搜索和推荐适合的餐厅，包括：
        1. 使用Google Places API搜索实际餐厅
        2. 根据用户预算和偏好筛选
        3. 提供模拟数据作为回退方案
        4. 返回排序后的餐厅列表

        参数：
        - trip_details: 包含目的地、预算等信息的旅行详情字典

        返回：Attraction对象列表，按推荐度排序
        """
        try:
            restaurants = []
            query = f"{trip_details['destination']} 餐厅"  # 中文搜索查询

            # 首先尝试API调用
            if self.api_key:
                places_data = self._search_places(query, 'restaurant')
                restaurants = self._process_places_data(places_data, 'restaurant', trip_details)

            # 如果API失败或无密钥，回退到模拟数据
            if not restaurants:
                restaurants = self._get_mock_restaurants(trip_details)

            return restaurants[:app_config.MAX_RESTAURANTS]

        except Exception as e:
            print(f"查找餐厅时出错: {e}")
            return self._get_mock_restaurants(trip_details)
    
    def find_activities(self, trip_details: Dict[str, Any]) -> List[Attraction]:
        """
        根据旅行详情和偏好查找活动

        这个方法负责搜索和推荐适合的娱乐活动，包括：
        1. 根据用户兴趣构建搜索查询
        2. 使用Google Places API搜索实际活动
        3. 根据用户预算和偏好筛选
        4. 提供模拟数据作为回退方案

        参数：
        - trip_details: 包含目的地、预算、偏好等信息的旅行详情字典

        返回：Attraction对象列表，按推荐度排序
        """
        try:
            activities = []

            # 根据偏好构建搜索查询
            interests = trip_details.get('preferences', {}).get('interests', [])
            if interests:
                query = f"{' '.join(interests)} 活动 {trip_details['destination']}"
            else:
                query = f"{trip_details['destination']} 娱乐活动"

            # 首先尝试API调用
            if self.api_key:
                places_data = self._search_places(query, 'point_of_interest')
                activities = self._process_places_data(places_data, 'activity', trip_details)

            # 如果API失败或无密钥，回退到模拟数据
            if not activities:
                activities = self._get_mock_activities(trip_details)

            return activities[:app_config.MAX_ACTIVITIES]

        except Exception as e:
            print(f"查找活动时出错: {e}")
            return self._get_mock_activities(trip_details)
    
    def _search_places(self, query: str, place_type: str) -> List[Dict]:
        """
        使用Google Places API搜索场所

        这个私有方法负责与Google Places API交互，包括：
        1. 构建API请求参数
        2. 发送HTTP请求到Google服务器
        3. 处理API响应和错误
        4. 返回搜索结果数据

        参数：
        - query: 搜索查询字符串
        - place_type: 场所类型（如restaurant、tourist_attraction等）

        返回：包含场所信息的字典列表
        """
        try:
            url = f"{self.base_url}/textsearch/json"
            params = {
                'query': query,
                'key': self.api_key,
                'type': place_type
            }

            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            return data.get('results', [])

        except Exception as e:
            print(f"API搜索失败: {e}")
            return []
    
    def _process_places_data(self, places_data: List[Dict], place_type: str, trip_details: Dict) -> List[Attraction]:
        """
        将Google Places API响应处理为Attraction对象

        这个私有方法负责处理API返回的原始数据，包括：
        1. 提取场所的基本信息（名称、评分、价格等级等）
        2. 根据场所类型和用户预算估算费用
        3. 确定推荐的游览时长
        4. 创建标准化的Attraction对象

        参数：
        - places_data: Google Places API返回的场所数据列表
        - place_type: 场所类型（景点、餐厅、活动等）
        - trip_details: 旅行详情，包含预算信息

        返回：处理后的Attraction对象列表
        """
        attractions = []
        budget_range = trip_details.get('budget_range', 'mid-range')

        for place in places_data:
            try:
                # 提取基本信息
                name = place.get('name', '未知场所')
                rating = place.get('rating', 4.0)
                price_level = place.get('price_level', 2)
                address = place.get('formatted_address', '地址信息不可用')

                # 根据类型和预算估算费用
                estimated_cost = self._estimate_cost(place_type, budget_range, price_level)

                # 根据类型确定游览时长
                duration = self._get_duration_by_type(place_type)

                attraction = Attraction(
                    name=name,
                    type=place_type,
                    rating=rating,
                    price_level=price_level,
                    address=address,
                    description=self._generate_description(place, place_type),
                    estimated_cost=estimated_cost,
                    duration=duration
                )

                attractions.append(attraction)

            except Exception as e:
                print(f"处理场所数据时出错: {e}")
                continue

        return attractions
    
    def _estimate_cost(self, place_type: str, budget_range: str, price_level: int) -> float:
        """
        根据场所类型、预算范围和价格等级估算费用

        这个方法使用多个因素来估算场所的费用：
        1. 基础费用：根据场所类型和用户预算范围
        2. 价格调整：根据Google的价格等级（0-4级）
        3. 最终计算：基础费用 × 价格倍数

        参数：
        - place_type: 场所类型（景点、餐厅、活动）
        - budget_range: 预算范围（经济型、中等预算、豪华型）
        - price_level: Google的价格等级（0-4，0最便宜，4最贵）

        返回：估算的费用（人民币）
        """
        base_cost = self.cost_estimates.get(place_type, {}).get(budget_range, 30)

        # 根据价格等级调整（Google的0-4级价格体系）
        price_multipliers = {0: 0.5, 1: 0.7, 2: 1.0, 3: 1.3, 4: 1.8}
        multiplier = price_multipliers.get(price_level, 1.0)

        return round(base_cost * multiplier, 2)

    def _get_duration_by_type(self, place_type: str) -> int:
        """
        根据场所类型获取典型的游览时长

        不同类型的场所有不同的推荐游览时间：
        - 景点：通常需要2小时深度游览
        - 餐厅：用餐时间约1小时
        - 活动：娱乐活动通常需要3小时

        参数：
        - place_type: 场所类型

        返回：推荐游览时长（小时）
        """
        durations = {
            'attraction': 2,  # 景点：2小时
            'restaurant': 1,  # 餐厅：1小时
            'activity': 3     # 活动：3小时
        }
        return durations.get(place_type, 2)
    
    def _generate_description(self, place: Dict, place_type: str) -> str:
        """Generate a description for the place"""
        types = place.get('types', [])
        rating = place.get('rating', 0)
        
        description_parts = []
        
        if rating >= 4.5:
            description_parts.append("Highly rated")
        elif rating >= 4.0:
            description_parts.append("Well-reviewed")
        
        if 'museum' in types:
            description_parts.append("cultural attraction")
        elif 'park' in types:
            description_parts.append("outdoor space")
        elif 'restaurant' in types:
            description_parts.append("dining establishment")
        elif 'shopping_mall' in types:
            description_parts.append("shopping destination")
        
        return " ".join(description_parts) if description_parts else f"Popular {place_type}"
    
    def _get_mock_attractions(self, trip_details: Dict) -> List[Attraction]:
        """
        当API不可用时生成模拟景点数据

        这个方法提供高质量的模拟景点数据，确保系统
        在外部API失败时仍能正常运行并提供有用的推荐。

        适用于大模型技术初级用户：
        这展示了如何在AI系统中实现回退机制，
        确保用户体验的连续性。
        """
        destination = trip_details['destination']
        budget_range = trip_details.get('budget_range', '中等预算')

        mock_attractions = [
            {
                'name': f'{destination}历史博物馆',
                'rating': 4.3,
                'price_level': 2,
                'description': '了解当地历史和文化',
                'duration': 2
            },
            {
                'name': f'{destination}中央公园',
                'rating': 4.5,
                'price_level': 0,
                'description': '美丽的公共公园，适合休闲放松',
                'duration': 2
            },
            {
                'name': f'{destination}艺术画廊',
                'rating': 4.2,
                'price_level': 2,
                'description': '当代和古典艺术展览',
                'duration': 2
            },
            {
                'name': f'{destination}老城区',
                'rating': 4.6,
                'price_level': 1,
                'description': '历史建筑和迷人街道',
                'duration': 3
            },
            {
                'name': f'{destination}观景台',
                'rating': 4.4,
                'price_level': 2,
                'description': '城市全景和天文展览',
                'duration': 2
            },
            {
                'name': f'{destination}文化中心',
                'rating': 4.1,
                'price_level': 2,
                'description': '本地表演和文化活动',
                'duration': 2
            },
            {
                'name': f'{destination}植物园',
                'rating': 4.7,
                'price_level': 1,
                'description': '多样植物收藏和宁静步道',
                'duration': 2
            },
            {
                'name': f'{destination}海滨长廊',
                'rating': 4.5,
                'price_level': 0,
                'description': '风景优美的海滨步道和休闲活动',
                'duration': 2
            }
        ]

        attractions = []
        for mock in mock_attractions:
            cost = self._estimate_cost('attraction', budget_range, mock['price_level'])

            attraction = Attraction(
                name=mock['name'],
                type='attraction',
                rating=mock['rating'],
                price_level=mock['price_level'],
                address=f"{destination}市中心",
                description=mock['description'],
                estimated_cost=cost,
                duration=mock['duration']
            )
            attractions.append(attraction)

        return attractions

    def _get_mock_restaurants(self, trip_details: Dict) -> List[Attraction]:
        """
        生成模拟餐厅数据

        当API不可用时，这个方法提供高质量的模拟餐厅数据，
        确保系统能够正常运行并提供有用的推荐。
        """
        destination = trip_details['destination']
        budget_range = trip_details.get('budget_range', '中等预算')

        mock_restaurants = [
            {
                'name': f'{destination}本地小酒馆',
                'rating': 4.4,
                'price_level': 2,
                'description': '传统本地菜肴融合现代风味'
            },
            {
                'name': f'{destination}街头美食市场',
                'rating': 4.2,
                'price_level': 1,
                'description': '正宗街头美食和当地特色小吃'
            },
            {
                'name': '精致餐厅',
                'rating': 4.6,
                'price_level': 3,
                'description': '高档用餐体验，提供时令菜单'
            },
            {
                'name': '屋顶咖啡厅',
                'rating': 4.3,
                'price_level': 2,
                'description': '绝佳景观，提供咖啡和轻食'
            },
            {
                'name': '家庭餐厅',
                'rating': 4.1,
                'price_level': 2,
                'description': '舒适氛围，提供国际美食'
            },
            {
                'name': '素食天堂',
                'rating': 4.5,
                'price_level': 2,
                'description': '植物性美食，使用新鲜本地食材'
            },
            {
                'name': '海鲜专门店',
                'rating': 4.4,
                'price_level': 3,
                'description': '新鲜海鲜配港口美景'
            }
        ]

        restaurants = []
        for mock in mock_restaurants:
            cost = self._estimate_cost('restaurant', budget_range, mock['price_level'])

            restaurant = Attraction(
                name=mock['name'],
                type='restaurant',
                rating=mock['rating'],
                price_level=mock['price_level'],
                address=f"{destination}市中心",
                description=mock['description'],
                estimated_cost=cost,
                duration=1
            )
            restaurants.append(restaurant)

        return restaurants

    def _get_mock_activities(self, trip_details: Dict) -> List[Attraction]:
        """
        生成模拟活动数据

        这个方法根据用户兴趣和目的地特点，
        生成多样化的活动推荐数据。
        """
        destination = trip_details['destination']
        budget_range = trip_details.get('budget_range', '中等预算')
        interests = trip_details.get('preferences', {}).get('interests', [])
        
        # 基础活动列表：涵盖各种类型的旅行活动
        mock_activities = [
            {
                'name': f'{destination}城市徒步游',
                'rating': 4.3,
                'price_level': 1,
                'description': '专业导游带领游览主要地标和小众景点',
                'duration': 3
            },
            {
                'name': '本地烹饪课程',
                'rating': 4.6,
                'price_level': 2,
                'description': '跟随当地厨师学习制作传统菜肴',
                'duration': 4
            },
            {
                'name': '自行车租赁城市游',
                'rating': 4.2,
                'price_level': 2,
                'description': '骑行探索城市风光',
                'duration': 3
            },
            {
                'name': '游船',
                'rating': 4.4,
                'price_level': 2,
                'description': '乘船欣赏城市天际线美景',
                'duration': 2
            },
            {
                'name': '冒险运动套餐',
                'rating': 4.5,
                'price_level': 3,
                'description': '刺激的户外活动和冒险体验',
                'duration': 4
            }
        ]

        # 根据用户兴趣添加特定活动
        # 这个智能匹配系统根据用户的兴趣偏好，动态添加相关活动
        if 'museums' in [i.lower() for i in interests] or '博物馆' in interests:
            mock_activities.append({
                'name': f'{destination}博物馆通票',
                'rating': 4.4,
                'price_level': 2,
                'description': '畅游多个博物馆和美术馆',
                'duration': 4
            })

        if 'food' in [i.lower() for i in interests] or '美食' in interests:
            mock_activities.append({
                'name': '美食美酒品鉴之旅',
                'rating': 4.7,
                'price_level': 3,
                'description': '品尝当地美酒和精致美食',
                'duration': 3
            })

        if 'nightlife' in [i.lower() for i in interests] or '夜生活' in interests:
            mock_activities.append({
                'name': '夜间娱乐套餐',
                'rating': 4.2,
                'price_level': 3,
                'description': '体验当地夜生活和娱乐文化',
                'duration': 4
            })

        # 创建活动对象列表
        # 将模拟数据转换为标准的Attraction对象，便于系统统一处理
        activities = []
        for mock in mock_activities:
            # 根据预算范围和价格等级估算活动费用
            cost = self._estimate_cost('activity', budget_range, mock['price_level'])

            # 创建标准化的活动对象
            activity = Attraction(
                name=mock['name'],                              # 活动名称
                type='activity',                                # 类型：活动
                rating=mock['rating'],                          # 用户评分
                price_level=mock['price_level'],                # 价格等级
                address=f"{destination}活动中心",                # 活动地址
                description=mock['description'],                # 活动描述
                estimated_cost=cost,                           # 估算费用
                duration=mock.get('duration', 3)               # 活动时长（小时）
            )
            activities.append(activity)

        return activities
    
    def get_recommendations_by_interests(self, attractions: List[Attraction], interests: List[str]) -> List[Attraction]:
        """
        根据用户兴趣筛选和排序景点推荐

        这个方法实现智能推荐算法，包括：
        1. 关键词匹配：检查景点信息是否包含用户兴趣关键词
        2. 评分加权：高评分景点获得额外推荐分数
        3. 名称匹配：景点名称中的关键词匹配获得更高分数
        4. 综合排序：按总分降序排列推荐结果

        参数：
        - attractions: 待筛选的景点列表
        - interests: 用户兴趣关键词列表

        返回：按推荐度排序的景点列表

        评分规则：
        - 描述匹配：每个关键词+2分
        - 名称匹配：每个关键词+1分（额外奖励）
        - 高评分奖励：4.5分以上+1分，4.0分以上+0.5分
        """
        if not interests:
            return attractions

        scored_attractions = []
        interest_keywords = [interest.lower() for interest in interests]

        for attraction in attractions:
            score = 0
            attraction_text = f"{attraction.name} {attraction.description}".lower()

            # 基于关键词匹配评分
            for keyword in interest_keywords:
                if keyword in attraction_text:
                    score += 2

                # 名称精确匹配额外奖励
                if keyword in attraction.name.lower():
                    score += 1

            # 高评分景点奖励
            if attraction.rating >= 4.5:
                score += 1
            elif attraction.rating >= 4.0:
                score += 0.5

            scored_attractions.append((attraction, score))

        # 按分数降序排序并返回景点列表
        scored_attractions.sort(key=lambda x: x[1], reverse=True)
        return [attraction for attraction, _ in scored_attractions]