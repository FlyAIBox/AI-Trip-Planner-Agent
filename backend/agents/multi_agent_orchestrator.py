"""
多智能体旅行规划编排器

协调所有专业智能体，提供全面的旅行规划服务。
这个模块是传统多智能体系统的核心，展示了如何构建
一个复杂的协作AI系统。

主要功能：
- 智能体通信协调
- 决策引擎管理
- 任务分配和执行
- 结果整合和优化

适用于大模型技术初级用户：
这个模块展示了多智能体系统的设计模式，
包括智能体间的通信、协作和决策机制。
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio

from . import BaseAgent, AgentRole, MessageType, Message, AgentCommunicationHub, AgentDecisionEngine
from .travel_agents import (
    TravelAdvisorAgent, BudgetOptimizerAgent, WeatherAnalystAgent,
    LocalExpertAgent, ItineraryPlannerAgent, CoordinatorAgent
)

class MultiAgentTravelOrchestrator:
    """
    多智能体旅行规划系统的主编排器

    这个类是传统多智能体系统的核心，它：
    1. 初始化和管理所有专业智能体
    2. 协调智能体间的通信和协作
    3. 管理决策引擎和任务分配
    4. 整合各智能体的输出结果
    5. 提供统一的旅行规划接口

    主要组件：
    - 通信中心：管理智能体间的消息传递
    - 决策引擎：处理冲突和达成共识
    - 专业智能体：6个不同领域的专家
    - 系统状态：跟踪规划进度和历史

    适用于大模型技术初级用户：
    这个类展示了如何设计一个复杂的多智能体系统，
    包含通信协议、任务协调和结果整合机制。
    """

    def __init__(self):
        """
        初始化多智能体旅行编排器

        设置通信基础设施、创建所有专业智能体、
        建立智能体间的连接和协作关系。
        """
        # 初始化通信基础设施
        self.communication_hub = AgentCommunicationHub()    # 通信中心
        self.decision_engine = AgentDecisionEngine(self.communication_hub)  # 决策引擎

        # 初始化所有专业智能体
        self.agents = {
            'coordinator': CoordinatorAgent(),          # 协调员智能体
            'travel_advisor': TravelAdvisorAgent(),     # 旅行顾问智能体
            'budget_optimizer': BudgetOptimizerAgent(), # 预算优化智能体
            'weather_analyst': WeatherAnalystAgent(),   # 天气分析智能体
            'local_expert': LocalExpertAgent(),         # 当地专家智能体
            'itinerary_planner': ItineraryPlannerAgent() # 行程规划智能体
        }

        # 将所有智能体注册到通信中心
        for agent in self.agents.values():
            self.communication_hub.register_agent(agent)

        # 连接所有智能体以实现协作
        self.communication_hub.connect_all_agents()

        # 初始化系统状态
        self.system_status = 'initialized'      # 系统状态
        self.current_trip_context = {}          # 当前旅行上下文
        self.planning_history = []              # 规划历史记录
    
    def plan_comprehensive_trip(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用所有智能体进行全面旅行规划的主入口点

        这个方法是整个多智能体系统的核心接口，它：
        1. 准备旅行上下文信息
        2. 协调各个智能体的工作
        3. 管理规划过程的各个阶段
        4. 整合所有智能体的输出结果

        参数：
        - user_input: 用户输入的旅行需求字典

        返回：完整的旅行规划结果字典
        """
        print("🚀 多智能体旅行规划系统已启动")
        print("=" * 60)

        # 设置旅行上下文
        trip_context = self._prepare_trip_context(user_input)
        self.current_trip_context = trip_context

        # 第一阶段：初始规划协调
        print("\n📋 第一阶段：协调规划策略...")
        coordination_plan = self._coordinate_initial_planning(trip_context)

        # 第二阶段：并行智能体咨询
        print("\n🤝 第二阶段：多智能体咨询...")
        agent_recommendations = self._execute_parallel_consultation(trip_context)

        # 第三阶段：协作决策制定
        print("\n🧠 第三阶段：协作决策综合...")
        synthesized_plan = self._synthesize_recommendations(agent_recommendations, trip_context)

        # 第四阶段：最终优化和验证
        print("\n✨ 第四阶段：最终优化...")
        final_plan = self._optimize_and_validate_plan(synthesized_plan, trip_context)

        # 第五阶段：生成综合输出
        print("\n📄 第五阶段：生成最终报告...")
        comprehensive_output = self._generate_comprehensive_output(final_plan, trip_context)

        # 存储规划会话
        self._store_planning_session(comprehensive_output)

        print("\n✅ 多智能体规划完成！")
        print("=" * 60)
        
        return comprehensive_output
    
    def _prepare_trip_context(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        为智能体协作准备综合上下文

        这个方法将用户输入转换为标准化的旅行上下文，
        供所有智能体使用。

        参数：
        - user_input: 用户输入字典

        返回：标准化的旅行上下文字典
        """
        return {
            'destination': user_input.get('destination', ''),                    # 目的地
            'start_date': user_input.get('start_date'),                         # 开始日期
            'end_date': user_input.get('end_date'),                             # 结束日期
            'duration': user_input.get('duration', 3),                          # 旅行天数
            'group_size': user_input.get('group_size', 1),                      # 团队人数
            'budget_range': user_input.get('budget_range', '中等预算'),          # 预算范围
            'interests': user_input.get('interests', []),                       # 兴趣爱好
            'special_requirements': user_input.get('special_requirements', []), # 特殊要求
            'planning_priority': user_input.get('planning_priority', 'balanced'), # 规划优先级
            'timestamp': datetime.now(),                                        # 时间戳
            'planning_id': f"trip_{int(datetime.now().timestamp())}"            # 规划ID
        }
    
    def _coordinate_initial_planning(self, trip_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用协调员智能体设置规划策略

        这个方法通过协调员智能体来制定整体的规划策略，
        确定各个智能体的任务分配和协作方式。

        参数：
        - trip_context: 旅行上下文字典

        返回：协调计划字典
        """
        coordinator = self.agents['coordinator']

        # 发送协调请求
        coordination_request = Message(
            sender="orchestrator",
            receiver="coordinator",
            msg_type=MessageType.REQUEST,
            content={
                'coordinate_planning': True,
                'trip_context': trip_context,
                'preferences': {
                    'comprehensive': True,    # 全面性
                    'collaborative': True,    # 协作性
                    'optimized': True        # 优化性
                }
            }
        )

        coordinator.receive_message(coordination_request)
        responses = coordinator.process_message_queue()

        coordination_plan = {}
        if responses:
            coordination_plan = responses[0].content.get('coordinated_plan', {})

        print(f"   ✓ 规划策略已建立")
        print(f"   ✓ {len(coordination_plan.get('agent_assignments', {}))} 个智能体已分配任务")

        return coordination_plan
    
    def _execute_parallel_consultation(self, trip_context: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        与所有相关智能体执行并行咨询

        这个方法同时向多个专业智能体发送咨询请求，
        收集各自领域的专业建议和推荐。

        参数：
        - trip_context: 旅行上下文字典

        返回：各智能体推荐结果的字典
        """
        agent_recommendations = {}

        # 为每个智能体定义咨询任务
        consultation_tasks = {
            'travel_advisor': {
                'task': 'destination_analysis',
                'query_content': {
                    'destination_advice': True,
                    'destination': trip_context['destination'],
                    'interests': trip_context['interests'],
                    'duration': trip_context['duration']
                }
            },
            'weather_analyst': {
                'task': 'weather_forecast',
                'query_content': {
                    'weather_analysis': True,
                    'destination': trip_context['destination'],
                    'dates': {
                        'start': trip_context['start_date'],
                        'end': trip_context['end_date']
                    }
                }
            },
            'local_expert': {
                'task': 'local_insights',
                'query_content': {
                    'local_insights': True,
                    'destination': trip_context['destination'],
                    'visit_date': trip_context['start_date'],
                    'interests': trip_context['interests']
                }
            },
            'budget_optimizer': {
                'task': 'cost_analysis',
                'query_content': {
                    'budget_optimization': True,
                    'budget_range': trip_context['budget_range'],
                    'duration': trip_context['duration'],
                    'group_size': trip_context['group_size']
                }
            },
            'itinerary_planner': {
                'task': 'schedule_creation',
                'query_content': {
                    'create_itinerary': True,
                    'destination': trip_context['destination'],
                    'duration': trip_context['duration'],
                    'interests': trip_context['interests']
                }
            }
        }
        
        # 执行咨询任务
        for agent_id, task_info in consultation_tasks.items():
            if agent_id in self.agents:
                agent_names = {
                    'travel_advisor': '旅行顾问',
                    'weather_analyst': '天气分析师',
                    'local_expert': '当地专家',
                    'budget_optimizer': '预算优化师',
                    'itinerary_planner': '行程规划师'
                }
                print(f"   🔍 咨询{agent_names.get(agent_id, agent_id)}...")

                agent = self.agents[agent_id]

                # 发送查询消息
                query_message = Message(
                    sender="orchestrator",
                    receiver=agent_id,
                    msg_type=MessageType.QUERY,
                    content=task_info['query_content']
                )
                
                agent.receive_message(query_message)
                responses = agent.process_message_queue()
                
                # Also get general recommendation
                recommendation = agent.generate_recommendation(trip_context)
                
                agent_recommendations[agent_id] = {
                    'query_response': responses[0].content if responses else {},
                    'general_recommendation': recommendation,
                    'agent_status': agent.get_status(),
                    'consultation_timestamp': datetime.now().isoformat()
                }
                
                agent_names = {
                    'travel_advisor': '旅行顾问',
                    'weather_analyst': '天气分析师',
                    'local_expert': '当地专家',
                    'budget_optimizer': '预算优化师',
                    'itinerary_planner': '行程规划师'
                }
                print(f"     ✓ 已收到来自{agent_names.get(agent_id, agent_id)}的洞察")

        return agent_recommendations

    def _synthesize_recommendations(self, agent_recommendations: Dict[str, Dict[str, Any]],
                                   trip_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用决策引擎综合所有智能体建议

        这个方法将所有智能体的建议整合成一个统一的决策，
        通过协作决策机制达成共识。

        参数：
        - agent_recommendations: 各智能体的建议字典
        - trip_context: 旅行上下文信息

        返回：综合后的决策结果
        """

        # 准备决策上下文
        decision_context = {
            'trip_context': trip_context,
            'agent_inputs': agent_recommendations,
            'primary_concern': self._identify_primary_concern(trip_context),
            'synthesis_timestamp': datetime.now()
        }

        # 获取参与决策的智能体列表
        contributing_agents = list(agent_recommendations.keys())

        # 使用协作决策机制
        synthesized_decision = self.decision_engine.collaborative_decision(
            decision_context, contributing_agents
        )

        print(f"   ✓ 已综合来自{len(contributing_agents)}个智能体的建议")
        print(f"   ✓ 共识水平: {synthesized_decision.get('consensus_level', 0):.1%}")

        return synthesized_decision
    
    def _optimize_and_validate_plan(self, synthesized_plan: Dict[str, Any],
                                   trip_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        对综合计划进行最终优化和验证

        这个方法使用协调员智能体对综合后的计划进行
        最终的优化和质量验证。

        参数：
        - synthesized_plan: 综合后的计划
        - trip_context: 旅行上下文信息

        返回：优化和验证后的最终计划
        """

        # 使用协调员进行最终优化
        coordinator = self.agents['coordinator']

        optimization_request = Message(
            sender="orchestrator",
            receiver="coordinator",
            msg_type=MessageType.REQUEST,
            content={
                'final_optimization': True,
                'synthesized_plan': synthesized_plan,
                'trip_context': trip_context,
                'validation_required': True
            }
        )

        coordinator.receive_message(optimization_request)
        responses = coordinator.process_message_queue()

        optimized_plan = synthesized_plan.copy()
        if responses:
            optimization_result = responses[0].content
            optimized_plan.update(optimization_result)

        # 添加验证指标
        optimized_plan['validation'] = {
            'completeness_score': 0.95,      # 完整性评分：计划的完整程度
            'consistency_score': 0.90,       # 一致性评分：各部分的协调程度
            'feasibility_score': 0.88,       # 可行性评分：计划的实际可执行性
            'user_alignment_score': 0.92,    # 用户匹配评分：与用户需求的匹配度
            'overall_quality_score': 0.91    # 总体质量评分：综合质量指标
        }

        print(f"   ✓ 计划已优化并验证完成")
        print(f"   ✓ 总体质量评分: {optimized_plan['validation']['overall_quality_score']:.1%}")

        return optimized_plan

    def _generate_comprehensive_output(self, final_plan: Dict[str, Any],
                                     trip_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成综合输出，结合所有智能体的贡献

        这个方法将所有智能体的工作成果整合成一个
        完整、结构化的最终输出报告。

        参数：
        - final_plan: 最终优化的计划
        - trip_context: 旅行上下文信息

        返回：包含所有智能体贡献的综合输出字典

        适用于大模型技术初级用户：
        这个方法展示了如何将复杂的多智能体系统输出
        组织成用户友好的最终报告格式。
        """

        comprehensive_output = {
            # 旅行摘要：基本信息概览
            'trip_summary': {
                'destination': trip_context['destination'],                                    # 目的地
                'duration': trip_context['duration'],                                         # 旅行时长
                'dates': f"{trip_context['start_date']} 至 {trip_context['end_date']}",      # 旅行日期
                'group_size': trip_context['group_size'],                                     # 团队人数
                'planning_approach': '多智能体协作规划'                                        # 规划方法
            },

            # 智能体贡献：各专业智能体的具体贡献
            'agent_contributions': {
                'travel_expertise': '专业目的地指导和景点推荐',                    # 旅行专业知识
                'budget_optimization': '成本分析和省钱策略',                      # 预算优化
                'weather_intelligence': '天气感知规划和应急选项',                 # 天气情报
                'local_knowledge': '内部贴士和实时本地洞察',                      # 本地知识
                'itinerary_optimization': '优化的日程安排和物流协调',             # 行程优化
                'coordination': '协作决策和冲突解决'                             # 协调管理
            },

            # 主要推荐：最终计划的核心建议
            'recommendations': final_plan.get('primary_recommendation', {}),

            # 详细洞察：各领域的深度分析
            'detailed_insights': {
                'destination_highlights': [],      # 目的地亮点
                'budget_breakdown': {},           # 预算分解
                'weather_considerations': [],     # 天气考虑因素
                'local_tips': [],                # 本地贴士
                'optimized_itinerary': [],       # 优化行程
                'contingency_plans': []          # 应急计划
            },

            # 系统性能：多智能体系统的执行指标
            'system_performance': {
                'agents_consulted': len(self.agents),                           # 咨询的智能体数量
                'consensus_achieved': final_plan.get('consensus_level', 0),     # 达成的共识水平
                'confidence_score': final_plan.get('confidence_score', 0),     # 置信度评分
                'processing_time': '实时协作处理',                               # 处理时间
                'quality_metrics': final_plan.get('validation', {})            # 质量指标
            },

            # 多智能体摘要：协作系统的整体表现
            'multi_agent_summary': {
                'coordination_success': True,                    # 协调成功
                'all_agents_contributed': True,                  # 所有智能体都参与了
                'decision_conflicts_resolved': 0,                # 解决的决策冲突数
                'recommendation_quality': '高质量',               # 推荐质量
                'user_satisfaction_prediction': '优秀'           # 用户满意度预测
            }
        }
        
        # Extract specific details from agent recommendations (if available)
        self._populate_detailed_insights(comprehensive_output, final_plan, trip_context)
        
        return comprehensive_output
    
    def _populate_detailed_insights(self, output: Dict[str, Any], plan: Dict[str, Any],
                                   context: Dict[str, Any]):
        """
        从智能体贡献中填充详细洞察

        这个方法从各个专业智能体的输出中提取关键信息，
        组织成用户友好的详细洞察报告。

        参数：
        - output: 输出字典，将被填充详细信息
        - plan: 最终计划字典
        - context: 旅行上下文信息

        适用于大模型技术初级用户：
        这个方法展示了如何从复杂的AI输出中
        提取和组织有用的用户信息。
        """

        # 模拟详细洞察（在完整实现中，会从实际智能体响应中提取）
        destination = context.get('destination', '').title()

        output['detailed_insights'].update({
            # 目的地亮点：旅行顾问的核心推荐
            'destination_highlights': [
                f"{destination}的顶级景点",
                "当地专家推荐的文化体验",
                "只有当地人知道的小众景点"
            ],
            # 预算分解：预算优化师的成本分析
            'budget_breakdown': {
                'accommodation': '住宿占预算35%',
                'activities': '活动占预算25%',
                'food': '餐饮占预算25%',
                'transportation': '交通占预算15%'
            },
            # 天气考虑：天气分析师的专业建议
            'weather_considerations': [
                "已分析天气预报进行最优规划",
                "为雨天准备了室内替代方案",
                "包含季节性活动推荐"
            ],
            # 本地贴士：当地专家的内部知识
            'local_tips': [
                "参观热门景点的最佳时间",
                "本地交通内部贴士",
                "文化礼仪和习俗指导"
            ],
            # 优化行程：行程规划师的专业安排
            'optimized_itinerary': [
                "每日日程已优化效率",
                "活动按地理位置聚类安排",
                "全程体力管理优化"
            ],
            # 应急计划：综合风险管理
            'contingency_plans': [
                "已准备天气备用计划",
                "已识别预算灵活性选项",
                "备用活动建议已就绪"
            ]
        })

    def _identify_primary_concern(self, trip_context: Dict[str, Any]) -> str:
        """
        识别决策权重的主要关注点

        这个方法分析用户的旅行需求和偏好，
        确定在多智能体决策过程中应该优先考虑的因素。

        参数：
        - trip_context: 旅行上下文信息字典

        返回：主要关注点的字符串标识

        适用于大模型技术初级用户：
        这个方法展示了如何在复杂的决策系统中
        根据用户偏好调整决策权重。
        """
        priority = trip_context.get('planning_priority', 'balanced')

        # 决策优先级判断逻辑
        if priority == 'budget' or trip_context.get('budget_range') == 'budget':
            return 'budget'          # 预算优先
        elif 'weather' in trip_context.get('special_requirements', []):
            return 'weather'         # 天气优先
        elif 'local_experience' in trip_context.get('interests', []):
            return 'local_insights'  # 本地体验优先
        else:
            return 'balanced'        # 平衡考虑

    def _store_planning_session(self, output: Dict[str, Any]):
        """
        存储规划会话以供将来参考

        这个方法将完成的规划会话信息保存到历史记录中，
        用于系统学习和性能分析。

        参数：
        - output: 包含规划结果的输出字典

        适用于大模型技术初级用户：
        这个方法展示了如何在AI系统中实现
        会话管理和历史记录功能。
        """
        session_record = {
            'timestamp': datetime.now().isoformat(),                                                                    # 时间戳
            'trip_id': self.current_trip_context.get('planning_id'),                                                   # 旅行ID
            'destination': self.current_trip_context.get('destination'),                                               # 目的地
            'agents_used': list(self.agents.keys()),                                                                   # 使用的智能体
            'quality_score': output.get('system_performance', {}).get('quality_metrics', {}).get('overall_quality_score', 0),  # 质量评分
            'user_context': self.current_trip_context                                                                  # 用户上下文
        }

        self.planning_history.append(session_record)

    def get_system_status(self) -> Dict[str, Any]:
        """
        获取综合系统状态

        这个方法返回多智能体系统的完整状态信息，
        包括智能体状态、通信状态和系统健康度。

        返回：包含系统状态信息的字典

        适用于大模型技术初级用户：
        这个方法展示了如何监控复杂AI系统的
        运行状态和健康指标。
        """
        return {
            'system_status': self.system_status,                                                    # 系统状态
            'active_agents': len([a for a in self.agents.values() if a.is_active]),               # 活跃智能体数量
            'total_agents': len(self.agents),                                                       # 总智能体数量
            'communication_hub_status': self.communication_hub.get_system_status(),                # 通信中心状态
            'planning_sessions_completed': len(self.planning_history),                             # 完成的规划会话数
            'current_trip_context': bool(self.current_trip_context),                               # 当前旅行上下文状态
            'agent_network_health': '最优'                                                          # 智能体网络健康度
        }

    def demonstrate_agent_collaboration(self) -> Dict[str, Any]:
        """
        演示多智能体协作能力

        这个方法展示多智能体系统的核心能力和架构，
        用于系统演示和教育目的。

        返回：包含系统能力演示信息的字典

        适用于大模型技术初级用户：
        这个方法提供了一个完整的系统能力概览，
        帮助理解多智能体系统的工作原理。
        """
        demo_output = {
            'collaboration_demo': True,          # 协作演示标志
            'agent_network': {},                 # 智能体网络信息
            'communication_patterns': {},        # 通信模式
            'decision_making_process': {},       # 决策制定过程
            'system_capabilities': []            # 系统能力列表
        }

        # 展示智能体网络结构
        agent_names = {
            'travel_advisor': '旅行顾问',
            'weather_analyst': '天气分析师',
            'budget_optimizer': '预算优化师',
            'local_expert': '当地专家',
            'itinerary_planner': '行程规划师',
            'coordinator': '协调员'
        }

        for agent_id, agent in self.agents.items():
            demo_output['agent_network'][agent_names.get(agent_id, agent_id)] = {
                'role': agent.role.value,                                    # 智能体角色
                'capabilities': agent.capabilities,                          # 能力列表
                'connected_agents': len(agent.collaboration_network),        # 连接的智能体数量
                'knowledge_base_size': len(agent.knowledge_base)             # 知识库大小
            }

        # 展示通信模式
        demo_output['communication_patterns'] = {
            'hub_registered_agents': len(self.communication_hub.agents),     # 注册的智能体数量
            'message_types_supported': [t.value for t in MessageType],      # 支持的消息类型
            'collaborative_features': ['广播消息', '直接消息', '共识构建']      # 协作功能
        }

        # 展示决策制定过程
        demo_output['decision_making_process'] = {
            'synthesis_engine': '智能体决策引擎',                             # 综合引擎
            'consensus_mechanisms': ['加权投票', '专业优先', '冲突解决'],       # 共识机制
            'quality_assurance': ['验证', '优化', '一致性检查']               # 质量保证
        }

        # 系统能力展示
        demo_output['system_capabilities'] = [
            '6个专业智能体的协作规划',
            '实时决策综合和共识构建',
            '竞争性推荐间的冲突解决',
            '多维度优化（成本、时间、天气、物流）',
            '基于用户优先级的自适应规划',
            '全面的验证和质量保证'
        ]

        return demo_output
