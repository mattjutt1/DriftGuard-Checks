#!/bin/bash

# Deploy training Space to HuggingFace
# Usage: ./deploy_to_hf.sh <your-hf-username>

if [ $# -eq 0 ]; then
    echo "Usage: ./deploy_to_hf.sh <your-hf-username>"
    exit 1
fi

HF_USERNAME=$1
SPACE_NAME="promptwizard-qwen-training"

echo "Deploying to HuggingFace Space: $HF_USERNAME/$SPACE_NAME"

# Initialize git repo if not already
if [ ! -d .git ]; then
    git init
    git remote add origin https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME
fi

# Add all files
git add .
git commit -m "Deploy PromptWizard Qwen training Space"

# Push to HuggingFace
git push origin main

echo "Space deployed to: https://huggingface.co/spaces/$HF_USERNAME/$SPACE_NAME"
echo ""
echo "Next steps:"
echo "1. Visit your Space URL"
echo "2. Wait for it to build (~2-3 minutes)"
echo "3. Start training with GPU support!"