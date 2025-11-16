# Platform Commission Quick Reference Card

## 🎯 At a Glance

| Platform | Vendor Gets | Vendor Pays | Buyer Pays Extra | Platform Total Revenue |
|----------|-------------|-------------|------------------|------------------------|
| **FARMHUB** | 90% | 10% | 0% | 10% + delivery |
| **HOME** | 97.5% | 2.5% | 3% | 5.5% + delivery |
| **COMMUNITY** | 97.5% | 2.5% | 5% | 7.5% + delivery |

---

## 💰 Example: ₦10,000 Product Sale

### FARMHUB
```
Vendor Lists: ₦10,000
Vendor Gets:  ₦9,000 (90%)
Buyer Pays:   ₦10,000 + delivery
Platform:     ₦1,000 + delivery
```

### HOME
```
Vendor Lists: ₦10,000
Vendor Gets:  ₦9,750 (97.5%)
Buyer Pays:   ₦10,300 + delivery (₦10k + ₦300 service)
Platform:     ₦550 + delivery (₦250 from vendor + ₦300 from buyer)
```

### COMMUNITY
```
Vendor Lists: ₦10,000
Vendor Gets:  ₦9,750 (97.5%)
Buyer Pays:   ₦10,500 + delivery (₦10k + ₦500 service)
Platform:     ₦750 + delivery (₦250 from vendor + ₦500 from buyer)
```

---

## 🔑 Key API Endpoints

### Get Vendor Charges (Transparency)
```bash
GET /api/platform/vendor-charges?platform_type=home
```

### Calculate Delivery Fee
```bash
POST /api/delivery/calculate-fee
Body: {
  "product_total": 10000,
  "buyer_state": "Lagos",
  "platform_type": "home",
  "quantity": 5,
  "buyer_location": "123 Street, Ikeja",
  "buyer_city": "Lagos",
  "seller_location": "456 Road, Oyo",
  "seller_city": "Oyo"
}
```

### Initialize Payment
```bash
POST /api/paystack/transaction/initialize
Body: {
  "product_total": 10000,
  "customer_state": "Lagos",
  "quantity": 5,
  "platform_type": "home",
  "buyer_location": "123 Street",
  "buyer_city": "Lagos",
  "seller_location": "456 Road",
  "seller_city": "Oyo",
  "subaccount_code": "ACCT_xxx"
}
```

---

## 📝 Constants in Backend

```python
# Commission rates (backend/server.py lines 61-73)
FARMHUB_SERVICE_CHARGE = 0.10
HOME_VENDOR_COMMISSION = 0.025
HOME_BUYER_SERVICE_CHARGE = 0.03
COMMUNITY_VENDOR_COMMISSION = 0.025
COMMUNITY_BUYER_SERVICE_CHARGE = 0.05
```

---

## 🎨 Frontend Order Summary

```javascript
// Calculate service charges (App.js lines 2253-2263)
if (isCommunity) {
  platformServiceCharge += itemTotal * 0.05;  // 5%
} else if (isFarmHub) {
  platformServiceCharge += itemTotal * 0.10;  // 10%
} else {
  platformServiceCharge += itemTotal * 0.03;  // 3%
}
```

---

## ⚠️ Important Notes

1. **Vendor commissions** are EXTRACTED from vendor's sales
2. **Buyer service charges** are ADDED to buyer's total
3. **Delivery fees** go entirely to platform
4. **All percentages** apply to product price only (not including delivery)
5. **Agent commissions** (4%) are separate, paid from platform revenue

---

## 📱 Vendor Transparency Message

**Before product posting, show:**

> ⚠️ **IMPORTANT:** On [HOME/COMMUNITY], you receive 97.5% of your product price. The [3%/5%] service charge is paid by the buyer, not deducted from your sales.

**Example for ₦10,000 product:**
- You receive: ₦9,750
- Buyer pays: ₦10,[300/500] + delivery
- Platform gets: ₦[550/750] + delivery

---

## 🧪 Testing Checklist

### Quick Tests
- [ ] HOME: Vendor gets ₦9,750 from ₦10k sale
- [ ] COMMUNITY: Buyer pays ₦10,500 for ₦10k product (before delivery)
- [ ] FARMHUB: Vendor gets ₦9,000 from ₦10k sale
- [ ] `/api/platform/vendor-charges` works for all platforms
- [ ] Order summary shows service charge, not commission

---

## 📊 Platform Revenue Comparison

For ₦10,000 product sale (excluding delivery):

| Platform | From Vendor | From Buyer | Total |
|----------|-------------|------------|-------|
| FARMHUB | ₦1,000 (10%) | ₦0 | ₦1,000 |
| HOME | ₦250 (2.5%) | ₦300 (3%) | ₦550 |
| COMMUNITY | ₦250 (2.5%) | ₦500 (5%) | ₦750 |

**Why this structure?**
- HOME vendors are more competitive → lower commission, moderate buyer fee
- COMMUNITY targets local markets → higher buyer service charge
- FARMHUB serves farmers → single service charge from vendor
