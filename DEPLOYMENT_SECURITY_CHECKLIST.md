# Deployment Security Checklist

## Pre-Deployment Checklist

Use this checklist before deploying the Django EDA application to production.

### 1. Environment Configuration

- [ ] Create `.env` file from `.env.example`
  ```bash
  cp .env.example .env
  ```

- [ ] Generate and set secure `SECRET_KEY`
  ```bash
  python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
  ```
  Update `.env` with generated key

- [ ] Set `DEBUG=False` in `.env`

- [ ] Configure `ALLOWED_HOSTS` with your domain(s)
  ```
  ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,api.yourdomain.com
  ```

- [ ] Verify `.env` file is in `.gitignore`
  ```bash
  cat .gitignore | grep .env
  ```

### 2. Database Configuration

- [ ] Configure production database (PostgreSQL recommended)
  ```
  DATABASE_URL=postgresql://user:password@host:port/database
  ```

- [ ] Clear existing sessions (session serializer changed)
  ```bash
  python manage.py clearsessions
  ```

- [ ] Run migrations
  ```bash
  python manage.py migrate
  ```

- [ ] Create superuser
  ```bash
  python manage.py createsuperuser
  ```

### 3. Dependencies Installation

- [ ] Install production dependencies
  ```bash
  pip install -r requirements.txt
  ```

- [ ] Verify critical security packages are installed:
  - [ ] python-decouple (environment variables)
  - [ ] python-magic (MIME type detection)
  - [ ] django-ratelimit (rate limiting)

### 4. Static Files

- [ ] Collect static files
  ```bash
  python manage.py collectstatic --noinput
  ```

- [ ] Configure static file serving (WhiteNoise or CDN)

### 5. SSL/HTTPS Configuration

- [ ] Obtain SSL certificate (Let's Encrypt, etc.)

- [ ] Configure web server (Nginx/Apache) for HTTPS

- [ ] Verify SSL settings in `.env`:
  ```
  SECURE_SSL_REDIRECT=True
  SECURE_HSTS_SECONDS=31536000
  CSRF_COOKIE_SECURE=True
  SESSION_COOKIE_SECURE=True
  ```

- [ ] Test HTTPS redirect
  ```bash
  curl -I http://yourdomain.com
  # Should see 301/302 redirect to https://
  ```

### 6. Security Settings Verification

- [ ] Verify SECRET_KEY is not the default
  ```bash
  # Should NOT contain 'django-insecure'
  echo $SECRET_KEY
  ```

- [ ] Verify DEBUG is False
  ```bash
  python manage.py shell
  >>> from django.conf import settings
  >>> print(settings.DEBUG)
  False
  ```

- [ ] Verify ALLOWED_HOSTS doesn't contain '*'
  ```bash
  python manage.py shell
  >>> from django.conf import settings
  >>> print(settings.ALLOWED_HOSTS)
  # Should show your domains, not '*'
  ```

### 7. File Upload Security

- [ ] Test file upload validation:
  - [ ] Try uploading non-CSV file (should be rejected)
  - [ ] Try uploading oversized file (should be rejected)
  - [ ] Try uploading file with suspicious content (should be rejected)

- [ ] Verify upload directory permissions
  ```bash
  ls -la media/
  # Should not be world-writable
  ```

### 8. Rate Limiting

- [ ] Test rate limiting on file uploads
  - [ ] Attempt 11 uploads in quick succession
  - [ ] Should get rate limit error on 11th attempt

- [ ] Test API rate limiting
  - [ ] Make 101 API calls in quick succession
  - [ ] Should get 429 (Too Many Requests) error

### 9. Session Security

- [ ] Verify session settings:
  ```bash
  python manage.py shell
  >>> from django.conf import settings
  >>> print(settings.SESSION_SERIALIZER)
  'django.contrib.sessions.serializers.JSONSerializer'
  >>> print(settings.SESSION_COOKIE_SECURE)
  True
  >>> print(settings.SESSION_COOKIE_HTTPONLY)
  True
  ```

- [ ] Test session expiration (sessions should expire after 1 hour)

### 10. CSRF Protection

- [ ] Verify CSRF middleware is enabled
  ```bash
  python manage.py shell
  >>> from django.conf import settings
  >>> 'django.middleware.csrf.CsrfViewMiddleware' in settings.MIDDLEWARE
  True
  ```

- [ ] Test POST requests without CSRF token (should fail)

- [ ] Test feedback form submission (should require CSRF token)

### 11. Logging Configuration

- [ ] Create logs directory with proper permissions
  ```bash
  mkdir -p logs
  chmod 750 logs
  ```

- [ ] Verify log files are created:
  - [ ] logs/django.log
  - [ ] logs/django_errors.log
  - [ ] logs/security.log
  - [ ] logs/performance.log

- [ ] Set up log rotation (logrotate)

### 12. Error Handling

- [ ] Test 404 page
  ```bash
  curl https://yourdomain.com/nonexistent
  ```

- [ ] Test 500 error page (in production mode)

- [ ] Verify errors don't expose sensitive information

### 13. Security Headers

- [ ] Test security headers
  ```bash
  curl -I https://yourdomain.com
  ```

  Should include:
  - [ ] X-Content-Type-Options: nosniff
  - [ ] X-Frame-Options: DENY
  - [ ] X-XSS-Protection: 1; mode=block
  - [ ] Content-Security-Policy: (should be present)
  - [ ] Strict-Transport-Security: (if HTTPS)

### 14. Database Security

- [ ] Use strong database password

- [ ] Configure database user with minimal permissions

- [ ] Enable database SSL connection (if available)

- [ ] Backup database
  ```bash
  python manage.py dumpdata > backup_$(date +%Y%m%d).json
  ```

### 15. Application Server

- [ ] Use Gunicorn (not Django development server)
  ```bash
  gunicorn eda_project.wsgi:application --bind 0.0.0.0:8000
  ```

- [ ] Configure worker processes appropriately
  ```
  workers = (2 * cpu_cores) + 1
  ```

- [ ] Set up process monitoring (systemd, supervisor, etc.)

### 16. Firewall Configuration

- [ ] Configure firewall to allow only necessary ports:
  - [ ] 80 (HTTP - redirects to HTTPS)
  - [ ] 443 (HTTPS)
  - [ ] 22 (SSH - from specific IPs only)

- [ ] Block direct access to application port (8000)

- [ ] Configure fail2ban for SSH protection

### 17. Backup Strategy

- [ ] Set up automated database backups

- [ ] Set up automated media files backup

- [ ] Test backup restoration process

- [ ] Store backups securely (encrypted, off-site)

### 18. Monitoring

- [ ] Set up application monitoring (Sentry, New Relic, etc.)

- [ ] Configure error notifications

- [ ] Set up uptime monitoring

- [ ] Monitor security logs regularly

### 19. Performance

- [ ] Enable caching (Redis recommended)

- [ ] Configure database connection pooling

- [ ] Enable gzip compression

- [ ] Optimize static file serving (CDN or WhiteNoise)

### 20. Final Security Tests

Run the security test suite:
```bash
python manage.py test test_security_fixes -v 2
```

Expected results:
- [ ] All tests pass
- [ ] No pickle serialization detected
- [ ] File validation working
- [ ] Input sanitization working
- [ ] Rate limiting working
- [ ] Session security configured
- [ ] CSRF protection enabled

### 21. Penetration Testing

Consider running:

- [ ] OWASP ZAP scan
  ```bash
  zap-cli quick-scan https://yourdomain.com
  ```

- [ ] SSL Labs test
  https://www.ssllabs.com/ssltest/

- [ ] Security headers check
  https://securityheaders.com

### 22. Documentation

- [ ] Document deployment process

- [ ] Document security configurations

- [ ] Create incident response plan

- [ ] Train team on security best practices

## Post-Deployment Monitoring

### First 24 Hours

- [ ] Monitor error logs
  ```bash
  tail -f logs/django_errors.log
  ```

- [ ] Monitor security logs
  ```bash
  tail -f logs/security.log
  ```

- [ ] Check application performance

- [ ] Verify all features working

- [ ] Test file upload functionality

- [ ] Test API endpoints

### Ongoing

- [ ] Weekly security log review

- [ ] Monthly security updates
  ```bash
  pip list --outdated
  pip install -U package-name
  ```

- [ ] Quarterly security audit

- [ ] Annual penetration testing

## Emergency Procedures

### If Security Breach Detected

1. [ ] Immediately disable affected services

2. [ ] Rotate all secrets:
   - [ ] SECRET_KEY
   - [ ] Database passwords
   - [ ] API keys
   - [ ] SSL certificates (if compromised)

3. [ ] Review security logs
   ```bash
   grep -i "suspicious\|attack\|injection" logs/security.log
   ```

4. [ ] Clear all sessions
   ```bash
   python manage.py clearsessions
   ```

5. [ ] Notify affected users

6. [ ] Document incident

7. [ ] Apply patches/fixes

8. [ ] Re-deploy with enhanced security

## Rollback Plan

If deployment fails:

1. [ ] Stop application server

2. [ ] Restore database from backup
   ```bash
   python manage.py loaddata backup_YYYYMMDD.json
   ```

3. [ ] Revert code to previous version
   ```bash
   git checkout previous-tag
   ```

4. [ ] Restart services

5. [ ] Verify functionality

6. [ ] Investigate failure

## Sign-Off

Deployment completed by: ___________________

Date: ___________________

Security review completed by: ___________________

Date: ___________________

Production approval: ___________________

Date: ___________________

---

## Support Contacts

**Security Issues:**
Email: thriloke96@gmail.com

**Emergency Contact:**
[Add emergency contact information]

---

**Document Version:** 1.0
**Last Updated:** 2025-10-06
