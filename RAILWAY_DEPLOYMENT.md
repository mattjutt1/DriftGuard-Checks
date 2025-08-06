# Railway Ollama Deployment Guide

## Current Status
The Ollama container builds successfully but crashes immediately on Railway. We've created multiple Dockerfile variations to resolve this.

## Dockerfile Options (Try in Order)

### Option 1: Ultra-Minimal (Dockerfile.minimal)
```bash
# Rename to use this version
cp Dockerfile.minimal Dockerfile
git add Dockerfile
git commit -m "Use minimal Ollama Dockerfile"
git push
```

This is the simplest possible configuration - just runs Ollama with PORT binding.

### Option 2: Direct Execution (Dockerfile.direct)
```bash
# Rename to use this version
cp Dockerfile.direct Dockerfile
git add Dockerfile
git commit -m "Use direct execution Dockerfile"
git push
```

Bypasses shell scripts entirely, runs Ollama directly with inline PORT handling.

### Option 3: Compatible Script Version (Current Dockerfile)
```bash
# This is already the active Dockerfile
git add Dockerfile
git commit -m "Use compatible script Dockerfile"
git push
```

Uses echo commands to create startup script (most compatible with Docker).

## Railway Configuration

Ensure these files exist in your repository root:

### railway.toml
```toml
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile"

[deploy]
healthcheckPath = "/api/tags"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

### railway.json (Alternative)
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "dockerfile"
  },
  "deploy": {
    "healthcheckPath": "/api/tags",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3,
    "numReplicas": 1
  }
}
```

## Deployment Steps

1. **Push to GitHub**:
```bash
git add .
git commit -m "Fix Ollama Railway deployment"
git push origin main
```

2. **In Railway Dashboard**:
- Go to your service
- Click "Settings" → "Deploy"
- Trigger a new deployment
- Watch the logs carefully

3. **Expected Log Output**:
```
========================================
Railway Ollama Server Starting...
========================================
Using Railway PORT: [dynamic port]
OLLAMA_HOST set to: 0.0.0.0:[port]
Current user: root
Ollama location: /bin/ollama
Working directory: /
========================================
Starting Ollama server...
========================================
```

4. **If it works**, you'll see:
- Health check passing (green status)
- Logs showing Ollama is serving
- Public URL accessible at `/api/tags`

## Debugging Failed Deployments

### Check Container Logs
Look for the FIRST error message - it usually indicates why the container crashed.

### Common Issues and Fixes

1. **"exec format error"**
   - The binary architecture doesn't match
   - Solution: Ensure using official ollama/ollama image

2. **"permission denied"**
   - Script execution permissions
   - Solution: Use Dockerfile.minimal or Dockerfile.direct

3. **No logs at all**
   - Container crashes before script runs
   - Solution: Use Dockerfile.minimal (simplest approach)

4. **"address already in use"**
   - PORT conflict
   - Solution: Ensure using ${PORT} variable correctly

## Testing Locally

Before deploying to Railway, test locally:

```bash
# Build locally
docker build -t ollama-test .

# Run with PORT variable
docker run -e PORT=8080 -p 8080:8080 ollama-test

# Test health endpoint
curl http://localhost:8080/api/tags
```

## After Successful Deployment

1. **Get the Railway URL**:
   - Click on your service in Railway
   - Copy the public URL (e.g., `https://your-app.up.railway.app`)

2. **Test the endpoint**:
```bash
curl https://your-app.up.railway.app/api/tags
```

3. **Update Convex Environment**:
```bash
# In nextjs-app directory
npx convex env set OLLAMA_SERVER_URL "https://your-app.up.railway.app"
```

4. **Download Qwen3 Model**:
Once Ollama is running, you can trigger model download:
```bash
curl -X POST https://your-app.up.railway.app/api/pull \
  -H "Content-Type: application/json" \
  -d '{"name": "qwen3:4b"}'
```

## Alternative: Railway Template

If custom Dockerfiles don't work, use Railway's official Ollama template:

1. Go to: https://railway.com/template/tXERGO
2. Click "Deploy Now"
3. Connect your GitHub account
4. Deploy the template
5. Modify for your needs

## Next Steps After Ollama Works

1. Test Convex integration:
```bash
cd nextjs-app
npx convex run actions:checkOllamaHealth
```

2. Deploy frontend to Vercel:
```bash
vercel --prod
```

3. Celebrate! 🎉 Your PromptEvolver is fully deployed!

## Support

If none of these options work:
1. Check Railway status page
2. Review Railway Ollama discussions: https://station.railway.com
3. Consider using a different hosting provider (Render, Fly.io)
4. Fall back to local Ollama with ngrok tunnel (temporary solution)