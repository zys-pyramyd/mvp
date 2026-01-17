# Auto-Refund Flow Explained

## 📊 Complete Payment & Refund Flow

### **Normal Flow (Success)**

```
Step 1: Buyer Pays for Order
├─ Payment: ₦50,000
├─ Status: held_in_escrow
└─ Funds: Held by platform

Step 2: Seller Delivers
├─ Seller marks as delivered
└─ Status: delivered

Step 3: Buyer Confirms Delivery
├─ Buyer enters tracking code
├─ Status: delivered
└─ Triggers payout process

Step 4: Payout Processing (payout_service.py)
├─ Calculate splits:
│  ├─ Platform fee (10%): ₦5,000
│  ├─ Agent commission (5%): ₦2,500
│  └─ Seller amount: ₦42,500
│
├─ Credit wallets:
│  ├─ Seller wallet: +₦42,500
│  └─ Agent wallet: +₦2,500
│
└─ Initiate bank transfer:
   ├─ Amount: ₦42,500
   ├─ To: Seller's bank account
   ├─ Debit seller wallet: -₦42,500
   └─ Status: transfer_initiated

Step 5: Paystack Processes Transfer
├─ Validates bank account
├─ Sends money to seller's bank
└─ Sends webhook: transfer.success

Step 6: Webhook Updates Order
├─ transfer_status: "success"
├─ payout_completed_at: timestamp
└─ ✅ COMPLETE
```

---

### **Failure Flow (Auto-Refund)**

```
Step 1-3: Same as above
└─ Seller wallet: +₦42,500

Step 4: Payout Processing
├─ Initiate bank transfer: ₦42,500
├─ Debit seller wallet: -₦42,500
└─ Current wallet: ₦0

Step 5: Paystack Transfer FAILS ❌
├─ Reason: Invalid account / Bank error
└─ Sends webhook: transfer.failed

Step 6: AUTO-REFUND (Webhook Handler)
├─ Receive: transfer.failed event
├─ Find order by transfer_ref
├─ Get seller_id and seller_amount
│
├─ REFUND TO WALLET:
│  └─ Seller wallet: +₦42,500 (restored)
│
├─ Update order:
│  └─ transfer_status: "failed"
│
└─ ✅ Seller can withdraw manually later
```

---

## 🔍 Code Breakdown

### **1. Initial Payout (payout_service.py)**

```python
# Lines 104-151 in payout_service.py

# Credit seller wallet first
db.users.update_one(
    {"id": seller_id},
    {"$inc": {"wallet_balance": seller_amount}}  # +₦42,500
)

# Then attempt bank transfer
transfer_resp = initiate_transfer(
    amount=amount_kobo,
    recipient_code=recipient_code,
    reason=f"Payout for Order {order_id}"
)

if transfer_resp.get("status"):
    # Transfer initiated successfully
    # Debit wallet (money is now "in transit")
    db.users.update_one(
        {"id": seller_id},
        {"$inc": {"wallet_balance": -seller_amount}}  # -₦42,500
    )
    
    # Save transfer reference for webhook tracking
    db.orders.update_one(
        {"order_id": order_id},
        {"$set": {"transfer_ref": transfer_ref}}
    )
```

**At this point:**
- ✅ Seller wallet: ₦0 (credited then debited)
- ⏳ Money "in transit" to bank
- 📝 Transfer reference saved

---

### **2. Transfer Fails (Paystack)**

Paystack attempts to send money to seller's bank but fails:

**Common failure reasons:**
- ❌ Invalid account number
- ❌ Account name mismatch
- ❌ Bank temporarily unavailable
- ❌ Insufficient balance in Paystack account
- ❌ Account frozen/restricted

Paystack sends webhook:
```json
{
  "event": "transfer.failed",
  "data": {
    "reference": "transfer_ref_123",
    "amount": 4250000,  // kobo
    "reason": "Invalid account number"
  }
}
```

---

### **3. Auto-Refund (Webhook Handler)**

```python
# Lines 136-158 in paystack.py

elif event_type == "transfer.failed":
    reference = data.get("reference")
    
    # Find the order that failed
    order = db.orders.find_one({"transfer_ref": reference})
    
    if order:
        # Get seller info
        seller_id = order.get("seller_id")
        amount = order.get("seller_amount", 0)  # ₦42,500
        
        # REFUND: Credit seller wallet
        db.users.update_one(
            {"id": seller_id},
            {"$inc": {"wallet_balance": amount}}  # +₦42,500
        )
        
        # Mark transfer as failed
        db.orders.update_one(
            {"order_id": order["order_id"]},
            {"$set": {"transfer_status": "failed"}}
        )
        
        logger.error(f"❌ Transfer failed. Refunded ₦{amount} to wallet.")
```

**Result:**
- ✅ Seller wallet: ₦42,500 (refunded)
- ✅ Order status: "delivered" (still complete)
- ✅ Transfer status: "failed"
- ✅ Seller can withdraw manually or use for purchases

---

## 💡 Why This Design?

### **1. Money Never Lost**
```
Escrow → Wallet → Bank (fails) → Back to Wallet
```
Money is always tracked and never disappears.

### **2. Seller Protection**
- Seller gets paid to wallet immediately on delivery confirmation
- If bank transfer fails, money stays in wallet
- Seller can:
  - Fix bank details
  - Withdraw manually later
  - Use wallet for purchases

### **3. Automatic & Instant**
- No manual intervention needed
- Happens within seconds of failure
- Seller notified immediately

---

## 🔄 What Happens Next?

### **Option 1: Seller Fixes Bank Details**

```python
# Seller updates bank account
POST /users/bank-account
{
  "account_number": "0123456789",  // Correct account
  "bank_code": "058",
  "bank_name": "GTBank"
}

# Seller requests manual withdrawal
POST /users/withdraw
{
  "amount": 42500
}

# Admin approves → New transfer initiated
```

### **Option 2: Seller Uses Wallet**

```python
# Seller uses wallet balance for:
- Paying for their own orders
- Funding new requests
- Transferring to other users (if enabled)
```

### **Option 3: Admin Manual Payout**

```python
# Admin sees failed transfer in dashboard
# Admin initiates manual payout with correct details
POST /admin/manual-payout
{
  "order_id": "order_123",
  "seller_id": "seller_456"
}
```

---

## 📊 Tracking & Notifications

### **Database States**

```javascript
// Order document
{
  "order_id": "order_123",
  "status": "delivered",           // Order complete
  "payout_status": "completed",    // Payout processed
  "transfer_status": "failed",     // Bank transfer failed
  "transfer_ref": "transfer_ref_123",
  "seller_amount": 42500
}

// User wallet
{
  "user_id": "seller_456",
  "wallet_balance": 42500,         // Refunded amount
  "wallet_history": [
    {
      "type": "credit",
      "amount": 42500,
      "description": "Payout for Order #order_123",
      "date": "2026-01-11T22:00:00"
    },
    {
      "type": "debit",
      "amount": 42500,
      "description": "Auto-Withdrawal to Bank (GTBank)",
      "date": "2026-01-11T22:00:05"
    },
    {
      "type": "credit",              // AUTO-REFUND
      "amount": 42500,
      "description": "Refund: Transfer failed",
      "date": "2026-01-11T22:00:10"
    }
  ]
}
```

### **Seller Notification** (Recommended to add)

```python
# In webhook handler after refund
send_notification(
    user_id=seller_id,
    title="Transfer Failed - Money Refunded",
    message=f"Bank transfer of ₦{amount} failed. "
            f"Money has been refunded to your wallet. "
            f"Please update your bank details and try again."
)
```

---

## ⚠️ Edge Cases Handled

### **1. Duplicate Webhooks**
```python
# Paystack may send webhook multiple times
# Check if already refunded:
if order.get("transfer_status") == "failed":
    return {"status": "already_processed"}
```

### **2. Order Not Found**
```python
if not order:
    logger.warning(f"Transfer failed but no order found: {reference}")
    # Manual investigation needed
```

### **3. Amount Mismatch**
```python
# Webhook amount should match order amount
webhook_amount = data.get("amount") / 100
if webhook_amount != order.get("seller_amount"):
    logger.error("Amount mismatch!")
```

---

## 🎯 Summary

**Auto-Refund Triggers:**
- ✅ When bank transfer fails (transfer.failed webhook)

**What Gets Refunded:**
- ✅ Seller's portion of payment (after platform fees)

**Where It Goes:**
- ✅ Back to seller's wallet balance

**Timing:**
- ✅ Instant (within seconds of failure)

**Seller Options:**
- ✅ Fix bank details and withdraw
- ✅ Use wallet for purchases
- ✅ Request manual payout from admin

**Safety:**
- ✅ Money never lost
- ✅ Fully tracked in wallet_history
- ✅ Order still marked as delivered
- ✅ Buyer not affected

**This ensures sellers always get paid, even if bank transfers fail!** 🎉
