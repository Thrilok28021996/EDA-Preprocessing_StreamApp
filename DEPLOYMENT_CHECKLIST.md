# Django EDA Application - Deployment Checklist

Quick reference guide for deploying the Django EDA application to production.

---

## Essential Files for Deployment

### Core Application (DO NOT DELETE)
- [x] `manage.py` - Django management
- [x] `requirements.txt` - Python dependencies
- [x] `utils.py` - Core utilities
- [x] `security_utils.py` - Security functions
- [x] All app directories: `home/`, `eda/`, `preprocessing/`, `feedback/`, `api/`
- [x] `eda_project/` - Django configuration
- [x] `templates/` - HTML templates
- [x] `static/` - Static assets (CSS, JS)

### Configuration Files (REQUIRED)
- [x] `.env.example` - Environment variable template (copy to .env)
- [x] `.gitignore` - Git ignore rules
- [x] `Dockerfile` - Container configuration
- [x] `docker-compose.yml` - Docker orchestration
- [x] `nginx.conf` - Web server configuration

### Documentation (KEEP)
- [x] `README.md` - Project overview
- [x] `DEPLOYMENT_GUIDE.md` - Deployment instructions
- [x] `DEPLOYMENT_SECURITY_CHECKLIST.md` - Security guide

---

## Files Successfully Removed

### Cache & Temporary Files
- [x] All `__pycache__/` directories (except venv)
- [x] All `*.pyc`, `*.pyo` files
- [x] `.pytest_cache/` directory
- [x] `.DS_Store` files
- [x] Temporary analysis reports

### Files in .gitignore (DO NOT COMMIT)
- [x] `venv/` - Virtual environment (325MB)
- [x] `staticfiles/` - Collected static files (3.6MB)
- [x] `db.sqlite3` - Development database (532KB)
- [x] `logs/*.log` - Log files
- [x] `.env` - Environment variables (create from .env.example)

---

## Pre-Deployment Checklist

### 1. Environment Configuration
```bash
# Step 1: Create .env file from template
[ ] cp .env.example .env

# Step 2: Generate SECRET_KEY
[ ] python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Step 3: Edit .env with production values
[ ] SECRET_KEY=<generated-key>
[ ] DEBUG=False
[ ] ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
[ ] DATABASE_URL=postgresql://user:pass@host:port/db
```

### 2. Database Setup
```bash
[ ] Install PostgreSQL (production) or use SQLite (small deployments)
[ ] Run migrations: python manage.py migrate
[ ] Create superuser: python manage.py createsuperuser
```

### 3. Static Files
```bash
[ ] Collect static files: python manage.py collectstatic --noinput
[ ] Configure WhiteNoise or CDN for static file serving
```

### 4. Security Verification
```bash
[ ] Run: python manage.py check --deploy
[ ] Ensure no CRITICAL errors
[ ] Review security warnings
[ ] Verify HTTPS is enabled
```

### 5. Dependencies
```bash
[ ] Create virtual environment: python3 -m venv venv
[ ] Activate: source venv/bin/activate
[ ] Install: pip install -r requirements.txt
```

### 6. Testing
```bash
[ ] Run tests: pytest
[ ] Check coverage: pytest --cov
[ ] Verify all tests pass
```

---

## Environment Variables (Production)

### Critical (MUST SET)
```bash
SECRET_KEY=                    # Generate random 50+ char string
DEBUG=False                    # NEVER True in production
ALLOWED_HOSTS=                 # your-domain.com
DATABASE_URL=                  # PostgreSQL connection string
```

### Security Settings
```bash
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Optional (Recommended)
```bash
REDIS_URL=                     # For caching and sessions
EMAIL_HOST=                    # SMTP server
EMAIL_HOST_USER=              # Email username
EMAIL_HOST_PASSWORD=          # Email password
SENTRY_DSN=                   # Error tracking
```

---

## Deployment Options

### Option A: Docker (Recommended)
```bash
[ ] Build: docker-compose -f docker-compose.prod.yml build
[ ] Run: docker-compose -f docker-compose.prod.yml up -d
[ ] Check: docker-compose logs -f
[ ] Verify: curl http://localhost:8000/api/health/
```

### Option B: AWS Elastic Beanstalk
```bash
[ ] Install EB CLI: pip install awsebcli
[ ] Initialize: eb init -p python-3.13 eda-app
[ ] Create environment: eb create eda-production
[ ] Deploy: eb deploy
[ ] Open: eb open
```

### Option C: Traditional Server
```bash
[ ] Install Gunicorn: pip install gunicorn
[ ] Run: gunicorn eda_project.wsgi:application --bind 0.0.0.0:8000
[ ] Configure Nginx (see nginx.conf)
[ ] Set up systemd service
[ ] Start: sudo systemctl start eda-app
```

---

## Post-Deployment Verification

### Health Checks
```bash
[ ] Application health: curl https://yourdomain.com/api/health/
[ ] Admin panel: https://yourdomain.com/admin/
[ ] API endpoints: https://yourdomain.com/api/
[ ] Home page: https://yourdomain.com/
```

### Security Checks
```bash
[ ] HTTPS working (green padlock)
[ ] Security headers present (check with securityheaders.com)
[ ] CSRF protection active
[ ] Rate limiting functional
[ ] File upload validation working
```

### Functionality Tests
```bash
[ ] Upload CSV file
[ ] Generate charts (all 8 types)
[ ] Perform preprocessing operations
[ ] Export data (CSV, JSON, Excel)
[ ] Submit feedback form
[ ] Test API endpoints with JWT
```

---

## Monitoring Setup

### Logging
```bash
[ ] Configure log rotation (logrotate)
[ ] Set up centralized logging
[ ] Monitor error logs: tail -f logs/django_errors.log
[ ] Monitor security logs: tail -f logs/security.log
```

### Performance
```bash
[ ] Set up APM (New Relic, DataDog, or Sentry)
[ ] Monitor response times
[ ] Track database query performance
[ ] Monitor memory usage
```

### Backups
```bash
[ ] Configure automated database backups
[ ] Test backup restoration
[ ] Set retention policy (30 days recommended)
[ ] Backup uploaded files (media/)
```

---

## Maintenance Schedule

### Daily
- [ ] Check error logs
- [ ] Monitor disk space
- [ ] Verify backups completed

### Weekly
- [ ] Review security logs
- [ ] Check dependency updates
- [ ] Monitor performance metrics

### Monthly
- [ ] Database maintenance (VACUUM, ANALYZE)
- [ ] Rotate logs
- [ ] Apply security patches
- [ ] Review access logs

### Quarterly
- [ ] Full security audit
- [ ] Performance optimization review
- [ ] Update dependencies (major versions)
- [ ] Review and update documentation

---

## Troubleshooting

### Common Issues

**Issue: Static files not loading**
```bash
Solution:
1. python manage.py collectstatic --noinput
2. Check STATIC_ROOT and STATIC_URL in settings.py
3. Verify WhiteNoise middleware is enabled
```

**Issue: Database connection errors**
```bash
Solution:
1. Check DATABASE_URL in .env
2. Verify PostgreSQL is running
3. Test connection: psql -U username -d database_name
4. Check firewall rules
```

**Issue: CSRF verification failed**
```bash
Solution:
1. Verify CSRF_COOKIE_SECURE matches HTTPS setup
2. Check ALLOWED_HOSTS includes your domain
3. Clear browser cookies
4. Check CSRF_TRUSTED_ORIGINS
```

**Issue: 500 Internal Server Error**
```bash
Solution:
1. Check logs: tail -f logs/django_errors.log
2. Run: python manage.py check --deploy
3. Verify all environment variables are set
4. Check SECRET_KEY is properly configured
```

---

## Rollback Procedure

If deployment fails:

1. **Docker:**
   ```bash
   docker-compose down
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

2. **AWS EB:**
   ```bash
   eb deploy --version <previous-version>
   ```

3. **Traditional Server:**
   ```bash
   git checkout <previous-commit>
   sudo systemctl restart eda-app
   ```

---

## Performance Benchmarks

Expected performance metrics:

- **Response Time:** < 200ms (median)
- **File Upload:** 10MB in < 5 seconds
- **Chart Generation:** < 1 second
- **Concurrent Users:** 100+ (with Redis)
- **Uptime:** 99.9% target

---

## Security Incident Response

If security issue detected:

1. **Immediate:**
   - Isolate affected systems
   - Review security logs
   - Change all credentials
   - Notify users if data breach

2. **Investigation:**
   - Analyze logs for attack vector
   - Identify compromised data
   - Document timeline

3. **Recovery:**
   - Apply security patches
   - Restore from clean backup
   - Update security measures

4. **Post-Incident:**
   - Conduct security audit
   - Update procedures
   - Implement additional monitoring

---

## Support Contacts

- **Technical Support:** thriloke96@gmail.com
- **Security Issues:** thriloke96@gmail.com (mark URGENT)
- **Documentation:** See /django_eda_app/README.md

---

## Quick Reference Commands

```bash
# Start development server
python manage.py runserver

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Run tests
pytest

# Check for issues
python manage.py check --deploy

# Start production server (Gunicorn)
gunicorn eda_project.wsgi:application --workers 4

# View logs
tail -f logs/django.log

# Database shell
python manage.py dbshell

# Django shell
python manage.py shell
```

---

**Last Updated:** 2025-10-11
**Application Version:** Django 4.2.16
**Status:** ✅ Production Ready
