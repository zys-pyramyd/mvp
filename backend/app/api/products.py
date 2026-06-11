
from fastapi import APIRouter, HTTPException, Depends, status
from app.api.deps import get_db, get_current_user
from app.models.product import Product, ProductCreate
from app.models.community import CommunityProductComment
from app.models.common import ProductCategory, PreOrderStatus
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.utils.sanitize import sanitize_regex

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
    city: Optional[str] = None,
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
                products_query["location"] = {"$regex": sanitize_regex(location), "$options": "i"}
                
            if city:
                products_query["city"] = {"$regex": sanitize_regex(city), "$options": "i"}
                
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
                    # Home page: Only business products
                    products_query["seller_type"] = {"$in": ["business"]}
                elif platform == "farm_deals":
                    # Farm Deals page: Only farmer and agent products
                    products_query["seller_type"] = {"$in": ["farmer", "agent"]}
                
            if search_term:
                words = [w.strip() for w in search_term.split() if w.strip()]
                if words:
                    word_queries = []
                    for word in words:
                        safe_word = sanitize_regex(word)
                        word_queries.append({
                            "$or": [
                                {"title": {"$regex": safe_word, "$options": "i"}},
                                {"description": {"$regex": safe_word, "$options": "i"}},
                                {"category": {"$regex": safe_word, "$options": "i"}},
                                {"subcategory": {"$regex": safe_word, "$options": "i"}},
                                {"location": {"$regex": safe_word, "$options": "i"}},
                                {"farm_name": {"$regex": safe_word, "$options": "i"}},
                                {"business_name": {"$regex": safe_word, "$options": "i"}}
                            ]
                        })
                    products_query["$and"] = word_queries
            
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
            results["total_count"] = db.products.count_documents(products_query)
        
        results["total_pages"] = (results["total_count"] + limit - 1) // limit
        
        return results
        
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error getting products: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get products")


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
        product_platform = 'farm_deals'
    elif user_role == 'business':
        # Businesses can list Farm Inputs, Food, etc. across platforms (PyExpress or PyHub)
        # We respect the platform sent from the frontend, default to pyexpress
        product_platform = product_data.platform or 'pyexpress'
            
    elif user_role == 'agent':
        # Agents can list on behalf of farmers effectively
        product_platform = 'farm_deals'
    
    # Enforce Pre-order Role Restrictions
    if product_data.is_preorder:
        # Enforce that only Farmers, Agents, and Businesses can create pre-orders.
        # Since 'processor' is removed, we just need to ensure the allowed roles are respected.
        # The current implementation restricts based on logic.
        # If user_role is 'personal' (buyer), they likely shouldn't be creating pre-orders either unless they are selling?
        # Assuming the standard checks pass.
        pass
        
    # Community Product Logic
    db = get_db()
    if product_data.community_id:
        product_platform = 'community'
        # Verify user is member of community
        member = db.community_members.find_one({
            "community_id": product_data.community_id,
            "user_id": current_user['id']
        })
        if not member:
            raise HTTPException(status_code=403, detail="You must be a member of the community to list products there")
            
        # Restrict to Admins/Creators or members with can_post flag
        if member.get('role') not in ['admin', 'creator', 'moderator'] and not member.get('can_post'):
             raise HTTPException(status_code=403, detail="Only community admins or approved members can list products")
            
        # Optional: Fetch community name for denormalization
        community = db.communities.find_one({"id": product_data.community_id})
        community_name = community.get('name') if community else None
    else:
        community_name = None
    
    # --- Agent Farmer Lookup Logic ---
    seller_id = current_user['id']
    seller_name = current_user['username']
    seller_type = current_user.get('role')
    seller_profile_picture = current_user.get('profile_picture')
    seller_is_verified = current_user.get('is_verified', False)
    business_name = current_user.get('business_name')
    agent_id = None
    agent_name = None
    agent_profile_picture = None
    listed_by_agent = False
    
    if user_role == 'agent' and product_data.farmer_identifier:
        # Agent is listing on behalf of a farmer
        farmer = db.users.find_one({
            "role": "farmer",
            "agent_id": current_user['id'],
            "$or": [
                {"phone": product_data.farmer_identifier},
                {"email": product_data.farmer_identifier},
                {"username": product_data.farmer_identifier}
            ]
        })
        
        if not farmer:
            raise HTTPException(status_code=404, detail="Farmer not found or not managed by you")
            
        # Assign Seller to Farmer, Link Agent
        seller_id = farmer.get('id') or str(farmer.get('_id'))
        seller_name = farmer.get('username')
        seller_type = "farmer"
        seller_profile_picture = farmer.get('profile_picture')
        seller_is_verified = farmer.get('is_verified', False)
        business_name = farmer.get('business_name')
        agent_id = current_user['id']
        agent_name = current_user['username']
        agent_profile_picture = current_user.get('profile_picture')
        listed_by_agent = True
        
        # --- PHASE 4: Overwrite Payout Details With Farmer's Verifiable Bank Info ---
        farmer_bank = farmer.get('bank_details', {})
        if farmer_bank and farmer_bank.get('account_number'):
            product_data.payout_account_number = farmer_bank.get('account_number')
            product_data.payout_bank_code = farmer_bank.get('bank_code')
            product_data.payout_account_name = farmer_bank.get('account_name')

    product_dict_payload = product_data.dict()
    product_dict_payload.pop('platform', None)
    product_dict_payload.pop('farmer_identifier', None)

    # Create product with seller profile picture
    product = Product(
        seller_id=seller_id,
        seller_name=seller_name,
        seller_type=seller_type,
        seller_profile_picture=seller_profile_picture,
        seller_is_verified=seller_is_verified,
        community_name=community_name,
        business_name=business_name,
        platform=product_platform,
        listed_by_agent=listed_by_agent,
        agent_id=agent_id,
        agent_name=agent_name,
        agent_profile_picture=agent_profile_picture,
        **product_dict_payload
    )
    
    # Apply service charges based on role
    if current_user.get('role') == 'farmer':
        product.price_per_unit = product_data.price_per_unit * 1.30
    elif current_user.get('role') == 'business':
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

@router.get("/{product_id}/delivery-options")
async def get_product_delivery_options(product_id: str):
    """Get delivery options for a specific product"""
    db = get_db()
    try:
        product = db.products.find_one({"id": product_id}) or db.preorders.find_one({"id": product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        delivery_options = {
            "product_id": product_id,
            "supports_dropoff_delivery": product.get("supports_dropoff_delivery", True),
            "supports_shipping_delivery": product.get("supports_shipping_delivery", True),
            "delivery_costs": {
                "dropoff": {
                    "cost": product.get("delivery_cost_dropoff", 0.0),
                    "is_free": product.get("delivery_cost_dropoff", 0.0) == 0.0
                },
                "shipping": {
                    "cost": product.get("delivery_cost_shipping", 0.0),
                    "is_free": product.get("delivery_cost_shipping", 0.0) == 0.0
                }
            },
            "delivery_notes": product.get("delivery_notes")
        }
        
        return delivery_options
        
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error getting delivery options: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get delivery options")

@router.put("/{product_id}/delivery-options")
async def update_product_delivery_options(
    product_id: str,
    delivery_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update delivery options for a product (suppliers only)"""
    db = get_db()
    try:
        # Check if product exists and user owns it
        product = db.products.find_one({"id": product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        if product.get("seller_id") != current_user["id"]:
            raise HTTPException(status_code=403, detail="You can only update delivery options for your own products")
        
        # Validate at least one delivery method is supported
        supports_dropoff = delivery_data.get("supports_dropoff_delivery", True)
        supports_shipping = delivery_data.get("supports_shipping_delivery", True)
        
        if not supports_dropoff and not supports_shipping:
            raise HTTPException(status_code=400, detail="At least one delivery method must be supported")
        
        # Update product delivery options
        from datetime import datetime
        update_data = {
            "supports_dropoff_delivery": supports_dropoff,
            "supports_shipping_delivery": supports_shipping,
            "delivery_cost_dropoff": max(0.0, delivery_data.get("delivery_cost_dropoff", 0.0)),
            "delivery_cost_shipping": max(0.0, delivery_data.get("delivery_cost_shipping", 0.0)),
            "delivery_notes": delivery_data.get("delivery_notes", "").strip() or None,
            "updated_at": datetime.utcnow()
        }
        
        db.products.update_one({"id": product_id}, {"$set": update_data})
        
        return {"message": "Delivery options updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error updating delivery options: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update delivery options")

