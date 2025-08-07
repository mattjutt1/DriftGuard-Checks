# 🚀 PromptWizard Training Monitor

**Space URL**: <https://huggingface.co/spaces/unfiltrdfreedom/promptwizard-qwen-training>
**Status**: 🔨 Building...

## What to Expect When Ready

### Gradio Interface Layout

```
┌─────────────────────────────────────┐
│  🧙 PromptWizard Qwen Fine-tuning  │
├─────────────────────────────────────┤
│ Model: [Qwen/Qwen2.5-7B        ▼]  │
│ Epochs: [====3====]                │
│ Batch Size: [====4====]            │
│ Learning Rate: [2e-5]              │
│ □ Use Weights & Biases             │
│                                     │
│ [🚀 Start Training]                 │
├─────────────────────────────────────┤
│ Training Output:                   │
│ ┌─────────────────────────────────┐ │
│ │ GPU Status: T4, 15GB available  │ │
│ │ Loading GSM8K dataset...         │ │
│ │ Train samples: 100               │ │
│ │ Eval samples: 50                 │ │
│ │ Starting training...             │ │
│ │ Epoch 1/3: ████░░░░ 45%         │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

## Training Stages

### Stage 1: Initialization (2-3 min)

- Load Qwen model with LoRA
- Configure 8-bit quantization
- Load GSM8K dataset

### Stage 2: Training (30-60 min)

- Process 100 training examples
- Validate on 50 test examples
- Update model weights
- Show loss metrics

### Stage 3: Model Upload

- Save to HuggingFace Hub
- Model available at: `unfiltrdfreedom/promptwizard-qwen-gsm8k`

## Real Metrics We'll See

- **Perplexity**: Lower is better (target: <10)
- **Loss**: Should decrease over epochs
- **Learning Rate**: Follows cosine schedule
- **GPU Memory**: ~10-12GB usage with 8-bit

## Commands While Training

### Monitor GPU Usage

The interface will show real-time GPU metrics

### Expected Timeline

- Building: 2-3 minutes ⬅️ We are here
- Interface Ready: 1 minute
- Training Start: User triggered
- Training Time: 30-60 minutes
- Model Upload: 2-3 minutes

## Success Indicators

✅ Loss decreasing steadily
✅ No out-of-memory errors
✅ Validation loss not increasing (no overfitting)
✅ Model successfully pushed to Hub

---
Monitoring started at: 23:11:30
