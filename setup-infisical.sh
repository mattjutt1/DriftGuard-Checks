#!/bin/bash
# Infisical Setup Script for PromptEvolver Development Environment

set -e

echo "🔐 Setting up Infisical for PromptEvolver Development..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Function to generate secure random key
generate_key() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-32
}

# Create .env.infisical from example if it doesn't exist
if [ ! -f ".env.infisical" ]; then
    echo -e "${YELLOW}📋 Creating .env.infisical configuration file...${NC}"
    
    # Copy example file
    cp .env.infisical.example .env.infisical
    
    # Generate secure keys
    ENCRYPTION_KEY=$(generate_key)
    AUTH_SECRET=$(generate_key)
    JWT_SIGNUP_SECRET=$(generate_key)
    JWT_REFRESH_SECRET=$(generate_key)
    JWT_AUTH_SECRET=$(generate_key)
    DB_PASSWORD=$(generate_key)
    
    # Replace placeholder values
    sed -i "s/your_32_char_encryption_key_here_change_this/${ENCRYPTION_KEY}/" .env.infisical
    sed -i "s/your_auth_secret_here_change_this_value/${AUTH_SECRET}/" .env.infisical
    sed -i "s/your_jwt_signup_secret_change_this/${JWT_SIGNUP_SECRET}/" .env.infisical
    sed -i "s/your_jwt_refresh_secret_change_this/${JWT_REFRESH_SECRET}/" .env.infisical
    sed -i "s/your_jwt_auth_secret_change_this/${JWT_AUTH_SECRET}/" .env.infisical
    sed -i "s/change_this_password_for_production/${DB_PASSWORD}/" .env.infisical
    
    echo -e "${GREEN}✅ Generated secure configuration in .env.infisical${NC}"
else
    echo -e "${BLUE}ℹ️  Using existing .env.infisical configuration${NC}"
fi

# Create data directory
mkdir -p infisical-data
echo -e "${GREEN}✅ Created data directory${NC}"

# Update .gitignore to exclude sensitive files
if ! grep -q "# Infisical" .gitignore; then
    echo "" >> .gitignore
    echo "# Infisical Secret Management" >> .gitignore
    echo ".env.infisical" >> .gitignore
    echo "infisical-data/" >> .gitignore
    echo "# End Infisical" >> .gitignore
    echo -e "${GREEN}✅ Updated .gitignore${NC}"
fi

# Start Infisical services
echo -e "${BLUE}🚀 Starting Infisical services...${NC}"
docker-compose --env-file .env.infisical -f docker-compose.infisical.yml up -d

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 10

# Check if services are running
if docker-compose --env-file .env.infisical -f docker-compose.infisical.yml ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Infisical services are running!${NC}"
    echo ""
    echo -e "${BLUE}📋 Next Steps:${NC}"
    echo -e "1. Open your browser and go to: ${YELLOW}http://localhost:8080${NC}"
    echo -e "2. Create your admin account"
    echo -e "3. Download the Emergency Kit PDF (IMPORTANT!)"
    echo -e "4. Create a project for PromptEvolver"
    echo -e "5. Install Infisical CLI: ${YELLOW}npm install -g @infisical/cli${NC}"
    echo ""
    echo -e "${BLUE}🔧 Management Commands:${NC}"
    echo -e "Stop services:  ${YELLOW}./infisical-manage.sh stop${NC}"
    echo -e "Start services: ${YELLOW}./infisical-manage.sh start${NC}"
    echo -e "View logs:      ${YELLOW}./infisical-manage.sh logs${NC}"
    echo -e "Status:         ${YELLOW}./infisical-manage.sh status${NC}"
else
    echo -e "${RED}❌ Some services failed to start. Check logs:${NC}"
    docker-compose --env-file .env.infisical -f docker-compose.infisical.yml logs
    exit 1
fi