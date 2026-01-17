from fastapi import HTTPException
from .models import OutsourcedOrder

def process_create_outsourced_order(produce: str, category: str, quantity: int, expected_price: float, location: str, current_user: dict, db):
    """
    Process creation of an Outsourced order (Farm Deals).
    """
    allowed_roles = ['agent', 'processor', 'supplier']
    if current_user.get('role') not in allowed_roles:
        raise HTTPException(status_code=403, detail="Only agents, processors, and suppliers can outsource orders")
    
    outsourced_order = OutsourcedOrder(
        requester_id=current_user['id'],
        produce=produce,
        category=category,
        quantity=quantity,
        expected_price=expected_price,
        location=location
    )
    
    order_dict = outsourced_order.dict()
    db.outsourced_orders.insert_one(order_dict)
    
    return {
        "message": "Order outsourced successfully",
        "order_id": outsourced_order.id,
        "status": "open"
    }
