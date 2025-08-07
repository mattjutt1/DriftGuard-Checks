#!/usr/bin/env python3
"""
PromptEvolver 3.0 - Checkpoint Manager
=======================================
Manage model checkpoints, merging LoRA adapters, and deployment preparation.

Copyright (c) 2025 Matthew J. Utt
"""

import os
import sys
import json
import shutil
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import hashlib

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)
from peft import PeftModel, PeftConfig
from safetensors.torch import save_file, load_file
from huggingface_hub import HfApi, create_repo, upload_folder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CheckpointManager:
    """Manage model checkpoints and deployments."""

    def __init__(self, base_model_path: str = None, output_dir: str = "./models"):
        """
        Initialize checkpoint manager.

        Args:
            base_model_path: Path to base model
            output_dir: Directory for saving outputs
        """
        self.base_model_path = base_model_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.checkpoints = []
        self.best_checkpoint = None

    def list_checkpoints(self, model_dir: str) -> List[Dict[str, Any]]:
        """
        List all available checkpoints.

        Args:
            model_dir: Directory containing checkpoints

        Returns:
            List of checkpoint information
        """
        model_dir = Path(model_dir)
        checkpoints = []

        # Find all checkpoint directories
        checkpoint_dirs = sorted([d for d in model_dir.glob("checkpoint-*") if d.is_dir()])

        for ckpt_dir in checkpoint_dirs:
            ckpt_info = {
                'name': ckpt_dir.name,
                'path': str(ckpt_dir),
                'step': int(ckpt_dir.name.split('-')[-1]) if '-' in ckpt_dir.name else 0,
                'created': datetime.fromtimestamp(ckpt_dir.stat().st_mtime),
                'size_mb': sum(f.stat().st_size for f in ckpt_dir.rglob("*") if f.is_file()) / (1024 * 1024)
            }

            # Try to load training state
            trainer_state_path = ckpt_dir / "trainer_state.json"
            if trainer_state_path.exists():
                with open(trainer_state_path, 'r') as f:
                    trainer_state = json.load(f)
                    ckpt_info['best_metric'] = trainer_state.get('best_metric')
                    ckpt_info['best_model_checkpoint'] = trainer_state.get('best_model_checkpoint')
                    ckpt_info['epoch'] = trainer_state.get('epoch')

            checkpoints.append(ckpt_info)

        self.checkpoints = checkpoints

        # Identify best checkpoint
        if checkpoints:
            # Try to find the best checkpoint based on metrics
            for ckpt in checkpoints:
                if ckpt.get('best_model_checkpoint'):
                    self.best_checkpoint = ckpt
                    break

            # If no best checkpoint marked, use the latest
            if not self.best_checkpoint:
                self.best_checkpoint = max(checkpoints, key=lambda x: x['created'])

        return checkpoints

    def load_checkpoint(self, checkpoint_path: str, load_in_8bit: bool = False) -> Tuple[Any, Any]:
        """
        Load a checkpoint with its tokenizer.

        Args:
            checkpoint_path: Path to checkpoint
            load_in_8bit: Whether to load in 8-bit precision

        Returns:
            Tuple of (model, tokenizer)
        """
        checkpoint_path = Path(checkpoint_path)

        logger.info(f"Loading checkpoint from {checkpoint_path}")

        # Load adapter configuration
        adapter_config_path = checkpoint_path / "adapter_config.json"
        if not adapter_config_path.exists():
            raise FileNotFoundError(f"No adapter config found at {adapter_config_path}")

        # Load PEFT config
        peft_config = PeftConfig.from_pretrained(str(checkpoint_path))

        # Determine base model path
        base_model = self.base_model_path or peft_config.base_model_name_or_path

        logger.info(f"Loading base model: {base_model}")

        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            base_model,
            trust_remote_code=True
        )

        # Setup quantization if needed
        device_map = "auto"
        if load_in_8bit:
            model = AutoModelForCausalLM.from_pretrained(
                base_model,
                load_in_8bit=True,
                device_map=device_map,
                trust_remote_code=True,
            )
        else:
            model = AutoModelForCausalLM.from_pretrained(
                base_model,
                torch_dtype=torch.float16,
                device_map=device_map,
                trust_remote_code=True,
            )

        # Load LoRA weights
        model = PeftModel.from_pretrained(model, str(checkpoint_path))

        logger.info("Checkpoint loaded successfully")

        return model, tokenizer

    def merge_lora_weights(self, checkpoint_path: str, output_path: str = None,
                          push_to_hub: bool = False, hub_model_id: str = None):
        """
        Merge LoRA weights with base model.

        Args:
            checkpoint_path: Path to LoRA checkpoint
            output_path: Path to save merged model
            push_to_hub: Whether to push to HuggingFace Hub
            hub_model_id: HuggingFace Hub model ID
        """
        checkpoint_path = Path(checkpoint_path)

        if output_path is None:
            output_path = self.output_dir / f"merged_{checkpoint_path.name}"
        else:
            output_path = Path(output_path)

        logger.info(f"Merging LoRA weights from {checkpoint_path}")

        # Load model and tokenizer
        model, tokenizer = self.load_checkpoint(checkpoint_path)

        # Merge LoRA weights
        logger.info("Merging LoRA weights with base model...")
        model = model.merge_and_unload()

        # Save merged model
        logger.info(f"Saving merged model to {output_path}")
        output_path.mkdir(parents=True, exist_ok=True)

        model.save_pretrained(output_path, safe_serialization=True)
        tokenizer.save_pretrained(output_path)

        # Save merge metadata
        metadata = {
            'merged_at': datetime.now().isoformat(),
            'base_model': self.base_model_path or model.config._name_or_path,
            'lora_checkpoint': str(checkpoint_path),
            'merge_method': 'standard',
        }

        with open(output_path / "merge_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.info("Model merged and saved successfully")

        # Push to hub if requested
        if push_to_hub and hub_model_id:
            self.push_to_hub(output_path, hub_model_id)

        return output_path

    def convert_to_gguf(self, model_path: str, output_path: str = None,
                       quantization: str = "q4_k_m"):
        """
        Convert model to GGUF format for llama.cpp.

        Args:
            model_path: Path to model
            output_path: Output path for GGUF file
            quantization: Quantization method
        """
        model_path = Path(model_path)

        if output_path is None:
            output_path = self.output_dir / f"{model_path.name}.gguf"
        else:
            output_path = Path(output_path)

        logger.info(f"Converting model to GGUF format: {model_path}")

        # This requires llama.cpp's convert.py script
        # For now, we'll just document the process
        logger.warning("GGUF conversion requires llama.cpp tools. Please run:")
        logger.warning(f"python llama.cpp/convert.py {model_path} --outtype {quantization} --outfile {output_path}")

        # Create a conversion script for reference
        script_path = self.output_dir / "convert_to_gguf.sh"
        with open(script_path, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write("# Script to convert model to GGUF format\n")
            f.write("# Requires llama.cpp repository\n\n")
            f.write("# Clone llama.cpp if not present\n")
            f.write("if [ ! -d 'llama.cpp' ]; then\n")
            f.write("    git clone https://github.com/ggerganov/llama.cpp\n")
            f.write("    cd llama.cpp && make && cd ..\n")
            f.write("fi\n\n")
            f.write(f"# Convert model\n")
            f.write(f"python llama.cpp/convert.py {model_path} \\\n")
            f.write(f"    --outtype {quantization} \\\n")
            f.write(f"    --outfile {output_path}\n")

        script_path.chmod(0o755)
        logger.info(f"Conversion script saved to {script_path}")

        return output_path

    def prepare_for_deployment(self, checkpoint_path: str, deployment_type: str = "api"):
        """
        Prepare checkpoint for deployment.

        Args:
            checkpoint_path: Path to checkpoint
            deployment_type: Type of deployment (api, edge, cloud)
        """
        checkpoint_path = Path(checkpoint_path)
        deployment_dir = self.output_dir / f"deployment_{checkpoint_path.name}"
        deployment_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Preparing checkpoint for {deployment_type} deployment")

        if deployment_type == "api":
            # Prepare for API deployment (FastAPI/vLLM)
            self._prepare_api_deployment(checkpoint_path, deployment_dir)
        elif deployment_type == "edge":
            # Prepare for edge deployment (ONNX/TensorRT)
            self._prepare_edge_deployment(checkpoint_path, deployment_dir)
        elif deployment_type == "cloud":
            # Prepare for cloud deployment (SageMaker/Vertex AI)
            self._prepare_cloud_deployment(checkpoint_path, deployment_dir)
        else:
            raise ValueError(f"Unknown deployment type: {deployment_type}")

        logger.info(f"Deployment package prepared at {deployment_dir}")
        return deployment_dir

    def _prepare_api_deployment(self, checkpoint_path: Path, output_dir: Path):
        """Prepare for API deployment."""
        # Copy checkpoint
        shutil.copytree(checkpoint_path, output_dir / "model", dirs_exist_ok=True)

        # Create deployment config
        config = {
            'model_path': './model',
            'model_type': 'lora',
            'base_model': self.base_model_path,
            'inference_config': {
                'max_length': 512,
                'temperature': 0.7,
                'top_p': 0.9,
                'do_sample': True,
            },
            'api_config': {
                'host': '0.0.0.0',
                'port': 8000,
                'workers': 1,
            }
        }

        with open(output_dir / "deployment_config.json", 'w') as f:
            json.dump(config, f, indent=2)

        # Create Dockerfile
        dockerfile = """FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy model and config
COPY model/ ./model/
COPY deployment_config.json .
COPY server.py .

# Expose port
EXPOSE 8000

# Run server
CMD ["python", "server.py"]
"""
        with open(output_dir / "Dockerfile", 'w') as f:
            f.write(dockerfile)

        # Create requirements.txt
        requirements = """torch>=2.1.0
transformers>=4.36.0
peft>=0.7.0
fastapi>=0.104.0
uvicorn>=0.24.0
"""
        with open(output_dir / "requirements.txt", 'w') as f:
            f.write(requirements)

        logger.info("API deployment package created")

    def _prepare_edge_deployment(self, checkpoint_path: Path, output_dir: Path):
        """Prepare for edge deployment."""
        logger.info("Edge deployment preparation (ONNX export) - Not yet implemented")
        # TODO: Implement ONNX export for edge deployment

    def _prepare_cloud_deployment(self, checkpoint_path: Path, output_dir: Path):
        """Prepare for cloud deployment."""
        logger.info("Cloud deployment preparation - Not yet implemented")
        # TODO: Implement cloud deployment preparation

    def cleanup_old_checkpoints(self, model_dir: str, keep_best: int = 3,
                               keep_last: int = 2):
        """
        Clean up old checkpoints to save space.

        Args:
            model_dir: Directory containing checkpoints
            keep_best: Number of best checkpoints to keep
            keep_last: Number of most recent checkpoints to keep
        """
        checkpoints = self.list_checkpoints(model_dir)

        if not checkpoints:
            logger.info("No checkpoints found to clean up")
            return

        # Sort by metric (ascending for loss)
        checkpoints_by_metric = sorted(
            [c for c in checkpoints if c.get('best_metric') is not None],
            key=lambda x: x['best_metric']
        )

        # Sort by creation time
        checkpoints_by_time = sorted(checkpoints, key=lambda x: x['created'], reverse=True)

        # Determine which checkpoints to keep
        keep_paths = set()

        # Keep best checkpoints
        for ckpt in checkpoints_by_metric[:keep_best]:
            keep_paths.add(ckpt['path'])

        # Keep most recent checkpoints
        for ckpt in checkpoints_by_time[:keep_last]:
            keep_paths.add(ckpt['path'])

        # Delete checkpoints not in keep list
        deleted_count = 0
        freed_space = 0

        for ckpt in checkpoints:
            if ckpt['path'] not in keep_paths:
                logger.info(f"Deleting checkpoint: {ckpt['name']}")
                shutil.rmtree(ckpt['path'])
                deleted_count += 1
                freed_space += ckpt['size_mb']

        logger.info(f"Deleted {deleted_count} checkpoints, freed {freed_space:.2f} MB")

    def validate_checkpoint(self, checkpoint_path: str) -> Dict[str, Any]:
        """
        Validate a checkpoint for completeness and integrity.

        Args:
            checkpoint_path: Path to checkpoint

        Returns:
            Validation results
        """
        checkpoint_path = Path(checkpoint_path)
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'files_checked': []
        }

        # Check required files
        required_files = [
            'adapter_config.json',
            'adapter_model.safetensors',  # or adapter_model.bin
        ]

        for file_name in required_files:
            file_path = checkpoint_path / file_name
            if not file_path.exists():
                # Check alternative format
                if file_name == 'adapter_model.safetensors':
                    alt_path = checkpoint_path / 'adapter_model.bin'
                    if alt_path.exists():
                        file_path = alt_path
                    else:
                        validation_results['valid'] = False
                        validation_results['errors'].append(f"Missing required file: {file_name}")
                        continue
                else:
                    validation_results['valid'] = False
                    validation_results['errors'].append(f"Missing required file: {file_name}")
                    continue

            validation_results['files_checked'].append(str(file_path))

            # Check file integrity
            if file_path.suffix in ['.safetensors', '.bin']:
                try:
                    # Try to load the file
                    if file_path.suffix == '.safetensors':
                        _ = load_file(file_path)
                    else:
                        _ = torch.load(file_path, map_location='cpu')
                except Exception as e:
                    validation_results['valid'] = False
                    validation_results['errors'].append(f"Failed to load {file_name}: {str(e)}")

        # Check optional files
        optional_files = ['trainer_state.json', 'training_args.json']
        for file_name in optional_files:
            file_path = checkpoint_path / file_name
            if file_path.exists():
                validation_results['files_checked'].append(str(file_path))
                try:
                    with open(file_path, 'r') as f:
                        _ = json.load(f)
                except Exception as e:
                    validation_results['warnings'].append(f"Failed to parse {file_name}: {str(e)}")

        # Calculate checkpoint hash for integrity
        if validation_results['valid']:
            hasher = hashlib.sha256()
            for file_path in validation_results['files_checked']:
                with open(file_path, 'rb') as f:
                    hasher.update(f.read())
            validation_results['checksum'] = hasher.hexdigest()

        return validation_results

    def push_to_hub(self, model_path: str, hub_model_id: str,
                   private: bool = True, token: str = None):
        """
        Push model to HuggingFace Hub.

        Args:
            model_path: Path to model
            hub_model_id: HuggingFace Hub model ID
            private: Whether to make repo private
            token: HuggingFace API token
        """
        model_path = Path(model_path)

        logger.info(f"Pushing model to HuggingFace Hub: {hub_model_id}")

        api = HfApi(token=token)

        # Create repository if it doesn't exist
        try:
            create_repo(
                repo_id=hub_model_id,
                private=private,
                token=token,
                exist_ok=True
            )
        except Exception as e:
            logger.warning(f"Failed to create repo (may already exist): {e}")

        # Upload model
        try:
            upload_folder(
                folder_path=str(model_path),
                repo_id=hub_model_id,
                token=token,
            )
            logger.info(f"Model successfully pushed to {hub_model_id}")
        except Exception as e:
            logger.error(f"Failed to push model: {e}")
            raise


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Manage PromptEvolver checkpoints")

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # List checkpoints
    list_parser = subparsers.add_parser('list', help='List all checkpoints')
    list_parser.add_argument('model_dir', help='Directory containing checkpoints')

    # Merge LoRA weights
    merge_parser = subparsers.add_parser('merge', help='Merge LoRA weights with base model')
    merge_parser.add_argument('checkpoint', help='Path to checkpoint')
    merge_parser.add_argument('--output', help='Output path for merged model')
    merge_parser.add_argument('--base-model', help='Base model path')
    merge_parser.add_argument('--push-to-hub', action='store_true', help='Push to HuggingFace Hub')
    merge_parser.add_argument('--hub-model-id', help='HuggingFace Hub model ID')

    # Validate checkpoint
    validate_parser = subparsers.add_parser('validate', help='Validate checkpoint')
    validate_parser.add_argument('checkpoint', help='Path to checkpoint')

    # Clean up old checkpoints
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old checkpoints')
    cleanup_parser.add_argument('model_dir', help='Directory containing checkpoints')
    cleanup_parser.add_argument('--keep-best', type=int, default=3, help='Number of best checkpoints to keep')
    cleanup_parser.add_argument('--keep-last', type=int, default=2, help='Number of recent checkpoints to keep')

    # Prepare for deployment
    deploy_parser = subparsers.add_parser('deploy', help='Prepare checkpoint for deployment')
    deploy_parser.add_argument('checkpoint', help='Path to checkpoint')
    deploy_parser.add_argument('--type', choices=['api', 'edge', 'cloud'], default='api',
                              help='Deployment type')
    deploy_parser.add_argument('--base-model', help='Base model path')

    # Convert to GGUF
    gguf_parser = subparsers.add_parser('gguf', help='Convert to GGUF format')
    gguf_parser.add_argument('model', help='Path to model')
    gguf_parser.add_argument('--output', help='Output path for GGUF file')
    gguf_parser.add_argument('--quantization', default='q4_k_m', help='Quantization method')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize manager
    manager = CheckpointManager(
        base_model_path=getattr(args, 'base_model', None)
    )

    # Execute command
    if args.command == 'list':
        checkpoints = manager.list_checkpoints(args.model_dir)

        print("\nAvailable Checkpoints:")
        print("-" * 80)
        for ckpt in checkpoints:
            print(f"Name: {ckpt['name']}")
            print(f"  Step: {ckpt['step']}")
            print(f"  Created: {ckpt['created']}")
            print(f"  Size: {ckpt['size_mb']:.2f} MB")
            if 'best_metric' in ckpt:
                print(f"  Metric: {ckpt['best_metric']:.4f}")
            print()

        if manager.best_checkpoint:
            print(f"Best checkpoint: {manager.best_checkpoint['name']}")

    elif args.command == 'merge':
        manager.merge_lora_weights(
            args.checkpoint,
            args.output,
            args.push_to_hub,
            args.hub_model_id
        )

    elif args.command == 'validate':
        results = manager.validate_checkpoint(args.checkpoint)

        print("\nValidation Results:")
        print("-" * 40)
        print(f"Valid: {results['valid']}")

        if results['errors']:
            print("\nErrors:")
            for error in results['errors']:
                print(f"  - {error}")

        if results['warnings']:
            print("\nWarnings:")
            for warning in results['warnings']:
                print(f"  - {warning}")

        if results.get('checksum'):
            print(f"\nChecksum: {results['checksum']}")

    elif args.command == 'cleanup':
        manager.cleanup_old_checkpoints(
            args.model_dir,
            args.keep_best,
            args.keep_last
        )

    elif args.command == 'deploy':
        manager.prepare_for_deployment(
            args.checkpoint,
            args.type
        )

    elif args.command == 'gguf':
        manager.convert_to_gguf(
            args.model,
            args.output,
            args.quantization
        )


if __name__ == "__main__":
    main()
