from pydantic import BaseModel

class ConversationCreate(BaseModel):
    role_type: str = "default"
