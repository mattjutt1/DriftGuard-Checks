#!/usr/bin/env python3
"""
Simplified PromptWizard Qwen Training for RTX 2080
No complex dependencies - just core training
"""

import os
import json
import time
from typing import List, Dict

# Check if we have GPU
try:
    import torch
    if torch.cuda.is_available():
        print(f"✅ GPU Available: {torch.cuda.get_device_name(0)}")
        print(f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")
        device = "cuda"
    else:
        print("⚠️ No GPU detected, using CPU")
        device = "cpu"
except ImportError:
    print("❌ PyTorch not installed!")
    print("Install with: pip install torch --index-url https://download.pytorch.org/whl/cu121")
    exit(1)

def check_requirements():
    """Check if all requirements are installed"""
    required = {
        "transformers": "Transformers library for models",
        "datasets": "Datasets library for data loading",
        "peft": "PEFT for LoRA training",
        "accelerate": "Accelerate for training",
    }
    
    missing = []
    for package, description in required.items():
        try:
            __import__(package)
            print(f"✅ {package}: {description}")
        except ImportError:
            print(f"❌ {package}: {description}")
            missing.append(package)
    
    if missing:
        print("\n⚠️ Missing packages! Install with:")
        print(f"pip install {' '.join(missing)}")
        return False
    return True

def load_local_gsm8k(data_path: str, max_samples: int = 100) -> List[Dict]:
    """Load GSM8K data from local file"""
    data = []
    
    if os.path.exists(data_path):
        print(f"📚 Loading data from {data_path}")
        with open(data_path, "r") as f:
            for i, line in enumerate(f):
                if i >= max_samples:
                    break
                data.append(json.loads(line))
        print(f"   Loaded {len(data)} examples")
    else:
        print(f"❌ Data file not found: {data_path}")
        print("   Using dummy data for demo")
        # Create dummy data
        for i in range(10):
            data.append({
                "question": f"What is {i} + {i+1}?",
                "answer": f"The answer is {i + i + 1}",
                "full_solution": f"To solve {i} + {i+1}, we add the numbers: {i} + {i+1} = {i + i + 1}"
            })
    
    return data

def simple_train():
    """Simple training function"""
    print("\n" + "="*60)
    print("🧙 PromptWizard Simple Training")
    print("="*60)
    
    # Check requirements
    if not check_requirements():
        return
    
    # Now import after checking
    from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
    from peft import LoraConfig, get_peft_model, TaskType
    from datasets import Dataset
    
    # Load data
    train_data = load_local_gsm8k(
        "/home/matt/prompt-wizard/nextjs-app/data/gsm8k/train.jsonl",
        max_samples=100
    )
    
    # Select model
    print("\n🤖 Select model to train:")
    print("1. distilgpt2 (355MB - Very fast, good for testing)")
    print("2. microsoft/phi-2 (2.7B - Good quality, fits RTX 2080)")
    print("3. Qwen/Qwen2.5-0.5B-Instruct (500MB - Qwen smallest)")
    
    # Use environment variable or default to 1 for non-interactive
    import sys
    if sys.stdin.isatty():
        choice = input("\nEnter choice (1-3, default=1): ").strip() or "1"
    else:
        choice = os.environ.get("MODEL_CHOICE", "1")
        print(f"\nUsing choice: {choice} (non-interactive mode)")
    
    model_map = {
        "1": "distilgpt2",
        "2": "microsoft/phi-2",
        "3": "Qwen/Qwen2.5-0.5B-Instruct"
    }
    
    model_name = model_map.get(choice, "distilgpt2")
    print(f"\n✅ Using model: {model_name}")
    
    # Load tokenizer
    print("\n📝 Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load model
    print("🤖 Loading model...")
    if device == "cuda" and "Qwen" in model_name:
        # For Qwen models, use float16 on GPU
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
    else:
        # For other models
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map="auto",
            trust_remote_code=True
        )
    
    print(f"   Model loaded on {device}")
    
    # Configure LoRA
    print("\n⚙️ Configuring LoRA for efficient training...")
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=8,
        lora_alpha=16,
        lora_dropout=0.1,
        bias="none"
    )
    
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    # Prepare dataset
    print("\n📊 Preparing dataset...")
    
    def format_example(example):
        # 2025 best practice: Use chat template format for better instruction following
        if "Qwen" in model_name:
            # Qwen format
            text = f"<|im_start|>user\n{example['question']}<|im_end|>\n<|im_start|>assistant\n{example.get('full_solution', example['answer'])}<|im_end|>"
        else:
            # Standard format for GPT models
            text = f"### Question:\n{example['question']}\n\n### Answer:\n{example.get('full_solution', example['answer'])}"
        return {"text": text}
    
    dataset = Dataset.from_list([format_example(ex) for ex in train_data])
    
    def tokenize_function(examples):
        # Standard tokenization for causal language modeling
        tokenized = tokenizer(
            examples["text"],
            padding="max_length",
            truncation=True,
            max_length=256
        )
        
        # For causal LM training, labels are the same as input_ids
        # The model will internally shift them for next-token prediction
        tokenized["labels"] = tokenized["input_ids"].copy()
        
        return tokenized
    
    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    
    # Training arguments - 2025 optimized settings
    print("\n🎯 Setting up training (2025 optimized)...")
    training_args = TrainingArguments(
        output_dir="./simple-qwen-gsm8k",
        num_train_epochs=1,  # Just 1 epoch for demo
        per_device_train_batch_size=2 if device == "cuda" else 1,  # RTX 2080 can handle batch size 2
        gradient_accumulation_steps=4,  # Effective batch size of 8
        warmup_steps=10,
        logging_steps=5,
        save_steps=50,
        fp16=(device == "cuda"),  # Use mixed precision on GPU
        bf16=False,  # RTX 2080 doesn't support bf16
        gradient_checkpointing=False,  # Disabled for small models
        learning_rate=5e-5,  # Standard for LoRA fine-tuning
        weight_decay=0.01,  # Small weight decay
        optim="adamw_torch",  # 2025: Use PyTorch AdamW
        logging_dir="./logs",
        report_to=[],  # No reporting for simplicity
        max_steps=50,  # Limit steps for demo
        remove_unused_columns=False,  # Keep all columns
        dataloader_drop_last=True,  # Drop incomplete batches
    )
    
    # Create trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        tokenizer=tokenizer,
    )
    
    # Train!
    print("\n" + "="*60)
    print("🚀 Starting training...")
    print("   This is a demo with 50 steps")
    print("   Watch GPU with: nvidia-smi -l 1")
    print("="*60 + "\n")
    
    start_time = time.time()
    
    try:
        train_result = trainer.train()
        training_time = time.time() - start_time
        
        print(f"\n✅ Training completed in {training_time:.1f} seconds!")
        print(f"   Final loss: {train_result.training_loss:.4f}")
        
        # Save model
        print("\n💾 Saving model...")
        trainer.save_model("./simple-trained-model")
        tokenizer.save_pretrained("./simple-trained-model")
        print("   Model saved to ./simple-trained-model")
        
        # Quick test with 2025 generation parameters
        print("\n🧪 Quick test of trained model (2025 settings)...")
        
        # Use proper format based on model
        if "Qwen" in model_name:
            test_prompt = "<|im_start|>user\nWhat is 5 + 3?<|im_end|>\n<|im_start|>assistant\n"
        else:
            test_prompt = "### Question:\nWhat is 5 + 3?\n\n### Answer:\n"
            
        inputs = tokenizer(test_prompt, return_tensors="pt").to(device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=50,
                temperature=0.7,
                do_sample=True,
                top_p=0.95,  # 2025: Use nucleus sampling
                repetition_penalty=1.1,  # 2025: Prevent repetition
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        print(f"Prompt: {test_prompt}")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        print("This might be due to memory constraints or missing dependencies")
    
    print("\n✨ Demo complete!")

if __name__ == "__main__":
    simple_train()