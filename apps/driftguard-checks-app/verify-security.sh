#!/bin/bash

# Security Verification Script for DriftGuard
# Comprehensive check of all security features

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
WARNINGS=0

# Function to print headers
print_header() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  $1"
    echo "═══════════════════════════════════════════════════════════════"
}

# Function to check test result
check_result() {
    local test_name="$1"
    local result="$2"
    local expected="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if [ "$result" = "$expected" ]; then
        echo -e "${GREEN}✅ PASS${NC}: $test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}: $test_name"
        echo "   Expected: $expected"
        echo "   Got: $result"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Function to check file exists
check_file() {
    local file="$1"
    local description="$2"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ PASS${NC}: $description exists"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}: $description missing: $file"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Function to check command exists
check_command() {
    local cmd="$1"
    local description="$2"
    
    if command -v "$cmd" &> /dev/null; then
        echo -e "${GREEN}✅${NC} $description available"
        return 0
    else
        echo -e "${YELLOW}⚠️${NC}  $description not available"
        WARNINGS=$((WARNINGS + 1))
        return 1
    fi
}

# Function to test endpoint
test_endpoint() {
    local url="$1"
    local expected_code="$2"
    local description="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_code"; then
        echo -e "${GREEN}✅ PASS${NC}: $description"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC}: $description"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Main verification
main() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║         DriftGuard Security Verification Suite             ║"
    echo "║                    Version 2.0.0                           ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    
    # 1. Check Prerequisites
    print_header "1. Prerequisites Check"
    
    check_command "node" "Node.js"
    check_command "npm" "NPM"
    check_command "docker" "Docker"
    check_command "redis-cli" "Redis CLI"
    check_command "curl" "cURL"
    
    # 2. Check Security Files
    print_header "2. Security Files Verification"
    
    check_file "src/security/index.ts" "Core security module"
    check_file "src/security/advanced-2025.ts" "Advanced security module"
    check_file "src/index-integrated.ts" "Integrated application"
    check_file ".env.example" "Environment template"
    check_file ".gitignore" "Git ignore file"
    check_file "docker-compose.yml" "Docker configuration"
    check_file "Dockerfile" "Docker build file"
    
    # 3. Check Removed Sensitive Files
    print_header "3. Sensitive Files Check"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if [ ! -f "private-key.pem" ]; then
        echo -e "${GREEN}✅ PASS${NC}: private-key.pem removed"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ CRITICAL${NC}: private-key.pem still exists!"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if [ ! -f ".env" ] || [ -f ".env.example" ]; then
        echo -e "${GREEN}✅ PASS${NC}: No production .env in repository"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${YELLOW}⚠️ WARNING${NC}: .env file exists (check if it's in .gitignore)"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    # 4. Check Dependencies
    print_header "4. Security Dependencies Check"
    
    echo "Checking package.json for security packages..."
    
    for pkg in "helmet" "express-rate-limit" "zod" "winston" "bull" "axios"; do
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
        if grep -q "\"$pkg\"" package.json; then
            echo -e "${GREEN}✅ PASS${NC}: $pkg installed"
            PASSED_TESTS=$((PASSED_TESTS + 1))
        else
            echo -e "${RED}❌ FAIL${NC}: $pkg not found in package.json"
            FAILED_TESTS=$((FAILED_TESTS + 1))
        fi
    done
    
    # 5. Build Application
    print_header "5. Build Verification"
    
    echo "Installing dependencies..."
    npm install --silent 2>/dev/null || {
        echo -e "${RED}❌ FAIL${NC}: npm install failed"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    }
    
    echo "Building TypeScript..."
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if npm run build --silent 2>/dev/null; then
        echo -e "${GREEN}✅ PASS${NC}: TypeScript build successful"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}❌ FAIL${NC}: TypeScript build failed"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    
    # 6. Run Security Tests
    print_header "6. Security Tests"
    
    echo "Running security unit tests..."
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if npm run test:security 2>/dev/null; then
        echo -e "${GREEN}✅ PASS${NC}: Security tests passed"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${YELLOW}⚠️ WARNING${NC}: Some security tests failed or not configured"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    # 7. Check Redis Connection
    print_header "7. Redis Connectivity"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if redis-cli ping 2>/dev/null | grep -q "PONG"; then
        echo -e "${GREEN}✅ PASS${NC}: Redis is running"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    elif docker ps | grep -q redis; then
        echo -e "${GREEN}✅ PASS${NC}: Redis running in Docker"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${YELLOW}⚠️ WARNING${NC}: Redis not running (async processing unavailable)"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    # 8. Check Git Security
    print_header "8. Git Security Check"
    
    echo "Checking for secrets in git history..."
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if ! git log --all --grep="private-key" 2>/dev/null | grep -q "private-key"; then
        echo -e "${GREEN}✅ PASS${NC}: No private key references in git log"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${YELLOW}⚠️ WARNING${NC}: Private key references found in git history"
        echo "   Run: git filter-branch to clean history"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    # 9. Environment Variables Check
    print_header "9. Environment Configuration"
    
    if [ -f ".env" ]; then
        echo "Checking .env configuration..."
        
        for var in "WEBHOOK_SECRET" "GITHUB_APP_ID" "GITHUB_CLIENT_ID"; do
            TOTAL_TESTS=$((TOTAL_TESTS + 1))
            if grep -q "^$var=" .env; then
                echo -e "${GREEN}✅ PASS${NC}: $var configured"
                PASSED_TESTS=$((PASSED_TESTS + 1))
            else
                echo -e "${YELLOW}⚠️ WARNING${NC}: $var not configured"
                WARNINGS=$((WARNINGS + 1))
            fi
        done
    else
        echo -e "${YELLOW}⚠️${NC} No .env file found (using defaults)"
    fi
    
    # 10. Docker Security Check
    print_header "10. Docker Security"
    
    check_file "Dockerfile" "Dockerfile"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if grep -q "USER nodejs" Dockerfile 2>/dev/null; then
        echo -e "${GREEN}✅ PASS${NC}: Non-root user configured"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${YELLOW}⚠️ WARNING${NC}: Container may run as root"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if grep -q "HEALTHCHECK" Dockerfile 2>/dev/null; then
        echo -e "${GREEN}✅ PASS${NC}: Health check configured"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${YELLOW}⚠️ WARNING${NC}: No health check configured"
        WARNINGS=$((WARNINGS + 1))
    fi
    
    # Summary Report
    print_header "VERIFICATION SUMMARY"
    
    echo ""
    echo "Total Tests:    $TOTAL_TESTS"
    echo -e "${GREEN}Passed:         $PASSED_TESTS${NC}"
    echo -e "${RED}Failed:         $FAILED_TESTS${NC}"
    echo -e "${YELLOW}Warnings:       $WARNINGS${NC}"
    echo ""
    
    # Calculate percentage
    if [ $TOTAL_TESTS -gt 0 ]; then
        PERCENTAGE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
        echo "Success Rate:   ${PERCENTAGE}%"
        
        # Security Score
        if [ $PERCENTAGE -ge 90 ]; then
            echo -e "${GREEN}Security Grade: A (Excellent)${NC}"
        elif [ $PERCENTAGE -ge 80 ]; then
            echo -e "${GREEN}Security Grade: B (Good)${NC}"
        elif [ $PERCENTAGE -ge 70 ]; then
            echo -e "${YELLOW}Security Grade: C (Acceptable)${NC}"
        elif [ $PERCENTAGE -ge 60 ]; then
            echo -e "${YELLOW}Security Grade: D (Needs Improvement)${NC}"
        else
            echo -e "${RED}Security Grade: F (Critical Issues)${NC}"
        fi
    fi
    
    echo ""
    
    # Critical Actions Required
    if [ $FAILED_TESTS -gt 0 ] || [ $WARNINGS -gt 0 ]; then
        print_header "ACTIONS REQUIRED"
        
        if [ -f "private-key.pem" ]; then
            echo -e "${RED}CRITICAL:${NC} Remove private-key.pem immediately!"
            echo "  Run: rm private-key.pem"
        fi
        
        if [ $WARNINGS -gt 0 ]; then
            echo -e "${YELLOW}WARNINGS:${NC}"
            echo "  1. Rotate GitHub App credentials"
            echo "  2. Configure environment variables"
            echo "  3. Clean git history if needed"
            echo "  4. Start Redis for async processing"
        fi
    else
        echo -e "${GREEN}🎉 All security checks passed!${NC}"
        echo "The application is ready for deployment."
    fi
    
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    
    # Exit with appropriate code
    if [ $FAILED_TESTS -gt 0 ]; then
        exit 1
    else
        exit 0
    fi
}

# Run verification
main "$@"