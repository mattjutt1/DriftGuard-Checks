#!/bin/bash

echo "================================================"
echo "🧙 PromptWizard Local Training Setup"
echo "================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "train_local.py" ]; then
    echo "❌ Error: Please run this script from the hf_training directory"
    exit 1
fi

# Check for NVIDIA GPU
if ! command -v nvidia-smi &> /dev/null; then
    echo "⚠️  Warning: nvidia-smi not found. Make sure NVIDIA drivers are installed."
else
    echo "✅ GPU Status:"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    echo ""
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install PyTorch with CUDA support
echo "🔥 Installing PyTorch with CUDA support..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install other requirements
echo "📦 Installing requirements..."
pip install -r requirements_local.txt

# Verify installation
echo ""
echo "🔍 Verifying installation..."
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "import transformers; print(f'Transformers: {transformers.__version__}')"
python -c "import peft; print(f'PEFT: {peft.__version__}')"

echo ""
echo "================================================"
echo "✅ Setup complete!"
echo ""
echo "To start training, run:"
echo "  source venv/bin/activate"
echo "  python train_local.py"
echo ""
echo "Monitor GPU usage with:"
echo "  watch -n 1 nvidia-smi"
echo ""
echo "View training progress with:"
echo "  tensorboard --logdir ./logs"
echo "================================================"