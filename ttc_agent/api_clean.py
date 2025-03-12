from fastapi import APIRouter, Depends, Body, Request
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
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

# Define request models
class ConversationCreate(BaseModel):
    role_type: str = "default"

class ChatRequest(BaseModel):
    content: str
    role_type: str = "default"

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
    data: Optional[ConversationCreate] = None,
    conversation_service: ConversationService = Depends(get_conversation_service)
):
    """创建新会话"""
    try:
        role_type = "default"
        if data:
            role_type = data.role_type
        print(f"Creating conversation with role_type: {role_type}")
        result = await conversation_service.create_conversation(role_type)
        # Convert datetime objects to strings for JSON serialization
        return {
            "id": result.id,
            "role_type": result.role_type,
            "created_at": result.created_at.isoformat(),
            "updated_at": result.updated_at.isoformat()
        }
    except Exception as e:
        print(f"Error creating conversation: {e}")
        import traceback
        traceback.print_exc()
        # Return a default conversation object if creation fails
        return {
            "id": "error",
            "role_type": "default",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }

@router.post("/new_conversation", status_code=200)
async def new_conversation(request: Request):
    """创建新会话 - 简化版本，不需要请求体"""
    print("Creating new conversation with default role_type")
    try:
        # Use dependency injection to get the database
        db = request.state.db
        
        # Create a conversation directly
        import uuid
        from datetime import datetime
        
        conversation_id = str(uuid.uuid4())
        role_type = "default"
        now = datetime.now()
        
        # Insert into database
        await db._asyncify(
            db._execute,
            "INSERT INTO conversations (id, role_type, created_at, updated_at) VALUES (?, ?, ?, ?)",
            conversation_id,
            role_type,
            now,
            now,
            commit=True
        )
        
        # Return the conversation data
        return {
            "id": conversation_id,
            "role_type": role_type,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }
    except Exception as e:
        print(f"Error in new_conversation endpoint: {e}")
        import traceback
        traceback.print_exc()
        # Return a default conversation object if creation fails
        return {
            "id": "error",
            "role_type": "default",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }

@router.get("/conversations")
async def get_conversations(
    conversation_service: ConversationService = Depends(get_conversation_service)
) -> List[dict]:
    """获取所有会话"""
    conversations = await conversation_service.get_conversations()
    # Convert datetime objects to strings for JSON serialization
    return [
        {
            "id": conv.id,
            "role_type": conv.role_type,
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat()
        }
        for conv in conversations
    ]

@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    conversation_service: ConversationService = Depends(get_conversation_service)
) -> Optional[dict]:
    """获取会话信息"""
    conversation = await conversation_service.get_conversation(conversation_id)
    if conversation:
        # Convert datetime objects to strings for JSON serialization
        return {
            "id": conversation.id,
            "role_type": conversation.role_type,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat()
        }
    return None

@router.post("/chat/{conversation_id}")
async def chat(
    conversation_id: str,
    request: Request,
    chat_service: ChatService = Depends(get_chat_service)
) -> StreamingResponse:
    """处理聊天消息"""
    try:
        # Parse JSON data from request body
        data = await request.json()
        content = data.get("content", "")
        role_type = data.get("role_type", "default")
        print(f"Processing message for conversation {conversation_id}: {content}")
        return StreamingResponse(
            chat_service.process_message(content, conversation_id, role_type),
            media_type='text/event-stream'
        )
    except Exception as e:
        print(f"Error processing chat message: {e}")
        # Return empty stream if parsing fails
        return StreamingResponse(
            iter([b'']),
            media_type='text/event-stream'
        )

@router.get("/chat/{conversation_id}/history")
async def get_chat_history(
    conversation_id: str,
    chat_service: ChatService = Depends(get_chat_service)
) -> List[Message]:
    """获取聊天历史"""
    return await chat_service.get_chat_history(conversation_id)
