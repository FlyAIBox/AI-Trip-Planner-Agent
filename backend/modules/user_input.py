"""
用户输入处理模块

这个模块负责处理和验证用户输入的旅行规划信息，包括：
- 目的地选择和验证
- 日期输入和格式化
- 预算范围和货币选择
- 兴趣爱好和偏好设置
- 特殊要求和额外选项

适用于大模型技术初级用户：
这个模块展示了如何构建一个健壮的用户输入系统，
包括数据验证、错误处理和用户友好的交互界面。
"""

import re
from datetime import datetime, date, timedelta
from typing import Dict, Any, Tuple, List, Optional

class UserInputHandler:
    """
    用户输入处理和验证类

    这个类负责收集和验证用户的旅行规划输入，包括：
    1. 目的地信息收集
    2. 日期范围验证
    3. 预算和货币设置
    4. 个人偏好收集
    5. 输入数据的完整性检查

    适用于大模型技术初级用户：
    这个类展示了如何设计一个用户友好的输入系统，
    包含数据验证、错误处理和智能提示功能。
    """

    def __init__(self):
        """
        初始化用户输入处理器

        设置各种预定义的选项列表，包括支持的货币、
        预算范围、热门目的地和常见兴趣爱好。
        """
        # 支持的货币列表（添加人民币为默认）
        self.valid_currencies = ['CNY', 'USD', 'EUR', 'GBP', 'INR', 'JPY', 'CAD', 'AUD', 'CHF', 'SGD']

        # 预算范围选项
        self.budget_ranges = ['经济型', '中等预算', '豪华型']

        # 热门目的地列表（更新为中国大陆城市为主）
        self.popular_destinations = [
            '北京', '上海', '广州', '深圳', '杭州', '成都', '西安', '南京',
            '苏州', '厦门', '青岛', '大连', '重庆', '天津', '武汉', '长沙',
            '昆明', '桂林', '三亚', '拉萨', '乌鲁木齐', '哈尔滨', '沈阳'
        ]

        # 常见兴趣爱好列表（中文化）
        self.common_interests = [
            '博物馆', '艺术', '历史', '美食', '夜生活', '购物', '自然风光',
            '冒险活动', '文化体验', '建筑', '摄影', '音乐', '体育',
            '海滩', '山景', '节庆活动', '当地体验', '奢华享受'
        ]
    
    def get_trip_details(self) -> Dict[str, Any]:
        """
        从用户收集所有旅行详情并进行全面验证

        这个方法是用户输入的主要入口点，它：
        1. 显示欢迎信息和指导
        2. 逐步收集各种旅行信息
        3. 验证输入的有效性
        4. 返回完整的旅行详情字典

        返回：包含所有旅行信息的字典

        适用于大模型技术初级用户：
        这个方法展示了如何设计一个用户友好的数据收集流程，
        通过分步骤的方式降低用户的认知负担。
        """

        print("🌍 欢迎使用AI旅行助手与费用规划师!")
        print("=" * 60)
        print("让我们规划您的完美旅程！请提供以下详细信息:")
        print("-" * 60)

        # 获取基本旅行信息
        destination = self._get_destination()           # 目的地
        start_date, end_date, total_days = self._get_dates()  # 日期信息
        budget_range = self._get_budget_range()         # 预算范围
        currency = self._get_currency()                 # 货币类型
        group_size = self._get_group_size()            # 团队人数

        # 获取偏好和特殊要求
        preferences = self._get_preferences()           # 个人偏好

        # 获取额外选项
        additional_options = self._get_additional_options()  # 额外选项

        # 构建旅行详情字典
        trip_details = {
            'destination': destination,      # 目的地
            'start_date': start_date,       # 开始日期
            'end_date': end_date,           # 结束日期
            'total_days': total_days,       # 总天数
            'budget_range': budget_range,   # 预算范围
            'currency': currency,           # 货币类型
            'group_size': group_size,
            'preferences': preferences,
            'additional_options': additional_options,
            'input_timestamp': datetime.now()
        }
        
        return trip_details
    
    def _get_destination(self) -> str:
        """
        获取和验证目的地，提供智能建议

        这个方法负责收集用户的目的地信息，包括：
        1. 显示热门目的地建议
        2. 验证输入格式的有效性
        3. 处理不常见目的地的确认
        4. 返回格式化的目的地名称

        返回：验证后的目的地名称
        """
        print("\n📍 目的地选择")
        print("热门目的地推荐:", ", ".join(self.popular_destinations[:10]))

        while True:
            destination = input("\n请输入您的目的地城市: ").strip()

            if not destination:
                print("❌ 请输入目的地。")
                continue

            if len(destination) < 2:
                print("❌ 请输入有效的城市名称（至少2个字符）。")
                continue

            # 检查数字或特殊字符（支持中文）
            if not re.match(r'^[\u4e00-\u9fa5a-zA-Z\s\-\'\.]+$', destination):
                print("❌ 请输入有效的城市名称（仅支持中文、英文字母、空格、连字符和撇号）。")
                continue

            # 正确格式化
            destination = destination.title()

            # 确认不常见的目的地
            if destination not in self.popular_destinations:
                confirm = input(f"您是指'{destination}'吗？(y/n): ").lower().strip()
                if confirm not in ['y', 'yes', '是', '确认']:
                    continue

            return destination
    
    def _get_dates(self) -> Tuple[date, date, int]:
        """
        获取和验证旅行日期，提供智能建议

        这个方法负责收集旅行日期信息，包括：
        1. 获取开始和结束日期
        2. 验证日期格式和逻辑
        3. 提供旅行时长建议
        4. 返回日期和总天数

        返回：开始日期、结束日期和总天数的元组
        """
        print("\n📅 旅行日期")
        print("日期格式: YYYY-MM-DD (例如: 2025-12-25)")

        while True:
            try:
                # 获取开始日期
                start_input = input("\n请输入开始日期: ").strip()
                if not start_input:
                    print("❌ 开始日期是必需的。")
                    continue

                start_date = datetime.strptime(start_input, "%Y-%m-%d").date()

                # 验证开始日期
                if start_date < date.today():
                    print("❌ 开始日期不能是过去的日期。")
                    continue

                if start_date > date.today() + timedelta(days=365):
                    confirm = input("⚠️  这个日期相当遥远。您确定吗？(y/n): ").lower()
                    if confirm not in ['y', 'yes', '是', '确认']:
                        continue

                # 获取结束日期
                end_input = input("请输入结束日期: ").strip()
                if not end_input:
                    print("❌ 结束日期是必需的。")
                    continue

                end_date = datetime.strptime(end_input, "%Y-%m-%d").date()

                # 验证结束日期
                if end_date <= start_date:
                    print("❌ 结束日期必须晚于开始日期。")
                    continue

                total_days = (end_date - start_date).days

                # 验证旅行时长
                if total_days > 90:
                    confirm = input(f"⚠️  这是一个{total_days}天的长途旅行！您确定吗？(y/n): ").lower()
                    if confirm not in ['y', 'yes', '是', '确认']:
                        continue

                # 显示旅行摘要
                print(f"✅ 旅行时长: {total_days}天")

                # 建议最佳时长
                if total_days < 2:
                    print("💡 建议延长至至少2-3天，以获得更充实的旅行体验。")
                elif total_days > 14:
                    print("💡 对于超过2周的旅行，建议考虑规划多个目的地。")

                return start_date, end_date, total_days

            except ValueError:
                print("❌ 请按YYYY-MM-DD格式输入日期（例如：2025-12-25）。")
    
    def _get_budget_range(self) -> str:
        """
        获取预算偏好，提供详细说明

        这个方法帮助用户选择合适的预算范围，包括：
        1. 展示不同预算级别的详细说明
        2. 提供每日费用估算
        3. 验证用户选择
        4. 返回标准化的预算范围

        返回：标准化的预算范围字符串
        """
        print("\n💰 预算范围")
        print("请选择您的预算类别:")
        print("1. 经济型      - 青旅、街边美食、公共交通 (~¥350-560/天)")
        print("2. 中等预算    - 酒店、餐厅、混合交通 (~¥700-1050/天)")
        print("3. 豪华型      - 高端酒店、精致餐饮、私人交通 (~¥1400+/天)")

        while True:
            try:
                choice = input("\n请选择预算范围 (1-3) 或输入名称: ").strip().lower()

                if choice in ['1', '经济型', 'budget', '经济']:
                    print("✅ 已选择经济型旅行 - 适合背包客和注重性价比的旅行者！")
                    return '经济型'
                elif choice in ['2', '中等预算', 'mid-range', 'mid', 'middle', '中等', '中档']:
                    print("✅ 已选择中等预算旅行 - 舒适与价值的完美平衡！")
                    return '中等预算'
                elif choice in ['3', '豪华型', 'luxury', 'premium', 'high-end', '豪华', '奢华']:
                    print("✅ 已选择豪华型旅行 - 体验最优质的住宿和服务！")
                    return '豪华型'
                else:
                    print("❌ 请选择1、2、3或输入'经济型'、'中等预算'、'豪华型'。")

            except KeyboardInterrupt:
                raise
            except:
                print("❌ 请输入有效的选择。")
    
    def _get_currency(self) -> str:
        """
        获取首选货币，提供汇率信息

        这个方法帮助用户选择货币类型，包括：
        1. 显示支持的货币列表
        2. 设置默认货币为人民币
        3. 验证货币代码有效性
        4. 提供汇率转换说明

        返回：标准化的货币代码
        """
        print(f"\n💱 货币选择")
        print("支持的货币:")
        print("CNY (人民币)       USD (美元)         EUR (欧元)")
        print("GBP (英镑)         JPY (日元)         CAD (加拿大元)")
        print("AUD (澳大利亚元)   CHF (瑞士法郎)     SGD (新加坡元)")
        print("INR (印度卢比)")

        while True:
            currency = input("\n请输入您的首选货币 (默认: CNY): ").upper().strip()

            if not currency:
                print("✅ 使用人民币(CNY)作为默认货币。")
                return "CNY"

            if currency in self.valid_currencies:
                print(f"✅ 货币已设置为 {currency}")
                if currency != 'CNY':
                    print("💡 所有费用将首先以人民币计算，然后转换为您选择的货币。")
                return currency
            else:
                print(f"❌ 不支持货币'{currency}'。")
                print(f"支持的货币: {', '.join(self.valid_currencies)}")
    
    def _get_group_size(self) -> int:
        """
        获取旅行者人数，提供团队优惠信息

        这个方法收集团队规模信息，包括：
        1. 验证人数输入的有效性
        2. 提供不同团队规模的建议
        3. 提醒团队优惠和注意事项
        4. 返回验证后的人数

        返回：旅行者总人数
        """
        print("\n👥 团队人数")

        while True:
            try:
                size_input = input("旅行者人数 (包括您自己): ").strip()

                if not size_input:
                    print("❌ 请输入旅行者人数。")
                    continue

                size = int(size_input)

                if size <= 0:
                    print("❌ 团队人数至少为1人。")
                    continue

                if size > 20:
                    confirm = input(f"⚠️  这是一个{size}人的大团队。您确定吗？(y/n): ").lower()
                    if confirm not in ['y', 'yes', '是', '确认']:
                        continue

                # 提供针对不同团队规模的建议
                if size == 1:
                    print("✅ 独自旅行 - 完美的灵活性和自我发现之旅！")
                elif size == 2:
                    print("✅ 双人旅行 - 适合情侣度假或朋友出行！")
                elif size <= 4:
                    print("✅ 小团队 - 非常适合家庭旅行或密友出游！")
                elif size <= 8:
                    print("✅ 中等团队 - 建议预订团体住宿！")
                    print("💡 您可能有资格享受活动和旅游的团体折扣。")
                else:
                    print("✅ 大团队 - 一定要寻找团体价格和批量预订！")
                    print("💡 建议在某些活动中分成小组进行。")

                return size

            except ValueError:
                print("❌ 请输入有效的数字。")
    
    def _get_preferences(self) -> Dict[str, Any]:
        """
        获取详细的用户偏好和要求

        这个方法收集用户的个人偏好，包括：
        1. 兴趣爱好和活动偏好
        2. 饮食限制和特殊需求
        3. 行动能力和无障碍需求
        4. 活动强度和旅行风格

        返回：包含所有偏好信息的字典
        """
        print("\n🎯 旅行偏好")
        print("请分享您的兴趣和要求，帮助我们为您定制个性化的旅行。")

        preferences = {}

        # 兴趣爱好
        print(f"\n兴趣爱好 (用逗号分隔):")
        print(f"示例: {', '.join(self.common_interests[:12])}")
        interests_input = input("您的兴趣爱好 (按回车跳过): ").strip()

        if interests_input:
            interests = [interest.strip() for interest in interests_input.split(',')]
            # 验证并建议修正
            valid_interests = []
            for interest in interests:
                if interest in self.common_interests:
                    valid_interests.append(interest)
                else:
                    # 查找相近匹配
                    suggestions = [ci for ci in self.common_interests if interest in ci or ci in interest]
                    if suggestions:
                        print(f"💡 您是指'{suggestions[0]}'而不是'{interest}'吗？")
                        confirm = input("(y/n): ").lower().strip()
                        if confirm in ['y', 'yes', '是', '确认']:
                            valid_interests.append(suggestions[0])
                        else:
                            valid_interests.append(interest)  # 保留原始输入
                    else:
                        valid_interests.append(interest)  # 保留原始输入

            preferences['interests'] = valid_interests
            print(f"✅ 兴趣爱好已记录: {', '.join(valid_interests)}")
        else:
            preferences['interests'] = []

        # 饮食限制
        dietary = input("\n饮食限制/偏好 (素食、纯素、清真等): ").strip()
        preferences['dietary_restrictions'] = dietary
        if dietary:
            print(f"✅ 饮食偏好已记录: {dietary}")

        # 行动能力考虑
        mobility = input("行动能力考虑或无障碍需求: ").strip()
        preferences['mobility'] = mobility
        if mobility:
            print(f"✅ 无障碍需求已记录: {mobility}")

        # 活动强度
        print("\n首选活动强度:")
        print("1. 轻松 - 最少步行，休闲活动")
        print("2. 适中 - 适量步行，平衡行程")
        print("3. 活跃 - 大量步行，冒险活动")

        while True:
            activity_level = input("选择活动强度 (1-3): ").strip()
            if activity_level in ['1']:
                preferences['activity_level'] = '轻松'
                print("✅ 已选择轻松节奏 - 完美的悠闲假期！")
                break
            elif activity_level in ['2']:
                preferences['activity_level'] = '适中'
                print("✅ 已选择适中节奏 - 活动与休息的良好平衡！")
                break
            elif activity_level in ['3']:
                preferences['activity_level'] = '活跃'
                print("✅ 已选择活跃节奏 - 冒险等着您！")
                break
            else:
                print("❌ 请选择1、2或3。")

        # 旅行风格
        print("\n旅行风格:")
        print("1. 观光客 - 热门景点和体验")
        print("2. 探索者 - 热门和小众景点的混合")
        print("3. 当地人 - 真实的当地体验")

        while True:
            travel_style = input("选择旅行风格 (1-3): ").strip()
            if travel_style in ['1']:
                preferences['travel_style'] = '观光客'
                print("✅ 观光客风格 - 您将看到所有必游景点！")
                break
            elif travel_style in ['2']:
                preferences['travel_style'] = '探索者'
                print("✅ 探索者风格 - 著名景点和小众景点的完美结合！")
                break
            elif travel_style in ['3']:
                preferences['travel_style'] = '当地人'
                print("✅ 当地人风格 - 真实的文化沉浸体验！")
                break
            else:
                print("❌ 请选择1、2或3。")

        return preferences
    
    def _get_additional_options(self) -> Dict[str, Any]:
        """
        获取额外选项和特殊要求

        这个方法收集用户的额外偏好和特殊要求，包括：
        1. 交通偏好设置
        2. 住宿类型偏好
        3. 特殊场合说明
        4. 其他特殊要求

        返回：包含所有额外选项的字典

        适用于大模型技术初级用户：
        这个方法展示了如何收集可选的用户偏好，
        为个性化服务提供更多定制选项。
        """
        print("\n⚙️  额外选项")
        options = {}

        # 交通偏好
        print("交通偏好:")
        print("1. 偏好公共交通")
        print("2. 混合交通方式")
        print("3. 偏好私人交通")

        while True:
            transport = input("选择偏好 (1-3，或按回车使用默认): ").strip()
            if not transport or transport == '2':
                options['transport_preference'] = '混合'
                break
            elif transport == '1':
                options['transport_preference'] = '公共交通'
                print("✅ 偏好公共交通 - 环保且经济实惠！")
                break
            elif transport == '3':
                options['transport_preference'] = '私人交通'
                print("✅ 偏好私人交通 - 舒适便捷！")
                break
            else:
                print("❌ 请选择1、2或3。")

        # 住宿偏好
        accommodation_prefs = input("\n住宿偏好 (酒店、青旅、民宿等): ").strip()
        options['accommodation_preference'] = accommodation_prefs

        # 特殊场合
        special_occasion = input("特殊场合 (周年纪念、生日、蜜月等): ").strip()
        options['special_occasion'] = special_occasion
        if special_occasion:
            print(f"✅ 特殊场合已记录: {special_occasion} - 我们会让它难忘！")

        # 额外要求
        additional_requests = input("其他特殊要求或需求: ").strip()
        options['additional_requests'] = additional_requests

        return options
    
    def confirm_details(self, details: Dict[str, Any]) -> bool:
        """
        显示完整的旅行摘要并确认详情

        这个方法展示用户输入的所有信息的综合摘要，
        让用户确认或修改详情。

        参数：
        - details: 包含所有旅行详情的字典

        返回：用户确认结果（True/False）

        适用于大模型技术初级用户：
        这个方法展示了如何创建用户友好的确认界面，
        提供清晰的信息展示和修改选项。
        """
        print("\n" + "="*70)
        print("📋 完整旅行摘要")
        print("="*70)

        # 基本信息
        print(f"🌍 目的地: {details['destination']}")
        print(f"📅 旅行日期: {details['start_date']} 至 {details['end_date']}")
        print(f"⏰ 时长: {details['total_days']} 天")
        print(f"👥 团队人数: {details['group_size']} 位旅行者")
        print(f"💰 预算范围: {details['budget_range']}")
        print(f"💱 货币: {details['currency']}")

        # 偏好设置
        preferences = details.get('preferences', {})
        if preferences.get('interests'):
            print(f"🎯 兴趣爱好: {', '.join(preferences['interests'])}")

        if preferences.get('activity_level'):
            print(f"🚶 活动强度: {preferences['activity_level']}")

        if preferences.get('travel_style'):
            print(f"✈️  旅行风格: {preferences['travel_style']}")

        if preferences.get('dietary_restrictions'):
            print(f"🍽️  饮食要求: {preferences['dietary_restrictions']}")

        # 额外选项
        additional = details.get('additional_options', {})
        if additional.get('transport_preference'):
            print(f"🚌 交通偏好: {additional['transport_preference']}")

        if additional.get('special_occasion'):
            print(f"🎉 特殊场合: {additional['special_occasion']}")

        print("="*70)

        # 费用预估预览
        self._show_cost_preview(details)

        print("\n" + "="*70)

        while True:
            print("\n选项:")
            print("1. 确认并继续")
            print("2. 编辑详情")
            print("3. 取消")

            choice = input("请选择 (1-3): ").strip()

            if choice == '1':
                print("✅ 详情已确认！让我们规划您的精彩旅程...")
                return True
            elif choice == '2':
                return self._edit_details(details)
            elif choice == '3':
                confirm_cancel = input("您确定要取消吗？(y/n): ").lower().strip()
                if confirm_cancel in ['y', 'yes', '是', '确认']:
                    print("❌ 旅行规划已取消。")
                    return False
            else:
                print("❌ 请选择1、2或3。")
    
    def _show_cost_preview(self, details: Dict[str, Any]) -> None:
        """
        根据输入显示估算费用预览

        这个方法基于用户的预算选择和旅行参数，
        提供初步的费用估算预览。

        参数：
        - details: 包含旅行详情的字典

        适用于大模型技术初级用户：
        这个方法展示了如何基于用户输入
        进行简单的费用估算和预览。
        """
        budget_range = details['budget_range']
        days = details['total_days']
        group_size = details['group_size']

        # 每人每日粗略估算（人民币）
        daily_estimates = {
            '经济型': 350,
            '中等预算': 700,
            '豪华型': 1400
        }

        daily_cost = daily_estimates.get(budget_range, 700)
        total_per_person = daily_cost * days
        total_for_group = total_per_person * group_size

        print(f"\n💡 粗略费用估算 ({details['currency']})")
        print(f"   每人每日: ~¥{daily_cost}")
        print(f"   每人总计: ~¥{total_per_person:,}")
        print(f"   团队总计: ~¥{total_for_group:,}")
        print("   (这是粗略估算 - 详细费用将在下一步计算)")
    
    def _edit_details(self, details: Dict[str, Any]) -> bool:
        """Allow user to edit specific details"""
        print("\n📝 EDIT TRIP DETAILS")
        print("What would you like to change?")
        print("1. Destination")
        print("2. Dates")
        print("3. Budget range")
        print("4. Currency")
        print("5. Group size")
        print("6. Preferences")
        print("7. Go back to confirmation")
        
        while True:
            choice = input("Select what to edit (1-7): ").strip()
            
            if choice == '1':
                details['destination'] = self._get_destination()
            elif choice == '2':
                start_date, end_date, total_days = self._get_dates()
                details['start_date'] = start_date
                details['end_date'] = end_date
                details['total_days'] = total_days
            elif choice == '3':
                details['budget_range'] = self._get_budget_range()
            elif choice == '4':
                details['currency'] = self._get_currency()
            elif choice == '5':
                details['group_size'] = self._get_group_size()
            elif choice == '6':
                details['preferences'] = self._get_preferences()
            elif choice == '7':
                return self.confirm_details(details)
            else:
                print("❌ Please select 1-7.")
                continue
            
            print("✅ Details updated!")
            
            # Ask if they want to edit more or confirm
            while True:
                next_action = input("Edit more details (e) or confirm (c)? ").lower().strip()
                if next_action in ['e', 'edit']:
                    break
                elif next_action in ['c', 'confirm']:
                    return self.confirm_details(details)
                else:
                    print("❌ Please enter 'e' for edit or 'c' for confirm.")
    
    def get_quick_trip_details(self) -> Dict[str, Any]:
        """Quick mode for experienced users"""
        print("🚀 QUICK TRIP SETUP")
        print("For experienced users - minimal questions!")
        
        destination = input("Destination: ").strip().title()
        start_date = datetime.strptime(input("Start date (YYYY-MM-DD): "), "%Y-%m-%d").date()
        end_date = datetime.strptime(input("End date (YYYY-MM-DD): "), "%Y-%m-%d").date()
        budget_range = input("Budget (budget/mid-range/luxury): ").lower().strip()
        
        if budget_range not in self.budget_ranges:
            budget_range = 'mid-range'
        
        return {
            'destination': destination,
            'start_date': start_date,
            'end_date': end_date,
            'total_days': (end_date - start_date).days,
            'budget_range': budget_range,
            'currency': 'USD',
            'group_size': 1,
            'preferences': {'interests': [], 'activity_level': 'moderate', 'travel_style': 'tourist'},
            'additional_options': {},
            'input_timestamp': datetime.now()
        }
    
    def validate_input_completeness(self, details: Dict[str, Any]) -> List[str]:
        """Validate that all required information is present"""
        issues = []
        
        required_fields = ['destination', 'start_date', 'end_date', 'budget_range', 'currency', 'group_size']
        
        for field in required_fields:
            if field not in details or not details[field]:
                issues.append(f"Missing {field}")
        
        # Date validation
        if 'start_date' in details and 'end_date' in details:
            if details['start_date'] >= details['end_date']:
                issues.append("End date must be after start date")
            
            if details['start_date'] < date.today():
                issues.append("Start date cannot be in the past")
        
        # Budget validation
        if details.get('budget_range') not in self.budget_ranges:
            issues.append("Invalid budget range")
        
        # Currency validation
        if details.get('currency') not in self.valid_currencies:
            issues.append("Invalid currency")
        
        # Group size validation
        if not isinstance(details.get('group_size'), int) or details.get('group_size', 0) <= 0:
            issues.append("Invalid group size")
        
        return issues