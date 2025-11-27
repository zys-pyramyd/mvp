import uuid
from datetime import datetime
from fastapi import HTTPException
from .paystack import (
    paystack_request, 
    naira_to_kobo, 
    kobo_to_naira
)

# COMMUNITY: 2.5% commission (from vendor) + 5% service charge (from buyer)
COMMUNITY_VENDOR_COMMISSION = 0.025
COMMUNITY_BUYER_SERVICE_CHARGE = 0.05

def initialize_community_payment(payment_data: dict, user: dict, delivery_fee: float, delivery_method: str):
    """
    Initialize payment for Community.
    Uses dynamic subaccount and transaction charge.
    """
    product_total = payment_data.get("product_total", 0)
    product_id = payment_data.get("product_id")
    order_id = payment_data.get("order_id")
    customer_state = payment_data.get("customer_state")
    subaccount_code = payment_data.get("subaccount_code")
    callback_url = payment_data.get("callback_url", "")
    
    if not subaccount_code:
        raise HTTPException(status_code=400, detail="Subaccount code is required for Community transactions")
    
    # Convert to kobo
    product_total_kobo = naira_to_kobo(product_total)
    delivery_fee_kobo = naira_to_kobo(delivery_fee)
    
    # Calculate platform cut
    # Vendor receives 97.5% of product total
    vendor_commission_kobo = int(product_total_kobo * COMMUNITY_VENDOR_COMMISSION)
    buyer_service_kobo = int(product_total_kobo * COMMUNITY_BUYER_SERVICE_CHARGE)
    platform_cut_kobo = vendor_commission_kobo + buyer_service_kobo + delivery_fee_kobo
    
    # Total amount customer pays
    total_amount_kobo = product_total_kobo + platform_cut_kobo
    
    # Generate unique reference
    reference = f"PYR_COMM_{uuid.uuid4().hex[:12].upper()}"
    
    # Prepare Paystack payload
    paystack_data = {
        "email": user["email"],
        "amount": total_amount_kobo,
        "subaccount": subaccount_code,
        "transaction_charge": platform_cut_kobo,
        "bearer": "account",
        "reference": reference,
        "callback_url": callback_url,
        "metadata": {
            "product_id": product_id,
            "order_id": order_id,
            "platform_type": "community",
            "buyer_id": user["id"],
            "customer_state": customer_state,
            "delivery_fee": delivery_fee,
            "delivery_method": delivery_method
        }
    }
    
    response = paystack_request("POST", "/transaction/initialize", paystack_data)
    
    return {
        "response": response,
        "reference": reference,
        "amount_kobo": total_amount_kobo,
        "platform_cut_kobo": platform_cut_kobo,
        "subaccount_code": subaccount_code,
        "split_code": None,
        "breakdown": {
            "product_total": kobo_to_naira(product_total_kobo),
            "delivery_fee": kobo_to_naira(delivery_fee_kobo),
            "platform_cut": kobo_to_naira(platform_cut_kobo),
            "vendor_commission": kobo_to_naira(vendor_commission_kobo),
            "buyer_service_charge": kobo_to_naira(buyer_service_kobo)
        }
    }
