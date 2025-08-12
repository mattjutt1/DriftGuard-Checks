#!/bin/bash

echo "================================================"
echo "🧙 PromptWizard Quick Local Training Setup"
echo "================================================"
echo ""

# Check for NVIDIA GPU
echo "🔍 Checking for GPU..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    echo ""
else
    echo "⚠️ No NVIDIA GPU detected"
    echo ""
fi

# Use system Python 3
echo "🐍 Using system Python 3..."
python3 --version

# Install packages with break-system-packages flag
echo ""
echo "📦 Installing PyTorch with CUDA support..."
echo "This will take a few minutes..."
pip3 install --user --break-system-packages torch --index-url https://download.pytorch.org/whl/cu121

echo ""
echo "📦 Installing training packages..."
pip3 install --user --break-system-packages transformers datasets peft accelerate tqdm

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start training, run:"
echo "  python3 simple_train.py"
echo ""
echo "Monitor GPU usage with:"
echo "  watch -n 1 nvidia-smi"
echo ""
echo "================================================"