#!/bin/bash

# Deploy Ollama server to Railway.app for free cloud hosting
# Railway provides free tier with public URL

set -e

echo "🚂 Deploying PromptEvolver Ollama to Railway"
echo "==========================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "📦 Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Check if logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway:"
    railway login
fi

# Create a new Railway project
echo "🏗️ Creating new Railway project..."
cd docker-ollama-server/

# Initialize Railway project
railway init

# Configure environment variables
echo "⚙️ Configuring environment variables..."
railway variables set OLLAMA_HOST=0.0.0.0:11434
railway variables set PORT=11434

# Deploy the application
echo "🚀 Deploying to Railway..."
railway up

# Get the deployment URL
echo "⏳ Getting deployment URL..."
sleep 10
RAILWAY_URL=$(railway domain)

if [ -n "$RAILWAY_URL" ]; then
    echo "✅ Deployment successful!"
    echo "🌐 Your Ollama server is available at: https://$RAILWAY_URL"
    echo
    echo "📋 Next steps:"
    echo "1. Wait 2-3 minutes for the model to download"
    echo "2. Test: curl https://$RAILWAY_URL/api/tags"
    echo "3. Update your .env.local:"
    echo "   OLLAMA_SERVER_URL=https://$RAILWAY_URL"
    echo
    echo "🔧 Railway Commands:"
    echo "   - Logs: railway logs"
    echo "   - Status: railway status"
    echo "   - Variables: railway variables"
else
    echo "⚠️ Deployment completed but URL not found"
    echo "Check Railway dashboard: https://railway.app/dashboard"
fi

cd ../
