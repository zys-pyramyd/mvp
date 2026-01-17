from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str
    recipient_id: str
    content: Optional[str] = None
    attachments: Optional[List[str]] = [] # List of R2 keys
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MessageCreate(BaseModel):
    recipient_username: str
    content: Optional[str] = None
    attachments: Optional[List[str]] = []
