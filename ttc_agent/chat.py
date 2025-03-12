from dataclasses import dataclass, field
from datetime import datetime
import json
import uuid
from typing import AsyncIterator, List, Optional, Literal
from .database import Database
from .agents import AgentFactory, AgentResponse

@dataclass
class Message:
    """消息模型"""
    id: str
    conversation_id: str
    role: Literal['user', 'assistant', 'system']
    content: str
    tokens_used: Optional[int] = None
    process_logs: Optional[List[str]] = None
    timestamp: datetime = field(default_factory=datetime.now)

    @classmethod
    def create_user_message(cls, conversation_id: str, content: str) -> 'Message':
        return cls(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            role='user',
            content=content
        )

    @classmethod
    def create_assistant_message(
        cls, 
        conversation_id: str, 
        content: str,
        tokens_used: int,
        process_logs: List[str]
    ) -> 'Message':
        return cls(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            role='assistant',
            content=content,
            tokens_used=tokens_used,
            process_logs=process_logs
        )

class ChatService:
    """聊天服务"""
    def __init__(self, db: Database, agent_factory: AgentFactory):
        self.db = db
        self.agent_factory = agent_factory

    async def process_message(
        self,
        content: str,
        conversation_id: str,
        role_type: str
    ) -> AsyncIterator[Message]:
        """处理消息并返回响应"""
        # 创建并保存用户消息
        user_message = Message.create_user_message(conversation_id, content)
        await self._save_message(user_message)

        # 获取对应的agent处理消息
        agent = self.agent_factory.get_agent(role_type)
        response: AgentResponse = await agent.process(content, conversation_id)

        # 创建并保存助手消息
        assistant_message = Message.create_assistant_message(
            conversation_id=conversation_id,
            content=response.content,
            tokens_used=response.tokens_used,
            process_logs=response.process_logs
        )
        await self._save_message(assistant_message)
        
        yield assistant_message

    async def get_chat_history(self, conversation_id: str) -> List[Message]:
        """获取聊天历史"""
        cursor = await self.db._asyncify(
            self.db._execute,
            """
            SELECT id, conversation_id, role, content, tokens_used, process_logs, timestamp
            FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp
            """,
            conversation_id
        )
        rows = await self.db._asyncify(cursor.fetchall)
        return [
            Message(
                id=row[0],
                conversation_id=row[1],
                role=row[2],
                content=row[3],
                tokens_used=row[4],
                process_logs=json.loads(row[5]) if row[5] else None,
                timestamp=datetime.fromisoformat(row[6])
            )
            for row in rows
        ]

    async def _save_message(self, message: Message) -> None:
        """保存消息到数据库"""
        await self.db._asyncify(
            self.db._execute,
            """
            INSERT INTO messages (
                id, conversation_id, role, content, 
                tokens_used, process_logs, timestamp
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            message.id,
            message.conversation_id,
            message.role,
            message.content,
            message.tokens_used,
            json.dumps(message.process_logs) if message.process_logs else None,
            message.timestamp,
            commit=True
        ) 