from fastapi import APIRouter, Depends, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from typing import Optional

from .config import settings
from .database import Database, get_database
from .conversation import Conversation, ConversationService
from .chat import Message, ChatService
from .agents import AgentFactory
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

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
    role_type: str,
    conversation_service: ConversationService = Depends(get_conversation_service)
) -> Conversation:
    """创建新会话"""
    return await conversation_service.create_conversation(role_type)

@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service)
) -> Optional[Conversation]:
    """获取会话信息"""
    return await conversation_service.get_conversation(conversation_id)

@router.post("/chat/{conversation_id}")
async def chat(
    conversation_id: str,
    content: str,
    role_type: str,
    chat_service: ChatService = Depends(get_chat_service)
) -> StreamingResponse:
    """处理聊天消息"""
    return StreamingResponse(
        chat_service.process_message(content, conversation_id, role_type),
        media_type='text/event-stream'
    )

@router.get("/chat/{conversation_id}/history")
async def get_chat_history(
    conversation_id: str,
    chat_service: ChatService = Depends(get_chat_service)
) -> list[Message]:
    """获取聊天历史"""
    return await chat_service.get_chat_history(conversation_id) 