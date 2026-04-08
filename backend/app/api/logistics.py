# Auto-extracted Router
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.api.deps import get_db, get_current_user
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
import random
import string

from app.models.common import DeliveryStatus
from app.models.order import DeliveryRequestCreate

router = APIRouter()

@router.post("/api/delivery/request")
async def create_delivery_request(request_data:DeliveryRequestCreate, current_user: dict = Depends(get_current_user)):
    """Create a delivery request"""
    db = get_db()
    try:
        # Validate user can request delivery
        allowed_roles = ['agent', 'farmer', 'supplier', 'processor']
        if current_user.get('role') not in allowed_roles:
            raise HTTPException(status_code=403, detail="Only sellers can request delivery")
        
        # Calculate distance (simplified - in real app would use maps API)
        import random
        distance_km = random.uniform(5.0, 50.0)  # Mock distance
        
        # Generate OTP
        import random
        otp = str(random.randint(100000, 999999))
        
        # Prepare pickup coordinates
        pickup_lat = request_data.pickup_coordinates.get("lat", 0.0) if request_data.pickup_coordinates else 0.0
        pickup_lng = request_data.pickup_coordinates.get("lng", 0.0) if request_data.pickup_coordinates else 0.0

        # Prepare delivery locations
        delivery_locations = []
        for i, addr in enumerate(request_data.delivery_addresses):
            lat = 0.0
            lng = 0.0
            if request_data.delivery_coordinates and i < len(request_data.delivery_coordinates):
                lat = request_data.delivery_coordinates[i].get("lat", 0.0)
                lng = request_data.delivery_coordinates[i].get("lng", 0.0)
            
            delivery_locations.append({
                "address": addr,
                "lat": lat,
                "lng": lng
            })

        # Create delivery request
        delivery_request = {
            "id": str(uuid.uuid4()),
            "order_id": request_data.order_id,
            "order_type": request_data.order_type,
            "requester_username": current_user["username"],
            "pickup_location": {
                "address": request_data.pickup_address,
                "lat": pickup_lat,
                "lng": pickup_lng
            },
            "delivery_locations": delivery_locations,
            "total_quantity": request_data.total_quantity,
            "quantity_unit": request_data.quantity_unit,
            "distance_km": distance_km,
            "estimated_price": request_data.estimated_price,
            "product_details": request_data.product_details,
            "weight_kg": request_data.weight_kg,
            "special_instructions": request_data.special_instructions,
            "status": DeliveryStatus.PENDING,
            "delivery_otp": otp,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Store in database
        db.delivery_requests.insert_one(delivery_request)
        
        # Send Delivery OTP to buyer via ZeptoMail
        try:
            buyer = db.users.find_one({"username": current_user["username"]})
            if buyer and buyer.get("email"):
                from app.utils.email import send_zeptomail
                otp_html = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333;">
                    <h2 style="color: #059669;">Delivery PIN Code</h2>
                    <p style="font-size: 16px;">Hello {buyer.get('first_name', 'Valued Customer')},</p>
                    <p style="font-size: 16px;">Your delivery has been successfully requested. Please provide the following PIN to your driver ONLY upon receiving your goods:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <span style="display: inline-block; padding: 12px 24px; background-color: #f3f4f6; color: #000; border: 1px dashed #059669; font-size: 24px; letter-spacing: 5px; font-weight: bold;">{otp}</span>
                    </div>
                    <p style="font-size: 14px; font-weight: bold; color: #dc2626;">Do NOT share this code before inspecting your items.</p>
                </div>
                """
                send_zeptomail(
                    to_email=buyer["email"],
                    subject="Your Pyramyd Delivery PIN",
                    html_content=otp_html,
                    to_name=buyer.get("first_name", "Customer")
                )
        except Exception as e:
            print(f"Failed to send ZeptoMail OTP: {e}")
            
        return {
            "message": "Delivery request created successfully",
            "request_id": delivery_request["id"],
            "estimated_price": request_data.estimated_price,
            "distance_km": distance_km,
            "delivery_otp": otp
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating delivery request: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create delivery request")

@router.post("/api/delivery/{request_id}/complete")
async def complete_delivery(request_id:str, otp: str, current_user: dict = Depends(get_current_user)):
    """Complete delivery with OTP verification"""
    db = get_db()
    try:
        # Find delivery request
        delivery_request = db.delivery_requests.find_one({"id": request_id})
        if not delivery_request:
            raise HTTPException(status_code=404, detail="Delivery request not found")
        
        # Verify OTP
        if delivery_request["delivery_otp"] != otp:
            raise HTTPException(status_code=400, detail="Invalid OTP")
        
        # Require the request to be confirmed by buyer or authorized user if needed
        # We removed the driver check and simply fulfill the delivery request
        
        # Update delivery request
        db.delivery_requests.update_one(
            {"id": request_id},
            {
                "$set": {
                    "status": DeliveryStatus.DELIVERED,
                    "completed_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "message": "Delivery completed successfully",
            "request_id": request_id,
            "completed_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error completing delivery: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to complete delivery")

@router.post("/api/delivery/calculate-fee")
async def calculate_delivery_fee_endpoint(
    product_total:float,
    buyer_state: str,
    product_id: Optional[str] = None
):
    """
    Calculate delivery fee with smart logic:
    1. Vendor logistics (if managed by seller)
    2. Kwik Delivery (for Lagos, Oyo, FCT Abuja)
    3. 20% rule (for other states)
    """
    db = get_db()
    try:
        product_data = None
        
        # Get product details if product_id provided
        if product_id:
            product = db.products.find_one({"id": product_id})
            if product:
                product_data = {
                    'logistics_managed_by': product.get('logistics_managed_by', 'pyramyd'),
                    'seller_delivery_fee': product.get('seller_delivery_fee', 0.0)
                }
        
        # Calculate delivery fee
        delivery_info = calculate_delivery_fee(product_total, buyer_state, product_data)
        
        return {
            "success": True,
            "delivery_fee": delivery_info['delivery_fee'],
            "delivery_method": delivery_info['delivery_method'],
            "kwik_available": delivery_info.get('kwik_available', False),
            "vendor_managed": delivery_info.get('vendor_managed', False),
            "is_free_delivery": delivery_info.get('is_free', False),
            "buyer_state": buyer_state,
            "details": delivery_info
        }
        
    except Exception as e:
        print(f"Error calculating delivery fee: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate delivery fee")

@router.post("/api/delivery/kwik/create")
async def create_kwik_delivery_endpoint(
    order_id:str,
    pickup_address: dict,
    delivery_address: dict,
    current_user: dict = Depends(get_current_user)
):
    """Create a Kwik delivery request for an order"""
    db = get_db()
    try:
        # Get order details
        order = db.orders.find_one({"order_id": order_id})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Prepare order details for Kwik
        order_details = {
            'seller_name': order.get('seller_username', 'Pyramyd Vendor'),
            'buyer_name': current_user.get('username', ''),
            'buyer_phone': current_user.get('phone', ''),
            'order_id': order_id,
            'description': f"Order {order_id} - {order.get('product_details', {}).get('product_name', 'Product')}",
            'amount': order.get('total_amount', 0)
        }
        
        # Create Kwik delivery
        kwik_result = create_kwik_delivery(pickup_address, delivery_address, order_details)
        
        if kwik_result:
            # Save Kwik delivery info
            kwik_delivery_doc = {
                "id": str(uuid.uuid4()),
                "community_id": community_id,
                "user_id": target_user["id"],
                "username": target_user["username"],
                "role": "member",
                "joined_at": datetime.utcnow().isoformat(),
                "is_active": True
            }
            community_members_collection.insert_one(new_member)

        # Update count
        count = community_members_collection.count_documents({"community_id": community_id, "is_active": True})
        communities_collection.update_one({"id": community_id}, {"$set": {"member_count": count}})

        return {"message": "Member added successfully"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error adding member: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add member")

@router.get("/api/delivery/kwik/track/{kwik_delivery_id}")
async def track_kwik_delivery(kwik_delivery_id: str):
    """Track a Kwik delivery"""
    db = get_db()
    try:
        # Get tracking info from Kwik API
        tracking_info = kwik_request("GET", f"/deliveries/{kwik_delivery_id}")
        
        if tracking_info:
            # Update local delivery status
            kwik_deliveries_collection.update_one(
                {"kwik_delivery_id": kwik_delivery_id},
                {"$set": {
                    "status": tracking_info.get('status', 'unknown'),
                    "last_updated": datetime.utcnow()
                }}
            )
            
            return {
                "success": True,
                "tracking_info": tracking_info
            }
        else:
            raise HTTPException(status_code=404, detail="Tracking information not available")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error tracking Kwik delivery: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to track delivery")

