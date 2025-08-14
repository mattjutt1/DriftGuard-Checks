# DriftGuard Quick Start Guide

Get DriftGuard running in your organization in under 10 minutes.

## 🚀 Installation Methods

### Method 1: Setup Wizard (Recommended)

The easiest way to get started:

```bash
# Clone the repository
git clone https://github.com/mattjutt1/DriftGuard-Checks.git
cd DriftGuard-Checks

# Run the interactive setup wizard
./scripts/setup-wizard.sh
```

The wizard will:
- ✅ Check all prerequisites
- 🔧 Configure your GitHub App
- ⚙️ Set up environment variables
- 📦 Install dependencies and build
- ✨ Validate your configuration

### Method 2: Manual Setup

For advanced users who prefer manual configuration:

```bash
# 1. Install dependencies
npm ci

# 2. Create environment file
cp .env.example .env

# 3. Configure your GitHub App
# Edit .env with your App ID, private key, and webhook secret

# 4. Build the application
npm run build

# 5. Validate setup
./scripts/validate-config.js

# 6. Start DriftGuard
npm start
```

## 🔧 GitHub App Setup

### Option A: GitHub Marketplace (Coming Soon)

1. Visit [DriftGuard on GitHub Marketplace](https://github.com/marketplace/driftguard)
2. Click "Install" and select repositories
3. Note your App ID and generate webhook secret

### Option B: Manual App Creation

1. Go to [GitHub Apps settings](https://github.com/settings/apps)
2. Click "New GitHub App"
3. Use these settings:

**Basic Information:**
- **App name:** `YourOrg-DriftGuard`
- **Homepage URL:** `https://your-domain.com`
- **Webhook URL:** `https://your-domain.com/webhooks/github`

**Permissions:**
- **Checks:** Read & Write
- **Pull requests:** Read
- **Contents:** Read
- **Metadata:** Read

**Events:**
- ☑️ Pull request
- ☑️ Check run
- ☑️ Check suite

4. Generate a private key and download it
5. Note your App ID and webhook secret

## 🏃‍♂️ Quick Configuration

### Essential Environment Variables

```bash
# GitHub App Configuration
APP_ID=123456                    # Your GitHub App ID
WEBHOOK_SECRET=your-secret-here  # Webhook secret (32+ chars)
PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
...your private key...
-----END PRIVATE KEY-----"

# Server Configuration
PORT=3000                       # Port to run on
NODE_ENV=production            # production or development
```

### Validation

Test your setup:

```bash
# Validate configuration
./scripts/validate-config.js

# Test health endpoint
curl http://localhost:3000/health

# Test metrics
curl http://localhost:3000/metrics
```

## 📝 Add Workflow to Repositories

Create `.github/workflows/driftguard.yml` in your repositories:

```yaml
name: DriftGuard Gate
on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read

jobs:
  driftguard-gate:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Run Analysis
        run: |
          # Your analysis logic here
          echo '{"status":"pass","summary":"All checks passed","score":95}' > driftguard-capsule.json

      - name: Upload Results
        uses: actions/upload-artifact@v4
        with:
          name: driftguard-capsule
          path: driftguard-capsule.json
          retention-days: 30
```

## 🚦 Testing the Integration

1. **Create a test PR** in a monitored repository
2. **Check the workflow runs** - should see DriftGuard gate
3. **Verify check runs** - DriftGuard should create a check run
4. **Monitor logs** - check DriftGuard application logs

## 📊 Monitoring

### Health Checks

```bash
# Application health
curl http://localhost:3000/health

# Readiness for load balancer
curl http://localhost:3000/readyz

# Prometheus metrics
curl http://localhost:3000/metrics
```

### Expected Response

```json
{
  "status": "healthy",
  "message": "DriftGuard Checks is running",
  "uptime": "2h 15m 32s",
  "version": "1.0.0",
  "eventCount": 42,
  "lastEventAt": "2024-01-15T10:30:00Z"
}
```

## 🔒 Security Best Practices

### Environment Security

```bash
# Set proper permissions on .env
chmod 600 .env

# Never commit secrets
echo ".env" >> .gitignore

# Use strong webhook secret
openssl rand -hex 32
```

### Production Deployment

```bash
# Use PM2 for process management
npm install -g pm2
pm2 start npm --name "driftguard" -- start

# Set up log rotation
pm2 install pm2-logrotate

# Monitor with PM2
pm2 monit
```

## 🐳 Docker Deployment

```bash
# Build Docker image
docker build -t driftguard .

# Run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f driftguard
```

## 🆘 Troubleshooting

### Common Issues

**❌ "Webhook signature verification failed"**
```bash
# Check webhook secret matches
echo $WEBHOOK_SECRET
# Should be 32+ characters, same as GitHub App settings
```

**❌ "GitHub App authentication failed"**
```bash
# Validate private key format
./scripts/validate-config.js
# Should see "GitHub App credentials format valid"
```

**❌ "Port already in use"**
```bash
# Check what's using the port
lsof -ti:3000
# Kill process or use different port
```

**❌ "Artifact not found"**
```bash
# Verify workflow uploads artifact
cat .github/workflows/driftguard.yml
# Must include actions/upload-artifact@v4 step
```

### Getting Help

- 📖 **Documentation:** [docs/](../docs/)
- 🐛 **Issues:** [GitHub Issues](https://github.com/mattjutt1/DriftGuard-Checks/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/mattjutt1/DriftGuard-Checks/discussions)
- 🔒 **Security:** [security@driftguard.dev](mailto:security@driftguard.dev)

## ⚡ Quick Commands Reference

```bash
# Setup & Installation
./scripts/setup-wizard.sh           # Interactive setup
./scripts/validate-config.js        # Validate configuration
npm run build                       # Build application
npm start                          # Start DriftGuard

# Development
npm run dev                        # Development mode
npm test                          # Run tests
npm run lint                      # Lint code

# Monitoring
curl localhost:3000/health        # Health check
curl localhost:3000/metrics       # Metrics
docker-compose logs -f            # View logs
```

## 🎯 Next Steps

1. **Configure repositories:** Add the workflow to your repositories
2. **Set up monitoring:** Integrate with your monitoring stack
3. **Customize analysis:** Modify the analysis logic in your workflows
4. **Scale deployment:** Use Docker/Kubernetes for production

**Ready to ship faster and more securely?** 🚀

---

*Need help? Check our [troubleshooting guide](troubleshooting.md) or [open an issue](https://github.com/mattjutt1/DriftGuard-Checks/issues).*