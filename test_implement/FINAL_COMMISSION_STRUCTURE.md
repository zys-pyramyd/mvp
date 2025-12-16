# Final Platform Commission Structure with Vendor Transparency

## Summary
Complete platform commission structure with vendor transparency features. All platforms now show vendors exactly what they'll pay and receive **before** posting products.

---

## Platform Commission Breakdown

### 🌾 FARMHUB (Farm Deals)
**Target Users:** Farmers, Agricultural Agents

**Commission Structure:**
- **Vendor Commission:** 10% (extracted from vendor's sales)
- **Buyer Service Charge:** 0%
- **Vendor Receives:** 90% of product price
- **Platform Gets:** 10% + delivery fees

**Example Transaction (₦10,000 product):**
```
Product Price:              ₦10,000
Vendor Commission (10%):    -₦1,000
────────────────────────────────────
Vendor Receives:            ₦9,000
Buyer Pays (Product):       ₦10,000
Buyer Pays (Service):       ₦0
Buyer Pays (Delivery):      Varies
────────────────────────────────────
Platform Revenue:           ₦1,000 + Delivery
```

---

### 🏠 HOME (PyExpress)
**Target Users:** Business, Food Suppliers, Processors

**Commission Structure:**
- **Vendor Commission:** 2.5% (extracted from vendor's sales)
- **Buyer Service Charge:** 3% (paid by buyer, on top of product price)
- **Vendor Receives:** 97.5% of product price
- **Platform Gets:** 2.5% (from vendor) + 3% (from buyer) + delivery fees

**Example Transaction (₦10,000 product):**
```
Product Price:              ₦10,000
Vendor Commission (2.5%):   -₦250
────────────────────────────────────
Vendor Receives:            ₦9,750 (97.5%)

Buyer Breakdown:
Product Price:              ₦10,000
Service Charge (3%):        +₦300
Delivery Fee:               +Varies
────────────────────────────────────
Buyer Pays Total:           ₦10,300 + Delivery

Platform Revenue:
From Vendor (2.5%):         ₦250
From Buyer (3%):            ₦300
Delivery Fee:               Varies
────────────────────────────────────
Total Platform Revenue:     ₦550 + Delivery
```

**⚠️ Vendor Transparency Note:**
*"You receive 97.5% of your product price. The 3% service charge is paid by the buyer, not deducted from your sales."*

---

### 👥 COMMUNITY
**Target Users:** Community Vendors, Local Sellers

**Commission Structure:**
- **Vendor Commission:** 2.5% (extracted from vendor's sales)
- **Buyer Service Charge:** 5% (paid by buyer, on top of product price)
- **Vendor Receives:** 97.5% of product price
- **Platform Gets:** 2.5% (from vendor) + 5% (from buyer) + delivery fees

**Example Transaction (₦10,000 product):**
```
Product Price:              ₦10,000
Vendor Commission (2.5%):   -₦250
────────────────────────────────────
Vendor Receives:            ₦9,750 (97.5%)

Buyer Breakdown:
Product Price:              ₦10,000
Service Charge (5%):        +₦500
Delivery Fee:               +Varies
────────────────────────────────────
Buyer Pays Total:           ₦10,500 + Delivery

Platform Revenue:
From Vendor (2.5%):         ₦250
From Buyer (5%):            ₦500
Delivery Fee:               Varies
────────────────────────────────────
Total Platform Revenue:     ₦750 + Delivery
```

**⚠️ Vendor Transparency Note:**
*"You receive 97.5% of your product price. The 5% service charge is paid by the buyer, not deducted from your sales."*

---

## Implementation Details

### Backend Changes (`backend/server.py`)

#### 1. Updated Commission Constants (Lines 61-73)
```python
# Commission rates
AGENT_BUYER_COMMISSION_RATE = 0.04  # 4% for agent buyers

# FARMHUB: 10% service charge (extracted from vendor, vendor gets 90%)
FARMHUB_SERVICE_CHARGE = 0.10

# HOME: 2.5% commission (from vendor) + 3% service charge (from buyer)
HOME_VENDOR_COMMISSION = 0.025  # Extracted from vendor's sales, vendor gets 97.5%
HOME_BUYER_SERVICE_CHARGE = 0.03  # Paid by buyer on top of product price

# COMMUNITY: 2.5% commission (from vendor) + 5% service charge (from buyer)
COMMUNITY_VENDOR_COMMISSION = 0.025  # Extracted from vendor's sales, vendor gets 97.5%
COMMUNITY_BUYER_SERVICE_CHARGE = 0.05  # Paid by buyer on top of product price
```

#### 2. Updated Payment Calculation (Lines 7756-7772)
```python
# Calculate platform cut based on type
if platform_type == "farmhub":
    # FarmHub: 10% service charge (extracted from vendor) + delivery
    # Vendor receives 90% of product total
    service_kobo = int(product_total_kobo * FARMHUB_SERVICE_CHARGE)
    platform_cut_kobo = service_kobo + delivery_fee_kobo
elif platform_type == "home":
    # HOME: 2.5% commission (from vendor) + 3% service charge (from buyer) + delivery
    # Vendor receives 97.5% of product total
    vendor_commission_kobo = int(product_total_kobo * HOME_VENDOR_COMMISSION)
    buyer_service_kobo = int(product_total_kobo * HOME_BUYER_SERVICE_CHARGE)
    platform_cut_kobo = vendor_commission_kobo + buyer_service_kobo + delivery_fee_kobo
else:
    # Community: 2.5% commission (from vendor) + 5% service charge (from buyer) + delivery
    # Vendor receives 97.5% of product total
    vendor_commission_kobo = int(product_total_kobo * COMMUNITY_VENDOR_COMMISSION)
    buyer_service_kobo = int(product_total_kobo * COMMUNITY_BUYER_SERVICE_CHARGE)
    platform_cut_kobo = vendor_commission_kobo + buyer_service_kobo + delivery_fee_kobo
```

#### 3. New Vendor Transparency Endpoint (Lines 2545-2640)
**Endpoint:** `GET /api/platform/vendor-charges?platform_type=home`

**Query Parameters:**
- `platform_type`: "home", "farmhub", or "community"

**Response Example (HOME):**
```json
{
  "platform": "HOME (PyExpress)",
  "platform_type": "home",
  "vendor_commission": {
    "rate": "2.5%",
    "description": "Commission extracted from your sales",
    "example": "If you sell ₦10,000 worth of products, ₦250 goes to platform"
  },
  "buyer_service_charge": {
    "rate": "3%",
    "description": "Service charge paid by buyer (added to their total)",
    "example": "Buyer pays ₦10,000 product + ₦300 service charge"
  },
  "vendor_receives": "97.5% of product price",
  "buyer_sees": "Product price + 3% service charge + delivery",
  "delivery_fees": "Platform manages delivery (varies by distance, capped at ₦40,000)",
  "transparency_note": "⚠️ IMPORTANT: You receive 97.5% of your product price. The 3% service charge is paid by the buyer, not deducted from your sales.",
  "example_calculation": {
    "product_price": 10000,
    "vendor_commission_deducted": 250,
    "vendor_receives": 9750,
    "buyer_pays_product": 10000,
    "buyer_pays_service_charge": 300,
    "buyer_pays_delivery": "Varies",
    "total_platform_revenue": "₦250 (from vendor) + ₦300 (from buyer) + delivery = ₦550 + delivery",
    "note": "Vendor gets 97.5%, buyer pays 3% service charge, platform gets both"
  }
}
```

### Frontend Changes (`frontend/src/App.js`)

#### 1. Updated Order Summary Calculation (Lines 2253-2263)
```javascript
// Calculate platform charges based on type
if (isCommunity) {
  // Community: 5% service charge (paid by buyer)
  platformServiceCharge += itemTotal * 0.05;
} else if (isFarmHub) {
  // FarmHub: 10% service charge only
  platformServiceCharge += itemTotal * 0.10;
} else {
  // Home/PyExpress: 3% service charge (paid by buyer)
  platformServiceCharge += itemTotal * 0.03;
}
```

---

## Vendor Transparency Features

### 1. Pre-Product Posting Information
Before vendors post products, they can call `/api/platform/vendor-charges` to see:
- Exact commission rate they'll pay
- Service charge buyers will see
- Clear examples with real numbers
- Transparency note explaining the charge structure

### 2. Product Creation Form Integration
**Frontend should display:**
```
┌─────────────────────────────────────────┐
│  📋 Platform Charges for HOME           │
├─────────────────────────────────────────┤
│  Your Commission: 2.5%                  │
│  You'll receive: 97.5% of sales         │
│                                         │
│  Buyer Service Charge: 3%               │
│  (Paid by buyer, not you)               │
│                                         │
│  Example: If you sell ₦10,000          │
│  • You receive: ₦9,750                 │
│  • Buyer pays: ₦10,300 + delivery      │
│  • Platform gets: ₦550 + delivery      │
└─────────────────────────────────────────┘
```

### 3. Order Confirmation Display
**Buyer sees:**
```
Product Total:        ₦10,000
Service Charge (3%):  ₦300
Delivery Fee:         ₦2,500
─────────────────────────────
Total:                ₦12,800
```

**Vendor sees in their dashboard:**
```
Sale Amount:          ₦10,000
Platform Fee (2.5%):  -₦250
─────────────────────────────
You Receive:          ₦9,750
```

---

## Testing Checklist

### Backend Testing
- [ ] Test FARMHUB charges 10% from vendor only
- [ ] Test HOME charges 2.5% from vendor + 3% from buyer
- [ ] Test COMMUNITY charges 2.5% from vendor + 5% from buyer
- [ ] Verify `/api/platform/vendor-charges` returns correct info for all platforms
- [ ] Test payment calculation with sample transactions
- [ ] Verify vendor receives exactly 97.5% for HOME/COMMUNITY

### Frontend Testing
- [ ] Order summary shows correct service charges (3% HOME, 5% COMMUNITY, 10% FARMHUB)
- [ ] Vendor transparency info displays before product posting
- [ ] Checkout shows service charge as separate line item
- [ ] Commission labels don't show on order summary (only service charges visible to buyers)

### Integration Testing
- [ ] Complete HOME purchase: Verify vendor gets 97.5%, platform gets 2.5% + 3% + delivery
- [ ] Complete COMMUNITY purchase: Verify vendor gets 97.5%, platform gets 2.5% + 5% + delivery
- [ ] Complete FARMHUB purchase: Verify vendor gets 90%, platform gets 10% + delivery
- [ ] Test with Paystack split payment
- [ ] Verify email notifications include correct amounts

---

## API Endpoints Summary

### 1. Get Vendor Platform Charges
```
GET /api/platform/vendor-charges?platform_type=home
```
Returns transparent breakdown of charges before product posting.

### 2. Initialize Payment
```
POST /api/paystack/transaction/initialize
```
Updated to calculate correct commission and service charges per platform.

### 3. Calculate Delivery Fee
```
POST /api/delivery/calculate-fee
```
Already supports all parameters (buyer_city, buyer_location, seller_city, seller_location, quantity, platform_type).

---

## Database Considerations

### Transactions Collection
Stores complete breakdown:
```javascript
{
  product_total: Number,        // Product price in kobo
  delivery_fee: Number,         // Delivery in kobo
  platform_cut: Number,         // Total platform revenue (vendor commission + buyer service + delivery)
  vendor_share: Number,         // What vendor receives (97.5% or 90%)
  platform_type: String,        // "home", "farmhub", "community"
  ...
}
```

---

## Frontend Implementation Guide

### 1. Add Transparency Display Component
```jsx
// VendorChargesInfo.js
const VendorChargesInfo = ({ platformType }) => {
  const [charges, setCharges] = useState(null);
  
  useEffect(() => {
    fetch(`/api/platform/vendor-charges?platform_type=${platformType}`)
      .then(res => res.json())
      .then(data => setCharges(data));
  }, [platformType]);
  
  if (!charges) return <div>Loading...</div>;
  
  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <h3>💰 {charges.platform} Charges</h3>
      <p><strong>You Receive:</strong> {charges.vendor_receives}</p>
      <p><strong>Buyer Service Charge:</strong> {charges.buyer_service_charge.rate}</p>
      <p className="text-sm text-gray-600">{charges.transparency_note}</p>
      <div className="mt-2 bg-white p-3 rounded">
        <h4>Example:</h4>
        <p>Product: ₦{charges.example_calculation.product_price.toLocaleString()}</p>
        <p>You Get: ₦{charges.example_calculation.vendor_receives.toLocaleString()}</p>
        <p>Buyer Pays: ₦{charges.example_calculation.buyer_pays_product.toLocaleString()} + ₦{charges.example_calculation.buyer_pays_service_charge.toLocaleString()}</p>
      </div>
    </div>
  );
};
```

### 2. Update Product Creation Form
Add `<VendorChargesInfo platformType="home" />` before product submission.

### 3. Update Order Summary
Remove "Platform Commission" line (confusing to buyers), only show "Service Charge".

---

## Key Differences Between Platforms

| Feature | FARMHUB | HOME | COMMUNITY |
|---------|---------|------|-----------|
| Vendor Gets | 90% | 97.5% | 97.5% |
| Vendor Pays | 10% | 2.5% | 2.5% |
| Buyer Pays (Service) | 0% | 3% | 5% |
| Platform Gets (Total) | 10% + delivery | 5.5% + delivery | 7.5% + delivery |
| Delivery Area | Nationwide | Lagos, Oyo, Abuja | Nationwide |
| Delivery Time | 3-14 days | 24 hours | 3-14 days |

---

## Notes
- All percentages are calculated on **product price only**, not including delivery
- Delivery fees go entirely to the platform (covers logistics costs)
- Agent commissions (4%) are separate and paid from platform revenue
- Vendor commission is **extracted** (reduces what vendor receives)
- Buyer service charge is **additive** (increases what buyer pays)
- This ensures vendors get competitive rates while platform stays profitable
