from dataclasses import dataclass
from typing import List, Dict
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage

@dataclass
class AgentResponse:
    """Agent响应模型"""
    content: str
    tokens_used: int
    process_logs: List[str]

class BaseAgent:
    """基础Agent类"""
    def __init__(self, model: OpenAIModel, system_prompt: str):
        self.model = model
        self.system_prompt = system_prompt
        self.agent = Agent(model, instrument=True)

    async def process(self, message: str, conversation_id: str) -> AgentResponse:
        """处理消息"""
        result = await self.agent.run(
            message,
            system_prompt=self.system_prompt
        )
        return AgentResponse(
            content=str(result.response),
            tokens_used=result.token_usage.total_tokens,
            process_logs=result.logs
        )

class CustomerServiceAgent(BaseAgent):
    """客服Agent"""
    SYSTEM_PROMPT = """You are a helpful customer service representative.
    You are patient, friendly, and always try to help customers solve their problems.
    You communicate clearly and professionally."""

    def __init__(self, model: OpenAIModel):
        super().__init__(model=model, system_prompt=self.SYSTEM_PROMPT)

class TechnicalSupportAgent(BaseAgent):
    """技术支持Agent"""
    SYSTEM_PROMPT = """You are a technical support specialist.
    You have deep knowledge of our products and can help users solve technical issues.
    You explain technical concepts clearly and provide step-by-step solutions."""

    def __init__(self, model: OpenAIModel):
        super().__init__(model=model, system_prompt=self.SYSTEM_PROMPT)

class AgentFactory:
    """Agent工厂类"""
    def __init__(self, openai_model: OpenAIModel, dmx_model: OpenAIModel):
        self.openai_model = openai_model
        self.dmx_model = dmx_model
        self.predefined_agents = {
            'customer_service': CustomerServiceAgent(openai_model),
            'technical_support': TechnicalSupportAgent(dmx_model)
        }

    def get_agent(self, role_type: str, system_prompt: str | None = None) -> BaseAgent:
        """获取指定角色的Agent或创建自定义Agent"""
        if system_prompt is not None:
            # Create a custom agent with the provided system prompt
            return BaseAgent(self.openai_model, system_prompt)
        
        # Use predefined agent if available
        agent = self.predefined_agents.get(role_type)
        if agent is None:
            # For unknown role types, create a default agent
            return BaseAgent(self.openai_model, "You are a helpful AI assistant.")
        return agent  