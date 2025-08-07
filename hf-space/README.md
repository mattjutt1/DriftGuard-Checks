---
title: PromptEvolver Qwen3-30B
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 5.0.0
app_file: app.py
pinned: false
models:
  - Qwen/Qwen3-30B-A3B-Instruct-2507
---

# PromptEvolver - Qwen3-30B-A3B MoE (2025)

Powerful prompt optimization using Microsoft PromptWizard methodology with Qwen3's latest 30B parameter Mixture of Experts model (256K context).

## Features
- **Qwen3-30B-A3B MoE Model**: 30B parameters total, only 3B active per request
- **PromptWizard Methodology**: Microsoft's proven optimization techniques
- **Multiple Modes**: Quick, Balanced, and Thorough optimization
- **Batch Processing**: Optimize multiple prompts at once
- **REST API**: Easy integration with any application

## API Usage

### Single Prompt
```python
import requests

response = requests.post(
    "https://[space-url]/api/optimize",
    json={"data": ["Your prompt", "Task description", "balanced", 0.7]}
)
result = response.json()["data"][0]
```

### Batch Processing
```python
response = requests.post(
    "https://[space-url]/api/batch",
    json={"data": ["Prompt1\\n---\\nPrompt2", "Task", "balanced"]}
)
results = response.json()["data"][0]
```

## Configuration
- **ZeroGPU**: Enabled for free GPU access
- **Model**: Qwen/Qwen3-30B-A3B
- **Framework**: Transformers + Gradio