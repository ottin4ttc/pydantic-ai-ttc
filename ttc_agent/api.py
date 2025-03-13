from fastapi import APIRouter, Depends, Request, Form, Body
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel

from .config import settings
from .database import Database, get_database
from .conversation import Conversation, ConversationService
from .chat import Message, ChatService
from .agents import AgentFactory
from .bot import Bot, BotService
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

# Define request model
class ConversationCreate(BaseModel):
    role_type: str = "default"
    bot_name: str = "Default Bot"

# 创建路由
router = APIRouter()

# 创建模型实例
openai_model = OpenAIModel(
    'gpt-4o-mini',
    provider=OpenAIProvider(api_key=settings.OPENAI_API_KEY)
)

dmx_model = OpenAIModel(
    'gpt-4o-mini',
    provider=OpenAIProvider(
        api_key=settings.DMX_API_KEY,
        base_url='https://vip.dmxapi.com/v1'
    )
)

# 创建Agent工厂
agent_factory = AgentFactory(openai_model, dmx_model)

# 依赖注入
async def get_chat_service(db: Database = Depends(get_database)) -> ChatService:
    return ChatService(db, agent_factory)

async def get_conversation_service(db: Database = Depends(get_database)) -> ConversationService:
    return ConversationService(db)

async def get_bot_service(db: Database = Depends(get_database)) -> BotService:
    return BotService(db)

# 静态文件路由
THIS_DIR = Path(__file__).parent
router.mount("/static", StaticFiles(directory=THIS_DIR / "static"), name="static")

@router.get('/')
async def index() -> FileResponse:
    """返回主页"""
    static_dir = THIS_DIR / "static"
    if static_dir.exists() and (static_dir / "index.html").exists():
        return FileResponse(static_dir / "index.html")
    return FileResponse(THIS_DIR / 'chat_app.html', media_type='text/html')

@router.get('/{path:path}')
async def serve_react(path: str) -> FileResponse:
    """服务静态文件"""
    static_dir = THIS_DIR / "static"
    if path and (static_dir / path).exists():
        return FileResponse(static_dir / path)
    elif static_dir.exists() and (static_dir / "index.html").exists():
        return FileResponse(static_dir / "index.html")
    return FileResponse(THIS_DIR / 'chat_app.html', media_type='text/html')

@router.post("/conversations")
async def create_conversation(
    request: Request,
    conversation_service: ConversationService = Depends(get_conversation_service),
    bot_service: BotService = Depends(get_bot_service)
) -> Conversation:
    """创建新会话"""
    try:
        # 直接使用请求体中的JSON数据
        data = await request.json()
        role_type = data.get("role_type", "default")
        bot_id = data.get("bot_id", None)
        
        # Get bot name from bot_id or use default bot
        bot_name = "Default Bot"
        if bot_id:
            bot = await bot_service.get_bot(bot_id)
            if bot:
                bot_name = bot.name
                role_type = bot.role_type
        else:
            # Use default bot if no bot_id provided
            default_bot = await bot_service.get_default_bot()
            if default_bot:
                bot_name = default_bot.name
                role_type = default_bot.role_type
                
        print(f"Creating conversation with role_type: {role_type}, bot_name: {bot_name}")
        return await conversation_service.create_conversation(role_type, bot_name)
    except Exception as e:
        print(f"Error creating conversation: {e}")
        import traceback
        traceback.print_exc()
        # 如果JSON解析失败，尝试使用默认值
        default_bot = await bot_service.get_default_bot()
        bot_name = default_bot.name if default_bot else "Default Bot"
        role_type = default_bot.role_type if default_bot else "default"
        return await conversation_service.create_conversation(role_type, bot_name)

@router.get("/conversations")
async def get_conversations(
    conversation_service: ConversationService = Depends(get_conversation_service)
) -> List[Conversation]:
    """获取所有会话"""
    return await conversation_service.get_conversations()

@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service)
) -> Optional[Conversation]:
    """获取会话信息"""
    return await conversation_service.get_conversation(conversation_id)

class ChatRequest(BaseModel):
    content: str
    role_type: str = "default"

@router.post("/chat/{conversation_id}")
async def chat(
    conversation_id: str,
    data: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
) -> StreamingResponse:
    """处理聊天消息"""
    return StreamingResponse(
        chat_service.process_message(data.content, conversation_id, data.role_type),
        media_type='text/event-stream'
    )

@router.get("/chat/{conversation_id}/history")
async def get_chat_history(
    conversation_id: str,
    chat_service: ChatService = Depends(get_chat_service)
) -> List[Message]:
    """获取聊天历史"""
    return await chat_service.get_chat_history(conversation_id)

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
    data: BotCreate,
    bot_service: BotService = Depends(get_bot_service)
) -> Bot:
    """Create a new bot configuration"""
    return await bot_service.create_bot(
        data.name, 
        data.role_type, 
        data.system_prompt, 
        data.is_default
    )

@router.get("/bots")
async def get_bots(
    bot_service: BotService = Depends(get_bot_service)
) -> List[Bot]:
    """Get all bot configurations"""
    return await bot_service.get_bots()

@router.get("/bots/default")
async def get_default_bot(
    bot_service: BotService = Depends(get_bot_service)
) -> Optional[Bot]:
    """Get the default bot configuration"""
    return await bot_service.get_default_bot()

@router.get("/bots/{bot_id}")
async def get_bot(
    bot_id: str,
    bot_service: BotService = Depends(get_bot_service)
) -> Optional[Bot]:
    """Get a bot configuration by ID"""
    return await bot_service.get_bot(bot_id)

@router.put("/bots/{bot_id}")
async def update_bot(
    bot_id: str,
    data: BotUpdate,
    bot_service: BotService = Depends(get_bot_service)
) -> Optional[Bot]:
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
) -> bool:
    """Delete a bot configuration"""
    return await bot_service.delete_bot(bot_id)

@router.get("/bots/{bot_id}/welcome")
async def generate_welcome_message(
    bot_id: str,
    bot_service: BotService = Depends(get_bot_service)
) -> dict:
    """Generate a welcome message using the bot's system prompt"""
    bot = await bot_service.get_bot(bot_id)
    if bot is None:
        return {"content": "Welcome! How can I assist you today?"}
    
    # Create a temporary agent with the bot's system prompt
    agent = agent_factory.get_agent(bot.role_type, bot.system_prompt)
    
    # Generate a welcome message
    response = await agent.process("Generate a brief welcome message for a new user.", "welcome")
    
    return {"content": response.content}                  