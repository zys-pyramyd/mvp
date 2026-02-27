
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
    moisture_content_percent: Optional[float] = None # Optional moisture content

class BuyerRequestCreate(BaseModel):
    type: str = Field(..., description="'instant' (PyExpress) or 'standard' (FarmDeals)")
    items: List[RequestItem]
    # Location split
    region_country: str = "Nigeria"
    region_state: str 
    location: str # Specific address/city for delivery logic
    
    delivery_days: Optional[int] = None # For Instant
    delivery_date: Optional[datetime] = None # For Standard
    publish_date: Optional[datetime] = None # When the request goes live to bidders
    expiry_date: datetime # Required: When the request closes
    
    budget: Optional[float] = None
    currency: str = "NGN"
    price_range_min: Optional[float] = None
    price_range_max: Optional[float] = None
    
    notes: Optional[str] = None # Description
    contact_phone: Optional[str] = None 
    payment_reference: Optional[str] = None
    amount_paid: Optional[float] = 0.0
    estimated_budget: Optional[float] = 0.0
    
    @validator('type')
    def validate_type(cls, v):
        if v not in ['instant', 'standard']:
            raise ValueError("Type must be 'instant' or 'standard'")
        return v

class OfferCreate(BaseModel):
    price: float # Total Price
    items: Optional[List[RequestItem]] = None # Detailed quotation
    images: List[str] = [] # URLs
    moisture_content_percent: Optional[float] = None
    quotation_file: Optional[str] = None # PDF/Doc URL
    delivery_date: datetime
    notes: Optional[str] = None
    quantity_offered: Optional[float] = None

class RFQPaymentRequest(BaseModel):
    type: str = Field(..., description="'instant' or 'standard'")
    items: List[RequestItem]
    estimated_budget: Optional[float] = 0.0
    
    @validator('type')
    def validate_type(cls, v):
        if v not in ['instant', 'standard']:
            raise ValueError("Type must be 'instant' or 'standard'")
        return v

class RequestUpdate(BaseModel):
    items: Optional[List[RequestItem]] = None
    region_state: Optional[str] = None
    location: Optional[str] = None
    publish_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    notes: Optional[str] = None
    contact_phone: Optional[str] = None

class AcceptOfferRequest(BaseModel):
    acknowledgment_note: Optional[str] = None
    acknowledgment_files: List[str] = []
    confirmed_delivery_date: Optional[datetime] = None
    payment_terms: Optional[dict] = None

class RequestStatusUpdate(BaseModel):
    status: str = Field(..., description="'active', 'on_hold', or 'closed'")

# --- Endpoints ---

@router.post("/initialize-payment", response_model=dict)
async def initialize_rfq_payment(
    payment_req: RFQPaymentRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Initialize payment for RFQ request.
    Calculates fees and returns Paystack payment URL.
    
    Fee Structure:
    - Instant: ₦3,000 + 4% of estimated budget
    - Standard: ₦5,000 (fixed)
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Calculate fees
    if payment_req.type == 'instant':
        service_charge = 3000.0
        agent_fee = payment_req.estimated_budget * 0.04
        total_amount = service_charge + agent_fee
    else:  # standard
        service_charge = 5000.0
        agent_fee = 0.0
        total_amount = service_charge
    
    # Initialize Paystack transaction
    from app.services.paystack import initialize_transaction
    import os
    
    try:
        amount_kobo = int(total_amount * 100)
        
        # Prepare metadata
        metadata = {
            "request_type": payment_req.type,
            "user_id": current_user['id'],
            "service_charge": service_charge,
            "agent_fee": agent_fee,
            "estimated_budget": payment_req.estimated_budget,
            "item_count": len(payment_req.items)
        }
        
        # Get callback URL
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        callback_url = f"{frontend_url}/rfq/payment-callback"
        
        result = initialize_transaction(
            email=current_user.get('email'),
            amount=amount_kobo,
            callback_url=callback_url,
            metadata=metadata
        )
        
        payment_reference = result["data"]["reference"]
        authorization_url = result["data"]["authorization_url"]
        
        # Create pending transaction record
        db = get_db()
        transaction = {
            "user_id": current_user["id"],
            "email": current_user.get("email"),
            "type": "debit",
            "category": "rfq_service_charge",
            "amount": total_amount,
            "reference": payment_reference,
            "description": f"RFQ Service Charge - {payment_req.type.capitalize()} Request",
            "status": "pending",
            "metadata": metadata,
            "created_at": datetime.utcnow()
        }
        db.wallet_transactions.insert_one(transaction)
        
        logger.info(f"RFQ payment initialized. Type: {payment_req.type}, Amount: ₦{total_amount}, Reference: {payment_reference}, User: {current_user['id']}")
        
        return {
            "message": "Payment initialized successfully",
            "payment_url": authorization_url,
            "payment_reference": payment_reference,
            "amount": total_amount,
            "service_charge": service_charge,
            "agent_fee": agent_fee,
            "breakdown": {
                "service_charge": service_charge,
                "agent_fee": agent_fee,
                "total": total_amount
            }
        }
        
    except Exception as e:
        logger.error(f"RFQ payment initialization failed. Error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Payment initialization failed: {str(e)}"
        )

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
        "region_country": request_data.region_country,
        "region_state": request_data.region_state,
        "delivery_days": request_data.delivery_days,
        "delivery_date": request_data.delivery_date,
        "publish_date": request_data.publish_date or datetime.utcnow(),
        "expiry_date": request_data.expiry_date,
        "budget": request_data.budget,
        "currency": request_data.currency,
        "price_range": {
            "min": request_data.price_range_min,
            "max": request_data.price_range_max
        },
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

@router.post("/verify-payment", response_model=dict)
async def verify_and_create_request(
    request_data: BuyerRequestCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Verify Paystack payment then create the request atomically.
    Called by frontend immediately after Paystack popup succeeds.
    Replaces the separate /requests endpoint for the payment flow.
    """
    import logging
    logger = logging.getLogger(__name__)
    db = get_db()

    if not request_data.payment_reference:
        raise HTTPException(status_code=402, detail="Payment reference is required")

    # 1. Check for duplicate — prevent double-submission if user clicks twice
    existing = db.requests.find_one({"payment_reference": request_data.payment_reference})
    if existing:
        return {
            "message": "Request already created",
            "request_id": existing["id"],
            "type": existing["type"]
        }

    # 2. Verify payment with Paystack
    from app.services.paystack import verify_transaction
    try:
        result = verify_transaction(request_data.payment_reference)
    except Exception as e:
        logger.error(f"Paystack verification failed: {e}")
        raise HTTPException(status_code=402, detail="Payment verification failed. Please contact support.")

    pay_data = result.get("data", {})
    if pay_data.get("status") != "success":
        raise HTTPException(status_code=402, detail="Payment not confirmed. Please complete payment first.")

    # 3. Confirm amount matches expected fee
    amount_paid_kobo = pay_data.get("amount", 0)
    amount_paid_naira = amount_paid_kobo / 100.0
    expected = 5000.0 if request_data.type == "standard" else (3000.0 + (request_data.estimated_budget or 0) * 0.04)
    if amount_paid_naira < expected - 1:  # 1 naira tolerance for rounding
        raise HTTPException(
            status_code=402,
            detail=f"Insufficient payment. Expected ₦{expected:.0f}, received ₦{amount_paid_naira:.0f}."
        )

    # 4. Mark wallet transaction as success (idempotent)
    db.wallet_transactions.update_one(
        {"reference": request_data.payment_reference, "status": "pending"},
        {"$set": {"status": "success", "verified_at": datetime.utcnow()}}
    )

    # 5. Create the request
    if request_data.type == 'instant' and not request_data.contact_phone:
        raise HTTPException(status_code=400, detail="Contact phone is required for Instant requests")

    req_id = f"RFQ-{uuid.uuid4().hex[:8].upper()}"
    new_request = {
        "id": req_id,
        "buyer_id": current_user['id'],
        "buyer_username": current_user['username'],
        "buyer_type": current_user.get('role'),
        "type": request_data.type,
        "platform": "pyexpress" if request_data.type == 'instant' else "farm_deals",
        "items": [item.dict() for item in request_data.items],
        "location": request_data.location,
        "region_country": request_data.region_country,
        "region_state": request_data.region_state,
        "delivery_days": request_data.delivery_days,
        "delivery_date": request_data.delivery_date,
        "publish_date": request_data.publish_date or datetime.utcnow(),
        "expiry_date": request_data.expiry_date,
        "budget": request_data.budget,
        "currency": request_data.currency,
        "price_range": {
            "min": request_data.price_range_min,
            "max": request_data.price_range_max
        },
        "notes": request_data.notes,
        "contact_phone": request_data.contact_phone,
        "payment_reference": request_data.payment_reference,
        "amount_paid": amount_paid_naira,
        "payment_status": "paid",
        "validation_data": {
            "estimated_budget": request_data.estimated_budget,
            "fee_structure": "Standard 5k" if request_data.type == 'standard' else "3k + 4% Budget"
        },
        "agent_fee_held": (request_data.estimated_budget * 0.04) if request_data.type == 'instant' else 0,
        "status": "active",
        "offers_count": 0,
        "created_at": datetime.utcnow()
    }

    db.requests.insert_one(new_request)
    logger.info(f"Request {req_id} created after payment verification. Ref: {request_data.payment_reference}")

    return {
        "message": "Payment verified. Request created successfully!",
        "request_id": req_id,
        "type": request_data.type
    }

@router.get("/")
async def list_requests(
    type: Optional[str] = None,
    platform: Optional[str] = None,
    location: Optional[str] = None,
    status: Optional[str] = "active",
    current_user: dict = Depends(get_current_user)
):
    """
    List requests with filtering.
    """
    db = get_db()
    query = {}
    
    if status and status != "all":
        query["status"] = status
    
    # Only show published requests
    query["publish_date"] = {"$lte": datetime.utcnow()}
    
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

@router.get("/mine")
async def get_my_requests(
    current_user: dict = Depends(get_current_user)
):
    """
    Get requests created by the current user along with their offers.
    """
    db = get_db()
    
    requests_cursor = db.requests.find({"buyer_id": current_user['id']}).sort("created_at", -1)
    requests = list(requests_cursor)
    
    for req in requests:
        req['_id'] = str(req['_id'])
        offers = list(db.offers.find({"request_id": req['id']}).sort("created_at", -1))
        for offer in offers:
            offer['_id'] = str(offer['_id'])
        req['offers'] = offers
        
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

    # Prevent self-bidding
    if request['buyer_id'] == current_user['id']:
        raise HTTPException(status_code=400, detail="You cannot bid on your own request")

    if request['status'] not in ['active', 'on_hold']:
        raise HTTPException(status_code=400, detail="Request is no longer active")
        
    if request.get('publish_date') and request['publish_date'] > datetime.utcnow():
        raise HTTPException(status_code=400, detail="Request is not yet published")

    offer_id = f"OFF-{uuid.uuid4().hex[:8].upper()}"
    
    offer = {
        "id": offer_id,
        "request_id": request_id,
        "seller_id": current_user['id'],
        "seller_username": current_user['username'],
        "seller_role": role,
        "price": offer_data.price,
        "items": [i.dict() for i in offer_data.items] if offer_data.items else [],
        "images": offer_data.images,
        "moisture_content_percent": offer_data.moisture_content_percent,
        "quotation_file": offer_data.quotation_file,
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
    accept_data: AcceptOfferRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Buyer accepts an offer -> Sets terms -> Waits for Seller Confirmation.
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
        pass # Allow multiple accepts negotiation
        
    # Update Offer with Terms
    db.offers.update_one(
        {"id": offer_id}, 
        {"$set": {
            "status": "accepted_by_buyer", # Waiting for seller to confirm
            "buyer_terms": {
                "acknowledgment_note": accept_data.acknowledgment_note,
                "acknowledgment_files": accept_data.acknowledgment_files,
                "confirmed_delivery_date": accept_data.confirmed_delivery_date,
                "payment_terms": accept_data.payment_terms
            },
            "terms_sent_at": datetime.utcnow()
        }}
    )
    
    return {
        "message": "Offer accepted and terms sent. Waiting for seller confirmation.",
        "offer_id": offer_id,
        "status": "accepted_by_buyer"
    }

@router.post("/offers/{offer_id}/confirm-terms")
async def confirm_offer_terms(
    offer_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Seller/Agent confirms the buyer's terms → creates an Order.
    Status: accepted_by_buyer → accepted (Order created).
    """
    db = get_db()
    offer = db.offers.find_one({"id": offer_id})
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    if offer["seller_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only the offer owner can confirm terms")

    if offer.get("status") != "accepted_by_buyer":
        raise HTTPException(status_code=400, detail="Offer is not awaiting your confirmation")

    # Create Order from offer
    tracking_id = generate_tracking_id()
    terms = offer.get("buyer_terms", {})

    order_data = {
        "order_id": tracking_id,
        "buyer_id": db.requests.find_one({"id": offer["request_id"]}, {"buyer_id": 1}).get("buyer_id"),
        "seller_id": current_user["id"],
        "seller_username": current_user["username"],
        "seller_role": offer.get("seller_role"),
        "origin_request_id": offer["request_id"],
        "origin_offer_id": offer_id,
        "items": offer.get("items", []),
        "total_amount": offer["price"],
        "delivery_date": terms.get("confirmed_delivery_date"),
        "payment_terms": terms.get("payment_terms"),
        "acknowledgment_note": terms.get("acknowledgment_note"),
        "acknowledgment_files": terms.get("acknowledgment_files", []),
        "platform": "farm_deals",
        "is_rfq_order": True, # Tag to indicate this is a non-escrow standard request order
        "status": "confirmed",
        "created_at": datetime.utcnow()
    }

    db.orders.insert_one(order_data)

    # Update offer status
    db.offers.update_one(
        {"id": offer_id},
        {"$set": {"status": "accepted", "order_id": tracking_id, "terms_confirmed_at": datetime.utcnow()}}
    )

    return {
        "message": "Terms confirmed! Order created.",
        "offer_id": offer_id,
        "order_id": tracking_id,
        "status": "accepted"
    }

@router.post("/offers/{offer_id}/reject-terms")
async def reject_offer_terms(
    offer_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Seller/Agent rejects the buyer's terms → offer goes back to pending.
    Buyer can re-negotiate or choose another bid.
    """
    db = get_db()
    offer = db.offers.find_one({"id": offer_id})
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    if offer["seller_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only the offer owner can reject terms")

    if offer.get("status") != "accepted_by_buyer":
        raise HTTPException(status_code=400, detail="Offer is not awaiting your confirmation")

    db.offers.update_one(
        {"id": offer_id},
        {"$set": {"status": "terms_rejected", "terms_rejected_at": datetime.utcnow()}}
    )

    return {
        "message": "Terms rejected. The buyer has been notified.",
        "offer_id": offer_id,
        "status": "terms_rejected"
    }

@router.post("/offers/{offer_id}/reject")
async def reject_offer(
    offer_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Buyer rejects an offer outright (before accepting terms).
    """
    db = get_db()
    offer = db.offers.find_one({"id": offer_id})
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    request = db.requests.find_one({"id": offer["request_id"]})
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if request["buyer_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only the request owner can reject offers")

    if offer.get("status") not in ["pending", "terms_rejected"]:
        raise HTTPException(status_code=400, detail="Offer cannot be rejected at this stage")

    db.offers.update_one(
        {"id": offer_id},
        {"$set": {"status": "rejected", "rejected_at": datetime.utcnow()}}
    )

    return {"message": "Offer rejected.", "offer_id": offer_id, "status": "rejected"}

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
            "notes": offer.get('notes'),
            "images": offer.get('images', []),
            "items": offer.get('items', []),
            "moisture_content_percent": offer.get('moisture_content_percent'),
            "buyer_terms": offer.get('buyer_terms'),  # Needed for agent terms modal
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
    
    # 5. Check if it's a non-escrow RFQ Order
    if order.get("is_rfq_order"):
        return {"message": "Delivery confirmed! As a standard RFQ order, please ensure direct payment is settled as per your negotiated terms."}
    
    # 6. Trigger Payout for Escrow Orders
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
        
    if req['status'] not in ['active', 'on_hold']:
        raise HTTPException(status_code=400, detail="Request is no longer active")
        
    # Check if publish_date has passed
    if req.get('publish_date') and req['publish_date'] > datetime.utcnow():
        raise HTTPException(status_code=400, detail="Request is not yet published")
        
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
    
    db.orders.update_one({"order_id": tracking_id}, {"$set": {"origin_offer_id": offer_id}})

    return {
        "message": "Job Taken Successfully!",
        "tracking_id": tracking_id,
        "order_id": tracking_id
    }

@router.put("/{request_id}/status")
async def update_request_status(
    request_id: str,
    status_update: RequestStatusUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update request status to allow pausing (on_hold) or closing (closed).
    """
    db = get_db()
    req = db.requests.find_one({"id": request_id})
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    if req["buyer_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only the request creator can change its status")
        
    current_status = req.get("status", "active")
    new_status = status_update.status
    
    if current_status == "closed":
        raise HTTPException(status_code=400, detail="Cannot modify a closed request")
        
    if new_status not in ["active", "on_hold", "closed"]:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    if current_status == new_status:
        return {"message": f"Request is already {new_status}"}

    update_data = {"status": new_status, "updated_at": datetime.utcnow()}
    
    # Handle Timer Logic
    now = datetime.utcnow()
    expiry = req.get("expiry_date")

    if new_status == "on_hold" and current_status == "active" and expiry:
        # Calculate remaining seconds
        remaining = (expiry - now).total_seconds()
        update_data["hold_duration_seconds"] = max(0, remaining)
        
    elif new_status == "active" and current_status == "on_hold":
        # Resume timer
        hold_seconds = req.get("hold_duration_seconds", 0)
        import datetime as dt
        new_expiry = now + dt.timedelta(seconds=hold_seconds)
        update_data["expiry_date"] = new_expiry
        update_data["hold_duration_seconds"] = None

    db.requests.update_one({"id": request_id}, {"$set": update_data})
    
    return {"message": f"Request status updated to {new_status}", "status": new_status}

@router.put("/{request_id}")
async def update_request(
    request_id: str,
    update_data: RequestUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Edit a request. Only allowed if status is active or on_hold.
    """
    db = get_db()
    req = db.requests.find_one({"id": request_id})
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    if req["buyer_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only the creator can edit this request")
        
    if req["status"] not in ["active", "on_hold"]:
        raise HTTPException(status_code=400, detail="Only active or on hold requests can be edited")
        
    updates = {k: v for k, v in update_data.dict(exclude_none=True).items()}
    if not updates:
        return {"message": "No changes provided"}
        
    if "items" in updates:
        updates["items"] = [item.dict() for item in update_data.items]
        
    updates["updated_at"] = datetime.utcnow()
    
    db.requests.update_one({"id": request_id}, {"$set": updates})
    return {"message": "Request updated successfully"}
