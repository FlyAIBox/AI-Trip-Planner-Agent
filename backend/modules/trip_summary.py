import json
from typing import Dict, Any, List
from datetime import datetime
from ..data.models import TripSummary, DayPlan, Hotel, Weather

class TripSummaryGenerator:
    """
    旅行总结生成器类

    这个类负责生成完整的旅行计划总结，包括：
    - 行程概览：基本的旅行信息和预算
    - 天气总结：目的地天气预报和打包建议
    - 住宿总结：推荐酒店和价格对比
    - 费用总结：详细的预算分解和省钱建议
    - 行程亮点：必游景点、推荐餐厅和活动
    - 个性化建议：基于天气和活动的打包和旅行建议
    - 旅行贴士：实用的旅行经验和安全提醒

    适用于大模型技术初级用户：
    这个类使用了面向对象编程的设计模式，将复杂的旅行总结生成过程
    分解为多个小的、专门的方法，每个方法负责生成总结的一个特定部分。
    """

    def __init__(self):
        """
        初始化旅行总结生成器

        创建一个包含所有总结部分的模板字典，用于组织生成的内容
        """
        # 总结模板：定义了旅行总结包含的所有主要部分
        self.summary_template = {
            'trip_overview': {},          # 行程概览
            'weather_summary': {},        # 天气总结
            'accommodation_summary': {},  # 住宿总结
            'expense_summary': {},        # 费用总结
            'itinerary_highlights': {},   # 行程亮点
            'recommendations': {},        # 个性化建议
            'travel_tips': {}            # 旅行贴士
        }
    
    def generate_summary(self, trip_details: Dict[str, Any], weather_data: List[Weather],
                        hotels: List[Hotel], expense_breakdown: Dict[str, Any],
                        itinerary: List[DayPlan]) -> TripSummary:
        """
        生成完整的旅行总结

        这是主要的方法，它整合所有旅行相关的数据，生成一个完整的旅行总结对象。

        参数说明：
        - trip_details: 包含旅行基本信息的字典（目的地、日期、天数等）
        - weather_data: 天气预报数据列表
        - hotels: 推荐酒店列表
        - expense_breakdown: 费用分解详情
        - itinerary: 每日行程计划列表

        返回值：
        - TripSummary对象：包含所有旅行总结信息的完整对象

        工作流程：
        1. 创建基础的TripSummary对象
        2. 调用各个专门的方法生成不同部分的总结
        3. 将所有部分整合到最终的总结对象中
        """

        # 第一步：创建基础的TripSummary对象，包含核心旅行信息
        summary = TripSummary(
            destination=trip_details['destination'],                    # 目的地
            start_date=trip_details['start_date'],                     # 开始日期
            end_date=trip_details['end_date'],                         # 结束日期
            total_days=trip_details['total_days'],                     # 总天数
            total_cost=expense_breakdown.get('total_cost', 0),         # 总费用
            daily_budget=expense_breakdown.get('daily_budget', 0),     # 每日预算
            currency=expense_breakdown.get('target_currency', 'CNY'),   # 货币单位（改为人民币）
            converted_total=expense_breakdown.get('converted_total', expense_breakdown.get('total_cost', 0)),
            itinerary=itinerary,                                       # 行程安排
            hotels=hotels[:3]  # 取前3个最佳酒店推荐
        )

        # 第二步：生成各个专门部分的详细总结
        summary.trip_overview = self._generate_trip_overview(trip_details, expense_breakdown)
        summary.weather_summary = self._generate_weather_summary(weather_data)
        summary.accommodation_summary = self._generate_accommodation_summary(hotels, trip_details)
        summary.expense_summary = self._generate_expense_summary(expense_breakdown)
        summary.itinerary_highlights = self._generate_itinerary_highlights(itinerary)
        summary.recommendations = self._generate_recommendations(trip_details, weather_data, itinerary)
        summary.travel_tips = self._generate_travel_tips(trip_details, weather_data)

        return summary
    
    def _generate_trip_overview(self, trip_details: Dict[str, Any], expense_breakdown: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成旅行概览部分

        这个方法创建旅行的基本概览信息，包括目的地、时间、预算等核心信息。
        还会根据旅行天数自动分类旅行类型（周末游、短途旅行等）。

        参数：
        - trip_details: 旅行详情字典
        - expense_breakdown: 费用分解字典

        返回：包含旅行概览信息的字典
        """

        # 构建基础概览信息
        overview = {
            'destination': trip_details['destination'],                                    # 目的地
            'duration': f"{trip_details['total_days']} 天",                              # 旅行时长
            'travel_dates': f"{trip_details['start_date']} 至 {trip_details['end_date']}", # 旅行日期
            'group_size': trip_details.get('group_size', 1),                             # 团队人数
            'budget_category': trip_details.get('budget_range', '中等预算').title(),        # 预算类别
            'total_budget': expense_breakdown.get('converted_total', 0),                  # 总预算
            'currency': expense_breakdown.get('target_currency', 'CNY'),                  # 货币单位（人民币）
            'cost_per_person': expense_breakdown.get('cost_per_person', 0),              # 人均费用
            'daily_budget': expense_breakdown.get('daily_budget', 0),                    # 每日预算
            'interests': trip_details.get('preferences', {}).get('interests', []),       # 兴趣爱好
            'planning_date': datetime.now().strftime('%Y-%m-%d')                         # 计划制定日期
        }

        # 根据旅行天数自动分类旅行类型
        # 这个分类帮助用户快速了解旅行的性质和规模
        duration = trip_details['total_days']
        if duration <= 3:
            overview['trip_type'] = '周末短途游'      # 1-3天：适合周末放松
        elif duration <= 7:
            overview['trip_type'] = '短期度假'        # 4-7天：经典的短期旅行
        elif duration <= 14:
            overview['trip_type'] = '深度旅行'        # 8-14天：可以深入体验目的地
        else:
            overview['trip_type'] = '长期旅行'        # 15天以上：深度探索或慢旅行

        return overview
    
    def _generate_weather_summary(self, weather_data: List[Weather]) -> Dict[str, Any]:
        """
        生成天气总结部分

        分析旅行期间的天气预报数据，提供温度范围、天气条件统计，
        并根据天气情况给出打包建议。

        参数：
        - weather_data: 天气数据列表，包含每日的温度、天气描述等信息

        返回：包含天气总结和打包建议的字典

        功能说明：
        1. 计算温度范围（最低、最高、平均温度）
        2. 统计不同天气条件的天数（雨天、晴天等）
        3. 根据天气情况生成个性化的打包建议
        """

        # 检查是否有天气数据
        if not weather_data:
            return {'status': '天气数据不可用'}

        # 提取所有天气数据中的温度和天气描述
        temperatures = [w.temperature for w in weather_data]
        conditions = [w.description for w in weather_data]

        # 构建天气总结
        summary = {
            'forecast_period': f"{len(weather_data)} 天",                    # 预报天数
            'temperature_range': {                                           # 温度范围
                'min': min(temperatures),                                    # 最低温度
                'max': max(temperatures),                                    # 最高温度
                'average': round(sum(temperatures) / len(temperatures), 1)   # 平均温度
            },
            'conditions': list(set(conditions)),                             # 去重后的天气条件列表
            # 统计特殊天气天数（用于打包建议）
            'rainy_days': len([w for w in weather_data if '雨' in w.description or 'rain' in w.description.lower()]),
            'sunny_days': len([w for w in weather_data if '晴' in w.description or 'sun' in w.description.lower() or 'clear' in w.description.lower()]),
            'daily_forecast': [                                              # 每日详细预报
                {
                    'date': w.date,                                          # 日期
                    'temperature': w.temperature,                            # 温度
                    'condition': w.description,                              # 天气状况
                    'feels_like': w.feels_like                              # 体感温度
                } for w in weather_data
            ]
        }

        # 根据平均温度生成打包建议
        avg_temp = summary['temperature_range']['average']

        weather_recommendations = []
        if avg_temp < 10:
            weather_recommendations.append("携带保暖衣物，包括外套和多层衣物")
        elif avg_temp > 25:
            weather_recommendations.append("携带轻便透气的衣物和防晒用品")
        else:
            weather_recommendations.append("携带适合温和气候的多样化衣物")

        # 如果有雨天，添加防雨建议
        if summary['rainy_days'] > 0:
            weather_recommendations.append("携带防水衣物和雨伞")

        summary['packing_recommendations'] = weather_recommendations

        return summary
    
    def _generate_accommodation_summary(self, hotels: List[Hotel], trip_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成住宿总结部分

        分析推荐的酒店列表，选出最佳推荐并提供价格对比。
        包括首选酒店的详细信息和备选方案。

        参数：
        - hotels: 酒店推荐列表，按评分和性价比排序
        - trip_details: 旅行详情，用于计算总住宿费用

        返回：包含住宿推荐和价格分析的字典

        功能说明：
        1. 选择评分最高的酒店作为首选推荐
        2. 提供3个备选酒店方案
        3. 分析价格范围，帮助用户做出选择
        """

        # 检查是否有酒店推荐数据
        if not hotels:
            return {'status': '暂无酒店推荐'}

        # 选择第一个酒店作为最佳推荐（列表已按评分排序）
        recommended_hotel = hotels[0]
        total_nights = trip_details['total_days']  # 总住宿夜数

        summary = {
            'recommended_hotel': {                                                    # 推荐酒店详情
                'name': recommended_hotel.name,                                       # 酒店名称
                'rating': recommended_hotel.rating,                                   # 评分
                'price_per_night': recommended_hotel.price_per_night,                # 每晚价格
                'total_cost': recommended_hotel.calculate_total_cost(total_nights),  # 总住宿费用
                'address': recommended_hotel.address,                                 # 地址
                'amenities': recommended_hotel.amenities                             # 设施服务
            },
            'alternative_options': [                                                  # 备选酒店方案
                {
                    'name': hotel.name,                                               # 酒店名称
                    'rating': hotel.rating,                                           # 评分
                    'price_per_night': hotel.price_per_night,                        # 每晚价格
                    'total_cost': hotel.calculate_total_cost(total_nights)           # 总费用
                } for hotel in hotels[1:4]  # 取接下来的3个备选方案
            ],
            'total_nights': total_nights,                                             # 总住宿夜数
            'budget_range': {                                                         # 价格范围分析
                'lowest_option': min(h.price_per_night for h in hotels),            # 最便宜选项
                'highest_option': max(h.price_per_night for h in hotels),           # 最贵选项
                'recommended_price': recommended_hotel.price_per_night               # 推荐酒店价格
            }
        }

        return summary
    
    def _generate_expense_summary(self, expense_breakdown: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成费用总结部分

        详细分析旅行的各项费用，包括住宿、餐饮、活动、交通等，
        并提供省钱建议和汇率转换信息。

        参数：
        - expense_breakdown: 费用分解字典，包含各项费用的详细信息

        返回：包含费用分析和省钱建议的字典

        功能说明：
        1. 汇总各项费用并计算百分比分布
        2. 提供实用的省钱建议
        3. 处理货币转换信息（如果适用）
        """

        summary = {
            'total_cost': expense_breakdown.get('converted_total', 0),                    # 总费用
            'currency': expense_breakdown.get('target_currency', 'CNY'),                  # 货币单位（人民币）
            'daily_budget': expense_breakdown.get('daily_budget', 0),                     # 每日预算
            'cost_per_person': expense_breakdown.get('cost_per_person', 0),              # 人均费用
            'budget_category': expense_breakdown.get('budget_range', '中等预算').title(),   # 预算类别

            'cost_breakdown': {                                                           # 费用分解
                'accommodation': expense_breakdown.get('accommodation_cost', 0),          # 住宿费用
                'food_dining': expense_breakdown.get('food_cost', 0),                    # 餐饮费用
                'activities_attractions': expense_breakdown.get('activities_cost', 0),   # 活动景点费用
                'transportation': expense_breakdown.get('transportation_cost', 0),       # 交通费用
                'miscellaneous': expense_breakdown.get('miscellaneous_cost', 0)          # 其他杂费
            },

            'percentage_breakdown': expense_breakdown.get('cost_percentages', {}),        # 费用百分比分布

            # 实用的省钱建议
            'budget_tips': [
                "提前预订住宿和机票可获得更优惠的价格",
                "选择当地餐厅用餐，既正宗又实惠",
                "优先使用公共交通工具",
                "寻找免费的活动和景点",
                "预留10-15%的额外费用应对意外支出"
            ]
        }

        # 如果涉及货币转换，添加汇率信息
        if expense_breakdown.get('base_currency') != expense_breakdown.get('target_currency'):
            summary['currency_conversion'] = {
                'original_currency': expense_breakdown.get('base_currency', 'USD'),       # 原始货币
                'converted_to': expense_breakdown.get('target_currency', 'CNY'),          # 转换后货币
                'exchange_rate': expense_breakdown.get('conversion_rate', 1.0),           # 汇率
                'conversion_date': expense_breakdown.get('converted_date', datetime.now().strftime('%Y-%m-%d'))  # 转换日期
            }

        return summary
    
    def _generate_itinerary_highlights(self, itinerary: List[DayPlan]) -> Dict[str, Any]:
        """
        生成行程亮点部分

        从完整的行程计划中提取最精华的内容，包括必游景点、
        推荐餐厅、热门活动，并提供每日行程概览。

        参数：
        - itinerary: 每日行程计划列表

        返回：包含行程亮点和每日概览的字典

        功能说明：
        1. 收集所有景点、餐厅、活动信息
        2. 按评分排序，选出最值得推荐的项目
        3. 生成每日行程概览，便于快速了解安排
        """

        # 检查是否有行程数据
        if not itinerary:
            return {'status': '暂无行程安排'}

        # 收集所有的景点、餐厅和活动信息
        all_attractions = []    # 所有景点
        all_restaurants = []    # 所有餐厅
        all_activities = []     # 所有活动

        # 遍历每日行程，收集所有项目
        for day in itinerary:
            all_attractions.extend(day.attractions)
            all_restaurants.extend(day.restaurants)
            all_activities.extend(day.activities)

        # 按评分排序，选出最佳推荐
        top_attractions = sorted(all_attractions, key=lambda x: x.rating, reverse=True)[:5]  # 前5个景点
        top_restaurants = sorted(all_restaurants, key=lambda x: x.rating, reverse=True)[:5]  # 前5个餐厅
        top_activities = sorted(all_activities, key=lambda x: x.rating, reverse=True)[:3]    # 前3个活动

        highlights = {
            'total_days_planned': len(itinerary),                                    # 计划总天数
            'must_visit_attractions': [                                              # 必游景点
                {
                    'name': attr.name,                                               # 景点名称
                    'rating': attr.rating,                                           # 评分
                    'estimated_cost': attr.estimated_cost,                          # 预估费用
                    'duration': attr.duration,                                       # 游览时长
                    'description': attr.description                                  # 景点描述
                } for attr in top_attractions
            ],
            'recommended_restaurants': [                                             # 推荐餐厅
                {
                    'name': rest.name,                                               # 餐厅名称
                    'rating': rest.rating,                                           # 评分
                    'estimated_cost': rest.estimated_cost,                          # 预估费用
                    'description': rest.description                                  # 餐厅描述
                } for rest in top_restaurants
            ],
            'top_activities': [                                                      # 热门活动
                {
                    'name': act.name,                                                # 活动名称
                    'rating': act.rating,                                            # 评分
                    'estimated_cost': act.estimated_cost,                           # 预估费用
                    'duration': act.duration,                                        # 活动时长
                    'description': act.description                                   # 活动描述
                } for act in top_activities
            ],
            'daily_overview': [                                                      # 每日概览
                {
                    'day': day.day,                                                  # 第几天
                    'date': day.date,                                                # 日期
                    'weather': day.weather.description,                             # 天气状况
                    'temperature': day.weather.temperature,                         # 温度
                    'planned_activities': len(day.attractions) + len(day.activities), # 计划活动数量
                    'dining_options': len(day.restaurants),                         # 用餐选择数量
                    'estimated_cost': day.daily_cost,                               # 预估每日费用
                    'highlights': [attr.name for attr in day.attractions[:2]] +     # 当日亮点（前2个景点+1个活动）
                                [act.name for act in day.activities[:1]]
                } for day in itinerary
            ]
        }

        return highlights
    
    def _generate_recommendations(self, trip_details: Dict[str, Any], weather_data: List[Weather],
                                itinerary: List[DayPlan]) -> Dict[str, Any]:
        """
        生成个性化建议

        根据天气预报、行程安排和目的地特点，生成个性化的旅行建议，
        包括打包清单、当地贴士、安全建议等。

        参数：
        - trip_details: 旅行详情
        - weather_data: 天气数据
        - itinerary: 行程安排

        返回：包含各类个性化建议的字典

        功能说明：
        1. 根据天气和活动类型生成打包建议
        2. 提供当地文化和实用信息
        3. 给出安全和财务管理建议
        """

        recommendations = {
            'packing_essentials': [],      # 打包必需品
            'local_tips': [],             # 当地贴士
            'safety_advice': [],          # 安全建议
            'cultural_considerations': [], # 文化注意事项
            'money_matters': []           # 财务事项
        }

        # 根据天气和活动生成打包建议
        if weather_data:
            avg_temp = sum(w.temperature for w in weather_data) / len(weather_data)

            if avg_temp < 15:
                recommendations['packing_essentials'].extend([
                    "保暖外套和多层衣物",
                    "舒适的保暖靴子",
                    "手套和保暖配件"
                ])
            elif avg_temp > 25:
                recommendations['packing_essentials'].extend([
                    "轻便透气的衣物",
                    "遮阳帽和太阳镜",
                    "防晒霜和水瓶"
                ])

            # 检查是否有雨天
            rainy_days = len([w for w in weather_data if '雨' in w.description or 'rain' in w.description.lower()])
            if rainy_days > 0:
                recommendations['packing_essentials'].extend([
                    "防水外套或雨伞",
                    "电子设备防水袋"
                ])

        # 根据活动类型添加打包建议
        has_outdoor_activities = any(
            any('户外' in act.description or 'outdoor' in act.description.lower() or
                '公园' in act.name or 'park' in act.name.lower()
                for act in day.activities + day.attractions)
            for day in itinerary
        )

        if has_outdoor_activities:
            recommendations['packing_essentials'].extend([
                "舒适的步行鞋",
                "日用背包",
                "相机或拍照设备"
            ])

        # 当地实用贴士
        recommendations['local_tips'] = [
            f"了解{trip_details['destination']}的当地习俗和礼仪",
            "下载离线地图和翻译应用",
            "学习基本的当地语言短语",
            "保存紧急联系电话",
            "了解当地的小费习惯和支付方式"
        ]

        # 安全建议
        recommendations['safety_advice'] = [
            "将重要文件复印件分开存放",
            "告知他人您的每日行程安排",
            "在人群密集的地方保持警觉",
            "准备一些当地货币现金以备急用",
            "了解当地紧急电话和求助程序"
        ]

        # 财务管理建议
        recommendations['money_matters'] = [
            f"提前通知银行您将前往{trip_details['destination']}旅行",
            "准备一些当地货币用于小额消费",
            "使用大型银行的ATM获得更好的汇率",
            "保留消费收据以便记账",
            "考虑购买旅行保险以应对意外费用"
        ]

        return recommendations
    
    def _generate_travel_tips(self, trip_details: Dict[str, Any], weather_data: List[Weather]) -> List[str]:
        """
        生成通用旅行贴士

        提供实用的旅行经验和建议，帮助旅行者获得更好的旅行体验。
        包括时间管理、安全注意事项、文化尊重等方面的建议。

        参数：
        - trip_details: 旅行详情（用于生成特定建议）
        - weather_data: 天气数据（用于生成天气相关建议）

        返回：旅行贴士列表

        功能说明：
        1. 提供通用的旅行经验分享
        2. 根据天气情况添加特定建议
        3. 涵盖安全、文化、实用性等多个方面
        """

        # 通用旅行贴士列表
        tips = [
            "早上较早到达景点可以避开人群",
            "保持手机电量充足，携带移动电源",
            "长时间步行时要注意补水和休息",
            "尝试当地美食，但肠胃敏感者需谨慎选择街边小食",
            "尊重当地习俗和着装要求，特别是在宗教场所",
            "妥善保管重要文件和贵重物品",
            "拍照留念的同时，也要用心感受当下的美好",
            "保持行程的灵活性，有时最美的体验来自意外发现",
            "与当地人交流，获得最地道的推荐",
            "如果要游览多个景点，考虑购买城市旅游通票"
        ]

        # 根据天气情况添加特定建议
        if weather_data:
            # 计算雨天比例
            rainy_days = len([w for w in weather_data if '雨' in w.description or 'rain' in w.description.lower()])
            if rainy_days > len(weather_data) * 0.3:  # 如果雨天超过30%
                tips.append("为雨天准备室内活动备选方案")

        return tips
    
    def save_to_file(self, summary: TripSummary, filename: str = None) -> str:
        """
        将旅行总结保存到文本文件

        将完整的旅行总结以易读的文本格式保存到文件中，
        方便用户打印或分享。

        参数：
        - summary: 旅行总结对象
        - filename: 可选的文件名，如果不提供会自动生成

        返回：保存的文件名

        功能说明：
        1. 自动生成包含目的地和时间戳的文件名
        2. 将总结内容格式化为易读的文本
        3. 使用UTF-8编码确保中文正确显示
        """

        # 如果没有提供文件名，自动生成一个
        if not filename:
            # 清理目的地名称，移除空格和逗号
            destination = summary.destination.replace(' ', '_').replace(',', '').replace('，', '')
            filename = f"旅行总结_{destination}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        # 格式化总结内容
        content = self._format_summary_for_file(summary)

        try:
            # 使用UTF-8编码保存文件，确保中文正确显示
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return filename
        except Exception as e:
            raise Exception(f"文件保存失败: {e}")
    
    def _format_summary_for_file(self, summary: TripSummary) -> str:
        """
        格式化旅行总结用于文件输出

        将旅行总结对象转换为格式化的文本内容，
        包含所有重要信息并使用中文标题和描述。

        参数：
        - summary: 旅行总结对象

        返回：格式化的文本字符串

        功能说明：
        1. 创建结构化的文本布局
        2. 使用中文标题和描述
        3. 包含所有重要的旅行信息
        """

        output = []
        output.append("="*80)
        output.append("完整旅行计划总结")
        output.append("="*80)
        output.append("")

        # 旅行概览
        output.append("🌍 旅行概览")
        output.append("-"*40)
        output.append(f"目的地: {summary.destination}")
        output.append(f"行程时长: {summary.total_days} 天 ({summary.start_date} 至 {summary.end_date})")
        output.append(f"总预算: {summary.currency} {summary.converted_total:,.2f}")
        output.append(f"每日预算: {summary.currency} {summary.daily_budget:,.2f}")
        output.append("")

        # 天气预报
        if hasattr(summary, 'weather_summary'):
            weather = summary.weather_summary
            output.append("🌤️ 天气预报")
            output.append("-"*40)
            if 'temperature_range' in weather:
                temp_range = weather['temperature_range']
                output.append(f"温度范围: {temp_range['min']}°C 至 {temp_range['max']}°C")
                output.append(f"平均温度: {temp_range['average']}°C")
            output.append(f"预期天气: {', '.join(weather.get('conditions', []))}")
            if weather.get('packing_recommendations'):
                output.append("打包建议:")
                for rec in weather['packing_recommendations']:
                    output.append(f"  • {rec}")
            output.append("")

        # 住宿推荐
        if summary.hotels:
            output.append("🏨 住宿推荐")
            output.append("-"*40)
            hotel = summary.hotels[0]
            output.append(f"推荐酒店: {hotel.name}")
            output.append(f"评分: {hotel.rating}⭐")
            output.append(f"价格: {summary.currency} {hotel.price_per_night:.2f} 每晚")
            output.append(f"总费用: {summary.currency} {hotel.calculate_total_cost(summary.total_days):.2f}")
            output.append(f"地址: {hotel.address}")
            if hotel.amenities:
                output.append(f"设施服务: {', '.join(hotel.amenities[:5])}")
            output.append("")
        
        # 每日行程安排
        if summary.itinerary:
            output.append("📅 每日行程安排")
            output.append("-"*40)
            for day in summary.itinerary:
                output.append(f"第 {day.day} 天 ({day.date})")
                output.append(f"天气: {day.weather.description}, {day.weather.temperature}°C")

                if day.attractions:
                    output.append("  景点游览:")
                    for attr in day.attractions:
                        output.append(f"    • {attr.name} ({attr.rating}⭐)")

                if day.activities:
                    output.append("  活动安排:")
                    for act in day.activities:
                        output.append(f"    • {act.name} ({act.duration}小时)")

                if day.restaurants:
                    output.append("  用餐推荐:")
                    for rest in day.restaurants:
                        output.append(f"    • {rest.name} ({rest.rating}⭐)")

                output.append(f"  预估每日费用: {summary.currency} {day.daily_cost:.2f}")
                output.append("")

        # 旅行贴士
        if hasattr(summary, 'travel_tips'):
            output.append("💡 旅行贴士")
            output.append("-"*40)
            for tip in summary.travel_tips[:10]:  # 显示前10条贴士
                output.append(f"• {tip}")
            output.append("")

        output.append("="*80)
        output.append("祝您旅途愉快! 🎉")
        output.append("由AI旅行助手和费用规划师生成")
        output.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("="*80)

        return "\n".join(output)
    
    def export_to_json(self, summary: TripSummary, filename: str = None) -> str:
        """
        将旅行总结导出为JSON格式

        将旅行总结对象转换为JSON格式并保存到文件，
        便于程序化处理和数据交换。

        参数：
        - summary: 旅行总结对象
        - filename: 可选的文件名，如果不提供会自动生成

        返回：保存的JSON文件名

        功能说明：
        1. 将复杂的对象结构转换为JSON兼容的字典
        2. 处理日期格式转换
        3. 使用UTF-8编码确保中文正确保存
        """

        # 如果没有提供文件名，自动生成一个
        if not filename:
            destination = summary.destination.replace(' ', '_').replace(',', '').replace('，', '')
            filename = f"旅行数据_{destination}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        # 将旅行总结对象转换为字典格式
        summary_dict = {
            'destination': summary.destination,                                                    # 目的地
            'start_date': summary.start_date.isoformat() if hasattr(summary.start_date, 'isoformat') else str(summary.start_date),  # 开始日期
            'end_date': summary.end_date.isoformat() if hasattr(summary.end_date, 'isoformat') else str(summary.end_date),          # 结束日期
            'total_days': summary.total_days,                                                     # 总天数
            'total_cost': summary.total_cost,                                                     # 总费用
            'currency': summary.currency,                                                         # 货币单位
            'hotels': [                                                                           # 酒店信息
                {
                    'name': hotel.name,                                                           # 酒店名称
                    'rating': hotel.rating,                                                       # 评分
                    'price_per_night': hotel.price_per_night,                                    # 每晚价格
                    'address': hotel.address,                                                     # 地址
                    'amenities': hotel.amenities                                                  # 设施服务
                } for hotel in summary.hotels
            ],
            'itinerary': [                                                                        # 行程安排
                {
                    'day': day.day,                                                               # 第几天
                    'date': day.date,                                                             # 日期
                    'weather': {                                                                  # 天气信息
                        'temperature': day.weather.temperature,                                   # 温度
                        'description': day.weather.description,                                   # 天气描述
                        'humidity': day.weather.humidity                                          # 湿度
                    },
                    'attractions': [{'name': a.name, 'rating': a.rating, 'cost': a.estimated_cost} for a in day.attractions],  # 景点
                    'restaurants': [{'name': r.name, 'rating': r.rating, 'cost': r.estimated_cost} for r in day.restaurants],  # 餐厅
                    'activities': [{'name': act.name, 'rating': act.rating, 'cost': act.estimated_cost} for act in day.activities],  # 活动
                    'daily_cost': day.daily_cost                                                  # 每日费用
                } for day in summary.itinerary
            ]
        }

        try:
            # 使用UTF-8编码和ensure_ascii=False确保中文正确保存
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(summary_dict, f, indent=2, ensure_ascii=False)
            return filename
        except Exception as e:
            raise Exception(f"JSON文件保存失败: {e}")

# 旅行总结生成器 - 完成
