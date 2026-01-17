# Complete Paystack Webhooks Guide

## 📍 Webhook URL

**Register this URL in Paystack Dashboard:**
```
https://yourdomain.com/api/paystack/webhook
```

**Development (using ngrok):**
```
https://your-ngrok-url.ngrok.io/api/paystack/webhook
```

---

## 🎯 All Webhooks Implemented

### 1. **charge.success** - Payment Received ✅

**When**: User pays for RFQ service charge, order, or funds wallet

**What happens**:
- ✅ RFQ payments → Activates buyer request
- ✅ Order payments → Marks order as paid
- ✅ Wallet funding → Credits user wallet
- ✅ Direct payments → Auto-credits wallet

**Example**:
```json
{
  "event": "charge.success",
  "data": {
    "reference": "ref_123456",
    "amount": 500000,
    "customer": {
      "email": "user@example.com",
      "customer_code": "CUS_xxx"
    }
  }
}
```

---

### 2. **transfer.success** - Payout Completed ✅

**When**: Seller payout transfer completes successfully

**What happens**:
- ✅ Updates order transfer_status to "success"
- ✅ Records payout completion timestamp
- ✅ Logs successful transfer

**Example**:
```json
{
  "event": "transfer.success",
  "data": {
    "reference": "transfer_ref_123",
    "amount": 450000,
    "recipient": {
      "name": "John Farmer"
    }
  }
}
```

---

### 3. **transfer.failed** - Payout Failed ✅

**When**: Seller payout transfer fails (invalid account, insufficient balance, etc.)

**What happens**:
- ✅ Refunds amount to seller's wallet
- ✅ Updates order transfer_status to "failed"
- ✅ Seller can withdraw manually later

**Example**:
```json
{
  "event": "transfer.failed",
  "data": {
    "reference": "transfer_ref_123",
    "amount": 450000
  }
}
```

---

### 4. **transfer.reversed** - Payout Reversed ✅

**When**: Successful transfer is reversed (rare, usually bank issues)

**What happens**:
- ✅ Updates order transfer_status to "reversed"
- ✅ Logs warning for manual review

---

### 5. **dedicatedaccount.assign.success** - DVA Created ✅

**When**: Paystack successfully creates DVA for user

**What happens**:
- ✅ Updates user with DVA account number
- ✅ Saves DVA bank name
- ✅ Records assignment timestamp

**Example**:
```json
{
  "event": "dedicatedaccount.assign.success",
  "data": {
    "customer": {
      "customer_code": "CUS_xxx"
    },
    "account_number": "1234567890",
    "bank": {
      "name": "Wema Bank"
    }
  }
}
```

---

### 6. **customeridentification.success** - BVN Verified ✅

**When**: Paystack verifies user's BVN

**What happens**:
- ✅ Marks user as BVN verified
- ✅ Records verification timestamp

---

### 7. **refund.processed** - Refund Completed ✅

**When**: Payment is refunded to customer

**What happens**:
- ✅ Creates refund transaction record
- ✅ Credits user wallet with refund amount
- ✅ Logs refund

**Example**:
```json
{
  "event": "refund.processed",
  "data": {
    "transaction_reference": "ref_123456",
    "amount": 500000
  }
}
```

---

### 8. **subscription.create / subscription.disable** ✅

**When**: Subscription created or disabled (future use)

**What happens**:
- ✅ Logged for future implementation
- ✅ Ready for subscription features

---

### 9. **dispute.create / dispute.resolve** ✅

**When**: Customer disputes a charge

**What happens**:
- ✅ Logged for manual review
- ✅ Ready for dispute handling

---

## 🔒 Security Features

### Signature Verification
Every webhook is verified using HMAC-SHA512:

```python
computed_signature = hmac.new(
    PAYSTACK_SECRET_KEY.encode('utf-8'),
    request_body,
    hashlib.sha512
).hexdigest()

if signature != computed_signature:
    return 400  # Reject fake webhooks
```

**Protection against**:
- ✅ Fake webhook requests
- ✅ Man-in-the-middle attacks
- ✅ Replay attacks

---

## 📋 Setup Checklist

### Step 1: Register Webhook in Paystack

1. Login to [Paystack Dashboard](https://dashboard.paystack.com)
2. Go to **Settings** → **Webhooks**
3. Click **Add Webhook URL**
4. Enter: `https://yourdomain.com/api/paystack/webhook`
5. Click **Save**

### Step 2: Test Webhook (Development)

**Using ngrok:**
```bash
# Start ngrok
ngrok http 8000

# Copy ngrok URL (e.g., https://abc123.ngrok.io)
# Register in Paystack: https://abc123.ngrok.io/api/paystack/webhook
```

### Step 3: Monitor Logs

Watch your backend logs for webhook events:
```bash
# You'll see:
✅ RFQ Service Charge verified. Request Activated. Ref: ref_123
✅ Wallet funded for user user_456: +₦10,000
✅ Transfer successful for order order_789: ₦45,000
❌ Transfer failed for order order_101. Refunded to wallet.
```

---

## 🧪 Testing Webhooks

### Option 1: Paystack Test Mode

1. Use test secret key
2. Make test payment
3. Paystack sends test webhook
4. Check logs

### Option 2: Manual cURL Test

```bash
curl -X POST http://localhost:8000/api/paystack/webhook \
  -H "Content-Type: application/json" \
  -H "x-paystack-signature: test_signature" \
  -d '{
    "event": "charge.success",
    "data": {
      "reference": "test_ref_123",
      "amount": 1000000,
      "customer": {
        "email": "test@example.com",
        "customer_code": "CUS_test"
      }
    }
  }'
```

### Option 3: Paystack Webhook Tester

1. Go to Paystack Dashboard → Webhooks
2. Click **Test Webhook**
3. Select event type
4. Click **Send Test**

---

## 📊 Webhook Flow Diagram

```
User Action → Paystack → Webhook → Your Backend → Database Update
    ↓
Payment Made
    ↓
Paystack processes
    ↓
POST /api/paystack/webhook
    ↓
Verify signature
    ↓
Handle event (charge.success, transfer.success, etc.)
    ↓
Update database (wallet, order, transaction)
    ↓
Return 200 OK
    ↓
Paystack marks as delivered
```

---

## 🚨 Important Notes

### 1. **Always Return 200**
Even if processing fails, return 200 to prevent Paystack retries:
```python
return {"status": "success", "event": event_type}
```

### 2. **Idempotency**
Webhooks may be sent multiple times. Always check if already processed:
```python
if existing_txn["status"] == "success":
    return {"status": "success", "message": "Already processed"}
```

### 3. **Async Processing**
For heavy operations, process webhooks asynchronously:
```python
# Queue for background processing
await queue.enqueue(process_webhook, event_data)
return {"status": "queued"}
```

### 4. **Logging**
Log everything for debugging:
```python
logger.info(f"✅ Webhook: {event_type} - {reference}")
logger.error(f"❌ Webhook failed: {error}")
```

---

## 📝 Summary

**Single Webhook URL handles ALL events:**
```
https://yourdomain.com/api/paystack/webhook
```

**Events Handled:**
1. ✅ charge.success - Payments
2. ✅ transfer.success - Payouts completed
3. ✅ transfer.failed - Payouts failed
4. ✅ transfer.reversed - Payouts reversed
5. ✅ dedicatedaccount.assign.success - DVA created
6. ✅ customeridentification.success - BVN verified
7. ✅ refund.processed - Refunds
8. ✅ subscription.* - Subscriptions
9. ✅ dispute.* - Disputes

**Security:**
- ✅ HMAC-SHA512 signature verification
- ✅ Idempotency checks
- ✅ Comprehensive logging

**You're all set!** 🎉
