#!/bin/bash

# Test script to verify Convex HTTP endpoints are working after deployment
# Run this script after completing the authentication and deployment process

set -e

BASE_URL="https://resilient-guanaco-29.convex.cloud"

echo "🧪 Testing Convex HTTP Endpoints Deployment"
echo "============================================="
echo ""

# Test 1: Health endpoint
echo "🔍 Test 1: Health Endpoint (GET /health)"
echo "URL: $BASE_URL/health"
echo ""

HEALTH_RESPONSE=$(curl -s -w "%{http_code}" -X GET "$BASE_URL/health" -H "Content-Type: application/json")
HEALTH_CODE="${HEALTH_RESPONSE: -3}"
HEALTH_BODY="${HEALTH_RESPONSE%???}"

echo "HTTP Status: $HEALTH_CODE"
echo "Response: $HEALTH_BODY"

if [ "$HEALTH_CODE" = "200" ]; then
    echo "✅ Health endpoint working"
else
    echo "❌ Health endpoint failed (Status: $HEALTH_CODE)"
fi

echo ""
echo "----------------------------------------"
echo ""

# Test 2: Optimize endpoint
echo "🔍 Test 2: Optimize Endpoint (POST /optimize)"
echo "URL: $BASE_URL/optimize"
echo ""

OPTIMIZE_RESPONSE=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/optimize" \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Write a better email subject line", "domain": "general"}')

OPTIMIZE_CODE="${OPTIMIZE_RESPONSE: -3}"
OPTIMIZE_BODY="${OPTIMIZE_RESPONSE%???}"

echo "HTTP Status: $OPTIMIZE_CODE"
echo "Response: $OPTIMIZE_BODY"

if [ "$OPTIMIZE_CODE" = "200" ]; then
    echo "✅ Optimize endpoint working"
else
    echo "❌ Optimize endpoint failed (Status: $OPTIMIZE_CODE)"
fi

echo ""
echo "----------------------------------------"
echo ""

# Test 3: CORS preflight
echo "🔍 Test 3: CORS Preflight (OPTIONS /health)"
echo ""

CORS_RESPONSE=$(curl -s -w "%{http_code}" -X OPTIONS "$BASE_URL/health" \
    -H "Access-Control-Request-Method: GET" \
    -H "Access-Control-Request-Headers: Content-Type")

CORS_CODE="${CORS_RESPONSE: -3}"

echo "HTTP Status: $CORS_CODE"

if [ "$CORS_CODE" = "200" ]; then
    echo "✅ CORS preflight working"
else
    echo "❌ CORS preflight failed (Status: $CORS_CODE)"
fi

echo ""
echo "----------------------------------------"
echo ""

# Test 4: CLI Integration
echo "🔍 Test 4: CLI Integration"
echo ""

cd /home/matt/prompt-wizard/cli

echo "Running CLI health check..."
CLI_RESULT=$(python -m promptevolver_cli.main health 2>&1 || true)

if echo "$CLI_RESULT" | grep -q "✅"; then
    echo "✅ CLI integration working"
    echo "$CLI_RESULT"
else
    echo "❌ CLI integration failed"
    echo "$CLI_RESULT"
fi

echo ""
echo "============================================="
echo "🎉 Deployment Test Summary"
echo ""

# Summary
if [ "$HEALTH_CODE" = "200" ] && [ "$OPTIMIZE_CODE" = "200" ] && [ "$CORS_CODE" = "200" ]; then
    echo "🎯 All HTTP endpoints are working correctly!"
    echo "✅ Health endpoint: $HEALTH_CODE"
    echo "✅ Optimize endpoint: $OPTIMIZE_CODE" 
    echo "✅ CORS preflight: $CORS_CODE"
    echo ""
    echo "Ready for CLI usage! Try:"
    echo "cd /home/matt/prompt-wizard/cli"
    echo "python -m promptevolver_cli.main optimize 'Write a better email subject line'"
else
    echo "⚠️  Some endpoints may need attention:"
    echo "Health: $HEALTH_CODE"
    echo "Optimize: $OPTIMIZE_CODE"
    echo "CORS: $CORS_CODE"
fi

echo ""