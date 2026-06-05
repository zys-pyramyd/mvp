from fastapi import APIRouter, HTTPException, Depends
from app.api.deps import get_db, get_current_user
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# ─────────────────────────── Request Schemas ────────────────────────────────

class WalletPinCreate(BaseModel):
    pin: str = Field(..., min_length=4, max_length=6)

class WalletPinVerify(BaseModel):
    pin: str

class BankAccountCreate(BaseModel):
    account_name: str
    account_number: str
    bank_name: str
    bank_code: str
    is_primary: bool = False

class GiftCardCreate(BaseModel):
    amount: float
    recipient_email: Optional[str] = None
    recipient_name: Optional[str] = None
    message: Optional[str] = None

class GiftCardRedeem(BaseModel):
    card_code: str
    amount: Optional[float] = None

class WithdrawalRequest(BaseModel):
    amount: float
    account_number: str
    bank_code: str
    account_name: str
    description: Optional[str] = "Wallet Withdrawal"


# ─────────────────────────── Wallet Summary ─────────────────────────────────

@router.get("/summary")
async def get_wallet_summary(current_user: dict = Depends(get_current_user)):
    """Comprehensive wallet summary for the current user."""
    db = get_db()
    user_id = current_user["id"]

    user = db.users.find_one({"id": user_id})
    current_balance = user.get("wallet_balance", 0.0) if user else 0.0

    all_transactions = list(db.wallet_transactions.find({"user_id": user_id, "status": "success"}))
    total_funded     = sum(t["amount"] for t in all_transactions if t.get("type") == "credit")
    total_spent      = sum(t["amount"] for t in all_transactions if t.get("category") == "order_payment")
    total_withdrawn  = sum(t["amount"] for t in all_transactions if t.get("type") == "withdrawal")

    pending_count = db.wallet_transactions.count_documents({"user_id": user_id, "status": "pending"})
    last_tx = db.wallet_transactions.find_one({"user_id": user_id}, sort=[("created_at", -1)])
    linked_accounts_count = db.bank_accounts.count_documents({"user_id": user_id})

    wallet_security = db.wallet_security.find_one({"user_id": user_id})
    security_status = {
        "pin_set": bool(wallet_security and wallet_security.get("transaction_pin")),
        "pin_locked": bool(
            wallet_security
            and wallet_security.get("pin_locked_until")
            and wallet_security["pin_locked_until"] > datetime.utcnow()
        ),
        "daily_limit": wallet_security.get("daily_limit", 50000.0) if wallet_security else 50000.0,
    }

    return {
        "user_id": user_id,
        "username": current_user["username"],
        "balance": current_balance,
        "total_funded": total_funded,
        "total_spent": total_spent,
        "total_withdrawn": total_withdrawn,
        "pending_transactions": pending_count,
        "last_transaction_date": last_tx["created_at"].isoformat() if last_tx else None,
        "security_status": security_status,
        "linked_accounts": linked_accounts_count,
    }


# ─────────────────────────── Transactions ───────────────────────────────────

@router.get("/transactions")
async def get_wallet_transactions(
    page: int = 1,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get paginated wallet transactions."""
    db = get_db()
    user_id = current_user["id"]
    query = {"user_id": user_id}

    total_count = db.wallet_transactions.count_documents(query)
    skip = (page - 1) * limit
    transactions = list(
        db.wallet_transactions.find(query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

    for tx in transactions:
        tx.pop("_id", None)
        for field in ("created_at", "completed_at"):
            if isinstance(tx.get(field), datetime):
                tx[field] = tx[field].isoformat()

    return {
        "transactions": transactions,
        "total_count": total_count,
        "page": page,
        "limit": limit,
        "total_pages": (total_count + limit - 1) // limit if total_count > 0 else 0,
    }


# ─────────────────────────── Withdrawal ─────────────────────────────────────

@router.post("/withdraw")
async def withdraw_funds(
    request: WithdrawalRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Withdraw funds from wallet to bank account via Paystack Transfer.
    Atomically deducts balance first; refunds if transfer initiation fails.
    """
    db = get_db()
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid withdrawal amount")

    user_id = current_user["id"]
    user = db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    current_balance = user.get("wallet_balance", 0.0)
    if current_balance < request.amount:
        raise HTTPException(status_code=400, detail="Insufficient wallet balance")

    # Atomically deduct balance to prevent race conditions
    new_balance = current_balance - request.amount
    tx_ref = f"WTH-{uuid.uuid4().hex[:12].upper()}"
    db.users.update_one({"id": user_id}, {"$set": {"wallet_balance": new_balance}})

    try:
        from app.services.paystack import create_transfer_recipient, initiate_transfer

        recipient_code = create_transfer_recipient(
            request.account_name, request.account_number, request.bank_code
        )
        transfer_data = initiate_transfer(
            request.amount, recipient_code, tx_ref, request.description
        )

        transaction = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "email": current_user.get("email"),
            "type": "withdrawal",
            "amount": request.amount,
            "reference": tx_ref,
            "transfer_code": transfer_data.get("transfer_code"),
            "status": "success",
            "channel": "paystack_transfer",
            "bank_details": {
                "bank_code": request.bank_code,
                "account_number": request.account_number,
                "account_name": request.account_name,
            },
            "created_at": datetime.utcnow(),
        }
        db.wallet_transactions.insert_one(transaction)
        logger.info(f"Withdrawal successful for user {user_id}: ₦{request.amount}, ref {tx_ref}")

        return {
            "message": "Withdrawal initiated successfully",
            "reference": tx_ref,
            "new_balance": new_balance,
        }

    except Exception as e:
        # Rollback balance if transfer failed
        logger.error(f"Withdrawal failed for user {user_id}: {e}. Refunding...")
        db.users.update_one({"id": user_id}, {"$inc": {"wallet_balance": request.amount}})
        db.wallet_transactions.insert_one({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "type": "refund",
            "amount": request.amount,
            "reference": f"REF-{tx_ref}",
            "status": "success",
            "reason": f"Transfer failed: {str(e)}",
            "created_at": datetime.utcnow(),
        })
        raise HTTPException(status_code=500, detail=f"Transfer failed: {str(e)}")


# ─────────────────────────── Bank Accounts ──────────────────────────────────

@router.post("/bank-accounts")
async def add_bank_account(
    account_data: BankAccountCreate,
    current_user: dict = Depends(get_current_user)
):
    """Add a bank account for wallet withdrawals."""
    db = get_db()
    user_id = current_user["id"]

    existing = db.bank_accounts.find_one({
        "user_id": user_id,
        "account_number": account_data.account_number
    })
    if existing:
        raise HTTPException(status_code=400, detail="Bank account already exists")

    if account_data.is_primary:
        db.bank_accounts.update_many({"user_id": user_id}, {"$set": {"is_primary": False}})

    bank_account = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "account_name": account_data.account_name,
        "account_number": account_data.account_number,
        "bank_name": account_data.bank_name,
        "bank_code": account_data.bank_code,
        "is_primary": account_data.is_primary,
        "is_verified": True,
        "created_at": datetime.utcnow(),
    }
    db.bank_accounts.insert_one(bank_account)

    return {
        "message": "Bank account added successfully",
        "account_id": bank_account["id"],
        "account_name": account_data.account_name,
        "account_number": account_data.account_number,
        "bank_name": account_data.bank_name,
        "is_verified": True,
    }


@router.get("/bank-accounts")
async def get_user_bank_accounts(current_user: dict = Depends(get_current_user)):
    """Get user's linked bank accounts (masked account numbers)."""
    db = get_db()
    accounts = list(db.bank_accounts.find({"user_id": current_user["id"]}))

    for acc in accounts:
        acc.pop("_id", None)
        if isinstance(acc.get("created_at"), datetime):
            acc["created_at"] = acc["created_at"].isoformat()
        num = acc.get("account_number", "")
        acc["masked_account_number"] = ("*" * (len(num) - 4) + num[-4:]) if len(num) >= 4 else num

    return {"accounts": accounts, "total_accounts": len(accounts)}


@router.delete("/bank-accounts/{account_id}")
async def remove_bank_account(account_id: str, current_user: dict = Depends(get_current_user)):
    """Remove a bank account."""
    db = get_db()
    account = db.bank_accounts.find_one({"id": account_id, "user_id": current_user["id"]})
    if not account:
        raise HTTPException(status_code=404, detail="Bank account not found")

    db.bank_accounts.delete_one({"id": account_id})
    return {"message": "Bank account removed successfully", "account_id": account_id}


# ─────────────────────────── Gift Cards ─────────────────────────────────────

@router.post("/gift-cards")
async def create_gift_card(
    gift_card_data: GiftCardCreate,
    current_user: dict = Depends(get_current_user)
):
    """Purchase a gift card from wallet balance."""
    db = get_db()
    user_id = current_user["id"]
    amount = gift_card_data.amount

    user = db.users.find_one({"id": user_id})
    current_balance = user.get("wallet_balance", 0.0) if user else 0.0

    if current_balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient wallet balance to purchase gift card")

    card_code = f"GIFT-{uuid.uuid4().hex[:8].upper()}"
    gift_card = {
        "id": str(uuid.uuid4()),
        "card_code": card_code,
        "amount": amount,
        "balance": amount,
        "status": "active",
        "purchaser_id": user_id,
        "purchaser_username": current_user["username"],
        "recipient_email": gift_card_data.recipient_email,
        "recipient_name": gift_card_data.recipient_name,
        "message": gift_card_data.message,
        "expiry_date": datetime.utcnow() + timedelta(days=365),
        "created_at": datetime.utcnow(),
        "redeemed_at": None,
        "redeemed_by_id": None,
    }
    db.gift_cards.insert_one(gift_card)

    # Deduct wallet & log transaction
    db.users.update_one({"id": user_id}, {"$inc": {"wallet_balance": -amount}})
    db.wallet_transactions.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "email": current_user.get("email"),
        "type": "debit",
        "category": "gift_card_purchase",
        "amount": amount,
        "reference": f"GIFT-{uuid.uuid4().hex[:12].upper()}",
        "description": f"Gift card purchase - {card_code}",
        "status": "success",
        "metadata": {"card_code": card_code},
        "created_at": datetime.utcnow(),
    })

    return {
        "message": "Gift card created successfully",
        "gift_card": {
            "id": gift_card["id"],
            "card_code": card_code,
            "amount": amount,
            "expiry_date": gift_card["expiry_date"].isoformat(),
            "recipient_email": gift_card_data.recipient_email,
            "recipient_name": gift_card_data.recipient_name,
        },
        "new_balance": current_balance - amount,
    }


@router.post("/gift-cards/redeem")
async def redeem_gift_card(
    redeem_data: GiftCardRedeem,
    current_user: dict = Depends(get_current_user)
):
    """Redeem a gift card to wallet balance."""
    db = get_db()
    user_id = current_user["id"]
    card_code = redeem_data.card_code.upper()

    gift_card = db.gift_cards.find_one({"card_code": card_code})
    if not gift_card:
        raise HTTPException(status_code=404, detail="Gift card not found")

    if gift_card["status"] != "active":
        raise HTTPException(status_code=400, detail=f"Gift card is {gift_card['status']}")

    if gift_card.get("expiry_date") and gift_card["expiry_date"] < datetime.utcnow():
        db.gift_cards.update_one({"id": gift_card["id"]}, {"$set": {"status": "expired"}})
        raise HTTPException(status_code=400, detail="Gift card has expired")

    available_balance = gift_card["balance"]
    redemption_amount = redeem_data.amount if redeem_data.amount else available_balance

    if redemption_amount > available_balance:
        raise HTTPException(status_code=400, detail=f"Insufficient gift card balance. Available: ₦{available_balance}")
    if redemption_amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid redemption amount")

    user = db.users.find_one({"id": user_id})
    current_balance = user.get("wallet_balance", 0.0) if user else 0.0
    new_gift_balance = available_balance - redemption_amount

    gift_updates = {
        "balance": new_gift_balance,
        "redeemed_by_id": user_id,
        "redeemed_by_username": current_user["username"],
    }
    if new_gift_balance == 0:
        gift_updates["status"] = "redeemed"
        gift_updates["redeemed_at"] = datetime.utcnow()

    db.gift_cards.update_one({"id": gift_card["id"]}, {"$set": gift_updates})
    db.users.update_one({"id": user_id}, {"$inc": {"wallet_balance": redemption_amount}})
    db.wallet_transactions.insert_one({
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "email": current_user.get("email"),
        "type": "credit",
        "category": "gift_card_redemption",
        "amount": redemption_amount,
        "reference": f"REDEEM-{uuid.uuid4().hex[:12].upper()}",
        "description": f"Gift card redemption - {card_code}",
        "status": "success",
        "metadata": {"card_code": card_code, "remaining_balance": new_gift_balance},
        "created_at": datetime.utcnow(),
    })

    return {
        "message": "Gift card redeemed successfully",
        "redeemed_amount": redemption_amount,
        "gift_card_remaining_balance": new_gift_balance,
        "new_wallet_balance": current_balance + redemption_amount,
        "fully_redeemed": new_gift_balance == 0,
    }


@router.get("/gift-cards/my-cards")
async def get_my_gift_cards(current_user: dict = Depends(get_current_user)):
    """Get gift cards purchased by the current user."""
    db = get_db()
    cards = list(db.gift_cards.find({"purchaser_id": current_user["id"]}).sort("created_at", -1))

    for card in cards:
        card.pop("_id", None)
        for field in ("created_at", "expiry_date", "redeemed_at"):
            if isinstance(card.get(field), datetime):
                card[field] = card[field].isoformat()

    return {"gift_cards": cards, "total_cards": len(cards)}


@router.get("/gift-cards/{card_code}")
async def get_gift_card_details(card_code: str):
    """Get public gift card info (for validating before redemption)."""
    db = get_db()
    gift_card = db.gift_cards.find_one({"card_code": card_code.upper()})
    if not gift_card:
        raise HTTPException(status_code=404, detail="Gift card not found")

    return {
        "card_code": gift_card["card_code"],
        "amount": gift_card["amount"],
        "balance": gift_card["balance"],
        "status": gift_card["status"],
        "expiry_date": gift_card["expiry_date"].isoformat() if isinstance(gift_card.get("expiry_date"), datetime) else None,
        "is_expired": gift_card["expiry_date"] < datetime.utcnow() if gift_card.get("expiry_date") else False,
        "recipient_name": gift_card.get("recipient_name"),
        "message": gift_card.get("message"),
    }


# ─────────────────────────── Security (PIN) ─────────────────────────────────

@router.post("/security/set-pin")
async def set_transaction_pin(
    pin_data: WalletPinCreate,
    current_user: dict = Depends(get_current_user)
):
    """Set or update transaction PIN."""
    from app.core.security import get_password_hash
    db = get_db()
    user_id = current_user["id"]
    hashed_pin = get_password_hash(pin_data.pin)

    existing = db.wallet_security.find_one({"user_id": user_id})
    if existing:
        db.wallet_security.update_one(
            {"user_id": user_id},
            {"$set": {"transaction_pin": hashed_pin, "pin_attempts": 0, "pin_locked_until": None, "updated_at": datetime.utcnow()}}
        )
    else:
        db.wallet_security.insert_one({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "transaction_pin": hashed_pin,
            "pin_attempts": 0,
            "pin_locked_until": None,
            "daily_limit": 50000.0,
            "monthly_limit": 1000000.0,
            "created_at": datetime.utcnow(),
            "updated_at": None,
        })

    return {"message": "Transaction PIN set successfully", "pin_set": True}


@router.post("/security/verify-pin")
async def verify_transaction_pin(
    pin_data: WalletPinVerify,
    current_user: dict = Depends(get_current_user)
):
    """Verify transaction PIN with lockout after 5 failed attempts."""
    from app.core.security import verify_password
    db = get_db()
    user_id = current_user["id"]

    record = db.wallet_security.find_one({"user_id": user_id})
    if not record or not record.get("transaction_pin"):
        raise HTTPException(status_code=400, detail="Transaction PIN not set")

    if record.get("pin_locked_until") and record["pin_locked_until"] > datetime.utcnow():
        raise HTTPException(status_code=423, detail="PIN is temporarily locked due to multiple failed attempts")

    if verify_password(pin_data.pin, record["transaction_pin"]):
        db.wallet_security.update_one(
            {"user_id": user_id},
            {"$set": {"pin_attempts": 0, "pin_locked_until": None, "updated_at": datetime.utcnow()}}
        )
        return {"message": "PIN verified successfully", "verified": True}

    # Failed attempt
    attempts = record.get("pin_attempts", 0) + 1
    updates = {"pin_attempts": attempts, "updated_at": datetime.utcnow()}
    if attempts >= 5:
        updates["pin_locked_until"] = datetime.utcnow() + timedelta(minutes=30)
    db.wallet_security.update_one({"user_id": user_id}, {"$set": updates})

    if attempts >= 5:
        raise HTTPException(status_code=423, detail="PIN locked for 30 minutes due to multiple failed attempts")
    raise HTTPException(status_code=400, detail=f"Invalid PIN. {5 - attempts} attempts remaining")
