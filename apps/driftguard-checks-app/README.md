# DriftGuard Checks App

GitHub App for automated prompt evaluation check runs.

## Operating the App Locally with PM2

### Prerequisites

- Node.js >= 18
- PM2 installed globally: `npm install -g pm2`
- Valid `.env` file with APP_ID, WEBHOOK_SECRET, PRIVATE_KEY_PATH, WEBHOOK_PROXY_URL

### Start the App

```bash
cd ~/prompt-wizard/apps/driftguard-checks-app

# Build TypeScript
npm run build

# Start with PM2 supervision
npm run start:pm2

# Verify running
pm2 status driftguard-checks
curl -s http://localhost:3002/health | jq .
```

### Monitor & Control

```bash
# View logs
pm2 logs driftguard-checks

# Monitor in real-time
pm2 monit

# Restart if needed
pm2 restart driftguard-checks

# Stop
pm2 stop driftguard-checks

# Remove from PM2
pm2 delete driftguard-checks
```

### Health Endpoints

- **Main App**: `http://localhost:3001` (Probot webhooks)
- **Health Check**: `http://localhost:3002/health` (app status)

### Testing

Use the smoke test script to verify check runs:

```bash
npm run smoke:pr -- 12  # Test PR #12
npm run smoke:pr -- 13  # Test PR #13
```
