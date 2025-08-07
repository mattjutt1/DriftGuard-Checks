# PromptEvolver Production Deployment Guide

## 🚀 Complete Deployment Instructions

### Step 1: Configure Convex Production Backend

1. **Login to Convex (run manually in your terminal):**
   ```bash
   cd /home/matt/prompt-wizard/nextjs-app
   npx convex auth
   ```

2. **Initialize Production Deployment:**
   ```bash
   npx convex deploy --prod
   ```

3. **Configure Environment Variables:**
   After deployment, copy the production URL to your `.env.local`:
   ```bash
   # The deployment will provide a URL like:
   # https://enchanted-rooster-257.convex.cloud
   ```

### Step 2: Update Configuration Files

1. **Update `.env.local`:**
   ```env
   # Production Convex Configuration
   NEXT_PUBLIC_CONVEX_URL=https://your-deployment-name.convex.cloud
   NODE_ENV=production
   ```

2. **Verify `convex.json` is updated:**
   The `prodUrl` should be populated after deployment.

### Step 3: Deploy Next.js Frontend to Vercel

1. **Install Vercel CLI (if not already installed):**
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Deploy to Production:**
   ```bash
   vercel --prod
   ```

4. **Set Environment Variables in Vercel:**
   - Go to Vercel Dashboard → Your Project → Settings → Environment Variables
   - Add: `NEXT_PUBLIC_CONVEX_URL` with your Convex deployment URL

### Step 4: Production Configuration Commands

Once you have the deployment URL, run these commands:

```bash
# Configure production environment
echo "NEXT_PUBLIC_CONVEX_URL=https://your-deployment-url.convex.cloud" > .env.production

# Build and test locally with production config
npm run build
npm run start

# Verify Convex functions are deployed
npx convex dashboard --prod
```

### Step 5: Validation Checklist

- [ ] Convex backend deployed and accessible
- [ ] Next.js frontend deployed to Vercel
- [ ] Environment variables configured correctly
- [ ] All HTTP endpoints responding
- [ ] Real-time features working
- [ ] Authentication system functional
- [ ] Prompt optimization features operational

## 🔗 Expected Deployment URLs

- **Frontend:** `https://prompt-wizard-[hash].vercel.app`
- **Backend:** `https://enchanted-rooster-257.convex.cloud`
- **Dashboard:** Accessible via `npx convex dashboard --prod`

## 🧪 Production Testing

After deployment, test these key features:

1. **Web Interface:** Visit your Vercel URL
2. **API Endpoints:** Test `/api/optimize` and other endpoints
3. **Real-time Updates:** Verify Convex subscriptions work
4. **Authentication:** Test user login/registration
5. **Prompt Optimization:** End-to-end optimization flow

## 🛠️ Troubleshooting

### Common Issues:

1. **"No CONVEX_DEPLOYMENT set" error:**
   ```bash
   npx convex dev  # Run once to configure
   ```

2. **Environment variables not loading:**
   - Check `.env.local` vs `.env.production`
   - Verify Vercel environment variables

3. **CORS issues:**
   - Convex automatically handles CORS for your deployment domain

4. **Function not found errors:**
   ```bash
   npx convex deploy --prod  # Redeploy functions
   ```

## 📊 Monitoring

Once deployed, monitor your application:

- **Convex Dashboard:** Function logs and performance
- **Vercel Analytics:** Frontend performance and errors
- **Browser DevTools:** Client-side functionality

---

**Ready for Production!** 🎉

Your PromptEvolver system is architecturally ready for deployment. Follow these steps to get it live and accessible to users.
