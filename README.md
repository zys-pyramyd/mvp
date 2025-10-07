# Pyramyd - Agricultural Trading Platform

Pyramyd is a comprehensive agricultural trading platform that connects farmers, agents, businesses, and buyers in a secure, efficient marketplace. The platform features role-based access, KYC verification, digital wallets, rating systems, and advanced trading capabilities.

## 🌟 Key Features

- **Multi-Platform Trading**: Home (Business marketplace) and Buy from Farm (Bulk trading)
- **Role-Based Access Control**: Farmer, Agent, Business, and Personal account types
- **KYC Verification System**: Comprehensive compliance for registered/unregistered businesses
- **Digital Wallet**: Mock wallet system with transaction history and gift cards
- **Rating & Review System**: 5-star ratings for users, products, and drivers
- **Driver Management**: Uber-like driver platform for logistics businesses
- **Real-Time Market Prices**: Agricultural commodity price tracking
- **Advanced Filtering**: Location-based and category filtering
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
