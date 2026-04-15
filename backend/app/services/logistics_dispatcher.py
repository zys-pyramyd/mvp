import requests
import logging

logger = logging.getLogger(__name__)

def dispatch_order_to_external_logistics(order_data: dict, is_rfq: bool = False):
    """
    Dummy API hook to push confirmed, paid orders to an external offline delivery partner.
    This simulates a POST request with the required tracking payload.
    Logs are kept minimal to save disk space as requested.
    """
    
    # 1. Structure the outbound payload standardizing pyhub vs rfq
    payload = {
        "external_reference": order_data.get("order_id", order_data.get("id")),
        "is_bulk_rfq": is_rfq,
        "delivery_address": order_data.get("delivery_address", ""),
        "seller_address": order_data.get("seller_address", ""), 
        "total_amount": order_data.get("total_amount", 0),
        "items_count": len(order_data.get("items", [])) if not is_rfq else 1,
        "customer_phone": order_data.get("customer_phone", "")
    }

    # 2. Simulate API POST
    # We purposefully do not execute the HTTP call to avoid timeouts/errors for the MVP offline phase
    try:
        # response = requests.post(
        #     "https://api.offline-logistics-partner.com/v1/dispatch",
        #     json=payload,
        #     timeout=5
        # )
        pass # Placeholder
    except Exception:
        pass # Silently fail to avoid redundant logs
