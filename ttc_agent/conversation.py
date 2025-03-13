from dataclasses import dataclass
from datetime import datetime
import uuid
from typing import Optional, List
from .database import Database

@dataclass
class Conversation:
    """会话模型"""
    id: str
    role_type: str
    bot_name: str  # Add bot name field
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, role_type: str, bot_name: str) -> 'Conversation':
        now = datetime.now()
        return cls(
            id=str(uuid.uuid4()),
            role_type=role_type,
            bot_name=bot_name,
            created_at=now,
            updated_at=now
        )

class ConversationService:
    """会话服务"""
    def __init__(self, db: Database):
        self.db = db

    async def create_conversation(self, role_type: str, bot_name: str) -> Conversation:
        """创建新会话"""
        conversation = Conversation.create(role_type, bot_name)
        await self.db._asyncify(
            self.db._execute,
            """
            INSERT INTO conversations (id, role_type, bot_name, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            conversation.id,
            conversation.role_type,
            conversation.bot_name,
            conversation.created_at,
            conversation.updated_at,
            commit=True
        )
        return conversation

    async def get_conversations(self) -> List[Conversation]:
        """获取所有会话"""
        cursor = await self.db._asyncify(
            self.db._execute,
            "SELECT id, role_type, bot_name, created_at, updated_at FROM conversations ORDER BY updated_at DESC"
        )
        rows = await self.db._asyncify(cursor.fetchall)
        return [
            Conversation(
                id=row[0],
                role_type=row[1],
                bot_name=row[2],
                created_at=datetime.fromisoformat(row[3]),
                updated_at=datetime.fromisoformat(row[4])
            )
            for row in rows
        ]

    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """获取会话信息"""
        cursor = await self.db._asyncify(
            self.db._execute,
            "SELECT id, role_type, bot_name, created_at, updated_at FROM conversations WHERE id = ?",
            conversation_id
        )
        row = await self.db._asyncify(cursor.fetchone)
        if row is None:
            return None
        return Conversation(
            id=row[0],
            role_type=row[1],
            bot_name=row[2],
            created_at=datetime.fromisoformat(row[3]),
            updated_at=datetime.fromisoformat(row[4])
        )

    async def update_conversation(self, conversation_id: str) -> None:
        """更新会话时间"""
        await self.db._asyncify(
            self.db._execute,
            "UPDATE conversations SET updated_at = ? WHERE id = ?",
            datetime.now(),
            conversation_id,
            commit=True
        )    
