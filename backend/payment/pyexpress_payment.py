import uuid
from datetime import datetime
from fastapi import HTTPException
from .paystack import (
    paystack_request, 
    naira_to_kobo, 
    kobo_to_naira
)

# HOME: 2.5% commission (from vendor) + 3% service charge (from buyer)
HOME_VENDOR_COMMISSION = 0.025
HOME_BUYER_SERVICE_CHARGE = 0.03

def initialize_pyexpress_payment(payment_data: dict, user: dict, delivery_fee: float, delivery_method: str):
    """
    Initialize payment for PyExpress (Home).
    Uses dynamic subaccount and transaction charge.
    """
    product_total = payment_data.get("product_total", 0)
    product_id = payment_data.get("product_id")
    order_id = payment_data.get("order_id")
    customer_state = payment_data.get("customer_state")
    subaccount_code = payment_data.get("subaccount_code")
    callback_url = payment_data.get("callback_url", "")
    
    if not subaccount_code:
        raise HTTPException(status_code=400, detail="Subaccount code is required for Home transactions")
    
    # Convert to kobo
    product_total_kobo = naira_to_kobo(product_total)
    delivery_fee_kobo = naira_to_kobo(delivery_fee)
    
    # Calculate platform cut
    # Vendor receives 97.5% of product total
    vendor_commission_kobo = int(product_total_kobo * HOME_VENDOR_COMMISSION)
    buyer_service_kobo = int(product_total_kobo * HOME_BUYER_SERVICE_CHARGE)
    platform_cut_kobo = vendor_commission_kobo + buyer_service_kobo + delivery_fee_kobo
    
    # Total amount customer pays
    total_amount_kobo = product_total_kobo + platform_cut_kobo
    
    # Generate unique reference
    reference = f"PYR_HOME_{uuid.uuid4().hex[:12].upper()}"
    
    # Prepare Paystack payload
    paystack_data = {
        "email": user["email"],
        "amount": total_amount_kobo,
        "subaccount": subaccount_code,
        "transaction_charge": platform_cut_kobo,
        "bearer": "account",  # Platform pays Paystack fees (or rather, fees are deducted from subaccount share? No, bearer=account means main account pays fees)
        # Actually, if we set transaction_charge, that amount goes to main account.
        # Paystack fees are usually deducted from the transaction amount.
        # If bearer=account, main account bears paystack fees.
        "reference": reference,
        "callback_url": callback_url,
        "metadata": {
            "product_id": product_id,
            "order_id": order_id,
            "platform_type": "home",
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
