import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class CartItem(BaseModel):
    product_id: str
    quantity: int

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    buyer_id: str
    buyer_name: str
    seller_id: str
    seller_name: str
    items: List[dict]
    total_amount: float
    delivery_address: str
    status: str = "pending"
    payment_status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class AgentPurchaseOption(BaseModel):
    commission_type: str
    customer_id: str
    delivery_address: str

class GroupBuyingRequest(BaseModel):
    produce: str
    category: str
    quantity: int
    location: str

class GroupOrder(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    produce: str
    category: str
    location: str
    total_quantity: int
    buyers: List[dict]
    selected_farm: dict
    commission_type: str
    total_amount: float
    agent_commission: float
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class OutsourcedOrder(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    requester_id: str
    produce: str
    category: str
    quantity: int
    expected_price: float
    location: str
    status: str = "open"
    accepting_agent_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
