# Pyramyd Platform - Paystack Payment Integration

## 🏦 Payment Architecture Overview

### Payment Flow Types

1. **FarmHub (PyHub) - Agent-Managed Farmers**
   - Platform Revenue: 10% service + delivery fee
   - Product Payout: Sophie Farms Investment Ltd Subaccount
   - Buyer Commission: 4% (if agent) via Transfer API

2. **Community Marketplace**
   - Platform Revenue: 2.5% commission + 10% service + delivery fee
   - Product Payout: Vendor's Subaccount
   - Buyer Commission: 4% (if agent) via Transfer API

3. **Group Buy (Special Case)**
   - If initiator is NOT a purchasing agent: 4% discount (deducted from platform cut)
   - If initiator IS a purchasing agent: Standard agent commission applies

---

## 📊 Commission Structure (All amounts in Kobo)

### FarmHub Calculation:
```python
product_total_kobo = product_price * 100
service_charge_kobo = product_total_kobo * 0.10  # 10%
delivery_fee_kobo = delivery_fee * 100

platform_cut = service_charge_kobo + delivery_fee_kobo
total_amount = product_total_kobo + platform_cut

# If buyer is agent:
agent_commission = product_total_kobo * 0.04  # 4%
# Paid later via Transfer API from platform balance
```

### Community Calculation:
```python
product_total_kobo = product_price * 100
commission_kobo = product_total_kobo * 0.025  # 2.5%
service_kobo = product_total_kobo * 0.10  # 10%
delivery_fee_kobo = delivery_fee * 100

platform_cut = commission_kobo + service_kobo + delivery_fee_kobo
total_amount = product_total_kobo + platform_cut

# If buyer is agent:
agent_commission = product_total_kobo * 0.04  # 4%
# Paid later via Transfer API from platform balance
```

---

## 🔑 API Endpoints

### 1. Create Subaccount (One-time per vendor)

**Endpoint:** `POST /api/paystack/subaccount/create`

**When to Use:**
- When vendor/farmer/community registers bank details
- Required before they can receive payments

**Request Body:**
```json
{
  "business_name": "Green Farms Ltd",
  "account_number": "0123456789",
  "bank_code": "057",
  "bank_name": "Zenith Bank"
}
```

**Response:**
```json
{
  "message": "Subaccount created successfully",
  "subaccount_code": "ACCT_xxxxxxxxxx"
}
```

**Important:** Store `subaccount_code` - needed for all future transactions!

---

### 2. Get List of Banks

**Endpoint:** `GET /api/paystack/banks`

**Use:** Get bank codes for subaccount creation

**Response:**
```json
{
  "status": true,
  "banks": [
    {
      "name": "Zenith Bank",
      "code": "057",
      "slug": "zenith-bank"
    },
    {
      "name": "GTBank Plc",
      "code": "058",
      "slug": "gtbank-plc"
    }
    // ... more banks
  ]
}
```

---

### 3. Initialize Payment

**Endpoint:** `POST /api/paystack/transaction/initialize`

**When to Use:**
- When buyer clicks "Pay Now" / "Checkout"
- Calculates split automatically based on platform type

**Request Body:**
```json
{
  "product_total": 5000.00,
  "delivery_fee": 500.00,
  "subaccount_code": "ACCT_xxxxxxxxxx",
  "product_id": "prod_12345",
  "order_id": "order_67890",
  "platform_type": "farmhub",
  "callback_url": "https://yoursite.com/payment/callback"
}
```

**Parameters:**
- `product_total`: Product price in Naira
- `delivery_fee`: Delivery cost in Naira
- `subaccount_code`: Vendor's subaccount (from step 1)
- `platform_type`: `"farmhub"` or `"community"`
- `callback_url`: Where to redirect after payment

**Response:**
```json
{
  "status": true,
  "message": "Payment initialized",
  "authorization_url": "https://checkout.paystack.com/...",
  "access_code": "xxxxxx",
  "reference": "PYR_ABC123456789",
  "amount": 6050.00,
  "breakdown": {
    "product_total": 5000.00,
    "delivery_fee": 500.00,
    "platform_cut": 1050.00,
    "agent_commission": 200.00
  }
}
```

**Next Step:** Redirect buyer to `authorization_url`

---

### 4. Verify Transaction

**Endpoint:** `GET /api/paystack/transaction/verify/{reference}`

**When to Use:**
- After payment completion (callback)
- To confirm payment status

**Response:**
```json
{
  "status": true,
  "transaction": {
    "reference": "PYR_ABC123456789",
    "payment_status": "success",
    "total_amount": 605000,
    "product_total": 500000,
    "platform_cut": 105000,
    "agent_commission": 20000,
    "buyer_is_agent": true
  },
  "paystack_data": {
    "status": "success",
    "amount": 605000,
    // ... full Paystack response
  }
}
```

---

### 5. Webhook Handler

**Endpoint:** `POST /api/paystack/webhook`

**Purpose:** Receive real-time payment notifications from Paystack

**Paystack Configuration:**
1. Go to Paystack Dashboard → Settings → Webhooks
2. Add URL: `https://yourapi.com/api/paystack/webhook`
3. Copy webhook secret (for signature verification)

**Events Handled:**
- `charge.success` - Payment successful
  - Updates transaction status
  - Creates commission payout record for agents

**Security:** Verifies `x-paystack-signature` header

---

## 💸 Commission Payout System

### How Agent Commissions Are Paid

1. **During Payment:**
   - Platform receives full `transaction_charge` amount
   - Agent commission (4%) is NOT deducted at payment time
   - Commission record is created in `commission_payouts` collection

2. **Batch Payout (Manual/Scheduled):**
   - Admin reviews pending commissions
   - Transfers are initiated via Paystack Transfer API
   - Commissions can be consolidated (e.g., weekly payouts)

### Commission Flow:
```
Payment → Platform Balance → Transfer to Agent
```

**Why Not Direct Split?**
- Allows commission consolidation
- Better cash flow management
- Can apply minimum payout thresholds
- Easier commission dispute resolution

---

## 🔐 Security Considerations

### 1. Webhook Signature Verification
```python
def verify_paystack_signature(payload: bytes, signature: str) -> bool:
    computed = hmac.new(
        PAYSTACK_SECRET_KEY.encode(),
        payload,
        hashlib.sha512
    ).hexdigest()
    return hmac.compare_digest(computed, signature)
```

### 2. Transaction Amount Validation
Always verify:
- Amount matches expected value
- Status is "success"
- Reference hasn't been processed before

### 3. Idempotency
- Use unique references for each transaction
- Check if reference already processed in webhook
- Prevent double-processing

---

## 📱 Frontend Integration

### Step 1: Initialize Payment
```javascript
const response = await fetch('/api/paystack/transaction/initialize', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    product_total: 5000,
    delivery_fee: 500,
    subaccount_code: 'ACCT_xxx',
    product_id: 'prod_123',
    platform_type: 'farmhub',
    callback_url: window.location.origin + '/payment/callback'
  })
});

const data = await response.json();
```

### Step 2: Redirect to Paystack
```javascript
if (data.status) {
  window.location.href = data.authorization_url;
}
```

### Step 3: Handle Callback
```javascript
// On your callback page
const urlParams = new URLSearchParams(window.location.search);
const reference = urlParams.get('reference');

if (reference) {
  const verify = await fetch(`/api/paystack/transaction/verify/${reference}`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  
  const result = await verify.json();
  
  if (result.transaction.payment_status === 'success') {
    // Show success message
    // Update order status
    // Redirect to order confirmation
  }
}
```

---

## 🧪 Testing

### Test Cards (Paystack Test Mode)

**Success:**
```
Card Number: 5078 5078 5078 5078 04
CVV: 884
Expiry: Any future date
PIN: 1234
OTP: 123456
```

**Failed:**
```
Card Number: 5078 5078 5078 5078 04
CVV: 884
Expiry: Any future date
PIN: 0000
```

### Test Flow:
1. Create test subaccount
2. Initialize payment
3. Use test card
4. Verify transaction
5. Check webhook logs

---

## 📊 Database Collections

### `paystack_subaccounts`
```javascript
{
  id: "uuid",
  user_id: "user_uuid",
  subaccount_code: "ACCT_xxx",
  business_name: "Vendor Name",
  account_number: "0123456789",
  bank_code: "057",
  bank_name: "Zenith Bank",
  is_active: true,
  created_at: ISODate()
}
```

### `paystack_transactions`
```javascript
{
  id: "uuid",
  reference: "PYR_ABC123",
  buyer_id: "user_uuid",
  product_total: 500000,  // kobo
  platform_cut: 105000,   // kobo
  total_amount: 605000,   // kobo
  subaccount_code: "ACCT_xxx",
  buyer_is_agent: true,
  agent_commission: 20000,  // kobo
  payment_status: "success",
  authorization_url: "https://...",
  verified_at: ISODate()
}
```

### `commission_payouts`
```javascript
{
  id: "uuid",
  transaction_id: "trans_uuid",
  recipient_user_id: "agent_uuid",
  amount: 20000,  // kobo
  status: "pending",
  reason: "Agent buyer commission (4%)",
  created_at: ISODate(),
  paid_at: null
}
```

---

## 🚨 Error Handling

### Common Errors:

1. **"Subaccount not found"**
   - Vendor hasn't created subaccount yet
   - Prompt to add bank details

2. **"Invalid bank code"**
   - Use `/api/paystack/banks` to get valid codes
   - Don't hardcode bank codes

3. **"Insufficient funds"**
   - Customer card issue
   - Try different payment method

4. **"Webhook signature mismatch"**
   - Check `PAYSTACK_SECRET_KEY` is correct
   - Ensure raw body is used for signature verification

---

## 📈 Monitoring & Analytics

### Key Metrics to Track:
- Transaction success rate
- Average transaction value
- Commission payouts pending
- Platform revenue
- Failed payment reasons

### Queries:
```javascript
// Total platform revenue (last 30 days)
db.paystack_transactions.aggregate([
  {
    $match: {
      payment_status: "success",
      created_at: { $gte: new Date(Date.now() - 30*24*60*60*1000) }
    }
  },
  {
    $group: {
      _id: null,
      total_revenue: { $sum: "$platform_cut" }
    }
  }
])

// Pending commissions
db.commission_payouts.aggregate([
  {
    $match: { status: "pending" }
  },
  {
    $group: {
      _id: null,
      total_pending: { $sum: "$amount" },
      count: { $sum: 1 }
    }
  }
])
```

---

## 🔄 Production Checklist

- [ ] Switch to live Paystack keys
- [ ] Update webhook URL in Paystack dashboard
- [ ] Test with real bank account
- [ ] Set up commission payout schedule
- [ ] Enable transaction monitoring
- [ ] Set up email notifications for failures
- [ ] Configure rate limiting on payment endpoints
- [ ] Set up backup webhook endpoint
- [ ] Document payout reconciliation process
- [ ] Train support team on payment issues

---

**Last Updated:** 2024  
**Review Schedule:** Monthly  
**Contact:** payments@pyramyd.com
