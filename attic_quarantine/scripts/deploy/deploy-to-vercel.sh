#!/bin/bash

# Deploy PromptEvolver Frontend to Vercel
# Backend (Convex) is already deployed, this deploys the UI

set -e

echo "🎨 Deploying PromptEvolver Frontend to Vercel"
echo "============================================"

cd nextjs-app/

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
fi

# Login to Vercel if needed
if ! vercel whoami &> /dev/null; then
    echo "🔐 Please login to Vercel:"
    vercel login
fi

# Set environment variables
echo "⚙️ Setting environment variables..."
echo "NEXT_PUBLIC_CONVEX_URL=https://resilient-guanaco-29.convex.cloud" > .env.production

# Build the application
echo "🏗️ Building application..."
npm run build

# Deploy to Vercel
echo "🚀 Deploying to Vercel..."
vercel --prod

echo "✅ Frontend deployed successfully!"
echo "🌐 Your PromptEvolver app is now live on Vercel"
echo
echo "📋 Complete Architecture:"
echo "   Frontend: Vercel (deployed)"
echo "   Backend:  Convex (deployed)"
echo "   AI:       External Ollama (pending)"
echo
echo "⚠️ Next step: Deploy external Ollama server"
echo "   Run: ./deploy-to-railway.sh (or choose other option)"
