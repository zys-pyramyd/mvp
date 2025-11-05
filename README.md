# Pyramyd - Agricultural Trading Platform

Pyramyd is a comprehensive agricultural trading platform that connects farmers, agents, businesses, and buyers in a secure, efficient marketplace. The platform features role-based access, KYC verification, digital wallets, rating systems, and advanced trading capabilities.

## 🌟 Key Features

### Core Marketplace
- **Multi-Platform Trading**: 
  - **PyExpress (Home)**: Business marketplace for processed goods
  - **Farm Deals**: Bulk trading platform for farmers and agents
  - **Communities**: Group buying and social features for agricultural communities
- **Role-Based Access Control**: Farmer, Agent, Business, Personal, and Logistics accounts
- **Advanced Product Filtering**: Category, location, price range, seller type
- **Nigerian States Support**: All 36 states + FCT Abuja

### Payment & Commission System
- **Paystack Integration**: Secure payment gateway with split payments
- **Agent Gamification System**: 5-tier commission structure
  - Starter (< 100 farmers): 4% base commission
  - Pro (100-999 farmers): 4.5% total (4% + 0.5% bonus)
  - Expert (1000-4999 farmers): 5% total (4% + 1% bonus)
  - Master (5000-9999 farmers): 6% total (4% + 2% bonus)
  - Elite (10000+ farmers): 8% total (4% + 4% bonus)
- **Smart Delivery System**: 
  - Vendor-managed logistics (FREE or custom fee)
  - Kwik Delivery integration (Lagos, Oyo, FCT Abuja)
  - 20% delivery fee for other states
- **Platform-Specific Checkout**: Separate flows for PyExpress and Farm Deals

### User Experience
- **Cart Tab System**: Separate PyExpress and Farm Deals carts with color coding
- **Communities Search**: Real-time filtering across name, description, category, location
- **Profile Pictures**: User and product seller profile images
- **Discount System**: Fixed or percentage discounts with visual badges
- **Seller Transparency**: Clickable seller profiles with detailed information

### Progressive Web App (PWA)
- **Offline Functionality**: Browse products and communities without internet
- **Service Worker**: Smart caching for optimal performance
- **Background Sync**: Auto-sync vendor posts when connection returns
- **Install to Home Screen**: Native app-like experience
- **Offline Indicator**: Clear status when browsing cached content

### Security & Compliance
- **KYC Verification System**: Comprehensive compliance for all seller types
- **Enhanced Agent Validation**: Strict KYC requirements with 24-hour verification
- **Secure Account Storage**: Encrypted payment details
- **JWT Authentication**: Token-based security with bcrypt hashing

### Other Features
- **Digital Wallet**: Mock wallet system with transaction history and gift cards
- **Rating & Review System**: 5-star ratings for users, products, and drivers
- **Driver Management**: Uber-like driver platform for logistics businesses
- **Real-Time Market Prices**: Agricultural commodity price tracking
- **Pre-order System**: Future delivery with partial payments
- **Enhanced Messaging**: Text and audio messages between users
- **Responsive Design**: Mobile-first approach with desktop optimization

## 🏗️ Architecture

### Backend
- **Framework**: FastAPI (Python)
- **Database**: MongoDB
- **Authentication**: JWT with bcrypt password hashing
- **API Design**: RESTful endpoints with comprehensive validation

### Frontend
- **Framework**: React 19 with hooks
- **Styling**: Tailwind CSS + Custom CSS
- **Build Tool**: CRACO (Create React App Configuration Override)
- **State Management**: React hooks (useState, useEffect)

## 📋 Prerequisites

Before running the application, ensure you have the following installed:

- **Python 3.8+** (for backend)
- **Node.js 16+** (for frontend)
- **Yarn** package manager
- **MongoDB** (local instance or connection)
- **Git** (for version control)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd pyramyd
```

### 2. Environment Setup

#### Backend Environment
Create `/app/backend/.env` file:
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=pyramyd_db
JWT_SECRET_KEY=your-secret-key-here
```

#### Frontend Environment
Create `/app/frontend/.env` file:
```env
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=3000
```

### 3. Backend Setup

```bash
# Navigate to backend directory
cd /app/backend

# Install Python dependencies
pip install -r requirements.txt

# Start MongoDB (if not running)
sudo service mongod start

# Run the FastAPI server
python server.py
```

The backend will be available at: `http://localhost:8001`

### 4. Frontend Setup

```bash
# Navigate to frontend directory
cd /app/frontend

# Install dependencies using Yarn
yarn install

# Start the React development server
yarn start
```

The frontend will be available at: `http://localhost:3000`

## 🐳 Docker/Production Setup

If you're running in a containerized environment (like this one), the application is managed by supervisor:

### Check Service Status
```bash
sudo supervisorctl status
```

### Restart Services
```bash
# Restart individual services
sudo supervisorctl restart backend
sudo supervisorctl restart frontend

# Restart all services
sudo supervisorctl restart all
```

### View Logs
```bash
# Frontend logs
tail -f /var/log/supervisor/frontend.out.log
tail -f /var/log/supervisor/frontend.err.log

# Backend logs
tail -f /var/log/supervisor/backend.out.log
tail -f /var/log/supervisor/backend.err.log
```

## 🧪 Local Testing Guide

### Prerequisites Check
Before testing locally, ensure you have:
```bash
# Check Python version (3.8+)
python --version

# Check Node.js version (16+)
node --version

# Check Yarn
yarn --version

# Check MongoDB status
sudo service mongod status
```

### Step 1: Clone and Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd pyramyd

# Create backend .env file
cat > backend/.env << EOL
MONGO_URL=mongodb://localhost:27017
DB_NAME=pyramyd_local_test
JWT_SECRET_KEY=$(openssl rand -hex 32)
PAYSTACK_SECRET_KEY=sk_test_your_paystack_secret_key
PAYSTACK_PUBLIC_KEY=pk_test_your_paystack_public_key
FARMHUB_SUBACCOUNT=ACCT_your_farmhub_subaccount
FARMHUB_SPLIT_GROUP=SPL_your_split_group_code
KWIK_API_KEY=your_kwik_api_key
KWIK_API_URL=https://api.kwik.delivery/v1
EOL

# Create frontend .env file
cat > frontend/.env << EOL
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=3000
EOL
```

### Step 2: Install Dependencies

```bash
# Backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# Frontend dependencies
cd frontend
yarn install
cd ..
```

### Step 3: Start MongoDB

```bash
# Start MongoDB service
sudo service mongod start

# Verify MongoDB is running
sudo service mongod status

# Optional: Connect to MongoDB shell to verify
mongosh
# In mongo shell:
# show dbs
# use pyramyd_local_test
# exit
```

### Step 4: Start Backend Server

```bash
# Open a new terminal window/tab
cd backend
python server.py

# You should see:
# "INFO:     Uvicorn running on http://0.0.0.0:8001"
# "INFO:     Application startup complete"

# Test backend is running:
curl http://localhost:8001/api/health
# Expected: {"status": "healthy"}
```

### Step 5: Start Frontend Server

```bash
# Open another terminal window/tab
cd frontend
yarn start

# The app will automatically open at http://localhost:3000
# You should see the Pyramyd homepage with:
# - Header with navigation
# - Slide shows
# - Product categories
# - Featured products
```

### Step 6: Test Core Functionality

#### A. User Registration & Authentication
1. Click "Sign In" in the header
2. Click "Don't have an account? Sign up"
3. Fill registration form:
   - First Name: Test
   - Last Name: User
   - Email: testuser@pyramyd.com
   - Password: password123
   - Select role (Personal, Farmer, Agent, or Business)
4. Complete registration
5. Login with credentials

#### B. Browse Products
1. Scroll through homepage
2. Click on category to filter products
3. Use location filter dropdown (top right)
4. Click on a product to view details
5. Verify product information displays correctly

#### C. Cart & Checkout System
1. Add products to cart (click "Add to Cart" button)
2. Click cart icon in header
3. **Verify Cart Tabs:**
   - See "PyExpress" tab (emerald/green)
   - See "Farm Deals" tab (orange)
   - Each tab shows correct item count
   - Switch between tabs
4. **Test Checkout:**
   - Click "Checkout PyExpress" or "Checkout Farm Deals"
   - Verify platform-specific colors:
     - PyExpress: Emerald green theme
     - Farm Deals: Orange theme
   - Fill shipping address (include a Nigerian state)
   - Proceed to payment step
   - See Paystack payment options

#### D. Communities Search
1. Click "Find Communities" in header
2. See communities browser modal
3. **Test Search:**
   - Type in search bar (e.g., "farm", "rice")
   - Verify results filter in real-time
   - See result count update
   - Click "X" button to clear search
4. Click on a community to view details
5. Join a community

#### E. Agent Features (Agent users only)
1. Login as agent user
2. Click profile icon → "Agent Dashboard"
3. **Verify Agent Tier System:**
   - See tier badge (Starter, Pro, Expert, Master, or Elite)
   - See farmer count
   - See bonus commission rate
   - See progression to next tier
4. Test agent-specific features

#### F. PWA Features
1. Open Chrome DevTools (F12)
2. Go to "Application" tab
3. **Verify Service Worker:**
   - Click "Service Workers" in left sidebar
   - See service-worker.js registered and activated
4. **Test Offline Mode:**
   - Open Network tab in DevTools
   - Select "Offline" from throttling dropdown
   - Refresh page
   - See offline indicator banner (gray with WiFi-off icon)
   - Verify you can still browse cached products
   - Go back online
   - Offline indicator should disappear
5. **Test Install Prompt:**
   - Look for emerald install banner at top
   - Click "Install Now" to install as PWA
   - Or use Chrome menu → "Install Pyramyd..."

### Step 7: Test API Endpoints (Optional)

```bash
# Test agent tier endpoint (requires agent user token)
curl -X GET http://localhost:8001/api/agent/tier \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Test delivery fee calculator
curl -X POST http://localhost:8001/api/delivery/calculate-fee \
  -H "Content-Type: application/json" \
  -d '{
    "product_total": 5000,
    "buyer_state": "Lagos"
  }'

# Test communities search
curl http://localhost:8001/api/communities

# Test product categories
curl http://localhost:8001/api/categories/products
```

### Step 8: Verify Key Features

✅ **Cart System:**
- [ ] Cart icon shows item count
- [ ] Two tabs: PyExpress (green) and Farm Deals (orange)
- [ ] Tab switching works
- [ ] Items correctly filtered by platform
- [ ] Totals calculated independently per tab

✅ **Checkout Flow:**
- [ ] Platform-specific colors throughout
- [ ] Progress indicators color-coded
- [ ] Vendor logistics badges display (FREE/custom fee)
- [ ] Paystack payment initialization works
- [ ] State-based delivery calculation applies

✅ **Communities:**
- [ ] "Find Communities" opens modal
- [ ] Search bar filters results
- [ ] Result count updates
- [ ] Clear button works
- [ ] Community cards display correctly

✅ **PWA:**
- [ ] Service worker registers successfully
- [ ] Offline indicator appears when offline
- [ ] Install prompt shows (on supported browsers)
- [ ] Can browse cached content offline

✅ **Agent Gamification:**
- [ ] Agent tier displays in dashboard
- [ ] Commission rates show (base + bonus)
- [ ] Farmer count visible
- [ ] Next tier progression info shown

### Troubleshooting Local Testing

#### Issue: Backend won't start
```bash
# Check if port 8001 is already in use
lsof -i :8001
# Kill the process if needed
kill -9 <PID>

# Check MongoDB is running
sudo service mongod status
sudo service mongod restart

# Check Python dependencies
pip list | grep fastapi
pip list | grep pymongo
```

#### Issue: Frontend won't compile
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
yarn install

# Clear cache
yarn cache clean

# Check for syntax errors in App.js
cat frontend/src/App.js | head -50
```

#### Issue: Can't see products
- Ensure backend is running (http://localhost:8001)
- Check backend logs for errors
- Verify REACT_APP_BACKEND_URL in frontend/.env
- Try creating a test product via API or UI

#### Issue: Service Worker not registering
- Must use HTTPS or localhost
- Check browser console for errors
- Clear browser cache and hard reload (Ctrl+Shift+R)
- Ensure service-worker.js is in /public folder

#### Issue: Paystack payments failing
- This is expected with dummy API keys
- For testing, use Paystack test keys from your account
- Calculation logic should still work even with dummy keys

### Performance Testing

```bash
# Check backend response times
time curl http://localhost:8001/api/products

# Check frontend build size
cd frontend
yarn build
ls -lh build/static/js/

# Check MongoDB query performance
mongosh
use pyramyd_local_test
db.products.find().explain("executionStats")
```

## 📁 Project Structure

```
/app/
├── backend/
│   ├── server.py              # FastAPI application
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Backend environment variables
├── frontend/
│   ├── src/
│   │   ├── App.js            # Main React component
│   │   ├── App.css           # Custom styles
│   │   └── index.js          # React entry point
│   ├── public/               # Static assets
│   ├── package.json          # Node.js dependencies
│   ├── tailwind.config.js    # Tailwind CSS configuration
│   └── .env                  # Frontend environment variables
├── tests/                    # Test files
└── README.md                # This file
```

## 🔑 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user profile

### Products & Trading
- `GET /api/products` - List products with filtering
- `POST /api/products` - Create new product (authenticated)
- `GET /api/categories/products` - Get product categories
- `GET /api/categories/business` - Get business categories

### KYC System
- `GET /api/users/kyc/status` - Get KYC status
- `POST /api/kyc/documents/upload` - Upload KYC documents
- `POST /api/kyc/registered-business/submit` - Submit business KYC
- `POST /api/kyc/unregistered-entity/submit` - Submit individual KYC

### Digital Wallet
- `GET /api/wallet/summary` - Wallet balance and statistics
- `POST /api/wallet/fund` - Fund wallet (mock)
- `POST /api/wallet/gift-cards` - Create gift cards
- `POST /api/wallet/gift-cards/redeem` - Redeem gift cards

### Dashboards
- `GET /api/farmer/dashboard` - Farmer business metrics
- `GET /api/agent/dashboard` - Agent performance data
- `POST /api/farmer/farmland` - Add farmland records
- `POST /api/agent/farmers/add` - Add farmer to agent network

## 👥 User Roles & Permissions

### Personal Account
- ✅ Can browse and purchase products
- ❌ Cannot sell products
- ❌ KYC not required

### Farmer Account
- ✅ Can buy and sell products
- ✅ Can post on "Buy from Farm" page
- ✅ Access to Farmer Dashboard
- ⚠️ KYC required for payments

### Agent Account
- ✅ Can buy and sell products
- ✅ Can post on "Buy from Farm" page
- ✅ Can manage farmer networks
- ✅ Access to Agent Dashboard
- ⚠️ KYC required for payments

### Business Account
- ✅ Can buy and sell products
- ✅ Can post on Home page (business marketplace)
- ✅ Driver management (if logistics business)
- ⚠️ KYC required for payments

## 🔐 KYC Requirements

### Registered Businesses
- Business Registration Number
- Tax Identification Number (TIN)
- Certificate of Incorporation (upload)
- TIN Certificate (upload)
- Utility Bill (upload)
- Business address and contact information

### Unregistered Entities (Farmers/Agents/Unregistered Businesses)
- NIN or BVN (11-digit validation)
- Headshot photo (camera capture)
- National ID document (upload)
- Utility Bill (upload)

## 🛠️ Development

### Adding New Features
1. Backend: Add API endpoints in `server.py`
2. Frontend: Update `App.js` with new components
3. Update this README with new features
4. Test both frontend and backend functionality

### Code Style
- Backend: Follow PEP 8 Python style guidelines
- Frontend: Use functional components with hooks
- Use Tailwind CSS for styling
- Maintain responsive design principles

## 🐛 Troubleshooting

### App Not Loading
1. **Check Services Status**:
   ```bash
   sudo supervisorctl status
   ```

2. **Check Logs**:
   ```bash
   tail -f /var/log/supervisor/frontend.err.log
   tail -f /var/log/supervisor/backend.err.log
   ```

3. **Restart Services**:
   ```bash
   sudo supervisorctl restart all
   ```

### Common Issues

#### Frontend Issues
- **Compilation Errors**: Check for syntax errors in React components
- **API Connection**: Verify `REACT_APP_BACKEND_URL` in frontend `.env`
- **Dependencies**: Run `yarn install` to ensure all packages are installed

#### Backend Issues
- **MongoDB Connection**: Ensure MongoDB is running and `MONGO_URL` is correct
- **Python Dependencies**: Install missing packages with `pip install -r requirements.txt`
- **Port Conflicts**: Ensure port 8001 is available

#### Environment Issues
- **Missing .env Files**: Create both frontend and backend `.env` files
- **Incorrect URLs**: Verify backend URL matches between services
- **Permission Errors**: Check file permissions and supervisor configuration

### Database Reset
If you need to reset the database:
```bash
# Connect to MongoDB
mongosh

# Drop the database
use pyramyd_db
db.dropDatabase()
```

## 📊 Features Overview

### Trading Platforms
- **Home Page**: Business-to-business marketplace for processed goods and services
- **Buy from Farm**: Bulk trading platform for farmers and agents to sell agricultural produce

### Digital Commerce
- **Multi-Unit Support**: kg, pieces, bags, tins, crates, liters
- **Location Filtering**: Find products by geographic location
- **Category Navigation**: Swipe-friendly category browsing
- **Market Prices**: Real-time agricultural commodity pricing

### User Management
- **Role-Based Access**: Different permissions for different account types
- **KYC Verification**: Compliance system for payment eligibility
- **Rating System**: 5-star ratings for users, products, and services
- **Digital Wallets**: Mock payment system with transaction history

### Business Intelligence
- **Farmer Dashboard**: Revenue tracking, farmland management, order history
- **Agent Dashboard**: Network management, commission tracking, performance metrics
- **Market Analytics**: Price trends and market insights

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Create a Pull Request

## 📄 License

This project is proprietary software developed for agricultural marketplace purposes.

## 📞 Support

For technical support or questions:
- Check the troubleshooting section above
- Review the logs for error messages
- Ensure all prerequisites are installed correctly

---

**Happy Trading! 🌾📈**
