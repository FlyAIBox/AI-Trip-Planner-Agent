"""
总费用和每日成本计算模块

这个模块负责计算旅行的各项费用，包括：
- 住宿费用计算和分摊
- 餐饮费用估算
- 活动和景点费用
- 交通费用预算
- 杂项费用估算
- 总费用汇总和分析

适用于大模型技术初级用户：
这个模块展示了如何设计一个复杂的费用计算系统，
包含多种费用类型的处理和预算范围的智能调整。
"""

from typing import Dict, Any, List
from ..data.models import Hotel, Attraction, Transportation

class ExpenseCalculator:
    """
    旅行费用计算服务类

    这个类负责计算旅行的所有相关费用，包括：
    1. 住宿费用的计算和优化
    2. 餐饮费用的估算和分配
    3. 活动和景点的费用预算
    4. 交通费用的规划
    5. 杂项费用的预估
    6. 总费用的汇总和分析

    主要功能：
    - 多维度费用计算
    - 预算范围智能调整
    - 团队费用分摊
    - 详细费用分解

    适用于大模型技术初级用户：
    这个类展示了如何设计一个全面的费用管理系统，
    包含复杂的计算逻辑和用户友好的费用分析。
    """

    def __init__(self):
        """
        初始化费用计算服务

        设置不同预算范围的倍数、交通费用估算和杂项费用标准，
        为各种费用计算做准备。
        """
        # 不同预算范围的基础倍数
        self.budget_multipliers = {
            '经济型': 0.8,     # 经济型：费用较低
            '中等预算': 1.0,   # 中等：标准费用
            '豪华型': 1.5      # 豪华：费用较高
        }

        # 每日交通费用估算（人民币）
        self.transportation_costs = {
            '经济型': 100,     # 公共交通、步行
            '中等预算': 250,   # 混合交通、部分出租车
            '豪华型': 420      # 私人交通、出租车
        }

        # 每日杂项费用（购物、小费等）
        self.miscellaneous_costs = {
            '经济型': 140,     # 基本购物和小费
            '中等预算': 280,   # 适度购物和娱乐
            '豪华型': 560      # 高端购物和服务
        }
    
    def calculate_total_expenses(self, trip_details: Dict[str, Any], hotels: List[Hotel],
                               attractions: List[Attraction], restaurants: List[Attraction],
                               activities: List[Attraction]) -> Dict[str, Any]:
        """
        计算全面的旅行费用

        这个方法是费用计算的核心，它整合所有费用类型，
        生成详细的费用分解和总结。

        参数：
        - trip_details: 旅行详情字典
        - hotels: 酒店列表
        - attractions: 景点列表
        - restaurants: 餐厅列表
        - activities: 活动列表

        返回：包含详细费用分解的字典

        功能说明：
        1. 提取旅行基本信息
        2. 计算各类费用
        3. 汇总总费用
        4. 生成费用分析报告
        """

        # 提取基本信息
        total_days = trip_details['total_days']                        # 总天数
        budget_range = trip_details.get('budget_range', '中等预算')     # 预算范围
        group_size = trip_details.get('group_size', 1)                # 团队人数

        # 计算住宿费用
        accommodation_cost = self._calculate_accommodation_cost(hotels, total_days, budget_range)

        # 计算餐饮费用
        food_cost = self._calculate_food_cost(restaurants, total_days, group_size, budget_range)

        # 计算活动费用（景点+活动）
        activities_cost = self._calculate_activities_cost(attractions + activities, total_days, group_size, budget_range)

        # 计算交通费用
        transportation_cost = self._calculate_transportation_cost(total_days, group_size, budget_range)
        
        # 计算杂项费用
        miscellaneous_cost = self._calculate_miscellaneous_cost(total_days, group_size, budget_range)

        # 计算总费用
        total_cost = (accommodation_cost + food_cost + activities_cost +
                     transportation_cost + miscellaneous_cost)

        daily_budget = total_cost / total_days if total_days > 0 else 0

        # 创建详细费用分解
        expense_breakdown = {
            'base_currency': 'CNY',  # 基础货币：人民币
            'trip_duration': total_days,
            'group_size': group_size,
            'budget_range': budget_range,

            # 主要费用类别
            'accommodation_cost': round(accommodation_cost, 2),    # 住宿费用
            'food_cost': round(food_cost, 2),                     # 餐饮费用
            'activities_cost': round(activities_cost, 2),         # 活动费用
            'transportation_cost': round(transportation_cost, 2), # 交通费用
            'miscellaneous_cost': round(miscellaneous_cost, 2),   # 杂项费用

            # 费用汇总
            'total_cost': round(total_cost, 2),                   # 总费用
            'daily_budget': round(daily_budget, 2),               # 每日预算
            'cost_per_person': round(total_cost / group_size, 2) if group_size > 0 else 0,        # 人均费用
            'daily_cost_per_person': round(daily_budget / group_size, 2) if group_size > 0 else 0, # 人均每日费用

            # 详细费用分解
            'detailed_breakdown': self._create_detailed_breakdown(
                hotels, attractions, restaurants, activities, trip_details
            ),

            # 费用百分比分解
            'cost_percentages': self._calculate_cost_percentages(
                accommodation_cost, food_cost, activities_cost,
                transportation_cost, miscellaneous_cost, total_cost
            )
        }
        
        return expense_breakdown
    
    def _calculate_accommodation_cost(self, hotels: List[Hotel], total_days: int, budget_range: str) -> float:
        """
        计算住宿费用

        这个方法负责计算整个旅行期间的住宿费用，包括：
        1. 根据预算范围筛选合适的酒店
        2. 使用回退估算（如果没有酒店数据）
        3. 计算总住宿费用

        参数：
        - hotels: 可选酒店列表
        - total_days: 总住宿天数
        - budget_range: 预算范围

        返回：总住宿费用（人民币）
        """
        if not hotels:
            # 回退估算（如果没有酒店数据）
            base_costs = {'经济型': 280, '中等预算': 700, '豪华型': 1750}
            return base_costs.get(budget_range, 700) * total_days

        # 根据预算选择最合适的酒店
        suitable_hotels = self._filter_hotels_by_budget(hotels, budget_range)
        selected_hotel = suitable_hotels[0] if suitable_hotels else hotels[0]

        return selected_hotel.calculate_total_cost(total_days)
    
    def _calculate_food_cost(self, restaurants: List[Attraction], total_days: int,
                           group_size: int, budget_range: str) -> float:
        """
        计算餐饮费用

        这个方法负责计算整个旅行期间的餐饮费用，包括：
        1. 基于餐厅数据计算平均用餐费用
        2. 使用回退估算（如果没有餐厅数据）
        3. 考虑团队人数和用餐频率

        参数：
        - restaurants: 推荐餐厅列表
        - total_days: 总天数
        - group_size: 团队人数
        - budget_range: 预算范围

        返回：总餐饮费用（人民币）
        """
        if not restaurants:
            # 回退估算（每天3餐）
            base_daily_cost = {'经济型': 175, '中等预算': 350, '豪华型': 700}
            return base_daily_cost.get(budget_range, 350) * total_days * group_size

        # 基于餐厅费用计算（假设每天2-3次餐厅用餐）
        avg_meal_cost = sum(r.estimated_cost for r in restaurants[:5]) / min(len(restaurants), 5)
        meals_per_day = 2.5  # 平均每天2-3次餐厅用餐

        daily_food_cost = avg_meal_cost * meals_per_day * group_size
        return daily_food_cost * total_days
    
    def _calculate_activities_cost(self, activities: List[Attraction], total_days: int,
                                 group_size: int, budget_range: str) -> float:
        """
        计算活动和景点费用

        这个方法负责计算所有娱乐活动和景点的费用，包括：
        1. 基于计划活动计算平均费用
        2. 使用回退估算（如果没有活动数据）
        3. 考虑每日活动频率和团队人数

        参数：
        - activities: 计划的活动和景点列表
        - total_days: 总天数
        - group_size: 团队人数
        - budget_range: 预算范围

        返回：总活动费用（人民币）
        """
        if not activities:
            # 回退估算
            base_daily_cost = {'经济型': 210, '中等预算': 420, '豪华型': 840}
            return base_daily_cost.get(budget_range, 420) * total_days * group_size

        # 基于计划活动计算（每天1-2个主要活动）
        activities_per_day = min(2, len(activities) / max(total_days, 1))
        avg_activity_cost = sum(a.estimated_cost for a in activities[:10]) / min(len(activities), 10)

        daily_activities_cost = avg_activity_cost * activities_per_day * group_size
        return daily_activities_cost * total_days

    def _calculate_transportation_cost(self, total_days: int, group_size: int, budget_range: str) -> float:
        """
        计算交通费用

        这个方法负责计算旅行期间的交通费用，包括：
        1. 根据预算范围确定每日交通费用
        2. 考虑团队规模的优惠（拼车等）
        3. 计算总交通费用

        参数：
        - total_days: 总天数
        - group_size: 团队人数
        - budget_range: 预算范围

        返回：总交通费用（人民币）
        """
        daily_transport_cost = self.transportation_costs.get(budget_range, 250)

        # 大团队优惠（拼车等，非线性增长）
        if group_size > 2:
            group_multiplier = 1 + (group_size - 1) * 0.7  # 非线性缩放
        else:
            group_multiplier = group_size

        return daily_transport_cost * group_multiplier * total_days

    def _calculate_miscellaneous_cost(self, total_days: int, group_size: int, budget_range: str) -> float:
        """
        计算杂项费用（购物、小费、紧急情况）

        这个方法负责计算各种杂项费用，包括：
        1. 购物和纪念品费用
        2. 小费和服务费
        3. 紧急备用金

        参数：
        - total_days: 总天数
        - group_size: 团队人数
        - budget_range: 预算范围

        返回：总杂项费用（人民币）
        """
        daily_misc_cost = self.miscellaneous_costs.get(budget_range, 280)
        return daily_misc_cost * group_size * total_days
    
    def _filter_hotels_by_budget(self, hotels: List[Hotel], budget_range: str) -> List[Hotel]:
        """Filter hotels based on budget range"""
        budget_ranges = {
            'budget': (0, 80),
            'mid-range': (80, 200),
            'luxury': (200, 1000)
        }
        
        min_price, max_price = budget_ranges.get(budget_range, (80, 200))
        
        suitable_hotels = [h for h in hotels if min_price <= h.price_per_night <= max_price]
        return suitable_hotels if suitable_hotels else hotels
    
    def _create_detailed_breakdown(self, hotels: List[Hotel], attractions: List[Attraction], 
                                 restaurants: List[Attraction], activities: List[Attraction], 
                                 trip_details: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed expense breakdown"""
        breakdown = {
            'accommodation': {
                'recommended_hotel': hotels[0].name if hotels else 'Standard Hotel',
                'price_per_night': hotels[0].price_per_night if hotels else 100,
                'total_nights': trip_details['total_days'],
                'total_cost': hotels[0].calculate_total_cost(trip_details['total_days']) if hotels else 100 * trip_details['total_days']
            },
            
            'dining': [
                {
                    'name': r.name,
                    'type': 'restaurant',
                    'estimated_cost': r.estimated_cost,
                    'rating': r.rating
                } for r in restaurants[:5]
            ],
            
            'attractions': [
                {
                    'name': a.name,
                    'type': a.type,
                    'estimated_cost': a.estimated_cost,
                    'duration': a.duration,
                    'rating': a.rating
                } for a in attractions[:8]
            ],
            
            'activities': [
                {
                    'name': a.name,
                    'type': a.type,
                    'estimated_cost': a.estimated_cost,
                    'duration': a.duration,
                    'rating': a.rating
                } for a in activities[:6]
            ],
            
            'transportation': {
                'daily_estimate': self.transportation_costs.get(trip_details.get('budget_range', 'mid-range'), 35),
                'total_days': trip_details['total_days'],
                'group_size': trip_details['group_size'],
                'description': self._get_transportation_description(trip_details.get('budget_range', 'mid-range'))
            },
            
            'miscellaneous': {
                'daily_estimate': self.miscellaneous_costs.get(trip_details.get('budget_range', 'mid-range'), 40),
                'total_days': trip_details['total_days'],
                'group_size': trip_details['group_size'],
                'includes': ['Shopping', 'Tips', 'Souvenirs', 'Emergency fund', 'Incidentals']
            }
        }
        
        return breakdown
    
    def _calculate_cost_percentages(self, accommodation: float, food: float, activities: float, 
                                  transportation: float, miscellaneous: float, total: float) -> Dict[str, float]:
        """Calculate percentage breakdown of costs"""
        if total == 0:
            return {}
        
        return {
            'accommodation': round((accommodation / total) * 100, 1),
            'food': round((food / total) * 100, 1),
            'activities': round((activities / total) * 100, 1),
            'transportation': round((transportation / total) * 100, 1),
            'miscellaneous': round((miscellaneous / total) * 100, 1)
        }
    
    def _get_transportation_description(self, budget_range: str) -> str:
        """Get transportation description based on budget"""
        descriptions = {
            'budget': 'Public transport, walking, occasional taxi',
            'mid-range': 'Mix of public transport, taxis, and ride-sharing',
            'luxury': 'Private transport, taxis, premium services'
        }
        return descriptions.get(budget_range, 'Mixed transportation options')
    
    def calculate_budget_comparison(self, base_expenses: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """Compare costs across different budget ranges"""
        base_total = base_expenses['total_cost']
        base_budget = base_expenses['budget_range']
        
        comparison = {}
        
        for budget_range in ['budget', 'mid-range', 'luxury']:
            if budget_range == base_budget:
                comparison[budget_range] = {
                    'total_cost': base_total,
                    'daily_budget': base_expenses['daily_budget'],
                    'difference': 0,
                    'percentage_change': 0
                }
            else:
                multiplier = self.budget_multipliers[budget_range] / self.budget_multipliers[base_budget]
                adjusted_total = base_total * multiplier
                
                comparison[budget_range] = {
                    'total_cost': round(adjusted_total, 2),
                    'daily_budget': round(adjusted_total / base_expenses['trip_duration'], 2),
                    'difference': round(adjusted_total - base_total, 2),
                    'percentage_change': round(((adjusted_total - base_total) / base_total) * 100, 1)
                }
        
        return comparison
    
    def get_cost_saving_tips(self, expenses: Dict[str, Any]) -> List[str]:
        """
        根据费用分解生成省钱贴士

        这个方法分析用户的费用结构，针对不同的费用类别
        提供个性化的省钱建议和优化策略。

        参数：
        - expenses: 包含费用分解和预算信息的字典

        返回：省钱贴士字符串列表

        适用于大模型技术初级用户：
        这个方法展示了如何根据数据分析结果
        生成个性化的建议和推荐。
        """
        tips = []
        budget_range = expenses.get('budget_range', '中等预算')
        percentages = expenses.get('cost_percentages', {})

        # 住宿费用优化建议
        if percentages.get('accommodation', 0) > 40:
            tips.append("考虑入住经济型酒店或民宿以降低住宿成本")
            tips.append("选择市中心外围的酒店可获得更优惠的价格")

        # 餐饮费用优化建议
        if percentages.get('food', 0) > 35:
            tips.append("尝试当地街头美食和市场，既正宗又经济实惠")
            tips.append("选择包含早餐的酒店可节省餐饮费用")

        # 活动费用优化建议
        if percentages.get('activities', 0) > 30:
            tips.append("寻找免费的徒步游览和公共景点")
            tips.append("查看活动和景点的团体折扣优惠")

        # 交通费用优化建议
        if percentages.get('transportation', 0) > 20:
            tips.append("尽可能使用公共交通而非出租车")
            tips.append("考虑购买多日城市交通通票")

        # 基于预算范围的通用建议
        if budget_range != '经济型':
            tips.append("选择淡季出行可获得更优惠的价格")
            tips.append("提前预订住宿和活动可享受早鸟折扣")

        tips.append("预留10-15%的预算用于意外支出")
        tips.append("使用旅行应用寻找优惠并比较价格")

        return tips