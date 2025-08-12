#!/usr/bin/env python3
"""
PromptWizard Qwen Training Script for RTX 2080 (8GB VRAM)
Optimized for local training with real GSM8K data
"""

import torch
from transformers import (
    AutoModelForCausalLM, 
    AutoTokenizer, 
    Trainer, 
    TrainingArguments,
    BitsAndBytesConfig
)
from datasets import load_dataset, Dataset
from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training
import json
import os
from tqdm import tqdm
import time

def print_gpu_info():
    """Check GPU availability and memory"""
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"✅ GPU Available: {gpu_name}")
        print(f"   Memory: {gpu_memory:.1f}GB")
        return True
    else:
        print("❌ No GPU detected!")
        return False

def load_gsm8k_data(num_train=500, num_test=100):
    """Load GSM8K dataset"""
    print("\n📚 Loading GSM8K dataset...")
    
    # Try local data first
    train_data = []
    test_data = []
    
    local_train = "/home/matt/prompt-wizard/nextjs-app/data/gsm8k/train.jsonl"
    local_test = "/home/matt/prompt-wizard/nextjs-app/data/gsm8k/test.jsonl"
    
    if os.path.exists(local_train):
        print("   Using local GSM8K data...")
        with open(local_train, "r") as f:
            for i, line in enumerate(f):
                if i >= num_train:
                    break
                train_data.append(json.loads(line))
        
        with open(local_test, "r") as f:
            for i, line in enumerate(f):
                if i >= num_test:
                    break
                test_data.append(json.loads(line))
    else:
        print("   Downloading GSM8K from HuggingFace...")
        dataset = load_dataset("openai/gsm8k", "main")
        train_data = dataset["train"].select(range(min(num_train, len(dataset["train"]))))
        test_data = dataset["test"].select(range(min(num_test, len(dataset["test"]))))
    
    print(f"   Loaded {len(train_data)} training examples")
    print(f"   Loaded {len(test_data)} test examples")
    
    return train_data, test_data

def format_prompt(item):
    """Format GSM8K example for training"""
    # Use Qwen chat template
    prompt = f"""<|im_start|>system
You are a helpful assistant that solves math problems step by step.<|im_end|>
<|im_start|>user
{item.get('question', '')}<|im_end|>
<|im_start|>assistant
{item.get('full_solution', item.get('answer', ''))}<|im_end|>"""
    return {"text": prompt}

def setup_model_and_tokenizer(model_name="Qwen/Qwen2.5-1.5B-Instruct"):
    """Load model with 4-bit quantization for RTX 2080"""
    print(f"\n🤖 Loading {model_name}...")
    print("   Using 4-bit quantization for 8GB VRAM...")
    
    # 4-bit quantization config for RTX 2080
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load model with quantization
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.float16,
    )
    
    # Prepare for k-bit training
    model = prepare_model_for_kbit_training(model)
    
    # Print memory usage
    memory_used = torch.cuda.memory_allocated() / 1e9
    print(f"   Model loaded! GPU memory used: {memory_used:.1f}GB")
    
    return model, tokenizer

def setup_lora(model):
    """Configure LoRA for efficient training"""
    print("\n⚙️ Configuring LoRA...")
    
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=16,  # Rank 16 for good performance
        lora_alpha=32,
        lora_dropout=0.1,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj"
        ],
        bias="none",
    )
    
    model = get_peft_model(model, lora_config)
    
    # Print trainable parameters
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"   Trainable parameters: {trainable_params:,} ({100 * trainable_params / total_params:.2f}%)")
    print(f"   Total parameters: {total_params:,}")
    
    return model

def train_model(model, tokenizer, train_data, test_data):
    """Train the model with PromptWizard methodology"""
    print("\n🚀 Starting training...")
    
    # Format datasets
    if isinstance(train_data, list):
        train_dataset = Dataset.from_list([format_prompt(item) for item in train_data])
    else:
        train_dataset = train_data.map(format_prompt)
    
    if isinstance(test_data, list):
        eval_dataset = Dataset.from_list([format_prompt(item) for item in test_data])
    else:
        eval_dataset = test_data.map(format_prompt)
    
    # Tokenize datasets
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            padding="max_length",
            truncation=True,
            max_length=512,  # Reasonable length for GSM8K
        )
    
    print("   Tokenizing datasets...")
    train_dataset = train_dataset.map(tokenize_function, batched=True)
    eval_dataset = eval_dataset.map(tokenize_function, batched=True)
    
    # Training arguments optimized for RTX 2080
    training_args = TrainingArguments(
        output_dir="./qwen-promptwizard-gsm8k",
        num_train_epochs=3,
        per_device_train_batch_size=2,  # Small batch for 8GB VRAM
        per_device_eval_batch_size=2,
        gradient_accumulation_steps=8,  # Effective batch size of 16
        warmup_steps=100,
        logging_steps=10,
        save_steps=500,
        eval_steps=100,
        evaluation_strategy="steps",
        save_strategy="steps",
        load_best_model_at_end=True,
        fp16=True,  # Mixed precision for speed
        gradient_checkpointing=True,  # Save memory
        optim="paged_adamw_8bit",  # 8-bit optimizer
        learning_rate=2e-4,
        max_grad_norm=0.3,
        warmup_ratio=0.03,
        lr_scheduler_type="cosine",
        report_to=["tensorboard"],  # Local tensorboard logging
        logging_dir="./logs",
    )
    
    # Create trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=tokenizer,
    )
    
    # Train!
    print("\n" + "="*60)
    print("Training started! This will take ~30-60 minutes on RTX 2080")
    print("Watch GPU usage with: nvidia-smi -l 1")
    print("View training progress with: tensorboard --logdir ./logs")
    print("="*60 + "\n")
    
    start_time = time.time()
    train_result = trainer.train()
    training_time = time.time() - start_time
    
    print(f"\n✅ Training completed in {training_time/60:.1f} minutes!")
    print(f"   Final loss: {train_result.training_loss:.4f}")
    
    # Save the model
    print("\n💾 Saving model...")
    trainer.save_model("./qwen-promptwizard-final")
    tokenizer.save_pretrained("./qwen-promptwizard-final")
    
    return trainer

def test_model(model, tokenizer):
    """Test the trained model with a sample problem"""
    print("\n🧪 Testing trained model...")
    
    test_problem = "Sarah has 5 apples. She buys 3 more apples from the store. How many apples does she have now?"
    
    inputs = tokenizer(
        f"<|im_start|>user\n{test_problem}<|im_end|>\n<|im_start|>assistant\n",
        return_tensors="pt"
    ).to("cuda")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=200,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id,
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    print(f"\nProblem: {test_problem}")
    print(f"Model response: {response}")

def main():
    """Main training pipeline"""
    print("="*60)
    print("🧙 PromptWizard Qwen Training for RTX 2080")
    print("="*60)
    
    # Check GPU
    if not print_gpu_info():
        print("ERROR: GPU required for training!")
        return
    
    # Load data
    train_data, test_data = load_gsm8k_data(num_train=500, num_test=100)
    
    # Setup model (you can change this)
    model_choices = [
        "Qwen/Qwen2.5-0.5B-Instruct",  # Tiny - fast training
        "Qwen/Qwen2.5-1.5B-Instruct",  # Small - good for RTX 2080
        "Qwen/Qwen2.5-3B-Instruct",    # Medium - might be tight on memory
    ]
    
    print("\nSelect model to train:")
    for i, model_name in enumerate(model_choices):
        print(f"  {i+1}. {model_name}")
    
    choice = input("\nEnter choice (1-3, default=2): ").strip() or "2"
    model_name = model_choices[int(choice)-1]
    
    # Load model and tokenizer
    model, tokenizer = setup_model_and_tokenizer(model_name)
    
    # Setup LoRA
    model = setup_lora(model)
    
    # Train
    trainer = train_model(model, tokenizer, train_data, test_data)
    
    # Test
    test_model(model, tokenizer)
    
    print("\n✨ Training complete! Model saved to ./qwen-promptwizard-final")
    print("   You can load it with: AutoModelForCausalLM.from_pretrained('./qwen-promptwizard-final')")

if __name__ == "__main__":
    main()