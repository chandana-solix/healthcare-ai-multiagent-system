"""
Enhanced Blackboard System for Real Agent Communication
"""
from typing import Dict, Any, List, Callable
from collections import defaultdict
from datetime import datetime
from enum import Enum
import asyncio
import json

class Priority(Enum):
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4

class MessageType(Enum):
    FINDING = "finding"
    QUESTION = "question"
    RESPONSE = "response"
    ALERT = "alert"
    CONSENSUS = "consensus"

class EnhancedBlackboard:
    """
    Intelligent blackboard that enables real agent communication and debate
    """
    
    def __init__(self):
        # Core data storage
        self.knowledge_base = {}
        self.conversation_log = []
        self.active_alerts = []
        
        # Agent communication
        self.subscribers = defaultdict(list)
        self.agent_responses = defaultdict(list)
        self.pending_questions = []
        
        # Consensus tracking
        self.agent_opinions = defaultdict(dict)
        self.consensus_topics = {}
        
    def subscribe(self, agent_id: str, event_patterns: List[str], callback: Callable):
        """
        Subscribe an agent to specific event patterns
        
        Examples:
        - "infection_suspected" - specific event
        - "lab_*" - all lab-related events
        - "*_critical" - all critical events
        """
        for pattern in event_patterns:
            self.subscribers[pattern].append({
                'agent_id': agent_id,
                'callback': callback
            })
    
    async def post(self, agent_id: str, message_type: MessageType, 
                   topic: str, content: Any, priority: Priority = Priority.NORMAL):
        """
        Post a message that other agents can respond to
        """
        message = {
            'id': f"{agent_id}_{datetime.now().timestamp()}",
            'timestamp': datetime.now().isoformat(),
            'agent_id': agent_id,
            'type': message_type.value,
            'topic': topic,
            'content': content,
            'priority': priority.value
        }
        
        # Log the conversation
        self.conversation_log.append(message)
        
        # Store in knowledge base
        if topic not in self.knowledge_base:
            self.knowledge_base[topic] = []
        self.knowledge_base[topic].append(message)
        
        # Handle critical alerts
        if priority == Priority.CRITICAL:
            self.active_alerts.append(message)
            print(f"\n🚨 CRITICAL ALERT from {agent_id}: {topic}")
        
        # Notify subscribers
        await self._notify_subscribers(topic, message)
        
        # Log the communication
        self._log_communication(agent_id, topic, content, priority)
    
    async def ask_question(self, agent_id: str, question: str, target_agents: List[str] = None):
        """
        Agent asks a question to other agents
        """
        question_data = {
            'question': question,
            'asking_agent': agent_id,
            'target_agents': target_agents or 'all',
            'responses': []
        }
        
        self.pending_questions.append(question_data)
        
        # Post as a question type
        await self.post(
            agent_id=agent_id,
            message_type=MessageType.QUESTION,
            topic=f"question_{len(self.pending_questions)}",
            content=question
        )
        
        return question_data
    
    async def respond_to_question(self, agent_id: str, question_id: str, response: str):
        """
        Agent responds to a question
        """
        # Find the question
        for q in self.pending_questions:
            if f"question_{self.pending_questions.index(q) + 1}" == question_id:
                q['responses'].append({
                    'agent_id': agent_id,
                    'response': response,
                    'timestamp': datetime.now().isoformat()
                })
                
                await self.post(
                    agent_id=agent_id,
                    message_type=MessageType.RESPONSE,
                    topic=question_id,
                    content=response
                )
                break
    
    def post_opinion(self, agent_id: str, topic: str, opinion: str, confidence: float):
        """
        Agent posts their opinion on a topic for consensus building
        """
        if topic not in self.agent_opinions:
            self.agent_opinions[topic] = {}
        
        self.agent_opinions[topic][agent_id] = {
            'opinion': opinion,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        }
        
        # Check if we have enough opinions for consensus
        if len(self.agent_opinions[topic]) >= 3:
            self._attempt_consensus(topic)
    
    def _attempt_consensus(self, topic: str):
        """
        Try to build consensus from agent opinions
        """
        opinions = self.agent_opinions[topic]
        
        # Group similar opinions
        opinion_groups = defaultdict(list)
        for agent_id, data in opinions.items():
            # Simple grouping - in real implementation, use NLP similarity
            key = data['opinion'].lower()[:50]  # Simplified
            opinion_groups[key].append({
                'agent': agent_id,
                'confidence': data['confidence']
            })
        
        # Find majority opinion
        majority_opinion = max(opinion_groups.items(), 
                              key=lambda x: sum(a['confidence'] for a in x[1]))
        
        consensus = {
            'topic': topic,
            'consensus': majority_opinion[0],
            'supporting_agents': [a['agent'] for a in majority_opinion[1]],
            'confidence': sum(a['confidence'] for a in majority_opinion[1]) / len(opinions),
            'dissenting_opinions': len(opinion_groups) - 1
        }
        
        self.consensus_topics[topic] = consensus
        
        print(f"\n🤝 CONSENSUS REACHED on {topic}:")
        print(f"   Decision: {consensus['consensus']}")
        print(f"   Confidence: {consensus['confidence']:.2%}")
        print(f"   Supporting agents: {', '.join(consensus['supporting_agents'])}")
    
    async def _notify_subscribers(self, topic: str, message: Dict):
        """
        Notify all subscribers matching the topic pattern
        """
        notified_agents = set()
        
        for pattern, subscribers in self.subscribers.items():
            if self._matches_pattern(topic, pattern):
                for subscriber in subscribers:
                    agent_id = subscriber['agent_id']
                    
                    # Don't notify the sender
                    if agent_id != message['agent_id'] and agent_id not in notified_agents:
                        callback = subscriber['callback']
                        
                        try:
                            # Call the agent's callback
                            result = callback(topic, message)
                            if asyncio.iscoroutine(result):
                                await result
                            
                            notified_agents.add(agent_id)
                        except Exception as e:
                            print(f"Error notifying {agent_id}: {e}")
    
    def _matches_pattern(self, topic: str, pattern: str) -> bool:
        """
        Check if topic matches subscription pattern
        """
        if pattern == topic:
            return True
        if pattern.endswith('*'):
            return topic.startswith(pattern[:-1])
        if pattern.startswith('*'):
            return topic.endswith(pattern[1:])
        return False
    
    def _log_communication(self, agent_id: str, topic: str, content: Any, priority: Priority):
        """
        Log agent communication for debugging
        """
        icon = "🚨" if priority == Priority.CRITICAL else "💬"
        print(f"\n{icon} [{agent_id}] → {topic}")
        
        if isinstance(content, dict):
            for key, value in content.items():
                print(f"   {key}: {value}")
        else:
            print(f"   {content}")
    
    def get_knowledge(self, topic: str) -> List[Dict]:
        """
        Get all knowledge on a topic
        """
        return self.knowledge_base.get(topic, [])
    
    def get_latest_finding(self, topic: str) -> Any:
        """
        Get the most recent finding on a topic
        """
        knowledge = self.get_knowledge(topic)
        if knowledge:
            return knowledge[-1]['content']
        return None
    
    def has_alert(self, alert_type: str) -> bool:
        """
        Check if there's an active alert
        """
        return any(alert['topic'] == alert_type for alert in self.active_alerts)
    
    def get_agent_conversation(self, agent_id: str = None) -> List[Dict]:
        """
        Get conversation history, optionally filtered by agent
        """
        if agent_id:
            return [msg for msg in self.conversation_log if msg['agent_id'] == agent_id]
        return self.conversation_log
    
    def clear(self):
        """
        Clear the blackboard for new patient
        """
        self.knowledge_base.clear()
        self.conversation_log.clear()
        self.active_alerts.clear()
        self.agent_opinions.clear()
        self.consensus_topics.clear()
        self.pending_questions.clear()
    
    async def process_events(self):
        """
        Process any pending events (placeholder for async processing)
        """
        # In a real implementation, this would process queued events
        # For now, just a small delay to allow async operations to complete
        await asyncio.sleep(0.1)

# Global blackboard instance
blackboard = EnhancedBlackboard()
