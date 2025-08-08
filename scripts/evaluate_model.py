#!/usr/bin/env python3
"""
PromptEvolver 3.0 - Model Evaluation Suite
==========================================
Comprehensive evaluation framework for trained prompt optimization models.
Implements multiple evaluation metrics and benchmarks.

Copyright (c) 2025 Matthew J. Utt
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
import time
from collections import defaultdict

import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
import numpy as np
from tqdm import tqdm

# HuggingFace imports
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    GenerationConfig,
)
from peft import PeftModel, PeftConfig
from datasets import Dataset, load_dataset

# Evaluation metrics
from rouge_score import rouge_scorer
from bert_score import score as bert_score
import evaluate
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class EvaluationConfig:
    """Configuration for model evaluation."""

    model_path: str = field(
        default="./models/qwen-promptevolver/checkpoint-best",
        metadata={"help": "Path to model checkpoint"}
    )
    base_model_path: Optional[str] = field(
        default=None,
        metadata={"help": "Path to base model (for LoRA)"}
    )
    test_data_path: str = field(
        default="./data/processed/splits/test_latest.json",
        metadata={"help": "Path to test data"}
    )
    output_dir: str = field(
        default="./evaluation_results",
        metadata={"help": "Directory for evaluation outputs"}
    )
    batch_size: int = field(
        default=8,
        metadata={"help": "Batch size for evaluation"}
    )
    max_length: int = field(
        default=512,
        metadata={"help": "Maximum sequence length"}
    )
    num_samples: Optional[int] = field(
        default=None,
        metadata={"help": "Number of samples to evaluate (None for all)"}
    )
    device: str = field(
        default="cuda" if torch.cuda.is_available() else "cpu",
        metadata={"help": "Device to use for evaluation"}
    )
    seed: int = field(
        default=42,
        metadata={"help": "Random seed"}
    )
    use_4bit: bool = field(
        default=False,
        metadata={"help": "Load model in 4-bit precision"}
    )


class PromptEvaluationMetrics:
    """Calculate various metrics for prompt optimization evaluation."""

    def __init__(self):
        """Initialize metric calculators."""
        self.rouge_scorer = rouge_scorer.RougeScorer(
            ['rouge1', 'rouge2', 'rougeL'], use_stemmer=True
        )
        self.bleu = evaluate.load("bleu")
        self.meteor = evaluate.load("meteor")

    def calculate_rouge(self, predictions: List[str], references: List[str]) -> Dict[str, float]:
        """Calculate ROUGE scores."""
        rouge_scores = {
            'rouge1': [],
            'rouge2': [],
            'rougeL': []
        }

        for pred, ref in zip(predictions, references):
            scores = self.rouge_scorer.score(ref, pred)
            for key in rouge_scores:
                rouge_scores[key].append(scores[key].fmeasure)

        return {
            f"{key}_f1": np.mean(values)
            for key, values in rouge_scores.items()
        }

    def calculate_bert_score(self, predictions: List[str], references: List[str]) -> Dict[str, float]:
        """Calculate BERTScore."""
        P, R, F1 = bert_score(predictions, references, lang='en', verbose=False)

        return {
            'bert_score_precision': P.mean().item(),
            'bert_score_recall': R.mean().item(),
            'bert_score_f1': F1.mean().item()
        }

    def calculate_bleu(self, predictions: List[str], references: List[str]) -> Dict[str, float]:
        """Calculate BLEU score."""
        # Tokenize for BLEU
        predictions_tokenized = [pred.split() for pred in predictions]
        references_tokenized = [[ref.split()] for ref in references]

        results = self.bleu.compute(
            predictions=predictions_tokenized,
            references=references_tokenized
        )

        return {
            'bleu': results['bleu'],
            'bleu_1': results['precisions'][0] if len(results['precisions']) > 0 else 0,
            'bleu_2': results['precisions'][1] if len(results['precisions']) > 1 else 0,
            'bleu_3': results['precisions'][2] if len(results['precisions']) > 2 else 0,
            'bleu_4': results['precisions'][3] if len(results['precisions']) > 3 else 0,
        }

    def calculate_meteor(self, predictions: List[str], references: List[str]) -> Dict[str, float]:
        """Calculate METEOR score."""
        results = self.meteor.compute(
            predictions=predictions,
            references=references
        )

        return {'meteor': results['meteor']}

    def calculate_quality_improvement(self,
                                     original_scores: List[float],
                                     optimized_scores: List[float]) -> Dict[str, float]:
        """Calculate quality improvement metrics."""
        improvements = [opt - orig for orig, opt in zip(original_scores, optimized_scores)]

        return {
            'avg_quality_improvement': np.mean(improvements),
            'median_quality_improvement': np.median(improvements),
            'improvement_rate': sum(1 for i in improvements if i > 0) / len(improvements),
            'avg_improvement_magnitude': np.mean([abs(i) for i in improvements if i > 0]) if any(i > 0 for i in improvements) else 0
        }

    def calculate_semantic_similarity(self, embeddings1: torch.Tensor, embeddings2: torch.Tensor) -> float:
        """Calculate semantic similarity between embeddings."""
        # Cosine similarity
        cos_sim = F.cosine_similarity(embeddings1, embeddings2, dim=-1)
        return cos_sim.mean().item()

    def calculate_diversity(self, texts: List[str]) -> float:
        """Calculate diversity of generated texts using unique n-grams."""
        all_ngrams = set()
        total_ngrams = 0

        for text in texts:
            words = text.lower().split()
            # Calculate bigrams
            for i in range(len(words) - 1):
                ngram = (words[i], words[i + 1])
                all_ngrams.add(ngram)
                total_ngrams += 1

        if total_ngrams == 0:
            return 0.0

        return len(all_ngrams) / total_ngrams

    def calculate_fluency_score(self, text: str) -> float:
        """Calculate fluency score based on perplexity (simplified)."""
        # This is a simplified version - in production, use a language model
        # to calculate actual perplexity

        # Simple heuristics for fluency
        sentences = text.split('.')
        avg_sentence_length = np.mean([len(s.split()) for s in sentences if s.strip()])

        # Penalize very short or very long sentences
        if avg_sentence_length < 5:
            fluency = 0.5
        elif avg_sentence_length > 30:
            fluency = 0.7
        else:
            fluency = 0.9

        # Check for repetition
        words = text.lower().split()
        unique_ratio = len(set(words)) / len(words) if words else 0
        fluency *= unique_ratio

        return fluency


class ModelEvaluator:
    """Main evaluator class for prompt optimization models."""

    def __init__(self, config: EvaluationConfig):
        """Initialize evaluator with configuration."""
        self.config = config
        self.device = torch.device(config.device)
        self.metrics = PromptEvaluationMetrics()

        # Set random seed
        torch.manual_seed(config.seed)
        np.random.seed(config.seed)

        # Create output directory
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load model and tokenizer
        self.model, self.tokenizer = self.load_model()

    def load_model(self) -> Tuple[Any, Any]:
        """Load model and tokenizer."""
        logger.info(f"Loading model from {self.config.model_path}")

        # Check if it's a LoRA model
        adapter_config_path = Path(self.config.model_path) / "adapter_config.json"
        is_lora = adapter_config_path.exists()

        if is_lora:
            # Load LoRA model
            peft_config = PeftConfig.from_pretrained(self.config.model_path)
            base_model_path = self.config.base_model_path or peft_config.base_model_name_or_path

            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(
                base_model_path,
                trust_remote_code=True
            )

            # Setup quantization if needed
            if self.config.use_4bit:
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True,
                )

                model = AutoModelForCausalLM.from_pretrained(
                    base_model_path,
                    quantization_config=bnb_config,
                    device_map="auto",
                    trust_remote_code=True,
                )
            else:
                model = AutoModelForCausalLM.from_pretrained(
                    base_model_path,
                    torch_dtype=torch.float16,
                    device_map="auto",
                    trust_remote_code=True,
                )

            # Load LoRA weights
            model = PeftModel.from_pretrained(model, self.config.model_path)

        else:
            # Load full model
            tokenizer = AutoTokenizer.from_pretrained(
                self.config.model_path,
                trust_remote_code=True
            )

            model = AutoModelForCausalLM.from_pretrained(
                self.config.model_path,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True,
            )

        # Set padding token
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            tokenizer.pad_token_id = tokenizer.eos_token_id

        model.eval()

        logger.info("Model loaded successfully")
        return model, tokenizer

    def load_test_data(self) -> List[Dict]:
        """Load test dataset."""
        with open(self.config.test_data_path, 'r') as f:
            data = json.load(f)

        if self.config.num_samples:
            data = data[:self.config.num_samples]

        logger.info(f"Loaded {len(data)} test samples")
        return data

    def generate_optimization(self, prompt: str, max_new_tokens: int = 256) -> str:
        """Generate optimized prompt for a given input."""
        # Format input
        input_text = f"### Instruction:\nOptimize the following prompt:\n{prompt}\n\n### Response:\n"

        # Tokenize
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            truncation=True,
            max_length=self.config.max_length
        ).to(self.device)

        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        # Decode
        generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract response
        if "### Response:" in generated:
            response = generated.split("### Response:")[-1].strip()
        else:
            response = generated[len(input_text):].strip()

        return response

    def evaluate_generation_quality(self, test_data: List[Dict]) -> Dict[str, Any]:
        """Evaluate generation quality on test set."""
        predictions = []
        references = []
        original_prompts = []

        logger.info("Generating optimizations for test set...")

        for sample in tqdm(test_data, desc="Generating"):
            original = sample.get('original_prompt', '')
            reference = sample.get('enhanced_prompt', '')

            # Generate prediction
            prediction = self.generate_optimization(original)

            predictions.append(prediction)
            references.append(reference)
            original_prompts.append(original)

        # Calculate metrics
        logger.info("Calculating evaluation metrics...")

        results = {}

        # ROUGE scores
        rouge_scores = self.metrics.calculate_rouge(predictions, references)
        results.update(rouge_scores)

        # BERTScore
        bert_scores = self.metrics.calculate_bert_score(predictions, references)
        results.update(bert_scores)

        # BLEU score
        bleu_scores = self.metrics.calculate_bleu(predictions, references)
        results.update(bleu_scores)

        # METEOR score
        meteor_scores = self.metrics.calculate_meteor(predictions, references)
        results.update(meteor_scores)

        # Diversity
        results['diversity'] = self.metrics.calculate_diversity(predictions)

        # Average fluency
        fluency_scores = [self.metrics.calculate_fluency_score(pred) for pred in predictions]
        results['avg_fluency'] = np.mean(fluency_scores)

        # Save examples
        examples = []
        for i in range(min(10, len(predictions))):
            examples.append({
                'original': original_prompts[i],
                'reference': references[i],
                'prediction': predictions[i],
                'fluency_score': fluency_scores[i]
            })

        results['examples'] = examples

        return results

    def evaluate_domain_performance(self, test_data: List[Dict]) -> Dict[str, Any]:
        """Evaluate performance across different domains."""
        domain_results = defaultdict(lambda: {
            'samples': [],
            'predictions': [],
            'references': []
        })

        logger.info("Evaluating domain-specific performance...")

        for sample in tqdm(test_data, desc="Domain evaluation"):
            domain = sample.get('domain', 'general')
            original = sample.get('original_prompt', '')
            reference = sample.get('enhanced_prompt', '')

            # Generate prediction
            prediction = self.generate_optimization(original)

            domain_results[domain]['samples'].append(original)
            domain_results[domain]['predictions'].append(prediction)
            domain_results[domain]['references'].append(reference)

        # Calculate metrics per domain
        domain_metrics = {}

        for domain, data in domain_results.items():
            if len(data['predictions']) > 0:
                domain_metrics[domain] = {
                    'num_samples': len(data['predictions']),
                    'rouge': self.metrics.calculate_rouge(
                        data['predictions'], data['references']
                    ),
                    'bleu': self.metrics.calculate_bleu(
                        data['predictions'], data['references']
                    )['bleu'],
                    'diversity': self.metrics.calculate_diversity(data['predictions'])
                }

        return domain_metrics

    def evaluate_efficiency(self, test_data: List[Dict]) -> Dict[str, float]:
        """Evaluate model efficiency metrics."""
        logger.info("Evaluating model efficiency...")

        # Sample for efficiency testing
        efficiency_samples = test_data[:min(100, len(test_data))]

        # Measure inference time
        inference_times = []

        for sample in tqdm(efficiency_samples, desc="Efficiency testing"):
            original = sample.get('original_prompt', '')

            start_time = time.time()
            _ = self.generate_optimization(original)
            end_time = time.time()

            inference_times.append(end_time - start_time)

        # Calculate statistics
        return {
            'avg_inference_time': np.mean(inference_times),
            'median_inference_time': np.median(inference_times),
            'p95_inference_time': np.percentile(inference_times, 95),
            'p99_inference_time': np.percentile(inference_times, 99),
            'throughput_per_second': 1.0 / np.mean(inference_times) if inference_times else 0
        }

    def run_comprehensive_evaluation(self) -> Dict[str, Any]:
        """Run comprehensive evaluation suite."""
        logger.info("Starting comprehensive evaluation...")

        # Load test data
        test_data = self.load_test_data()

        # Initialize results
        results = {
            'metadata': {
                'model_path': self.config.model_path,
                'test_samples': len(test_data),
                'timestamp': datetime.now().isoformat(),
                'config': {
                    'batch_size': self.config.batch_size,
                    'max_length': self.config.max_length,
                    'device': str(self.config.device)
                }
            }
        }

        # Generation quality evaluation
        logger.info("Evaluating generation quality...")
        generation_results = self.evaluate_generation_quality(test_data)
        results['generation_quality'] = generation_results

        # Domain-specific evaluation
        logger.info("Evaluating domain performance...")
        domain_results = self.evaluate_domain_performance(test_data[:min(200, len(test_data))])
        results['domain_performance'] = domain_results

        # Efficiency evaluation
        logger.info("Evaluating efficiency...")
        efficiency_results = self.evaluate_efficiency(test_data)
        results['efficiency'] = efficiency_results

        # Calculate overall score
        overall_score = self.calculate_overall_score(results)
        results['overall_score'] = overall_score

        # Save results
        self.save_results(results)

        return results

    def calculate_overall_score(self, results: Dict[str, Any]) -> float:
        """Calculate overall model performance score."""
        scores = []

        # Generation quality (40% weight)
        gen_quality = results.get('generation_quality', {})
        quality_score = np.mean([
            gen_quality.get('rouge1_f1', 0),
            gen_quality.get('rouge2_f1', 0),
            gen_quality.get('rougeL_f1', 0),
            gen_quality.get('bert_score_f1', 0),
            gen_quality.get('bleu', 0),
            gen_quality.get('meteor', 0)
        ])
        scores.append(quality_score * 0.4)

        # Diversity (20% weight)
        diversity_score = gen_quality.get('diversity', 0)
        scores.append(diversity_score * 0.2)

        # Fluency (20% weight)
        fluency_score = gen_quality.get('avg_fluency', 0)
        scores.append(fluency_score * 0.2)

        # Efficiency (20% weight)
        efficiency = results.get('efficiency', {})
        # Normalize inference time (lower is better)
        avg_time = efficiency.get('avg_inference_time', 10)
        efficiency_score = max(0, 1 - (avg_time / 10))  # Assuming 10s is poor performance
        scores.append(efficiency_score * 0.2)

        return sum(scores)

    def save_results(self, results: Dict[str, Any]):
        """Save evaluation results to files."""
        # Save full results as JSON
        results_path = self.output_dir / f"evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"Results saved to {results_path}")

        # Generate summary report
        self.generate_summary_report(results)

    def generate_summary_report(self, results: Dict[str, Any]):
        """Generate human-readable summary report."""
        report_path = self.output_dir / f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(report_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("PROMPTEVOLVER 3.0 - MODEL EVALUATION REPORT\n")
            f.write("=" * 80 + "\n\n")

            # Metadata
            f.write("EVALUATION METADATA\n")
            f.write("-" * 40 + "\n")
            f.write(f"Model: {results['metadata']['model_path']}\n")
            f.write(f"Test Samples: {results['metadata']['test_samples']}\n")
            f.write(f"Timestamp: {results['metadata']['timestamp']}\n")
            f.write(f"Device: {results['metadata']['config']['device']}\n\n")

            # Generation Quality
            f.write("GENERATION QUALITY METRICS\n")
            f.write("-" * 40 + "\n")
            gen_quality = results.get('generation_quality', {})
            f.write(f"ROUGE-1 F1: {gen_quality.get('rouge1_f1', 0):.4f}\n")
            f.write(f"ROUGE-2 F1: {gen_quality.get('rouge2_f1', 0):.4f}\n")
            f.write(f"ROUGE-L F1: {gen_quality.get('rougeL_f1', 0):.4f}\n")
            f.write(f"BERTScore F1: {gen_quality.get('bert_score_f1', 0):.4f}\n")
            f.write(f"BLEU: {gen_quality.get('bleu', 0):.4f}\n")
            f.write(f"METEOR: {gen_quality.get('meteor', 0):.4f}\n")
            f.write(f"Diversity: {gen_quality.get('diversity', 0):.4f}\n")
            f.write(f"Average Fluency: {gen_quality.get('avg_fluency', 0):.4f}\n\n")

            # Domain Performance
            f.write("DOMAIN-SPECIFIC PERFORMANCE\n")
            f.write("-" * 40 + "\n")
            domain_perf = results.get('domain_performance', {})
            for domain, metrics in domain_perf.items():
                f.write(f"\n{domain.upper()}:\n")
                f.write(f"  Samples: {metrics['num_samples']}\n")
                f.write(f"  ROUGE-L: {metrics['rouge']['rougeL_f1']:.4f}\n")
                f.write(f"  BLEU: {metrics['bleu']:.4f}\n")
                f.write(f"  Diversity: {metrics['diversity']:.4f}\n")

            # Efficiency
            f.write("\nEFFICIENCY METRICS\n")
            f.write("-" * 40 + "\n")
            efficiency = results.get('efficiency', {})
            f.write(f"Average Inference Time: {efficiency.get('avg_inference_time', 0):.3f}s\n")
            f.write(f"Median Inference Time: {efficiency.get('median_inference_time', 0):.3f}s\n")
            f.write(f"P95 Inference Time: {efficiency.get('p95_inference_time', 0):.3f}s\n")
            f.write(f"Throughput: {efficiency.get('throughput_per_second', 0):.2f} samples/sec\n\n")

            # Overall Score
            f.write("OVERALL PERFORMANCE\n")
            f.write("-" * 40 + "\n")
            f.write(f"Overall Score: {results.get('overall_score', 0):.4f}\n\n")

            # Examples
            f.write("EXAMPLE OPTIMIZATIONS\n")
            f.write("-" * 40 + "\n")
            examples = gen_quality.get('examples', [])
            for i, example in enumerate(examples[:3], 1):
                f.write(f"\nExample {i}:\n")
                f.write(f"Original: {example['original'][:100]}...\n")
                f.write(f"Prediction: {example['prediction'][:100]}...\n")
                f.write(f"Reference: {example['reference'][:100]}...\n")
                f.write(f"Fluency Score: {example['fluency_score']:.4f}\n")

        logger.info(f"Summary report saved to {report_path}")


def main():
    """Main entry point for evaluation."""
    parser = argparse.ArgumentParser(description="Evaluate PromptEvolver model")

    parser.add_argument(
        "--model-path",
        type=str,
        default="./models/qwen-promptevolver/checkpoint-best",
        help="Path to model checkpoint"
    )
    parser.add_argument(
        "--base-model",
        type=str,
        default=None,
        help="Path to base model (for LoRA)"
    )
    parser.add_argument(
        "--test-data",
        type=str,
        default="./data/processed/splits/test_latest.json",
        help="Path to test data"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./evaluation_results",
        help="Directory for evaluation outputs"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=8,
        help="Batch size for evaluation"
    )
    parser.add_argument(
        "--num-samples",
        type=int,
        default=None,
        help="Number of samples to evaluate"
    )
    parser.add_argument(
        "--use-4bit",
        action="store_true",
        help="Load model in 4-bit precision"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda" if torch.cuda.is_available() else "cpu",
        help="Device to use"
    )

    args = parser.parse_args()

    # Create configuration
    config = EvaluationConfig(
        model_path=args.model_path,
        base_model_path=args.base_model,
        test_data_path=args.test_data,
        output_dir=args.output_dir,
        batch_size=args.batch_size,
        num_samples=args.num_samples,
        use_4bit=args.use_4bit,
        device=args.device
    )

    # Run evaluation
    evaluator = ModelEvaluator(config)
    results = evaluator.run_comprehensive_evaluation()

    # Print summary
    print("\n" + "=" * 80)
    print("EVALUATION COMPLETE")
    print("=" * 80)
    print(f"Overall Score: {results['overall_score']:.4f}")
    print(f"ROUGE-L F1: {results['generation_quality']['rougeL_f1']:.4f}")
    print(f"BERTScore F1: {results['generation_quality']['bert_score_f1']:.4f}")
    print(f"BLEU: {results['generation_quality']['bleu']:.4f}")
    print(f"Avg Inference Time: {results['efficiency']['avg_inference_time']:.3f}s")
    print(f"\nResults saved to: {config.output_dir}")


if __name__ == "__main__":
    main()
