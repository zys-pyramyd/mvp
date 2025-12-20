import uuid
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field

class Comment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    username: str
    user_avatar: Optional[str] = None
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    replies: List['Comment'] = []  # Nested comments

class Like(BaseModel):
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Post(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    community_id: str
    user_id: str
    username: str
    user_role: Optional[str] = None # 'admin', 'creator', etc.
    user_avatar: Optional[str] = None
    content: str
    images: List[str] = [] # URLs to R2 images
    type: str = "regular" # 'regular' or 'product'
    
    # Product details (only if type='product')
    product_price: Optional[float] = None
    product_name: Optional[str] = None
    quantity_available: Optional[int] = None
    unit: Optional[str] = None # kg, bag, etc.
    is_available: bool = True
    
    likes: List[str] = [] # List of user_ids who liked
    comments: List[Comment] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Community(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    creator_id: str
    banner_image: Optional[str] = None
    members: List[str] = [] # List of user_ids
    created_at: datetime = Field(default_factory=datetime.utcnow)
