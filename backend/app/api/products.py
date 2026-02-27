
from fastapi import APIRouter, HTTPException, Depends, status
from app.api.deps import get_db, get_current_user
from app.models.product import Product, ProductCreate
from app.models.community import CommunityProductComment
from app.models.common import ProductCategory, PreOrderStatus
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)
from datetime import datetime

router = APIRouter()

@router.get("/recent-prices")
async def get_recent_prices(name: str):
    """
    Get recent prices for a product by name.
    Returns average price from recent completed orders.
    Used for price estimation in instant requests.
    """
    db = get_db()
    
    # Search in completed orders for price history
    recent_orders = list(db.orders.find({
        "status": {"$in": ["completed", "delivered"]},
        "items.title": {"$regex": name, "$options": "i"}
    }).sort("created_at", -1).limit(20))
    
    prices = []
    for order in recent_orders:
        for item in order.get("items", []):
            if name.lower() in item.get("title", "").lower():
                price = item.get("price_per_unit", 0)
                if price > 0:
                    prices.append(price)
    
    # Also check recent products
    recent_products = list(db.products.find({
        "title": {"$regex": name, "$options": "i"},
        "price_per_unit": {"$gt": 0}
    }).sort("created_at", -1).limit(10))
    
    for product in recent_products:
        prices.append(product.get("price_per_unit", 0))
    
    if prices:
        avg_price = sum(prices) / len(prices)
        return {
            "product_name": name,
            "average_price": round(avg_price, 2),
            "sample_count": len(prices),
            "price_range": {
                "min": round(min(prices), 2),
                "max": round(max(prices), 2)
            },
            "status": "available"
        }
    
    return {
        "product_name": name,
        "average_price": None,
        "sample_count": 0,
        "message": "No recent price data available",
        "status": "unavailable"
    }

@router.get("/")
async def get_products(
    category: Optional[str] = None,
    location: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    only_preorders: Optional[bool] = None,
    search_term: Optional[str] = None,
    seller_type: Optional[str] = None,
    platform: Optional[str] = None,  # 'home' or 'farm_deals'
    global_search: Optional[bool] = None,  # Search across all platforms
    page: int = 1,
    limit: int = 20
):
    """Get products with advanced filtering"""
    db = get_db()
    try:
        results = {"products": [], "preorders": [], "total_count": 0, "page": page, "limit": limit}
        
        # Regular products query
        if not only_preorders:
            products_query = {}
            
            if category:
                products_query["category"] = category
                
            if location:
                products_query["location"] = {"$regex": location, "$options": "i"}
                
            if min_price is not None or max_price is not None:
                price_filter = {}
                if min_price is not None:
                    price_filter["$gte"] = min_price
                if max_price is not None:
                    price_filter["$lte"] = max_price
                products_query["price_per_unit"] = price_filter
                
                
                
            if seller_type:
                products_query["seller_type"] = seller_type
            
            # Platform-based filtering (skip if global search)
            if not global_search:
                if platform == "home":
                    # Home page: Only business and supplier products
                    products_query["seller_type"] = {"$in": ["business", "supplier"]}
                elif platform == "farm_deals":
                    # Farm Deals page: Only farmer and agent products
                    products_query["seller_type"] = {"$in": ["farmer", "agent"]}
                
            if search_term:
                products_query["$or"] = [
                    {"crop_type": {"$regex": search_term, "$options": "i"}},
                    {"location": {"$regex": search_term, "$options": "i"}},
                    {"farm_name": {"$regex": search_term, "$options": "i"}}
                ]
            
            # Get products
            skip = (page - 1) * limit
            products = list(db.products.find(products_query).sort("created_at", -1).skip(skip).limit(limit))
            
            # Clean up products
            for product in products:
                product["_id"] = str(product["_id"])
                if "created_at" in product and isinstance(product["created_at"], datetime):
                    product["created_at"] = product["created_at"].isoformat()
                product["type"] = "regular"
            
            results["products"] = products
            results["total_count"] += db.products.count_documents(products_query)
        
        # Pre-orders query (if not filtering out pre-orders)
        if only_preorders or only_preorders is None:
            preorders_query = {"status": PreOrderStatus.PUBLISHED}
            
            if category:
                preorders_query["product_category"] = category
                
            if location:
                preorders_query["location"] = {"$regex": location, "$options": "i"}
                
            if min_price is not None or max_price is not None:
                price_filter = {}
                if min_price is not None:
                    price_filter["$gte"] = min_price
                if max_price is not None:
                    price_filter["$lte"] = max_price
                preorders_query["price_per_unit"] = price_filter
                
            if search_term:
                preorders_query["$or"] = [
                    {"product_name": {"$regex": search_term, "$options": "i"}},
                    {"description": {"$regex": search_term, "$options": "i"}},
                    {"business_name": {"$regex": search_term, "$options": "i"}},
                    {"farm_name": {"$regex": search_term, "$options": "i"}}
                ]
                
            if seller_type:
                preorders_query["seller_type"] = seller_type
            
            # Platform-based filtering for preorders (skip if global search)
            if not global_search:
                if platform == "home":
                    # Home page: Only business and supplier preorders
                    preorders_query["seller_type"] = {"$in": ["business", "supplier"]}
                elif platform == "farm_deals":
                    # Farm Deals page: Only farmer and agent preorders
                    preorders_query["seller_type"] = {"$in": ["farmer", "agent"]}
            
            # Get pre-orders with improved pagination logic
            skip = (page - 1) * limit if only_preorders else 0
            
            # Fix: Ensure pre-orders get a fair share of the response, not just leftovers
            if only_preorders:
                limit_preorders = limit
            else:
                # Allow pre-orders alongside products - increase effective limit or reserve space
                max_products_for_mixed = max(1, int(limit * 0.75))  # Reserve 75% for products, 25% for pre-orders  
                if len(results["products"]) > max_products_for_mixed:
                    # Trim products to make space for pre-orders
                    results["products"] = results["products"][:max_products_for_mixed]
                
                limit_preorders = limit - len(results["products"])
                limit_preorders = max(limit_preorders, int(limit * 0.25))  # Always allow at least 25% for pre-orders
            
            if limit_preorders > 0:
                preorders = list(db.preorders.find(preorders_query).sort("created_at", -1).skip(skip).limit(limit_preorders))
                
                # Clean up pre-orders
                for preorder in preorders:
                    preorder.pop('_id', None)
                    if "created_at" in preorder and isinstance(preorder["created_at"], datetime):
                        preorder["created_at"] = preorder["created_at"].isoformat()
                    if "updated_at" in preorder and isinstance(preorder["updated_at"], datetime):
                        preorder["updated_at"] = preorder["updated_at"].isoformat()
                    if "delivery_date" in preorder and isinstance(preorder["delivery_date"], datetime):
                        preorder["delivery_date"] = preorder["delivery_date"].isoformat()
                    preorder["type"] = "preorder"
                
                results["preorders"] = preorders
                results["total_count"] += db.preorders.count_documents(preorders_query)
        
        results["total_pages"] = (results["total_count"] + limit - 1) // limit
        
        return results
        
    except Exception as e:
        print(f"Error getting products: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get products")

@router.get("/categories")
async def get_categories():
    return [{"value": cat.value, "label": cat.value.replace("_", " ").title()} for cat in ProductCategory]

@router.post("/")
async def create_product(product_data: ProductCreate, current_user: dict = Depends(get_current_user)):
    if not current_user.get('role'):
        raise HTTPException(status_code=400, detail="Please select a role first")
    
    # Check if user can create products
    allowed_roles = ['farmer', 'agent', 'business']
    if current_user.get('role') not in allowed_roles:
        raise HTTPException(status_code=403, detail="Not authorized to create products")
        
    # Enforce Verification
    if not current_user.get('is_verified'):
         raise HTTPException(
            status_code=403, 
            detail="Account not verified. Please complete KYC or contact support to list products."
        )
    
    # Determine platform based on user role and product category
    user_role = current_user.get('role')
    product_platform = product_data.platform
    
    # Enforce platform restrictions
    if user_role == 'farmer':
        product_platform = 'pyhub'
    elif user_role == 'business':
        # Businesses can list Farm Inputs, Food, etc. across platforms (PyExpress or PyHub)
        # We respect the platform sent from the frontend, default to pyexpress
        product_platform = product_data.platform or 'pyexpress'
            
    elif user_role == 'agent':
        # Agents can list on behalf of farmers effectively
        product_platform = 'pyhub'
    
    # Enforce Pre-order Role Restrictions
    if product_data.is_preorder:
        # Enforce that only Farmers, Agents, and Businesses can create pre-orders.
        # Since 'processor' is removed, we just need to ensure the allowed roles are respected.
        # The current implementation restricts based on logic.
        # If user_role is 'personal' (buyer), they likely shouldn't be creating pre-orders either unless they are selling?
        # Assuming the standard checks pass.
        pass
        
    # Community Product Logic
    if product_data.community_id:
        product_platform = 'community'
        # Verify user is member of community
        member = db.community_members.find_one({
            "community_id": product_data.community_id,
            "user_id": current_user['id']
        })
        if not member:
            raise HTTPException(status_code=403, detail="You must be a member of the community to list products there")
            
        # Restrict to Admins/Creators only
        if member.get('role') not in ['admin', 'creator']:
             raise HTTPException(status_code=403, detail="Only community admins can list products")
            
        # Optional: Fetch community name for denormalization
        community = db.communities.find_one({"id": product_data.community_id})
        community_name = community.get('name') if community else None
    else:
        community_name = None
    
    db = get_db()
    
    # Create product with seller profile picture
    product = Product(
        seller_id=current_user['id'],
        seller_name=current_user['username'],
        seller_type=current_user.get('role'),
        seller_profile_picture=current_user.get('profile_picture'),  # Include seller's profile picture
        seller_is_verified=current_user.get('is_verified', False),  # Verified status
        community_name=community_name, # Community Name
        business_name=current_user.get('business_name'),  # Include business name for transparency
        platform=product_platform,
        **{k: v for k, v in product_data.dict().items() if k != 'platform'}
    )
    
    # Apply service charges based on role
    if current_user.get('role') == 'farmer':
        product.price_per_unit = product_data.price_per_unit * 1.30
    elif current_user.get('role') in ['supplier_food_produce', 'processor']:
        product.price_per_unit = product_data.price_per_unit * 0.90
    
    # Calculate discount if applicable
    if product_data.has_discount and product_data.discount_value:
        product.original_price = product.price_per_unit
        
        if product_data.discount_type == "percentage":
            discount_amount = product.price_per_unit * (product_data.discount_value / 100)
            product.discount_amount = round(discount_amount, 2)
            product.price_per_unit = round(product.price_per_unit - discount_amount, 2)
        elif product_data.discount_type == "fixed":
            product.discount_amount = product_data.discount_value
            product.price_per_unit = round(product.price_per_unit - product_data.discount_value, 2)
            
        if product.price_per_unit < 0:
            raise HTTPException(status_code=400, detail="Discount cannot exceed product price")
    
    # Validate logistics management
    if product_data.logistics_managed_by == "seller":
        if product_data.seller_delivery_fee is None:
            raise HTTPException(status_code=400, detail="Delivery fee is required when seller manages logistics")
    
    product_dict = product.dict()
    db.products.insert_one(product_dict)
    
    return {"message": "Product created successfully", "product_id": product.id}

@router.get("/{product_id}")
async def get_product(product_id: str):
    db = get_db()
    product = db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.pop('_id', None)
    product.pop('_id', None)
    return product

@router.put("/{product_id}/preorder-time")
async def update_preorder_time(
    product_id: str,
    time_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update pre-order availability time"""
    if "available_date" not in time_data:
         raise HTTPException(status_code=400, detail="available_date is required")

    db = get_db()
    product = db.products.find_one({"id": product_id, "seller_id": current_user["id"]})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or not owned by you")
    
    # Convert strings to datetime if necessary (simplified handling)
    avail_date = time_data.get("available_date")
    end_date = time_data.get("end_date")
    
    # Update
    db.products.update_one(
        {"id": product_id},
        {"$set": {
            "is_preorder": True,
            "preorder_available_date": avail_date,
            "preorder_end_date": end_date,
            "preorder_target_quantity": time_data.get("target_quantity"), # New Field
            # Also update about fields if passed
            "about_product": time_data.get("about_product"),
            "product_benefits": time_data.get("product_benefits", []),
            "usage_instructions": time_data.get("usage_instructions")
        }}
    )
    
    
    return {"message": "Pre-order settings updated"}

@router.post("/{product_id}/comments")
async def create_product_comment(
    product_id: str,
    comment_data: CommentCreate,
    current_user: dict = Depends(get_current_user)
):
    """Comment on a product offering"""
    db = get_db()
    
    # Verify product exists
    product = db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
    comment = CommunityProductComment(
        product_id=product_id,
        user_id=current_user['id'],
        username=current_user['username'],
        comment=comment_data.content
    )
    
    db.product_comments.insert_one(comment.dict())
    
    # Update comment count on product (optional but good for UI)
    db.products.update_one(
        {"id": product_id},
        {"$inc": {"comments_count": 1}}
    )
    
    return comment

@router.get("/{product_id}/comments")
async def get_product_comments(product_id: str, limit: int = 20):
    """Get comments for a product"""
    db = get_db()
    comments = list(db.product_comments.find({"product_id": product_id})
                   .sort("created_at", -1)
                   .limit(limit))
    
    for c in comments:
        c.pop("_id", None)
    return comments
