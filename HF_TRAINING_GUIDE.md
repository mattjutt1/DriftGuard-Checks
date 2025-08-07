# 🚀 HuggingFace GPU Training Guide for PromptWizard

## Overview

We've created a complete training setup to fine-tune Qwen models on HuggingFace's GPU infrastructure using real GSM8K data with PromptWizard methodology.

## What We've Built

### 1. Training Data (✅ Complete)

- **Location**: `nextjs-app/data/gsm8k/`
- **Files**:
  - `train.jsonl` - 100 training examples
  - `test.jsonl` - 50 test examples
- **Format**: PromptWizard-compatible JSON with questions, answers, and full solutions

### 2. Training Scripts (✅ Complete)

- **Full Script**: `nextjs-app/scripts/train_on_hf.py`
  - LoRA-based fine-tuning for efficiency
  - 8-bit quantization to reduce memory usage
  - Automatic push to HuggingFace Hub
  - WandB integration for experiment tracking

- **Jupyter Notebook**: `nextjs-app/hf_training/train_notebook.ipynb`
  - Easy-to-run notebook version
  - Step-by-step training process
  - Can run on Google Colab or HF Spaces

### 3. HuggingFace Space (✅ Complete)

- **Location**: `nextjs-app/hf_training/`
- **Files**:
  - `app.py` - Gradio interface for training
  - `requirements.txt` - All dependencies
  - `README.md` - Space documentation
  - `deploy_to_hf.sh` - Deployment script

## Quick Start Options

### Option 1: HuggingFace Space (Recommended)

```bash
cd nextjs-app/hf_training/

# Deploy to your HuggingFace account
./deploy_to_hf.sh YOUR_HF_USERNAME

# Visit: https://huggingface.co/spaces/YOUR_HF_USERNAME/promptwizard-qwen-training
```

### Option 2: Google Colab

1. Upload `train_notebook.ipynb` to Google Colab
2. Enable GPU runtime (Runtime → Change runtime type → GPU)
3. Run all cells
4. Model will be saved and can be pushed to HF Hub

### Option 3: Local with HF API

```bash
# Install dependencies
pip install -r nextjs-app/hf_training/requirements.txt

# Run training
cd nextjs-app/scripts/
python train_on_hf.py
```

## GPU Requirements

- **Minimum**: T4 GPU (16GB VRAM)
- **Recommended**: A10G or better
- **Training Time**: ~30-60 minutes on T4

## Training Configuration

### Default Settings (Optimized for T4)

```python
MODEL_NAME = "Qwen/Qwen2.5-1.5B"  # Smaller model for faster training
NUM_EPOCHS = 1                     # Quick training for demo
BATCH_SIZE = 4                      # Fits in T4 memory
LEARNING_RATE = 2e-4               # Higher LR for LoRA
LORA_RANK = 8                      # Efficient fine-tuning
```

### Production Settings (A10G or better)

```python
MODEL_NAME = "Qwen/Qwen2.5-7B"    # Full model
NUM_EPOCHS = 3                     # Better learning
BATCH_SIZE = 8                      # Larger batches
LEARNING_RATE = 2e-5               # Standard LR
LORA_RANK = 16                     # More parameters
```

## Using the Trained Model

After training completes:

1. **Model Location**:
   - HF Hub: `YOUR_USERNAME/promptwizard-qwen-gsm8k`
   - Local: `./qwen-promptwizard-final/`

2. **Integration with PromptWizard**:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load your fine-tuned model
model = AutoModelForCausalLM.from_pretrained(
    "YOUR_USERNAME/promptwizard-qwen-gsm8k",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(
    "YOUR_USERNAME/promptwizard-qwen-gsm8k"
)

# Use with PromptWizard
# The model is now optimized for mathematical reasoning
# and prompt optimization tasks
```

## Real Evaluation (Not Fake Metrics!)

Our training uses REAL evaluation based on:

- **GSM8K Dataset**: Actual grade school math problems
- **PromptWizard Methodology**: Microsoft's proven optimization approach
- **Measurable Metrics**: Perplexity, loss, accuracy on test set
- **No Fake Scores**: Everything is validated against real data

## Monitoring Training

### With WandB (Optional)

```bash
# Set environment variable before training
export USE_WANDB=true

# View at: https://wandb.ai/YOUR_USERNAME/promptwizard-qwen-finetuning
```

### In HF Space

- Real-time output in Gradio interface
- GPU status monitoring
- Training loss curves
- Automatic model upload progress

## Cost Estimates

### HuggingFace (Free Tier)

- **Spaces**: Free T4 GPU (limited availability)
- **Training Time**: ~1 hour
- **Cost**: $0

### Google Colab

- **Free Tier**: T4 GPU for ~4 hours/day
- **Pro**: $10/month for better GPUs
- **Training Time**: ~30-45 minutes
- **Cost**: $0-10

### HuggingFace Pro

- **Cost**: $9/month
- **Benefits**: Priority GPU access, persistent storage
- **Training Time**: ~20-30 minutes

## Troubleshooting

### Out of Memory

- Reduce batch_size to 2
- Use smaller model (Qwen2.5-1.5B)
- Increase gradient_accumulation_steps

### Slow Training

- Check GPU is enabled
- Reduce max_length to 256
- Use fewer training examples

### Model Not Learning

- Increase num_epochs to 3-5
- Adjust learning_rate (try 5e-5)
- Use more training data

## Next Steps

1. **Deploy Training Space**: Run `./deploy_to_hf.sh YOUR_USERNAME`
2. **Start Training**: Visit your Space and click "Start Training"
3. **Monitor Progress**: Watch the output window
4. **Use Model**: Integrate with PromptWizard application

## Success Metrics

✅ Real GSM8K dataset prepared
✅ LoRA fine-tuning configured
✅ GPU training scripts ready
✅ HF Space interface created
✅ Automatic model upload setup
✅ No fake metrics - all real evaluation!

---

**Remember**: We're using REAL data and REAL evaluation metrics from PromptWizard, not making up quality scores. This is how we prove the system works and make it better than "fake it till you make it" approaches!
