# Delivery Fee Calculation & Platform Updates Summary

## Changes Implemented

### 1. Enhanced `calculate_delivery_fee()` Function

**Location:** `backend/server.py` (lines 370-534)

**New Parameters:**
- `platform_type`: Specifies the platform ("home", "farmhub", or "community")
- `quantity`: Product quantity (used for farmhub/community calculations)
- `buyer_location`: Buyer's full address/location string
- `seller_location`: Seller's full address/location string
- `buyer_city`: Buyer's city (enhances geocoding accuracy)
- `seller_city`: Seller's city (enhances geocoding accuracy)

**New Logic:**

#### Priority 1: Vendor-Managed Logistics
- If seller manages logistics, use their delivery fee
- Returns estimated delivery days based on platform

#### Priority 2: HOME Platform + Kwik-Enabled States
- For HOME platform in Lagos, Oyo, or FCT Abuja:
  - Tries Kwik API for real-time quotes (if addresses provided)
  - Falls back to state-based Kwik fees if API fails
  - Delivers within **24 hours**

#### Priority 3: Platform-Specific Geocode Calculation

**For HOME Platform:**
- Formula: `base_fee + (distance_km * 1000)`
- **Maximum cap:** ₦40,000
- Delivery time: **24 hours within same location**
- Base fees from `BASE_DELIVERY_FEES` dictionary (₦1,500-₦4,500 depending on state)

**For FARMHUB/COMMUNITY Platforms:**
- Formula: `base_fee + (distance_km * quantity * multiplier)`
- Multiplier: 
  - **15** for perishable products (fish_meat, spices_vegetables categories)
  - **10** for non-perishable products
- Delivery time: **3-14 days**
- No maximum cap (actual cost-based)

**Geocoding Enhancement:**
- Uses `geo_helper` from `geopy.py` to calculate distances
- Builds complete addresses including city and state for better accuracy
- Appends "Nigeria" to addresses for better geocoding results
- Falls back to base state fees if geocoding fails

### 2. Updated Delivery Fee Calculation Endpoints

**Endpoint:** `/api/delivery/calculate-fee`
**Location:** `backend/server.py` (lines 6404-6467)

**New Parameters:**
- `platform_type` (default: "home")
- `quantity` (default: 1)
- `buyer_location`
- `seller_location`
- `buyer_city`
- `seller_city`

**Enhanced Response:**
- `estimated_delivery_days`: "24 hours" or "3-14 days"
- `distance_km`: Calculated distance if available
- `platform_type`: Echoes the platform type
- Full delivery calculation breakdown

### 3. Updated Payment Initialization

**Endpoint:** `/api/paystack/transaction/initialize`
**Location:** `backend/server.py` (lines 7519-7602)

**New Parameters Accepted:**
- `quantity`: Product quantity for delivery calculation
- `buyer_location`: Buyer's address
- `buyer_city`: Buyer's city
- `seller_location`: Seller's location (fallback to product location)
- `seller_city`: Seller's city

**Integration:**
- Passes all parameters to `calculate_delivery_fee()`
- Retrieves product category for perishable check
- Stores `estimated_delivery_days` in transaction metadata

### 4. Group Buying Feature for FARMHUB

**Added to Product Model:**
- `group_buy_enabled`: Boolean to enable group buying
- `group_buy_min_quantity`: Minimum quantity required
- `group_buy_discount_percentage`: Discount for reaching min quantity
- `group_buy_current_participants`: Track participants
- `group_buy_deadline`: Deadline for group buy

**Added to ProductCreate Model:**
- Same fields as Product model (except current_participants)

**Platform Support:**
- FARMHUB products can now enable group buying
- Community products already had this feature
- Allows bulk purchasing with discounts

### 5. Delivery Time Estimation

**HOME Platform:**
- **24 hours** delivery for products within Lagos, Oyo, or FCT Abuja
- Requires buyers to purchase from within their location for this guarantee

**FARMHUB/COMMUNITY Platforms:**
- **3-14 days** delivery time
- Delivery depends on pickup location or buyer-specified address
- Time range accounts for coordination and logistics

## Platform-Specific Rules

### HOME Platform
- Delivery limited to: **Lagos, Oyo, FCT Abuja**
- Priority: Kwik Delivery (if available) > Geocode calculation
- 24-hour delivery guarantee within same location
- Max delivery fee: ₦40,000
- Seller types: Business, Supplier

### FARMHUB Platform
- Delivery: Nationwide (pickup or buyer-specified address)
- Uses geocode-based calculation
- Delivery time: 3-14 days
- Fee includes quantity and perishability multiplier
- Group buying enabled
- Seller types: Farmer, Agent

### COMMUNITY Platform
- Same as FARMHUB for delivery
- Community-specific products
- Group buying enabled
- Social features (likes, comments, shares)

## Base Delivery Fees by State

Fees stored in `BASE_DELIVERY_FEES` dictionary:

### Tier 1 (₦1,500)
- Lagos, FCT Abuja

### Tier 2 (₦2,000-₦2,500)
- Ogun, Oyo, Osun, Rivers, Delta, Edo, Anambra, Enugu, Imo, Abia

### Tier 3 (₦3,000-₦3,500)
- Ondo, Ekiti, Bayelsa, Cross River, Akwa Ibom, Ebonyi, Nasarawa, Niger, Kogi, Benue, Plateau, Kwara, Kaduna, Kano, Adamawa, Gombe, Bauchi, Taraba

### Tier 4 (₦4,000-₦4,500)
- Katsina, Sokoto, Zamfara, Kebbi, Jigawa, Borno, Yobe

## Geocoding Implementation

**Helper Class:** `GeopyHelper` (`backend/geopy.py`)
**Features:**
- Caches geocoding results in MongoDB
- Uses Nominatim geocoder
- Calculates geodesic distance in kilometers
- Handles errors gracefully with fallback logic

**Usage in Calculation:**
```python
buyer_coords = geo_helper.geocode_address(buyer_addr)
seller_coords = geo_helper.geocode_address(seller_addr)
distance_km = geo_helper.distance_km(buyer_coords, seller_coords)
```

## Kwik Delivery Integration

**Enabled States:** Lagos, Oyo, FCT Abuja
**Priority:** Only used for HOME platform
**Fallback:** If Kwik API fails or addresses not provided, falls back to geocode calculation

## Perishable Products

**Categories:**
- `fish_meat`
- `spices_vegetables`

**Impact:**
- Higher delivery multiplier (15 vs 10) for FARMHUB/COMMUNITY
- Ensures faster handling and appropriate pricing

## Implementation Notes

1. **Geocoding with City:**
   - City is included in address string if provided
   - Format: `"{location}, {city}, {state}, Nigeria"`
   - Improves geocoding accuracy

2. **Fallback Mechanism:**
   - If geocoding fails → uses base state fee
   - If Kwik API fails → uses geocode calculation
   - Ensures delivery fee is always calculated

3. **Maximum Cap:**
   - Only HOME platform has ₦40,000 cap
   - FARMHUB/COMMUNITY have no cap (cost-based)

## TODO: Implementation Needed

1. **HOME Platform Restrictions:**
   - Add validation to ensure buyers only purchase from sellers in their same location
   - Enforce Lagos, Oyo, FCT Abuja limitation
   - Show warning/error if trying to buy from other locations

2. **Frontend Integration:**
   - Update order forms to collect buyer_city and buyer_location
   - Show estimated delivery time during checkout
   - Display delivery fee breakdown

3. **Testing:**
   - Test geocoding accuracy with real Nigerian addresses
   - Verify perishable product detection
   - Test Kwik API integration in production
   - Validate delivery fee caps and minimums

## API Usage Examples

### Calculate Delivery Fee
```json
POST /api/delivery/calculate-fee
{
  "product_total": 25000,
  "buyer_state": "Lagos",
  "platform_type": "home",
  "quantity": 2,
  "buyer_location": "Ikeja",
  "buyer_city": "Ikeja",
  "seller_location": "Lekki",
  "seller_city": "Lekki",
  "product_id": "product_123"
}
```

### Initialize Payment with Delivery
```json
POST /api/paystack/transaction/initialize
{
  "product_total": 25000,
  "customer_state": "Lagos",
  "platform_type": "farmhub",
  "quantity": 10,
  "buyer_location": "123 Main St, Ikeja",
  "buyer_city": "Ikeja",
  "seller_location": "Farm Location, Badagry",
  "seller_city": "Badagry",
  "product_id": "product_123",
  "subaccount_code": "ACCT_xxx"
}
```

## Files Modified

1. `backend/server.py`:
   - Updated `calculate_delivery_fee()` function (lines 370-534)
   - Updated `/api/delivery/calculate-fee` endpoint (lines 6404-6467)
   - Updated `/api/paystack/transaction/initialize` (lines 7519-7602)
   - Added group_buy fields to Product model (lines 1282-1287)
   - Added group_buy fields to ProductCreate model (lines 1322-1326)

2. `backend/geopy.py`:
   - No changes needed (already supports city-based geocoding)

## Benefits

1. **Accurate Pricing:** Distance-based calculation ensures fair pricing
2. **Transparency:** Buyers see delivery breakdown before purchase
3. **Flexibility:** Supports multiple platforms with different logic
4. **Perishable Handling:** Higher rates ensure proper handling of delicate goods
5. **Scalability:** Geocoding with caching scales well
6. **Fallback Safety:** Multiple fallback layers prevent calculation failures
7. **Group Buying:** FARMHUB products support bulk purchasing with discounts
