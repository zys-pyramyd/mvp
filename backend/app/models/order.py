
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import uuid
from app.models.common import OrderStatus, DeliveryStatus, PreOrderStatus, ProductCategory

class QuantityUnit(BaseModel):
    unit: str
    specification: Optional[str] = None
    
    @validator('unit')
    def validate_unit(cls, v):
        allowed_units = ['kg', 'g', 'ton', 'pieces', 'liters', 'bags', 'crates', 'gallons']
        if v not in allowed_units:
            raise ValueError(f'Unit must be one of: {", ".join(allowed_units)}')
        return v

class Order(BaseModel):
    id: Optional[str] = None
    order_id: str
    buyer_username: str
    seller_username: str
    product_details: dict
    quantity: float
    unit: str
    unit_specification: Optional[str] = None  # e.g., "100kg" for bags, "5 litres" for gallons
    unit_price: float
    total_amount: float
    delivery_method: str = "dropoff"  # "platform", "offline", or "dropoff"
    delivery_status: str = "pending"  # For offline deliveries
    shipping_address: Optional[str] = None  # Traditional shipping address (optional when using dropoff)
    dropoff_location_id: Optional[str] = None  # ID of selected drop-off location
    dropoff_location_details: Optional[dict] = None  # Snapshot of drop-off location info
    agent_fee_percentage: float = 0.05  # Updated agent fee (5%)
    payment_timing: str = "after_delivery"  # "after_delivery" for offline, "during_transit" for platform
    status: OrderStatus = OrderStatus.PENDING
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

class OrderCreate(BaseModel):
    product_id: str
    quantity: float
    unit: str
    unit_specification: Optional[str] = None
    shipping_address: Optional[str] = None  # Optional when using drop-off
    delivery_method: str = "dropoff"  # "platform", "offline", or "dropoff"
    dropoff_location_id: Optional[str] = None  # Required when delivery_method is "dropoff"
    
    @validator('dropoff_location_id')
    def validate_dropoff_location(cls, v, values):
        delivery_method = values.get('delivery_method')
        if delivery_method == 'dropoff' and not v:
            raise ValueError('Drop-off location is required when using drop-off delivery method')
        return v
    
class OrderStatusUpdate(BaseModel):
    order_id: str
    status: OrderStatus
    delivery_status: Optional[str] = None  # For offline deliveries

class DeliveryRequest(BaseModel):
    id: Optional[str] = None
    order_id: str  # References order or pre-order
    order_type: str  # "regular" or "preorder"
    requester_username: str  # Agent, farmer, or supplier requesting delivery
    pickup_location: dict  # {"lat": float, "lng": float, "address": str}
    delivery_locations: List[dict] = []  # Multiple destinations support
    total_quantity: float
    quantity_unit: str  # "kg", "pieces", etc.
    distance_km: float
    estimated_price: float
    negotiated_price: Optional[float] = None
    product_details: str
    weight_kg: Optional[float] = None
    special_instructions: Optional[str] = None
    assigned_driver_id: Optional[str] = None
    preferred_driver_id: Optional[str] = None  # For driver search and selection
    status: DeliveryStatus = DeliveryStatus.PENDING
    delivery_otp: Optional[str] = None
    chat_messages: List[dict] = []  # Messaging between requester and driver
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class DeliveryMessage(BaseModel):
    id: Optional[str] = None
    delivery_request_id: str
    sender_username: str
    sender_type: str  # "requester" or "driver"
    message_type: str  # "text", "location", "image"
    content: str
    location_data: Optional[dict] = None  # For location sharing
    timestamp: Optional[datetime] = None

class DeliveryRequestCreate(BaseModel):
    order_id: str
    order_type: str
    pickup_address: str
    pickup_coordinates: Optional[dict] = None  # {"lat": float, "lng": float}
    delivery_addresses: List[str]  # Multiple delivery addresses
    delivery_coordinates: Optional[List[dict]] = []  # Coordinates for each delivery address
    total_quantity: float
    quantity_unit: str
    product_details: str
    weight_kg: Optional[float] = None
    special_instructions: Optional[str] = None
    estimated_price: float
    preferred_driver_username: Optional[str] = None  # For driver selection

class PreOrder(BaseModel):
    id: Optional[str] = None
    seller_username: str
    seller_type: str  # farmer, supplier, processor
    business_name: str
    farm_name: Optional[str] = None
    agent_username: Optional[str] = None  # If published by agent
    product_name: str
    product_category: ProductCategory
    description: str
    total_stock: int
    available_stock: int
    unit: str  # kg, pieces, tons, etc.
    price_per_unit: float
    partial_payment_percentage: float  # 0.1 to 0.9 (10% to 90%)
    location: str
    delivery_date: datetime  # When product will be available
    images: List[str] = []
    status: PreOrderStatus = PreOrderStatus.DRAFT
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    orders_count: int = 0  # Number of pre-orders placed
    total_ordered_quantity: int = 0

class PreOrderCreate(BaseModel):
    product_name: str
    product_category: ProductCategory
    description: str
    total_stock: int
    unit: str
    price_per_unit: float
    partial_payment_percentage: float
    location: str
    delivery_date: datetime
    business_name: str
    farm_name: Optional[str] = None
    images: List[str] = []
    
    @validator('partial_payment_percentage')
    def validate_percentage(cls, v):
        if not 0.1 <= v <= 0.9:
            raise ValueError('Partial payment percentage must be between 10% and 90%')
        return v
    
    @validator('total_stock')
    def validate_stock(cls, v):
        if v <= 0:
            raise ValueError('Total stock must be greater than 0')
        return v
    
    @validator('price_per_unit')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price per unit must be greater than 0')
        return v

class PreOrderFilter(BaseModel):
    category: Optional[ProductCategory] = None
    location: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    delivery_date_from: Optional[datetime] = None
    delivery_date_to: Optional[datetime] = None
    only_preorders: Optional[bool] = None
    search_term: Optional[str] = None
    seller_type: Optional[str] = None  # farmer, supplier, processor

class DropoffLocation(BaseModel):
    id: Optional[str] = None
    name: str
    address: str
    city: str
    state: str
    country: str = "Nigeria"
    coordinates: Optional[dict] = None  # {"lat": float, "lng": float}
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    operating_hours: Optional[str] = None
    description: Optional[str] = None
    agent_username: str  # Agent who added this location
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class DropoffLocationCreate(BaseModel):
    name: str
    address: str
    city: str
    state: str
    country: str = "Nigeria"
    coordinates: Optional[dict] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    operating_hours: Optional[str] = None
    description: Optional[str] = None
    
    @validator('name')
    def validate_name(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Location name must be at least 3 characters long')
        return v.strip()
    
    @validator('address')
    def validate_address(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('Address must be at least 5 characters long')
        return v.strip()

class DropoffLocationUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    coordinates: Optional[dict] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    operating_hours: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
