# Product Requirements Document (PRD) & Engineering Guide: Pyramyd

## 1. Executive Summary & Product Vision
**Pyramyd** is a comprehensive B2B/B2C agricultural trading platform that connects farmers, agents, businesses, and end-consumers in a secure, efficient marketplace. Our vision is to eliminate friction in the agricultural supply chain by offering role-based access, automated logistics, true escrow payments, and community-driven commerce.

---

## 2. Problem Statement & Pain Points
The current agricultural supply chain in Nigeria is fragmented and opaque, leading to the following key pain points:
- **Lack of Trust & Fraud Risk**: Buyers and sellers hesitate to trade remotely due to payment fraud or failure to deliver goods.
- **Logistics Bottlenecks**: Finding reliable, transparently-priced freight for bulk farm produce is extremely difficult.
- **Middleman Exploitation**: Farmers lack direct access to broader markets and are forced to accept lowgate prices.
- **Market Invisibility**: Procurement managers and businesses struggle to source raw materials predictably and at scale.

---

## 3. Target Audience & Personas

- **Farmers**: Primary producers. Can list bulk produce on "Farm Deals", manage farmland, track revenue, and bid on active procurement requests.
- **Agents**: Facilitators who manage farmer networks, aggregate produce, and earn commissions by matching supply to demand.
- **Businesses**: Buyers and sellers of processed agricultural goods on "PyExpress". They can also operate as logistics providers.
- **Personal Users**: End-consumers who browse and purchase agricultural goods but cannot sell.

---

## 4. Key User Journeys

### Journey 1: Bulk Procurement (Buyer)
1. Buyer navigates to the Deal Board and posts an RFQ (Request for Quote) specifying quantity, budget, and delivery state.
2. Buyer receives bids from verified Farmers and Agents.
3. Buyer reviews profiles, accepts a bid, and funds the Paystack Escrow account.
4. Goods are delivered. Buyer confirms receipt on the platform, releasing the escrowed funds to the seller.

### Journey 2: Instant Retail Trade (Seller)
1. A registered Business lists processed goods (e.g., packaged rice) on PyExpress.
2. A Consumer adds the item to their cart and checks out via the Smart Delivery Calculator.
3. Payment is escrowed, and the Business is notified to dispatch the item.
4. Upon delivery confirmation, funds are credited to the Business's wallet/subaccount.

---

## 5. Core Features & Scope

### 5.1 Dual-Marketplace Architecture
- **PyExpress (Instant Commerce)**: Fast-moving marketplace for processed or retail-ready goods. Features its own dedicated shopping cart and instant delivery workflows.
- **Farm Deals (Bulk Commerce)**: Wholesale platform for bulk agricultural produce requiring standard or freight delivery. Features an independent shopping cart to prevent mixed logistics.

### 5.2 The Deal Board (RFQ System)
- **Live Requests**: Buyers post their procurement needs (e.g., "Need 500kg of Maize").
- **Bidding Workflow**: Sellers (Agents/Farmers/Businesses) submit competitive quotes to buyers.
- **Offer Management**: Buyers can review incoming offers, view seller ratings, and accept the best bid.

### 5.3 Automated Logistics & Escrow Payments
- **Smart Delivery Calculator**: Dynamically calculates intra-city and inter-state logistics fees based on buyer and seller state mappings.
- **True Escrow Handling**: Powered by Paystack. Funds are held securely in escrow and only released to the vendor subaccount upon confirmed delivery.
- **Automated Refunds**: Full debit reversals automatically trigger if an administrator cancels a pending RFQ or a buyer cancels an escrowed delivery.
- **Async Dispatch**: Backend `logistics_dispatcher.py` handles dummy deliveries asynchronously to avoid overloading core thread traffic.

### 5.4 Community & Social Commerce
- **Community Hubs**: Users can join geographical or topical agricultural groups.
- **Localized Listings**: Products can be scoped exclusively to community members.
- **Messaging**: Built-in real-time text and audio messaging between users.

### 5.5 Security & Compliance (KYC)
- **Registered Businesses**: Requires Business Registration Number, Tax Identification Number (TIN), Certificate of Incorporation, and Utility Bill.
- **Unregistered Entities (Farmers/Agents)**: Requires NIN/BVN validation, live headshot capture, and National ID document uploads.

---

## 6. System Architecture & Tech Stack

### 6.1 Technology Stack
- **Frontend**: React 19, Tailwind CSS, CRACO.
- **Backend**: Python 3.8+, FastAPI.
- **Database**: MongoDB (NoSQL).
- **Payment & Escrow**: Paystack API (Subaccounts, Escrow, Refunds).
- **Communication**: ZeptoMail (Email notifications).

### 6.2 Progressive Web App (PWA)
- **Offline Functionality**: Users can browse cached products without an internet connection.
- **Background Sync**: Auto-syncs vendor posts when the network connection is restored.
- **Service Worker**: Smart caching for optimal rural performance.

### 6.3 Database Optimization
- **N+1 Query Elimination**: All iterative `find_one` loops across feeds have been eliminated. Pyramyd computes relationships using hashed `$in` bulk queries.
- **Mandatory Indexing**: A dedicated `create_indexes.py` script enforces strict document indexing to prevent iteration bottlenecks on live MongoDB hosts.

---

## 7. Developer Setup & Deployment Guide

### 7.1 Prerequisites
- **Python 3.8+** (for backend)
- **Node.js 16+** (for frontend)
- **Yarn** package manager
- **MongoDB** (local instance or connection)

### 7.2 Environment Setup
Create `/app/backend/.env`:
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=pyramyd_db
JWT_SECRET_KEY=your-secret-key-here
PAYSTACK_SECRET_KEY=sk_test_your_paystack_secret_key
PAYSTACK_PUBLIC_KEY=pk_test_your_paystack_public_key
ZEPTOMAIL_TOKEN=your_zeptomail_token
```

Create `/app/frontend/.env`:
```env
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=3000
```

### 7.3 Local Startup
**Backend**:
```bash
cd /app/backend
pip install -r requirements.txt
sudo service mongod start
python server.py
# Available at: http://localhost:8001
```

**Frontend**:
```bash
cd /app/frontend
yarn install
yarn start
# Available at: http://localhost:3000
```

### 7.4 Docker/Production Deployment
To run using Docker Compose:
```bash
docker-compose up --build -d
```

---

## 8. API Architecture Reference

### Core Domains
- `POST /api/auth/*` - Registration, Login, Profile Management
- `GET /api/products/*` - Feed fetching, filtered searches, categorical mappings
- `POST /api/paystack/*` - Subaccount creation, transaction init, escrow verification
- `POST /api/checkout/*` - Smart delivery calculation, distance matrices
- `GET /api/requests/*` - RFQ Deal Board management
- `POST /api/kyc/*` - Compliance document ingestion

**Note**: See Swagger UI (`http://localhost:8001/docs`) for full payload schemas during local execution.
