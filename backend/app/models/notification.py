from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from typing import Optional

class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    message: str
    type: str = "system"  # kyc, order, system, promotion
    is_read: bool = False
    action_link: Optional[str] = None  # Deep link or route
    created_at: datetime = Field(default_factory=datetime.utcnow)
