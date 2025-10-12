# Security Upgrade Guide

## Overview

This document provides a comprehensive guide for the security upgrades applied to the Django EDA application. All critical and high-severity vulnerabilities have been addressed.

## What Changed?

### Critical Changes (Immediate Action Required)

1. **Pickle Removed** - All `pickle` serialization replaced with secure JSON
2. **Environment Variables** - SECRET_KEY, DEBUG, ALLOWED_HOSTS now from .env
3. **CSRF Protection** - All @csrf_exempt decorators removed
4. **Session Security** - Changed from PickleSerializer to JSONSerializer

### Important Changes

- Rate limiting added to all endpoints
- Comprehensive file upload validation
- Input sanitization for all user inputs
- Security event logging
- HTTPS enforcement in production
- Improved session cookie security

## Files Modified

### Core Files
- `/Volumes/personal/programmingFolders/saas/EDA-Preprocessing_StreamApp_main/django_eda_app/eda_project/settings.py` - Security configuration
- `/Volumes/personal/programmingFolders/saas/EDA-Preprocessing_StreamApp_main/django_eda_app/utils.py` - Secure serialization
- `/Volumes/personal/programmingFolders/saas/EDA-Preprocessing_StreamApp_main/django_eda_app/requirements.txt` - New dependencies

### New Files
- `/Volumes/personal/programmingFolders/saas/EDA-Preprocessing_StreamApp_main/django_eda_app/security_utils.py` - Security utilities module
- `/Volumes/personal/programmingFolders/saas/EDA-Preprocessing_StreamApp_main/django_eda_app/test_security_fixes.py` - Security test suite
- `/Volumes/personal/programmingFolders/saas/EDA-Preprocessing_StreamApp_main/django_eda_app/SECURITY_FIXES_SUMMARY.md` - Detailed fixes
- `/Volumes/personal/programmingFolders/saas/EDA-Preprocessing_StreamApp_main/django_eda_app/DEPLOYMENT_SECURITY_CHECKLIST.md` - Deployment guide

### View Files
- `/Volumes/personal/programmingFolders/saas/EDA-Preprocessing_StreamApp_main/django_eda_app/home/views.py` - Secure upload, rate limiting
- `/Volumes/personal/programmingFolders/saas/EDA-Preprocessing_StreamApp_main/django_eda_app/api/views.py` - Secure API, rate limiting
- `/Volumes/personal/programmingFolders/saas/EDA-Preprocessing_StreamApp_main/django_eda_app/feedback/views.py` - Input sanitization

### Configuration Files
- `/Volumes/personal/programmingFolders/saas/EDA-Preprocessing_StreamApp_main/django_eda_app/.env.example` - Updated with all variables
- `/Volumes/personal/programmingFolders/saas/EDA-Preprocessing_StreamApp_main/django_eda_app/eda_project/middleware.py` - Enhanced security

## Installation Steps

### 1. Backup Current Installation

```bash
# Backup database
python manage.py dumpdata > backup_before_security_upgrade.json

# Backup .env if exists
cp .env .env.backup

# Create git commit
git add -A
git commit -m "Backup before security upgrade"
```

### 2. Install New Dependencies

```bash
# Install new security packages
pip install python-magic==0.4.27
pip install django-ratelimit==4.1.0

# Or install all at once
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Create .env file from template
cp .env.example .env

# Generate new SECRET_KEY
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Edit .env and set:
# - SECRET_KEY (use generated key above)
# - DEBUG=True (for development) or False (for production)
# - ALLOWED_HOSTS (your domain or localhost,127.0.0.1)
```

### 4. Clear Existing Sessions

**IMPORTANT:** Session serializer changed from Pickle to JSON. Existing sessions are incompatible.

```bash
python manage.py clearsessions
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Run Security Tests

```bash
python manage.py test test_security_fixes -v 2
```

All tests should pass.

### 7. Test Locally

```bash
# Start development server
python manage.py runserver

# Test file upload
# Test API endpoints
# Test feedback form
```

## Breaking Changes

### Session Incompatibility

**Issue:** Existing user sessions will be invalid.

**Impact:** All users will be logged out and need to re-upload their data.

**Reason:** Session serializer changed from PickleSerializer (insecure) to JSONSerializer (secure).

**Action:**
```bash
python manage.py clearsessions
```

### CSRF Token Required

**Issue:** POST requests now require CSRF tokens.

**Impact:** API clients must include CSRF tokens or use session authentication.

**Action:** Update API clients to:
1. Get CSRF token from cookies
2. Include in POST request headers as `X-CSRFToken`

**Example:**
```javascript
// Get CSRF token
const csrfToken = document.cookie.match(/csrftoken=([^;]+)/)[1];

// Include in fetch request
fetch('/api/upload/', {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrfToken
    },
    body: formData
});
```

### Rate Limiting

**Issue:** Requests are now rate-limited.

**Impact:** Rapid successive requests may be blocked.

**Limits:**
- File uploads: 10 per hour
- API calls: 100 per hour
- Feedback: 5 per 5 minutes

**Action:** Implement exponential backoff in API clients.

### Environment Variables Required

**Issue:** Application won't start without proper .env configuration.

**Impact:** Must create .env file with required variables.

**Action:** Follow step 3 above.

## Migration for Existing Deployments

### Development Environment

```bash
# 1. Pull latest changes
git pull origin main

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env
cp .env.example .env
# Edit .env with your settings (DEBUG=True for dev)

# 4. Clear sessions
python manage.py clearsessions

# 5. Test
python manage.py runserver
```

### Production Environment

**DO NOT deploy directly to production. Follow these steps:**

1. **Test in Staging First**
   ```bash
   # Deploy to staging environment
   # Run full test suite
   # Verify all functionality
   ```

2. **Schedule Maintenance Window**
   - Notify users of downtime
   - Choose low-traffic period
   - Allow 1-2 hours for deployment

3. **Backup Everything**
   ```bash
   # Database
   python manage.py dumpdata > backup_production.json

   # Media files
   tar -czf media_backup.tar.gz media/

   # Code
   git tag pre-security-upgrade-$(date +%Y%m%d)
   git push --tags
   ```

4. **Deploy**
   ```bash
   # Pull latest code
   git pull origin main

   # Install dependencies
   pip install -r requirements.txt

   # Configure .env (CRITICAL)
   # Set DEBUG=False
   # Set proper SECRET_KEY
   # Set ALLOWED_HOSTS

   # Clear sessions
   python manage.py clearsessions

   # Collect static files
   python manage.py collectstatic --noinput

   # Restart application
   systemctl restart gunicorn  # or your app server
   ```

5. **Verify Deployment**
   ```bash
   # Check application is running
   curl https://yourdomain.com

   # Check logs
   tail -f logs/django.log
   tail -f logs/security.log

   # Test critical functionality
   # - File upload
   # - Data analysis
   # - API endpoints
   ```

6. **Monitor**
   - Watch error logs for first 24 hours
   - Monitor security logs
   - Check performance metrics

## Rollback Plan

If something goes wrong:

```bash
# 1. Stop application
systemctl stop gunicorn

# 2. Restore code
git checkout pre-security-upgrade-YYYYMMDD

# 3. Restore database
python manage.py loaddata backup_production.json

# 4. Restart application
systemctl start gunicorn

# 5. Investigate issue
# Check logs: logs/django_errors.log
```

## Troubleshooting

### "CSRF verification failed"

**Cause:** CSRF protection now enabled.

**Solution:** Ensure CSRF token is included in POST requests.

### "SECRET_KEY must be set"

**Cause:** SECRET_KEY not configured in .env.

**Solution:**
```bash
# Generate key
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Add to .env
echo "SECRET_KEY=<generated-key>" >> .env
```

### "Rate limit exceeded"

**Cause:** Too many requests in short time.

**Solution:** Wait for rate limit window to reset, or adjust limits in settings.

### "Session data corrupted"

**Cause:** Old pickle sessions incompatible with new JSON serializer.

**Solution:**
```bash
python manage.py clearsessions
```

### "File upload failed"

**Cause:** New file validation may be stricter.

**Solution:** Check:
- File is valid CSV
- File size under 10MB
- File doesn't contain suspicious content

## Testing

### Manual Testing Checklist

- [ ] File upload works
- [ ] CSV parsing works
- [ ] Data analysis features work
- [ ] Charts generate correctly
- [ ] Preprocessing operations work
- [ ] Export functionality works
- [ ] Feedback form works
- [ ] API endpoints work
- [ ] Rate limiting works (test with rapid requests)
- [ ] Error pages display correctly

### Automated Testing

```bash
# Run full test suite
python manage.py test -v 2

# Run only security tests
python manage.py test test_security_fixes -v 2

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## Security Verification

### Verify No Pickle Usage

```bash
# Should return no results
grep -r "pickle.loads\|pickle.dumps" --include="*.py" \
  --exclude-dir=venv --exclude-dir=env .
```

### Verify CSRF Protection

```bash
# Should show no @csrf_exempt decorators
grep -r "@csrf_exempt" --include="*.py" \
  --exclude-dir=venv --exclude-dir=env .
```

### Verify Environment Variables

```bash
python manage.py shell
>>> from django.conf import settings
>>> assert 'django-insecure' not in settings.SECRET_KEY
>>> assert settings.SESSION_SERIALIZER == 'django.contrib.sessions.serializers.JSONSerializer'
>>> print("All checks passed!")
```

## Performance Impact

### Expected Changes:

1. **JSON Serialization:** Slightly slower than pickle, but secure
   - Impact: < 100ms per operation
   - Acceptable for security improvement

2. **File Validation:** Additional MIME type checking
   - Impact: < 50ms per file upload
   - Worth it for security

3. **Rate Limiting:** Cache lookups for rate checks
   - Impact: < 10ms per request
   - Negligible

### Optimization Tips:

- Use Redis for caching/sessions (faster than database)
- Enable gzip compression
- Use CDN for static files
- Configure database connection pooling

## Support

### Documentation
- See `SECURITY_FIXES_SUMMARY.md` for detailed fixes
- See `DEPLOYMENT_SECURITY_CHECKLIST.md` for deployment guide
- See `.env.example` for configuration options

### Issues

For security-related issues:
- Email: thriloke96@gmail.com
- Do NOT post security issues publicly

For general issues:
- Create GitHub issue (if applicable)
- Include logs and error messages
- Include steps to reproduce

## Next Steps

After successful upgrade:

1. **Monitor Logs**
   ```bash
   tail -f logs/security.log
   ```

2. **Regular Security Updates**
   ```bash
   pip list --outdated
   pip install -U package-name
   ```

3. **Security Audit**
   - Review logs weekly
   - Update dependencies monthly
   - Full security audit quarterly

4. **Consider Additional Security**
   - Implement user authentication
   - Add two-factor authentication
   - Set up Web Application Firewall
   - Enable DDoS protection

## Changelog

### Version 2.0 - Security Hardening (2025-10-06)

**Critical Fixes:**
- Replaced pickle with secure JSON serialization
- Moved SECRET_KEY to environment variable
- Fixed DEBUG mode configuration
- Fixed ALLOWED_HOSTS configuration
- Removed CSRF exemptions
- Changed session serializer to JSON

**High-Priority Fixes:**
- Added rate limiting
- Implemented file upload validation
- Added input sanitization
- Enabled HTTPS enforcement
- Hardened session security
- Added security event logging

**New Features:**
- Security utilities module
- Comprehensive test suite
- Deployment checklist
- Security documentation

---

**Version:** 2.0
**Date:** 2025-10-06
**Author:** Thrilok E
**Contact:** thriloke96@gmail.com
