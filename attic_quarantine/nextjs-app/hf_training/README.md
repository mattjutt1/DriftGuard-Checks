---
title: PromptWizard Qwen Training
emoji: 🧙
colorFrom: purple
colorTo: blue
sdk: gradio
sdk_version: 4.14.0
app_file: app.py
pinned: false
license: mit
---

# PromptWizard Qwen Fine-tuning

This Space fine-tunes Qwen models using the GSM8K dataset with PromptWizard optimization methodology.

## Features

- **GPU-Accelerated Training**: Uses HuggingFace's GPU infrastructure for fast training
- **LoRA Fine-tuning**: Efficient parameter-efficient fine-tuning
- **GSM8K Dataset**: High-quality mathematical reasoning dataset
- **PromptWizard Integration**: Uses Microsoft's PromptWizard evaluation methodology
- **Auto Push to Hub**: Trained models are automatically uploaded to HuggingFace Hub

## How to Use

1. Select your base model (default: Qwen/Qwen2.5-7B)
2. Configure training parameters:
   - Number of epochs (3-5 recommended)
   - Batch size (4-8 for T4 GPU)
   - Learning rate (2e-5 is a good default)
3. Click "Start Training" and monitor the output
4. The trained model will be pushed to HuggingFace Hub

## Training Data

The Space uses the GSM8K dataset, which contains grade school math problems. The data is formatted according to PromptWizard specifications for optimal prompt optimization.

## Model Output

After training, the model will be available at:
- HuggingFace Hub: `your-username/promptwizard-qwen-gsm8k`
- Local download: Available in the Space's output directory

## Technical Details

- **Base Model**: Qwen2.5-7B (or your choice)
- **Training Method**: LoRA with rank 16
- **Quantization**: 8-bit for memory efficiency
- **Mixed Precision**: FP16 for faster training
- **Gradient Checkpointing**: Enabled for memory savings

## Resource Requirements

- **GPU**: T4 or better recommended
- **Memory**: 16GB+ GPU memory
- **Training Time**: ~30-60 minutes on T4

## Citation

If you use this training setup, please cite:

```bibtex
@misc{promptwizard2024,
  title={PromptWizard: Task-Aware Prompt Optimization},
  author={Microsoft Research},
  year={2024}
}
```