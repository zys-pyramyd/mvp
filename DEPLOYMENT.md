# Pyramyd Platform - Deployment Guide

## 🔐 Security Checklist

### Before Deployment

1. **Generate Secure Keys**
   ```bash
   # JWT Secret (minimum 32 characters)
   openssl rand -base64 32
   
   # Encryption Key for sensitive data
   python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

2. **Update Environment Variables**
   - Never commit `.env` files
   - Use `.env.example` as template
   - Set all secrets in hosting platform dashboard

3. **Database Security**
   - Use strong MongoDB credentials
   - Enable IP whitelisting
   - Enable SSL/TLS connections

---

## 🚀 Deployment Options

### Option 1: Render.com (Recommended for Quick Deploy)

**Pros**: Easy setup, free tier available, auto-scaling
**Cons**: Cold starts on free tier

#### Steps:
1. **Prepare Repository**
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Deploy to Render**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render auto-detects `render.yaml`
   - Set environment variables in dashboard:
     - `MONGO_URL`: From Render MongoDB service
     - `PAYSTACK_SECRET_KEY`: Your Paystack key
     - `TWILIO_ACCOUNT_SID`: Your Twilio SID
     - `TWILIO_AUTH_TOKEN`: Your Twilio token
   - Click "Apply"

3. **Verify Deployment**
   - Frontend: `https://pyramyd-frontend.onrender.com`
   - Backend: `https://pyramyd-backend.onrender.com/docs`

#### Estimated Cost:
- **Free Tier**: Backend + Frontend (with cold starts)
- **Starter**: $7/month per service = $14/month
- **MongoDB**: $0 (free 500MB) or $7/month (starter)

---

### Option 2: Digital Ocean App Platform

**Pros**: Predictable pricing, no cold starts, good performance
**Cons**: No free tier

#### Steps:

1. **Install Digital Ocean CLI**
   ```bash
   # macOS
   brew install doctl
   
   # Linux
   cd ~
   wget https://github.com/digitalocean/doctl/releases/download/v1.98.1/doctl-1.98.1-linux-amd64.tar.gz
   tar xf ~/doctl-1.98.1-linux-amd64.tar.gz
   sudo mv ~/doctl /usr/local/bin
   ```

2. **Authenticate**
   ```bash
   doctl auth init
   # Enter your Digital Ocean API token
   ```

3. **Update app.yaml**
   - Replace `your-username/pyramyd` with your GitHub repo path

4. **Deploy**
   ```bash
   # Via CLI
   doctl apps create --spec app.yaml
   
   # Or via Dashboard
   # Go to https://cloud.digitalocean.com/apps
   # Click "Create App" → Connect GitHub → Auto-detects app.yaml
   ```

5. **Set Environment Variables**
   - In Digital Ocean dashboard → App → Settings → Environment Variables
   - Add all required secrets

6. **Deploy and Monitor**
   ```bash
   # Get app ID
   doctl apps list
   
   # View logs
   doctl apps logs <app-id> --follow
   ```

#### Estimated Cost:
- **Basic Setup**: ~$25/month
  - 2x basic-xxs instances ($5 each) = $10
  - MongoDB basic-xs = $15
- **Production**: ~$50-100/month with scaling

---

### Option 3: Docker + Your Own VPS

**Pros**: Full control, cheapest for high traffic
**Cons**: Requires server management

#### Steps:

1. **Set Up VPS** (DigitalOcean, Linode, AWS EC2)
   ```bash
   # Connect to VPS
   ssh root@your-server-ip
   
   # Update system
   apt update && apt upgrade -y
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   
   # Install Docker Compose
   apt install docker-compose -y
   ```

2. **Clone Repository**
   ```bash
   git clone https://github.com/your-username/pyramyd.git
   cd pyramyd
   ```

3. **Configure Environment**
   ```bash
   # Backend
   cp backend/.env.example backend/.env
   nano backend/.env  # Edit with your values
   
   # Frontend
   cp frontend/.env.example frontend/.env
   nano frontend/.env  # Edit with your values
   ```

4. **Deploy with Docker Compose**
   ```bash
   # Build and start services
   docker-compose up -d --build
   
   # View logs
   docker-compose logs -f
   
   # Check status
   docker-compose ps
   ```

5. **Set Up Reverse Proxy (Nginx)**
   ```bash
   apt install nginx certbot python3-certbot-nginx -y
   ```
   
   Create `/etc/nginx/sites-available/pyramyd`:
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       location / {
           proxy_pass http://localhost:3000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
       
       location /api {
           proxy_pass http://localhost:8001;
           proxy_http_version 1.1;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```
   
   ```bash
   # Enable site
   ln -s /etc/nginx/sites-available/pyramyd /etc/nginx/sites-enabled/
   nginx -t
   systemctl reload nginx
   
   # Get SSL certificate
   certbot --nginx -d yourdomain.com
   ```

6. **Monitoring**
   ```bash
   # View logs
   docker-compose logs -f backend
   docker-compose logs -f frontend
   
   # Restart services
   docker-compose restart
   
   # Update application
   git pull
   docker-compose up -d --build
   ```

#### Estimated Cost:
- **VPS**: $5-10/month (1GB RAM)
- **Domain**: $10-15/year
- **Total**: ~$6-11/month

---

## 🔒 Production Security Best Practices

### 1. Environment Variables
✅ Never hardcode secrets
✅ Use different keys for dev/staging/prod
✅ Rotate keys regularly
✅ Use secret management services

### 2. Database Security
```bash
# MongoDB security checklist
- Enable authentication
- Use strong passwords
- Enable SSL/TLS
- Regular backups
- IP whitelisting
- Disable remote root access
```

### 3. API Security
- Rate limiting enabled
- CORS configured properly
- JWT tokens expire (set reasonable timeout)
- Input validation on all endpoints
- SQL injection protection (using pymongo)
- XSS protection headers

### 4. SSL/HTTPS
- Always use HTTPS in production
- Use Let's Encrypt for free certificates
- Enforce HTTPS redirects
- Set HSTS headers

### 5. Backup Strategy
```bash
# MongoDB backup (daily cron job)
0 2 * * * mongodump --uri="$MONGO_URL" --out=/backups/$(date +\%Y\%m\%d)

# Keep last 7 days
find /backups/* -mtime +7 -exec rm -rf {} \;
```

---

## 📊 Monitoring & Logging

### Application Logs
```bash
# Docker
docker-compose logs -f

# Render
# View in dashboard → Logs tab

# Digital Ocean
doctl apps logs <app-id> --follow
```

### Health Checks
- Backend: `https://your-domain.com/health`
- Frontend: `https://your-domain.com/`

### Performance Monitoring
Recommended tools:
- **Sentry**: Error tracking
- **LogRocket**: User session replay
- **New Relic**: Performance monitoring
- **Uptime Robot**: Uptime monitoring (free)

---

## 🔄 CI/CD Pipeline (GitHub Actions)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Render
        env:
          RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
        run: |
          curl -X POST \
            -H "Authorization: Bearer $RENDER_API_KEY" \
            https://api.render.com/v1/services/${{ secrets.RENDER_SERVICE_ID }}/deploys
```

---

## 🆘 Troubleshooting

### Backend not starting
```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Missing environment variables
# 2. MongoDB connection failed
# 3. Port already in use
```

### Frontend not connecting to backend
```bash
# Verify REACT_APP_BACKEND_URL in .env
# Check CORS settings in backend
# Ensure /api prefix is used for all API calls
```

### Database connection issues
```bash
# Test MongoDB connection
mongosh "$MONGO_URL"

# Check firewall rules
# Verify IP whitelist
# Confirm credentials
```

---

## 📞 Support

For deployment issues:
1. Check logs first
2. Review environment variables
3. Verify all services are running
4. Check firewall/network settings

---

## ✅ Deployment Checklist

- [ ] Generated secure JWT_SECRET
- [ ] Generated secure ENCRYPTION_KEY
- [ ] Set all environment variables
- [ ] Database configured with authentication
- [ ] SSL/HTTPS enabled
- [ ] CORS configured correctly
- [ ] Firewall rules set
- [ ] Backups configured
- [ ] Monitoring set up
- [ ] Domain configured
- [ ] Health checks passing
- [ ] Test all critical flows

---

**🎉 Your Pyramyd platform is now deployed securely!**
