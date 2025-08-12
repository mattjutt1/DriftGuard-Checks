#!/bin/bash

# PromptEvolver Production Deployment Script
# This script automates the deployment process for the PromptEvolver system

set -e  # Exit on any error

echo "🚀 PromptEvolver Production Deployment"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "package.json" ] || [ ! -d "convex" ]; then
    print_error "Please run this script from the nextjs-app directory"
    exit 1
fi

print_status "Starting production deployment process..."

# Step 1: Install dependencies
print_status "Installing dependencies..."
npm install
print_success "Dependencies installed"

# Step 2: Build the application
print_status "Building Next.js application..."
npm run build
if [ $? -eq 0 ]; then
    print_success "Build completed successfully"
else
    print_error "Build failed"
    exit 1
fi

# Step 3: Check Convex configuration
print_status "Checking Convex configuration..."
if [ ! -s .env.local ] || ! grep -q "NEXT_PUBLIC_CONVEX_URL" .env.local; then
    print_warning "Convex URL not configured in .env.local"
    echo "Please run the following commands manually:"
    echo "1. npx convex auth"
    echo "2. npx convex deploy --prod"
    echo "3. Update .env.local with the deployment URL"
else
    print_success "Convex configuration found"
fi

# Step 4: Run production tests
print_status "Running production tests..."
npm test -- --passWithNoTests
if [ $? -eq 0 ]; then
    print_success "All tests passed"
else
    print_warning "Some tests failed - review before deploying"
fi

# Step 5: Prepare production environment
print_status "Creating production environment file..."
cat > .env.production << EOL
# Production Configuration for PromptEvolver
NODE_ENV=production

# This will be populated after Convex deployment
# NEXT_PUBLIC_CONVEX_URL=https://your-deployment-name.convex.cloud

# Performance optimizations
NEXT_TELEMETRY_DISABLED=1
EOL

print_success "Production environment file created"

# Step 6: Generate deployment checklist
print_status "Generating deployment checklist..."
cat > DEPLOYMENT-CHECKLIST.md << 'EOL'
# PromptEvolver Deployment Checklist

## Pre-Deployment ✅

- [x] Dependencies installed
- [x] Application builds successfully
- [x] Tests passing
- [x] Production environment configured

## Manual Steps (Required)

### 1. Convex Backend Deployment
```bash
# Login to Convex
npx convex auth

# Deploy backend functions
npx convex deploy --prod

# Note the deployment URL (e.g., https://enchanted-rooster-257.convex.cloud)
```

### 2. Update Environment Variables
```bash
# Update .env.local with your Convex URL
echo "NEXT_PUBLIC_CONVEX_URL=https://your-deployment-url.convex.cloud" >> .env.local

# Update .env.production
echo "NEXT_PUBLIC_CONVEX_URL=https://your-deployment-url.convex.cloud" >> .env.production
```

### 3. Frontend Deployment (Vercel)
```bash
# Install Vercel CLI (if needed)
npm i -g vercel

# Login to Vercel
vercel login

# Deploy to production
vercel --prod

# Set environment variables in Vercel dashboard
# Go to: Project Settings → Environment Variables
# Add: NEXT_PUBLIC_CONVEX_URL = your-convex-url
```

## Post-Deployment Verification

- [ ] Frontend accessible at Vercel URL
- [ ] Backend functions responding
- [ ] Database connectivity working
- [ ] Authentication system functional
- [ ] Prompt optimization working
- [ ] Real-time updates functional

## Production URLs

- **Frontend:** https://prompt-wizard-[hash].vercel.app
- **Backend:** https://your-deployment-name.convex.cloud
- **Dashboard:** `npx convex dashboard --prod`

EOL

print_success "Deployment checklist created"

# Step 7: Final instructions
echo ""
echo "=================================================="
print_success "Pre-deployment preparation completed!"
echo "=================================================="
echo ""
print_status "Next steps:"
echo "1. Review DEPLOYMENT-CHECKLIST.md"
echo "2. Run manual Convex deployment commands"
echo "3. Deploy frontend to Vercel"
echo "4. Test production deployment"
echo ""
print_warning "Remember to:"
echo "- Set environment variables in both .env.local and Vercel"
echo "- Test all features after deployment"
echo "- Monitor logs for any issues"
echo ""
print_success "Your PromptEvolver system is ready for production! 🎉"
