#!/usr/bin/env python3
"""
PromptEvolver 3.0 - Main Training Script with QLoRA
====================================================
Train Qwen model for prompt optimization using QLoRA (4-bit quantization).
Implements the latest 2025 best practices from HuggingFace PEFT and TRL.

Copyright (c) 2025 Matthew J. Utt
"""

import os
import sys
import json
import yaml
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

# HuggingFace imports
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    EarlyStoppingCallback,
    set_seed,
)

from datasets import Dataset, load_dataset, load_from_disk
from accelerate import Accelerator
from accelerate.utils import gather_object

# PEFT imports for QLoRA
from peft import (
    LoraConfig,
    TaskType,
    get_peft_model,
    prepare_model_for_kbit_training,
    PeftModel,
)

# TRL for supervised fine-tuning
from trl import SFTTrainer, SFTConfig, DataCollatorForCompletionOnlyLM

# Monitoring imports
import wandb
from tensorboardX import SummaryWriter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ModelArguments:
    """Arguments pertaining to which model/config/tokenizer we are going to fine-tune."""

    model_name_or_path: str = field(
        default="Qwen/Qwen2.5-3B",
        metadata={"help": "Path to pretrained model or model identifier"}
    )
    tokenizer_name: Optional[str] = field(
        default=None,
        metadata={"help": "Pretrained tokenizer name or path if different from model_name"}
    )
    cache_dir: Optional[str] = field(
        default="./cache",
        metadata={"help": "Directory to store downloaded models"}
    )
    trust_remote_code: bool = field(
        default=True,
        metadata={"help": "Trust remote code from model hub"}
    )
    revision: str = field(
        default="main",
        metadata={"help": "Model revision to use"}
    )


@dataclass
class DataArguments:
    """Arguments pertaining to the data used for training and evaluation."""

    train_data_path: str = field(
        default="./data/processed/splits/train_latest.json",
        metadata={"help": "Path to training data"}
    )
    val_data_path: str = field(
        default="./data/processed/splits/val_latest.json",
        metadata={"help": "Path to validation data"}
    )
    max_seq_length: int = field(
        default=512,
        metadata={"help": "Maximum sequence length"}
    )
    preprocessing_num_workers: int = field(
        default=4,
        metadata={"help": "Number of processes to use for preprocessing"}
    )
    prompt_template: str = field(
        default="### Instruction:\nOptimize the following prompt:\n{original_prompt}\n\n### Response:\n{enhanced_prompt}",
        metadata={"help": "Template for formatting prompts"}
    )


@dataclass
class TrainingConfig:
    """Training configuration arguments."""

    # Output
    output_dir: str = field(
        default="./models/qwen-promptevolver",
        metadata={"help": "Output directory for model checkpoints"}
    )

    # Training hyperparameters
    num_train_epochs: int = field(default=3)
    per_device_train_batch_size: int = field(default=4)
    per_device_eval_batch_size: int = field(default=4)
    gradient_accumulation_steps: int = field(default=4)
    learning_rate: float = field(default=2e-4)
    warmup_ratio: float = field(default=0.03)
    weight_decay: float = field(default=0.001)
    max_grad_norm: float = field(default=0.3)

    # Optimizer
    optim: str = field(default="paged_adamw_32bit")
    lr_scheduler_type: str = field(default="cosine")

    # Logging and saving
    logging_steps: int = field(default=10)
    save_strategy: str = field(default="steps")
    save_steps: int = field(default=100)
    save_total_limit: int = field(default=3)
    eval_strategy: str = field(default="steps")
    eval_steps: int = field(default=100)

    # Precision and memory
    fp16: bool = field(default=False)
    bf16: bool = field(default=True)
    gradient_checkpointing: bool = field(default=True)

    # Early stopping
    load_best_model_at_end: bool = field(default=True)
    metric_for_best_model: str = field(default="eval_loss")
    greater_is_better: bool = field(default=False)
    early_stopping_patience: int = field(default=3)

    # Monitoring
    report_to: str = field(default="tensorboard")
    run_name: str = field(default="qwen-promptevolver-qlora")

    # Seed
    seed: int = field(default=42)


@dataclass
class QLoRAConfig:
    """QLoRA specific configuration."""

    # Quantization
    load_in_4bit: bool = field(default=True)
    bnb_4bit_compute_dtype: str = field(default="float16")
    bnb_4bit_quant_type: str = field(default="nf4")
    bnb_4bit_use_double_quant: bool = field(default=True)

    # LoRA parameters
    lora_r: int = field(default=16)
    lora_alpha: int = field(default=32)
    lora_dropout: float = field(default=0.05)
    lora_bias: str = field(default="none")
    lora_target_modules: List[str] = field(
        default_factory=lambda: ["q_proj", "k_proj", "v_proj", "o_proj",
                                  "gate_proj", "up_proj", "down_proj"]
    )
    task_type: str = field(default="CAUSAL_LM")


class PromptOptimizationDataset:
    """Dataset class for prompt optimization training."""

    def __init__(self, data_path: str, tokenizer, max_length: int = 512,
                 prompt_template: str = None):
        """Initialize dataset."""
        self.data_path = data_path
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.prompt_template = prompt_template

        # Load data
        self.data = self._load_data()

    def _load_data(self) -> List[Dict]:
        """Load training data from JSON file."""
        with open(self.data_path, 'r') as f:
            data = json.load(f)

        logger.info(f"Loaded {len(data)} examples from {self.data_path}")
        return data

    def format_prompt(self, example: Dict) -> str:
        """Format a single example using the prompt template."""
        if self.prompt_template:
            return self.prompt_template.format(
                original_prompt=example.get('original_prompt', ''),
                enhanced_prompt=example.get('enhanced_prompt', '')
            )
        else:
            # Fallback format
            original = example.get('original_prompt', '')
            enhanced = example.get('enhanced_prompt', '')
            return f"### Original:\n{original}\n\n### Enhanced:\n{enhanced}"

    def prepare_dataset(self) -> Dataset:
        """Prepare HuggingFace dataset."""
        # Format all examples
        formatted_texts = [self.format_prompt(ex) for ex in self.data]

        # Create dataset
        dataset = Dataset.from_dict({"text": formatted_texts})

        return dataset


class QLoRATrainer:
    """Main trainer class for QLoRA fine-tuning."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize trainer with configuration."""
        self.config_path = config_path or "configs/training_config.yaml"
        self.config = self._load_config()

        # Initialize components
        self.accelerator = Accelerator()
        self.device = self.accelerator.device

        # Set seed for reproducibility
        set_seed(self.config.get('training', {}).get('seed', 42))

    def _load_config(self) -> Dict:
        """Load training configuration from YAML."""
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Loaded configuration from {self.config_path}")
        return config

    def setup_quantization(self) -> BitsAndBytesConfig:
        """Setup 4-bit quantization configuration."""
        quant_config = self.config.get('quantization', {})

        compute_dtype = getattr(torch, quant_config.get('bnb_4bit_compute_dtype', 'float16'))

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=quant_config.get('load_in_4bit', True),
            bnb_4bit_compute_dtype=compute_dtype,
            bnb_4bit_quant_type=quant_config.get('bnb_4bit_quant_type', 'nf4'),
            bnb_4bit_use_double_quant=quant_config.get('bnb_4bit_use_double_quant', True),
        )

        logger.info("Configured 4-bit quantization with NF4 and double quantization")
        return bnb_config

    def load_model_and_tokenizer(self) -> Tuple[Any, Any]:
        """Load the base model and tokenizer."""
        model_config = self.config.get('model', {})
        model_name = model_config.get('name', 'Qwen/Qwen2.5-3B')

        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=model_config.get('trust_remote_code', True),
            padding_side="right"
        )

        # Set padding token if not set
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            tokenizer.pad_token_id = tokenizer.eos_token_id

        # Setup quantization
        bnb_config = self.setup_quantization()

        # Load model with quantization
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=model_config.get('trust_remote_code', True),
            torch_dtype=torch.float16,
        )

        # Prepare model for k-bit training
        model = prepare_model_for_kbit_training(model)

        logger.info(f"Loaded model: {model_name}")
        logger.info(f"Model memory footprint: {model.get_memory_footprint() / 1e9:.2f} GB")

        return model, tokenizer

    def setup_lora(self, model) -> Any:
        """Setup LoRA configuration and apply to model."""
        lora_config = self.config.get('lora', {})

        config = LoraConfig(
            r=lora_config.get('r', 16),
            lora_alpha=lora_config.get('lora_alpha', 32),
            lora_dropout=lora_config.get('lora_dropout', 0.05),
            bias=lora_config.get('bias', 'none'),
            task_type=TaskType.CAUSAL_LM,
            target_modules=lora_config.get('target_modules',
                                          ["q_proj", "k_proj", "v_proj", "o_proj",
                                           "gate_proj", "up_proj", "down_proj"]),
        )

        # Apply LoRA to model
        model = get_peft_model(model, config)

        # Print trainable parameters
        model.print_trainable_parameters()

        return model

    def prepare_datasets(self, tokenizer) -> Tuple[Dataset, Dataset]:
        """Prepare training and validation datasets."""
        dataset_config = self.config.get('dataset', {})

        # Load training data
        train_dataset = PromptOptimizationDataset(
            data_path=dataset_config.get('train_path', './data/processed/splits/train_latest.json'),
            tokenizer=tokenizer,
            max_length=dataset_config.get('max_length', 512),
            prompt_template=dataset_config.get('prompt_template')
        ).prepare_dataset()

        # Load validation data
        val_dataset = PromptOptimizationDataset(
            data_path=dataset_config.get('validation_path', './data/processed/splits/val_latest.json'),
            tokenizer=tokenizer,
            max_length=dataset_config.get('max_length', 512),
            prompt_template=dataset_config.get('prompt_template')
        ).prepare_dataset()

        logger.info(f"Training samples: {len(train_dataset)}")
        logger.info(f"Validation samples: {len(val_dataset)}")

        return train_dataset, val_dataset

    def setup_training_arguments(self) -> SFTConfig:
        """Setup training arguments for SFTTrainer."""
        train_config = self.config.get('training', {})

        # Determine precision settings
        fp16 = train_config.get('fp16', False)
        bf16 = train_config.get('bf16', True)

        # Ensure only one precision is set
        if bf16:
            fp16 = False

        training_args = SFTConfig(
            output_dir=train_config.get('output_dir', './models/qwen-promptevolver'),
            num_train_epochs=train_config.get('num_train_epochs', 3),
            per_device_train_batch_size=train_config.get('per_device_train_batch_size', 4),
            per_device_eval_batch_size=train_config.get('per_device_eval_batch_size', 4),
            gradient_accumulation_steps=train_config.get('gradient_accumulation_steps', 4),
            learning_rate=float(train_config.get('learning_rate', 2e-4)),
            warmup_ratio=train_config.get('warmup_ratio', 0.03),
            weight_decay=train_config.get('weight_decay', 0.001),
            max_grad_norm=train_config.get('max_grad_norm', 0.3),

            # Optimizer
            optim=train_config.get('optim', 'paged_adamw_32bit'),
            lr_scheduler_type=train_config.get('lr_scheduler_type', 'cosine'),

            # Logging and saving
            logging_dir=train_config.get('logging_dir', './logs'),
            logging_steps=train_config.get('logging_steps', 10),
            logging_first_step=train_config.get('logging_first_step', True),
            save_strategy=train_config.get('save_strategy', 'steps'),
            save_steps=train_config.get('save_steps', 100),
            save_total_limit=train_config.get('save_total_limit', 3),
            save_safetensors=train_config.get('save_safetensors', True),

            # Evaluation
            eval_strategy=train_config.get('eval_strategy', 'steps'),
            eval_steps=train_config.get('eval_steps', 100),
            metric_for_best_model=train_config.get('metric_for_best_model', 'eval_loss'),
            greater_is_better=train_config.get('greater_is_better', False),
            load_best_model_at_end=train_config.get('load_best_model_at_end', True),

            # Precision and memory
            fp16=fp16,
            bf16=bf16,
            tf32=train_config.get('tf32', True),
            gradient_checkpointing=train_config.get('gradient_checkpointing', True),
            gradient_checkpointing_kwargs={
                "use_reentrant": False
            },

            # Data loading
            dataloader_drop_last=train_config.get('dataloader_drop_last', False),
            dataloader_num_workers=train_config.get('dataloader_num_workers', 4),
            dataloader_pin_memory=train_config.get('dataloader_pin_memory', True),

            # Tracking
            report_to=train_config.get('report_to', 'tensorboard'),
            run_name=train_config.get('run_name', 'qwen-promptevolver-qlora'),

            # Seed
            seed=train_config.get('seed', 42),
            data_seed=train_config.get('data_seed', 42),

            # Dataset configuration
            max_seq_length=self.config.get('dataset', {}).get('max_length', 512),
            dataset_text_field="text",
            packing=False,  # Disable packing for prompt optimization

            # Push to hub (optional)
            push_to_hub=train_config.get('push_to_hub', False),
            hub_model_id=train_config.get('hub_model_id'),
            hub_strategy=train_config.get('hub_strategy', 'every_save'),
        )

        return training_args

    def train(self):
        """Main training loop."""
        logger.info("Starting QLoRA training for PromptEvolver 3.0")

        # Load model and tokenizer
        model, tokenizer = self.load_model_and_tokenizer()

        # Setup LoRA
        model = self.setup_lora(model)

        # Prepare datasets
        train_dataset, val_dataset = self.prepare_datasets(tokenizer)

        # Setup training arguments
        training_args = self.setup_training_arguments()

        # Setup callbacks
        callbacks = []

        # Add early stopping if configured
        if self.config.get('training', {}).get('early_stopping', True):
            callbacks.append(
                EarlyStoppingCallback(
                    early_stopping_patience=self.config.get('training', {}).get('early_stopping_patience', 3),
                    early_stopping_threshold=self.config.get('training', {}).get('early_stopping_threshold', 0.001)
                )
            )

        # Initialize trainer
        trainer = SFTTrainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            tokenizer=tokenizer,
            packing=False,
            callbacks=callbacks,
        )

        # Log initial metrics
        logger.info("Starting training...")
        logger.info(f"Total training steps: {trainer.state.max_steps}")
        logger.info(f"Effective batch size: {training_args.per_device_train_batch_size * training_args.gradient_accumulation_steps}")

        # Train the model
        train_result = trainer.train()

        # Save the final model
        logger.info("Saving final model...")
        trainer.save_model()

        # Save training metrics
        metrics_path = Path(training_args.output_dir) / "training_metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump(train_result.metrics, f, indent=2)

        logger.info(f"Training completed! Model saved to {training_args.output_dir}")

        # Evaluate on validation set
        if val_dataset:
            logger.info("Running final evaluation...")
            eval_results = trainer.evaluate()

            # Save evaluation metrics
            eval_path = Path(training_args.output_dir) / "eval_metrics.json"
            with open(eval_path, 'w') as f:
                json.dump(eval_results, f, indent=2)

            logger.info(f"Evaluation results: {eval_results}")

        return trainer, train_result

    def save_adapter_config(self, trainer):
        """Save adapter configuration for later use."""
        output_dir = Path(trainer.args.output_dir)
        adapter_config_path = output_dir / "adapter_config.json"

        # Get LoRA config from the model
        if hasattr(trainer.model, 'peft_config'):
            config_dict = trainer.model.peft_config.to_dict()
            with open(adapter_config_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
            logger.info(f"Saved adapter config to {adapter_config_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Train PromptEvolver with QLoRA")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/training_config.yaml",
        help="Path to training configuration file"
    )
    parser.add_argument(
        "--resume",
        type=str,
        default=None,
        help="Path to checkpoint to resume training from"
    )
    parser.add_argument(
        "--local_rank",
        type=int,
        default=-1,
        help="Local rank for distributed training"
    )

    args = parser.parse_args()

    # Initialize trainer
    trainer_manager = QLoRATrainer(config_path=args.config)

    try:
        # Run training
        trainer, results = trainer_manager.train()

        # Save adapter configuration
        trainer_manager.save_adapter_config(trainer)

        logger.info("Training completed successfully!")

    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
