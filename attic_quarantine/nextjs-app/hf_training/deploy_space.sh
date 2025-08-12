#!/bin/bash

# Deploy PromptWizard training to HuggingFace Space
# This will create a public Space that can train the model

SPACE_NAME="promptwizard-qwen-training"
HF_USERNAME="promptwizard"  # You can change this to your username

echo "=========================================="
echo "🚀 Deploying to HuggingFace Space"
echo "=========================================="
echo ""
echo "Space will be created at:"
echo "https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME"
echo ""

# Initialize git repo in hf_training directory
cd /home/matt/prompt-wizard/nextjs-app/hf_training

if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
    git config user.email "promptwizard@example.com"
    git config user.name "PromptWizard Bot"
fi

# Add all files
echo "📝 Adding files to git..."
git add -A

# Create commit
echo "💾 Creating commit..."
git commit -m "Deploy PromptWizard Qwen training Space with GSM8K data" || echo "No changes to commit"

# Add HuggingFace remote
echo "🔗 Setting up HuggingFace remote..."
git remote remove origin 2>/dev/null || true
git remote add origin https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME

echo ""
echo "=========================================="
echo "📋 Space Contents:"
echo "=========================================="
ls -la

echo ""
echo "=========================================="
echo "🎯 Next Steps:"
echo "=========================================="
echo ""
echo "1. Create a HuggingFace account at https://huggingface.co/join"
echo "2. Get your access token from https://huggingface.co/settings/tokens"
echo "3. Create the Space at https://huggingface.co/new-space"
echo "   - Name: $SPACE_NAME"
echo "   - SDK: Gradio"
echo "   - Hardware: GPU (T4 small)"
echo ""
echo "4. Push the code:"
echo "   cd /home/matt/prompt-wizard/nextjs-app/hf_training"
echo "   git push origin main"
echo ""
echo "5. Monitor training at:"
echo "   https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME"
echo ""
echo "The Space will:"
echo "  ✅ Use real GSM8K data (100 train, 50 test)"
echo "  ✅ Fine-tune Qwen with LoRA"
echo "  ✅ Run on HuggingFace T4 GPU"
echo "  ✅ Show progress in Gradio interface"
echo "  ✅ Push trained model to HF Hub"
echo ""
echo "=========================================="