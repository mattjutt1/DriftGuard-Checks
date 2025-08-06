# PromptEvolver Deployment Guide

Current Status: ✅ Convex backend deployed | ⏳ External Ollama needed

## Current Architecture

```
Frontend (localhost:3000) → Convex Cloud (deployed) → External Ollama Server (needed)
```

## Deployment Options

### Option 1: Railway (Free, Recommended)
Railway provides free hosting with automatic public URLs.

```bash
# Deploy to Railway (free tier)
./deploy-to-railway.sh
```

**Pros**: Free, automatic HTTPS, easy deployment
**Cons**: May have usage limits

### Option 2: Docker on Any VPS
Deploy using Docker on any cloud provider (DigitalOcean, Linode, AWS, etc.)

```bash
# Copy docker-ollama-server/ to your VPS
scp -r docker-ollama-server/ user@your-vps:/tmp/

# SSH and deploy
ssh user@your-vps
cd /tmp/docker-ollama-server
docker-compose up -d
```

**Pros**: Full control, reliable
**Cons**: Requires VPS ($5-10/month)

### Option 3: Manual VPS Setup
Use the deployment script on any Ubuntu/Debian server.

```bash
# Copy to your VPS and run
scp deploy-ollama-server.sh user@your-vps:/tmp/
ssh user@your-vps
sudo /tmp/deploy-ollama-server.sh
```

### Option 4: Cloud Container Services

**Google Cloud Run** (Pay per use):
```bash
cd docker-ollama-server/
gcloud builds submit --tag gcr.io/YOUR_PROJECT/ollama-server
gcloud run deploy --image gcr.io/YOUR_PROJECT/ollama-server --port 11434
```

**AWS Fargate**, **DigitalOcean App Platform**, etc. also supported.

## Current Convex Configuration

The backend is already deployed and configured:
- ✅ Convex URL: `https://resilient-guanaco-29.convex.cloud`
- ✅ Authentication: Working with deploy key
- ✅ HTTP Actions: Enabled at `/health` and `/optimize`

## Next Steps

1. **Choose a deployment option** and deploy Ollama server
2. **Get the public URL** of your Ollama server
3. **Update environment variable**: Add `OLLAMA_SERVER_URL=http://YOUR_SERVER:11434` to Convex
4. **Test integration**: The health check should show "available: true"
5. **Deploy frontend**: Deploy to Vercel with working backend

## Testing After Deployment

```bash
# Test your external Ollama server
curl http://YOUR_SERVER:11434/api/tags

# Test Convex integration
curl https://resilient-guanaco-29.convex.cloud/health

# Test optimization
curl -X POST https://resilient-guanaco-29.convex.cloud/optimize \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Write a hello world program", "domain": "programming"}'
```

## Environment Variables Needed

In Convex Dashboard → Environment Variables:
```
OLLAMA_SERVER_URL=http://YOUR_SERVER_IP:11434
```

## Resource Requirements

- **Minimum VPS**: 4GB RAM, 2 vCPU, 10GB storage
- **Model Size**: Qwen3:4b requires ~2.6GB RAM
- **Recommended**: 8GB RAM for better performance

## Cost Estimate

- **Railway**: Free tier (with limits)
- **Basic VPS**: $5-10/month
- **Cloud Run**: ~$0.10/request (pay per use)

## Ready to Deploy?

Choose your preferred option and run the deployment. The fastest option is Railway:

```bash
./deploy-to-railway.sh
```

Then update the Convex environment variable and test!