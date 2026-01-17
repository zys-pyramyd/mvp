# Environment Variables for Render Deployment

## 🔐 Required Environment Variables

Add these in your Render Dashboard under **Environment** section.

---

## 1. Database Configuration

### `MONGO_URL` ⚠️ CRITICAL
- **Description:** MongoDB connection string
- **Format:** `mongodb+srv://username:password@cluster.mongodb.net/database_name`
- **Example:** `mongodb+srv://pyramyd_user:SecurePassword123@cluster0.abcde.mongodb.net/pyramyd_db`
- **Where to get:**
  - MongoDB Atlas: https://cloud.mongodb.com
  - Create a free cluster
  - Get connection string from "Connect" → "Connect your application"
- **⚠️ Security:** Never commit this to version control

---

## 2. Authentication & Security

### `JWT_SECRET` ⚠️ CRITICAL
- **Description:** Secret key for JWT token generation
- **Format:** Long random string (minimum 32 characters)
- **Example:** `kJ8s9Df3mN2vB7xQ1pL5yT4wE6rU0zA9cG2hF8bK3dM7jN1sP`
- **Generate using:**
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(48))"
  ```
  or
  ```bash
  openssl rand -base64 48
  ```
- **⚠️ Security:** Must be unique, never reuse or share

### `ENCRYPTION_KEY` ⚠️ CRITICAL
- **Description:** Fernet key for encrypting sensitive user data
- **Format:** Base64-encoded 32-byte key
- **Example:** `bXyEncryptionKey12345abcdefghijk67890ABCDEFGH=`
- **Generate using:**
  ```bash
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  ```
- **⚠️ Security:** Critical for data encryption, backup securely

---

## 3. Payment Gateway (Paystack)

### `PAYSTACK_SECRET_KEY` ⚠️ CRITICAL
- **Description:** Paystack secret key for API authentication
- **Format:** `sk_live_xxxxxxxxxxxxxxxxxxxx` (live) or `sk_test_xxxxxxxxxxxxxxxxxxxx` (test)
- **Example:** `sk_live_abc123def456ghi789jkl012mno345pqr`
- **Where to get:**
  - Paystack Dashboard: https://dashboard.paystack.com
  - Settings → API Keys & Webhooks
- **⚠️ Security:** Use test key for staging, live key for production only

### `PAYSTACK_PUBLIC_KEY`
- **Description:** Paystack public key (safe to expose on frontend)
- **Format:** `pk_live_xxxxxxxxxxxxxxxxxxxx` or `pk_test_xxxxxxxxxxxxxxxxxxxx`
- **Example:** `pk_live_xyz789abc123def456ghi012jkl345mno`
- **Where to get:** Same location as secret key

### `FARMHUB_SPLIT_GROUP`
- **Description:** Paystack split group code for FarmHub transactions
- **Format:** `SPL_xxxxxxxxxxxx`
- **Default:** `SPL_dCqIOTFNRu`
- **Where to get:**
  - Paystack Dashboard → Transaction Splits
  - Create a split group for Sophie Farms Investment Ltd

### `FARMHUB_SUBACCOUNT`
- **Description:** Paystack subaccount code for FarmHub
- **Format:** `ACCT_xxxxxxxxxxxx`
- **Default:** `ACCT_c94r8ia2jeg41lx`
- **Where to get:** Paystack Dashboard → Subaccounts

---

## 4. SMS & Phone Verification (Twilio)

### `TWILIO_ACCOUNT_SID`
- **Description:** Twilio account identifier
- **Format:** `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
- **Example:** `AC1234567890abcdef1234567890abcdef`
- **Where to get:**
  - Twilio Console: https://console.twilio.com
  - Account Info section

### `TWILIO_AUTH_TOKEN` ⚠️ SENSITIVE
- **Description:** Twilio authentication token
- **Format:** 32-character alphanumeric string
- **Example:** `abcdef1234567890abcdef1234567890`
- **Where to get:** Same location as SID
- **⚠️ Security:** Keep secret, never expose publicly

### `TWILIO_PHONE_NUMBER` (Optional)
- **Description:** Twilio phone number for SMS
- **Format:** `+1234567890` (E.164 format)
- **Example:** `+12345678901`
- **Where to get:** Twilio Console → Phone Numbers

---

## 5. Email Service (SMTP)

### `SMTP_SERVER`
- **Description:** SMTP server hostname
- **Default:** `smtp.gmail.com`
- **Examples:**
  - Gmail: `smtp.gmail.com`
  - SendGrid: `smtp.sendgrid.net`
  - Mailgun: `smtp.mailgun.org`

### `SMTP_PORT`
- **Description:** SMTP server port
- **Default:** `587` (TLS)
- **Options:**
  - `587` - TLS (recommended)
  - `465` - SSL
  - `25` - Unencrypted (not recommended)

### `SMTP_USERNAME`
- **Description:** SMTP authentication username
- **Format:** Usually your email address
- **Example:** `noreply@pyramydhub.com`

### `SMTP_PASSWORD` ⚠️ SENSITIVE
- **Description:** SMTP authentication password
- **Format:** App-specific password (for Gmail)
- **Example:** `abcd efgh ijkl mnop` (Gmail app password)
- **Where to get (Gmail):**
  - Google Account → Security → 2-Step Verification → App passwords
- **⚠️ Security:** Use app-specific passwords, not your main email password

### `FROM_EMAIL` (Optional)
- **Description:** Email address shown as sender
- **Default:** `support@pyramydhub.com`
- **Example:** `noreply@pyramydhub.com`

---

## 6. Kwik Delivery API (Optional)

### `KWIK_ACCESS_TOKEN`
- **Description:** Kwik Delivery API access token
- **Format:** Long alphanumeric string
- **Example:** `kwik_live_abc123def456ghi789jkl012`
- **Where to get:** Contact Kwik Delivery for API access
- **Note:** Optional - fallback delivery calculation used if not provided

### `KWIK_DOMAIN_NAME`
- **Description:** Your domain name registered with Kwik
- **Default:** `pyramyd.com`
- **Example:** `pyramydhub.com`

### `KWIK_VENDOR_ID`
- **Description:** Your vendor ID in Kwik system
- **Format:** Alphanumeric string
- **Example:** `vendor_12345abc`
- **Where to get:** Kwik Delivery dashboard

---

## 7. Application Configuration

### `ENVIRONMENT` (Optional)
- **Description:** Application environment
- **Values:** `development`, `staging`, `production`
- **Default:** `production` (on Render)
- **Recommendation:** Set to `production`

### `CORS_ORIGINS` (Optional)
- **Description:** Allowed CORS origins (comma-separated)
- **Format:** `https://domain1.com,https://domain2.com`
- **Example:** `https://pyramydhub.com,https://www.pyramydhub.com`
- **Note:** Render automatically handles CORS for same domain

---

## 📋 Environment Variables Checklist

Copy this checklist when deploying to Render:

### ✅ Critical (Must Have)
- [ ] `MONGO_URL` - MongoDB connection string
- [ ] `JWT_SECRET` - JWT secret key (generate new)
- [ ] `ENCRYPTION_KEY` - Fernet encryption key (generate new)
- [ ] `PAYSTACK_SECRET_KEY` - Paystack secret key
- [ ] `PAYSTACK_PUBLIC_KEY` - Paystack public key

### ⚠️ Important (Recommended)
- [ ] `FARMHUB_SPLIT_GROUP` - Paystack split group
- [ ] `FARMHUB_SUBACCOUNT` - Paystack subaccount
- [ ] `SMTP_SERVER` - Email server
- [ ] `SMTP_PORT` - Email port (587)
- [ ] `SMTP_USERNAME` - Email username
- [ ] `SMTP_PASSWORD` - Email password
- [ ] `FROM_EMAIL` - Sender email address

### 📱 Optional (If Using Services)
- [ ] `TWILIO_ACCOUNT_SID` - Twilio SID
- [ ] `TWILIO_AUTH_TOKEN` - Twilio token
- [ ] `KWIK_ACCESS_TOKEN` - Kwik API token
- [ ] `KWIK_DOMAIN_NAME` - Your domain
- [ ] `KWIK_VENDOR_ID` - Kwik vendor ID

---

## 🚀 Render Deployment Steps

### 1. Create Web Service on Render
1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name:** `pyramyd-backend`
   - **Region:** Choose closest to your users
   - **Branch:** `main` or `master`
   - **Root Directory:** `backend` (if monorepo)
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn server:app --host 0.0.0.0 --port $PORT`

### 2. Add Environment Variables
In Render dashboard → Environment section, add all variables above.

### 3. Configure MongoDB Atlas
1. Whitelist Render IP or use `0.0.0.0/0` (all IPs)
2. Create database user with read/write permissions
3. Get connection string and add as `MONGO_URL`

### 4. Test Deployment
After deployment completes:
- Check logs for errors
- Test health endpoint: `https://your-app.onrender.com/health`
- Test API: `https://your-app.onrender.com/docs`

---

## 🔒 Security Best Practices

### 1. Generate Unique Keys
```bash
# JWT Secret
python -c "import secrets; print(secrets.token_urlsafe(48))"

# Encryption Key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 2. Use Different Keys for Each Environment
- Development: Use test keys
- Staging: Use separate test keys
- Production: Use live keys only

### 3. Never Commit Secrets
- Add `.env` to `.gitignore`
- Use Render's environment variables UI
- Rotate keys if accidentally exposed

### 4. Monitor Access
- Enable Paystack webhook security
- Set up MongoDB Atlas access logs
- Monitor Twilio usage for anomalies

---

## 📝 Example .env File (Local Development Only)

```bash
# DO NOT COMMIT THIS FILE
# Use Render's Environment Variables UI for production

# Database
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/db_name

# Security
JWT_SECRET=your-generated-jwt-secret-here
ENCRYPTION_KEY=your-generated-encryption-key-here

# Paystack
PAYSTACK_SECRET_KEY=sk_test_your_test_key
PAYSTACK_PUBLIC_KEY=pk_test_your_test_key
FARMHUB_SPLIT_GROUP=SPL_dCqIOTFNRu
FARMHUB_SUBACCOUNT=ACCT_c94r8ia2jeg41lx

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@pyramydhub.com

# Twilio (Optional)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-twilio-token

# Kwik (Optional)
KWIK_ACCESS_TOKEN=your-kwik-token
KWIK_DOMAIN_NAME=pyramyd.com
KWIK_VENDOR_ID=your-vendor-id

# Config
ENVIRONMENT=development
```

---

## ⚡ Quick Copy-Paste Template for Render

```
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/pyramyd_db
JWT_SECRET=[GENERATE_NEW]
ENCRYPTION_KEY=[GENERATE_NEW]
PAYSTACK_SECRET_KEY=sk_live_[YOUR_KEY]
PAYSTACK_PUBLIC_KEY=pk_live_[YOUR_KEY]
FARMHUB_SPLIT_GROUP=SPL_dCqIOTFNRu
FARMHUB_SUBACCOUNT=ACCT_c94r8ia2jeg41lx
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=noreply@pyramydhub.com
SMTP_PASSWORD=[YOUR_APP_PASSWORD]
FROM_EMAIL=noreply@pyramydhub.com
TWILIO_ACCOUNT_SID=[IF_USING_TWILIO]
TWILIO_AUTH_TOKEN=[IF_USING_TWILIO]
ENVIRONMENT=production
```

---

## 🆘 Troubleshooting

### "MongoDB connection failed"
- Check `MONGO_URL` format
- Verify IP whitelist in MongoDB Atlas
- Ensure database user has correct permissions

### "Paystack authentication failed"
- Verify you're using correct key (test vs live)
- Check key hasn't been rotated/regenerated
- Ensure no extra spaces in key

### "Email sending failed"
- Verify SMTP credentials
- For Gmail: Enable "Less secure app access" or use App Password
- Check SMTP port is correct (587 for TLS)

### "Encryption errors"
- Regenerate `ENCRYPTION_KEY` if corrupted
- ⚠️ WARNING: Regenerating key will make existing encrypted data unreadable

---

## 📞 Support

For Render-specific issues: https://render.com/docs/deploy-fastapi
For MongoDB Atlas: https://www.mongodb.com/docs/atlas/
For Paystack: https://paystack.com/docs/
