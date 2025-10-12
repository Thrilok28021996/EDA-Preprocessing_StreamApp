# EDA & Preprocessing Web Application - Deployment Guide

## 🚀 Quick Start Deployment Options

### Option 1: Development Setup (Recommended for Testing)

```bash
# Clone or navigate to project
cd django_eda_app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver 8000
```

Access at: `http://localhost:8000`

### Option 2: Docker Development

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access at: http://localhost:8000
# Redis available at: localhost:6379
```

### Option 3: Production Deployment

```bash
# Copy environment file
cp .env.example .env

# Edit .env with your production values
nano .env

# Deploy with production Docker Compose
docker-compose -f docker-compose.prod.yml up --build -d
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file from `.env.example`:

```bash
# Required for Production
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database (PostgreSQL recommended for production)
DATABASE_URL=postgresql://user:pass@localhost:5432/eda_db

# Redis Cache
REDIS_URL=redis://localhost:6379/0

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Database Configuration

#### Development (SQLite - Default)
No additional setup required.

#### Production (PostgreSQL - Recommended)
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb eda_database
sudo -u postgres createuser eda_user
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE eda_database TO eda_user;"
```

### Redis Setup (for Caching & Sessions)

#### Ubuntu/Debian
```bash
sudo apt-get install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

#### macOS
```bash
brew install redis
brew services start redis
```

#### Docker (Recommended)
Redis is included in docker-compose configurations.

---

## 🐳 Docker Deployment

### Development Environment

```yaml
# docker-compose.yml - Development
services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - DEBUG=True
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

### Production Environment

```bash
# Set up production environment
export SECRET_KEY="your-production-secret-key"
export DATABASE_URL="postgresql://user:pass@db:5432/eda_db"
export ALLOWED_HOSTS="your-domain.com"

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f web
```

---

## 🔒 Security Configuration

### SSL/TLS Setup (Production)

1. **Using Let's Encrypt with Certbot:**
```bash
# Generate SSL certificates
docker-compose -f docker-compose.prod.yml run --rm certbot \
  certonly --webroot --webroot-path=/var/www/certbot \
  -d your-domain.com -d www.your-domain.com

# Auto-renewal cron job
0 12 * * * docker-compose -f docker-compose.prod.yml run --rm certbot renew
```

2. **Update Nginx Configuration:**
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL configuration...
}
```

### Security Headers (Already Configured)
- Content Security Policy (CSP)
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block

---

## 📊 Monitoring & Logging

### Health Check Endpoints

```bash
# Comprehensive health check
curl http://localhost:8000/health/

# Simple health check (for load balancers)
curl http://localhost:8000/health/simple/
```

### Log Files

```bash
# Application logs
tail -f logs/django.log

# Error logs
tail -f logs/django_errors.log

# Performance logs
tail -f logs/performance.log
```

### Monitoring Setup

1. **Prometheus Integration:**
```yaml
# Add to docker-compose.prod.yml
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

2. **Application Metrics:**
```python
# Access metrics endpoint
GET /health/
# Returns CPU usage, memory usage, response times, etc.
```

---

## ⚡ Performance Optimization

### Production Settings

```python
# settings.py - Production
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']

# Caching
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
    }
}

# Sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Database Optimization

```sql
-- PostgreSQL optimization
-- Add indexes for session lookups
CREATE INDEX CONCURRENTLY idx_django_session_expire_date ON django_session (expire_date);

-- Add database connection pooling
-- Use pgbouncer for connection pooling
```

### Nginx Configuration

```nginx
# nginx.prod.conf
server {
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    
    # Client upload limits
    client_max_body_size 20M;
    
    # Static files caching
    location /static/ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
}
```

---

## 🧪 Testing

### Run Test Suite

```bash
# Run all tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html

# Run specific test modules
python manage.py test tests.test_home
python manage.py test tests.test_eda
python manage.py test tests.test_preprocessing
python manage.py test tests.test_feedback
```

### Load Testing

```bash
# Install load testing tools
pip install locust

# Create locustfile.py
# Run load tests
locust -f locustfile.py --host=http://localhost:8000
```

---

## 🔧 Maintenance

### Database Maintenance

```bash
# Create database backup
python manage.py dbbackup

# Apply migrations
python manage.py migrate

# Clear expired sessions
python manage.py clearsessions

# Clear cache
python manage.py shell -c "from django.core.cache import cache; cache.clear()"
```

### Log Rotation

```bash
# Set up logrotate for Django logs
sudo tee /etc/logrotate.d/django-eda <<EOF
/path/to/django_eda_app/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 www-data www-data
    postrotate
        docker-compose -f docker-compose.prod.yml restart web
    endscript
}
EOF
```

### System Updates

```bash
# Update Docker containers
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Update Python dependencies
pip install -r requirements.txt --upgrade

# Collect static files
python manage.py collectstatic --noinput
```

---

## 🚨 Troubleshooting

### Common Issues

1. **Memory Issues with Large CSV Files:**
```python
# Increase Docker memory limits
services:
  web:
    deploy:
      resources:
        limits:
          memory: 2G
```

2. **Session Data Corruption:**
```bash
# Clear all sessions
python manage.py shell -c "from django.contrib.sessions.models import Session; Session.objects.all().delete()"
```

3. **Static Files Not Loading:**
```bash
# Collect static files
python manage.py collectstatic --noinput --clear
```

4. **Redis Connection Issues:**
```bash
# Check Redis status
docker-compose logs redis

# Test Redis connection
redis-cli ping
```

### Performance Issues

1. **Slow Chart Generation:**
   - Reduce `MAX_CHART_DATA_POINTS` in settings
   - Enable chart caching with `ENABLE_CHART_CACHING = True`
   - Use data sampling for large datasets

2. **High Memory Usage:**
   - Monitor with `/health/` endpoint
   - Optimize DataFrame data types
   - Clear sessions regularly

3. **Database Locks:**
   - Check for long-running queries
   - Optimize database indexes
   - Use connection pooling

---

## 📞 Support

### Getting Help

1. **Application Logs:** Check `logs/` directory
2. **Health Check:** Visit `/health/` for system status
3. **Error Tracking:** Check `logs/django_errors.log`
4. **Performance:** Monitor `/health/` metrics

### Contact Information

- **Developer:** Thrilok E
- **Email:** thriloke96@gmail.com
- **GitHub:** https://github.com/Thrilok28021996

---

## 📋 Deployment Checklist

### Pre-deployment
- [ ] Set up production environment variables
- [ ] Configure production database
- [ ] Set up Redis for caching
- [ ] Configure email settings
- [ ] Set up SSL certificates
- [ ] Configure monitoring and logging

### Deployment
- [ ] Build and test Docker containers
- [ ] Run database migrations
- [ ] Collect static files
- [ ] Test health check endpoints
- [ ] Verify all functionality works
- [ ] Set up automated backups

### Post-deployment
- [ ] Monitor application logs
- [ ] Set up log rotation
- [ ] Configure automated updates
- [ ] Test backup and recovery procedures
- [ ] Monitor performance metrics
- [ ] Set up alerting for critical issues

---

*This deployment guide ensures a robust, scalable, and secure production deployment of the EDA & Preprocessing Web Application.*