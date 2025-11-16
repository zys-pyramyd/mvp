# Docker Deployment Guide

## 🐳 Docker Build and Deployment

### Prerequisites
- Docker installed (https://docs.docker.com/get-docker/)
- Docker Compose (optional, included with Docker Desktop)
- Environment variables configured (see RENDER_ENV_VARIABLES.md)

---

## Local Development with Docker

### 1. Build the Docker Image
```bash
cd backend
docker build -t pyramyd-backend:latest .
```

### 2. Run the Container Locally
```bash
docker run -d \
  --name pyramyd-api \
  -p 8001:8001 \
  -e MONGO_URL="mongodb+srv://user:pass@cluster.mongodb.net/db" \
  -e JWT_SECRET="your-jwt-secret" \
  -e ENCRYPTION_KEY="your-encryption-key" \
  -e PAYSTACK_SECRET_KEY="sk_test_xxx" \
  -e PAYSTACK_PUBLIC_KEY="pk_test_xxx" \
  pyramyd-backend:latest
```

### 3. Check Logs
```bash
docker logs -f pyramyd-api
```

### 4. Test the API
```bash
curl http://localhost:8001/health
curl http://localhost:8001/docs
```

### 5. Stop the Container
```bash
docker stop pyramyd-api
docker rm pyramyd-api
```

---

## Using Docker Compose (Recommended for Local Development)

### 1. Create docker-compose.yml
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8001:8001"
    environment:
      - MONGO_URL=${MONGO_URL}
      - JWT_SECRET=${JWT_SECRET}
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
      - PAYSTACK_SECRET_KEY=${PAYSTACK_SECRET_KEY}
      - PAYSTACK_PUBLIC_KEY=${PAYSTACK_PUBLIC_KEY}
      - FARMHUB_SPLIT_GROUP=${FARMHUB_SPLIT_GROUP}
      - FARMHUB_SUBACCOUNT=${FARMHUB_SUBACCOUNT}
      - SMTP_SERVER=${SMTP_SERVER}
      - SMTP_PORT=${SMTP_PORT}
      - SMTP_USERNAME=${SMTP_USERNAME}
      - SMTP_PASSWORD=${SMTP_PASSWORD}
      - FROM_EMAIL=${FROM_EMAIL}
      - ENVIRONMENT=development
    volumes:
      - ./:/app
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Optional: Local MongoDB for testing
  mongodb:
    image: mongo:7.0
    ports:
      - "27017:27017"
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=password
    volumes:
      - mongo_data:/data/db
    restart: unless-stopped

volumes:
  mongo_data:
```

### 2. Create .env file
```bash
# Copy from .env.example
cp .env.example .env

# Edit with your values
nano .env
```

### 3. Run with Docker Compose
```bash
docker-compose up -d
```

### 4. View Logs
```bash
docker-compose logs -f api
```

### 5. Stop Services
```bash
docker-compose down
```

---

## Render Deployment

### Option 1: Deploy from Dockerfile (Recommended)

1. **Push Code to GitHub**
   ```bash
   git add .
   git commit -m "Update Docker configuration"
   git push origin main
   ```

2. **Create Web Service on Render**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name:** `pyramyd-backend`
     - **Region:** Choose closest to your users
     - **Branch:** `main`
     - **Root Directory:** `backend`
     - **Environment:** `Docker`
     - **Dockerfile Path:** `./Dockerfile`
     - **Docker Command:** Leave empty (uses CMD from Dockerfile)

3. **Add Environment Variables**
   - Go to Environment section
   - Add all variables from RENDER_ENV_VARIABLES.md
   - Render automatically sets `PORT` variable

4. **Deploy**
   - Click "Create Web Service"
   - Wait for build to complete
   - Test: `https://your-app.onrender.com/health`

### Option 2: Deploy with Docker Hub

1. **Build and Tag Image**
   ```bash
   docker build -t yourusername/pyramyd-backend:latest .
   docker tag yourusername/pyramyd-backend:latest yourusername/pyramyd-backend:v1.0.0
   ```

2. **Push to Docker Hub**
   ```bash
   docker login
   docker push yourusername/pyramyd-backend:latest
   docker push yourusername/pyramyd-backend:v1.0.0
   ```

3. **Deploy on Render**
   - Select "Deploy an existing image from a registry"
   - Image URL: `docker.io/yourusername/pyramyd-backend:latest`
   - Add environment variables
   - Deploy

---

## Production Optimizations

### Multi-Worker Configuration
The Dockerfile uses 4 workers by default. Adjust based on your instance size:

```dockerfile
# For smaller instances (512MB RAM)
CMD uvicorn server:app --host 0.0.0.0 --port ${PORT:-8001} --workers 2

# For larger instances (2GB+ RAM)
CMD uvicorn server:app --host 0.0.0.0 --port ${PORT:-8001} --workers 8
```

### Environment-Specific Settings

**Development:**
```bash
ENVIRONMENT=development
DEBUG=True
```

**Production:**
```bash
ENVIRONMENT=production
DEBUG=False
```

---

## Health Checks

The Dockerfile includes a health check that runs every 30 seconds:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:${PORT}/health', timeout=5)" || exit 1
```

**Manual Health Check:**
```bash
curl http://localhost:8001/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-16T10:00:00Z"
}
```

---

## Troubleshooting

### Build Fails with "No module named 'geopy'"
- **Solution:** Ensure `geopy>=2.4.0` is in requirements.txt
- Rebuild: `docker build --no-cache -t pyramyd-backend:latest .`

### Container Exits Immediately
- Check logs: `docker logs pyramyd-api`
- Verify environment variables are set
- Check MongoDB connection string

### Port Already in Use
```bash
# Find process using port 8001
lsof -i :8001  # Mac/Linux
netstat -ano | findstr :8001  # Windows

# Kill the process or use different port
docker run -p 8002:8001 pyramyd-backend:latest
```

### Permission Denied Errors
- Ensure files are owned by appuser (non-root)
- Check Dockerfile USER directive

### MongoDB Connection Errors
- Verify `MONGO_URL` environment variable
- Check MongoDB Atlas IP whitelist (use 0.0.0.0/0 for Render)
- Ensure database user has correct permissions

---

## CI/CD with GitHub Actions

Create `.github/workflows/docker-build.yml`:

```yaml
name: Docker Build and Push

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: ./backend
        push: true
        tags: |
          yourusername/pyramyd-backend:latest
          yourusername/pyramyd-backend:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

---

## Security Best Practices

1. **Never commit secrets** - Use environment variables
2. **Use non-root user** - Already configured in Dockerfile
3. **Scan for vulnerabilities:**
   ```bash
   docker scan pyramyd-backend:latest
   ```
4. **Keep base image updated:**
   ```bash
   docker pull python:3.11-slim
   docker build --pull -t pyramyd-backend:latest .
   ```
5. **Use specific version tags** in production
6. **Enable Docker Content Trust:**
   ```bash
   export DOCKER_CONTENT_TRUST=1
   ```

---

## Monitoring and Logging

### Container Stats
```bash
docker stats pyramyd-api
```

### Resource Limits
```bash
docker run -d \
  --name pyramyd-api \
  --memory="512m" \
  --cpus="1.0" \
  -p 8001:8001 \
  pyramyd-backend:latest
```

### Export Logs
```bash
docker logs pyramyd-api > app.log 2>&1
```

---

## Useful Commands

### Cleanup
```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune -a

# Remove all unused data
docker system prune -a --volumes
```

### Inspect
```bash
# View image layers
docker history pyramyd-backend:latest

# Inspect container
docker inspect pyramyd-api

# View resource usage
docker stats pyramyd-api
```

### Shell Access
```bash
# Execute commands in running container
docker exec -it pyramyd-api bash

# Run temporary container with shell
docker run --rm -it pyramyd-backend:latest bash
```

---

## Links

- **Render Documentation:** https://render.com/docs/docker
- **Docker Documentation:** https://docs.docker.com
- **FastAPI Deployment:** https://fastapi.tiangolo.com/deployment/docker/
- **Uvicorn Settings:** https://www.uvicorn.org/settings/
