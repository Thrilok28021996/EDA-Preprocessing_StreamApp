# Django EDA App - AWS Deployment Package

Complete AWS deployment solution for the Django Exploratory Data Analysis & Preprocessing application.

---

## 📦 What's Included

This deployment package contains everything you need to deploy to AWS:

### 1. **Documentation**
- `AWS_DEPLOYMENT_GUIDE.md` - Comprehensive deployment guide (4 deployment options)
- `AWS_QUICK_START.md` - Get running in 15 minutes
- `DEPLOYMENT_GUIDE.md` - General deployment guide (Docker, production)

### 2. **Configuration Files**
- `.ebextensions/` - Elastic Beanstalk configuration
  - `01_django.config` - Django app configuration
  - `02_packages.config` - System packages
  - `03_environment.config` - Environment settings
- `.ebignore` - Files to exclude from EB deployment
- `.env.example` - Environment variables template

### 3. **Deployment Scripts**
- `deploy_to_aws.sh` - Automated EB deployment
- `deploy_to_ec2.sh` - EC2 instance setup script

### 4. **Docker Files**
- `Dockerfile` - Development container
- `Dockerfile.prod` - Production container
- `docker-compose.yml` - Development setup
- `docker-compose.prod.yml` - Production setup

---

## 🚀 Quick Deployment (Choose One)

### Option 1: Elastic Beanstalk (Recommended - Easiest)

```bash
# Install prerequisites
pip install awsebcli
aws configure

# Deploy (15 minutes)
./deploy_to_aws.sh production

# Access your app
eb open
```

**Best for**: Beginners, auto-scaling, managed infrastructure
**Cost**: ~$50/month
**Difficulty**: ⭐⭐☆☆☆

### Option 2: EC2 with Docker (Most Flexible)

```bash
# 1. Launch EC2 instance (t3.small)
# 2. SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. Run setup script
wget https://your-repo/deploy_to_ec2.sh
chmod +x deploy_to_ec2.sh
./deploy_to_ec2.sh

# 4. Configure and start
nano .env
docker-compose up -d
```

**Best for**: Custom configurations, full control
**Cost**: ~$15-30/month
**Difficulty**: ⭐⭐⭐☆☆

### Option 3: Lightsail (Cheapest)

```bash
# Via AWS Console:
# 1. Create Lightsail instance (Ubuntu)
# 2. SSH and run deploy_to_ec2.sh
# 3. Open ports 80, 443
```

**Best for**: Small projects, learning
**Cost**: ~$10-25/month
**Difficulty**: ⭐⭐☆☆☆

### Option 4: ECS Fargate (Fully Managed Containers)

See `AWS_DEPLOYMENT_GUIDE.md` for detailed instructions.

**Best for**: Scalable containerized apps
**Cost**: ~$30-60/month
**Difficulty**: ⭐⭐⭐⭐☆

---

## 📋 Pre-Deployment Checklist

Before deploying, ensure you have:

- [ ] AWS account with billing enabled
- [ ] AWS CLI installed and configured (`aws configure`)
- [ ] Secret key generated for Django
- [ ] Database choice decided (RDS PostgreSQL recommended)
- [ ] Domain name (optional, but recommended)
- [ ] SSL certificate plan (Let's Encrypt or ACM)

---

## 🎯 Deployment Steps Overview

### 1. Prepare Application (5 minutes)

```bash
cd django_eda_app

# Generate secret key
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Create production environment file
cp .env.example .env.production
nano .env.production  # Add your values
```

### 2. Choose Deployment Method

See options above and follow respective guide.

### 3. Deploy

```bash
# For Elastic Beanstalk
./deploy_to_aws.sh production

# For EC2
# (Run deploy_to_ec2.sh on the EC2 instance)
```

### 4. Configure Database

```bash
# If using RDS (automatically created with EB)
eb printenv | grep RDS

# Or create manually
aws rds create-db-instance \
  --db-instance-identifier django-eda-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password YourPassword123!
```

### 5. Set Up Domain & SSL (Optional)

```bash
# Point domain to EB/EC2
# For EB: Use Route 53 alias record
# For EC2: Use A record pointing to public IP

# Get free SSL certificate
sudo certbot --nginx -d yourdomain.com
```

---

## 🔧 Configuration

### Environment Variables

Required in `.env.production`:

```bash
SECRET_KEY=your-random-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,yourdomain.elasticbeanstalk.com
DATABASE_URL=postgresql://user:pass@host:5432/dbname
REDIS_URL=redis://host:6379/0
```

### Elastic Beanstalk Settings

```bash
# Set all environment variables at once
eb setenv $(cat .env.production | xargs)

# Or individually
eb setenv SECRET_KEY="your-key"
eb setenv DEBUG=False
```

---

## 📊 Post-Deployment

### Verify Deployment

```bash
# Check application health
curl http://your-app-url/health/simple/

# Should return: {"status": "ok"}

# Check detailed health
curl http://your-app-url/health/

# View logs
eb logs  # For EB
docker-compose logs -f  # For EC2
```

### Security Checklist

- [ ] Changed admin password
- [ ] Updated SECRET_KEY
- [ ] Enabled HTTPS
- [ ] Configured security groups (only 80, 443, 22)
- [ ] Set up database backups
- [ ] Configured CloudWatch alarms
- [ ] Enabled WAF (optional but recommended)

### Performance Optimization

- [ ] Enabled Redis caching
- [ ] Set up auto-scaling
- [ ] Configured CDN (CloudFront)
- [ ] Optimized database indexes
- [ ] Enabled gzip compression

---

## 💰 Cost Breakdown

### Minimum Configuration (~$25/month)
- EC2 t3.micro spot: $5/month
- RDS db.t3.micro: $15/month
- S3 storage: $1/month
- Data transfer: $4/month

### Recommended Configuration (~$50/month)
- EC2 t3.small: $15/month
- RDS db.t3.small: $25/month
- ElastiCache t3.micro: $10/month
- Load Balancer: Free tier / $18
- S3 + CloudFront: $5/month

### Production Configuration (~$150/month)
- EC2 t3.medium (2 instances): $60/month
- RDS db.t3.medium Multi-AZ: $70/month
- ElastiCache t3.small: $20/month
- Load Balancer: $18/month
- S3 + CloudFront: $10/month

---

## 🛠️ Maintenance

### Regular Tasks

```bash
# Update application
git pull
eb deploy  # or docker-compose up -d --build

# Database backup
eb ssh
pg_dump dbname > backup_$(date +%F).sql

# Clear old sessions
eb ssh --command "python manage.py clearsessions"

# View metrics
eb health --view
```

### Monitoring

- **CloudWatch**: CPU, memory, disk usage
- **Application logs**: `/var/log/eb-engine.log`
- **Health checks**: Automatic via ELB
- **Cost monitoring**: AWS Cost Explorer

---

## 🆘 Troubleshooting

### Common Issues

**1. Application won't start**
```bash
eb logs
# Check for:
# - Missing SECRET_KEY
# - Database connection errors
# - Missing dependencies
```

**2. Static files not loading**
```bash
eb ssh
source /var/app/venv/*/bin/activate
python manage.py collectstatic --noinput
```

**3. Database connection failed**
```bash
# Check security group allows port 5432
# Verify DATABASE_URL is correct
eb printenv DATABASE_URL
```

**4. High costs**
```bash
# Check instance size
eb status

# Reduce if needed
eb scale 1
eb scale --instance-type t3.micro
```

---

## 📚 Documentation Guide

| Document | Use Case | Time to Read |
|----------|----------|--------------|
| `AWS_QUICK_START.md` | Quick deployment | 5 min |
| `AWS_DEPLOYMENT_GUIDE.md` | Comprehensive guide | 30 min |
| `DEPLOYMENT_GUIDE.md` | General deployment | 20 min |

---

## 🎓 Learning Resources

- [AWS Elastic Beanstalk Tutorial](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/tutorials.html)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

---

## 🔄 Migration from Other Platforms

### From Heroku

```bash
# Export Heroku config
heroku config -s > .env.production

# Deploy to AWS
./deploy_to_aws.sh production

# Migrate database
heroku pg:backups:capture
heroku pg:backups:download
# Restore to RDS
```

### From DigitalOcean

```bash
# Backup current database
pg_dump dbname > backup.sql

# Deploy to AWS
./deploy_to_aws.sh production

# Restore database
psql -h rds-endpoint -U user dbname < backup.sql
```

---

## 📞 Support

**Email**: thriloke96@gmail.com
**Documentation**: See `AWS_DEPLOYMENT_GUIDE.md`
**Issues**: Check troubleshooting section

---

## ✅ Success Criteria

Your deployment is successful when:

- ✅ Application loads at your URL
- ✅ Health check returns `{"status": "ok"}`
- ✅ Admin panel is accessible
- ✅ File uploads work
- ✅ Charts display correctly
- ✅ HTTPS is enabled (green lock icon)
- ✅ Database backups are configured
- ✅ Monitoring is active

---

## 🎉 Next Steps After Deployment

1. **Change default admin password**
2. **Set up automated backups**
3. **Configure custom domain**
4. **Enable HTTPS/SSL**
5. **Set up monitoring alerts**
6. **Test disaster recovery**
7. **Document your deployment**
8. **Train your team**

---

**Deployment Difficulty**: ⭐⭐☆☆☆ (Easy with scripts)
**Time to Deploy**: 15-60 minutes (depending on method)
**Maintenance**: 1-2 hours/month

Ready to deploy? Start with `AWS_QUICK_START.md`! 🚀
