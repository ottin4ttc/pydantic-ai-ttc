from dataclasses import dataclass
from datetime import datetime
import uuid
from typing import Optional, List
from .database import Database

@dataclass
class Bot:
    """Bot model for storing configurations"""
    id: str
    name: str
    role_type: str
    system_prompt: str
    is_default: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(cls, name: str, role_type: str, system_prompt: str, is_default: bool = False) -> 'Bot':
        now = datetime.now()
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            role_type=role_type,
            system_prompt=system_prompt,
            is_default=is_default,
            created_at=now,
            updated_at=now
        )

class BotService:
    """Bot service for managing bot configurations"""
    def __init__(self, db: Database):
        self.db = db

    async def create_bot(self, name: str, role_type: str, system_prompt: str, is_default: bool = False) -> Bot:
        """Create a new bot configuration"""
        # If this bot is set as default, unset any existing default
        if is_default:
            await self.db._asyncify(
                self.db._execute,
                "UPDATE bots SET is_default = 0",
                commit=True
            )
        
        bot = Bot.create(name, role_type, system_prompt, is_default)
        await self.db._asyncify(
            self.db._execute,
            """
            INSERT INTO bots (id, name, role_type, system_prompt, is_default, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            bot.id,
            bot.name,
            bot.role_type,
            bot.system_prompt,
            1 if bot.is_default else 0,
            bot.created_at,
            bot.updated_at,
            commit=True
        )
        return bot

    async def get_bots(self) -> List[Bot]:
        """Get all bot configurations"""
        cursor = await self.db._asyncify(
            self.db._execute,
            "SELECT id, name, role_type, system_prompt, is_default, created_at, updated_at FROM bots ORDER BY name"
        )
        rows = await self.db._asyncify(cursor.fetchall)
        return [
            Bot(
                id=row[0],
                name=row[1],
                role_type=row[2],
                system_prompt=row[3],
                is_default=bool(row[4]),
                created_at=datetime.fromisoformat(row[5]),
                updated_at=datetime.fromisoformat(row[6])
            )
            for row in rows
        ]

    async def get_bot(self, bot_id: str) -> Optional[Bot]:
        """Get a bot configuration by ID"""
        cursor = await self.db._asyncify(
            self.db._execute,
            "SELECT id, name, role_type, system_prompt, is_default, created_at, updated_at FROM bots WHERE id = ?",
            bot_id
        )
        row = await self.db._asyncify(cursor.fetchone)
        if row is None:
            return None
        return Bot(
            id=row[0],
            name=row[1],
            role_type=row[2],
            system_prompt=row[3],
            is_default=bool(row[4]),
            created_at=datetime.fromisoformat(row[5]),
            updated_at=datetime.fromisoformat(row[6])
        )

    async def get_default_bot(self) -> Optional[Bot]:
        """Get the default bot configuration"""
        cursor = await self.db._asyncify(
            self.db._execute,
            "SELECT id, name, role_type, system_prompt, is_default, created_at, updated_at FROM bots WHERE is_default = 1"
        )
        row = await self.db._asyncify(cursor.fetchone)
        if row is None:
            return None
        return Bot(
            id=row[0],
            name=row[1],
            role_type=row[2],
            system_prompt=row[3],
            is_default=bool(row[4]),
            created_at=datetime.fromisoformat(row[5]),
            updated_at=datetime.fromisoformat(row[6])
        )

    async def update_bot(self, bot_id: str, name: str, role_type: str, system_prompt: str, is_default: bool = False) -> Optional[Bot]:
        """Update a bot configuration"""
        # If this bot is set as default, unset any existing default
        if is_default:
            await self.db._asyncify(
                self.db._execute,
                "UPDATE bots SET is_default = 0",
                commit=True
            )
        
        now = datetime.now()
        await self.db._asyncify(
            self.db._execute,
            """
            UPDATE bots 
            SET name = ?, role_type = ?, system_prompt = ?, is_default = ?, updated_at = ?
            WHERE id = ?
            """,
            name,
            role_type,
            system_prompt,
            1 if is_default else 0,
            now,
            bot_id,
            commit=True
        )
        return await self.get_bot(bot_id)

    async def delete_bot(self, bot_id: str) -> bool:
        """Delete a bot configuration"""
        # Check if this is the default bot
        bot = await self.get_bot(bot_id)
        if bot is None:
            return False
            
        # Don't allow deleting the default bot
        if bot.is_default:
            return False
            
        await self.db._asyncify(
            self.db._execute,
            "DELETE FROM bots WHERE id = ?",
            bot_id,
            commit=True
        )
        return True
