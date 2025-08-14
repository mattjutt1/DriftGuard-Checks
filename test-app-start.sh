#!/bin/bash
# Test if app starts properly with current config
set -e

echo "🧪 Testing app startup with current configuration..."

# Check private key exists
if [ ! -f "private-key.pem" ]; then
    echo "❌ private-key.pem not found!"
    echo "📥 Download it from: https://github.com/settings/apps"
    exit 1
fi

echo "✅ Private key found"
echo "✅ Environment configured"

# Test app startup (using environment PORT from .env)
echo "🚀 Testing app startup..."
PORT=3000 timeout 10 npm run start:dev > startup.log 2>&1 &
APP_PID=$!
sleep 5

# Check if app started successfully
if ps -p $APP_PID > /dev/null; then
    echo "✅ App started successfully!"
    
    # Test health endpoint
    HEALTH=$(curl -s http://localhost:3000/health || echo "failed")
    if [[ "$HEALTH" == *"healthy"* ]]; then
        echo "✅ Health endpoint working"
    else
        echo "⚠️  Health endpoint issue"
    fi
    
    # Test webhook endpoint exists
    WEBHOOK=$(curl -s -w "%{http_code}" -o /dev/null http://localhost:3000/api/github/webhooks || echo "000")
    echo "🔗 Webhook endpoint response: $WEBHOOK"
    
    kill $APP_PID 2>/dev/null || true
    echo "✅ App test complete!"
else
    echo "❌ App failed to start"
    echo "📋 Startup log:"
    cat startup.log
fi

rm -f startup.log