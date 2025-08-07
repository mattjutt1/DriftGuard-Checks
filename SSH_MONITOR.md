# 🔧 HuggingFace Space SSH Access Guide

**Space**: https://huggingface.co/spaces/unfiltrdfreedom/promptwizard-qwen-training  
**Developer Mode**: ✅ ENABLED  
**Hardware**: Zero GPU (A10G)

## SSH Connection (Once Available)

When the Space is running with dev mode, you'll get:
- SSH command like: `ssh user@hostname -p PORT`
- Password or SSH key
- VS Code remote connection option

## What We Can Do via SSH:

### 1. Check GPU Status
```bash
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"
```

### 2. Monitor Training Live
```bash
# See running processes
ps aux | grep python

# Watch GPU usage
watch -n 1 nvidia-smi

# Check logs
tail -f training.log
```

### 3. Debug Issues
```bash
# Test imports
python -c "import spaces; print('Spaces module OK')"
python -c "from peft import LoraConfig; print('PEFT OK')"

# Check data files
ls -la data/
wc -l data/train.jsonl
```

### 4. Run Training Manually
```bash
# Activate environment
source /app/venv/bin/activate

# Run training script directly
python train_on_hf.py

# Or test Gradio app
python app.py
```

## Zero GPU Testing

With Zero GPU, the GPU is allocated dynamically when the @spaces.GPU decorated function runs:

```python
# This should show GPU info when inside decorated function
@spaces.GPU(duration=300)
def test_gpu():
    import torch
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")
    return "GPU test complete"
```

## Files to Check via SSH:

1. **App Status**: `/app/app.py`
2. **Requirements**: `/app/requirements.txt`
3. **Data Files**: `/app/data/train.jsonl`
4. **Logs**: Check for any `.log` files
5. **GPU Access**: Test if Zero GPU decorator works

## Common SSH Commands:

```bash
# Check Space environment
pwd
ls -la
env | grep -E "HF|SPACE|GPU"

# Test Zero GPU allocation
python -c "
import spaces
import torch

@spaces.GPU
def test():
    return torch.cuda.is_available()

print(test())
"

# Monitor resource usage
htop
df -h
free -h
```

## Troubleshooting via SSH:

### If GPU not available:
```bash
# Check if spaces module loaded
python -c "import spaces; print(dir(spaces))"

# Verify Zero GPU hardware setting
env | grep HARDWARE
```

### If training fails:
```bash
# Check Python version
python --version

# Verify all packages
pip list | grep -E "torch|transformers|peft|gradio"

# Test data loading
python -c "
import json
with open('data/train.jsonl', 'r') as f:
    data = [json.loads(line) for line in f]
print(f'Loaded {len(data)} examples')
"
```

---

**Status**: Waiting for Space to finish building...  
**Next**: SSH in and verify Zero GPU works with real GSM8K data!