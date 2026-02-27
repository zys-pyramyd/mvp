import requests
import hashlib
import hmac
from app.core.config import settings
from fastapi import HTTPException

def paystack_request(method: str, endpoint: str, data: dict = None) -> dict:
    """Make authenticated request to Paystack API"""
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    url = f"{settings.PAYSTACK_API_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        # Handle 4xx/5xx errors gracefully-ish
        detail = f"Paystack API error: {str(e)}"
        if hasattr(e.response, 'text'):
            detail += f" Response: {e.response.text}"
        print(detail)
        # return None or raise? For critical flows like DVA, raising is better.
        raise HTTPException(status_code=e.response.status_code, detail=detail)
    except Exception as e:
        print(f"Paystack request failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Paystack connection failed: {str(e)}")

def create_customer(user: dict) -> dict:
    """Create a Paystack customer"""
    data = {
        "email": user["email"],
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
        "phone": user.get("phone")
    }
    return paystack_request("POST", "/customer", data)

def assign_dedicated_account(user: dict, bvn: str) -> dict:
    """
    Assign a Dedicated Virtual Account to the user.
    Note: BVN should be passed decrypted here.
    """
    # First, ensure customer exists or get their customer code
    # Usually /dedicated_account/assign handles customer creation if not exists, 
    # but strictly it needs a customer code or email.
    
    data = {
        "email": user["email"],
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
        "phone": user.get("phone"),
        "preferred_bank": "wema-bank",
        "country": "NG",
        "bvn": bvn
    }
    
    result = paystack_request("POST", "/dedicated_account/assign", data)
    return result

def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify Paystack webhook signature"""
    if not signature:
        return False
        
    computed_signature = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
        payload,
        hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(computed_signature, signature)

def resolve_account_number(account_number: str, bank_code: str) -> dict:
    """Verify account number matches bank"""
    return paystack_request("GET", f"/bank/resolve?account_number={account_number}&bank_code={bank_code}")

def resolve_bvn(bvn: str) -> dict:
    """Verify BVN and return details including name"""
    return paystack_request("GET", f"/bank/resolve_bvn/{bvn}")

def create_transfer_recipient(name: str, account_number: str, bank_code: str, currency: str = "NGN") -> dict:
    """Create a transfer recipient"""
    data = {
        "type": "nuban",
        "name": name,
        "account_number": account_number,
        "bank_code": bank_code,
        "currency": currency
    }
    return paystack_request("POST", "/transferrecipient", data)

def initiate_transfer(amount: int, recipient_code: str, reason: str = None) -> dict:
    """
    Initiate a transfer from balance.
    Amount in kobo.
    """
    data = {
        "source": "balance", 
        "amount": amount,
        "recipient": recipient_code,
        "reason": reason
    }
    return paystack_request("POST", "/transfer", data)

def initialize_transaction(email: str, amount: int, callback_url: str, metadata: dict = None) -> dict:
    """
    Initialize a transaction.
    Amount in kobo.
    """
    data = {
        "email": email,
        "amount": amount,
        "callback_url": callback_url,
        "metadata": metadata or {}
    }
    return paystack_request("POST", "/transaction/initialize", data)

def verify_transaction(reference: str) -> dict:
    """
    Verify a Paystack transaction by reference.
    Returns the full Paystack response; check data['status'] == 'success'.
    """
    return paystack_request("GET", f"/transaction/verify/{reference}")
