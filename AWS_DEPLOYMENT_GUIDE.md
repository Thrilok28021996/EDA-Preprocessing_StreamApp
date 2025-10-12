# AWS Deployment Guide for Django EDA Application

Complete guide for deploying the Django EDA & Preprocessing application to AWS using multiple deployment options.

---

## 🚀 Quick Start - Deployment Options

### Option 1: AWS Elastic Beanstalk (Easiest - Recommended for Beginners)
- **Best for**: Quick deployment, auto-scaling, managed infrastructure
- **Time to deploy**: 15-30 minutes
- **Cost**: ~$20-50/month (t3.small instance)

### Option 2: AWS EC2 with Docker (Flexible)
- **Best for**: Full control, custom configurations
- **Time to deploy**: 30-60 minutes
- **Cost**: ~$10-30/month (t3.micro/small)

### Option 3: AWS ECS Fargate (Container-based)
- **Best for**: Scalable containerized applications
- **Time to deploy**: 45-90 minutes
- **Cost**: ~$25-60/month

### Option 4: AWS Lightsail (Simplest)
- **Best for**: Small projects, learning
- **Time to deploy**: 10-20 minutes
- **Cost**: $3.50-10/month

---

## 📋 Prerequisites

### 1. AWS Account Setup
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure
# Enter: AWS Access Key ID, Secret Access Key, Region (e.g., us-east-1)
```

### 2. Required Tools
```bash
# Install EB CLI (for Elastic Beanstalk)
pip install awsebcli

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

---

## 🎯 Option 1: AWS Elastic Beanstalk Deployment (RECOMMENDED)

### Step 1: Prepare Application

```bash
# Navigate to project directory
cd django_eda_app

# Create .ebignore file
cat > .ebignore << 'EOF'
venv/
*.pyc
__pycache__/
db.sqlite3
.env
.git/
logs/
media/
staticfiles/
*.log
EOF

# Update requirements.txt (already includes all dependencies)
```

### Step 2: Create Elastic Beanstalk Configuration

Create `.ebextensions/01_django.config`:

```yaml
option_settings:
  aws:elasticbeanstalk:application:environment:
    DJANGO_SETTINGS_MODULE: "eda_project.settings"
    PYTHONPATH: "/var/app/current:$PYTHONPATH"
  aws:elasticbeanstalk:container:python:
    WSGIPath: "eda_project.wsgi:application"
  aws:elasticbeanstalk:environment:proxy:staticfiles:
    /static: staticfiles

container_commands:
  01_migrate:
    command: "source /var/app/venv/*/bin/activate && python manage.py migrate --noinput"
    leader_only: true
  02_collectstatic:
    command: "source /var/app/venv/*/bin/activate && python manage.py collectstatic --noinput"
    leader_only: true
  03_create_superuser:
    command: "source /var/app/venv/*/bin/activate && python manage.py shell -c \"from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'changeme123')\""
    leader_only: true
```

### Step 3: Initialize and Deploy

```bash
# Initialize Elastic Beanstalk
eb init -p python-3.11 django-eda-app --region us-east-1

# Create environment variables file
cat > .env.production << 'EOF'
SECRET_KEY=your-super-secret-key-here-change-this
DEBUG=False
ALLOWED_HOSTS=.elasticbeanstalk.com,.amazonaws.com
EOF

# Create environment
eb create django-eda-prod --instance-type t3.small --database.engine postgres

# Set environment variables
eb setenv $(cat .env.production | xargs)

# Deploy application
eb deploy

# Open application in browser
eb open
```

### Step 4: Configure RDS Database (Automatic with EB)

```bash
# Database is automatically created with --database.engine postgres
# Get database credentials
eb printenv

# Update settings to use RDS
# (Already configured in settings.py to use DATABASE_URL)
```

### Step 5: Set Up Redis Cache (Optional)

```bash
# Create ElastiCache Redis cluster via AWS Console or CLI
aws elasticache create-cache-cluster \
  --cache-cluster-id django-eda-redis \
  --engine redis \
  --cache-node-type cache.t3.micro \
  --num-cache-nodes 1

# Update environment variable
eb setenv REDIS_URL=redis://your-redis-endpoint:6379/0
```

---

## 🖥️ Option 2: AWS EC2 Deployment with Docker

### Step 1: Launch EC2 Instance

```bash
# Launch Ubuntu EC2 instance (t3.small recommended)
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.small \
  --key-name your-key-pair \
  --security-group-ids sg-xxxxxxxx \
  --subnet-id subnet-xxxxxxxx \
  --block-device-mappings '[{"DeviceName":"/dev/xvda","Ebs":{"VolumeSize":30}}]' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=django-eda-server}]'

# Get instance public IP
aws ec2 describe-instances --filters "Name=tag:Name,Values=django-eda-server" --query 'Reservations[0].Instances[0].PublicIpAddress'
```

### Step 2: Configure EC2 Security Group

```bash
# Allow HTTP (80), HTTPS (443), SSH (22)
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxx \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxx \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxx \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0
```

### Step 3: Connect and Install Dependencies

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login to apply docker group
exit
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### Step 4: Deploy Application

```bash
# Clone or upload your application
git clone your-repo-url django_eda_app
cd django_eda_app

# Create production environment file
nano .env
# Add production values (SECRET_KEY, DATABASE_URL, etc.)

# Build and run with Docker Compose
docker-compose -f docker-compose.prod.yml up -d --build

# Check status
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f web
```

### Step 5: Set Up Nginx and SSL

```bash
# Install Certbot for SSL
sudo apt install certbot python3-certbot-nginx -y

# Configure Nginx (already in nginx.conf)
sudo cp nginx.conf /etc/nginx/sites-available/django-eda
sudo ln -s /etc/nginx/sites-available/django-eda /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

## 🐳 Option 3: AWS ECS Fargate Deployment

### Step 1: Build and Push Docker Image to ECR

```bash
# Create ECR repository
aws ecr create-repository --repository-name django-eda-app

# Get login command
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account-id.dkr.ecr.us-east-1.amazonaws.com

# Build and tag image
docker build -f Dockerfile.prod -t django-eda-app:latest .
docker tag django-eda-app:latest your-account-id.dkr.ecr.us-east-1.amazonaws.com/django-eda-app:latest

# Push to ECR
docker push your-account-id.dkr.ecr.us-east-1.amazonaws.com/django-eda-app:latest
```

### Step 2: Create ECS Task Definition

Create `ecs-task-definition.json`:

```json
{
  "family": "django-eda-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::your-account-id:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "django-eda-web",
      "image": "your-account-id.dkr.ecr.us-east-1.amazonaws.com/django-eda-app:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DEBUG",
          "value": "False"
        }
      ],
      "secrets": [
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account-id:secret:django-secret-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/django-eda",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Step 3: Create ECS Cluster and Service

```bash
# Create cluster
aws ecs create-cluster --cluster-name django-eda-cluster

# Register task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create service with load balancer
aws ecs create-service \
  --cluster django-eda-cluster \
  --service-name django-eda-service \
  --task-definition django-eda-task \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx],securityGroups=[sg-xxxxx],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:region:account-id:targetgroup/django-eda-tg/xxx,containerName=django-eda-web,containerPort=8000"
```

---

## 🌟 Option 4: AWS Lightsail (Simplest & Cheapest)

### Step 1: Create Lightsail Instance

```bash
# Create Lightsail instance via CLI
aws lightsail create-instances \
  --instance-names django-eda-server \
  --availability-zone us-east-1a \
  --blueprint-id ubuntu_22_04 \
  --bundle-id medium_2_0

# Open ports
aws lightsail open-instance-public-ports \
  --instance-name django-eda-server \
  --port-info fromPort=80,toPort=80,protocol=TCP

aws lightsail open-instance-public-ports \
  --instance-name django-eda-server \
  --port-info fromPort=443,toPort=443,protocol=TCP
```

### Step 2: Deploy Application

```bash
# Get SSH key
aws lightsail download-default-key-pair --output text > lightsail-key.pem
chmod 400 lightsail-key.pem

# SSH into instance
ssh -i lightsail-key.pem ubuntu@your-lightsail-ip

# Follow EC2 deployment steps (install Docker, deploy app)
```

---

## 🗄️ Database Setup

### Option A: Amazon RDS (Recommended for Production)

```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier django-eda-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password SecurePassword123! \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxx \
  --db-name eda_database \
  --backup-retention-period 7

# Get endpoint
aws rds describe-db-instances --db-instance-identifier django-eda-db --query 'DBInstances[0].Endpoint.Address'

# Update environment variable
export DATABASE_URL="postgresql://admin:SecurePassword123!@your-rds-endpoint:5432/eda_database"
```

### Option B: Amazon Aurora Serverless (Auto-scaling)

```bash
# Create Aurora Serverless cluster
aws rds create-db-cluster \
  --db-cluster-identifier django-eda-aurora \
  --engine aurora-postgresql \
  --engine-mode serverless \
  --master-username admin \
  --master-user-password SecurePassword123! \
  --scaling-configuration MinCapacity=2,MaxCapacity=4,AutoPause=true,SecondsUntilAutoPause=300
```

---

## 🔴 Redis Cache Setup

### Option A: Amazon ElastiCache

```bash
# Create Redis cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id django-eda-redis \
  --engine redis \
  --cache-node-type cache.t3.micro \
  --num-cache-nodes 1 \
  --security-group-ids sg-xxxxx

# Get endpoint
aws elasticache describe-cache-clusters \
  --cache-cluster-id django-eda-redis \
  --show-cache-node-info \
  --query 'CacheClusters[0].CacheNodes[0].Endpoint.Address'

# Update environment variable
export REDIS_URL="redis://your-elasticache-endpoint:6379/0"
```

---

## 📦 Static Files & Media Storage

### Using Amazon S3

```bash
# Create S3 bucket
aws s3 mb s3://django-eda-static-files

# Enable public access for static files
aws s3api put-bucket-policy --bucket django-eda-static-files --policy '{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::django-eda-static-files/*"
  }]
}'

# Install django-storages
pip install django-storages boto3

# Update settings.py
# Add to INSTALLED_APPS: 'storages'
# Configure S3 (see code below)
```

Add to `settings.py`:

```python
# S3 Storage Configuration
if not DEBUG:
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = 'django-eda-static-files'
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

    # Static files
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

    # Media files
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

---

## 🔒 Security Configuration

### 1. AWS Secrets Manager

```bash
# Store secret key
aws secretsmanager create-secret \
  --name django-eda/SECRET_KEY \
  --secret-string "your-super-secret-key"

# Store database password
aws secretsmanager create-secret \
  --name django-eda/DB_PASSWORD \
  --secret-string "your-database-password"

# Retrieve in application
# Install: pip install boto3
```

### 2. IAM Roles and Policies

```bash
# Create IAM role for EC2/ECS
aws iam create-role \
  --role-name DjangoEdaRole \
  --assume-role-policy-document file://trust-policy.json

# Attach policies
aws iam attach-role-policy \
  --role-name DjangoEdaRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-role-policy \
  --role-name DjangoEdaRole \
  --policy-arn arn:aws:iam::aws:policy/SecretsManagerReadWrite
```

### 3. WAF (Web Application Firewall)

```bash
# Create WAF WebACL
aws wafv2 create-web-acl \
  --name django-eda-waf \
  --scope REGIONAL \
  --default-action Allow={} \
  --rules file://waf-rules.json
```

---

## 📊 Monitoring & Logging

### CloudWatch Setup

```bash
# Create CloudWatch log group
aws logs create-log-group --log-group-name /aws/django-eda

# Create metric filters
aws logs put-metric-filter \
  --log-group-name /aws/django-eda \
  --filter-name ErrorCount \
  --filter-pattern "[time, request_id, level = ERROR*, ...]" \
  --metric-transformations \
    metricName=ErrorCount,metricNamespace=DjangoEDA,metricValue=1
```

### CloudWatch Alarms

```bash
# Create alarm for high error rate
aws cloudwatch put-metric-alarm \
  --alarm-name django-eda-high-errors \
  --alarm-description "Alert when error rate is high" \
  --metric-name ErrorCount \
  --namespace DjangoEDA \
  --statistic Sum \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1
```

---

## 🚀 Auto-Scaling Configuration

### Application Load Balancer

```bash
# Create load balancer
aws elbv2 create-load-balancer \
  --name django-eda-lb \
  --subnets subnet-xxxxx subnet-yyyyy \
  --security-groups sg-xxxxx

# Create target group
aws elbv2 create-target-group \
  --name django-eda-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-xxxxx \
  --health-check-path /health/simple/
```

### Auto Scaling Group (for EC2)

```bash
# Create launch template
aws ec2 create-launch-template \
  --launch-template-name django-eda-template \
  --version-description v1 \
  --launch-template-data file://launch-template.json

# Create auto-scaling group
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name django-eda-asg \
  --launch-template LaunchTemplateName=django-eda-template \
  --min-size 1 \
  --max-size 4 \
  --desired-capacity 2 \
  --target-group-arns arn:aws:elasticloadbalancing:region:account-id:targetgroup/django-eda-tg/xxx
```

---

## 💰 Cost Optimization

### Recommended Configuration by Budget

#### Budget: $10-20/month
- **Compute**: Lightsail ($10) or t3.micro EC2 spot instance
- **Database**: SQLite (local) or RDS db.t3.micro with reserved pricing
- **Storage**: S3 Standard (first 50GB free tier)

#### Budget: $30-50/month
- **Compute**: t3.small EC2 with auto-scaling (1-2 instances)
- **Database**: RDS db.t3.small PostgreSQL
- **Cache**: ElastiCache t3.micro
- **Load Balancer**: Application Load Balancer

#### Budget: $100+/month
- **Compute**: ECS Fargate or t3.medium+ instances
- **Database**: Aurora Serverless or RDS db.t3.medium+
- **Cache**: ElastiCache with Multi-AZ
- **CDN**: CloudFront
- **Storage**: S3 with Intelligent-Tiering

---

## 🔧 Deployment Automation

### GitHub Actions CI/CD

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to AWS

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1

    - name: Deploy to Elastic Beanstalk
      run: |
        pip install awsebcli
        eb deploy django-eda-prod
```

---

## 📞 Troubleshooting

### Common AWS Issues

1. **Permission Denied Errors**
   - Check IAM roles and policies
   - Ensure security groups allow required ports

2. **Database Connection Issues**
   - Verify security group inbound rules
   - Check RDS endpoint and credentials
   - Ensure VPC configuration is correct

3. **Static Files Not Loading**
   - Run `python manage.py collectstatic`
   - Check S3 bucket policy for public read access
   - Verify STATIC_URL and MEDIA_URL settings

4. **Memory Issues**
   - Increase instance size
   - Enable swap file on EC2
   - Optimize DataFrame processing

---

## 🎯 Post-Deployment Checklist

- [ ] Set up SSL certificate (Let's Encrypt or AWS Certificate Manager)
- [ ] Configure custom domain name (Route 53)
- [ ] Set up automated backups (RDS snapshots, S3 versioning)
- [ ] Enable CloudWatch monitoring and alarms
- [ ] Configure auto-scaling policies
- [ ] Set up log aggregation and analysis
- [ ] Implement WAF rules for security
- [ ] Test disaster recovery procedures
- [ ] Configure CDN (CloudFront) for static assets
- [ ] Set up automated deployment pipeline

---

## 📚 Additional Resources

- [AWS Elastic Beanstalk Documentation](https://docs.aws.amazon.com/elasticbeanstalk/)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Django on AWS Best Practices](https://docs.djangoproject.com/en/stable/howto/deployment/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

---

**Need Help?** Contact: thriloke96@gmail.com
