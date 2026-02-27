
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid
from app.models.common import ProductCategory, ProcessingLevel, RatingType

class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    seller_id: str
    seller_name: str
    seller_type: Optional[str] = None  # "farmer", "agent", "business", "supplier"
    seller_profile_picture: Optional[str] = None  # Seller's profile picture for transparency
    title: str
    description: str
    # Enhanced category structure
    category: ProductCategory
    subcategory: Optional[str] = None  # Dynamic based on category
    processing_level: ProcessingLevel = ProcessingLevel.NOT_PROCESSED
    price_per_unit: float
    original_price: Optional[float] = None  # Original price before discount
    # Discount system
    has_discount: bool = False
    discount_type: Optional[str] = None  # "percentage" or "fixed"
    discount_value: Optional[float] = None  # Percentage (e.g., 10 for 10%) or fixed amount (e.g., 500)
    discount_amount: Optional[float] = None  # Calculated discount amount in currency
    unit_of_measure: str  # kg, basket, crate, bag, gallon, etc.
    unit_specification: Optional[str] = None  # "100kg", "big", "5 litres", etc.
    quantity_available: int
    minimum_order_quantity: int = 1
    location: str
    colors: Optional[List[str]] = []
    farm_name: Optional[str] = None
    listed_by_agent: bool = False
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    agent_profile_picture: Optional[str] = None  # Agent's profile picture for transparency
    business_name: Optional[str] = None  # Business name for transparency
    images: List[str] = []
    platform: str  # "pyhub" or "pyexpress"
    # Community logic
    community_id: Optional[str] = None
    community_name: Optional[str] = None
    # Logistics Management
    logistics_managed_by: str = "pyramyd"  # "pyramyd" or "seller"
    seller_delivery_fee: Optional[float] = None  # If seller manages logistics, their delivery fee (0 = free)
    # Enhanced delivery options for suppliers
    supports_dropoff_delivery: bool = True  # Whether supplier accepts drop-off locations
    supports_shipping_delivery: bool = True  # Whether supplier accepts shipping addresses
    delivery_cost_dropoff: float = 0.0  # Cost for drop-off delivery (0.0 = free)
    delivery_cost_shipping: float = 0.0  # Cost for shipping delivery (0.0 = free)
    delivery_notes: Optional[str] = None  # Special delivery instructions/notes
    # Rating information
    average_rating: float = 5.0  # Product rating
    total_ratings: int = 0  # Number of product ratings
    
    # Pre-order fields
    is_preorder: bool = False
    preorder_available_date: Optional[datetime] = None
    preorder_end_date: Optional[datetime] = None
    
    preorder_target_quantity: Optional[int] = None # Target goal for pre-orders
    
    # About product (detailed description)
    about_product: Optional[str] = None  # Long-form description
    product_benefits: Optional[List[str]] = []
    usage_instructions: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ProductCreate(BaseModel):
    title: str
    description: str
    # Enhanced category structure
    category: ProductCategory
    subcategory: Optional[str] = None  # Dynamic based on category
    processing_level: ProcessingLevel = ProcessingLevel.NOT_PROCESSED
    price_per_unit: float
    # Discount options
    has_discount: bool = False
    discount_type: Optional[str] = None  # "percentage" or "fixed"
    discount_value: Optional[float] = None  # Percentage (e.g., 10 for 10%) or fixed amount (e.g., 500)
    unit_of_measure: str
    unit_specification: Optional[str] = None  # "100kg", "big", "5 litres", etc.
    quantity_available: int
    minimum_order_quantity: int = 1
    location: str
    colors: Optional[List[str]] = []
    farm_name: Optional[str] = None
    images: List[str] = []
    platform: str = "pyhub"
    # Community logic
    community_id: Optional[str] = None
    # Logistics Management
    logistics_managed_by: str = "pyramyd"  # "pyramyd" or "seller"
    seller_delivery_fee: Optional[float] = None  # If seller manages logistics
    # Enhanced delivery options for suppliers
    supports_dropoff_delivery: bool = True  # Whether supplier accepts drop-off locations  
    supports_shipping_delivery: bool = True  # Whether supplier accepts shipping addresses
    delivery_cost_dropoff: float = 0.0  # Cost for drop-off delivery (0.0 = free)
    delivery_cost_shipping: float = 0.0  # Cost for shipping delivery (0.0 = free)
    delivery_notes: Optional[str] = None  # Special delivery instructions/notes
    
    # Pre-order fields
    is_preorder: bool = False
    preorder_available_date: Optional[datetime] = None
    preorder_end_date: Optional[datetime] = None
    
    preorder_target_quantity: Optional[int] = None
    
    # About product
    about_product: Optional[str] = None
    product_benefits: Optional[List[str]] = []
    usage_instructions: Optional[str] = None

class CartItem(BaseModel):
    product_id: str
    quantity: int

class Rating(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rating_type: RatingType
    rating_value: int = Field(..., ge=1, le=5)  # 1-5 star rating
    rater_username: str  # Who gave the rating
    rater_id: str
    rated_entity_id: str  # ID of user, product, driver being rated
    rated_entity_username: Optional[str] = None  # Username if rating a user/driver
    order_id: Optional[str] = None  # Associated order if applicable
    comment: Optional[str] = None  # Optional review comment
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class RatingCreate(BaseModel):
    rating_type: RatingType
    rating_value: int = Field(..., ge=1, le=5)
    rated_entity_id: str
    rated_entity_username: Optional[str] = None
    order_id: Optional[str] = None
    comment: Optional[str] = None

class RatingResponse(BaseModel):
    id: str
    rating_type: RatingType
    rating_value: int
    rater_username: str
    rated_entity_id: str
    rated_entity_username: Optional[str] = None
    comment: Optional[str] = None
    created_at: datetime
