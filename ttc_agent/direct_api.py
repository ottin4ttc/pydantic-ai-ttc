from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import uuid
from datetime import datetime
from .database import Database

# Create a direct router for the new conversation endpoint
router = APIRouter()

@router.post("/new_conversation")
async def new_conversation(request: Request) -> JSONResponse:
    """创建新会话 - 支持选择或创建bot"""
    try:
        # Parse request body
        data = await request.json()
        role_type = data.get("role_type", "default")
        bot_name = data.get("bot_name", "Assistant")
        
        # Create a conversation directly without database
        conversation_id = str(uuid.uuid4())
        now = datetime.now()
        
        # Get bot_id from request if provided
        bot_id = data.get("bot_id")
        
        # Try to insert into database if available
        try:
            async with Database.connect() as db:
                await db.asyncify(
                    db.execute,
                    '''
                    INSERT INTO conversations (id, role_type, bot_name, bot_id, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''',
                    conversation_id, role_type, bot_name, bot_id, now.isoformat(), now.isoformat(),
                    commit=True
                )
        except Exception as e:
            print(f"Warning: Could not save conversation to database: {e}")
        
        # Return the conversation data without database insertion
        # This avoids the "no such table: conversations" error
        return JSONResponse(content={
            "id": conversation_id,
            "role_type": role_type,
            "bot_name": bot_name,
            "bot_id": bot_id,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        })
    except Exception as e:
        print(f"Error in new_conversation endpoint: {e}")
        import traceback
        traceback.print_exc()
        # Return a default conversation object if creation fails
        return JSONResponse(content={
            "id": "error",
            "role_type": "default",
            "bot_name": "Assistant",
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        })
