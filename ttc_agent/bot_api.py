from fastapi import APIRouter, Depends, Request
from typing import Optional, List

from .database import Database, get_database
from .bot import Bot, BotService
from .agents import AgentFactory
from pydantic import BaseModel

# Create router
router = APIRouter()

# Dependency injection
async def get_bot_service(db: Database = Depends(get_database)):
    return BotService(db)

# Bot management endpoints
class BotCreate(BaseModel):
    name: str
    role_type: str
    system_prompt: str
    is_default: bool = False

class BotUpdate(BaseModel):
    name: str
    role_type: str
    system_prompt: str
    is_default: bool = False

@router.post("/bots")
async def create_bot(
    data: BotCreate
):
    """Create a new bot configuration"""
    try:
        # Create database connection
        async with Database.connect() as db:
            bot_service = BotService(db)
            bot = await bot_service.create_bot(
                data.name, 
                data.role_type, 
                data.system_prompt, 
                data.is_default
            )
            return {
                "id": bot.id,
                "name": bot.name,
                "role_type": bot.role_type,
                "system_prompt": bot.system_prompt,
                "is_default": bot.is_default,
                "created_at": bot.created_at.isoformat(),
                "updated_at": bot.updated_at.isoformat()
            }
    except Exception as e:
        print(f"Error creating bot: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@router.get("/bots")
async def get_bots():
    """Get all bot configurations"""
    try:
        # Create database connection
        async with Database.connect() as db:
            bot_service = BotService(db)
            bots = await bot_service.get_bots()
            # Convert to dict for serialization
            return [
                {
                    "id": bot.id,
                    "name": bot.name,
                    "role_type": bot.role_type,
                    "system_prompt": bot.system_prompt,
                    "is_default": bot.is_default,
                    "created_at": bot.created_at.isoformat(),
                    "updated_at": bot.updated_at.isoformat()
                }
                for bot in bots
            ]
    except Exception as e:
        print(f"Error getting bots: {e}")
        import traceback
        traceback.print_exc()
        return []

@router.get("/bots/default")
async def get_default_bot():
    """Get the default bot configuration"""
    try:
        # Create database connection
        async with Database.connect() as db:
            bot_service = BotService(db)
            bot = await bot_service.get_default_bot()
            if bot:
                return {
                    "id": bot.id,
                    "name": bot.name,
                    "role_type": bot.role_type,
                    "system_prompt": bot.system_prompt,
                    "is_default": bot.is_default,
                    "created_at": bot.created_at.isoformat(),
                    "updated_at": bot.updated_at.isoformat()
                }
            return None
    except Exception as e:
        print(f"Error getting default bot: {e}")
        import traceback
        traceback.print_exc()
        return None

@router.get("/bots/{bot_id}")
async def get_bot(
    bot_id: str,
    bot_service: BotService = Depends(get_bot_service)
):
    """Get a bot configuration by ID"""
    return await bot_service.get_bot(bot_id)

@router.put("/bots/{bot_id}")
async def update_bot(
    bot_id: str,
    data: BotUpdate,
    bot_service: BotService = Depends(get_bot_service)
):
    """Update a bot configuration"""
    return await bot_service.update_bot(
        bot_id,
        data.name,
        data.role_type,
        data.system_prompt,
        data.is_default
    )

@router.delete("/bots/{bot_id}")
async def delete_bot(
    bot_id: str,
    bot_service: BotService = Depends(get_bot_service)
):
    """Delete a bot configuration"""
    return await bot_service.delete_bot(bot_id)

@router.get("/bots/{bot_id}/welcome")
async def generate_welcome_message(
    bot_id: str
):
    """Generate a welcome message using the bot's system prompt"""
    try:
        # Create database connection
        async with Database.connect() as db:
            bot_service = BotService(db)
            bot = await bot_service.get_bot(bot_id)
            
            if bot is None:
                return {"content": "Welcome! How can I assist you today?"}
            
            # Create a temporary agent with the bot's system prompt
            from .api_fixed import agent_factory
            agent = agent_factory.get_agent(bot.role_type, bot.system_prompt)
            
            # Generate a welcome message
            response = await agent.process("Generate a brief welcome message for a new user.", "welcome")
            
            return {"content": response.content}
    except Exception as e:
        print(f"Error generating welcome message: {e}")
        import traceback
        traceback.print_exc()
        return {"content": "Welcome! How can I assist you today?", "error": str(e)}
