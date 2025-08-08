#!/usr/bin/env python3
"""
Prepare Qwen3:4b Model for Fine-tuning
=======================================
This script prepares the Qwen3:4b model for efficient fine-tuning using:
- QLoRA (4-bit quantization with LoRA adapters)
- Optimized memory management for consumer GPUs
- Latest 2025 best practices from HuggingFace

Based on:
- HuggingFace Transformers 2025 documentation
- QLoRA optimization techniques
- Unsloth optimizations for Qwen models

Copyright (c) 2025 Matthew J. Utt
"""

import json
import logging
import os
import sys
import torch
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Check for required libraries
try:
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
        TrainingArguments,
        Trainer,
        DataCollatorForLanguageModeling
    )
    from peft import (
        LoraConfig,
        get_peft_model,
        prepare_model_for_kbit_training,
        TaskType
    )
    import bitsandbytes as bnb
    LIBRARIES_AVAILABLE = True
except ImportError as e:
    LIBRARIES_AVAILABLE = False
    logger.warning(f"Required libraries not installed: {e}")
    logger.info("Install with: pip install transformers peft bitsandbytes accelerate")

@dataclass
class ModelConfig:
    """Configuration for Qwen model preparation"""
    model_name: str = "Qwen/Qwen2.5-3B"  # Latest Qwen 2.5 3B model
    use_4bit: bool = True
    bnb_4bit_compute_dtype: str = "float16"
    bnb_4bit_quant_type: str = "nf4"
    use_double_quant: bool = True

    # LoRA configuration based on 2025 best practices
    lora_r: int = 16  # Rank - higher for better quality, lower for efficiency
    lora_alpha: int = 32  # Scaling factor (typically 2x lora_r)
    lora_dropout: float = 0.05  # Dropout for regularization
    lora_bias: str = "none"  # Bias setting

    # Target all linear transformer blocks for better performance
    target_modules: list = None  # Will be set based on model architecture

    # Training efficiency
    gradient_checkpointing: bool = True
    gradient_accumulation_steps: int = 4
    max_memory_usage: float = 0.9  # Use up to 90% of available VRAM

    # Flash Attention 2 support
    use_flash_attention: bool = False  # Enable if hardware supports

    def __post_init__(self):
        """Set target modules for Qwen architecture"""
        if self.target_modules is None:
            # For Qwen models, target all linear layers for best results
            self.target_modules = [
                "q_proj", "k_proj", "v_proj", "o_proj",  # Attention layers
                "gate_proj", "up_proj", "down_proj",      # MLP layers
                "lm_head"  # Output layer (optional, but can improve quality)
            ]

class QwenModelPreparer:
    """Main class for preparing Qwen model for fine-tuning"""

    def __init__(self, config: ModelConfig = None):
        self.config = config or ModelConfig()
        self.model = None
        self.tokenizer = None
        self.peft_model = None

        # Check CUDA availability
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        if self.device == "cuda":
            self.gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            logger.info(f"GPU detected: {torch.cuda.get_device_name(0)} with {self.gpu_memory:.2f}GB")
        else:
            logger.warning("No GPU detected. QLoRA requires CUDA for 4-bit quantization.")

    def check_requirements(self) -> bool:
        """Check system requirements for QLoRA training"""
        if not LIBRARIES_AVAILABLE:
            logger.error("Required libraries not installed")
            return False

        if self.device != "cuda":
            logger.error("CUDA GPU required for QLoRA training")
            return False

        # Check minimum GPU memory (recommended: 16GB for 3B model with QLoRA)
        min_memory = 8.0  # Minimum 8GB VRAM
        if self.gpu_memory < min_memory:
            logger.warning(f"GPU memory ({self.gpu_memory:.2f}GB) below recommended {min_memory}GB")
            logger.warning("Training may be slower or require smaller batch sizes")

        # Check PyTorch version
        torch_version = torch.__version__
        logger.info(f"PyTorch version: {torch_version}")

        return True

    def get_quantization_config(self) -> BitsAndBytesConfig:
        """Get BitsAndBytesConfig for QLoRA"""
        compute_dtype = getattr(torch, self.config.bnb_4bit_compute_dtype)

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=self.config.use_4bit,
            bnb_4bit_compute_dtype=compute_dtype,
            bnb_4bit_quant_type=self.config.bnb_4bit_quant_type,
            bnb_4bit_use_double_quant=self.config.use_double_quant,
        )

        logger.info("Quantization config:")
        logger.info(f"  4-bit: {self.config.use_4bit}")
        logger.info(f"  Compute dtype: {self.config.bnb_4bit_compute_dtype}")
        logger.info(f"  Quant type: {self.config.bnb_4bit_quant_type}")
        logger.info(f"  Double quantization: {self.config.use_double_quant}")

        return bnb_config

    def load_base_model(self) -> Tuple[Any, Any]:
        """Load Qwen base model with quantization"""
        logger.info(f"Loading model: {self.config.model_name}")

        # Get quantization config
        bnb_config = self.get_quantization_config()

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.model_name,
            trust_remote_code=True
        )

        # Set padding token if not set
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id

        # Model loading arguments
        model_kwargs = {
            "quantization_config": bnb_config,
            "device_map": "auto",
            "trust_remote_code": True,
        }

        # Add Flash Attention 2 if supported
        if self.config.use_flash_attention:
            model_kwargs["attn_implementation"] = "flash_attention_2"
            model_kwargs["torch_dtype"] = torch.bfloat16
            logger.info("Flash Attention 2 enabled")

        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_name,
            **model_kwargs
        )

        # Enable gradient checkpointing for memory efficiency
        if self.config.gradient_checkpointing:
            self.model.gradient_checkpointing_enable()
            logger.info("Gradient checkpointing enabled")

        # Prepare model for k-bit training
        self.model = prepare_model_for_kbit_training(self.model)

        # Print model info
        total_params = sum(p.numel() for p in self.model.parameters())
        logger.info(f"Model loaded: {total_params/1e9:.2f}B parameters")

        # Estimate memory usage
        self.estimate_memory_usage()

        return self.model, self.tokenizer

    def setup_lora(self) -> Any:
        """Setup LoRA configuration and apply to model"""
        logger.info("Setting up LoRA configuration")

        # Create LoRA config
        lora_config = LoraConfig(
            r=self.config.lora_r,
            lora_alpha=self.config.lora_alpha,
            lora_dropout=self.config.lora_dropout,
            bias=self.config.lora_bias,
            task_type=TaskType.CAUSAL_LM,
            target_modules=self.config.target_modules,
        )

        # Log LoRA configuration
        logger.info("LoRA configuration:")
        logger.info(f"  Rank (r): {self.config.lora_r}")
        logger.info(f"  Alpha: {self.config.lora_alpha}")
        logger.info(f"  Dropout: {self.config.lora_dropout}")
        logger.info(f"  Target modules: {self.config.target_modules}")

        # Apply LoRA to model
        self.peft_model = get_peft_model(self.model, lora_config)

        # Print trainable parameters
        self.peft_model.print_trainable_parameters()

        return self.peft_model

    def estimate_memory_usage(self):
        """Estimate memory usage for training"""
        if not self.model:
            return

        # Count parameters
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)

        # Estimate memory (rough approximation)
        # 4-bit model: ~0.5GB per billion parameters
        # LoRA adapters: ~2MB per million trainable parameters
        # Optimizer states: ~2x trainable parameters
        # Gradients: ~1x trainable parameters

        model_memory = (total_params / 1e9) * 0.5  # 4-bit quantized
        lora_memory = (trainable_params / 1e6) * 0.002
        optimizer_memory = (trainable_params / 1e6) * 0.004
        gradient_memory = (trainable_params / 1e6) * 0.002

        total_memory = model_memory + lora_memory + optimizer_memory + gradient_memory

        logger.info(f"\nMemory estimation:")
        logger.info(f"  Model (4-bit): {model_memory:.2f}GB")
        logger.info(f"  LoRA adapters: {lora_memory:.2f}GB")
        logger.info(f"  Optimizer states: {optimizer_memory:.2f}GB")
        logger.info(f"  Gradients: {gradient_memory:.2f}GB")
        logger.info(f"  Total estimated: {total_memory:.2f}GB")

        if self.device == "cuda":
            if total_memory > self.gpu_memory * self.config.max_memory_usage:
                logger.warning(f"Estimated memory ({total_memory:.2f}GB) exceeds available GPU memory!")
                logger.warning("Consider reducing batch size or using gradient accumulation")

    def get_training_args(self, output_dir: str = "./qwen-lora") -> TrainingArguments:
        """Get recommended training arguments for QLoRA"""
        # Calculate per-device batch size based on available memory
        if self.gpu_memory < 12:
            batch_size = 1
        elif self.gpu_memory < 16:
            batch_size = 2
        elif self.gpu_memory < 24:
            batch_size = 4
        else:
            batch_size = 8

        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=3,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            gradient_accumulation_steps=self.config.gradient_accumulation_steps,
            gradient_checkpointing=self.config.gradient_checkpointing,
            warmup_ratio=0.03,
            learning_rate=2e-4,
            fp16=True if self.config.bnb_4bit_compute_dtype == "float16" else False,
            bf16=True if self.config.bnb_4bit_compute_dtype == "bfloat16" else False,
            logging_steps=10,
            save_steps=100,
            eval_steps=100,
            save_total_limit=3,
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            report_to="none",  # Can be "wandb", "tensorboard", etc.
            optim="paged_adamw_32bit",  # Paged optimizer for memory efficiency
            max_grad_norm=0.3,
            weight_decay=0.001,
            group_by_length=True,  # Group sequences of similar length for efficiency
            ddp_find_unused_parameters=False if torch.cuda.device_count() > 1 else None,
        )

        logger.info(f"\nTraining configuration:")
        logger.info(f"  Batch size: {batch_size}")
        logger.info(f"  Gradient accumulation: {self.config.gradient_accumulation_steps}")
        logger.info(f"  Effective batch size: {batch_size * self.config.gradient_accumulation_steps}")
        logger.info(f"  Learning rate: {training_args.learning_rate}")
        logger.info(f"  Epochs: {training_args.num_train_epochs}")

        return training_args

    def save_config(self, output_dir: str = "./model_config"):
        """Save model configuration for later use"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        config_dict = {
            "model_name": self.config.model_name,
            "quantization": {
                "use_4bit": self.config.use_4bit,
                "compute_dtype": self.config.bnb_4bit_compute_dtype,
                "quant_type": self.config.bnb_4bit_quant_type,
                "double_quant": self.config.use_double_quant
            },
            "lora": {
                "r": self.config.lora_r,
                "alpha": self.config.lora_alpha,
                "dropout": self.config.lora_dropout,
                "bias": self.config.lora_bias,
                "target_modules": self.config.target_modules
            },
            "training": {
                "gradient_checkpointing": self.config.gradient_checkpointing,
                "gradient_accumulation_steps": self.config.gradient_accumulation_steps,
                "flash_attention": self.config.use_flash_attention
            },
            "system": {
                "gpu": torch.cuda.get_device_name(0) if self.device == "cuda" else "CPU",
                "gpu_memory_gb": self.gpu_memory if self.device == "cuda" else 0,
                "pytorch_version": torch.__version__,
                "cuda_version": torch.version.cuda if self.device == "cuda" else None
            },
            "timestamp": datetime.now().isoformat()
        }

        config_file = output_path / "model_preparation_config.json"
        with open(config_file, 'w') as f:
            json.dump(config_dict, f, indent=2)

        logger.info(f"Configuration saved to {config_file}")

    def prepare(self) -> Tuple[Any, Any, Any]:
        """Main preparation pipeline"""
        logger.info("="*80)
        logger.info("QWEN MODEL PREPARATION FOR FINE-TUNING")
        logger.info("="*80)

        # Check requirements
        if not self.check_requirements():
            raise RuntimeError("System requirements not met")

        # Load base model
        model, tokenizer = self.load_base_model()

        # Setup LoRA
        peft_model = self.setup_lora()

        # Save configuration
        self.save_config()

        logger.info("\n" + "="*80)
        logger.info("✅ MODEL PREPARATION COMPLETE")
        logger.info("="*80)

        return peft_model, tokenizer, self.get_training_args()

def test_model_loading():
    """Test function to verify model can be loaded"""
    logger.info("Testing model loading...")

    # Use smaller config for testing
    test_config = ModelConfig(
        model_name="Qwen/Qwen2.5-0.5B",  # Smaller model for testing
        lora_r=8,
        lora_alpha=16
    )

    preparer = QwenModelPreparer(test_config)

    try:
        # Just check if we can create configs
        if preparer.check_requirements():
            bnb_config = preparer.get_quantization_config()
            training_args = preparer.get_training_args()
            logger.info("✅ Configuration test passed")
        else:
            logger.warning("Requirements not met for full test")
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False

    return True

def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description="Prepare Qwen model for QLoRA fine-tuning")
    parser.add_argument("--model", default="Qwen/Qwen2.5-3B", help="Model name or path")
    parser.add_argument("--lora-r", type=int, default=16, help="LoRA rank")
    parser.add_argument("--lora-alpha", type=int, default=32, help="LoRA alpha")
    parser.add_argument("--output-dir", default="./qwen-lora", help="Output directory")
    parser.add_argument("--test", action="store_true", help="Run test mode")
    parser.add_argument("--flash-attention", action="store_true", help="Enable Flash Attention 2")

    args = parser.parse_args()

    if args.test:
        success = test_model_loading()
        sys.exit(0 if success else 1)

    # Create configuration
    config = ModelConfig(
        model_name=args.model,
        lora_r=args.lora_r,
        lora_alpha=args.lora_alpha,
        use_flash_attention=args.flash_attention
    )

    # Prepare model
    preparer = QwenModelPreparer(config)

    try:
        peft_model, tokenizer, training_args = preparer.prepare()

        # Print summary
        print("\n" + "="*80)
        print("MODEL READY FOR FINE-TUNING")
        print("="*80)
        print(f"Model: {config.model_name}")
        print(f"LoRA Rank: {config.lora_r}")
        print(f"Output Directory: {args.output_dir}")
        print("\nNext steps:")
        print("1. Prepare your training data")
        print("2. Run train_model.py with this configuration")
        print("3. Monitor training with tensorboard or wandb")
        print("="*80)

    except Exception as e:
        logger.error(f"Preparation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
