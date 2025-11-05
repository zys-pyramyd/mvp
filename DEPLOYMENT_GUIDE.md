# Pyramyd Platform - Deployment Guide

This guide covers deployment to various platforms including Render, Digital Ocean, and other cloud providers.

## 📋 Pre-Deployment Checklist

Before deploying, ensure you have:

### 1. API Keys & Credentials
- [ ] Paystack Secret Key (`PAYSTACK_SECRET_KEY`)
- [ ] Paystack Public Key (`PAYSTACK_PUBLIC_KEY`)
- [ ] Paystack Subaccount Code (`FARMHUB_SUBACCOUNT`)
- [ ] Paystack Split Group Code (`FARMHUB_SPLIT_GROUP`)
- [ ] Kwik Delivery API Key (`KWIK_API_KEY`)
- [ ] MongoDB Connection String (production)
- [ ] JWT Secret Key (generate secure random string)

### 2. Account Setup
- [ ] Paystack account created and verified
- [ ] Kwik Delivery account (for Lagos, Oyo, FCT Abuja deliveries)
- [ ] MongoDB Atlas account (recommended for production)
- [ ] Domain name (optional but recommended)
- [ ] SSL certificate (usually provided by hosting platform)

### 3. Code Preparation
- [ ] All environment variables documented
- [ ] Database migrations tested
- [ ] Production build tested locally
- [ ] CORS settings configured
- [ ] Security headers configured

---

## 🚀 Deployment Options

### Option 1: Render (Recommended for Quick Deploy)

Render provides easy deployment with automatic SSL and good performance.

#### Prerequisites
1. Render account (free tier available)
2. GitHub/GitLab repository with your code
3. MongoDB Atlas connection string

#### Step 1: Setup MongoDB Atlas (if not already)
```bash
# Visit https://www.mongodb.com/cloud/atlas
# 1. Create a free cluster
# 2. Create database user
# 3. Whitelist all IPs (0.0.0.0/0) for Render access
# 4. Get connection string:
#    mongodb+srv://username:password@cluster.mongodb.net/pyramyd_prod
```

#### Step 2: Deploy Backend on Render

1. **Create New Web Service:**
   - Go to Render Dashboard
   - Click "New +" → "Web Service"
   - Connect your Git repository
   - Configure:
     ```
     Name: pyramyd-backend
     Environment: Python 3
     Build Command: cd backend && pip install -r requirements.txt
     Start Command: cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT
     ```

2. **Add Environment Variables:**
   ```
   MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/pyramyd_prod
   DB_NAME=pyramyd_prod
   JWT_SECRET_KEY=<generate-secure-random-string>
   PAYSTACK_SECRET_KEY=sk_live_your_secret_key
   PAYSTACK_PUBLIC_KEY=pk_live_your_public_key
   FARMHUB_SUBACCOUNT=ACCT_your_subaccount_code
   FARMHUB_SPLIT_GROUP=SPL_your_split_group_code
   KWIK_API_KEY=your_kwik_api_key
   KWIK_API_URL=https://api.kwik.delivery/v1
   ```

3. **Deploy:**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)
   - Note your backend URL: `https://pyramyd-backend.onrender.com`

#### Step 3: Deploy Frontend on Render

1. **Create Static Site:**
   - Click "New +" → "Static Site"
   - Connect your Git repository
   - Configure:
     ```
     Name: pyramyd-frontend
     Build Command: cd frontend && yarn install && yarn build
     Publish Directory: frontend/build
     ```

2. **Add Environment Variables:**
   ```
   REACT_APP_BACKEND_URL=https://pyramyd-backend.onrender.com
   ```

3. **Deploy:**
   - Click "Create Static Site"
   - Wait for deployment (5-10 minutes)
   - Your app will be live at: `https://pyramyd-frontend.onrender.com`

#### Step 4: Configure CORS on Backend

Update backend/server.py to allow your frontend domain:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://pyramyd-frontend.onrender.com",
        "http://localhost:3000"  # Keep for local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Option 2: Digital Ocean App Platform

Digital Ocean provides excellent performance and scalability.

#### Prerequisites
1. Digital Ocean account
2. GitHub/GitLab repository
3. MongoDB connection string

#### Step 1: Create App

1. **Go to App Platform:**
   - Visit https://cloud.digitalocean.com/apps
   - Click "Create App"
   - Connect GitHub/GitLab repository

2. **Configure Backend Component:**
   ```yaml
   name: pyramyd-backend
   source_dir: /backend
   build_command: pip install -r requirements.txt
   run_command: uvicorn server:app --host 0.0.0.0 --port $PORT
   http_port: 8080
   instance_size: basic-xs
   environment_variables:
     - key: MONGO_URL
       value: mongodb+srv://...
     - key: DB_NAME
       value: pyramyd_prod
     - key: JWT_SECRET_KEY
       value: <secret>
       scope: RUN_TIME
       type: SECRET
     # ... add all other variables
   ```

3. **Configure Frontend Component:**
   ```yaml
   name: pyramyd-frontend
   source_dir: /frontend
   build_command: yarn install && yarn build
   output_dir: build
   environment_variables:
     - key: REACT_APP_BACKEND_URL
       value: ${pyramyd-backend.PUBLIC_URL}
   ```

4. **Deploy:**
   - Review configuration
   - Click "Create Resources"
   - Wait for deployment (10-15 minutes)

#### Step 2: Custom Domain (Optional)

1. Add domain in Digital Ocean
2. Update DNS records:
   ```
   Type: CNAME
   Name: @
   Value: <your-app>.ondigitalocean.app
   ```
3. Enable SSL (automatic)

---

### Option 3: Docker Deployment (VPS/Self-Hosted)

For deployment on your own VPS (DigitalOcean Droplet, AWS EC2, etc.)

#### Prerequisites
- VPS with Ubuntu 20.04+
- Docker and Docker Compose installed
- Domain name pointed to your VPS IP

#### Step 1: Server Setup

```bash
# SSH into your server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Install Nginx (for reverse proxy)
apt install nginx -y

# Install Certbot (for SSL)
apt install certbot python3-certbot-nginx -y
```

#### Step 2: Clone and Configure

```bash
# Clone repository
git clone <your-repo-url> /var/www/pyramyd
cd /var/www/pyramyd

# Create production environment files
cat > backend/.env << EOL
MONGO_URL=mongodb://mongodb:27017
DB_NAME=pyramyd_prod
JWT_SECRET_KEY=$(openssl rand -hex 32)
PAYSTACK_SECRET_KEY=sk_live_your_key
PAYSTACK_PUBLIC_KEY=pk_live_your_key
FARMHUB_SUBACCOUNT=ACCT_your_code
FARMHUB_SPLIT_GROUP=SPL_your_code
KWIK_API_KEY=your_key
KWIK_API_URL=https://api.kwik.delivery/v1
EOL

cat > frontend/.env << EOL
REACT_APP_BACKEND_URL=https://api.yourdomain.com
EOL
```

#### Step 3: Docker Compose

Use the existing `docker-compose.yml` in the repository:

```bash
# Build and start containers
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

#### Step 4: Nginx Configuration

```bash
# Create Nginx config
cat > /etc/nginx/sites-available/pyramyd << 'EOL'
# Frontend
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        
        # CORS headers (if needed)
        add_header 'Access-Control-Allow-Origin' 'https://yourdomain.com';
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS';
        add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type';
    }
}
EOL

# Enable site
ln -s /etc/nginx/sites-available/pyramyd /etc/nginx/sites-enabled/

# Test configuration
nginx -t

# Restart Nginx
systemctl restart nginx
```

#### Step 5: SSL Certificate

```bash
# Get SSL certificates
certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com

# Auto-renewal is configured automatically
# Test renewal:
certbot renew --dry-run
```

---

## 🔐 Security Checklist

### Before Going Live:

- [ ] Change all default passwords
- [ ] Use strong JWT secret (32+ characters random)
- [ ] Enable HTTPS/SSL everywhere
- [ ] Configure CORS properly (whitelist specific domains)
- [ ] Set up MongoDB user authentication
- [ ] Whitelist only necessary IPs for MongoDB
- [ ] Use environment variables (never commit secrets)
- [ ] Enable rate limiting on API endpoints
- [ ] Set up monitoring and alerts
- [ ] Configure backup system for database
- [ ] Review and test KYC document upload security
- [ ] Implement API request logging
- [ ] Set up error tracking (Sentry, LogRocket, etc.)

### Production Environment Variables:

```bash
# Backend (.env)
MONGO_URL=<production-mongo-connection-string>
DB_NAME=pyramyd_prod
JWT_SECRET_KEY=<32-char-random-string>
PAYSTACK_SECRET_KEY=sk_live_<your-live-key>
PAYSTACK_PUBLIC_KEY=pk_live_<your-live-key>
FARMHUB_SUBACCOUNT=ACCT_<your-code>
FARMHUB_SPLIT_GROUP=SPL_<your-code>
KWIK_API_KEY=<your-production-key>
KWIK_API_URL=https://api.kwik.delivery/v1

# Frontend (.env)
REACT_APP_BACKEND_URL=https://api.yourdomain.com
```

---

## 📊 Post-Deployment Tasks

### 1. Verify Deployment

```bash
# Test backend health
curl https://api.yourdomain.com/api/health

# Test frontend loading
curl https://yourdomain.com

# Test API endpoints
curl https://api.yourdomain.com/api/products
curl https://api.yourdomain.com/api/communities
curl https://api.yourdomain.com/api/categories/products
```

### 2. Test Payment Integration

1. Create test account
2. Add product to cart
3. Proceed through checkout
4. Use Paystack test card: 4084084084084081
5. Verify payment success and commission calculation

### 3. Test PWA Features

1. Open site in Chrome/Edge
2. Check for install prompt
3. Install as PWA
4. Test offline mode (disconnect network)
5. Verify service worker in DevTools

### 4. Monitor Performance

```bash
# Setup monitoring with PM2 (if using Node/VPS)
npm install -g pm2
pm2 startup
pm2 save

# Or use cloud monitoring:
# - Render: Built-in metrics
# - Digital Ocean: App metrics
# - New Relic for detailed APM
```

### 5. Database Backup

```bash
# MongoDB Atlas: Enable automated backups
# Or manual backup:
mongodump --uri="mongodb+srv://..." --out=/backup/pyramyd-$(date +%Y%m%d)

# Restore if needed:
mongorestore --uri="mongodb+srv://..." /backup/pyramyd-20240101
```

---

## 🐛 Troubleshooting Deployment

### Issue: Backend not responding

```bash
# Check backend logs
docker-compose logs backend
# or on Render/DO: Check logs in dashboard

# Common issues:
# - MongoDB connection string incorrect
# - Missing environment variables
# - Port conflicts
```

### Issue: Frontend can't reach backend

```bash
# Check CORS configuration
# Verify REACT_APP_BACKEND_URL is correct
# Check browser console for CORS errors

# Test backend directly:
curl https://api.yourdomain.com/api/products
```

### Issue: Paystack payments failing

```bash
# Verify Paystack keys are LIVE keys (not test)
# Check subaccount code is correct
# Ensure split group exists in Paystack dashboard
# Check webhook URL is configured in Paystack
```

### Issue: Service Worker not registering

```bash
# Must be served over HTTPS (not HTTP)
# Check service-worker.js is accessible
# Clear browser cache completely
# Check for console errors
```

---

## 🎯 Production Best Practices

1. **Use a CDN**: CloudFlare, AWS CloudFront for static assets
2. **Enable Compression**: Gzip/Brotli for faster loading
3. **Database Indexing**: Index frequently queried fields
4. **Caching**: Redis for session data and API responses
5. **Load Balancing**: If traffic grows significantly
6. **Regular Backups**: Automated daily database backups
7. **Monitoring**: Set up uptime monitoring (UptimeRobot, Pingdom)
8. **Error Tracking**: Sentry or Rollbar for error reporting
9. **Analytics**: Google Analytics or Mixpanel
10. **Documentation**: Keep API docs updated (Swagger/OpenAPI)

---

## 📞 Support & Maintenance

### Regular Maintenance Tasks:

**Weekly:**
- Check error logs
- Monitor API response times
- Review security alerts

**Monthly:**
- Update dependencies
- Review database performance
- Check disk space usage
- Backup verification

**Quarterly:**
- Security audit
- Performance optimization
- Feature usage analysis
- Cost optimization review

---

## 🚀 Scaling Guide

When your platform grows, consider:

1. **Database Scaling:**
   - MongoDB sharding
   - Read replicas
   - Connection pooling

2. **Application Scaling:**
   - Horizontal scaling (multiple instances)
   - Load balancer (Nginx, HAProxy)
   - Microservices architecture

3. **Caching Layer:**
   - Redis for sessions and frequently accessed data
   - CDN for static assets

4. **Queue System:**
   - RabbitMQ or Celery for background jobs
   - Email notifications
   - Payment processing

---

**Your Pyramyd platform is ready for production! 🌾🚀**

For questions or issues, refer to the main README.md troubleshooting section.
