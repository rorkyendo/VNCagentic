# VNCagentic Deployment Guide

## Overview

This guide covers deployment options for VNCagentic, from local development to production environments. The application is fully containerized using Docker Compose for easy deployment and scaling.

## Prerequisites

### System Requirements
- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended  
- **Storage**: 10GB available space
- **Network**: Ports 3000, 6080, 8000, 8090 available

### Software Dependencies
- Docker Engine 20.10+
- Docker Compose 2.0+
- Git (for cloning repository)

### API Requirements
- Comet API key for LLM integration
- Internet connection for API calls

## Quick Start (Local Development)

### 1. Clone and Setup
```bash
# Clone repository
git clone <repository-url>
cd VNCagentic

# Copy environment template
cp .env.example .env

# Edit configuration
nano .env  # or use your preferred editor
```

### 2. Minimal Configuration
Edit `.env` with minimum required settings:
```bash
# Required: Comet API
COMET_API_KEY=your_actual_api_key_here
COMET_API_BASE_URL=https://api.comet.ml

# Database (use default for development)
POSTGRES_PASSWORD=dev_password
DATABASE_URL=postgresql+asyncpg://postgres:dev_password@postgres:5432/vncagentic
```

### 3. Start Services
```bash
# Build and start all containers
docker-compose up --build -d

# Monitor startup logs
docker-compose logs -f
```

### 4. Verify Deployment
```bash
# Check service status
docker-compose ps

# Test backend health
curl http://localhost:8000/health

# Access applications
open http://localhost:3000    # Chat interface
open http://localhost:6080    # VNC desktop
```

## Production Deployment

### 1. Security Configuration
```bash
# Generate secure passwords
POSTGRES_PASSWORD=$(openssl rand -base64 32)
VNC_PASSWORD=$(openssl rand -base64 16)

# Update .env with secure values
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
VNC_PASSWORD=$VNC_PASSWORD
LOG_LEVEL=INFO
DEBUG=false
```

### 2. Production docker-compose.yml
Create `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    restart: unless-stopped
    environment:
      - LOG_LEVEL=INFO
      - DEBUG=false
      - WORKERS=4
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  vnc-agent:
    build: ./vnc-agent
    restart: unless-stopped
    shm_size: 2gb
    environment:
      - VNC_RESOLUTION=1920x1080

  postgres:
    image: postgres:15
    restart: unless-stopped
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    environment:
      - POSTGRES_SHARED_PRELOAD_LIBRARIES=pg_stat_statements

volumes:
  postgres_data:
    driver: local
```

### 3. Start Production Environment
```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# Scale backend for high availability
docker-compose -f docker-compose.prod.yml up --scale backend=3 -d
```

## Container Management

### Health Monitoring
```bash
# Check all container health
docker-compose ps

# View real-time logs
docker-compose logs -f backend
docker-compose logs -f vnc-agent

# Monitor resource usage
docker stats
```

### Service Management
```bash
# Restart specific service
docker-compose restart backend

# Update single service
docker-compose up -d --no-deps backend

# Scale services
docker-compose up --scale backend=2 -d
```

### Maintenance Operations
```bash
# Stop all services gracefully
docker-compose down

# Update and restart
git pull
docker-compose up --build -d

# Clean up unused resources
docker system prune -f
```

## Database Management

### Backup Operations
```bash
# Create database backup
docker-compose exec postgres pg_dump -U postgres vncagentic > backup_$(date +%Y%m%d).sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec postgres pg_dump -U postgres vncagentic > $BACKUP_DIR/vncagentic_$DATE.sql
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete  # Keep 7 days
```

### Restore Operations
```bash
# Restore from backup
docker-compose exec -T postgres psql -U postgres vncagentic < backup_file.sql

# Reset database (development only)
docker-compose down
docker volume rm vncagentic_postgres_data
docker-compose up -d
```

## Environment-Specific Configurations

### Development
```bash
# .env for development
LOG_LEVEL=DEBUG
DEBUG=true
RELOAD=true
POSTGRES_PASSWORD=dev_password
```

### Staging
```bash
# .env for staging
LOG_LEVEL=INFO
DEBUG=false
POSTGRES_PASSWORD=staging_secure_password
WORKERS=2
```

### Production
```bash
# .env for production
LOG_LEVEL=WARNING
DEBUG=false
POSTGRES_PASSWORD=super_secure_random_password
WORKERS=4
RESTART_POLICY=unless-stopped
```

## Load Balancing & Scaling

### Nginx Load Balancer
Create `nginx.conf`:
```nginx
upstream backend_servers {
    server backend_1:8000;
    server backend_2:8000;
    server backend_3:8000;
}

server {
    listen 80;
    location /api/ {
        proxy_pass http://backend_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location / {
        proxy_pass http://frontend:3000;
    }
}
```

### Add to docker-compose.yml:
```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - backend
      - frontend
```

## SSL/TLS Configuration

### Using Certbot (Let's Encrypt)
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal setup
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Manual SSL Setup
```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;
    
    location / {
        proxy_pass http://frontend:3000;
    }
}
```

## Monitoring & Logging

### Centralized Logging
```yaml
# Add to docker-compose.yml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Prometheus Monitoring
```yaml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

## Troubleshooting

### Common Issues

#### Container Won't Start
```bash
# Check container logs
docker-compose logs container-name

# Check resource usage
docker system df
docker system prune

# Verify port availability
netstat -tlnp | grep 8000
```

#### Database Connection Errors
```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Test connection manually
docker-compose exec backend python -c "
import asyncpg
import asyncio
async def test():
    conn = await asyncpg.connect('postgresql://postgres:password@postgres:5432/vncagentic')
    print('Connected successfully')
    await conn.close()
asyncio.run(test())
"
```

#### VNC Agent Issues
```bash
# Restart VNC API server
docker-compose exec vnc-agent bash -c "pkill -f vnc_api.py; cd /home/computeruse && python3 vnc_api.py &"

# Check X11 display
docker-compose exec vnc-agent bash -c "DISPLAY=:1 xdpyinfo"
```

### Performance Optimization

#### Backend Scaling
```bash
# Scale backend instances
docker-compose up --scale backend=4 -d

# Monitor CPU usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

#### Database Tuning
```sql
-- PostgreSQL optimization
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
SELECT pg_reload_conf();
```

#### Memory Management
```bash
# Limit container memory
docker-compose run --memory=1g backend
```

## Security Best Practices

### Network Security
```bash
# Restrict external access
iptables -A INPUT -p tcp --dport 8000 -s localhost -j ACCEPT
iptables -A INPUT -p tcp --dport 8000 -j DROP
```

### Container Security
```yaml
# Security-hardened service
services:
  backend:
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
    user: "1000:1000"
```

### Secrets Management
```bash
# Use Docker secrets for production
echo "my_secret_password" | docker secret create postgres_password -

# Reference in compose file
services:
  postgres:
    secrets:
      - postgres_password
```

## Backup & Disaster Recovery

### Automated Backup Script
```bash
#!/bin/bash
# backup.sh - Daily backup script

BACKUP_DIR="/backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Database backup
docker-compose exec postgres pg_dump -U postgres vncagentic > $BACKUP_DIR/database.sql

# Configuration backup
cp .env $BACKUP_DIR/
cp docker-compose.yml $BACKUP_DIR/

# Upload to S3 (optional)
# aws s3 sync $BACKUP_DIR s3://your-backup-bucket/vncagentic/$(date +%Y%m%d)/

echo "Backup completed: $BACKUP_DIR"
```

### Recovery Procedure
```bash
# Stop services
docker-compose down

# Restore database
docker-compose up -d postgres
sleep 10
docker-compose exec -T postgres psql -U postgres vncagentic < backup/database.sql

# Restore configuration
cp backup/.env .
cp backup/docker-compose.yml .

# Start all services
docker-compose up -d
```

---

For additional support, see [README.md](../README.md) or create an issue in the repository.
