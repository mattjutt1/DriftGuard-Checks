#!/usr/bin/env python3
"""
Train Qwen model on HuggingFace infrastructure using GSM8K dataset
This script is designed to run on HuggingFace Spaces or HF Training API
"""

import json
import os
import torch
from datasets import Dataset, load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType
import numpy as np
from typing import Dict, List
import wandb

# Initialize wandb for experiment tracking (optional)
USE_WANDB = os.getenv("USE_WANDB", "false").lower() == "true"
if USE_WANDB:
    wandb.init(project="promptwizard-qwen-finetuning")

class PromptWizardDataset:
    """Dataset handler for PromptWizard-style training data"""
    
    def __init__(self, data_path: str, tokenizer, max_length: int = 512):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.data = self.load_data(data_path)
    
    def load_data(self, path: str) -> List[Dict]:
        """Load JSONL data from file"""
        data = []
        with open(path, 'r') as f:
            for line in f:
                data.append(json.loads(line))
        return data
    
    def format_prompt(self, item: Dict) -> str:
        """Format data item into a prompt for training"""
        # Use PromptWizard-style formatting
        prompt = f"""<|system|>
You are a mathematics expert. Your task is to solve grade school math problems step by step.
<|user|>
{item['question']}
<|assistant|>
Let me solve this step by step.

{item['full_solution']}"""
        return prompt
    
    def tokenize_function(self, examples):
        """Tokenize examples for training"""
        prompts = [self.format_prompt(item) for item in examples]
        
        model_inputs = self.tokenizer(
            prompts,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        # Set labels same as input_ids for causal LM
        model_inputs["labels"] = model_inputs["input_ids"].clone()
        
        return model_inputs

def prepare_model_for_training(model_name: str = "Qwen/Qwen2.5-7B"):
    """Prepare model and tokenizer for training with LoRA"""
    
    print(f"Loading model: {model_name}")
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=True,
        padding_side="left"
    )
    
    # Add padding token if not present
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load model with quantization for efficiency
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        trust_remote_code=True,
        torch_dtype=torch.float16,
        device_map="auto",
        load_in_8bit=True  # Use 8-bit quantization to reduce memory
    )
    
    # Configure LoRA for efficient fine-tuning
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=16,  # LoRA rank
        lora_alpha=32,
        lora_dropout=0.1,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],  # Target attention layers
        bias="none"
    )
    
    # Apply LoRA
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()
    
    return model, tokenizer

def create_datasets(tokenizer):
    """Create train and eval datasets from prepared data"""
    
    train_path = "/home/matt/prompt-wizard/nextjs-app/data/gsm8k/train.jsonl"
    test_path = "/home/matt/prompt-wizard/nextjs-app/data/gsm8k/test.jsonl"
    
    # For HF Spaces, we might need to download from HF Hub instead
    if not os.path.exists(train_path):
        print("Local data not found, downloading from HF Hub...")
        dataset = load_dataset("openai/gsm8k", "main")
        
        # Process and save locally
        train_data = []
        for item in dataset['train'][:100]:  # Use subset for demo
            answer_parts = item['answer'].split('####')
            final_answer = answer_parts[-1].strip() if len(answer_parts) >= 2 else item['answer'].strip()
            train_data.append({
                "question": item['question'],
                "answer": final_answer,
                "full_solution": item['answer']
            })
        
        test_data = []
        for item in dataset['test'][:50]:  # Use subset for demo
            answer_parts = item['answer'].split('####')
            final_answer = answer_parts[-1].strip() if len(answer_parts) >= 2 else item['answer'].strip()
            test_data.append({
                "question": item['question'],
                "answer": final_answer,
                "full_solution": item['answer']
            })
    else:
        # Load from local files
        train_handler = PromptWizardDataset(train_path, tokenizer)
        test_handler = PromptWizardDataset(test_path, tokenizer)
        train_data = train_handler.data
        test_data = test_handler.data
    
    # Format prompts
    def format_for_training(item):
        prompt = f"""<|system|>
You are a mathematics expert. Your task is to solve grade school math problems step by step.
<|user|>
{item['question']}
<|assistant|>
Let me solve this step by step.

{item['full_solution']}"""
        return {"text": prompt}
    
    train_texts = [format_for_training(item) for item in train_data]
    test_texts = [format_for_training(item) for item in test_data]
    
    # Create HF datasets
    train_dataset = Dataset.from_list(train_texts)
    eval_dataset = Dataset.from_list(test_texts)
    
    # Tokenize datasets
    def tokenize_function(examples):
        return tokenizer(
            examples["text"],
            padding="max_length",
            truncation=True,
            max_length=512
        )
    
    train_dataset = train_dataset.map(tokenize_function, batched=True)
    eval_dataset = eval_dataset.map(tokenize_function, batched=True)
    
    return train_dataset, eval_dataset

def compute_metrics(eval_pred):
    """Compute training metrics"""
    predictions, labels = eval_pred
    
    # Calculate perplexity
    loss = np.mean(predictions)
    perplexity = np.exp(loss)
    
    return {
        "perplexity": perplexity
    }

def main():
    """Main training function"""
    
    print("="*60)
    print("PromptWizard Qwen Fine-tuning on HuggingFace")
    print("="*60)
    
    # Configuration
    MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-7B")
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./qwen-promptwizard-finetuned")
    NUM_EPOCHS = int(os.getenv("NUM_EPOCHS", "3"))
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "4"))
    LEARNING_RATE = float(os.getenv("LEARNING_RATE", "2e-5"))
    
    # Prepare model and tokenizer
    model, tokenizer = prepare_model_for_training(MODEL_NAME)
    
    # Create datasets
    print("\nPreparing datasets...")
    train_dataset, eval_dataset = create_datasets(tokenizer)
    
    print(f"Train dataset size: {len(train_dataset)}")
    print(f"Eval dataset size: {len(eval_dataset)}")
    
    # Training arguments optimized for HF infrastructure
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=4,  # Simulate larger batch size
        warmup_steps=100,
        weight_decay=0.01,
        logging_dir="./logs",
        logging_steps=10,
        evaluation_strategy="steps",
        eval_steps=50,
        save_strategy="steps",
        save_steps=100,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        fp16=True,  # Use mixed precision for faster training
        push_to_hub=True,  # Push to HF Hub when done
        hub_model_id="promptwizard-qwen-gsm8k",
        hub_strategy="end",
        report_to=["wandb"] if USE_WANDB else [],
        gradient_checkpointing=True,  # Save memory
        optim="adamw_torch",
        learning_rate=LEARNING_RATE,
        lr_scheduler_type="cosine",
    )
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,  # Causal LM, not masked LM
        pad_to_multiple_of=8
    )
    
    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )
    
    # Start training
    print("\nStarting training...")
    print(f"Using {torch.cuda.device_count()} GPUs")
    
    trainer.train()
    
    # Save the final model
    print("\nSaving model...")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    
    # Push to HF Hub
    if training_args.push_to_hub:
        print("\nPushing to HuggingFace Hub...")
        trainer.push_to_hub()
    
    print("\n" + "="*60)
    print("Training complete!")
    print(f"Model saved to: {OUTPUT_DIR}")
    print("="*60)
    
    # Evaluate final performance
    print("\nFinal evaluation:")
    eval_results = trainer.evaluate()
    for key, value in eval_results.items():
        print(f"{key}: {value:.4f}")
    
    return trainer, model, tokenizer

if __name__ == "__main__":
    trainer, model, tokenizer = main()