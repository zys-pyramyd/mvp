import re
import os

filepath = r"c:\Users\Downloads\mvp\backend\app\api\logistics.py"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Remove imports
content = content.replace("from app.models.driver import DriverCreate\n", "")
content = content.replace("from app.models.common import DriverStatus, DeliveryStatus", "from app.models.common import DeliveryStatus")

funcs_to_remove = [
    "register_independent_driver",
    "add_driver_to_logistics",
    "get_my_drivers",
    "get_available_deliveries",
    "accept_delivery_request",
    "negotiate_delivery_price",
    "search_drivers",
    "create_enhanced_delivery_request",
    "send_delivery_message",
    "get_delivery_messages",
    "update_driver_location"
]

parts = content.split("@router.")
new_parts = [parts[0]]

for part in parts[1:]:
    m = re.search(r"async def ([a-zA-Z0-9_]+)\(", part)
    if m:
        func_name = m.group(1)
        if func_name not in funcs_to_remove:
            new_parts.append("@router." + part)
    else:
        new_parts.append("@router." + part)

content = "".join(new_parts)

complete_delivery_search = """        # Check if user is authorized (buyer or the assigned driver)
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
            )"""

complete_delivery_replace = """        # Require the request to be confirmed by buyer or authorized user if needed
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
        )"""

content = content.replace(complete_delivery_search, complete_delivery_replace)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Driver functions removed successfully from {filepath}")
