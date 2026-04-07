# Auto-extracted Router
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.api.deps import get_db, get_current_user
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
import random
import string

router = APIRouter()

@router.post("/api/drivers/register-independent")
async def register_independent_driver(driver_data:DriverCreate, current_user: dict = Depends(get_current_user)):
    """Register as an independent driver"""
    db = get_db()
    try:
        # Validate user can register as driver
        if current_user.get('role') != 'driver':
            raise HTTPException(status_code=403, detail="Only users with driver role can register as independent drivers")
        
        # Check if user already has a driver profile
        existing_driver = db.drivers.find_one({"driver_username": current_user["username"]})
        if existing_driver:
            raise HTTPException(status_code=400, detail="Driver profile already exists")
        
        # Create driver document
        driver = {
            "id": str(uuid.uuid4()),
            "driver_username": current_user["username"],
            "driver_name": driver_data.driver_name,
            "phone_number": driver_data.phone_number,
            "email": driver_data.email,
            "profile_picture": driver_data.profile_picture,
            "driver_license": driver_data.driver_license,
            "status": DriverStatus.OFFLINE,
            "current_location": None,
            "rating": 5.0,
            "total_deliveries": 0,
            "is_independent": True,
            "logistics_business_id": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Create vehicle document
        vehicle = {
            "id": str(uuid.uuid4()),
            "driver_id": driver["id"],
            "vehicle_type": driver_data.vehicle_type,
            "plate_number": driver_data.plate_number,
            "make_model": driver_data.make_model,
            "color": driver_data.color,
            "year": driver_data.year,
            "created_at": datetime.utcnow()
        }
        
        # Store in database
        db.drivers.insert_one(driver)
        db.vehicles.insert_one(vehicle)
        
        return {"message": "Driver registered successfully", "driver_id": driver["id"]}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error registering independent driver: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to register driver")

@router.post("/api/logistics/add-driver")
async def add_driver_to_logistics(driver_data:DriverCreate, current_user: dict = Depends(get_current_user)):
    """Add a driver to logistics business dashboard"""
    db = get_db()
    try:
        # Validate user is logistics business
        if current_user.get('partner_type') != 'business' or current_user.get('business_category') != 'logistics_business':
            raise HTTPException(status_code=403, detail="Only logistics businesses can add managed drivers")
        
        # Get or create logistics business profile
        logistics_business = db.logistics_businesses.find_one({"business_username": current_user["username"]})
        if not logistics_business:
            # Create logistics business profile
            logistics_business = {
                "id": str(uuid.uuid4()),
                "business_username": current_user["username"],
                "business_name": current_user.get("business_info", {}).get("business_name", "Unknown Business"),
                "business_address": current_user.get("business_info", {}).get("business_address", ""),
                "phone_number": current_user.get("phone", ""),
                "email": current_user.get("email", ""),
                "cac_number": current_user.get("verification_info", {}).get("cac_number", ""),
                "drivers": [],
                "vehicles": [],
                "created_at": datetime.utcnow()
            }
            db.logistics_businesses.insert_one(logistics_business)
        
        # Create unique driver username
        driver_username = f"{current_user['username']}_driver_{len(logistics_business.get('drivers', [])) + 1}"
        
        # Create driver document
        driver = {
            "id": str(uuid.uuid4()),
            "driver_username": driver_username,
            "driver_name": driver_data.driver_name,
            "phone_number": driver_data.phone_number,
            "email": driver_data.email,
            "profile_picture": driver_data.profile_picture,
            "driver_license": driver_data.driver_license,
            "status": DriverStatus.OFFLINE,
            "current_location": None,
            "rating": 5.0,
            "total_deliveries": 0,
            "is_independent": False,
            "logistics_business_id": logistics_business["id"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Create vehicle document
        vehicle = {
            "id": str(uuid.uuid4()),
            "driver_id": driver["id"],
            "vehicle_type": driver_data.vehicle_type,
            "plate_number": driver_data.plate_number,
            "make_model": driver_data.make_model,
            "color": driver_data.color,
            "year": driver_data.year,
            "created_at": datetime.utcnow()
        }
        
        # Store in database
        db.drivers.insert_one(driver)
        db.vehicles.insert_one(vehicle)
        
        # Update logistics business
        db.logistics_businesses.update_one(
            {"id": logistics_business["id"]},
            {
                "$push": {
                    "drivers": driver["id"],
                    "vehicles": vehicle["id"]
                }
            }
        )
        
        return {
            "message": "Driver added successfully",
            "driver_id": driver["id"],
            "driver_username": driver_username,
            "driver_access_link": f"/driver-portal?token={driver['id']}"  # Link for driver to access portal
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error adding driver to logistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add driver")

@router.get("/api/logistics/my-drivers")
async def get_my_drivers(current_user:dict = Depends(get_current_user)):
    """Get all drivers managed by current logistics business"""
    db = get_db()
    try:
        # Get logistics business
        logistics_business = db.logistics_businesses.find_one({"business_username": current_user["username"]})
        if not logistics_business:
            return {"drivers": [], "vehicles": []}
        
        # Get drivers
        drivers = list(db.drivers.find({
            "logistics_business_id": logistics_business["id"]
        }))
        
        # Get vehicles
        vehicles = list(db.vehicles.find({
            "driver_id": {"$in": [driver["id"] for driver in drivers]}
        }))
        
        # Clean up response
        for driver in drivers:
            driver.pop('_id', None)
            if driver.get("created_at"):
                driver["created_at"] = driver["created_at"].isoformat()
            if driver.get("updated_at"):
                driver["updated_at"] = driver["updated_at"].isoformat()
        
        for vehicle in vehicles:
            vehicle.pop('_id', None)
            if vehicle.get("created_at"):
                vehicle["created_at"] = vehicle["created_at"].isoformat()
        
        return {"drivers": drivers, "vehicles": vehicles}
        
    except Exception as e:
        print(f"Error getting logistics drivers: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get drivers")

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

@router.get("/api/delivery/available")
async def get_available_deliveries(current_user:dict = Depends(get_current_user)):
    """Get available delivery requests for drivers"""
    db = get_db()
    try:
        # Check if user is a driver
        driver = db.drivers.find_one({"driver_username": current_user["username"]})
        if not driver:
            raise HTTPException(status_code=403, detail="Only registered drivers can view delivery requests")
        
        # Get pending delivery requests
        delivery_requests = list(db.delivery_requests.find({
            "status": DeliveryStatus.PENDING
        }).sort("created_at", -1))
        
        # Clean up response
        for request in delivery_requests:
            request.pop('_id', None)
            request["created_at"] = request["created_at"].isoformat()
            request["updated_at"] = request["updated_at"].isoformat()
            # Don't expose OTP to drivers until they accept
            request.pop('delivery_otp', None)
        
        return {"delivery_requests": delivery_requests}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting available deliveries: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get available deliveries")

@router.post("/api/delivery/{request_id}/accept")
async def accept_delivery_request(request_id:str, current_user: dict = Depends(get_current_user)):
    """Accept a delivery request"""
    db = get_db()
    try:
        # Check if user is a driver
        driver = db.drivers.find_one({"driver_username": current_user["username"]})
        if not driver:
            raise HTTPException(status_code=403, detail="Only registered drivers can accept deliveries")
        
        # Check if driver is available
        if driver["status"] in [DriverStatus.BUSY, DriverStatus.ON_DELIVERY]:
            raise HTTPException(status_code=400, detail="Driver is not available")
        
        # Find and update delivery request
        delivery_request = db.delivery_requests.find_one({"id": request_id})
        if not delivery_request:
            raise HTTPException(status_code=404, detail="Delivery request not found")
        
        if delivery_request["status"] != DeliveryStatus.PENDING:
            raise HTTPException(status_code=400, detail="Delivery request is no longer available")
        
        # Update delivery request
        db.delivery_requests.update_one(
            {"id": request_id},
            {
                "$set": {
                    "assigned_driver_id": driver["id"],
                    "status": DeliveryStatus.ACCEPTED,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Update driver status
        db.drivers.update_one(
            {"id": driver["id"]},
            {
                "$set": {
                    "status": DriverStatus.ON_DELIVERY,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "message": "Delivery request accepted",
            "request_id": request_id,
            "pickup_address": delivery_request["pickup_location"]["address"],
            "delivery_address": delivery_request["delivery_location"]["address"],
            "estimated_price": delivery_request["estimated_price"],
            "delivery_otp": delivery_request["delivery_otp"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error accepting delivery: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to accept delivery")

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
        
        # Check if user is authorized (buyer or the assigned driver)
        driver = db.drivers.find_one({"id": delivery_request.get("assigned_driver_id")})
        if current_user["username"] != driver.get("driver_username"):
            # Could be buyer/agent confirming - add additional validation here
            pass
        
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
        
        # Update driver status and stats
        if driver:
            db.drivers.update_one(
                {"id": driver["id"]},
                {
                    "$set": {
                        "status": DriverStatus.ONLINE,
                        "updated_at": datetime.utcnow()
                    },
                    "$inc": {"total_deliveries": 1}
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

@router.post("/api/delivery/{request_id}/negotiate")
async def negotiate_delivery_price(request_id:str, proposed_price: float, current_user: dict = Depends(get_current_user)):
    """Negotiate delivery price"""
    db = get_db()
    try:
        # Check if user is a driver
        driver = db.drivers.find_one({"driver_username": current_user["username"]})
        if not driver:
            raise HTTPException(status_code=403, detail="Only registered drivers can negotiate prices")
        
        # Find delivery request
        delivery_request = db.delivery_requests.find_one({"id": request_id})
        if not delivery_request:
            raise HTTPException(status_code=404, detail="Delivery request not found")
        
        if delivery_request["status"] != DeliveryStatus.PENDING:
            raise HTTPException(status_code=400, detail="Cannot negotiate on this delivery request")
        
        # Update with negotiated price
        db.delivery_requests.update_one(
            {"id": request_id},
            {
                "$set": {
                    "negotiated_price": proposed_price,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "message": "Price negotiation submitted",
            "request_id": request_id,
            "proposed_price": proposed_price,
            "original_price": delivery_request["estimated_price"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error negotiating price: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to negotiate price")

@router.get("/api/drivers/search")
async def search_drivers(
    pickup_lat:Optional[float] = None,
    pickup_lng: Optional[float] = None,
    radius_km: float = 50.0,
    vehicle_type: Optional[str] = None,
    min_rating: float = 3.0,
    current_user: dict = Depends(get_current_user)
):
    """Search for available drivers near pickup location"""
    db = get_db()
    try:
        # Build search query
        query = {
            "status": {"$in": [DriverStatus.ONLINE, DriverStatus.OFFLINE]},
            "rating": {"$gte": min_rating}
        }
        
        if vehicle_type:
            # Get vehicle IDs with matching type
            vehicle_query = {"vehicle_type": vehicle_type}
            vehicles = list(db.vehicles.find(vehicle_query))
            driver_ids = [v["driver_id"] for v in vehicles]
            query["id"] = {"$in": driver_ids}
        
        # Get drivers
        drivers = list(db.drivers.find(query))
        
        # Get vehicle info for each driver
        driver_results = []
        for driver in drivers:
            vehicle = db.vehicles.find_one({"driver_id": driver["id"]})
            
            # Calculate distance if pickup coordinates provided
            distance_km = None
            if pickup_lat and pickup_lng and driver.get("current_location"):
                # Simple distance calculation (in real app would use proper geo calculation)
                import math
                lat1, lng1 = pickup_lat, pickup_lng
                lat2, lng2 = driver["current_location"].get("lat", 0), driver["current_location"].get("lng", 0)
                
                # Haversine formula approximation
                dlat = math.radians(lat2 - lat1)
                dlng = math.radians(lng2 - lng1)
                a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
                c = 2 * math.asin(math.sqrt(a))
                distance_km = 6371 * c  # Earth's radius in km
                
                # Filter by radius
                if distance_km > radius_km:
                    continue
            
            driver_result = {
                "driver_id": driver["id"],
                "driver_name": driver["driver_name"],
                "driver_username": driver["driver_username"],
                "rating": driver["rating"],
                "total_deliveries": driver["total_deliveries"],
                "current_location": driver.get("current_location"),
                "vehicle_info": {
                    "type": vehicle.get("vehicle_type") if vehicle else "unknown",
                    "plate_number": vehicle.get("plate_number") if vehicle else "",
                    "make_model": vehicle.get("make_model") if vehicle else "",
                    "color": vehicle.get("color") if vehicle else ""
                },
                "status": driver["status"],
                "distance_km": round(distance_km, 2) if distance_km else None
            }
            driver_results.append(driver_result)
        
        # Sort by distance if available, then by rating
        driver_results.sort(key=lambda x: (x["distance_km"] or 999, -x["rating"]))
        
        return {"drivers": driver_results[:20]}  # Limit to 20 results
        
    except Exception as e:
        print(f"Error searching drivers: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search drivers")

@router.post("/api/delivery/request-enhanced")
async def create_enhanced_delivery_request(request_data:DeliveryRequestCreate, current_user: dict = Depends(get_current_user)):
    """Create enhanced delivery request with multiple destinations and driver selection"""
    db = get_db()
    try:
        # Validate user can request delivery
        allowed_roles = ['agent', 'farmer', 'supplier', 'processor']
        if current_user.get('role') not in allowed_roles:
            raise HTTPException(status_code=403, detail="Only sellers can request delivery")
        
        # Calculate total distance for multiple destinations
        total_distance = 0.0
        for i in range(len(request_data.delivery_addresses)):
            total_distance += 10.0  # Mock distance calculation
        
        # Generate OTP
        import random
        otp = str(random.randint(100000, 999999))
        
        # Process delivery locations
        delivery_locations = []
        for i, address in enumerate(request_data.delivery_addresses):
            coords = request_data.delivery_coordinates[i] if i < len(request_data.delivery_coordinates) else {"lat": 0.0, "lng": 0.0}
            delivery_locations.append({
                "address": address,
                "lat": coords.get("lat", 0.0),
                "lng": coords.get("lng", 0.0),
                "order": i + 1
            })
        
        # Create delivery request
        delivery_request = {
            "id": str(uuid.uuid4()),
            "order_id": request_data.order_id,
            "order_type": request_data.order_type,
            "requester_username": current_user["username"],
            "pickup_location": {
                "address": request_data.pickup_address,
                "lat": request_data.pickup_coordinates.get("lat", 0.0) if request_data.pickup_coordinates else 0.0,
                "lng": request_data.pickup_coordinates.get("lng", 0.0) if request_data.pickup_coordinates else 0.0
            },
            "delivery_locations": delivery_locations,
            "total_quantity": request_data.total_quantity,
            "quantity_unit": request_data.quantity_unit,
            "distance_km": total_distance,
            "estimated_price": request_data.estimated_price,
            "product_details": request_data.product_details,
            "weight_kg": request_data.weight_kg,
            "special_instructions": request_data.special_instructions,
            "status": DeliveryStatus.PENDING,
            "delivery_otp": otp,
            "chat_messages": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # If preferred driver specified, assign directly
        if request_data.preferred_driver_username:
            preferred_driver = db.drivers.find_one({"driver_username": request_data.preferred_driver_username})
            if preferred_driver:
                delivery_request["preferred_driver_id"] = preferred_driver["id"]
        
        # Store in database
        db.delivery_requests.insert_one(delivery_request)
        
        return {
            "message": "Enhanced delivery request created successfully",
            "request_id": delivery_request["id"],
            "total_destinations": len(delivery_locations),
            "total_quantity": request_data.total_quantity,
            "quantity_unit": request_data.quantity_unit,
            "estimated_price": request_data.estimated_price,
            "total_distance_km": total_distance,
            "delivery_otp": otp
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating enhanced delivery request: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create delivery request")

@router.post("/api/delivery/{request_id}/message")
async def send_delivery_message(request_id:str, message_data: dict, current_user: dict = Depends(get_current_user)):
    """Send message in delivery chat"""
    db = get_db()
    try:
        # Find delivery request
        delivery_request = db.delivery_requests.find_one({"id": request_id})
        if not delivery_request:
            raise HTTPException(status_code=404, detail="Delivery request not found")
        
        # Determine sender type
        sender_type = "requester"
        if delivery_request.get("assigned_driver_id"):
            driver = db.drivers.find_one({"id": delivery_request["assigned_driver_id"]})
            if driver and driver["driver_username"] == current_user["username"]:
                sender_type = "driver"
        
        # Validate authorization
        if (sender_type == "requester" and current_user["username"] != delivery_request["requester_username"]) or \
           (sender_type == "driver" and current_user["username"] != driver.get("driver_username")):
            raise HTTPException(status_code=403, detail="Not authorized to send messages in this delivery")
        
        # Create message
        message = {
            "id": str(uuid.uuid4()),
            "delivery_request_id": request_id,
            "sender_username": current_user["username"],
            "sender_type": sender_type,
            "message_type": message_data.get("type", "text"),
            "content": message_data.get("content", ""),
            "location_data": message_data.get("location_data"),
            "timestamp": datetime.utcnow()
        }
        
        # Add message to delivery request
        db.delivery_requests.update_one(
            {"id": request_id},
            {
                "$push": {"chat_messages": message},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return {"message": "Message sent successfully", "message_id": message["id"]}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error sending delivery message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send message")

@router.get("/api/delivery/{request_id}/messages")
async def get_delivery_messages(request_id:str, current_user: dict = Depends(get_current_user)):
    """Get all messages for a delivery request"""
    db = get_db()
    try:
        # Find delivery request
        delivery_request = db.delivery_requests.find_one({"id": request_id})
        if not delivery_request:
            raise HTTPException(status_code=404, detail="Delivery request not found")
        
        # Validate authorization
        is_requester = current_user["username"] == delivery_request["requester_username"]
        is_driver = False
        if delivery_request.get("assigned_driver_id"):
            driver = db.drivers.find_one({"id": delivery_request["assigned_driver_id"]})
            is_driver = driver and driver["driver_username"] == current_user["username"]
        
        if not is_requester and not is_driver:
            raise HTTPException(status_code=403, detail="Not authorized to view messages")
        
        # Get messages
        messages = delivery_request.get("chat_messages", [])
        
        # Format timestamps
        for message in messages:
            if isinstance(message.get("timestamp"), datetime):
                message["timestamp"] = message["timestamp"].isoformat()
        
        return {
            "messages": messages,
            "delivery_request": {
                "id": delivery_request["id"],
                "status": delivery_request["status"],
                "pickup_location": delivery_request["pickup_location"],
                "delivery_locations": delivery_request["delivery_locations"],
                "product_details": delivery_request["product_details"],
                "total_quantity": delivery_request["total_quantity"],
                "quantity_unit": delivery_request["quantity_unit"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting delivery messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get messages")

@router.post("/api/drivers/location")
async def update_driver_location(location_data:dict, current_user: dict = Depends(get_current_user)):
    """Update driver's current location"""
    db = get_db()
    try:
        # Find driver
        driver = db.drivers.find_one({"driver_username": current_user["username"]})
        if not driver:
            raise HTTPException(status_code=404, detail="Driver profile not found")
        
        # Update location
        location = {
            "lat": location_data.get("lat"),
            "lng": location_data.get("lng"),
            "address": location_data.get("address", ""),
            "updated_at": datetime.utcnow()
        }
        
        db.drivers.update_one(
            {"driver_username": current_user["username"]},
            {
                "$set": {
                    "current_location": location,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {"message": "Location updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating driver location: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update location")

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

