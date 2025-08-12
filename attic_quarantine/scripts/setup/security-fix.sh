#!/bin/bash

# DriftGuard Security Fix Script
# This script implements immediate security fixes for critical vulnerabilities
# Date: August 10, 2025

set -e  # Exit on error

echo "🚨 DriftGuard Security Fix Script 🚨"
echo "===================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "apps/driftguard-checks-app/package.json" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

echo "Step 1: Backing up current configuration..."
mkdir -p security-backup
cp -r apps/driftguard-checks-app/.env* security-backup/ 2>/dev/null || true
cp -r apps/driftguard-checks-app/*.pem security-backup/ 2>/dev/null || true
print_status "Backup created in security-backup/"

echo ""
echo "Step 2: Removing sensitive files from repository..."

# Remove private key if it exists
if [ -f "apps/driftguard-checks-app/private-key.pem" ]; then
    print_warning "Found private-key.pem - removing from repository"
    rm -f apps/driftguard-checks-app/private-key.pem
    git rm --cached apps/driftguard-checks-app/private-key.pem 2>/dev/null || true
fi

# Remove .env files
if [ -f "apps/driftguard-checks-app/.env" ]; then
    print_warning "Found .env file - removing from repository"
    rm -f apps/driftguard-checks-app/.env
    git rm --cached apps/driftguard-checks-app/.env 2>/dev/null || true
fi

print_status "Sensitive files removed"

echo ""
echo "Step 3: Updating .gitignore..."

# Add security entries to .gitignore
cat >> apps/driftguard-checks-app/.gitignore << EOF

# Security - Never commit these
*.pem
*.key
*.cert
.env
.env.*
!.env.example
private-key*
webhook-secret*
credentials/
secrets/
EOF

print_status ".gitignore updated"

echo ""
echo "Step 4: Creating secure environment template..."

cat > apps/driftguard-checks-app/.env.example << EOF
# DriftGuard Configuration Template
# NEVER commit actual values - use environment variables or secret management

# GitHub App Configuration
GITHUB_APP_ID=your_app_id_here
GITHUB_CLIENT_ID=your_client_id_here
GITHUB_CLIENT_SECRET=generate_secure_secret_here
WEBHOOK_SECRET=generate_64_char_random_string_here
PRIVATE_KEY_PATH=/secure/path/to/private-key.pem

# Environment
NODE_ENV=production
PORT=3000

# Security Settings
RATE_LIMIT_WINDOW_MS=60000
RATE_LIMIT_MAX_REQUESTS=100
LOG_LEVEL=error

# Optional: External Services
SENTRY_DSN=your_sentry_dsn_here
EOF

print_status "Created .env.example template"

echo ""
echo "Step 5: Installing security dependencies..."

cd apps/driftguard-checks-app

# Install security packages
npm install --save \
    helmet \
    express-rate-limit \
    express-validator \
    dotenv \
    winston \
    crypto

npm install --save-dev \
    @types/express-rate-limit \
    eslint-plugin-security

print_status "Security dependencies installed"

echo ""
echo "Step 6: Creating security middleware..."

cat > src/security.ts << 'EOF'
import crypto from 'crypto';
import rateLimit from 'express-rate-limit';
import { Request, Response, NextFunction } from 'express';

/**
 * Verify GitHub webhook signature
 */
export function verifyWebhookSignature(
  payload: string,
  signature: string | undefined,
  secret: string
): boolean {
  if (!signature) return false;
  
  const expectedSignature = `sha256=${crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex')}`;
  
  try {
    return crypto.timingSafeEqual(
      Buffer.from(signature),
      Buffer.from(expectedSignature)
    );
  } catch {
    return false;
  }
}

/**
 * Webhook signature validation middleware
 */
export function webhookSignatureMiddleware(secret: string) {
  return (req: Request, res: Response, next: NextFunction) => {
    const signature = req.headers['x-hub-signature-256'] as string;
    const payload = JSON.stringify(req.body);
    
    if (!verifyWebhookSignature(payload, signature, secret)) {
      console.error('Invalid webhook signature attempted', {
        ip: req.ip,
        timestamp: new Date().toISOString()
      });
      return res.status(401).json({ error: 'Unauthorized' });
    }
    
    next();
  };
}

/**
 * Rate limiting for webhooks
 */
export const webhookRateLimiter = rateLimit({
  windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '60000'),
  max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS || '100'),
  message: 'Too many webhook requests, please try again later',
  standardHeaders: true,
  legacyHeaders: false,
  handler: (req, res) => {
    console.warn('Rate limit exceeded', {
      ip: req.ip,
      timestamp: new Date().toISOString()
    });
    res.status(429).json({ error: 'Too many requests' });
  }
});

/**
 * Sanitize error messages for external responses
 */
export function sanitizeError(error: any): string {
  // Log full error internally
  console.error('Internal error:', error);
  
  // Return generic message externally
  if (process.env.NODE_ENV === 'production') {
    return 'An error occurred processing your request';
  }
  
  // In development, return more details
  return error.message || 'An error occurred';
}

/**
 * Security headers middleware
 */
export function securityHeaders() {
  return (req: Request, res: Response, next: NextFunction) => {
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('X-Frame-Options', 'DENY');
    res.setHeader('X-XSS-Protection', '1; mode=block');
    res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
    next();
  };
}
EOF

print_status "Security middleware created"

echo ""
echo "Step 7: Creating security audit script..."

cd ../..

cat > security-audit.sh << 'EOF'
#!/bin/bash

echo "Running Security Audit..."
echo "========================"

# Check for exposed secrets
echo "Checking for exposed secrets..."
grep -r "BEGIN RSA PRIVATE KEY\|BEGIN PRIVATE KEY\|secret.*=\|api.*key.*=\|token.*=" \
    --exclude-dir=node_modules \
    --exclude-dir=.git \
    --exclude="*.md" \
    --exclude="security-audit.sh" \
    . 2>/dev/null | grep -v "example\|template\|\.example" || echo "✓ No exposed secrets found"

# Check dependencies
echo ""
echo "Checking npm vulnerabilities..."
cd apps/driftguard-checks-app
npm audit --audit-level=moderate

# Check for .env files
echo ""
echo "Checking for .env files in repository..."
find . -name ".env*" -not -name ".env.example" -not -path "*/node_modules/*" -not -path "*/.git/*"

echo ""
echo "Security audit complete!"
EOF

chmod +x security-audit.sh
print_status "Security audit script created"

echo ""
echo "Step 8: Generating secure webhook secret..."

# Generate a secure random webhook secret
WEBHOOK_SECRET=$(openssl rand -hex 32)
echo ""
print_warning "New secure webhook secret generated:"
echo "WEBHOOK_SECRET=$WEBHOOK_SECRET"
echo ""
print_warning "Save this secret securely and add it to your GitHub App settings!"

echo ""
echo "=============================================="
echo "🔐 Security Fix Complete!"
echo "=============================================="
echo ""
echo "⚠️  CRITICAL ACTIONS STILL REQUIRED:"
echo ""
echo "1. Go to GitHub and revoke your current GitHub App credentials:"
echo "   https://github.com/settings/apps/driftguard-checks"
echo ""
echo "2. Generate a new private key and download it"
echo ""
echo "3. Update your webhook secret to: $WEBHOOK_SECRET"
echo ""
echo "4. Clean git history to remove exposed secrets:"
echo "   git filter-branch --force --index-filter \\"
echo "   'git rm --cached --ignore-unmatch apps/driftguard-checks-app/private-key.pem' \\"
echo "   --prune-empty --tag-name-filter cat -- --all"
echo ""
echo "5. Force push the cleaned history:"
echo "   git push origin --force --all"
echo ""
echo "6. Run the security audit:"
echo "   ./security-audit.sh"
echo ""
echo "7. Update your deployment with new credentials"
echo ""
print_error "DO NOT DEPLOY until all security issues are resolved!"