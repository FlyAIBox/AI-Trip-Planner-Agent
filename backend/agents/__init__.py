"""
多智能体旅行规划系统的基础智能体框架

这个模块定义了传统多智能体系统的核心组件，包括：
- 智能体角色定义和枚举
- 消息类型和通信协议
- 基础智能体抽象类
- 智能体通信中心
- 协作决策引擎

适用于大模型技术初级用户：
这个模块展示了如何设计一个完整的多智能体系统架构，
包含通信机制、协作模式和决策流程。
"""

import json
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from enum import Enum

class AgentRole(Enum):
    """
    定义不同的智能体角色

    这个枚举类定义了系统中所有智能体的角色类型，
    每个角色都有特定的职责和专业领域。

    适用于大模型技术初级用户：
    枚举类是一种定义常量集合的优雅方式，
    确保角色名称的一致性和类型安全。
    """
    COORDINATOR = "coordinator"           # 协调员：总体协调和决策
    TRAVEL_ADVISOR = "travel_advisor"     # 旅行顾问：目的地专业知识
    BUDGET_OPTIMIZER = "budget_optimizer" # 预算优化师：成本控制和优化
    WEATHER_ANALYST = "weather_analyst"   # 天气分析师：天气情报和建议
    LOCAL_EXPERT = "local_expert"         # 当地专家：本地知识和文化
    ITINERARY_PLANNER = "itinerary_planner" # 行程规划师：日程安排和物流

class MessageType(Enum):
    """
    智能体可以发送的消息类型

    定义了智能体间通信的不同消息类型，
    每种类型都有特定的用途和处理方式。

    适用于大模型技术初级用户：
    通过定义消息类型，系统可以更好地处理
    不同类型的智能体交互和协作。
    """
    REQUEST = "request"               # 请求：向其他智能体请求信息或服务
    RESPONSE = "response"             # 响应：对请求的回复
    BROADCAST = "broadcast"           # 广播：向所有智能体发送信息
    QUERY = "query"                   # 查询：询问特定信息
    RECOMMENDATION = "recommendation" # 推荐：提供建议或推荐

class Message:
    """
    智能体通信的消息结构

    这个类定义了智能体间通信的标准消息格式，
    包含发送者、接收者、消息类型和内容等信息。

    适用于大模型技术初级用户：
    这个类展示了如何设计一个完整的消息系统，
    包含元数据管理和序列化功能。
    """

    def __init__(self, sender: str, receiver: str, msg_type: MessageType,
                 content: Dict[str, Any], timestamp: datetime = None):
        """
        初始化消息对象

        参数：
        - sender: 发送者ID
        - receiver: 接收者ID
        - msg_type: 消息类型
        - content: 消息内容
        - timestamp: 时间戳（可选）
        """
        self.sender = sender                                    # 发送者
        self.receiver = receiver                                # 接收者
        self.msg_type = msg_type                               # 消息类型
        self.content = content                                 # 消息内容
        self.timestamp = timestamp or datetime.now()          # 时间戳
        self.id = f"{sender}_{receiver}_{int(time.time() * 1000)}" # 唯一ID

    def to_dict(self) -> Dict[str, Any]:
        """
        将消息转换为字典格式

        用于消息的序列化和存储，
        便于日志记录和调试。

        返回：消息的字典表示
        """
        return {
            'id': self.id,
            'sender': self.sender,
            'receiver': self.receiver,
            'type': self.msg_type.value,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }

class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(self, agent_id: str, role: AgentRole, capabilities: List[str]):
        self.agent_id = agent_id
        self.role = role
        self.capabilities = capabilities
        self.message_queue: List[Message] = []
        self.knowledge_base: Dict[str, Any] = {}
        self.is_active = True
        self.collaboration_network: Dict[str, 'BaseAgent'] = {}
        
    @abstractmethod
    def process_message(self, message: Message) -> Optional[Message]:
        """Process incoming message and return response if needed"""
        pass
    
    @abstractmethod
    def generate_recommendation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recommendations based on context"""
        pass
    
    def send_message(self, receiver: str, msg_type: MessageType, content: Dict[str, Any]) -> bool:
        """Send message to another agent"""
        if receiver in self.collaboration_network:
            message = Message(self.agent_id, receiver, msg_type, content)
            self.collaboration_network[receiver].receive_message(message)
            return True
        return False
    
    def receive_message(self, message: Message):
        """Receive and queue message"""
        self.message_queue.append(message)
    
    def process_message_queue(self) -> List[Message]:
        """Process all queued messages"""
        responses = []
        while self.message_queue:
            message = self.message_queue.pop(0)
            response = self.process_message(message)
            if response:
                responses.append(response)
        return responses
    
    def connect_agent(self, agent: 'BaseAgent'):
        """Connect to another agent for collaboration"""
        self.collaboration_network[agent.agent_id] = agent
        agent.collaboration_network[self.agent_id] = self
    
    def update_knowledge(self, key: str, value: Any):
        """Update agent's knowledge base"""
        self.knowledge_base[key] = value
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'agent_id': self.agent_id,
            'role': self.role.value,
            'capabilities': self.capabilities,
            'is_active': self.is_active,
            'messages_queued': len(self.message_queue),
            'connected_agents': list(self.collaboration_network.keys()),
            'knowledge_items': len(self.knowledge_base)
        }

class AgentCommunicationHub:
    """Central hub for agent communication and coordination"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.message_log: List[Message] = []
        
    def register_agent(self, agent: BaseAgent):
        """Register an agent with the hub"""
        self.agents[agent.agent_id] = agent
        
    def connect_all_agents(self):
        """Connect all agents to each other"""
        agent_list = list(self.agents.values())
        for i, agent1 in enumerate(agent_list):
            for j, agent2 in enumerate(agent_list):
                if i != j:
                    agent1.connect_agent(agent2)
    
    def broadcast_message(self, sender_id: str, content: Dict[str, Any]) -> List[Message]:
        """Broadcast message from one agent to all others"""
        responses = []
        if sender_id in self.agents:
            sender = self.agents[sender_id]
            for agent_id, agent in self.agents.items():
                if agent_id != sender_id:
                    message = Message(sender_id, agent_id, MessageType.BROADCAST, content)
                    agent.receive_message(message)
                    self.message_log.append(message)
        return responses
    
    def process_all_agents(self) -> Dict[str, List[Message]]:
        """Process message queues for all agents"""
        all_responses = {}
        for agent_id, agent in self.agents.items():
            responses = agent.process_message_queue()
            if responses:
                all_responses[agent_id] = responses
        return all_responses
    
    def get_agent_by_role(self, role: AgentRole) -> Optional[BaseAgent]:
        """Get agent by role"""
        for agent in self.agents.values():
            if agent.role == role:
                return agent
        return None
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            'total_agents': len(self.agents),
            'active_agents': len([a for a in self.agents.values() if a.is_active]),
            'total_messages': len(self.message_log),
            'agents': {aid: agent.get_status() for aid, agent in self.agents.items()}
        }

class AgentDecisionEngine:
    """Decision engine for complex multi-agent decisions"""
    
    def __init__(self, communication_hub: AgentCommunicationHub):
        self.hub = communication_hub
        
    def collaborative_decision(self, decision_context: Dict[str, Any], 
                             involved_agents: List[str]) -> Dict[str, Any]:
        """Make collaborative decision involving multiple agents"""
        
        # Step 1: Gather recommendations from involved agents
        recommendations = {}
        for agent_id in involved_agents:
            if agent_id in self.hub.agents:
                agent = self.hub.agents[agent_id]
                rec = agent.generate_recommendation(decision_context)
                recommendations[agent_id] = rec
        
        # Step 2: Analyze and synthesize recommendations
        final_decision = self._synthesize_recommendations(recommendations, decision_context)
        
        # Step 3: Broadcast final decision
        self.hub.broadcast_message("decision_engine", {
            'decision': final_decision,
            'context': decision_context,
            'contributing_agents': involved_agents
        })
        
        return final_decision
    
    def _synthesize_recommendations(self, recommendations: Dict[str, Dict], 
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize multiple agent recommendations into final decision"""
        
        # Weight recommendations based on agent expertise and context
        weights = self._calculate_agent_weights(recommendations, context)
        
        # Combine recommendations
        final_decision = {
            'primary_recommendation': None,
            'confidence_score': 0.0,
            'supporting_evidence': [],
            'alternative_options': [],
            'consensus_level': 0.0
        }
        
        # Simple consensus mechanism (can be enhanced with ML)
        if recommendations:
            # Find most common recommendations
            all_recommendations = []
            for agent_id, rec in recommendations.items():
                weight = weights.get(agent_id, 1.0)
                all_recommendations.append({
                    'agent': agent_id,
                    'recommendation': rec,
                    'weight': weight
                })
            
            # Select best recommendation based on weights and consensus
            best_rec = max(all_recommendations, key=lambda x: x['weight'])
            final_decision['primary_recommendation'] = best_rec['recommendation']
            final_decision['confidence_score'] = best_rec['weight']
            final_decision['supporting_evidence'] = [r['recommendation'] for r in all_recommendations]
            
            # Calculate consensus level
            final_decision['consensus_level'] = len(all_recommendations) / len(recommendations) if recommendations else 0
        
        return final_decision
    
    def _calculate_agent_weights(self, recommendations: Dict[str, Dict], 
                               context: Dict[str, Any]) -> Dict[str, float]:
        """Calculate weights for agent recommendations based on expertise"""
        weights = {}
        
        # Default weights based on agent roles and context
        for agent_id in recommendations.keys():
            if agent_id in self.hub.agents:
                agent = self.hub.agents[agent_id]
                base_weight = 1.0
                
                # Increase weight based on relevance to context
                if context.get('primary_concern') == 'budget' and agent.role == AgentRole.BUDGET_OPTIMIZER:
                    base_weight = 2.0
                elif context.get('primary_concern') == 'weather' and agent.role == AgentRole.WEATHER_ANALYST:
                    base_weight = 2.0
                elif context.get('primary_concern') == 'local_insights' and agent.role == AgentRole.LOCAL_EXPERT:
                    base_weight = 2.0
                
                weights[agent_id] = base_weight
        
        return weights
