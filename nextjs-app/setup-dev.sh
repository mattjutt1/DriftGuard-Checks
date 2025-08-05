#!/bin/bash

echo "🚀 Setting up PromptEvolver Development Environment"
echo "=================================================="

# Check if Convex CLI is installed
if ! command -v convex &> /dev/null; then
    echo "📦 Installing Convex CLI..."
    npm install -g convex
fi

# Initialize Convex if not already done
if [ ! -f "convex.json" ]; then
    echo "🔧 Initializing Convex project..."
    npx convex dev --once
else
    echo "✅ Convex project already initialized"
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Start Convex development server
echo "🔄 Starting Convex development server..."
echo "This will:"
echo "  1. Deploy your Convex functions"
echo "  2. Generate API types"
echo "  3. Provide your deployment URL"
echo ""
echo "After this completes:"
echo "  1. Copy the deployment URL to .env.local"
echo "  2. Run 'npm run dev' in another terminal"
echo "  3. Test the advanced UI!"
echo ""

npx convex dev