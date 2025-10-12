#!/bin/bash

# =============================================================================
# AWS EC2 Deployment Script for Django EDA Application
# =============================================================================
# This script sets up a Django application on an EC2 instance
# Run this script ON the EC2 instance after SSH connection
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Django EDA App - EC2 Setup${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Update system
echo -e "${YELLOW}Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y
echo -e "${GREEN}✓ System updated${NC}"

# Install Docker
echo -e "${YELLOW}Installing Docker...${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo -e "${GREEN}✓ Docker installed${NC}"
else
    echo -e "${GREEN}✓ Docker already installed${NC}"
fi

# Install Docker Compose
echo -e "${YELLOW}Installing Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✓ Docker Compose installed${NC}"
else
    echo -e "${GREEN}✓ Docker Compose already installed${NC}"
fi

# Install Git
echo -e "${YELLOW}Installing Git...${NC}"
sudo apt install -y git
echo -e "${GREEN}✓ Git installed${NC}"

# Install Nginx
echo -e "${YELLOW}Installing Nginx...${NC}"
sudo apt install -y nginx
echo -e "${GREEN}✓ Nginx installed${NC}"

# Install Certbot for SSL
echo -e "${YELLOW}Installing Certbot for SSL...${NC}"
sudo apt install -y certbot python3-certbot-nginx
echo -e "${GREEN}✓ Certbot installed${NC}"

# Create application directory
echo -e "${YELLOW}Setting up application directory...${NC}"
sudo mkdir -p /var/www/django-eda
sudo chown -R $USER:$USER /var/www/django-eda
cd /var/www/django-eda

# Clone or upload application
echo -e "${YELLOW}Application Setup${NC}"
echo "Please upload your application files to /var/www/django-eda"
echo "or clone from git repository"
read -p "Enter git repository URL (or press Enter to skip): " GIT_REPO

if [ ! -z "$GIT_REPO" ]; then
    git clone $GIT_REPO .
    echo -e "${GREEN}✓ Application cloned${NC}"
fi

# Create .env file
echo -e "${YELLOW}Creating environment configuration...${NC}"
if [ ! -f .env ]; then
    cat > .env << 'EOF'
SECRET_KEY=your-super-secret-key-change-this
DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-ec2-ip
DATABASE_URL=postgresql://user:password@localhost:5432/eda_db
REDIS_URL=redis://localhost:6379/0
EOF
    echo -e "${YELLOW}⚠ Please edit /var/www/django-eda/.env with your values${NC}"
fi

# Create docker-compose override for production
echo -e "${YELLOW}Creating Docker Compose configuration...${NC}"
if [ -f docker-compose.prod.yml ]; then
    ln -sf docker-compose.prod.yml docker-compose.yml
fi

# Build and start application
echo -e "${YELLOW}Building and starting application...${NC}"
docker-compose up -d --build
echo -e "${GREEN}✓ Application started${NC}"

# Configure Nginx
echo -e "${YELLOW}Configuring Nginx...${NC}"
sudo tee /etc/nginx/sites-available/django-eda > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;
    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /var/www/django-eda/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/django-eda/media/;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/django-eda /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
echo -e "${GREEN}✓ Nginx configured${NC}"

# Get EC2 public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}EC2 Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Application URL: ${GREEN}http://$PUBLIC_IP${NC}"
echo -e "Health Check: ${GREEN}http://$PUBLIC_IP/health/${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Edit /var/www/django-eda/.env with your configuration"
echo "2. Restart: cd /var/www/django-eda && docker-compose restart"
echo "3. Set up SSL: sudo certbot --nginx -d your-domain.com"
echo "4. Check logs: docker-compose logs -f"
echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo "  View logs: docker-compose logs -f"
echo "  Restart: docker-compose restart"
echo "  Stop: docker-compose down"
echo "  Update: git pull && docker-compose up -d --build"
echo ""
