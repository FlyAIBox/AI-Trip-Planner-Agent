"""
酒店搜索和住宿费用估算模块

这个模块负责查找和推荐酒店，以及估算住宿费用，包括：
- 酒店搜索和筛选
- 基于预算的价格估算
- 城市价格系数调整
- Google Places API集成
- 模拟酒店数据生成
- 住宿费用计算和优化

适用于大模型技术初级用户：
这个模块展示了如何构建一个智能的酒店推荐系统，
包含价格预测、地区调整和用户偏好匹配。
"""

import requests
import json
from typing import List, Dict, Any, Optional
import random
from ..data.models import Hotel
from ..config.api_config import api_config

class HotelEstimator:
    """
    酒店查找和住宿费用估算服务类

    这个类负责处理所有与酒店住宿相关的功能，包括：
    1. 基于目的地的酒店搜索
    2. 根据预算范围筛选酒店
    3. 住宿费用的精确估算
    4. 城市价格差异的调整
    5. API集成和数据处理
    6. 模拟数据生成和回退

    主要功能：
    - Google Places API集成
    - 智能价格预测
    - 预算匹配算法
    - 地区价格调整

    适用于大模型技术初级用户：
    这个类展示了如何设计一个复杂的推荐系统，
    包含多维度的数据处理和智能筛选算法。
    """

    def __init__(self):
        """
        初始化酒店估算服务

        设置API配置、价格范围、城市倍数等参数，
        为酒店搜索和费用估算做准备。
        """
        # API配置
        self.api_key = api_config.GOOGLE_PLACES_API_KEY  # Google Places API密钥
        self.base_url = api_config.PLACES_BASE_URL       # API基础URL
        self.session = requests.Session()                # HTTP会话对象

        # 不同预算类别的基础价格范围（每晚，人民币）
        self.budget_price_ranges = {
            '经济型': {'min': 200, 'max': 560, 'avg': 350},      # 经济型酒店
            '中等预算': {'min': 560, 'max': 1400, 'avg': 910},   # 中档酒店
            '豪华型': {'min': 1400, 'max': 3500, 'avg': 2100}   # 豪华酒店
        }

        # 城市价格倍数（根据目的地生活成本调整）
        self.city_multipliers = {
            '北京': 1.6,      # 一线城市，价格较高
            '上海': 1.7,      # 一线城市，价格最高
            '广州': 1.4,      # 一线城市
            '深圳': 1.5,      # 一线城市
            '杭州': 1.3,      # 新一线城市
            '成都': 1.2,      # 新一线城市
            '西安': 1.1,      # 新一线城市
            '南京': 1.2,      # 新一线城市
            'default': 1.0    # 默认倍数
        }
    
    def find_hotels(self, trip_details: Dict[str, Any]) -> List[Hotel]:
        """
        根据旅行要求查找酒店

        这个方法负责搜索和推荐适合的酒店，包括：
        1. 使用Google Places API搜索真实酒店
        2. 根据预算范围筛选合适选项
        3. 应用城市价格调整
        4. 提供模拟数据作为回退方案

        参数：
        - trip_details: 包含目的地、预算等信息的旅行详情字典

        返回：Hotel对象列表，按推荐度排序

        功能说明：
        1. 提取目的地和预算信息
        2. 尝试API搜索获取真实酒店数据
        3. 处理和筛选搜索结果
        4. 回退到模拟数据（如果需要）
        """
        try:
            hotels = []
            destination = trip_details['destination']                    # 目的地
            budget_range = trip_details.get('budget_range', '中等预算')  # 预算范围

            # 首先尝试API搜索
            if self.api_key:
                hotels_data = self._search_hotels_api(destination)
                hotels = self._process_hotels_data(hotels_data, trip_details)

            # 如果API失败，回退到模拟数据
            if not hotels:
                hotels = self._generate_mock_hotels(trip_details)
            
            # 按评分和价格适配度排序
            hotels = self._rank_hotels(hotels, budget_range)

            return hotels[:6]  # 返回前6个最佳选择

        except Exception as e:
            print(f"查找酒店时出错: {e}")
            return self._generate_mock_hotels(trip_details)
    
    def _search_hotels_api(self, destination: str) -> List[Dict]:
        """
        使用Google Places API搜索酒店

        这个私有方法负责与Google Places API交互，
        搜索指定目的地的酒店信息。

        参数：
        - destination: 目的地名称

        返回：包含酒店信息的字典列表
        """
        try:
            url = f"{self.base_url}/textsearch/json"
            params = {
                'query': f'{destination} 酒店',  # 中文搜索查询
                'key': self.api_key,
                'type': 'lodging'  # 住宿类型
            }

            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            return data.get('results', [])

        except Exception as e:
            print(f"酒店API搜索失败: {e}")
            return []
    
    def _process_hotels_data(self, hotels_data: List[Dict], trip_details: Dict) -> List[Hotel]:
        """
        将Google Places API响应处理为Hotel对象

        这个私有方法负责处理API返回的原始酒店数据，
        包括价格估算、设施生成和对象创建。

        参数：
        - hotels_data: Google Places API返回的酒店数据列表
        - trip_details: 旅行详情，包含预算信息

        返回：处理后的Hotel对象列表
        """
        hotels = []
        destination = trip_details['destination']
        budget_range = trip_details.get('budget_range', '中等预算')

        for hotel_data in hotels_data:
            try:
                name = hotel_data.get('name', '未知酒店')
                rating = hotel_data.get('rating', 4.0)
                address = hotel_data.get('formatted_address', f'{destination} 市中心')
                price_level = hotel_data.get('price_level', 2)

                # 估算每晚价格
                price_per_night = self._estimate_hotel_price(destination, budget_range, price_level, rating)

                # 根据价格等级和评分生成设施
                amenities = self._generate_amenities(price_level, rating)

                hotel = Hotel(
                    name=name,
                    rating=rating,
                    price_per_night=price_per_night,
                    address=address,
                    amenities=amenities
                )

                hotels.append(hotel)

            except Exception as e:
                print(f"处理酒店数据时出错: {e}")
                continue

        return hotels
    
    def _estimate_hotel_price(self, destination: str, budget_range: str, price_level: int, rating: float) -> float:
        """
        估算酒店每晚价格

        这个方法使用多个因素来估算酒店的每晚价格：
        1. 基础价格：根据预算范围确定
        2. 城市调整：根据目的地生活成本
        3. 价格等级：根据Google的价格等级（0-4）
        4. 评分调整：高评分酒店通常更贵
        5. 随机变化：增加价格的真实性

        参数：
        - destination: 目的地名称
        - budget_range: 预算范围
        - price_level: Google的价格等级（0-4）
        - rating: 酒店评分

        返回：估算的每晚价格（人民币）
        """
        # 获取基础价格范围
        base_range = self.budget_price_ranges.get(budget_range, self.budget_price_ranges['中等预算'])
        base_price = base_range['avg']

        # 应用城市价格倍数
        city_key = destination.lower()
        multiplier = self.city_multipliers.get(city_key, self.city_multipliers['default'])

        # 根据价格等级调整（Google Places的0-4级价格体系）
        price_level_multipliers = {0: 0.6, 1: 0.8, 2: 1.0, 3: 1.3, 4: 1.8}
        price_multiplier = price_level_multipliers.get(price_level, 1.0)

        # 根据评分调整（高评分酒店通常更贵）
        if rating >= 4.5:
            rating_multiplier = 1.2    # 优秀酒店
        elif rating >= 4.0:
            rating_multiplier = 1.1    # 良好酒店
        elif rating < 3.5:
            rating_multiplier = 0.9    # 一般酒店
        else:
            rating_multiplier = 1.0    # 标准酒店

        final_price = base_price * multiplier * price_multiplier * rating_multiplier

        # 添加随机变化以增加真实性
        final_price *= random.uniform(0.9, 1.1)

        return round(final_price, 2)
    
    def _generate_amenities(self, price_level: int, rating: float) -> List[str]:
        """
        根据价格等级和评分生成酒店设施

        这个方法根据酒店的价格等级和评分，
        智能生成相应的酒店设施和服务。

        参数：
        - price_level: 价格等级（0-4）
        - rating: 酒店评分

        返回：酒店设施列表
        """
        basic_amenities = ['免费WiFi', '空调', '24小时前台']

        mid_range_amenities = [
            '餐厅', '客房服务', '健身中心', '商务中心',
            '洗衣服务', '停车场', '含早餐'
        ]

        luxury_amenities = [
            'SPA', '游泳池', '礼宾服务', '机场接送',
            '多个餐厅', '酒吧/休息室', '代客泊车',
            '高级床品', '迷你吧', '阳台/景观'
        ]

        amenities = basic_amenities.copy()

        # 中档酒店添加中档设施
        if price_level >= 2:
            amenities.extend(random.sample(mid_range_amenities, min(4, len(mid_range_amenities))))

        # 高档酒店或高评分酒店添加豪华设施
        if price_level >= 3 or rating >= 4.5:
            amenities.extend(random.sample(luxury_amenities, min(3, len(luxury_amenities))))

        return list(set(amenities))  # 去除重复项
    
    def _generate_mock_hotels(self, trip_details: Dict) -> List[Hotel]:
        """
        当API不可用时生成模拟酒店数据

        这个方法生成一系列模拟的酒店数据，
        确保系统在API失败时仍能正常运行。

        参数：
        - trip_details: 旅行详情字典

        返回：模拟的Hotel对象列表
        """
        destination = trip_details['destination']
        budget_range = trip_details.get('budget_range', '中等预算')

        mock_hotels_data = [
            {
                'name': f'{destination}大酒店',
                'rating': 4.5,
                'price_level': 3,
                'address': f'{destination}市中心'
            },
            {
                'name': f'{destination}广场酒店',
                'rating': 4.3,
                'price_level': 3,
                'address': f'{destination}市区'
            },
            {
                'name': f'{destination}经济酒店',
                'rating': 4.0,
                'price_level': 1,
                'address': f'{destination}旅游区'
            },
            {
                'name': f'{destination}舒适酒店',
                'rating': 4.1,
                'price_level': 2,
                'address': f'{destination}中心区'
            },
            {
                'name': f'{destination}豪华度假村',
                'rating': 4.7,
                'price_level': 4,
                'address': f'{destination}高档区'
            },
            {
                'name': f'{destination}商务酒店',
                'rating': 4.2,
                'price_level': 2,
                'address': f'{destination}商务区'
            },
            {
                'name': f'{destination}精品酒店',
                'rating': 4.4,
                'price_level': 3,
                'address': f'{destination}历史街区'
            },
            {
                'name': f'{destination}长住酒店',
                'rating': 3.9,
                'price_level': 1,
                'address': f'{destination}住宅区'
            }
        ]

        hotels = []
        for hotel_data in mock_hotels_data:
            # 估算每晚价格
            price_per_night = self._estimate_hotel_price(
                destination, budget_range, hotel_data['price_level'], hotel_data['rating']
            )

            # 生成酒店设施
            amenities = self._generate_amenities(hotel_data['price_level'], hotel_data['rating'])

            # 创建Hotel对象
            hotel = Hotel(
                name=hotel_data['name'],
                rating=hotel_data['rating'],
                price_per_night=price_per_night,
                address=hotel_data['address'],
                amenities=amenities
            )

            hotels.append(hotel)

        return hotels
    
    def _rank_hotels(self, hotels: List[Hotel], budget_range: str) -> List[Hotel]:
        """
        根据预算范围和质量对酒店进行排序

        这个方法使用综合评分系统对酒店进行排序，
        考虑评分、价格适配度、预算匹配和设施质量。

        参数：
        - hotels: 酒店列表
        - budget_range: 预算范围

        返回：按推荐度排序的酒店列表

        评分规则：
        - 评分权重：评分 × 10
        - 价格适配：与目标价格的匹配度
        - 预算匹配：在预算范围内+5分
        - 设施奖励：设施数量 × 0.5
        """
        target_range = self.budget_price_ranges.get(budget_range, self.budget_price_ranges['中等预算'])

        scored_hotels = []
        for hotel in hotels:
            score = 0

            # 基于评分的得分
            score += hotel.rating * 10

            # 基于价格适配度的得分
            price_diff = abs(hotel.price_per_night - target_range['avg'])
            max_diff = target_range['max'] - target_range['min']
            price_score = max(0, 10 - (price_diff / max_diff * 10))
            score += price_score

            # 在预算范围内的奖励分
            if target_range['min'] <= hotel.price_per_night <= target_range['max']:
                score += 5

            # 设施质量奖励分
            score += len(hotel.amenities) * 0.5

            scored_hotels.append((hotel, score))

        # 按分数降序排序
        scored_hotels.sort(key=lambda x: x[1], reverse=True)
        return [hotel for hotel, _ in scored_hotels]
    
    def calculate_accommodation_cost(self, hotels: List[Hotel], nights: int, budget_range: str) -> Dict[str, Any]:
        """
        计算总住宿费用

        这个方法计算整个旅行期间的住宿费用，
        选择最适合预算的酒店并提供备选方案。

        参数：
        - hotels: 可选酒店列表
        - nights: 住宿夜数
        - budget_range: 预算范围

        返回：包含费用详情和推荐酒店的字典
        """
        if not hotels:
            return {'total_cost': 0, 'cost_per_night': 0, 'recommended_hotel': None}

        # 获取预算范围内的最佳酒店
        target_range = self.budget_price_ranges.get(budget_range, self.budget_price_ranges['中等预算'])

        suitable_hotels = [h for h in hotels if target_range['min'] <= h.price_per_night <= target_range['max']]
        recommended_hotel = suitable_hotels[0] if suitable_hotels else hotels[0]

        total_cost = recommended_hotel.calculate_total_cost(nights)

        return {
            'total_cost': total_cost,                    # 总费用
            'cost_per_night': recommended_hotel.price_per_night,  # 每晚费用
            'recommended_hotel': recommended_hotel,      # 推荐酒店
            'alternatives': hotels[:3]                   # 前3个备选方案
        }
    
    def get_hotel_suggestions_by_group_size(self, hotels: List[Hotel], group_size: int) -> List[Dict[str, Any]]:
        """
        根据团队规模建议酒店住宿安排

        这个方法根据旅行团队的人数，为每个推荐酒店
        提供最优的房间安排和费用分摊方案。

        参数：
        - hotels: 推荐酒店列表
        - group_size: 团队人数

        返回：包含住宿安排详情的字典列表

        安排规则：
        - 1-2人：单间双人房
        - 3-4人：两间双人房
        - 5人以上：多间双人房（每房2人）
        """
        suggestions = []

        for hotel in hotels[:3]:  # 前3个推荐酒店
            if group_size <= 2:
                # 单间安排
                arrangement = {
                    'hotel': hotel,
                    'rooms': 1,
                    'room_type': '双人房',
                    'total_per_night': hotel.price_per_night,
                    'cost_per_person': hotel.price_per_night / group_size
                }
            elif group_size <= 4:
                # 两间房安排
                arrangement = {
                    'hotel': hotel,
                    'rooms': 2,
                    'room_type': '2间双人房',
                    'total_per_night': hotel.price_per_night * 2,
                    'cost_per_person': (hotel.price_per_night * 2) / group_size
                }
            else:
                # 多间房安排
                rooms_needed = (group_size + 1) // 2  # 每房2人
                arrangement = {
                    'hotel': hotel,
                    'rooms': rooms_needed,
                    'room_type': f'{rooms_needed}间双人房',
                    'total_per_night': hotel.price_per_night * rooms_needed,
                    'cost_per_person': (hotel.price_per_night * rooms_needed) / group_size
                }

            suggestions.append(arrangement)

        return suggestions