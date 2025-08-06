# Correct External Ollama Deployment Guide

After researching deployment options, here are the **correct approaches** ranked by ease and cost:

## 🥇 Option 1: Railway (Free, Recommended)

**Why Railway**: Free tier, automatic HTTPS, GitHub integration, perfect for Ollama

**Requirements**: 
- GitHub account
- This repository pushed to GitHub

**Steps**:
1. **Push this repo to GitHub** (if not already done):
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/prompt-wizard.git
   git push -u origin main
   ```

2. **Go to Railway.app**:
   - Sign up with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your `prompt-wizard` repository

3. **Configure Railway**:
   - Set **Root Directory**: `docker-ollama-server`
   - Railway will auto-detect the Dockerfile
   - Click Deploy

4. **Get Public URL**:
   - Railway provides a public URL like `https://your-app.up.railway.app`
   - Test: `curl https://your-app.up.railway.app/api/tags`

5. **Update Convex**:
   - Go to Convex Dashboard → Environment Variables
   - Set: `OLLAMA_SERVER_URL=https://your-app.up.railway.app`

**Estimated Time**: 10 minutes  
**Cost**: Free (500 hours/month)

---

## 🥈 Option 2: Google Cloud Run (Pay-per-use)

**Why Cloud Run**: Scales to zero, pay only when used, handles large models well

**Requirements**: 
- Google Cloud account
- `gcloud` CLI installed

**Steps**:
1. **Setup Google Cloud**:
   ```bash
   # Install gcloud CLI
   curl https://sdk.cloud.google.com | bash
   gcloud init
   gcloud auth login
   ```

2. **Build and Deploy**:
   ```bash
   cd docker-ollama-server/
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ollama-server
   gcloud run deploy ollama-server \
     --image gcr.io/YOUR_PROJECT_ID/ollama-server \
     --port 11434 \
     --memory 4Gi \
     --cpu 2 \
     --timeout 3600 \
     --allow-unauthenticated
   ```

3. **Get Service URL** and update Convex environment

**Estimated Time**: 15 minutes  
**Cost**: ~$0.05 per hour when active

---

## 🥉 Option 3: DigitalOcean App Platform

**Why DO App Platform**: Fixed pricing, reliable, good for production

**Requirements**: 
- DigitalOcean account
- GitHub repo

**Steps**:
1. Go to DigitalOcean → App Platform
2. Create app from GitHub repo
3. Set build context: `docker-ollama-server/`
4. Choose $5/month plan (minimum for 4GB RAM)
5. Deploy and get public URL

**Estimated Time**: 10 minutes  
**Cost**: $5/month

---

## 🛠️ Option 4: Manual VPS (Full Control)

**Why VPS**: Complete control, predictable costs, can use for other projects

**Requirements**: 
- VPS with 4GB+ RAM (DigitalOcean, Linode, etc.)

**Steps**:
1. **Create VPS** (Ubuntu 22.04, 4GB RAM minimum)

2. **SSH and setup**:
   ```bash
   ssh root@your-vps-ip
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   
   # Install Docker Compose
   apt install docker-compose -y
   ```

3. **Deploy Ollama**:
   ```bash
   # Copy our docker setup
   git clone https://github.com/YOUR_USERNAME/prompt-wizard.git
   cd prompt-wizard/docker-ollama-server/
   docker-compose up -d
   ```

4. **Test**: `curl http://YOUR_VPS_IP:11434/api/tags`

**Estimated Time**: 20 minutes  
**Cost**: $5-10/month

---

## ✅ Recommended Approach

**For Development/Testing**: Use Railway (free)  
**For Production**: Use Google Cloud Run or DigitalOcean

## Next Steps

1. **Choose your deployment method** from above
2. **Follow the steps** to get a public URL
3. **Update Convex environment**: Set `OLLAMA_SERVER_URL=https://your-url`
4. **Test integration**: `curl https://resilient-guanaco-29.convex.cloud/health`
5. **Deploy frontend**: `./deploy-to-vercel.sh`

## Testing After Deployment

```bash
# Test Ollama server directly
curl https://YOUR_OLLAMA_URL/api/tags

# Test Convex integration
curl https://resilient-guanaco-29.convex.cloud/health

# Should return: {"status":"success","data":{"available":true,"model":"Qwen3:4b available","error":null}}
```

Which deployment method would you like to use?