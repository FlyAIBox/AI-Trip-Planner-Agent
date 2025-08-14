"""
行程规划逻辑模块

这个模块负责创建详细的逐日行程安排，包括：
- 景点和活动的时间分配
- 基于天气的活动推荐
- 交通方式和时间估算
- 餐饮安排和时间规划
- 每日费用计算和优化
- 个性化行程定制

适用于大模型技术初级用户：
这个模块展示了如何设计一个智能的行程规划系统，
包含时间管理、天气适应和个性化推荐算法。
"""

import random
from typing import Dict, Any, List
from datetime import datetime, date, timedelta
from ..data.models import DayPlan, Weather, Attraction, Transportation

class ItineraryPlanner:
    """
    行程规划服务类

    这个类负责创建详细的逐日旅行行程，包括：
    1. 景点和活动的智能分配
    2. 基于天气的活动调整
    3. 时间段的合理安排
    4. 交通方式的选择和估算
    5. 餐饮时间的规划
    6. 每日费用的计算

    主要功能：
    - 智能时间分配
    - 天气适应性规划
    - 交通优化
    - 个性化定制

    适用于大模型技术初级用户：
    这个类展示了如何构建一个复杂的规划算法，
    包含多维度的约束条件和优化目标。
    """

    def __init__(self):
        """
        初始化行程规划服务

        设置活动时间偏好、天气活动推荐和交通估算，
        为智能行程规划做准备。
        """
        # 活动时间偏好设置
        self.activity_timings = {
            'morning': {    # 上午时段
                'start': 9, 'end': 12,
                'activities': ['博物馆', '美术馆', '公园', '观光']
            },
            'afternoon': {  # 下午时段
                'start': 13, 'end': 17,
                'activities': ['活动', '购物', '游览', '景点']
            },
            'evening': {    # 晚上时段
                'start': 18, 'end': 21,
                'activities': ['用餐', '娱乐', '夜生活', '文化']
            }
        }

        # 基于天气的活动推荐
        self.weather_activities = {
            'sunny': ['户外游览', '公园', '步行游', '户外活动'],      # 晴天
            'rainy': ['博物馆', '美术馆', '购物', '室内景点'],       # 雨天
            'cloudy': ['观光', '文化景点', '混合活动'],             # 多云
            'cold': ['室内景点', '博物馆', '温暖咖啡厅', '购物'],    # 寒冷
            'hot': ['室内景点', '早晨游览', '晚间活动']              # 炎热
        }

        # 活动间交通估算（人民币和时间）
        self.transport_estimates = {
            'walking': {'cost': 0, 'time': 15},           # 步行
            'public_transport': {'cost': 20, 'time': 20}, # 公共交通
            'taxi': {'cost': 80, 'time': 15},             # 出租车
            'uber': {'cost': 70, 'time': 12}              # 网约车
        }
    
    def create_itinerary(self, trip_details: Dict[str, Any], weather_data: List[Weather],
                        attractions: List[Attraction], restaurants: List[Attraction],
                        activities: List[Attraction]) -> List[DayPlan]:
        """
        创建完整的逐日行程安排

        这个方法是行程规划的核心，它整合所有信息，
        创建优化的每日行程计划。

        参数：
        - trip_details: 旅行详情字典
        - weather_data: 天气预报数据列表
        - attractions: 景点列表
        - restaurants: 餐厅列表
        - activities: 活动列表

        返回：DayPlan对象列表，每个代表一天的行程

        功能说明：
        1. 提取旅行基本信息
        2. 将景点、餐厅、活动分配到各天
        3. 根据天气优化每日安排
        4. 计算每日费用和交通
        5. 生成完整的行程计划
        """

        # 提取基本信息
        total_days = trip_details['total_days']                           # 总天数
        start_date = trip_details['start_date']                          # 开始日期
        budget_range = trip_details.get('budget_range', '中等预算')       # 预算范围
        group_size = trip_details.get('group_size', 1)                   # 团队人数
        interests = trip_details.get('preferences', {}).get('interests', [])  # 兴趣爱好

        itinerary = []  # 行程列表

        # 将景点、餐厅和活动分配到各天
        daily_attractions = self._distribute_items_across_days(attractions, total_days, 2)  # 每天2个景点
        daily_restaurants = self._distribute_items_across_days(restaurants, total_days, 2)  # 每天2个餐厅
        daily_activities = self._distribute_items_across_days(activities, total_days, 1)
        
        for day_num in range(1, total_days + 1):
            current_date = start_date + timedelta(days=day_num - 1)
            date_str = current_date.strftime('%Y-%m-%d')
            
            # 获取当天天气信息
            day_weather = self._get_weather_for_day(weather_data, day_num - 1)

            # 创建日程计划
            day_plan = DayPlan(
                day=day_num,
                date=date_str,
                weather=day_weather
            )

            # 添加当天的景点
            if day_num <= len(daily_attractions):
                day_plan.attractions = daily_attractions[day_num - 1]

            # 添加当天的餐厅
            if day_num <= len(daily_restaurants):
                day_plan.restaurants = daily_restaurants[day_num - 1]

            # 添加当天的活动
            if day_num <= len(daily_activities):
                day_plan.activities = daily_activities[day_num - 1]

            # 根据天气和兴趣优化日程安排
            day_plan = self._optimize_day_schedule(day_plan, interests, budget_range)

            # 添加活动间的交通安排
            day_plan.transportation = self._plan_transportation(day_plan, budget_range)

            # 计算每日费用
            day_plan.daily_cost = self._calculate_daily_cost(day_plan, group_size)

            itinerary.append(day_plan)

        # 平衡各天的行程安排
        itinerary = self._balance_itinerary(itinerary, total_days)
        
        return itinerary
    
    def _distribute_items_across_days(self, items: List[Attraction], total_days: int, items_per_day: int) -> List[List[Attraction]]:
        """
        将景点/餐厅/活动分配到各天

        这个方法负责将所有的景点、餐厅和活动
        合理地分配到旅行的各个天数中。

        参数：
        - items: 要分配的项目列表
        - total_days: 总天数
        - items_per_day: 每天的项目数量

        返回：按天分组的项目列表
        """
        if not items:
            return [[] for _ in range(total_days)]

        # 按评分排序（最好的优先）
        sorted_items = sorted(items, key=lambda x: x.rating, reverse=True)

        daily_items = []
        for day in range(total_days):
            start_idx = day * items_per_day
            end_idx = start_idx + items_per_day
            day_items = sorted_items[start_idx:end_idx]
            daily_items.append(day_items)

        return daily_items
    
    def _get_weather_for_day(self, weather_data: List[Weather], day_index: int) -> Weather:
        """
        获取特定日期的天气数据

        这个方法从天气预报数据中获取指定日期的天气信息，
        如果数据不足则提供默认天气。

        参数：
        - weather_data: 天气预报数据列表
        - day_index: 日期索引（从0开始）

        返回：Weather对象
        """
        if day_index < len(weather_data):
            return weather_data[day_index]

        # 如果数据不足，使用默认天气
        return Weather(
            temperature=22.0,
            description="多云",
            humidity=65,
            wind_speed=5.0,
            feels_like=24.0,
            date=(datetime.now() + timedelta(days=day_index)).strftime('%Y-%m-%d')
        )
    
    def _optimize_day_schedule(self, day_plan: DayPlan, interests: List[str], budget_range: str) -> DayPlan:
        """
        根据天气和偏好优化每日日程

        这个方法根据天气条件和用户偏好调整每日活动的顺序，
        确保在不同天气条件下都有合适的活动安排。

        参数：
        - day_plan: 每日计划对象
        - interests: 用户兴趣列表
        - budget_range: 预算范围

        返回：优化后的每日计划
        """

        # 获取天气条件分类
        weather_condition = self._categorize_weather(day_plan.weather)

        # 根据天气重新排序活动
        if weather_condition == 'rainy':
            # 优先安排室内活动
            day_plan.attractions = self._prioritize_indoor_activities(day_plan.attractions)
            day_plan.activities = self._prioritize_indoor_activities(day_plan.activities)
        elif weather_condition == 'sunny':
            # 优先安排户外活动
            day_plan.attractions = self._prioritize_outdoor_activities(day_plan.attractions)
            day_plan.activities = self._prioritize_outdoor_activities(day_plan.activities)

        # 添加时间建议
        day_plan = self._add_timing_recommendations(day_plan)

        # 添加天气特定建议
        day_plan = self._add_weather_recommendations(day_plan, weather_condition)

        return day_plan
    
    def _categorize_weather(self, weather: Weather) -> str:
        """
        对天气条件进行分类

        根据天气描述和温度将天气分为不同类别，
        用于后续的活动安排优化。
        """
        description = weather.description.lower()
        temp = weather.temperature

        if '雨' in description or 'rain' in description or 'storm' in description:
            return 'rainy'
        elif temp < 10:
            return 'cold'
        elif temp > 30:
            return 'hot'
        elif '晴' in description or 'sun' in description or 'clear' in description:
            return 'sunny'
        else:
            return 'cloudy'

    def _prioritize_indoor_activities(self, activities: List[Attraction]) -> List[Attraction]:
        """
        为恶劣天气优先安排室内活动

        这个方法将活动按室内/室外分类，
        在恶劣天气时优先推荐室内活动。
        """
        indoor_keywords = ['博物馆', '美术馆', '商场', '中心', '室内', '剧院', '电影院',
                          'museum', 'gallery', 'mall', 'center', 'indoor', 'theater', 'cinema']

        indoor_activities = []
        outdoor_activities = []

        for activity in activities:
            is_indoor = any(keyword in activity.name.lower() or keyword in activity.description.lower()
                          for keyword in indoor_keywords)

            if is_indoor:
                indoor_activities.append(activity)
            else:
                outdoor_activities.append(activity)

        return indoor_activities + outdoor_activities
    
    def _prioritize_outdoor_activities(self, activities: List[Attraction]) -> List[Attraction]:
        """
        为好天气优先安排户外活动

        这个方法根据天气条件智能地重新排列活动顺序，
        将户外活动优先安排在天气良好的时候。

        工作原理：
        1. 定义户外活动关键词列表
        2. 遍历所有活动，根据名称和描述判断是否为户外活动
        3. 将活动分为户外和室内两类
        4. 返回户外活动优先的排序列表

        参数：
        - activities: 待排序的活动列表

        返回：重新排序后的活动列表（户外活动在前）

        适用于大模型技术初级用户：
        这个方法展示了如何使用关键词匹配和列表操作
        来实现智能的内容分类和排序功能。
        """
        # 定义户外活动的关键词（中英文混合支持）
        outdoor_keywords = [
            'park', 'garden', 'tour', 'walk', 'outdoor', 'beach', 'view', 'nature',
            '公园', '花园', '游览', '步行', '户外', '海滩', '景观', '自然'
        ]

        outdoor_activities = []  # 户外活动列表
        indoor_activities = []   # 室内活动列表

        # 遍历所有活动进行分类
        for activity in activities:
            # 检查活动名称或描述中是否包含户外关键词
            is_outdoor = any(keyword in activity.name.lower() or keyword in activity.description.lower()
                           for keyword in outdoor_keywords)

            if is_outdoor:
                outdoor_activities.append(activity)
            else:
                indoor_activities.append(activity)

        # 返回户外活动优先的列表
        return outdoor_activities + indoor_activities

    def _add_timing_recommendations(self, day_plan: DayPlan) -> DayPlan:
        """
        为活动添加时间安排建议

        这个方法为每日行程中的各种活动分配合理的时间段，
        确保行程安排符合常规的旅行节奏和用餐时间。

        时间安排策略：
        1. 景点参观：上午和下午的黄金时段
        2. 活动体验：跨越上午到下午的较长时段
        3. 餐厅用餐：标准的午餐和晚餐时间

        参数：
        - day_plan: 需要添加时间建议的日程计划

        返回：添加了时间建议的日程计划

        适用于大模型技术初级用户：
        这个方法展示了如何为对象动态添加属性，
        以及如何设计合理的时间分配算法。
        """

        # 为景点添加时间安排
        for i, attraction in enumerate(day_plan.attractions):
            if i == 0:  # 第一个景点安排在上午
                attraction.recommended_time = "上午9:00 - 11:00"
                attraction.time_slot = "上午"
            else:       # 其他景点安排在下午
                attraction.recommended_time = "下午2:00 - 4:00"
                attraction.time_slot = "下午"

        # 为活动添加时间安排（通常需要较长时间）
        for activity in day_plan.activities:
            activity.recommended_time = "上午10:00 - 下午1:00"
            activity.time_slot = "上午-下午"

        # 为餐厅添加用餐时间安排
        for i, restaurant in enumerate(day_plan.restaurants):
            if i == 0:  # 第一个餐厅作为午餐
                restaurant.recommended_time = "中午12:00 - 1:30"
                restaurant.time_slot = "午餐"
            else:       # 其他餐厅作为晚餐
                restaurant.recommended_time = "晚上7:00 - 9:00"
                restaurant.time_slot = "晚餐"

        return day_plan

    def _add_weather_recommendations(self, day_plan: DayPlan, weather_condition: str) -> DayPlan:
        """
        根据天气条件添加专门的旅行建议

        这个方法分析当日的天气状况，为旅行者提供
        针对性的建议和注意事项，确保旅行体验最佳。

        天气建议策略：
        1. 雨天：重点推荐室内活动和防雨措施
        2. 晴天：鼓励户外活动并提醒防晒
        3. 寒冷：建议保暖措施和室内活动
        4. 炎热：提醒防暑和合理安排活动时间

        参数：
        - day_plan: 需要添加天气建议的日程计划
        - weather_condition: 天气状况描述

        返回：添加了天气建议的日程计划

        适用于大模型技术初级用户：
        这个方法展示了如何根据条件生成个性化建议，
        以及如何动态扩展对象的属性。
        """
        recommendations = []

        # 根据不同天气条件提供相应建议
        if weather_condition == 'rainy' or '雨' in weather_condition:
            recommendations.extend([
                "携带雨伞或雨衣",
                "今天重点安排室内景点",
                "考虑博物馆巡游",
                "购物中心是不错的选择"
            ])
        elif weather_condition == 'sunny' or '晴' in weather_condition:
            recommendations.extend([
                "户外活动的绝佳天气",
                "别忘记防晒霜和充足的水",
                "非常适合徒步游览",
                "考虑户外用餐"
            ])
        elif weather_condition == 'cold' or '冷' in weather_condition or '寒' in weather_condition:
            recommendations.extend([
                "多层穿衣保暖",
                "推荐室内景点",
                "热饮和温暖的咖啡厅",
                "缩短户外活动时间"
            ])
        elif weather_condition == 'hot' or '热' in weather_condition or '炎热' in weather_condition:
            recommendations.extend([
                "保持水分充足，寻找阴凉处",
                "高温时段安排室内活动",
                "清晨或傍晚进行户外活动",
                "推荐有空调的场所"
            ])

        # 将建议添加到日程计划的属性中
        if not hasattr(day_plan, 'recommendations'):
            day_plan.recommendations = []
        day_plan.recommendations.extend(recommendations)

        return day_plan

    def _plan_transportation(self, day_plan: DayPlan, budget_range: str) -> List[Transportation]:
        """
        规划活动间的交通安排

        这个方法根据预算范围和活动数量，智能地规划
        一天中各个活动之间的交通方式和费用。

        交通规划策略：
        1. 根据预算范围确定可用的交通方式
        2. 计算活动间的交通需求
        3. 随机选择合适的交通方式（模拟真实选择）
        4. 估算交通费用和时间

        预算对应的交通方式：
        - 经济型：步行、公共交通
        - 中等预算：步行、公共交通、网约车
        - 豪华型：出租车、网约车、公共交通

        参数：
        - day_plan: 日程计划对象
        - budget_range: 预算范围

        返回：交通安排列表

        适用于大模型技术初级用户：
        这个方法展示了如何根据不同条件进行决策，
        以及如何处理复杂的业务逻辑。
        """
        transportation = []

        # 计算当日活动总数
        total_activities = len(day_plan.attractions) + len(day_plan.activities) + len(day_plan.restaurants)

        # 如果活动数量少于等于1，无需交通安排
        if total_activities <= 1:
            return transportation

        # 根据预算确定可用的交通方式
        transport_modes = {
            '经济型': ['walking', 'public_transport'],
            '中等预算': ['walking', 'public_transport', 'uber'],
            '豪华型': ['taxi', 'uber', 'public_transport']
        }

        # 获取当前预算对应的交通方式，默认为公共交通和步行
        available_modes = transport_modes.get(budget_range, ['public_transport', 'walking'])

        # 为活动间创建交通安排
        for i in range(total_activities - 1):
            # 随机选择一种可用的交通方式
            mode = random.choice(available_modes)
            transport_info = self.transport_estimates[mode]

            # 创建交通对象
            transport = Transportation(
                mode=mode.replace('_', ' ').title(),  # 格式化交通方式名称
                estimated_cost=transport_info['cost'],
                duration=transport_info['time']
            )
            transportation.append(transport)

        return transportation

    def _calculate_daily_cost(self, day_plan: DayPlan, group_size: int) -> float:
        """
        计算当日总费用

        这个方法汇总一天中所有活动的费用，包括景点门票、
        餐饮消费、活动费用和交通费用，并考虑团队人数。

        费用计算包括：
        1. 景点门票费用 × 团队人数
        2. 餐厅用餐费用 × 团队人数
        3. 活动体验费用 × 团队人数
        4. 交通出行费用 × 团队人数

        参数：
        - day_plan: 包含当日所有活动的日程计划
        - group_size: 团队人数

        返回：当日总费用（保留2位小数）

        适用于大模型技术初级用户：
        这个方法展示了如何进行费用汇总计算，
        以及如何处理浮点数的精度问题。
        """
        total_cost = 0.0

        # 累加景点费用
        for attraction in day_plan.attractions:
            total_cost += attraction.estimated_cost * group_size

        # 累加餐厅费用
        for restaurant in day_plan.restaurants:
            total_cost += restaurant.estimated_cost * group_size

        # 累加活动费用
        for activity in day_plan.activities:
            total_cost += activity.estimated_cost * group_size

        # 累加交通费用
        for transport in day_plan.transportation:
            total_cost += transport.estimated_cost * group_size

        # 返回四舍五入到2位小数的总费用
        return round(total_cost, 2)

    def _balance_itinerary(self, itinerary: List[DayPlan], total_days: int) -> List[DayPlan]:
        """
        平衡各天的活动安排，避免某天过度安排

        这个方法分析整个行程的活动分布，确保每天的活动量
        相对均衡，避免某天过于繁忙而其他天过于轻松。

        平衡策略：
        1. 计算所有天数的平均景点和活动数量
        2. 识别活动过多的天数
        3. 将多余的活动重新分配到较轻松的天数
        4. 重新计算调整后的每日费用

        参数：
        - itinerary: 完整的行程计划列表
        - total_days: 旅行总天数

        返回：平衡后的行程计划列表

        适用于大模型技术初级用户：
        这个方法展示了如何实现负载均衡算法，
        以及如何在复杂数据结构中进行元素重分配。
        """

        # 计算所有天数的平均活动数量
        total_attractions = sum(len(day.attractions) for day in itinerary)
        total_activities = sum(len(day.activities) for day in itinerary)

        # 计算每天的目标景点和活动数量（至少为1）
        target_attractions_per_day = max(1, total_attractions // total_days)
        target_activities_per_day = max(1, total_activities // total_days)

        # 重新分配过度安排的天数
        for i, day_plan in enumerate(itinerary):
            # 如果某天的景点数量超过目标值+1（允许一定的灵活性）
            if len(day_plan.attractions) > target_attractions_per_day + 1:
                # 将多余的景点移出
                excess = day_plan.attractions[target_attractions_per_day:]
                day_plan.attractions = day_plan.attractions[:target_attractions_per_day]

                # 寻找活动较少的天数来接收多余的景点
                for j, other_day in enumerate(itinerary):
                    # 如果是不同的天数且该天景点数量少于目标值，且还有多余景点
                    if j != i and len(other_day.attractions) < target_attractions_per_day and excess:
                        other_day.attractions.append(excess.pop(0))

            # 重新平衡后重新计算每日费用
            day_plan.daily_cost = self._calculate_daily_cost(day_plan, 1)  # 基础费用，后续会乘以团队人数

        return itinerary
    
    def generate_itinerary_summary(self, itinerary: List[DayPlan]) -> Dict[str, Any]:
        """
        生成完整行程的摘要

        这个方法分析整个行程计划，生成统计信息和亮点摘要，
        帮助用户快速了解旅行的整体安排。

        参数：
        - itinerary: 完整的行程计划列表

        返回：包含行程统计和亮点的摘要字典
        """

        total_attractions = sum(len(day.attractions) for day in itinerary)
        total_restaurants = sum(len(day.restaurants) for day in itinerary)
        total_activities = sum(len(day.activities) for day in itinerary)
        total_cost = sum(day.daily_cost for day in itinerary)

        # 找出评分最高的活动
        all_items = []
        for day in itinerary:
            all_items.extend(day.attractions + day.restaurants + day.activities)

        top_rated = sorted(all_items, key=lambda x: x.rating, reverse=True)[:5]

        # 天气概览
        weather_conditions = [day.weather.description for day in itinerary]
        
        summary = {
            'total_days': len(itinerary),
            'total_attractions': total_attractions,
            'total_restaurants': total_restaurants,
            'total_activities': total_activities,
            'estimated_total_cost': round(total_cost, 2),
            'average_daily_cost': round(total_cost / len(itinerary), 2) if itinerary else 0,
            'top_rated_experiences': [
                {
                    'name': item.name,
                    'type': item.type,
                    'rating': item.rating,
                    'cost': item.estimated_cost
                } for item in top_rated
            ],
            'weather_overview': {
                'conditions': weather_conditions,
                'rainy_days': len([w for w in weather_conditions if '雨' in w or 'rain' in w.lower()]),
                'sunny_days': len([w for w in weather_conditions if '晴' in w or 'sun' in w.lower() or 'clear' in w.lower()])
            },
            'daily_highlights': [
                {
                    'day': day.day,
                    'date': day.date,
                    'weather': day.weather.description,
                    'main_attractions': [a.name for a in day.attractions[:2]],
                    'main_activity': day.activities[0].name if day.activities else None,
                    'cost': day.daily_cost
                } for day in itinerary
            ]
        }
        
        return summary
    
    def export_itinerary_to_text(self, itinerary: List[DayPlan], trip_details: Dict[str, Any]) -> str:
        """
        将行程导出为格式化文本

        这个方法将完整的行程计划转换为易于阅读的文本格式，
        方便用户打印或分享。

        参数：
        - itinerary: 完整的行程计划列表
        - trip_details: 旅行详情字典

        返回：格式化的行程文本字符串
        """

        text_output = []
        text_output.append("=" * 60)
        text_output.append(f"旅行行程 - {trip_details['destination'].upper()}")
        text_output.append("=" * 60)
        text_output.append(f"时长: {len(itinerary)} 天")
        text_output.append(f"日期: {trip_details['start_date']} 至 {trip_details['end_date']}")
        text_output.append(f"预算范围: {trip_details['budget_range'].title()}")
        text_output.append("")
        
        for day_plan in itinerary:
            text_output.append(f"第 {day_plan.day} 天 - {day_plan.date}")
            text_output.append("-" * 40)
            text_output.append(f"天气: {day_plan.weather}")
            text_output.append("")

            if day_plan.attractions:
                text_output.append("🏛️  景点:")
                for attraction in day_plan.attractions:
                    time_info = getattr(attraction, 'recommended_time', '灵活安排')
                    text_output.append(f"   • {attraction.name} ({time_info})")
                    text_output.append(f"     评分: {attraction.rating}⭐ | 费用: ¥{attraction.estimated_cost}")
                text_output.append("")

            if day_plan.activities:
                text_output.append("🎯 活动:")
                for activity in day_plan.activities:
                    time_info = getattr(activity, 'recommended_time', '灵活安排')
                    text_output.append(f"   • {activity.name} ({time_info})")
                    text_output.append(f"     时长: {activity.duration}小时 | 费用: ¥{activity.estimated_cost}")
                text_output.append("")

            if day_plan.restaurants:
                text_output.append("🍽️  用餐:")
                for restaurant in day_plan.restaurants:
                    time_info = getattr(restaurant, 'recommended_time', '用餐时间')
                    text_output.append(f"   • {restaurant.name} ({time_info})")
                    text_output.append(f"     评分: {restaurant.rating}⭐ | 费用: ¥{restaurant.estimated_cost}")
                text_output.append("")

            if hasattr(day_plan, 'recommendations') and day_plan.recommendations:
                text_output.append("💡 推荐建议:")
                for rec in day_plan.recommendations:
                    text_output.append(f"   • {rec}")
                text_output.append("")

            text_output.append(f"💰 每日费用估算: ¥{day_plan.daily_cost}")
            text_output.append("")
            text_output.append("=" * 60)
            text_output.append("")

        return "\n".join(text_output)