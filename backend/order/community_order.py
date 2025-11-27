from fastapi import HTTPException
from .models import GroupOrder

def process_create_group_order(order_data: dict, current_user: dict, db):
    """
    Process creation of a Group Buying order (Community).
    """
    if current_user.get('role') != 'agent':
        raise HTTPException(status_code=403, detail="Only agents can create group orders")
    
    # Calculate commission
    total_amount = order_data['selectedPrice']['price_per_unit'] * order_data['quantity']
    
    if order_data['commissionType'] == 'pyramyd':
        agent_commission = total_amount * 0.05  # 5% commission
    else:
        agent_commission = 0  # Will be collected after delivery
    
    # Create group order
    group_order = GroupOrder(
        agent_id=current_user['id'],
        produce=order_data['produce'],
        category=order_data['category'],
        location=order_data['location'],
        total_quantity=order_data['quantity'],
        buyers=order_data['buyers'],
        selected_farm=order_data['selectedPrice'],
        commission_type=order_data['commissionType'],
        total_amount=total_amount,
        agent_commission=agent_commission
    )
    
    # Save to database
    order_dict = group_order.dict()
    db.group_orders.insert_one(order_dict)
    
    # Update product quantity (real-time stock management)
    db.products.update_one(
        {"id": order_data['selectedPrice']['product_id']},
        {"$inc": {"quantity_available": -order_data['quantity']}}
    )
    
    return {
        "message": "Group order created successfully",
        "order_id": group_order.id,
        "total_amount": total_amount,
        "agent_commission": agent_commission
    }
