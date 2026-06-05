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
        allowed_roles = ['agent', 'farmer', 'business']
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


