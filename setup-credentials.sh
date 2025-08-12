#!/bin/bash

# GitHub App Credentials Setup Helper
# This script helps you configure your DriftGuard app credentials

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║         DriftGuard GitHub App Credentials Setup            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Function to prompt for input with default
prompt_with_default() {
    local prompt="$1"
    local default="$2"
    local var_name="$3"
    
    if [ -n "$default" ]; then
        echo -e "${CYAN}$prompt ${YELLOW}[$default]${NC}: "
    else
        echo -e "${CYAN}$prompt${NC}: "
    fi
    
    read -r input
    
    if [ -z "$input" ] && [ -n "$default" ]; then
        eval "$var_name='$default'"
    else
        eval "$var_name='$input'"
    fi
}

# Check if .env exists
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file already exists. Creating backup...${NC}"
    cp .env .env.backup.$(date +%Y%m%d-%H%M%S)
    echo -e "${GREEN}✅ Backup saved${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 1: GitHub App Information${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📍 Go to: https://github.com/settings/apps"
echo "📍 Click on your DriftGuard app"
echo ""

# Get App ID
echo -e "${GREEN}From the General tab (at the top of the page):${NC}"
prompt_with_default "Enter your App ID (numeric)" "" "APP_ID"

# Get Client ID
echo ""
echo -e "${GREEN}From the OAuth credentials section:${NC}"
prompt_with_default "Enter your Client ID (starts with Iv1.)" "" "CLIENT_ID"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 2: Generate New Secrets${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Client Secret
echo -e "${YELLOW}⚠️  IMPORTANT: You need to generate a NEW client secret${NC}"
echo "📍 In GitHub App settings, find 'Client secrets' section"
echo "📍 Click 'Generate a new client secret'"
echo "📍 Copy the generated secret immediately (you won't see it again!)"
echo ""
prompt_with_default "Enter your Client Secret" "" "CLIENT_SECRET"

# Webhook Secret
echo ""
echo -e "${GREEN}For the Webhook Secret, you have two options:${NC}"
echo "1. Use our generated secure secret (recommended)"
echo "2. Enter your own secret"
echo ""

GENERATED_SECRET="038e746ab2bc61a08f54ab203e72423f6a675c799a5855d2184bb49f1c480702"
echo -e "Generated secret: ${YELLOW}$GENERATED_SECRET${NC}"
echo ""
prompt_with_default "Press Enter to use generated secret, or type your own" "$GENERATED_SECRET" "WEBHOOK_SECRET"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 3: Private Key${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}⚠️  CRITICAL: You must generate a NEW private key${NC}"
echo "📍 In GitHub App settings, find 'Private keys' section"
echo "📍 Click 'Generate a private key'"
echo "📍 This will download a .pem file"
echo ""
echo "Have you downloaded the new private key? (y/n)"
read -r downloaded

if [ "$downloaded" = "y" ] || [ "$downloaded" = "Y" ]; then
    echo ""
    echo "Great! Now let's set it up:"
    echo ""
    
    # Check for downloaded key
    DOWNLOAD_DIR="$HOME/Downloads"
    PEM_FILES=$(find "$DOWNLOAD_DIR" -name "*.private-key.pem" -mmin -5 2>/dev/null | head -1)
    
    if [ -n "$PEM_FILES" ]; then
        echo -e "${GREEN}✅ Found recently downloaded private key:${NC}"
        echo "   $PEM_FILES"
        echo ""
        echo "Move this file to the app directory? (y/n)"
        read -r move_key
        
        if [ "$move_key" = "y" ] || [ "$move_key" = "Y" ]; then
            cp "$PEM_FILES" ./private-key.pem
            chmod 600 ./private-key.pem
            echo -e "${GREEN}✅ Private key saved and secured${NC}"
            PRIVATE_KEY_PATH="./private-key.pem"
        fi
    else
        echo "Please specify the path to your downloaded private key file:"
        read -r key_path
        if [ -f "$key_path" ]; then
            cp "$key_path" ./private-key.pem
            chmod 600 ./private-key.pem
            echo -e "${GREEN}✅ Private key saved and secured${NC}"
            PRIVATE_KEY_PATH="./private-key.pem"
        else
            echo -e "${YELLOW}⚠️  File not found. You'll need to manually copy it later.${NC}"
            PRIVATE_KEY_PATH="./private-key.pem"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  Remember to download and save the private key before starting the app!${NC}"
    PRIVATE_KEY_PATH="./private-key.pem"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 4: Additional Configuration${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

prompt_with_default "Environment (development/production)" "development" "NODE_ENV"
prompt_with_default "Port" "3000" "PORT"
prompt_with_default "Redis URL" "redis://localhost:6379" "REDIS_URL"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Creating .env file...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Create .env file
cat > .env << EOF
# DriftGuard Checks App Configuration
# Generated on $(date)

# GitHub App Configuration
GITHUB_APP_ID=$APP_ID
GITHUB_CLIENT_ID=$CLIENT_ID
GITHUB_CLIENT_SECRET=$CLIENT_SECRET
WEBHOOK_SECRET=$WEBHOOK_SECRET

# Private Key Path
PRIVATE_KEY_PATH=$PRIVATE_KEY_PATH

# Server Configuration
NODE_ENV=$NODE_ENV
PORT=$PORT
LOG_LEVEL=info

# Redis Configuration
REDIS_URL=$REDIS_URL

# Security Features (All enabled for maximum security)
ENABLE_WEBHOOK_VALIDATION=true
ENABLE_RATE_LIMITING=true
ENABLE_IP_WHITELIST=false
ENABLE_REPLAY_PROTECTION=true
ENABLE_ASYNC=true

# Rate Limiting
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX_REQUESTS=100

# Process Limits
MAX_MEMORY_MB=512
MAX_CPU_PERCENT=80
EOF

echo -e "${GREEN}✅ .env file created successfully!${NC}"

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Step 5: Update GitHub Webhook Settings${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📍 Go back to your GitHub App settings"
echo "📍 Click on 'Webhook' in the left sidebar"
echo ""
echo -e "${CYAN}Set these values:${NC}"
echo ""
echo -e "Webhook URL: ${YELLOW}https://your-domain.com/api/github/webhooks${NC}"
echo "   (For local testing, use ngrok: https://xxxxx.ngrok.io/api/github/webhooks)"
echo ""
echo -e "Webhook secret: ${YELLOW}$WEBHOOK_SECRET${NC}"
echo ""
echo "Select these events:"
echo "  ✅ Check run"
echo "  ✅ Workflow run"
echo ""

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Verify configuration
echo "Would you like to verify your configuration? (y/n)"
read -r verify

if [ "$verify" = "y" ] || [ "$verify" = "Y" ]; then
    echo ""
    echo "Checking configuration..."
    echo ""
    
    # Check each required field
    if [ -n "$APP_ID" ] && [ "$APP_ID" != "" ]; then
        echo -e "${GREEN}✅ App ID configured${NC}"
    else
        echo -e "${YELLOW}⚠️  App ID missing${NC}"
    fi
    
    if [ -n "$CLIENT_ID" ] && [[ "$CLIENT_ID" == Iv1.* ]]; then
        echo -e "${GREEN}✅ Client ID configured correctly${NC}"
    else
        echo -e "${YELLOW}⚠️  Client ID may be incorrect (should start with Iv1.)${NC}"
    fi
    
    if [ -n "$CLIENT_SECRET" ] && [ ${#CLIENT_SECRET} -ge 40 ]; then
        echo -e "${GREEN}✅ Client Secret configured${NC}"
    else
        echo -e "${YELLOW}⚠️  Client Secret may be too short${NC}"
    fi
    
    if [ -n "$WEBHOOK_SECRET" ] && [ ${#WEBHOOK_SECRET} -ge 32 ]; then
        echo -e "${GREEN}✅ Webhook Secret configured${NC}"
    else
        echo -e "${YELLOW}⚠️  Webhook Secret may be too short${NC}"
    fi
    
    if [ -f "./private-key.pem" ]; then
        echo -e "${GREEN}✅ Private key file exists${NC}"
    else
        echo -e "${YELLOW}⚠️  Private key file not found - remember to add it!${NC}"
    fi
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    Setup Complete! 🎉                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Make sure your private key is saved as ./private-key.pem"
echo "2. Update the webhook settings in GitHub"
echo "3. Start the application:"
echo ""
echo "   ./start-with-redis.sh"
echo ""
echo "Or with Docker:"
echo ""
echo "   docker-compose up -d"
echo ""
echo -e "${GREEN}Good luck with your secure DriftGuard app!${NC}"
echo ""