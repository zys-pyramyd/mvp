# Pyramyd Platform - Admin Dashboard Guide

## 🔐 Admin Access

### Default Admin Credentials
- **Email:** `abdulazeezshakrullah@gmail.com`
- **Password:** `Admin@2024`

⚠️ **IMPORTANT:** Change the default password immediately after first login in production!

---

## 📊 Admin Dashboard Features

### 1. Dashboard Overview

The admin dashboard provides comprehensive platform statistics:

**User Statistics:**
- Total users count
- Active users
- Users by role (Farmer, Agent, Business, Personal, Logistics)

**Product Statistics:**
- Total products
- Products by platform (PyExpress, Farm Deals)

**Order Statistics:**
- Total orders
- Pending orders
- Completed orders

**Community Statistics:**
- Total communities
- Public vs Private communities

**KYC Statistics:**
- Pending approvals
- Approved users
- Rejected users
- Not started

**Payment Statistics:**
- Total transactions
- Successful transactions
- Total revenue (in Naira)

**Agent Tier Distribution:**
- Starter agents
- Pro agents
- Expert agents
- Master agents
- Elite agents

**Recent Activities:**
- Last 10 platform activities
- Audit logs

---

## 🔑 Admin API Endpoints

### Authentication

#### Admin Login
```bash
POST /api/admin/login
Content-Type: application/json

{
  "email": "abdulazeezshakrullah@gmail.com",
  "password": "Admin@2024"
}

Response:
{
  "token": "eyJ...",
  "user": {
    "id": "admin_001",
    "email": "abdulazeezshakrullah@gmail.com",
    "role": "admin",
    "username": "Admin",
    "first_name": "Abdulazeez",
    "last_name": "Shakrullah"
  },
  "message": "Admin login successful"
}
```

### Dashboard Statistics

#### Get Dashboard Data
```bash
GET /api/admin/dashboard
Authorization: Bearer <admin_token>

Response:
{
  "users": {
    "total": 150,
    "active": 120,
    "by_role": {
      "farmer": 50,
      "agent": 30,
      "business": 20,
      "personal": 40,
      "logistics": 10
    }
  },
  "products": {
    "total": 500,
    "by_platform": {
      "pyexpress": 300,
      "pyhub": 200
    }
  },
  "orders": {
    "total": 1000,
    "pending": 50,
    "completed": 900
  },
  "communities": {
    "total": 25,
    "public": 20,
    "private": 5
  },
  "kyc": {
    "pending": 15,
    "approved": 80,
    "rejected": 5,
    "not_started": 50
  },
  "payments": {
    "total_transactions": 800,
    "successful_transactions": 750,
    "total_revenue_naira": 5000000.00
  },
  "agent_tiers": {
    "starter": 20,
    "pro": 8,
    "expert": 2,
    "master": 0,
    "elite": 0
  },
  "recent_activities": [...]
}
```

### User Management

#### Get All Users (with filtering)
```bash
GET /api/admin/users?role=farmer&kyc_status=pending&page=1&limit=50
Authorization: Bearer <admin_token>

Query Parameters:
- role: Filter by user role (farmer, agent, business, personal, logistics)
- kyc_status: Filter by KYC status (pending, approved, rejected, not_started)
- page: Page number (default: 1)
- limit: Items per page (default: 50)

Response:
{
  "users": [
    {
      "id": "user_123",
      "username": "farmer1",
      "email": "farmer1@example.com",
      "role": "farmer",
      "kyc_status": "pending",
      "created_at": "2024-01-15T10:30:00",
      ...
    }
  ],
  "pagination": {
    "total_count": 150,
    "page": 1,
    "limit": 50,
    "total_pages": 3
  }
}
```

### KYC Management

#### Approve User KYC
```bash
POST /api/admin/users/{user_id}/kyc/approve
Authorization: Bearer <admin_token>

Response:
{
  "message": "KYC approved successfully"
}
```

#### Reject User KYC
```bash
POST /api/admin/users/{user_id}/kyc/reject
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "reason": "Unclear document images. Please resubmit with better quality."
}

Response:
{
  "message": "KYC rejected successfully"
}
```

### Audit Logs

#### Get Audit Logs
```bash
GET /api/admin/audit-logs?user_id=user_123&action=kyc_approved&days=30&page=1&limit=50
Authorization: Bearer <admin_token>

Query Parameters:
- user_id: Filter by user ID
- action: Filter by action type
- days: Number of days to look back (default: 30)
- page: Page number (default: 1)
- limit: Items per page (default: 50)

Response:
{
  "logs": [
    {
      "id": "log_123",
      "user_id": "admin_001",
      "action": "kyc_approved",
      "details": {
        "target_user_id": "user_456"
      },
      "timestamp": "2024-01-15T10:30:00"
    }
  ],
  "pagination": {
    "total_count": 250,
    "page": 1,
    "limit": 50,
    "total_pages": 5
  }
}
```

---

## 🧪 Testing Admin Endpoints

### Step 1: Admin Login
```bash
# Login as admin
curl -X POST https://your-domain.com/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "abdulazeezshakrullah@gmail.com",
    "password": "Admin@2024"
  }'

# Save the token from response
TOKEN="eyJ..."
```

### Step 2: Get Dashboard Statistics
```bash
curl -X GET https://your-domain.com/api/admin/dashboard \
  -H "Authorization: Bearer $TOKEN"
```

### Step 3: View All Users
```bash
# Get all farmers
curl -X GET "https://your-domain.com/api/admin/users?role=farmer" \
  -H "Authorization: Bearer $TOKEN"

# Get pending KYC users
curl -X GET "https://your-domain.com/api/admin/users?kyc_status=pending" \
  -H "Authorization: Bearer $TOKEN"
```

### Step 4: Approve/Reject KYC
```bash
# Approve KYC
curl -X POST https://your-domain.com/api/admin/users/user_123/kyc/approve \
  -H "Authorization: Bearer $TOKEN"

# Reject KYC
curl -X POST https://your-domain.com/api/admin/users/user_456/kyc/reject \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Documents not clear. Please resubmit."
  }'
```

### Step 5: View Audit Logs
```bash
curl -X GET "https://your-domain.com/api/admin/audit-logs?days=7" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🎨 Frontend Integration (Optional)

If you want to create a frontend admin dashboard, here's what you need:

### Admin Login Component
```javascript
const adminLogin = async (email, password) => {
  const response = await fetch(`${API_URL}/api/admin/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  const data = await response.json();
  
  if (response.ok) {
    localStorage.setItem('admin_token', data.token);
    localStorage.setItem('admin_user', JSON.stringify(data.user));
    return data;
  }
  throw new Error(data.detail || 'Login failed');
};
```

### Admin Dashboard Component
```javascript
const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchDashboardStats = async () => {
      const token = localStorage.getItem('admin_token');
      
      const response = await fetch(`${API_URL}/api/admin/dashboard`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      const data = await response.json();
      setStats(data);
      setLoading(false);
    };
    
    fetchDashboardStats();
  }, []);
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div className="admin-dashboard">
      <h1>Admin Dashboard</h1>
      
      {/* User Statistics */}
      <div className="stats-card">
        <h2>Users</h2>
        <p>Total: {stats.users.total}</p>
        <p>Active: {stats.users.active}</p>
        <ul>
          <li>Farmers: {stats.users.by_role.farmer}</li>
          <li>Agents: {stats.users.by_role.agent}</li>
          <li>Businesses: {stats.users.by_role.business}</li>
        </ul>
      </div>
      
      {/* KYC Statistics */}
      <div className="stats-card">
        <h2>KYC Status</h2>
        <p>Pending: {stats.kyc.pending}</p>
        <p>Approved: {stats.kyc.approved}</p>
        <p>Rejected: {stats.kyc.rejected}</p>
      </div>
      
      {/* Revenue Statistics */}
      <div className="stats-card">
        <h2>Revenue</h2>
        <p>Total: ₦{stats.payments.total_revenue_naira.toLocaleString()}</p>
        <p>Transactions: {stats.payments.total_transactions}</p>
      </div>
      
      {/* More sections... */}
    </div>
  );
};
```

### KYC Management Component
```javascript
const KYCManagement = () => {
  const [pendingUsers, setPendingUsers] = useState([]);
  
  useEffect(() => {
    const fetchPendingKYC = async () => {
      const token = localStorage.getItem('admin_token');
      
      const response = await fetch(
        `${API_URL}/api/admin/users?kyc_status=pending`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      
      const data = await response.json();
      setPendingUsers(data.users);
    };
    
    fetchPendingKYC();
  }, []);
  
  const approveKYC = async (userId) => {
    const token = localStorage.getItem('admin_token');
    
    await fetch(`${API_URL}/api/admin/users/${userId}/kyc/approve`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    // Refresh list
    setPendingUsers(prev => prev.filter(u => u.id !== userId));
    alert('KYC approved!');
  };
  
  const rejectKYC = async (userId, reason) => {
    const token = localStorage.getItem('admin_token');
    
    await fetch(`${API_URL}/api/admin/users/${userId}/kyc/reject`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ reason })
    });
    
    // Refresh list
    setPendingUsers(prev => prev.filter(u => u.id !== userId));
    alert('KYC rejected!');
  };
  
  return (
    <div className="kyc-management">
      <h2>Pending KYC Approvals ({pendingUsers.length})</h2>
      
      {pendingUsers.map(user => (
        <div key={user.id} className="kyc-card">
          <h3>{user.username}</h3>
          <p>Email: {user.email}</p>
          <p>Role: {user.role}</p>
          
          <button onClick={() => approveKYC(user.id)}>
            Approve
          </button>
          
          <button onClick={() => {
            const reason = prompt('Rejection reason:');
            if (reason) rejectKYC(user.id, reason);
          }}>
            Reject
          </button>
        </div>
      ))}
    </div>
  );
};
```

---

## 🔒 Security Best Practices

### 1. Change Default Password
```bash
# After first login, change the password in backend/.env
# Generate new hash:
python3 -c "import bcrypt; password = input('New password: '); print(bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'))"

# Update server.py with new hash
ADMIN_PASSWORD_HASH = "new_hash_here"
```

### 2. Use Strong Passwords
- Minimum 12 characters
- Include uppercase, lowercase, numbers, and symbols
- Don't use common words or patterns

### 3. Enable Two-Factor Authentication (Future Enhancement)
- Add 2FA for admin login
- Use TOTP (Time-based One-Time Password)
- Libraries: pyotp, qrcode

### 4. Secure Token Storage
- Never commit tokens to git
- Use environment variables
- Rotate tokens regularly

### 5. Audit Logging
- All admin actions are logged
- Review logs regularly
- Set up alerts for suspicious activity

---

## 📊 Common Admin Tasks

### Monitor Platform Health
```bash
# Check total users and growth
GET /api/admin/dashboard

# Review recent activities
GET /api/admin/audit-logs?days=1
```

### Process KYC Approvals
```bash
# Get pending KYC
GET /api/admin/users?kyc_status=pending

# Review documents and approve/reject
POST /api/admin/users/{user_id}/kyc/approve
POST /api/admin/users/{user_id}/kyc/reject
```

### Monitor Revenue
```bash
# Dashboard shows total revenue
GET /api/admin/dashboard

# Check specific transaction
GET /api/paystack/transaction/verify/{reference}
```

### Review User Activities
```bash
# Get audit logs for specific user
GET /api/admin/audit-logs?user_id={user_id}&days=30

# Get all admin actions
GET /api/admin/audit-logs?action=kyc_approved
```

---

## 🚨 Troubleshooting

### Issue: Can't login as admin
```bash
# Verify admin credentials in server.py
grep ADMIN_EMAIL backend/server.py
grep ADMIN_PASSWORD_HASH backend/server.py

# Test login endpoint
curl -X POST http://localhost:8001/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"email":"abdulazeezshakrullah@gmail.com","password":"Admin@2024"}'
```

### Issue: Token expired
```bash
# Generate new token by logging in again
# Tokens expire after 7 days by default
```

### Issue: 403 Forbidden errors
```bash
# Verify you're using admin token
# Check that role in token is "admin"
```

---

## 📞 Support

For admin-related issues:
1. Check audit logs for suspicious activity
2. Review recent changes in `/api/admin/audit-logs`
3. Verify admin credentials are correct
4. Check backend logs: `tail -f /var/log/supervisor/backend.err.log`

---

**Admin Dashboard is now fully operational! 🎉**

Use these credentials to access the admin panel and manage the Pyramyd platform.
