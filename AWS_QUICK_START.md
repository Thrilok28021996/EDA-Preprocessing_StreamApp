# AWS Quick Start Guide - Django EDA App

Get your Django EDA application running on AWS in **15 minutes**!

---

## 🎯 Fastest Deployment (Elastic Beanstalk)

### Prerequisites (5 minutes)

```bash
# 1. Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# 2. Configure AWS credentials
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Default region: us-east-1
# Default output format: json

# 3. Install EB CLI
pip install awsebcli

# 4. Verify installation
aws --version
eb --version
```

### Deploy (10 minutes)

```bash
# Navigate to project
cd django_eda_app

# Run deployment script
./deploy_to_aws.sh production

# That's it! The script will:
# ✓ Initialize Elastic Beanstalk
# ✓ Create environment with PostgreSQL
# ✓ Deploy application
# ✓ Set up health checks
# ✓ Provide application URL
```

### Access Your Application

After deployment completes:
- **Application**: http://your-app.elasticbeanstalk.com
- **Health Check**: http://your-app.elasticbeanstalk.com/health/
- **Admin Panel**: http://your-app.elasticbeanstalk.com/admin/

**Default Admin Credentials**:
- Username: `admin`
- Password: `ChangeThisPassword123!`

⚠️ **Change the password immediately after first login!**

---

## 💰 Cost Estimate

### Elastic Beanstalk Deployment
- **t3.small EC2 instance**: ~$15/month
- **RDS db.t3.micro**: ~$15/month
- **Load Balancer**: ~$18/month
- **S3 Storage**: ~$1/month
- **Total**: **~$50/month**

### Budget Option (Lightsail)
- **Lightsail bundle**: $10/month
- **Database**: $15/month
- **Total**: **~$25/month**

---

## 🔧 Post-Deployment Tasks

### 1. Secure Your Application (5 minutes)

```bash
# Change admin password via web interface
# Visit: http://your-app-url/admin/

# Generate new SECRET_KEY
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Update environment variable
eb setenv SECRET_KEY="your-new-secret-key"
```

### 2. Set Up Custom Domain (Optional - 10 minutes)

```bash
# In Route 53, create hosted zone for your domain
aws route53 create-hosted-zone --name yourdomain.com --caller-reference $(date +%s)

# Get EB environment CNAME
eb status | grep CNAME

# Create alias record pointing to EB CNAME
# Then update ALLOWED_HOSTS
eb setenv ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com"
```

### 3. Enable HTTPS (10 minutes)

```bash
# Via AWS Console:
# 1. Go to EC2 → Load Balancers
# 2. Select your EB load balancer
# 3. Add listener on port 443
# 4. Request certificate from ACM
# 5. Update security group to allow port 443
```

---

## 📊 Monitoring & Logs

```bash
# View application logs
eb logs

# Stream logs in real-time
eb logs --stream

# Check application health
eb health

# SSH into instance
eb ssh

# View CloudWatch metrics
# AWS Console → CloudWatch → Metrics → EBS
```

---

## 🚀 Scaling

### Vertical Scaling (Increase Instance Size)

```bash
# Change instance type
eb scale --instance-type t3.medium
```

### Horizontal Scaling (Add More Instances)

```bash
# Enable auto-scaling
eb scale 2  # Run 2 instances

# Or via config file (.ebextensions/04_scaling.config):
option_settings:
  aws:autoscaling:asg:
    MinSize: 2
    MaxSize: 4
  aws:autoscaling:trigger:
    MeasureName: CPUUtilization
    Statistic: Average
    Unit: Percent
    UpperThreshold: 70
    LowerThreshold: 30
```

---

## 🔄 Updates & Deployments

```bash
# Make changes to your code
git add .
git commit -m "Update feature"

# Deploy updates
eb deploy

# Rollback to previous version
eb deploy --version previous-version-label
```

---

## 🗄️ Database Management

```bash
# Get database endpoint
eb printenv | grep RDS

# Connect to RDS database
psql -h your-rds-endpoint -U ebroot -d ebdb

# Create database backup
eb ssh
pg_dump -h your-rds-endpoint -U ebroot ebdb > backup.sql

# Restore database
psql -h your-rds-endpoint -U ebroot ebdb < backup.sql
```

---

## 🛠️ Troubleshooting

### Application Not Starting

```bash
# Check logs
eb logs

# Common issues:
# 1. SECRET_KEY not set → eb setenv SECRET_KEY="your-key"
# 2. Database connection failed → Check RDS security group
# 3. Static files missing → Check collectstatic in logs
```

### High Costs

```bash
# Reduce instance size
eb scale --instance-type t3.micro

# Use RDS db.t3.micro
# Reduce instance count
eb scale 1

# Monitor costs in AWS Billing Dashboard
```

### Slow Performance

```bash
# Add Redis cache
# 1. Create ElastiCache Redis cluster
# 2. Update REDIS_URL
eb setenv REDIS_URL="redis://your-elasticache-endpoint:6379/0"

# Enable auto-scaling
eb scale 2
```

---

## 📞 Common Commands Cheat Sheet

```bash
# Deployment
eb deploy                          # Deploy application
eb deploy --staged                 # Deploy uncommitted changes

# Environment Management
eb create prod                     # Create new environment
eb use prod                        # Switch to environment
eb terminate prod                  # Delete environment

# Configuration
eb setenv KEY=value                # Set environment variable
eb printenv                        # Show all env variables
eb config                          # Edit configuration

# Monitoring
eb logs                            # View logs
eb logs --stream                   # Stream logs
eb health                          # Check health
eb status                          # Environment status

# SSH & Database
eb ssh                             # SSH to instance
eb ssh --command "python manage.py migrate"  # Run command

# Scaling
eb scale 3                         # Set instance count
eb scale --instance-type t3.large  # Change instance type
```

---

## 🎓 Next Steps

1. ✅ **Secure Application**
   - Change admin password
   - Update SECRET_KEY
   - Enable HTTPS

2. ✅ **Set Up Monitoring**
   - Configure CloudWatch alarms
   - Set up error notifications
   - Monitor costs

3. ✅ **Optimize Performance**
   - Enable Redis caching
   - Set up CDN (CloudFront)
   - Optimize database queries

4. ✅ **Implement CI/CD**
   - Set up GitHub Actions
   - Automate deployments
   - Run tests before deploy

---

## 🆘 Getting Help

- **AWS Documentation**: https://docs.aws.amazon.com/elasticbeanstalk/
- **EB CLI Guide**: https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html
- **Django on AWS**: https://docs.djangoproject.com/en/stable/howto/deployment/

**Need support?** Email: thriloke96@gmail.com

---

## 💡 Pro Tips

1. **Use `.env` file** for environment-specific configurations
2. **Enable CloudWatch logs** for better debugging
3. **Set up auto-scaling** to handle traffic spikes
4. **Use RDS snapshots** for regular backups
5. **Monitor costs** in AWS Billing Dashboard
6. **Test in staging** before deploying to production
7. **Use managed services** (RDS, ElastiCache) instead of self-hosting

---

**Deployment Time**: ~15 minutes
**Setup Difficulty**: ⭐⭐☆☆☆ (Easy)
**Monthly Cost**: $25-50 (varies by usage)

Happy Deploying! 🚀
