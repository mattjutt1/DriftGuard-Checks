#!/usr/bin/env python3
"""
Multi-Stage Training for Prompt Enhancement Model
Based on PRD specifications for PromptEvolver 3.0
"""

import json
import logging
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

import torch
from datasets import Dataset, load_dataset
from peft import LoraConfig, PeftModel, TaskType, get_peft_model
from tqdm import tqdm
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class TrainingConfig:
    """Configuration for multi-stage training"""

    # Model settings
    model_name: str = "Qwen/Qwen2.5-3B-Instruct"  # Using smaller Qwen for RTX 2080

    # LoRA settings (as per PRD)
    lora_rank: int = 32
    lora_alpha: int = 64
    lora_dropout: float = 0.05
    target_modules: List[str] = None  # Will be set based on model architecture

    # Training settings
    learning_rate: float = 1e-5
    batch_size: int = 2  # Small batch for RTX 2080
    gradient_accumulation_steps: int = 8
    num_epochs_stage1: int = 1  # Reduced for demo
    num_epochs_stage2: int = 2
    num_epochs_stage3: int = 1
    max_seq_length: int = 2048  # Reduced for memory

    # Paths
    stage1_data: str = "data/stage1_foundational.jsonl"
    stage2_data: str = "data/stage2_specialization.jsonl"
    stage3_data: str = "data/gsm8k_reasoning.jsonl"  # Optional
    validation_data: str = "data/validation.jsonl"
    output_dir: str = "models/prompt_enhancer"

    # Hardware
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    fp16: bool = True  # Use mixed precision for memory efficiency

    def __post_init__(self):
        """Set target modules based on Qwen architecture"""
        if self.target_modules is None:
            # Qwen-specific modules as per PRD
            self.target_modules = [
                "q_proj",
                "k_proj",
                "v_proj",
                "o_proj",
                "gate_proj",
                "up_proj",
                "down_proj",
            ]


class PromptEnhancerTrainer:
    """Multi-stage trainer for prompt enhancement model"""

    def __init__(self, config: TrainingConfig):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.device_info()

    def device_info(self):
        """Print device information"""
        if torch.cuda.is_available():
            logger.info(f"✅ GPU: {torch.cuda.get_device_name(0)}")
            logger.info(
                f"   Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB"
            )

            # Clear cache
            torch.cuda.empty_cache()
            allocated = torch.cuda.memory_allocated() / 1e9
            reserved = torch.cuda.memory_reserved() / 1e9
            logger.info(f"   Allocated: {allocated:.1f}GB, Reserved: {reserved:.1f}GB")
        else:
            logger.warning("⚠️ No GPU detected, using CPU (will be very slow)")

    def load_model_and_tokenizer(self):
        """Load base model and tokenizer"""
        logger.info(f"📦 Loading model: {self.config.model_name}")

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.model_name, trust_remote_code=True, padding_side="left"
        )

        # Add padding token if not present
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Load model with memory optimization
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            torch_dtype=torch.float16 if self.config.fp16 else torch.float32,
            device_map="auto",
            trust_remote_code=True,
            low_cpu_mem_usage=True,
        )

        logger.info(f"✅ Model loaded: {self.model.num_parameters() / 1e9:.2f}B parameters")

    def prepare_lora_model(self, stage: int):
        """Configure LoRA for specific training stage"""
        logger.info(f"🔧 Configuring LoRA for Stage {stage}")

        # Adjust LoRA rank based on stage
        lora_rank = self.config.lora_rank if stage == 2 else self.config.lora_rank // 2

        lora_config = LoraConfig(
            r=lora_rank,
            lora_alpha=self.config.lora_alpha,
            lora_dropout=self.config.lora_dropout,
            bias="none",
            task_type=TaskType.CAUSAL_LM,
            target_modules=self.config.target_modules,
        )

        # Apply LoRA to model
        if stage == 1:
            self.model = get_peft_model(self.model, lora_config)
        else:
            # For subsequent stages, we might want to load previous adapter
            try:
                adapter_path = f"{self.config.output_dir}/stage{stage-1}"
                if os.path.exists(adapter_path):
                    logger.info(f"Loading adapter from stage {stage-1}")
                    self.model = PeftModel.from_pretrained(self.model, adapter_path)
            except:
                self.model = get_peft_model(self.model, lora_config)

        self.model.print_trainable_parameters()

    def load_dataset_for_stage(self, stage: int) -> Dataset:
        """Load appropriate dataset for training stage"""
        data_paths = {
            1: self.config.stage1_data,
            2: self.config.stage2_data,
            3: self.config.stage3_data,
        }

        data_path = data_paths.get(stage)
        if not os.path.exists(data_path) and stage == 3:
            logger.warning(f"Stage 3 data not found, skipping reasoning enhancement")
            return None

        logger.info(f"📚 Loading data for Stage {stage}: {data_path}")

        # Load JSONL data
        data = []
        with open(data_path, "r") as f:
            for line in f:
                data.append(json.loads(line))

        # Format for training
        formatted_data = []
        for item in data:
            # Create prompt-response format
            if "instruction" in item:
                text = f"""### Instruction:
{item['instruction']}

### Input:
{item.get('input', '')}

### Response:
{item.get('output', '')}"""
            else:
                # Fallback for other formats
                text = f"Q: {item.get('question', item.get('input', ''))} A: {item.get('answer', item.get('output', ''))}"

            formatted_data.append({"text": text})

        # Create dataset
        dataset = Dataset.from_list(formatted_data)

        # Tokenize
        def tokenize_function(examples):
            tokenized = self.tokenizer(
                examples["text"],
                truncation=True,
                padding="max_length",
                max_length=self.config.max_seq_length,
            )
            tokenized["labels"] = tokenized["input_ids"].copy()
            return tokenized

        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        logger.info(f"✅ Loaded {len(tokenized_dataset)} examples")

        return tokenized_dataset

    def train_stage(self, stage: int, dataset: Dataset, num_epochs: int):
        """Train a specific stage"""
        logger.info(f"\n{'='*50}")
        logger.info(f"🚀 Starting Stage {stage} Training")
        logger.info(f"{'='*50}")

        output_dir = f"{self.config.output_dir}/stage{stage}"

        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=self.config.batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            learning_rate=self.config.learning_rate,
            warmup_steps=100,
            logging_steps=10,
            save_steps=500,
            save_total_limit=2,
            fp16=self.config.fp16,
            gradient_checkpointing=True,  # Save memory
            report_to="none",  # Disable wandb/tensorboard for demo
            dataloader_num_workers=0,  # Avoid multiprocessing issues
            remove_unused_columns=False,
            prediction_loss_only=True,
        )

        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,
        )

        # Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=dataset,
            data_collator=data_collator,
        )

        # Train
        trainer.train()

        # Save adapter
        trainer.save_model(output_dir)
        logger.info(f"✅ Stage {stage} training complete. Model saved to {output_dir}")

        # Clear cache
        torch.cuda.empty_cache()

    def validate_model(self):
        """Validate model on schema compliance and quality metrics"""
        logger.info("\n📊 Validating Model Performance")

        # Load validation data
        val_data = []
        with open(self.config.validation_data, "r") as f:
            for line in f:
                val_data.append(json.loads(line))

        # Test schema compliance
        schema_compliant = 0
        total = min(10, len(val_data))  # Test on subset

        for item in val_data[:total]:
            prompt = f"Transform this vague prompt into a detailed prompt: {item['input']}"

            # Generate response
            inputs = self.tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids.to(self.config.device),
                    max_length=1024,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                )

            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Check for required tags
            required_tags = ["<OBJECTIVE>", "<CONTEXT>", "<OUTPUT_FORMAT>", "<EVALUATION_CRITERIA>"]
            if all(tag in response for tag in required_tags):
                schema_compliant += 1

        compliance_rate = (schema_compliant / total) * 100
        logger.info(f"✅ Schema Compliance: {compliance_rate:.1f}% ({schema_compliant}/{total})")

        # Per PRD: Must achieve ≥98% schema compliance
        if compliance_rate < 98:
            logger.warning(f"⚠️ Schema compliance below target (98%)")

        return compliance_rate

    def run_training_pipeline(self):
        """Execute complete multi-stage training pipeline"""
        logger.info("\n🧙 PromptWizard Multi-Stage Training Pipeline")
        logger.info("=" * 60)

        # Load base model
        self.load_model_and_tokenizer()

        # Stage 1: Foundational Instruction Tuning
        if os.path.exists(self.config.stage1_data):
            self.prepare_lora_model(stage=1)
            dataset = self.load_dataset_for_stage(1)
            self.train_stage(1, dataset, self.config.num_epochs_stage1)

        # Stage 2: Prompt Transformation Specialization
        if os.path.exists(self.config.stage2_data):
            self.prepare_lora_model(stage=2)
            dataset = self.load_dataset_for_stage(2)
            self.train_stage(2, dataset, self.config.num_epochs_stage2)

        # Stage 3: Reasoning Enhancement (Optional)
        if os.path.exists(self.config.stage3_data):
            self.prepare_lora_model(stage=3)
            dataset = self.load_dataset_for_stage(3)
            if dataset:
                self.train_stage(3, dataset, self.config.num_epochs_stage3)

        # Validation
        self.validate_model()

        logger.info("\n✅ Training pipeline complete!")
        logger.info(f"📁 Models saved in: {self.config.output_dir}")


def main():
    """Main training function"""
    # Check dependencies
    try:
        import datasets
        import peft
        import transformers

        logger.info(
            f"✅ Dependencies: transformers={transformers.__version__}, peft={peft.__version__}"
        )
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        logger.error("Install with: pip install transformers peft datasets accelerate")
        return

    # Create configuration
    config = TrainingConfig()

    # For RTX 2080 (11GB), we might need to use even smaller model
    if torch.cuda.is_available() and torch.cuda.get_device_properties(0).total_memory < 12e9:
        logger.warning("⚠️ Limited GPU memory detected. Using smaller model...")
        config.model_name = "Qwen/Qwen2.5-1.5B-Instruct"  # Even smaller for safety
        config.batch_size = 1
        config.max_seq_length = 1024

    # Run training
    trainer = PromptEnhancerTrainer(config)
    trainer.run_training_pipeline()


if __name__ == "__main__":
    main()
