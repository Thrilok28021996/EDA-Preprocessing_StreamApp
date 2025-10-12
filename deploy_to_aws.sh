#!/bin/bash

# =============================================================================
# AWS Deployment Script for Django EDA Application
# =============================================================================
# This script automates deployment to AWS Elastic Beanstalk
# Usage: ./deploy_to_aws.sh [environment]
# Example: ./deploy_to_aws.sh production
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="django-eda-app"
REGION="${AWS_REGION:-us-east-1}"
ENVIRONMENT="${1:-production}"
INSTANCE_TYPE="${INSTANCE_TYPE:-t3.small}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Django EDA App - AWS Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command_exists aws; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    echo "Install: https://aws.amazon.com/cli/"
    exit 1
fi

if ! command_exists eb; then
    echo -e "${RED}Error: EB CLI is not installed${NC}"
    echo "Install: pip install awsebcli"
    exit 1
fi

if ! command_exists python; then
    echo -e "${RED}Error: Python is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All prerequisites met${NC}"
echo ""

# Check AWS credentials
echo -e "${YELLOW}Checking AWS credentials...${NC}"
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo -e "${RED}Error: AWS credentials not configured${NC}"
    echo "Run: aws configure"
    exit 1
fi
echo -e "${GREEN}✓ AWS credentials configured${NC}"
echo ""

# Create environment file if it doesn't exist
if [ ! -f .env.production ]; then
    echo -e "${YELLOW}Creating .env.production file...${NC}"
    cat > .env.production << 'EOF'
SECRET_KEY=CHANGE_THIS_TO_A_RANDOM_SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=.elasticbeanstalk.com,.amazonaws.com
DATABASE_URL=
REDIS_URL=
EOF
    echo -e "${YELLOW}⚠ Please edit .env.production with your actual values${NC}"
    read -p "Press enter to continue after editing .env.production..."
fi

# Initialize EB if not already initialized
if [ ! -d .elasticbeanstalk ]; then
    echo -e "${YELLOW}Initializing Elastic Beanstalk...${NC}"
    eb init -p python-3.11 $APP_NAME --region $REGION
    echo -e "${GREEN}✓ EB initialized${NC}"
fi

# Check if environment exists
ENV_EXISTS=$(eb list 2>/dev/null | grep -c "$APP_NAME-$ENVIRONMENT" || true)

if [ "$ENV_EXISTS" -eq 0 ]; then
    echo -e "${YELLOW}Creating new EB environment: $APP_NAME-$ENVIRONMENT${NC}"
    echo "This may take 5-10 minutes..."

    # Prompt for database setup
    read -p "Do you want to create RDS PostgreSQL database? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        eb create $APP_NAME-$ENVIRONMENT \
            --instance-type $INSTANCE_TYPE \
            --database.engine postgres \
            --database.instance db.t3.micro \
            --database.username ebroot \
            --scale 1 \
            --envvars $(cat .env.production | grep -v '^#' | grep -v '^$' | tr '\n' ',' | sed 's/,$//')
    else
        eb create $APP_NAME-$ENVIRONMENT \
            --instance-type $INSTANCE_TYPE \
            --scale 1 \
            --envvars $(cat .env.production | grep -v '^#' | grep -v '^$' | tr '\n' ',' | sed 's/,$//')
    fi

    echo -e "${GREEN}✓ Environment created${NC}"
else
    echo -e "${GREEN}Environment $APP_NAME-$ENVIRONMENT already exists${NC}"
fi

# Set environment variables
echo -e "${YELLOW}Setting environment variables...${NC}"
eb setenv $(cat .env.production | grep -v '^#' | grep -v '^$' | xargs)
echo -e "${GREEN}✓ Environment variables set${NC}"

# Deploy application
echo -e "${YELLOW}Deploying application...${NC}"
eb deploy $APP_NAME-$ENVIRONMENT

# Check deployment status
echo -e "${YELLOW}Checking deployment status...${NC}"
eb status $APP_NAME-$ENVIRONMENT

# Get application URL
APP_URL=$(eb status $APP_NAME-$ENVIRONMENT | grep "CNAME" | awk '{print $2}')

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Application URL: ${GREEN}http://$APP_URL${NC}"
echo -e "Health Check: ${GREEN}http://$APP_URL/health/${NC}"
echo -e "Admin Panel: ${GREEN}http://$APP_URL/admin/${NC}"
echo ""
echo -e "${YELLOW}Default Admin Credentials:${NC}"
echo "  Username: admin"
echo "  Password: ChangeThisPassword123!"
echo ""
echo -e "${RED}⚠ IMPORTANT: Change the admin password immediately!${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Visit $APP_URL and verify the application is running"
echo "2. Change the admin password: $APP_URL/admin/"
echo "3. Set up a custom domain (optional)"
echo "4. Enable HTTPS with AWS Certificate Manager"
echo "5. Monitor logs: eb logs $APP_NAME-$ENVIRONMENT"
echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo "  View logs: eb logs $APP_NAME-$ENVIRONMENT"
echo "  SSH to instance: eb ssh $APP_NAME-$ENVIRONMENT"
echo "  Open in browser: eb open $APP_NAME-$ENVIRONMENT"
echo "  Check status: eb status $APP_NAME-$ENVIRONMENT"
echo "  Terminate: eb terminate $APP_NAME-$ENVIRONMENT"
echo ""
