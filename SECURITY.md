# Pyramyd Platform - Security Documentation

## 🔐 Security Features Implemented

### 1. Data Encryption at Rest

**What's Protected:**
- Bank account numbers
- Mobile money numbers
- Payment card details (if stored)
- Any sensitive financial information

**How it Works:**
```python
# Encryption using Fernet (symmetric encryption)
from cryptography.fernet import Fernet

# Data is encrypted before storage
encrypted_account = encrypt_data("1234567890")  
# Stored as: gAAAAABf... (encrypted string)

# Decrypted only when needed
decrypted_account = decrypt_data(encrypted_account)
# Returns: "1234567890"
```

**Key Management:**
- Encryption key stored in `ENCRYPTION_KEY` environment variable
- Never committed to code
- Unique per environment (dev/staging/prod)
- Rotatable without data loss (with migration)

---

### 2. Password Security

**Hashing Algorithm:** bcrypt
- Industry-standard password hashing
- Automatically salted
- Configurable work factor (cost)

```python
# Password never stored in plaintext
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# Verification
bcrypt.checkpw(password.encode(), stored_hash)
```

---

### 3. JWT Authentication

**Token Security:**
- Signed with secret key (`JWT_SECRET`)
- Expires after set duration
- Contains only non-sensitive user data
- Stateless authentication

**Best Practices:**
```python
# Short-lived tokens
token_expiry = timedelta(hours=24)

# Include minimal claims
payload = {
    "id": user_id,
    "username": username,
    "role": role,
    "exp": datetime.utcnow() + token_expiry
}
```

---

### 4. Secure Account Details Storage

**API Endpoints:**

#### Save Account Details
```http
POST /api/users/account-details
Authorization: Bearer <token>
Content-Type: application/json

{
  "bank_name": "First Bank",
  "account_number": "1234567890",
  "account_name": "John Doe",
  "mobile_money_provider": "MTN",
  "mobile_money_number": "0801234567"
}
```

#### Get Account Details (Masked)
```http
GET /api/users/account-details
Authorization: Bearer <token>

Response:
{
  "has_details": true,
  "bank_name": "First Bank",
  "account_name": "John Doe",
  "account_number_masked": "****7890",
  "mobile_money_provider": "MTN",
  "mobile_money_masked": "****4567",
  "is_verified": false
}
```

#### Delete Account Details
```http
DELETE /api/users/account-details
Authorization: Bearer <token>
```

**Security Features:**
- ✅ Encryption at rest
- ✅ Only owner can access
- ✅ Masked display (last 4 digits only)
- ✅ Full number only decrypted when needed for payouts
- ✅ Audit logging capability

---

### 5. Environment Variable Security

**Required Secrets:**
```bash
# Authentication
JWT_SECRET=<min-32-chars-random>
ENCRYPTION_KEY=<fernet-key>

# Database
MONGO_URL=mongodb://...

# Payment Gateway
PAYSTACK_SECRET_KEY=sk_...

# SMS Gateway
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
```

**Security Checklist:**
- [ ] All secrets in environment variables
- [ ] No secrets in code
- [ ] `.env` in `.gitignore`
- [ ] Different keys for dev/prod
- [ ] Keys rotated regularly
- [ ] Access to production keys restricted

---

### 6. API Security

**CORS Configuration:**
```python
# Only allow specific origins
allowed_origins = [
    "https://yourdomain.com",
    "https://www.yourdomain.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
```

**Rate Limiting:**
Recommended implementation:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/auth/login")
@limiter.limit("5/minute")  # Max 5 attempts per minute
async def login():
    pass
```

**Input Validation:**
- All inputs validated with Pydantic models
- Type checking enforced
- SQL injection protection (NoSQL with pymongo)
- XSS protection (sanitized inputs)

---

### 7. Database Security

**MongoDB Security:**
```javascript
// Enable authentication
use admin
db.createUser({
  user: "admin",
  pwd: "<strong-password>",
  roles: ["root"]
})

// Connection string with auth
mongodb://admin:password@host:27017/pyramyd_db?authSource=admin
```

**Best Practices:**
- ✅ Authentication enabled
- ✅ Strong passwords
- ✅ SSL/TLS connections
- ✅ IP whitelisting
- ✅ Regular backups
- ✅ Principle of least privilege

---

### 8. HTTPS/SSL

**Production Requirements:**
- All traffic over HTTPS
- Valid SSL certificate (Let's Encrypt)
- HSTS headers enabled
- Redirect HTTP to HTTPS

**Nginx SSL Configuration:**
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
```

---

### 9. Audit Logging

**What to Log:**
- Authentication attempts (success/failure)
- Account detail changes
- Payment transactions
- KYC submissions
- Administrative actions

**Implementation:**
```python
def log_audit_event(user_id, action, details):
    audit_logs_collection.insert_one({
        "user_id": user_id,
        "action": action,
        "details": details,
        "ip_address": request.client.host,
        "timestamp": datetime.utcnow()
    })

# Usage
log_audit_event(user_id, "account_details_updated", {
    "bank_name": bank_name,
    "changed_at": datetime.utcnow()
})
```

---

### 10. Data Privacy (GDPR/NDPR Compliance)

**User Rights:**
- ✅ Right to access data
- ✅ Right to delete data
- ✅ Right to export data
- ✅ Right to rectification

**Implementation:**
```python
# Data export
@app.get("/api/users/export-data")
async def export_user_data(current_user: dict = Depends(get_current_user)):
    user_data = {
        "profile": get_user_profile(current_user["id"]),
        "orders": get_user_orders(current_user["id"]),
        "products": get_user_products(current_user["id"]),
        # ... all user data
    }
    return user_data

# Data deletion
@app.delete("/api/users/account")
async def delete_account(current_user: dict = Depends(get_current_user)):
    # Anonymize or delete all user data
    pass
```

---

## 🛡️ Security Incident Response

### If Credentials Are Compromised:

1. **Immediate Actions:**
   ```bash
   # Rotate compromised keys immediately
   
   # 1. Generate new keys
   openssl rand -base64 32  # New JWT_SECRET
   python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"  # New ENCRYPTION_KEY
   
   # 2. Update in production
   # Render: Dashboard → Environment Variables
   # Digital Ocean: App → Settings → Environment Variables
   # Docker: Update .env and restart services
   
   # 3. Force all users to re-login
   # Old JWT tokens will be invalid with new JWT_SECRET
   ```

2. **Notify Users:**
   - Send email to all users
   - Explain what happened
   - What data was affected
   - What actions you've taken
   - What they should do

3. **Investigate:**
   - Check audit logs
   - Identify breach source
   - Document findings
   - Implement fixes

4. **Prevent Future:**
   - Review security practices
   - Update documentation
   - Add monitoring
   - Train team

---

## 🔍 Security Testing

### Manual Testing:
```bash
# 1. Test authentication
curl -X POST https://api.yourdomain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"wrong"}'
# Should return 401

# 2. Test unauthorized access
curl https://api.yourdomain.com/api/users/account-details
# Should return 401 without token

# 3. Test encrypted storage
# Save account details, then check MongoDB directly
# Account numbers should be encrypted (unreadable)

# 4. Test token expiry
# Wait for token to expire, try to use it
# Should return 401
```

### Automated Testing:
```python
# pytest tests
def test_account_details_encryption():
    # Save account details
    response = client.post("/api/users/account-details",
        headers={"Authorization": f"Bearer {token}"},
        json={"account_number": "1234567890"}
    )
    
    # Check in database
    stored = db.secure_account_details.find_one({"user_id": user_id})
    
    # Should be encrypted
    assert stored["account_number"] != "1234567890"
    assert stored["account_number"].startswith("gAAAAA")
```

---

## 📋 Security Checklist for Production

### Before Launch:
- [ ] All secrets in environment variables
- [ ] Strong passwords everywhere
- [ ] HTTPS enabled with valid certificate
- [ ] Database authentication enabled
- [ ] Firewall configured
- [ ] Rate limiting enabled
- [ ] CORS configured properly
- [ ] Security headers set
- [ ] Audit logging enabled
- [ ] Backup strategy implemented
- [ ] Monitoring setup
- [ ] Incident response plan documented
- [ ] Security testing completed
- [ ] Third-party security audit (recommended)

### Regular Maintenance:
- [ ] Weekly: Review logs for anomalies
- [ ] Monthly: Rotate credentials
- [ ] Monthly: Update dependencies
- [ ] Quarterly: Security audit
- [ ] Annually: Penetration testing

---

## 🆘 Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. Email: security@yourdomain.com
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will:
- Acknowledge within 24 hours
- Provide fix timeline within 48 hours
- Credit you (if desired) once fixed

---

**Last Updated:** 2024
**Review Schedule:** Quarterly
**Next Review:** [Date]
