#!/bin/bash

# DriftGuard Setup Wizard
# Enterprise-grade onboarding experience

set -euo pipefail

# Colors for better UX
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# ASCII Logo
show_logo() {
    echo -e "${BLUE}${BOLD}"
    echo "    ____        _ ____  ____                      __"
    echo "   / __ \\_   __(_) __/ / __ \\__  ______ ________/ /"
    echo "  / / / / | / / / /_  / / / / / / / __ \`/ ___/ __  /"
    echo " / /_/ /| |/ / / __/ / /_/ / /_/ / /_/ / /  / /_/ / "
    echo "/_____/ |___/_/_/    \\____/\\__,_/\\__,_/_/   \\__,_/  "
    echo ""
    echo "           Enterprise Code Analysis Platform"
    echo -e "${NC}"
}

# Progress indicators
show_step() {
    echo -e "${CYAN}${BOLD}[STEP $1/7]${NC} $2"
    echo ""
}

show_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

show_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

show_error() {
    echo -e "${RED}❌ $1${NC}"
}

show_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Validation functions
check_command() {
    if ! command -v "$1" &> /dev/null; then
        return 1
    fi
    return 0
}

validate_port() {
    local port="$1"
    if [[ ! "$port" =~ ^[0-9]+$ ]] || [ "$port" -lt 1 ] || [ "$port" -gt 65535 ]; then
        return 1
    fi
    return 0
}

validate_app_id() {
    local app_id="$1"
    if [[ ! "$app_id" =~ ^[0-9]+$ ]]; then
        return 1
    fi
    return 0
}

# Main setup functions
welcome() {
    clear
    show_logo
    echo -e "${BOLD}Welcome to DriftGuard Setup Wizard!${NC}"
    echo ""
    echo "This wizard will guide you through setting up DriftGuard for your"
    echo "GitHub organization with enterprise-grade security and monitoring."
    echo ""
    echo -e "${YELLOW}⏱️  Estimated time: 5-10 minutes${NC}"
    echo ""
    read -p "Press Enter to continue..."
    echo ""
}

check_prerequisites() {
    show_step 1 "Checking Prerequisites"
    
    local errors=0
    
    # Check Node.js
    if check_command "node"; then
        local node_version=$(node --version)
        show_success "Node.js found: $node_version"
    else
        show_error "Node.js not found. Please install Node.js 18+ from https://nodejs.org"
        errors=$((errors + 1))
    fi
    
    # Check npm
    if check_command "npm"; then
        local npm_version=$(npm --version)
        show_success "npm found: v$npm_version"
    else
        show_error "npm not found. Please install npm"
        errors=$((errors + 1))
    fi
    
    # Check Docker (optional)
    if check_command "docker"; then
        local docker_version=$(docker --version | cut -d' ' -f3 | tr -d ',')
        show_success "Docker found: $docker_version (optional)"
    else
        show_warning "Docker not found (optional for containerized deployment)"
    fi
    
    # Check Git
    if check_command "git"; then
        show_success "Git found"
    else
        show_error "Git not found. Please install Git"
        errors=$((errors + 1))
    fi
    
    if [ $errors -gt 0 ]; then
        echo ""
        show_error "Please install missing prerequisites and run the wizard again."
        exit 1
    fi
    
    echo ""
    show_success "All prerequisites met!"
    echo ""
}

configure_github_app() {
    show_step 2 "GitHub App Configuration"
    
    echo "You need to create a GitHub App for DriftGuard to access your repositories."
    echo ""
    echo -e "${BOLD}Option 1: GitHub Marketplace (Recommended)${NC}"
    echo "• Visit: https://github.com/marketplace/driftguard"
    echo "• Click 'Install' and follow the prompts"
    echo ""
    echo -e "${BOLD}Option 2: Manual Creation${NC}"
    echo "• Visit: https://github.com/settings/apps"
    echo "• Click 'New GitHub App'"
    echo "• Use manifest from: app/manifest.example.json"
    echo ""
    
    read -p "Have you created/installed the GitHub App? (y/n): " app_created
    
    if [[ ! "$app_created" =~ ^[Yy]$ ]]; then
        show_warning "Please create the GitHub App first and re-run this wizard."
        exit 0
    fi
    
    echo ""
    echo "Great! Now we need your app credentials:"
    echo ""
    
    # App ID
    while true; do
        read -p "GitHub App ID: " APP_ID
        if validate_app_id "$APP_ID"; then
            break
        else
            show_error "Invalid App ID. Please enter a numeric ID."
        fi
    done
    
    # Private Key
    echo ""
    echo "Private Key (paste the entire key including headers):"
    echo "-----BEGIN PRIVATE KEY-----"
    echo "(paste here and press Ctrl+D when done)"
    PRIVATE_KEY=$(cat)
    
    # Webhook Secret
    echo ""
    read -p "Webhook Secret: " WEBHOOK_SECRET
    
    echo ""
    show_success "GitHub App configuration collected!"
    echo ""
}

configure_environment() {
    show_step 3 "Environment Configuration"
    
    # Port
    while true; do
        read -p "Port to run DriftGuard on (default: 3000): " PORT
        PORT=${PORT:-3000}
        if validate_port "$PORT"; then
            break
        else
            show_error "Invalid port. Please enter a port between 1-65535."
        fi
    done
    
    # Environment
    echo ""
    echo "Select environment:"
    echo "1) Development"
    echo "2) Production"
    read -p "Choice (1-2, default: 1): " env_choice
    env_choice=${env_choice:-1}
    
    if [ "$env_choice" = "2" ]; then
        NODE_ENV="production"
    else
        NODE_ENV="development"
    fi
    
    echo ""
    show_success "Environment configuration set!"
    echo ""
}

create_env_file() {
    show_step 4 "Creating Environment File"
    
    cat > .env << EOF
# DriftGuard Configuration
# Generated by setup wizard on $(date)

# GitHub App Configuration
APP_ID=$APP_ID
WEBHOOK_SECRET=$WEBHOOK_SECRET

# Server Configuration
PORT=$PORT
NODE_ENV=$NODE_ENV

# Security
SESSION_SECRET=$(openssl rand -hex 32)

# Monitoring (optional)
# PROMETHEUS_ENABLED=true
# LOG_LEVEL=info

# Database (if using external)
# DATABASE_URL=postgresql://user:pass@host:port/db
EOF

    echo "PRIVATE_KEY=\"$PRIVATE_KEY\"" >> .env
    
    show_success "Environment file created: .env"
    show_info "🔒 Keep this file secure and never commit it to version control!"
    echo ""
}

install_dependencies() {
    show_step 5 "Installing Dependencies"
    
    echo "Installing Node.js dependencies..."
    if npm ci --silent; then
        show_success "Dependencies installed successfully"
    else
        show_error "Failed to install dependencies"
        exit 1
    fi
    
    echo ""
    echo "Building application..."
    if npm run build --silent; then
        show_success "Application built successfully"
    else
        show_error "Failed to build application"
        exit 1
    fi
    
    echo ""
}

validate_setup() {
    show_step 6 "Validating Setup"
    
    echo "Starting DriftGuard for validation..."
    
    # Start app in background
    timeout 30 npm start &
    local pid=$!
    
    # Wait for app to start
    sleep 5
    
    # Test health endpoint
    if curl -s http://localhost:$PORT/health > /dev/null; then
        show_success "Health check passed"
    else
        show_error "Health check failed"
        kill $pid 2>/dev/null || true
        exit 1
    fi
    
    # Test readiness
    if curl -s http://localhost:$PORT/readyz > /dev/null; then
        show_success "Readiness check passed"
    else
        show_error "Readiness check failed"
        kill $pid 2>/dev/null || true
        exit 1
    fi
    
    # Stop test instance
    kill $pid 2>/dev/null || true
    sleep 2
    
    show_success "All validation checks passed!"
    echo ""
}

setup_complete() {
    show_step 7 "Setup Complete!"
    
    show_logo
    
    echo -e "${GREEN}${BOLD}🎉 DriftGuard is ready!${NC}"
    echo ""
    echo -e "${BOLD}Next steps:${NC}"
    echo ""
    echo "1. Start DriftGuard:"
    echo -e "   ${CYAN}npm start${NC}"
    echo ""
    echo "2. Add workflow to your repositories:"
    echo -e "   ${CYAN}cp .github/workflows/driftguard-gate.yml <your-repo>/.github/workflows/${NC}"
    echo ""
    echo "3. Monitor your application:"
    echo -e "   ${CYAN}Health: http://localhost:$PORT/health${NC}"
    echo -e "   ${CYAN}Metrics: http://localhost:$PORT/metrics${NC}"
    echo ""
    echo -e "${BOLD}Documentation:${NC}"
    echo "• Installation: docs/installation.md"
    echo "• Configuration: docs/configuration.md"
    echo "• Troubleshooting: docs/troubleshooting.md"
    echo ""
    echo -e "${BOLD}Support:${NC}"
    echo "• Issues: https://github.com/mattjutt1/DriftGuard-Checks/issues"
    echo "• Discussions: https://github.com/mattjutt1/DriftGuard-Checks/discussions"
    echo ""
    echo -e "${GREEN}Happy analyzing! 🛡️${NC}"
}

# Main execution
main() {
    welcome
    check_prerequisites
    configure_github_app
    configure_environment
    create_env_file
    install_dependencies
    validate_setup
    setup_complete
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi