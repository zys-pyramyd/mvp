# Service Charge Correction & Frontend Delivery Parameters Update

## Summary
Updated the platform to correctly handle HOME service charges (3%) and enhanced frontend to pass additional delivery calculation parameters to the backend.

## Changes Made

### Backend Updates (`backend/server.py`)

#### 1. Added HOME_SERVICE_CHARGE Constant
**Location:** Lines 61-66

```python
# Commission rates
AGENT_BUYER_COMMISSION_RATE = 0.04  # 4% for agent buyers
FARMHUB_SERVICE_CHARGE = 0.10  # 10% service charge
HOME_SERVICE_CHARGE = 0.03  # 3% service charge for HOME platform
COMMUNITY_COMMISSION = 0.025  # 2.5% commission (extracted from vendor's sales)
COMMUNITY_SERVICE = 0.10  # 10% service charge
```

#### 2. Updated Payment Platform Cut Calculation
**Location:** Lines 7747-7760 in `/api/paystack/transaction/initialize` endpoint

**Before:**
```python
# Calculate platform cut based on type
if platform_type == "farmhub":
    # FarmHub: 10% service + delivery
    platform_cut_kobo = int(product_total_kobo * FARMHUB_SERVICE_CHARGE) + delivery_fee_kobo
else:
    # Community/Home: 2.5% commission + 10% service + delivery
    commission_kobo = int(product_total_kobo * COMMUNITY_COMMISSION)
    service_kobo = int(product_total_kobo * COMMUNITY_SERVICE)
    platform_cut_kobo = commission_kobo + service_kobo + delivery_fee_kobo
```

**After:**
```python
# Calculate platform cut based on type
if platform_type == "farmhub":
    # FarmHub: 10% service + delivery
    platform_cut_kobo = int(product_total_kobo * FARMHUB_SERVICE_CHARGE) + delivery_fee_kobo
elif platform_type == "home":
    # HOME: 3% service charge + delivery
    service_kobo = int(product_total_kobo * HOME_SERVICE_CHARGE)
    platform_cut_kobo = service_kobo + delivery_fee_kobo
else:
    # Community: 2.5% commission (extracted from vendor) + delivery
    # The 2.5% is taken from the vendor's product total, so vendor gets 97.5%
    commission_kobo = int(product_total_kobo * COMMUNITY_COMMISSION)
    platform_cut_kobo = commission_kobo + delivery_fee_kobo
```

### Frontend Updates (`frontend/src/App.js`)

#### 1. Fixed HOME Service Charge in Order Summary Calculation
**Location:** Lines 2253-2265 in `calculateOrderSummary()` function

**Changed:**
- HOME/PyExpress: From 2.5% commission + 10% service → **3% service charge only**
- Community: From 2.5% commission + 10% service → **2.5% commission only** (correctly reflects that commission is extracted from vendor sales)

```javascript
// Calculate platform charges based on type
if (isCommunity) {
  // Community: 2.5% commission (extracted from vendor sales)
  platformCommission += itemTotal * 0.025;
} else if (isFarmHub) {
  // FarmHub: 10% service charge only
  platformServiceCharge += itemTotal * 0.10;
} else {
  // Home/PyExpress: 3% service charge
  platformServiceCharge += itemTotal * 0.03;
}
```

#### 2. Enhanced Payment Initialization with Delivery Parameters
**Location:** Lines 2539-2550 in `initializePayment()` function

**Added Parameters:**
- `quantity`: Total quantity of all items in cart
- `buyer_location`: Full buyer address (address_line_1 + address_line_2)
- `buyer_city`: Buyer's city from shipping address
- `seller_location`: Seller's location from product
- `seller_city`: Seller's city from product

```javascript
// Prepare payment data with enhanced delivery parameters
const paymentData = {
  product_total: productTotal,
  customer_state: shippingAddress.state,
  product_weight: cartItems.reduce((sum, item) => sum + (item.quantity * 1), 0),
  quantity: cartItems.reduce((sum, item) => sum + item.quantity, 0), // Total quantity
  subaccount_code: subaccountCode,
  product_id: cartItems.map(item => item.product.id).join(','),
  platform_type: platformType,
  buyer_location: `${shippingAddress.address_line_1}${shippingAddress.address_line_2 ? ', ' + shippingAddress.address_line_2 : ''}`,
  buyer_city: shippingAddress.city,
  seller_location: firstProduct.location || '',
  seller_city: firstProduct.city || '',
  callback_url: `${window.location.origin}/payment-callback`
};
```

#### 3. Updated Order Summary Display
**Location:** Lines 6410-6416

**Changed:** Service charge label from "Service Charge (10%)" to "Service Charge" (percentage now varies by platform)

```javascript
{orderSummary.platform_service_charge > 0 && (
  <div className="flex justify-between text-sm">
    <span className="text-gray-600">Service Charge</span>
    <span className="font-medium">₦{orderSummary.platform_service_charge?.toLocaleString() || 0}</span>
  </div>
)}
```

## Platform Commission Structure (Corrected)

### HOME Platform
- **Service Charge:** 3% of product total
- **Commission:** None
- **Delivery:** Calculated based on distance + base fee, capped at ₦40,000
- **Total Platform Revenue:** Service charge + Delivery fee

**Example:** Product = ₦10,000
- Service charge: ₦300 (3%)
- Delivery: ₦2,500 (varies)
- Vendor receives: ₦10,000
- Platform receives: ₦300 + ₦2,500 = ₦2,800

### FARMHUB Platform
- **Service Charge:** 10% of product total
- **Commission:** None
- **Delivery:** Base fee + (distance × quantity × multiplier)
- **Multiplier:** 15 for perishable, 10 for others
- **Total Platform Revenue:** Service charge + Delivery fee

**Example:** Product = ₦10,000, Quantity = 5
- Service charge: ₦1,000 (10%)
- Delivery: Base ₦1,500 + (50km × 5 × 10) = ₦4,000
- Vendor receives: ₦10,000
- Platform receives: ₦1,000 + ₦4,000 = ₦5,000

### COMMUNITY Platform
- **Commission:** 2.5% (extracted from vendor's sales)
- **Service Charge:** None
- **Delivery:** Base fee + (distance × quantity × multiplier)
- **Total Platform Revenue:** Commission + Delivery fee

**Example:** Product total = ₦10,000
- Commission: ₦250 (2.5% extracted from vendor)
- Delivery: ₦3,000 (varies)
- **Vendor receives: ₦9,750** (97.5% of product total)
- Platform receives: ₦250 + ₦3,000 = ₦3,250

## Testing Checklist

### Backend Testing
- [ ] Verify HOME platform charges 3% service fee (not 10%)
- [ ] Verify COMMUNITY commission is extracted from vendor sales (vendor gets 97.5%)
- [ ] Test delivery fee calculation with new parameters (buyer_city, buyer_location, etc.)
- [ ] Confirm distance-based calculations work correctly

### Frontend Testing
- [ ] Check HOME order summary shows 3% service charge
- [ ] Check COMMUNITY order summary shows only 2.5% commission (no service charge)
- [ ] Verify payment initialization sends all required parameters
- [ ] Test checkout flow with complete shipping address
- [ ] Confirm delivery parameters are properly extracted from forms

### End-to-End Testing
- [ ] Complete HOME purchase and verify charges
- [ ] Complete FARMHUB purchase and verify charges
- [ ] Complete COMMUNITY purchase and verify vendor receives 97.5%
- [ ] Test with different locations to verify geocoding
- [ ] Verify email notifications on order completion

## API Contract Changes

### `/api/paystack/transaction/initialize`

**New Required/Optional Parameters:**
```json
{
  "product_total": 10000,
  "customer_state": "Lagos",
  "quantity": 5,
  "platform_type": "home",
  "buyer_location": "123 Main St, Ikeja",
  "buyer_city": "Lagos",
  "seller_location": "456 Farm Rd, Oyo",
  "seller_city": "Oyo",
  "subaccount_code": "ACCT_xxxxx",
  "product_id": "prod_123",
  "callback_url": "https://example.com/callback"
}
```

**Response includes:**
```json
{
  "status": true,
  "authorization_url": "https://checkout.paystack.com/...",
  "breakdown": {
    "product_total": 10000,
    "delivery_fee": 2500,
    "platform_cut": 800,
    "total": 13300,
    "delivery_state": "Lagos",
    "delivery_method": "geocode_distance_based",
    "estimated_delivery_days": "24 hours"
  }
}
```

## Next Steps

1. **Database Migration:** Ensure product records have `location` and `city` fields
2. **Vendor Onboarding:** Update vendor forms to capture location/city during product listing
3. **Admin Dashboard:** Add commission breakdown reports by platform
4. **Analytics:** Track delivery fees by platform and location
5. **Documentation:** Update vendor documentation with commission structure

## Notes

- The frontend still needs product data to include `location` and `city` fields
- Consider adding a geocoding fallback if seller location is not provided
- May need to add validation to ensure required location fields are present
- Consider caching geocoding results to reduce API calls
