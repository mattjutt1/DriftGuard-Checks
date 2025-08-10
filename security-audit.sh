#!/bin/bash

# DriftGuard Security Audit Script
# Comprehensive security checks for the application

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔒 DriftGuard Security Audit"
echo "============================"
echo ""

ISSUES_FOUND=0

# Function to check for patterns
check_pattern() {
    local pattern="$1"
    local description="$2"
    local exclude_dirs="--exclude-dir=node_modules --exclude-dir=.git --exclude-dir=security-backup"
    
    echo -n "Checking for $description... "
    
    if grep -r "$pattern" $exclude_dirs --exclude="*.md" --exclude="*.sh" --exclude="*.example" . 2>/dev/null | grep -v "example\|template\|\.example" > /dev/null; then
        echo -e "${RED}[FOUND]${NC}"
        echo "  Files containing $description:"
        grep -r "$pattern" $exclude_dirs --exclude="*.md" --exclude="*.sh" --exclude="*.example" . 2>/dev/null | grep -v "example\|template\|\.example" | head -5
        ((ISSUES_FOUND++))
    else
        echo -e "${GREEN}[CLEAN]${NC}"
    fi
}

# 1. Check for exposed private keys
echo "1. Checking for exposed private keys..."
check_pattern "BEGIN RSA PRIVATE KEY\|BEGIN PRIVATE KEY\|BEGIN EC PRIVATE KEY" "private keys"

# 2. Check for hardcoded secrets
echo ""
echo "2. Checking for hardcoded secrets..."
check_pattern "secret.*=.*['\"].*['\"]" "hardcoded secrets"
check_pattern "api[_-]?key.*=.*['\"].*['\"]" "API keys"
check_pattern "token.*=.*['\"].*['\"]" "tokens"
check_pattern "password.*=.*['\"].*['\"]" "passwords"

# 3. Check for .env files
echo ""
echo "3. Checking for .env files in repository..."
echo -n "Looking for .env files... "
ENV_FILES=$(find . -name ".env*" -not -name ".env.example" -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/security-backup/*" 2>/dev/null)
if [ -z "$ENV_FILES" ]; then
    echo -e "${GREEN}[CLEAN]${NC}"
else
    echo -e "${RED}[FOUND]${NC}"
    echo "  .env files found:"
    echo "$ENV_FILES"
    ((ISSUES_FOUND++))
fi

# 4. Check npm vulnerabilities
echo ""
echo "4. Checking npm vulnerabilities..."
cd apps/driftguard-checks-app 2>/dev/null || {
    echo -e "${YELLOW}[SKIPPED]${NC} - DriftGuard app directory not found"
}

if [ -d "apps/driftguard-checks-app" ]; then
    cd apps/driftguard-checks-app
    echo -n "Running npm audit... "
    
    AUDIT_RESULT=$(npm audit --json 2>/dev/null || echo '{"vulnerabilities":{}}')
    VULN_COUNT=$(echo "$AUDIT_RESULT" | grep -o '"total":[0-9]*' | grep -o '[0-9]*' || echo "0")
    
    if [ "$VULN_COUNT" -eq 0 ]; then
        echo -e "${GREEN}[CLEAN]${NC}"
    else
        echo -e "${RED}[$VULN_COUNT vulnerabilities]${NC}"
        npm audit 2>/dev/null || true
        ((ISSUES_FOUND++))
    fi
    cd ../..
fi

# 5. Check file permissions
echo ""
echo "5. Checking file permissions..."
echo -n "Checking for world-readable sensitive files... "
SENSITIVE_PERMS=$(find . -name "*.pem" -o -name "*.key" -o -name ".env*" 2>/dev/null | xargs -I {} ls -la {} 2>/dev/null | grep -E "^-rw-r--r--|^-rw-rw-r--|^-rw-rw-rw-" || true)
if [ -z "$SENSITIVE_PERMS" ]; then
    echo -e "${GREEN}[SECURE]${NC}"
else
    echo -e "${YELLOW}[WARNING]${NC}"
    echo "  Files with loose permissions:"
    echo "$SENSITIVE_PERMS"
fi

# 6. Check for TODO security items
echo ""
echo "6. Checking for TODO security items..."
echo -n "Scanning for security TODOs... "
SECURITY_TODOS=$(grep -r "TODO.*security\|FIXME.*security\|XXX.*security\|HACK.*security" --exclude-dir=node_modules --exclude-dir=.git . 2>/dev/null || true)
if [ -z "$SECURITY_TODOS" ]; then
    echo -e "${GREEN}[NONE]${NC}"
else
    echo -e "${YELLOW}[FOUND]${NC}"
    echo "  Security TODOs found:"
    echo "$SECURITY_TODOS" | head -5
fi

# 7. Check GitHub App configuration
echo ""
echo "7. Checking GitHub App configuration..."
if [ -f "apps/driftguard-checks-app/src/index-secure.ts" ]; then
    echo -n "Checking for webhook validation... "
    if grep -q "webhookSignatureMiddleware" apps/driftguard-checks-app/src/index-secure.ts; then
        echo -e "${GREEN}[IMPLEMENTED]${NC}"
    else
        echo -e "${RED}[MISSING]${NC}"
        ((ISSUES_FOUND++))
    fi
    
    echo -n "Checking for rate limiting... "
    if grep -q "rateLimiters" apps/driftguard-checks-app/src/index-secure.ts; then
        echo -e "${GREEN}[IMPLEMENTED]${NC}"
    else
        echo -e "${RED}[MISSING]${NC}"
        ((ISSUES_FOUND++))
    fi
    
    echo -n "Checking for error sanitization... "
    if grep -q "sanitizeError" apps/driftguard-checks-app/src/index-secure.ts; then
        echo -e "${GREEN}[IMPLEMENTED]${NC}"
    else
        echo -e "${RED}[MISSING]${NC}"
        ((ISSUES_FOUND++))
    fi
else
    echo -e "${YELLOW}[SKIPPED]${NC} - Secure index file not found"
fi

# 8. Check for sensitive data in logs
echo ""
echo "8. Checking for sensitive data in logs..."
echo -n "Scanning log files... "
LOG_FILES=$(find . -name "*.log" -not -path "*/node_modules/*" 2>/dev/null)
if [ -z "$LOG_FILES" ]; then
    echo -e "${GREEN}[NO LOGS]${NC}"
else
    SENSITIVE_IN_LOGS=$(grep -E "secret|password|token|key" $LOG_FILES 2>/dev/null | grep -v "example\|template" || true)
    if [ -z "$SENSITIVE_IN_LOGS" ]; then
        echo -e "${GREEN}[CLEAN]${NC}"
    else
        echo -e "${RED}[FOUND]${NC}"
        echo "  Potential sensitive data in logs:"
        echo "$SENSITIVE_IN_LOGS" | head -3
        ((ISSUES_FOUND++))
    fi
fi

# 9. Check git history for secrets
echo ""
echo "9. Checking git history for secrets..."
echo -n "Scanning recent commits... "
GIT_SECRETS=$(git log -p -10 2>/dev/null | grep -E "secret.*=|key.*=|token.*=|password.*=" | grep -v "example\|template\|\.example" || true)
if [ -z "$GIT_SECRETS" ]; then
    echo -e "${GREEN}[CLEAN]${NC}"
else
    echo -e "${YELLOW}[WARNING]${NC}"
    echo "  Potential secrets in recent git history"
    echo "  Run ./clean-git-history.sh to clean"
fi

# 10. Security headers check
echo ""
echo "10. Checking security headers implementation..."
if [ -f "apps/driftguard-checks-app/src/security/index.ts" ]; then
    HEADERS=("X-Content-Type-Options" "X-Frame-Options" "X-XSS-Protection" "Strict-Transport-Security")
    ALL_HEADERS_FOUND=true
    
    for header in "${HEADERS[@]}"; do
        echo -n "  Checking for $header... "
        if grep -q "$header" apps/driftguard-checks-app/src/security/index.ts; then
            echo -e "${GREEN}[FOUND]${NC}"
        else
            echo -e "${RED}[MISSING]${NC}"
            ALL_HEADERS_FOUND=false
            ((ISSUES_FOUND++))
        fi
    done
else
    echo -e "${YELLOW}[SKIPPED]${NC} - Security module not found"
fi

# Summary
echo ""
echo "========================================="
echo "Security Audit Summary"
echo "========================================="

if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✅ All security checks passed!${NC}"
    echo "Your application appears to be secure."
else
    echo -e "${RED}⚠️  $ISSUES_FOUND security issues found!${NC}"
    echo ""
    echo "Recommended actions:"
    echo "1. Remove any exposed secrets immediately"
    echo "2. Rotate all credentials that may have been exposed"
    echo "3. Run npm audit fix to patch vulnerabilities"
    echo "4. Clean git history if secrets were committed"
    echo "5. Implement missing security features"
fi

echo ""
echo "Security Score: $((100 - ISSUES_FOUND * 10))/100"
echo ""
echo "For detailed remediation steps, see SECURITY_VULNERABILITY_REPORT.md"

exit $ISSUES_FOUND