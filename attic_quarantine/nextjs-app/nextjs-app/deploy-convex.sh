#!/bin/bash

echo "==================================="
echo "PromptEvolver Convex Deployment"
echo "==================================="
echo ""

# Navigate to the correct directory
cd /home/matt/prompt-wizard/nextjs-app

echo "Current directory: $(pwd)"
echo ""

# Check if we're logged in
echo "Checking Convex login status..."
npx convex whoami 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Not logged in. Please run: npx convex login"
    exit 1
fi

echo ""
echo "You are logged in to Convex!"
echo ""

# Instructions for deployment
echo "To deploy your Convex backend, follow these steps:"
echo ""
echo "1. Configure a new project (if needed):"
echo "   npx convex dev"
echo ""
echo "   When prompted:"
echo "   - Choose: 'create a new project'"
echo "   - Project name: prompt-evolver (or your choice)"
echo "   - Wait for configuration to complete"
echo "   - Press Ctrl+C to stop the dev server"
echo ""
echo "2. Deploy to production:"
echo "   npx convex deploy"
echo ""
echo "3. Get your deployment URL:"
echo "   It will look like: https://xxx.convex.cloud"
echo "   Save this URL!"
echo ""
echo "4. Update your .env.production file:"
echo "   echo 'NEXT_PUBLIC_CONVEX_URL=YOUR_URL_HERE' > .env.production"
echo ""
echo "5. Deploy frontend to Vercel:"
echo "   vercel --prod"
echo ""

# Try to get current project info
echo "Current Convex configuration:"
cat convex.json 2>/dev/null || echo "No convex.json found"
echo ""

echo "==================================="
echo "Ready to deploy!"
echo "Run: npx convex dev"
echo "==================================="
