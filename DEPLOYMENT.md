# Deployment Guide

This guide covers all the ways to deploy the ATS Resume Optimizer.

## Quick Start with Docker Compose (Recommended)

The easiest way to get everything running in production.

### Prerequisites
- Docker installed (https://docs.docker.com/get-docker/)
- Docker Compose installed
- OpenAI API Key

### Steps

1. **Clone/Download the project**
```bash
cd ats-resume-optimizer
```

2. **Create .env file with your API key**
```bash
cat > .env << EOF
OPENAI_API_KEY=sk-your-api-key-here
EOF
```

3. **Build and start containers**
```bash
docker-compose up --build
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

5. **Stop the application**
```bash
docker-compose down
```

---

## Deploy to Cloud Platforms

### AWS Deployment (EC2 + RDS)

1. **Launch EC2 Instance**
   - Ubuntu 22.04 LTS
   - t3.medium or larger (for good performance)
   - Allow ports: 80, 443, 8000, 3000

2. **SSH into instance and setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone your repository
git clone <your-repo-url>
cd ats-resume-optimizer

# Create .env with API key
echo "OPENAI_API_KEY=sk-your-key" > .env

# Start application
sudo docker-compose up -d
```

3. **Setup NGINX reverse proxy**
```bash
sudo apt install nginx -y

# Create nginx config
sudo tee /etc/nginx/sites-available/default > /dev/null <<EOF
upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:3000;
}

server {
    listen 80 default_server;
    listen [::]:80 default_server;
    
    server_name _;
    
    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable and restart nginx
sudo systemctl enable nginx
sudo systemctl restart nginx
```

4. **Setup SSL with Let's Encrypt**
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

### Heroku Deployment

1. **Install Heroku CLI**
```bash
npm install -g heroku
heroku login
```

2. **Create Heroku apps**
```bash
heroku create your-app-backend
heroku create your-app-frontend
```

3. **Deploy backend**
```bash
cd backend
heroku git:remote -a your-app-backend
git push heroku main
heroku config:set OPENAI_API_KEY=sk-your-key
```

4. **Deploy frontend**
```bash
cd ../frontend
heroku git:remote -a your-app-frontend
echo "REACT_APP_API_URL=https://your-app-backend.herokuapp.com" > .env
git push heroku main
```

### Vercel + Railway Stack

**Frontend on Vercel:**
1. Connect your GitHub repo to Vercel
2. Set environment variables: `REACT_APP_API_URL`
3. Deploy

**Backend on Railway:**
1. Connect your GitHub repo to Railway
2. Add environment variables
3. Deploy

---

## Docker Compose Production Configuration

For production, use this enhanced `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DEBUG=false
      - MAX_WORKERS=4
    volumes:
      - ./backend:/app
      - /tmp/ats_resume_optimizer:/tmp/ats_resume_optimizer
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - ats-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=${REACT_APP_API_URL:-http://localhost:8000}
    depends_on:
      backend:
        condition: service_healthy
    restart: always
    networks:
      - ats-network
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  ats-network:
    driver: bridge

volumes:
  temp_storage:
    driver: local
```

Use it with:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## Environment Variables

### Backend (.env)
```
OPENAI_API_KEY=sk-your-api-key-here
API_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini
DEBUG=false
MAX_WORKERS=4
```

### Frontend (.env)
```
REACT_APP_API_URL=https://your-api-domain.com
REACT_APP_ENV=production
```

---

## Monitoring & Maintenance

### Check logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Monitor performance
```bash
# Docker stats
docker stats

# Check disk usage
df -h
```

### Backup
```bash
# Backup database/files if applicable
docker cp ats-resume-optimizer-backend:/tmp/ats_resume_optimizer ./backups/
```

### Update application
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up --build -d
```

---

## Scaling Considerations

For high traffic:

1. **Use load balancer** (AWS ELB, Nginx)
2. **Scale backend** with multiple instances
3. **Add caching** (Redis for frequent queries)
4. **Use CDN** for frontend assets (CloudFront, Cloudflare)
5. **Database optimization** if using persistent storage
6. **Rate limiting** to prevent abuse

---

## Troubleshooting

### Containers won't start
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild everything
docker-compose down
docker-compose up --build
```

### Out of memory
```bash
# Increase Docker desktop memory limit
# Or add limits to docker-compose
```

### API key not working
```bash
# Verify it's set correctly
docker-compose exec backend env | grep OPENAI

# Update it
docker-compose down
# Edit .env file
docker-compose up -d
```

### CORS errors
- Check `REACT_APP_API_URL` is correct
- Verify backend CORS settings in `main.py`
- Clear browser cache

---

## Security Best Practices

1. **Use HTTPS** in production
2. **Keep API key secret** - never commit it
3. **Use environment variables** for all secrets
4. **Enable rate limiting** on backend
5. **Add authentication** for production
6. **Keep dependencies updated**
7. **Use strong passwords** for any accounts
8. **Monitor logs** for suspicious activity
9. **Use firewall rules** to restrict access
10. **Enable CORS** only for your domain

---

## Support

For deployment issues:
1. Check the troubleshooting section
2. Review Docker logs
3. Verify all environment variables
4. Ensure all ports are available
5. Check internet connectivity
