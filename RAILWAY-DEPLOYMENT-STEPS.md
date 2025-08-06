# 🚂 Railway Deployment - Step by Step Guide

Your repository is now ready for Railway deployment! Follow these exact steps:

## ✅ Prerequisites (DONE)
- ✅ Repository pushed to GitHub: `https://github.com/mattjutt1/prompt-wizard`
- ✅ Docker files created in `docker-ollama-server/`
- ✅ Railway configuration ready

## 🚀 Deployment Steps

### Step 1: Sign Up for Railway
1. Go to **https://railway.app**
2. Click **"Login"** → **"Sign up with GitHub"**
3. Authorize Railway to access your repositories

### Step 2: Deploy Your Repository
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository: **`mattjutt1/prompt-wizard`**
4. Click **"Deploy Now"**

### Step 3: Configure the Service
1. Railway will auto-detect the Dockerfile
2. **IMPORTANT**: Set the **"Root Directory"** to `docker-ollama-server`
   - Click on your service
   - Go to **"Settings"** → **"Build"**  
   - Set **"Root Directory"**: `docker-ollama-server`
3. Click **"Save Changes"**

### Step 4: Configure Environment (Optional)
1. Go to **"Variables"** tab
2. Add these if needed:
   - `PORT`: `11434`
   - `OLLAMA_HOST`: `0.0.0.0:11434`

### Step 5: Deploy and Wait
1. Railway will start building your Docker image
2. **Wait time**: 5-10 minutes (downloading Qwen3:4b model)
3. Watch the logs for "✅ External Ollama server ready with Qwen3:4b!"

### Step 6: Get Your Public URL
1. In Railway dashboard, click your service
2. Go to **"Settings"** → **"Networking"**
3. Click **"Generate Domain"** if not auto-generated
4. Copy your public URL (e.g., `https://your-app.up.railway.app`)

### Step 7: Test Your Deployment
```bash
# Test that your Ollama server is running
curl https://YOUR_RAILWAY_URL/api/tags

# Should return:
# {"models":[{"name":"qwen3:4b",...}]}
```

### Step 8: Update Convex Environment
1. Go to **Convex Dashboard**: https://dashboard.convex.dev
2. Select your project: **"resilient-guanaco-29"**
3. Go to **"Environment Variables"**
4. Add/Update:
   - **Key**: `OLLAMA_SERVER_URL`
   - **Value**: `https://YOUR_RAILWAY_URL` (your Railway domain)
5. Click **"Save"**

### Step 9: Test Complete Integration
```bash
# Test Convex can reach your Ollama server
curl https://resilient-guanaco-29.convex.cloud/health

# Should return:
# {"status":"success","data":{"available":true,"model":"Qwen3:4b available","error":null}}
```

## 🎯 **After Successful Deployment**

You'll have a complete working system:
```
localhost:3001 (Frontend) → Convex Cloud (Backend) → Railway (Ollama)
```

Next step: Deploy frontend to Vercel with `./deploy-to-vercel.sh`

## 🚨 Troubleshooting

**If build fails:**
- Check logs in Railway dashboard
- Ensure "Root Directory" is set to `docker-ollama-server`
- Verify repository has latest commits

**If health check fails:**
- Wait 2-3 minutes for model download
- Check Railway logs for "Ollama server ready"
- Verify URL format: `https://` not `http://`

**If Convex integration fails:**
- Double-check `OLLAMA_SERVER_URL` in Convex environment
- Test Railway URL directly first
- Ensure no trailing slashes in URL

## 💰 Railway Pricing
- **Free Tier**: 500 execution hours/month
- **Perfect for**: Development and testing
- **Upgrade**: $5/month for production use

---

## ⚡ Quick Summary

1. **Railway.app** → Login with GitHub
2. **New Project** → Deploy `mattjutt1/prompt-wizard`  
3. **Settings** → Root Directory: `docker-ollama-server`
4. **Wait** 5-10 minutes for deployment
5. **Copy** Railway URL → Update Convex environment
6. **Test** integration endpoints

**Ready to start? Go to https://railway.app and begin with Step 1!**