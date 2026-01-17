
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid
from app.models.common import CommunityRole, CommunityPrivacy

class Community(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    creator_id: str
    creator_username: str
    profile_picture: Optional[str] = None  # Community profile picture
    privacy: CommunityPrivacy = CommunityPrivacy.PUBLIC
    category: str  # e.g., "farming", "business", "trading"
    location: Optional[str] = None  # Community focus location
    cover_image: Optional[str] = None
    member_count: int = 0
    product_count: int = 0
    is_active: bool = True
    community_rules: Optional[List[str]] = []
    tags: Optional[List[str]] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CommunityMember(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    community_id: str
    user_id: str
    username: str
    role: CommunityRole = CommunityRole.MEMBER
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    invited_by: Optional[str] = None  # User ID who invited this member
    is_active: bool = True

class CommunityProduct(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    community_id: str
    community_name: str  # For easier display
    title: str
    description: str
    price: float
    quantity_available: int
    unit_of_measure: str
    category: str
    images: List[str] = []
    seller_id: str
    seller_username: str
    location: str
    is_active: bool = True
    likes_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    group_buy_enabled: bool = False
    group_buy_min_quantity: Optional[int] = None
    group_buy_participants: List[str] = []  # User IDs in group buy
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CommunityProductLike(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    user_id: str
    username: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CommunityProductComment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    user_id: str
    username: str
    comment: str
    reply_to: Optional[str] = None  # ID of comment being replied to
    created_at: datetime = Field(default_factory=datetime.utcnow)

class GroupBuyParticipant(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product_id: str
    user_id: str
    username: str
    quantity_requested: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FarmlandRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    farmer_id: str
    location: str  # Farmland location
    size_hectares: float
    crop_types: List[str]  # Types of crops grown
    soil_type: Optional[str] = None
    irrigation_method: Optional[str] = None
    coordinates: Optional[dict] = None  # GPS coordinates
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class AgentFarmer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    farmer_id: str
    farmer_name: str
    farmer_phone: Optional[str] = None
    farmer_location: str
    linked_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    total_listings: int = 0
    total_sales: float = 0.0
