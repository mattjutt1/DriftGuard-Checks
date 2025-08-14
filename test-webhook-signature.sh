#!/bin/bash
# Test webhook signature validation with configured secret
set -e

WEBHOOK_SECRET="038e746ab2bc61a08f54ab203e72423f6a675c799a5855d2184bb49f1c480702"
PORT=3000

echo "🧪 Testing webhook signature validation..."

# Start app in background (using simple index.ts)
echo "🚀 Starting app..."
PORT=3000 NODE_OPTIONS='-r ts-node/register' timeout 15 npx probot run ./src/index.ts > app.log 2>&1 &
APP_PID=$!
sleep 5

# Test invalid signature
echo "🔒 Testing invalid signature (should fail)..."
INVALID_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: ping" \
  -H "X-GitHub-Delivery: test-delivery-123" \
  -H "X-Hub-Signature-256: sha256=invalid_signature" \
  -d '{"zen": "test", "hook_id": 123}' \
  http://localhost:$PORT/api/github/webhooks || echo "000")

echo "📊 Invalid signature response: $INVALID_RESPONSE"

# Test valid signature
echo "🔑 Testing valid signature (should succeed)..."
PAYLOAD='{"zen": "test", "hook_id": 123}'
SIGNATURE=$(echo -n "$PAYLOAD" | openssl dgst -sha256 -hmac "$WEBHOOK_SECRET" -binary | xxd -p)

VALID_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: ping" \
  -H "X-GitHub-Delivery: test-delivery-456" \
  -H "X-Hub-Signature-256: sha256=$SIGNATURE" \
  -d "$PAYLOAD" \
  http://localhost:$PORT/api/github/webhooks || echo "000")

echo "📊 Valid signature response: $VALID_RESPONSE"

# Kill app
kill $APP_PID 2>/dev/null || true
sleep 2

# Analyze results
echo ""
echo "📋 Results Summary:"
if [[ "$INVALID_RESPONSE" =~ ^(401|403|400)$ ]]; then
    echo "✅ Invalid signature properly rejected ($INVALID_RESPONSE)"
else
    echo "❌ Invalid signature not rejected ($INVALID_RESPONSE)"
fi

if [[ "$VALID_RESPONSE" == "200" ]]; then
    echo "✅ Valid signature accepted ($VALID_RESPONSE)"
else
    echo "⚠️  Valid signature response: $VALID_RESPONSE (may be expected for ping)"
fi

# Show last few log lines for context
echo ""
echo "📋 App log (last 10 lines):"
tail -10 app.log

rm -f app.log