from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TrackingLogEntry(BaseModel):
    status: str  # "Order Placed", "Processing", "In Transit", "Delivered"
    location: Optional[str] = None
    timestamp: datetime = datetime.utcnow()
    note: Optional[str] = None
    updated_by: Optional[str] = "System" # "System", "Admin", "Agent"

class TrackingLog(BaseModel):
    tracking_id: str
    order_id: Optional[str] = None # Link to BuyerRequest or Offer
    logs: List[TrackingLogEntry] = []
    current_status: str = "Order Placed"
    estimated_delivery: Optional[datetime] = None
    
    # Metadata for Public View (Confidential info stripped in API response)
    recipient_city: Optional[str] = None 
    origin_city: Optional[str] = None
