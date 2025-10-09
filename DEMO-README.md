# 🎯 Pyramyd Agent Demo - Staging Environment

A complete separate staging environment for demonstrating the agent onboarding workflow, isolated from the main production application.

## 📍 Demo Access

**Direct Access**: Open `/app/frontend/public/demo.html` in your browser  
**Or via URL**: `http://localhost:3000/demo.html` (if served by frontend)

## 🎮 Demo Features

### 🚀 Complete Agent Onboarding Workflow
- **Registration & KYC**: Instant approval simulation
- **Farmer Network**: Add and manage farmers  
- **Product Management**: Create and publish agricultural products
- **Order Processing**: Simulated order and transaction flow
- **Analytics Dashboard**: Revenue tracking and performance metrics

### 💾 Local Storage Persistence
- All demo data stored in browser's localStorage
- Data persists across sessions
- Easy reset functionality
- No backend dependencies

### 📊 Pre-populated Demo Data

#### 👨‍🌾 Demo Farmers
- **Adebayo Ogundimu** (Ogun State) - Rice, Yam, Cassava - 5 hectares
- **Fatima Aliyu** (Kaduna State) - Maize, Beans, Millet - 3 hectares

#### 📦 Demo Products  
- **Premium Local Rice** - ₦800/kg - 500kg available
- **Fresh White Yam** - ₦1,200/tuber - 200 tubers available
- **Organic White Beans** - ₦600/kg - 300kg available

#### 🛒 Demo Orders
- **Premium Local Rice**: ₦42,500 (50kg + shipping) - Delivered
- **Organic White Beans**: ₦63,000 (100kg + shipping) - Processing  
- **Fresh White Yam**: ₦24,200 (20 tubers + dropoff) - Delivered

#### 💰 Demo Analytics
- **Total Revenue**: ₦129,700
- **Agent Commission**: ₦6,485 (5% of sales)
- **Completed Orders**: 3 orders
- **Active Farmers**: 2 farmers in network

## 🏗️ Demo Workflow

### Step 1: Welcome Screen
- Overview of demo features
- Introduction to agent onboarding process
- "Start Agent Demo" button to begin

### Step 2: KYC Submission (Simulated)
1. **Business Information** - Pre-filled demo business details
2. **Document Upload** - Mock file upload simulation
3. **Review & Submit** - Final review of information
4. **Instant Approval** - Bypasses 24-hour timeline for demo

### Step 3: Agent Dashboard
- **Overview Tab**: Metrics cards and recent activity
- **Farmers Tab**: Network management and farmer registration
- **Products Tab**: Product creation and inventory management
- **Orders Tab**: Order tracking and transaction history

## 🎯 Interactive Features

### Farmer Management
- ✅ Add new farmers to network
- ✅ View farmer profiles with crops and location
- ✅ Manage farmer contact information
- ✅ Track farm sizes and specializations

### Product Creation
- ✅ Create new agricultural products
- ✅ Set pricing and availability
- ✅ Link products to specific farmers
- ✅ Configure delivery options

### Order & Transaction Tracking  
- ✅ View order history and status
- ✅ Track commission earnings
- ✅ Monitor revenue analytics
- ✅ Manage customer relationships

## 🔧 Technical Implementation

### Architecture
- **Standalone HTML Application**: Self-contained demo environment
- **React via CDN**: No build process required
- **Tailwind CSS**: For responsive styling
- **LocalStorage API**: For data persistence

### Storage Structure
```javascript
// Demo data stored in browser localStorage
{
  "pyramyd_demo_user": {...},      // Demo agent profile
  "pyramyd_demo_farmers": [...],   // Farmer network
  "pyramyd_demo_products": [...],  // Product catalog  
  "pyramyd_demo_orders": [...],    // Order history
  "pyramyd_demo_kyc": {...}       // KYC status
}
```

### Key Components
- **DemoStorage**: Manages localStorage operations
- **KYCSubmission**: 4-step KYC simulation
- **AgentDashboard**: Complete management interface
- **Modal Components**: Farmer and product creation forms

## 🎨 Demo Environment Features

### Visual Indicators
- **Demo Watermark**: Persistent header showing "STAGING ENVIRONMENT"
- **Demo Badges**: Orange badges throughout indicating demo mode
- **Mock Notifications**: Simulated approval and success messages

### Isolated Environment
- ❌ **No Backend Dependencies**: Completely client-side
- ❌ **No Production Data**: Safe for demonstrations  
- ❌ **No Real Transactions**: All payments simulated
- ❌ **No User Interference**: Separate from main application

## 🚀 Usage Instructions

### For Demonstrations
1. Open `demo.html` in browser
2. Click "Start Agent Demo"
3. Complete simulated KYC process
4. Explore agent dashboard features
5. Add farmers and create products
6. Review analytics and order history

### For Testing
- Test complete agent onboarding flow
- Validate farmer registration process  
- Verify product creation workflow
- Check order management features
- Confirm analytics calculations

### For Training
- Walk through agent responsibilities
- Practice farmer network building
- Learn product listing process
- Understand commission structure
- Experience dashboard navigation

## 🔄 Demo Reset

To reset demo data:
```javascript
// Clear all demo data
localStorage.removeItem('pyramyd_demo_user');
localStorage.removeItem('pyramyd_demo_farmers');
localStorage.removeItem('pyramyd_demo_products');
localStorage.removeItem('pyramyd_demo_orders');
localStorage.removeItem('pyramyd_demo_kyc');

// Or clear all localStorage
localStorage.clear();
```

## ⚠️ Important Notes

- **Staging Environment Only**: Not connected to production systems
- **Local Data Storage**: Data only persists in current browser
- **Demo Purpose**: For demonstrations, training, and testing only
- **No Real Transactions**: All monetary values are simulated
- **Isolated Experience**: Completely separate from main application

## 🎓 Perfect For

- **Sales Demonstrations**: Show complete agent workflow
- **Training Sessions**: Onboard new agents safely
- **Feature Testing**: Test agent features without production impact
- **Stakeholder Reviews**: Present agent capabilities to stakeholders
- **Development Testing**: Validate agent workflow logic

---

**🎯 Pyramyd Agent Demo - Comprehensive staging environment for agent onboarding workflow demonstration**