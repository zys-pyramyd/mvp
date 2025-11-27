import uuid
from datetime import datetime
from .paystack import (
    paystack_request, 
    naira_to_kobo, 
    kobo_to_naira, 
    FARMHUB_SPLIT_GROUP, 
    FARMHUB_SUBACCOUNT
)

# FARMHUB: 10% service charge (extracted from vendor, vendor gets 90%)
FARMHUB_SERVICE_CHARGE = 0.10

def initialize_farmhub_payment(payment_data: dict, user: dict, delivery_fee: float, delivery_method: str):
    """
    Initialize payment for FarmHub (Farm Deals).
    Uses Paystack Split Group for automatic splitting.
    """
    product_total = payment_data.get("product_total", 0)
    product_id = payment_data.get("product_id")
    order_id = payment_data.get("order_id")
    customer_state = payment_data.get("customer_state")
    callback_url = payment_data.get("callback_url", "")
    
    # Convert to kobo
    product_total_kobo = naira_to_kobo(product_total)
    delivery_fee_kobo = naira_to_kobo(delivery_fee)
    
    # Calculate platform cut
    # Vendor receives 90% of product total
    service_kobo = int(product_total_kobo * FARMHUB_SERVICE_CHARGE)
    platform_cut_kobo = service_kobo + delivery_fee_kobo
    
    # Total amount customer pays
    total_amount_kobo = product_total_kobo + platform_cut_kobo
    
    # Generate unique reference
    reference = f"PYR_FARM_{uuid.uuid4().hex[:12].upper()}"
    
    # Prepare Paystack payload
    paystack_data = {
        "email": user["email"],
        "amount": total_amount_kobo,
        "split_code": FARMHUB_SPLIT_GROUP,
        "reference": reference,
        "callback_url": callback_url,
        "metadata": {
            "product_id": product_id,
            "order_id": order_id,
            "platform_type": "farmhub",
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
        "subaccount_code": FARMHUB_SUBACCOUNT,
        "split_code": FARMHUB_SPLIT_GROUP,
        "breakdown": {
            "product_total": kobo_to_naira(product_total_kobo),
            "delivery_fee": kobo_to_naira(delivery_fee_kobo),
            "platform_cut": kobo_to_naira(platform_cut_kobo),
            "service_charge": kobo_to_naira(service_kobo)
        }
    }
