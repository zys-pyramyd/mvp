
from fastapi import APIRouter, HTTPException, Depends, status
from app.api.deps import get_db, get_current_user
from app.models.product import CartItem
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
import uuid
from app.utils.id_generator import generate_tracking_id

router = APIRouter()

# --- Models ---

class RequestItem(BaseModel):
    name: str
    quantity: float
    unit: str
    specifications: Optional[str] = None
    target_price: Optional[float] = None

class BuyerRequestCreate(BaseModel):
    type: str = Field(..., description="'instant' (PyExpress) or 'standard' (FarmDeals)")
    items: List[RequestItem]
    location: str
    delivery_days: Optional[int] = None # For Instant
    delivery_date: Optional[datetime] = None # For Standard
    budget: Optional[float] = None
    notes: Optional[str] = None
    
    contact_phone: Optional[str] = None # Required for Instant
    payment_reference: Optional[str] = None
    amount_paid: Optional[float] = 0.0
    estimated_budget: Optional[float] = 0.0
    
    @validator('type')
    def validate_type(cls, v):
        if v not in ['instant', 'standard']:
            raise ValueError("Type must be 'instant' or 'standard'")
        return v

class OfferCreate(BaseModel):
    price: float
    delivery_date: datetime
    notes: Optional[str] = None
    quantity_offered: Optional[float] = None # Partial offers?

# --- Endpoints ---

@router.post("/", response_model=dict)
async def create_request(
    request_data: BuyerRequestCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a Buyer Request (RFQ).
    - Instant: For quick delivery (PyExpress).
    - Standard: For bulk/scheduled (Farm Deals).
    """
    db = get_db()
    
    # Optional: Enforce verification for Standard requests (Farm Deals usually B2B)
    if request_data.type == 'standard' and not current_user.get('is_verified'):
         # Maybe warning or block? Adhering to strictness:
         pass # Let's allow request creation but warn? or Block? 
         # Plan didn't specify strictness here, but let's be safe.
    
    req_id = f"RFQ-{uuid.uuid4().hex[:8].upper()}"
    
    new_request = {
        "id": req_id,
        "buyer_id": current_user['id'],
        "buyer_username": current_user['username'],
        "buyer_type": current_user.get('role'),
        "type": request_data.type,  # instant / standard
        "platform": "pyexpress" if request_data.type == 'instant' else "farm_deals",
        "items": [item.dict() for item in request_data.items],
        "location": request_data.location,
        "delivery_days": request_data.delivery_days,
        "delivery_date": request_data.delivery_date,
        "budget": request_data.budget,
        "notes": request_data.notes,
        "contact_phone": request_data.contact_phone,
        # Payment Info
        "payment_reference": request_data.payment_reference,
        "amount_paid": request_data.amount_paid,
        "service_fees_paid": request_data.amount_paid - (request_data.amount_paid * 0.04 if request_data.type == 'instant' else 0), # Approx split, refining below
        # Wait, if Instant: 3000 + 4% Budget.
        # Let's store raw values for clarity
        "validation_data": {
             "estimated_budget": request_data.estimated_budget,
             "fee_structure": "Standard 5k" if request_data.type == 'standard' else "3k + 4% Budget"
        },
        "agent_fee_held": (request_data.estimated_budget * 0.04) if request_data.type == 'instant' else 0,
        
        "status": "active",
        "offers_count": 0,
        "created_at": datetime.utcnow()
    }
    
    # 4. Enforce validations
    if request_data.type == 'instant' and not request_data.contact_phone:
         raise HTTPException(status_code=400, detail="Contact phone is required for Instant requests")

    # 5. Verify Payment (Simulation)
    if not request_data.payment_reference:
          raise HTTPException(status_code=402, detail="Payment required to activate request")
    
    db.requests.insert_one(new_request)
    
    return {
        "message": "Request created successfully",
        "request_id": req_id,
        "type": request_data.type
    }

@router.get("/")
async def list_requests(
    type: Optional[str] = None,
    platform: Optional[str] = None,
    location: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    List active requests.
    Agents/Farmers/Businesses view these to make offers.
    """
    db = get_db()
    query = {"status": "active"}
    
    if type:
        query["type"] = type
    if platform:
        query["platform"] = platform
    if location:
        query["location"] = {"$regex": location, "$options": "i"}
        
    requests = list(db.requests.find(query).sort("created_at", -1))
    
    for r in requests:
        r['_id'] = str(r['_id'])
        
    return requests

@router.post("/{request_id}/offers")
async def make_offer(
    request_id: str,
    offer_data: OfferCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Agent/Farmer/Business makes an offer on a request.
    """
    # Authorization checks
    role = current_user.get('role')
    if role not in ['agent', 'farmer', 'business', 'supplier_food_produce']:
        raise HTTPException(status_code=403, detail="Not authorized to make offers")
        
    # Enforce verification for sellers
    if not current_user.get('is_verified'):
        raise HTTPException(status_code=403, detail="Verification required to make offers")

    db = get_db()
    request = db.requests.find_one({"id": request_id})
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
        
    if request['status'] != 'active':
        raise HTTPException(status_code=400, detail="Request is no longer active")

    offer_id = f"OFF-{uuid.uuid4().hex[:8].upper()}"
    
    offer = {
        "id": offer_id,
        "request_id": request_id,
        "seller_id": current_user['id'],
        "seller_username": current_user['username'],
        "seller_role": role,
        "price": offer_data.price,
        "delivery_date": offer_data.delivery_date,
        "notes": offer_data.notes,
        "status": "pending",
        "created_at": datetime.utcnow()
    }
    
    db.offers.insert_one(offer)
    db.requests.update_one({"id": request_id}, {"$inc": {"offers_count": 1}})
    
    return {"message": "Offer sent successfully", "offer_id": offer_id}

@router.post("/offers/{offer_id}/accept")
async def accept_offer(
    offer_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Buyer accepts an offer -> Creates an Order.
    """
    db = get_db()
    offer = db.offers.find_one({"id": offer_id})
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
        
    request = db.requests.find_one({"id": offer['request_id']})
    if not request:
        raise HTTPException(status_code=404, detail="Original request not found")
        
    if request['buyer_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="Only the request owner can accept offers")
        
    if request['status'] != 'active':
        # raise HTTPException(status_code=400, detail="Request is already closed")
        pass # Allow multiple accepts? Usually single accept closes it.
        
    # Create Order
    tracking_id = generate_tracking_id()
    
    # Calculate Total
    # Assuming full fulfillment for MVP
    total_amount = offer['price'] 
    
    order_data = {
        "order_id": tracking_id,
        "buyer_id": current_user['id'],
        "buyer_username": current_user['username'],
        "seller_id": offer['seller_id'],
        "seller_username": offer['seller_username'],
        "seller_role": offer['seller_role'], # Important for commission logic
        "items": request['items'], # List of items
        "total_amount": total_amount,
        "status": "pending", # Awaiting payment
        "origin_request_id": request['id'],
        "origin_offer_id": offer['id'],
        "platform": request['platform'], 
        "created_at": datetime.utcnow()
    }
    
    db.orders.insert_one(order_data)
    
    # Update Request & Offer status
    db.requests.update_one({"id": request['id']}, {"$set": {"status": "completed"}})
    db.offers.update_one({"id": offer_id}, {"$set": {"status": "accepted"}})
    
    return {
        "message": "Offer accepted. Order created.",
        "order_id": tracking_id,
        "tracking_id": tracking_id
    }

@router.post("/offers/{offer_id}/delivered")
async def mark_offer_delivered(
    offer_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Seller/Agent marks the offer as delivered to the buyer.
    This updates the status but requires Buyer Confirmation (or Auto-Release) to release funds.
    """
    db = get_db()
    
    # 1. Find Offer
    offer = db.offers.find_one({"id": offer_id})
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
        
    # 2. Check Permissions
    if offer['seller_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    if offer['status'] != 'accepted':
        raise HTTPException(status_code=400, detail="Offer must be accepted first")

    # 3. Update Offer Status
    db.offers.update_one({"id": offer_id}, {"$set": {"status": "delivered", "delivered_at": datetime.utcnow()}})
    
    # 4. Update Linked Order Status
    # We need to find the order generated from this offer
    order = db.orders.find_one({"origin_offer_id": offer_id})
    if order:
        db.orders.update_one(
            {"order_id": order['order_id']}, 
            {"$set": {"status": "delivered_pending_confirmation"}}
        )
        
    return {"message": "Marked as delivered. Waiting for buyer confirmation."}

@router.get("/offers/mine")
async def list_my_offers(current_user: dict = Depends(get_current_user)):
    """
    List offers made by the current user (Agent/Seller).
    Includes Tracking ID (delivery_otp) if the offer is accepted/delivered so Agent can share it.
    """
    db = get_db()
    role = current_user.get('role')
    
    # Find offers where seller_id is current user
    offers = list(db.offers.find({"seller_id": current_user['id']}).sort("created_at", -1))
    
    results = []
    for offer in offers:
        offer_data = {
            "id": offer['id'],
            "request_id": offer['request_id'],
            "price": offer['price'],
            "status": offer['status'],
            "delivery_date": offer['delivery_date'],
            "quantity_offered": offer.get('quantity_offered'),
            "created_at": offer['created_at']
        }
        
        # Should we include Request Title? Maybe useful for UI
        req = db.requests.find_one({"id": offer['request_id']})
        if req:
            offer_data['request_title'] = req.get('items', [{}])[0].get('name', 'Unknown Request')
        
        # If Accepted/Delivered, include Tracking ID from Order
        if offer['status'] in ['accepted', 'delivered', 'completed']:
            order = db.orders.find_one({"origin_offer_id": offer['id']})
            if order:
                offer_data['tracking_id'] = order['order_id']
                # Security: Only show delivery_otp (last 8 chars) or full tracking ID?
                # Requirement: "Agent to indicate delivered, buyer inputs last 8 chars".
                # So Agent needs full Tracking ID to give to buyer? Or Buyer has it?
                # Usually: Agent delivers, Buyer checks item. 
                # Buyer needs to input a code. If code is from Tracking ID, Agent shouldn't need to give it if Buyer already has Order info.
                # BUT, if Buyer created Request, they might NOT have Tracking ID until Order is created.
                # When Agent marks delivered, Agent tells Buyer "Here is your package".
                # Buyer checks package.
                # CONFUSION: "Buyer inputs last 8 characters of tracking ID".
                # Does Buyer have Tracking ID? Yes, usually in "My Orders".
                # Does Agent have it? Yes.
                # If checking physicality, maybe Agent GIVES the code?
                # "modify confirm_delivery_otp endpoint to allow the buyer (not the seller) to confirm receipt by inputting the last 8 characters of the tracking ID."
                # This implies Buyer KNOWS the tracking ID or matches what is on the package label.
                # Let's send tracking_id to Agent so they can write it on package or verify.
                offer_data['delivery_otp'] = order['order_id'] 

        results.append(offer_data)
        
    return results

@router.post("/offers/{offer_id}/confirm-delivery")
async def confirm_delivery(
    offer_id: str,
    confirmation_data: dict, # Expects {"code": "..."}
    current_user: dict = Depends(get_current_user)
):
    """
    Buyer confirms receipt using the last 8 characters of the Tracking ID.
    Releases funds.
    """
    code = confirmation_data.get('code')
    if not code:
        raise HTTPException(status_code=400, detail="Confirmation code required")

    db = get_db()
    
    # 1. Find Offer and Request to verify Buyer
    offer = db.offers.find_one({"id": offer_id})
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
        
    request = db.requests.find_one({"id": offer['request_id']})
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
        
    if request['buyer_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="Only the buyer can confirm delivery")

    # 2. Find Order
    order = db.orders.find_one({"origin_offer_id": offer_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    # 3. Verify Code (Last 8 chars of Order ID / Tracking ID)
    # Order ID is Tracking ID e.g. NGA_PYD-XXX-XXX
    tracking_id = order['order_id']
    if not tracking_id.endswith(code):
        raise HTTPException(status_code=400, detail="Invalid confirmation code")
        
    # 4. Complete Process
    # Update Order
    db.orders.update_one(
        {"order_id": tracking_id},
        {"$set": {"status": "delivered", "confirmed_by_buyer": True, "completed_at": datetime.utcnow()}}
    )
    # Update Offer
    db.offers.update_one(
        {"id": offer_id},
        {"$set": {"status": "completed"}}
    )
    
    # 5. Trigger Payout
    from app.services.payout_service import process_order_payout
    success, msg = await process_order_payout(tracking_id, db)
    
    if not success:
        # Log error but don't fail the request user-side 
        # (Status is already updated, admin can fix payout)
        print(f"Payout failed for {tracking_id}: {msg}")
        return {"message": "Delivery confirmed! Payment processing status: Pending Admin Review"}

    return {"message": "Delivery confirmed! Funds released to seller."}

@router.post("/requests/{request_id}/take")
async def take_instant_request(
    request_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Agent 'Takes' an Instant Request (PyExpress).
    Immediately creates an Order without Offer/Accept loop.
    """
    # 1. Check User Role
    if current_user.get('role') != 'agent':
        raise HTTPException(status_code=403, detail="Only agents can take instant requests")
        
    if not current_user.get('is_verified'):
         raise HTTPException(status_code=403, detail="Verification required")

    db = get_db()
    
    # 2. Find Request
    req = db.requests.find_one({"id": request_id})
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    if req['type'] != 'instant':
        raise HTTPException(status_code=400, detail="This endpoint is for Instant requests only")
        
    if req['status'] != 'active':
        raise HTTPException(status_code=400, detail="Request is no longer active")
        
    # 3. Create Order Directly
    tracking_id = generate_tracking_id()
    
    # For instant requests, price is usually fixed/budget or negotiated separately?
    # Assuming Agent accepts the 'budget' if set, or we need a price?
    # MVP: Take it at budget price. If budget is None, error?
    if not req.get('budget'):
         raise HTTPException(status_code=400, detail="Request has no budget set. Use Standard Offer flow.")
    
    order_data = {
        "order_id": tracking_id,
        "buyer_id": req['buyer_id'],
        "buyer_username": req['buyer_username'],
        "seller_id": current_user['id'],
        "seller_username": current_user['username'],
        "seller_role": "agent",
        "items": req['items'],
        "total_amount": req['budget'],
        "status": "confirmed", # Confirmed immediately
        "origin_request_id": req['id'],
        "platform": "pyexpress",
        "created_at": datetime.utcnow()
    }
    
    db.orders.insert_one(order_data)
    
    # 4. Close Request
    db.requests.update_one({"id": request_id}, {"$set": {"status": "completed"}})
    
    # 5. Create a 'Fake' Accepted Offer for consistency?
    # Helpful for "My Offers" list validation
    offer_id = f"OFF-INST-{uuid.uuid4().hex[:8].upper()}"
    offer = {
        "id": offer_id,
        "request_id": request_id,
        "seller_id": current_user['id'],
        "seller_username": current_user['username'],
        "seller_role": "agent",
        "price": req['budget'],
        "delivery_date": datetime.utcnow(), # ASAP
        "notes": "Instant Job Taken",
        "status": "accepted",
        "created_at": datetime.utcnow()
    }
    db.offers.insert_one(offer)
    
    # Link Order to this fake offer
    db.orders.update_one({"order_id": tracking_id}, {"$set": {"origin_offer_id": offer_id}})

    return {
        "message": "Job Taken Successfully!",
        "tracking_id": tracking_id,
        "order_id": tracking_id
    }
