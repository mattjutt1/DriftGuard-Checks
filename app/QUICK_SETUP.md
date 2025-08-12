# 🚀 DriftGuard Quick Setup Guide

## Step 1: Configure Environment Variables

Edit your `.env` file:

```bash
nano .env
```

Replace the placeholder values with your actual GitHub App credentials:

```env
# GitHub App Configuration (GET FROM GITHUB)
GITHUB_APP_ID=your-actual-app-id
GITHUB_CLIENT_ID=Iv1.your-actual-client-id
GITHUB_CLIENT_SECRET=your-actual-client-secret

# Use this generated secure webhook secret:
WEBHOOK_SECRET=038e746ab2bc61a08f54ab203e72423f6a675c799a5855d2184bb49f1c480702

# Path to your private key
PRIVATE_KEY_PATH=./private-key.pem

# For local development, change to:
NODE_ENV=development

# Redis (if you have it running)
REDIS_URL=redis://localhost:6379
```

## Step 2: Get Your GitHub App Credentials

1. Go to: https://github.com/settings/apps
2. Click on your DriftGuard app
3. Copy these values:
   - **App ID**: Number at the top of the page
   - **Client ID**: Under "OAuth credentials"
   - **Client Secret**: Click "Generate a new client secret"
   - **Private Key**: Click "Generate a private key" (downloads a .pem file)

## Step 3: Save Your Private Key

```bash
# Move the downloaded private key to the app directory
mv ~/Downloads/driftguard-checks.*.private-key.pem ./private-key.pem

# Set proper permissions
chmod 600 private-key.pem
```

## Step 4: Update GitHub Webhook Settings

1. In your GitHub App settings, go to "Webhook"
2. Set the **Webhook URL**: `https://your-domain.com/api/github/webhooks`
   - For local testing: Use ngrok or similar: `https://xxxxx.ngrok.io/api/github/webhooks`
3. Set the **Webhook secret**: 
   ```
   038e746ab2bc61a08f54ab203e72423f6a675c799a5855d2184bb49f1c480702
   ```
4. Select events to subscribe to:
   - ✅ Check run
   - ✅ Workflow run

## Step 5: Install Dependencies

```bash
npm install
```

## Step 6: Start the Application

### Option A: With Docker (Recommended)
```bash
docker-compose up -d
```

### Option B: With the Start Script
```bash
./start-with-redis.sh
```

### Option C: Manual Start
```bash
# Start Redis (if not running)
docker run -d -p 6379:6379 redis:7-alpine

# Build
npm run build

# Start
npm start
```

## Step 7: Verify Everything Works

```bash
# Check health
curl http://localhost:3000/health

# Check security status
curl http://localhost:3000/security/status

# Run verification script
./verify-security.sh
```

## Step 8: Test Webhook

```bash
# Test with the webhook secret we generated
PAYLOAD='{"test":"data"}'
SECRET="038e746ab2bc61a08f54ab203e72423f6a675c799a5855d2184bb49f1c480702"
SIGNATURE="sha256=$(echo -n "$PAYLOAD" | openssl dgst -sha256 -hmac "$SECRET" | cut -d' ' -f2)"

curl -X POST http://localhost:3000/api/github/webhooks \
  -H "Content-Type: application/json" \
  -H "X-Hub-Signature-256: $SIGNATURE" \
  -H "X-GitHub-Delivery: test-123" \
  -d "$PAYLOAD"
```

## 🎉 You're Done!

Your DriftGuard app is now secured and ready to use!

### Security Features Enabled:
- ✅ Webhook signature validation
- ✅ Rate limiting
- ✅ Replay protection
- ✅ Security headers
- ✅ Input validation
- ✅ Error sanitization
- ✅ Async processing (if Redis available)

### Next Steps:
1. Deploy to production using Docker
2. Set up monitoring and logging
3. Configure alerts for security events
4. Regularly rotate secrets (monthly recommended)

### Troubleshooting:
- If Redis isn't available, the app will still work in synchronous mode
- Check logs in the `logs/` directory for any issues
- Run `./verify-security.sh` to diagnose problems

---

**Remember**: Since your private key was previously exposed, make sure you're using a NEW private key from GitHub!