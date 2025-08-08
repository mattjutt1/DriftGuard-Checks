#!/usr/bin/env python3
"""
PromptEvolver 3.0 - Benchmark Suite
====================================
Comprehensive benchmarking framework for prompt optimization models.
Includes standard benchmarks, ablation studies, and comparative analysis.

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
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field, asdict
import time
from collections import defaultdict
import concurrent.futures
from functools import partial

import torch
import numpy as np
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Import evaluation metrics
from evaluate_model import ModelEvaluator, PromptEvaluationMetrics, EvaluationConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class BenchmarkTask:
    """Definition of a benchmark task."""

    name: str
    description: str
    dataset_path: str
    metrics: List[str]
    domain: str = "general"
    difficulty: str = "medium"  # easy, medium, hard
    max_samples: Optional[int] = None
    custom_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkConfig:
    """Configuration for benchmark suite."""

    output_dir: str = "./benchmark_results"
    models_to_compare: List[str] = field(default_factory=list)
    baseline_model: Optional[str] = None
    benchmark_tasks: List[BenchmarkTask] = field(default_factory=list)
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    batch_size: int = 8
    max_samples_per_task: int = 500
    enable_ablation: bool = True
    enable_visualization: bool = True
    parallel_workers: int = 1
    seed: int = 42


class StandardBenchmarks:
    """Collection of standard benchmark tasks."""

    @staticmethod
    def get_standard_tasks() -> List[BenchmarkTask]:
        """Get list of standard benchmark tasks."""
        return [
            BenchmarkTask(
                name="clarity_improvement",
                description="Measure improvement in prompt clarity",
                dataset_path="./benchmarks/clarity_test.json",
                metrics=["rouge_l", "bert_score", "clarity_score"],
                domain="general",
                difficulty="easy"
            ),
            BenchmarkTask(
                name="specificity_enhancement",
                description="Evaluate specificity improvements",
                dataset_path="./benchmarks/specificity_test.json",
                metrics=["specificity_score", "information_gain", "rouge_2"],
                domain="technical",
                difficulty="medium"
            ),
            BenchmarkTask(
                name="creative_expansion",
                description="Test creative prompt expansion abilities",
                dataset_path="./benchmarks/creative_test.json",
                metrics=["diversity", "novelty", "fluency"],
                domain="creative",
                difficulty="hard"
            ),
            BenchmarkTask(
                name="technical_precision",
                description="Assess technical prompt optimization",
                dataset_path="./benchmarks/technical_test.json",
                metrics=["accuracy", "technical_terms", "bert_score"],
                domain="technical",
                difficulty="hard"
            ),
            BenchmarkTask(
                name="instruction_following",
                description="Evaluate instruction clarity improvements",
                dataset_path="./benchmarks/instruction_test.json",
                metrics=["instruction_clarity", "actionability", "rouge_l"],
                domain="business",
                difficulty="medium"
            ),
            BenchmarkTask(
                name="context_preservation",
                description="Test context preservation during optimization",
                dataset_path="./benchmarks/context_test.json",
                metrics=["context_similarity", "information_retention", "bert_score"],
                domain="general",
                difficulty="medium"
            ),
            BenchmarkTask(
                name="length_optimization",
                description="Evaluate appropriate length adjustments",
                dataset_path="./benchmarks/length_test.json",
                metrics=["length_appropriateness", "conciseness", "completeness"],
                domain="general",
                difficulty="easy"
            ),
            BenchmarkTask(
                name="ambiguity_reduction",
                description="Measure reduction in prompt ambiguity",
                dataset_path="./benchmarks/ambiguity_test.json",
                metrics=["ambiguity_score", "clarity_score", "precision"],
                domain="general",
                difficulty="medium"
            )
        ]

    @staticmethod
    def create_synthetic_benchmark(name: str, num_samples: int = 100) -> List[Dict]:
        """Create synthetic benchmark data for testing."""
        np.random.seed(42)

        templates = {
            "clarity": [
                "Make a thing that does stuff",
                "Create something for users",
                "Build a solution",
                "Develop a system"
            ],
            "technical": [
                "Implement algorithm",
                "Create API",
                "Build database",
                "Design architecture"
            ],
            "creative": [
                "Write about topic",
                "Create story",
                "Design concept",
                "Imagine scenario"
            ]
        }

        enhanced_templates = {
            "clarity": [
                "Develop a web application that enables user authentication and data management",
                "Create an interactive dashboard for real-time analytics visualization",
                "Build a RESTful API service with comprehensive error handling",
                "Develop a scalable microservices architecture with load balancing"
            ],
            "technical": [
                "Implement a distributed consensus algorithm using Raft protocol",
                "Create a GraphQL API with subscription support and caching",
                "Build a time-series database optimized for IoT data ingestion",
                "Design a event-driven architecture using Apache Kafka"
            ],
            "creative": [
                "Write a compelling narrative about climate change impact on future societies",
                "Create an immersive story world with detailed character backgrounds",
                "Design a innovative game concept combining education and entertainment",
                "Imagine alternative history scenarios with plausible technological developments"
            ]
        }

        data = []
        for _ in range(num_samples):
            category = np.random.choice(list(templates.keys()))
            original = np.random.choice(templates[category])
            enhanced = np.random.choice(enhanced_templates[category])

            data.append({
                "original_prompt": original,
                "enhanced_prompt": enhanced,
                "domain": category,
                "quality_score": np.random.uniform(0.6, 0.95)
            })

        return data


class BenchmarkMetrics:
    """Advanced metrics for benchmark evaluation."""

    def __init__(self):
        """Initialize metrics calculators."""
        self.base_metrics = PromptEvaluationMetrics()

    def calculate_clarity_score(self, text: str) -> float:
        """Calculate clarity score based on readability metrics."""
        # Simplified Flesch Reading Ease adaptation
        sentences = text.split('.')
        words = text.split()
        syllables = sum([self._count_syllables(word) for word in words])

        if len(sentences) == 0 or len(words) == 0:
            return 0.0

        avg_sentence_length = len(words) / len(sentences)
        avg_syllables_per_word = syllables / len(words)

        # Modified Flesch score normalized to 0-1
        score = 206.835 - 1.015 * avg_sentence_length - 84.6 * avg_syllables_per_word
        normalized_score = max(0, min(1, score / 100))

        return normalized_score

    def calculate_specificity_score(self, original: str, optimized: str) -> float:
        """Calculate how much more specific the optimized prompt is."""
        # Count specific terms and details
        original_terms = set(original.lower().split())
        optimized_terms = set(optimized.lower().split())

        # More terms generally means more specific
        term_increase = len(optimized_terms) / (len(original_terms) + 1)

        # Check for numbers, proper nouns (simplified)
        specificity_markers = sum([
            1 for word in optimized.split()
            if word[0].isupper() or any(char.isdigit() for char in word)
        ])

        specificity = min(1.0, (term_increase * 0.5 + specificity_markers * 0.1))
        return specificity

    def calculate_information_gain(self, original: str, optimized: str) -> float:
        """Calculate information gain from original to optimized."""
        original_info = set(original.lower().split())
        optimized_info = set(optimized.lower().split())

        new_info = optimized_info - original_info
        preserved_info = original_info & optimized_info

        if len(original_info) == 0:
            return 0.0

        gain = (len(new_info) + len(preserved_info)) / len(original_info)
        return min(1.0, gain)

    def calculate_technical_terms(self, text: str) -> float:
        """Calculate density of technical terms."""
        technical_keywords = {
            'api', 'algorithm', 'database', 'framework', 'architecture',
            'protocol', 'implementation', 'interface', 'module', 'component',
            'service', 'endpoint', 'schema', 'optimization', 'performance',
            'scalability', 'reliability', 'security', 'encryption', 'authentication'
        }

        words = text.lower().split()
        technical_count = sum(1 for word in words if word in technical_keywords)

        return technical_count / (len(words) + 1)

    def calculate_instruction_clarity(self, text: str) -> float:
        """Calculate clarity of instructions."""
        # Check for action verbs and clear directives
        action_verbs = {
            'create', 'build', 'implement', 'design', 'develop',
            'write', 'generate', 'analyze', 'evaluate', 'optimize',
            'configure', 'setup', 'install', 'deploy', 'test'
        }

        words = text.lower().split()
        has_action = any(word in action_verbs for word in words)

        # Check for clear structure
        has_steps = any(marker in text for marker in ['1.', '2.', 'first', 'then', 'finally'])

        # Check for specificity
        has_specifics = len(words) > 10

        score = (has_action * 0.4 + has_steps * 0.3 + has_specifics * 0.3)
        return score

    def calculate_actionability(self, text: str) -> float:
        """Calculate how actionable the prompt is."""
        actionable_patterns = [
            'create', 'build', 'implement', 'must', 'should',
            'need to', 'required', 'ensure', 'verify', 'test'
        ]

        text_lower = text.lower()
        actionability = sum(1 for pattern in actionable_patterns if pattern in text_lower)

        return min(1.0, actionability / 5)

    def calculate_context_similarity(self, original: str, optimized: str) -> float:
        """Calculate semantic similarity between original and optimized."""
        # Simplified version - in production, use embeddings
        original_words = set(original.lower().split())
        optimized_words = set(optimized.lower().split())

        if not original_words:
            return 0.0

        overlap = original_words & optimized_words
        similarity = len(overlap) / len(original_words)

        return similarity

    def calculate_information_retention(self, original: str, optimized: str) -> float:
        """Calculate how much original information is retained."""
        original_concepts = set(original.lower().split())
        optimized_concepts = set(optimized.lower().split())

        if not original_concepts:
            return 1.0

        retained = original_concepts & optimized_concepts
        retention = len(retained) / len(original_concepts)

        return retention

    def calculate_ambiguity_score(self, text: str) -> float:
        """Calculate ambiguity level (lower is better)."""
        ambiguous_terms = {
            'thing', 'stuff', 'something', 'whatever', 'somehow',
            'maybe', 'possibly', 'might', 'could', 'probably',
            'various', 'several', 'some', 'many', 'few'
        }

        words = text.lower().split()
        ambiguity_count = sum(1 for word in words if word in ambiguous_terms)

        # Invert score (less ambiguity is better)
        ambiguity = 1.0 - min(1.0, ambiguity_count / (len(words) + 1))
        return ambiguity

    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)."""
        vowels = "aeiouAEIOU"
        syllable_count = 0
        previous_was_vowel = False

        for char in word:
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel

        # Ensure at least one syllable
        return max(1, syllable_count)


class BenchmarkRunner:
    """Main benchmark runner class."""

    def __init__(self, config: BenchmarkConfig):
        """Initialize benchmark runner."""
        self.config = config
        self.metrics_calculator = BenchmarkMetrics()
        self.results = {}

        # Create output directory
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set random seed
        np.random.seed(config.seed)
        torch.manual_seed(config.seed)

    def run_benchmark_task(self,
                          model_path: str,
                          task: BenchmarkTask) -> Dict[str, Any]:
        """Run a single benchmark task on a model."""
        logger.info(f"Running benchmark '{task.name}' on model: {model_path}")

        # Load or create benchmark data
        if Path(task.dataset_path).exists():
            with open(task.dataset_path, 'r') as f:
                data = json.load(f)
        else:
            # Create synthetic data for testing
            logger.warning(f"Dataset not found, creating synthetic data for {task.name}")
            data = StandardBenchmarks.create_synthetic_benchmark(
                task.name,
                task.max_samples or 100
            )

        # Limit samples if specified
        if self.config.max_samples_per_task:
            data = data[:self.config.max_samples_per_task]

        # Create evaluator
        eval_config = EvaluationConfig(
            model_path=model_path,
            test_data_path="",  # We'll pass data directly
            output_dir=str(self.output_dir / "temp"),
            batch_size=self.config.batch_size,
            device=self.config.device
        )

        evaluator = ModelEvaluator(eval_config)

        # Run evaluation
        results = {
            'task_name': task.name,
            'description': task.description,
            'domain': task.domain,
            'difficulty': task.difficulty,
            'num_samples': len(data),
            'metrics': {}
        }

        # Generate predictions
        predictions = []
        references = []
        originals = []

        for sample in tqdm(data, desc=f"Evaluating {task.name}"):
            original = sample.get('original_prompt', '')
            reference = sample.get('enhanced_prompt', '')

            prediction = evaluator.generate_optimization(original)

            predictions.append(prediction)
            references.append(reference)
            originals.append(original)

        # Calculate metrics based on task requirements
        for metric_name in task.metrics:
            if metric_name == "rouge_l":
                scores = evaluator.metrics.calculate_rouge(predictions, references)
                results['metrics'][metric_name] = scores.get('rougeL_f1', 0)

            elif metric_name == "rouge_2":
                scores = evaluator.metrics.calculate_rouge(predictions, references)
                results['metrics'][metric_name] = scores.get('rouge2_f1', 0)

            elif metric_name == "bert_score":
                scores = evaluator.metrics.calculate_bert_score(predictions, references)
                results['metrics'][metric_name] = scores.get('bert_score_f1', 0)

            elif metric_name == "clarity_score":
                scores = [self.metrics_calculator.calculate_clarity_score(pred)
                         for pred in predictions]
                results['metrics'][metric_name] = np.mean(scores)

            elif metric_name == "specificity_score":
                scores = [self.metrics_calculator.calculate_specificity_score(orig, pred)
                         for orig, pred in zip(originals, predictions)]
                results['metrics'][metric_name] = np.mean(scores)

            elif metric_name == "information_gain":
                scores = [self.metrics_calculator.calculate_information_gain(orig, pred)
                         for orig, pred in zip(originals, predictions)]
                results['metrics'][metric_name] = np.mean(scores)

            elif metric_name == "diversity":
                results['metrics'][metric_name] = evaluator.metrics.calculate_diversity(predictions)

            elif metric_name == "fluency":
                scores = [evaluator.metrics.calculate_fluency_score(pred) for pred in predictions]
                results['metrics'][metric_name] = np.mean(scores)

            elif metric_name == "technical_terms":
                scores = [self.metrics_calculator.calculate_technical_terms(pred)
                         for pred in predictions]
                results['metrics'][metric_name] = np.mean(scores)

            elif metric_name == "instruction_clarity":
                scores = [self.metrics_calculator.calculate_instruction_clarity(pred)
                         for pred in predictions]
                results['metrics'][metric_name] = np.mean(scores)

            elif metric_name == "actionability":
                scores = [self.metrics_calculator.calculate_actionability(pred)
                         for pred in predictions]
                results['metrics'][metric_name] = np.mean(scores)

            elif metric_name == "context_similarity":
                scores = [self.metrics_calculator.calculate_context_similarity(orig, pred)
                         for orig, pred in zip(originals, predictions)]
                results['metrics'][metric_name] = np.mean(scores)

            elif metric_name == "information_retention":
                scores = [self.metrics_calculator.calculate_information_retention(orig, pred)
                         for orig, pred in zip(originals, predictions)]
                results['metrics'][metric_name] = np.mean(scores)

            elif metric_name == "ambiguity_score":
                scores = [self.metrics_calculator.calculate_ambiguity_score(pred)
                         for pred in predictions]
                results['metrics'][metric_name] = np.mean(scores)

        # Calculate aggregate score for the task
        if results['metrics']:
            results['aggregate_score'] = np.mean(list(results['metrics'].values()))
        else:
            results['aggregate_score'] = 0.0

        return results

    def run_all_benchmarks(self) -> Dict[str, Any]:
        """Run all benchmark tasks on all models."""
        all_results = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'config': asdict(self.config),
                'num_models': len(self.config.models_to_compare),
                'num_tasks': len(self.config.benchmark_tasks)
            },
            'model_results': {},
            'task_summaries': {},
            'comparisons': {}
        }

        # Get benchmark tasks
        if not self.config.benchmark_tasks:
            self.config.benchmark_tasks = StandardBenchmarks.get_standard_tasks()

        # Run benchmarks for each model
        for model_path in self.config.models_to_compare:
            model_name = Path(model_path).name
            all_results['model_results'][model_name] = []

            logger.info(f"Benchmarking model: {model_name}")

            # Run each benchmark task
            for task in self.config.benchmark_tasks:
                try:
                    task_results = self.run_benchmark_task(model_path, task)
                    all_results['model_results'][model_name].append(task_results)
                except Exception as e:
                    logger.error(f"Failed to run task {task.name}: {e}")
                    all_results['model_results'][model_name].append({
                        'task_name': task.name,
                        'error': str(e)
                    })

            # Calculate model summary
            valid_results = [r for r in all_results['model_results'][model_name]
                           if 'aggregate_score' in r]
            if valid_results:
                all_results['model_results'][model_name].append({
                    'summary': {
                        'avg_score': np.mean([r['aggregate_score'] for r in valid_results]),
                        'tasks_completed': len(valid_results),
                        'tasks_failed': len(self.config.benchmark_tasks) - len(valid_results)
                    }
                })

        # Generate task summaries
        for task in self.config.benchmark_tasks:
            task_name = task.name
            all_results['task_summaries'][task_name] = {}

            for model_name, results in all_results['model_results'].items():
                task_result = next((r for r in results if r.get('task_name') == task_name), None)
                if task_result and 'aggregate_score' in task_result:
                    all_results['task_summaries'][task_name][model_name] = task_result['aggregate_score']

        # Generate comparisons
        if len(self.config.models_to_compare) > 1:
            all_results['comparisons'] = self.generate_comparisons(all_results)

        # Save results
        self.save_results(all_results)

        # Generate visualizations if enabled
        if self.config.enable_visualization:
            self.generate_visualizations(all_results)

        return all_results

    def generate_comparisons(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate model comparisons."""
        comparisons = {
            'best_overall': None,
            'best_per_task': {},
            'statistical_tests': {}
        }

        # Find best overall model
        model_scores = {}
        for model_name in self.config.models_to_compare:
            model_key = Path(model_name).name
            if model_key in results['model_results']:
                summary = next((r.get('summary') for r in results['model_results'][model_key]
                              if 'summary' in r), None)
                if summary:
                    model_scores[model_key] = summary['avg_score']

        if model_scores:
            comparisons['best_overall'] = max(model_scores, key=model_scores.get)

        # Find best model per task
        for task_name, task_scores in results['task_summaries'].items():
            if task_scores:
                comparisons['best_per_task'][task_name] = max(task_scores, key=task_scores.get)

        # Statistical significance tests (if baseline exists)
        if self.config.baseline_model:
            baseline_name = Path(self.config.baseline_model).name

            for model_path in self.config.models_to_compare:
                if model_path == self.config.baseline_model:
                    continue

                model_name = Path(model_path).name

                # Collect scores for comparison
                baseline_scores = []
                model_scores = []

                for task_name in results['task_summaries']:
                    if baseline_name in results['task_summaries'][task_name]:
                        baseline_scores.append(results['task_summaries'][task_name][baseline_name])
                    if model_name in results['task_summaries'][task_name]:
                        model_scores.append(results['task_summaries'][task_name][model_name])

                if baseline_scores and model_scores and len(baseline_scores) == len(model_scores):
                    # Paired t-test
                    t_stat, p_value = stats.ttest_rel(model_scores, baseline_scores)

                    comparisons['statistical_tests'][f"{model_name}_vs_{baseline_name}"] = {
                        't_statistic': float(t_stat),
                        'p_value': float(p_value),
                        'significant': p_value < 0.05,
                        'mean_improvement': float(np.mean(model_scores) - np.mean(baseline_scores))
                    }

        return comparisons

    def run_ablation_study(self, model_path: str) -> Dict[str, Any]:
        """Run ablation study on model components."""
        logger.info(f"Running ablation study on {model_path}")

        ablation_results = {
            'model': Path(model_path).name,
            'components': {},
            'impact_analysis': {}
        }

        # Define ablation configurations
        ablation_configs = [
            {
                'name': 'no_domain_classification',
                'description': 'Disable domain-specific optimization',
                'modify': lambda x: x  # Placeholder for actual modification
            },
            {
                'name': 'no_quality_scoring',
                'description': 'Disable quality scoring guidance',
                'modify': lambda x: x
            },
            {
                'name': 'reduced_context',
                'description': 'Reduce context window by 50%',
                'modify': lambda x: x
            },
            {
                'name': 'no_few_shot',
                'description': 'Remove few-shot examples',
                'modify': lambda x: x
            }
        ]

        # Run benchmark with each ablation
        base_task = BenchmarkTask(
            name="ablation_test",
            description="Ablation study benchmark",
            dataset_path="./benchmarks/ablation_test.json",
            metrics=["rouge_l", "bert_score", "clarity_score"],
            max_samples=50
        )

        # Get baseline performance
        baseline_results = self.run_benchmark_task(model_path, base_task)
        ablation_results['baseline'] = baseline_results['aggregate_score']

        # Run ablations
        for config in ablation_configs:
            # This is a placeholder - actual ablation would modify model behavior
            ablated_results = self.run_benchmark_task(model_path, base_task)

            ablation_results['components'][config['name']] = {
                'description': config['description'],
                'score': ablated_results['aggregate_score'],
                'impact': baseline_results['aggregate_score'] - ablated_results['aggregate_score']
            }

        # Analyze impact
        impacts = [comp['impact'] for comp in ablation_results['components'].values()]
        ablation_results['impact_analysis'] = {
            'most_important': max(ablation_results['components'],
                                 key=lambda x: ablation_results['components'][x]['impact']),
            'least_important': min(ablation_results['components'],
                                  key=lambda x: ablation_results['components'][x]['impact']),
            'avg_impact': np.mean(impacts),
            'total_impact': sum(impacts)
        }

        return ablation_results

    def generate_visualizations(self, results: Dict[str, Any]):
        """Generate benchmark visualizations."""
        # Set style
        sns.set_style("whitegrid")

        # Create figure with subplots
        fig = plt.figure(figsize=(20, 12))

        # 1. Model comparison across tasks
        ax1 = plt.subplot(2, 3, 1)
        model_names = []
        task_names = list(results['task_summaries'].keys())

        for model_path in self.config.models_to_compare:
            model_name = Path(model_path).name
            model_names.append(model_name)

        # Create matrix for heatmap
        score_matrix = []
        for model_name in model_names:
            model_scores = []
            for task_name in task_names:
                score = results['task_summaries'][task_name].get(model_name, 0)
                model_scores.append(score)
            score_matrix.append(model_scores)

        if score_matrix:
            sns.heatmap(score_matrix, annot=True, fmt='.3f',
                       xticklabels=task_names, yticklabels=model_names,
                       cmap='YlOrRd', ax=ax1)
            ax1.set_title('Model Performance Across Tasks')
            ax1.set_xlabel('Benchmark Task')
            ax1.set_ylabel('Model')

        # 2. Overall model comparison
        ax2 = plt.subplot(2, 3, 2)
        model_avg_scores = []

        for model_name in model_names:
            if model_name in results['model_results']:
                summary = next((r.get('summary') for r in results['model_results'][model_name]
                              if 'summary' in r), None)
                if summary:
                    model_avg_scores.append(summary['avg_score'])
                else:
                    model_avg_scores.append(0)

        if model_avg_scores:
            bars = ax2.bar(range(len(model_names)), model_avg_scores)
            ax2.set_xticks(range(len(model_names)))
            ax2.set_xticklabels(model_names, rotation=45, ha='right')
            ax2.set_ylabel('Average Score')
            ax2.set_title('Overall Model Performance')
            ax2.set_ylim(0, 1)

            # Add value labels on bars
            for bar, score in zip(bars, model_avg_scores):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{score:.3f}', ha='center', va='bottom')

        # 3. Task difficulty analysis
        ax3 = plt.subplot(2, 3, 3)
        difficulty_scores = {'easy': [], 'medium': [], 'hard': []}

        for task in self.config.benchmark_tasks:
            if task.name in results['task_summaries']:
                task_scores = list(results['task_summaries'][task.name].values())
                if task_scores:
                    difficulty_scores[task.difficulty].append(np.mean(task_scores))

        if any(scores for scores in difficulty_scores.values()):
            bp = ax3.boxplot([difficulty_scores[d] for d in ['easy', 'medium', 'hard']],
                            labels=['Easy', 'Medium', 'Hard'])
            ax3.set_ylabel('Score')
            ax3.set_title('Performance by Task Difficulty')
            ax3.set_ylim(0, 1)

        # 4. Metric distribution
        ax4 = plt.subplot(2, 3, 4)
        all_metrics = defaultdict(list)

        for model_name, model_results in results['model_results'].items():
            for task_result in model_results:
                if 'metrics' in task_result:
                    for metric_name, value in task_result['metrics'].items():
                        all_metrics[metric_name].append(value)

        if all_metrics:
            metric_names = list(all_metrics.keys())[:6]  # Limit to 6 metrics for visibility
            metric_values = [all_metrics[m] for m in metric_names]

            bp = ax4.boxplot(metric_values, labels=metric_names)
            ax4.set_xticklabels(metric_names, rotation=45, ha='right')
            ax4.set_ylabel('Score')
            ax4.set_title('Metric Distribution Across All Tests')
            ax4.set_ylim(0, 1)

        # 5. Domain performance
        ax5 = plt.subplot(2, 3, 5)
        domain_scores = defaultdict(list)

        for task in self.config.benchmark_tasks:
            if task.name in results['task_summaries']:
                task_scores = list(results['task_summaries'][task.name].values())
                if task_scores:
                    domain_scores[task.domain].append(np.mean(task_scores))

        if domain_scores:
            domains = list(domain_scores.keys())
            scores = [np.mean(domain_scores[d]) for d in domains]

            bars = ax5.bar(range(len(domains)), scores)
            ax5.set_xticks(range(len(domains)))
            ax5.set_xticklabels(domains, rotation=45, ha='right')
            ax5.set_ylabel('Average Score')
            ax5.set_title('Performance by Domain')
            ax5.set_ylim(0, 1)

        # 6. Improvement over baseline (if applicable)
        if self.config.baseline_model and 'statistical_tests' in results.get('comparisons', {}):
            ax6 = plt.subplot(2, 3, 6)

            improvements = []
            model_labels = []

            for test_name, test_results in results['comparisons']['statistical_tests'].items():
                model_labels.append(test_name.split('_vs_')[0])
                improvements.append(test_results['mean_improvement'])

            if improvements:
                colors = ['green' if imp > 0 else 'red' for imp in improvements]
                bars = ax6.bar(range(len(model_labels)), improvements, color=colors)
                ax6.set_xticks(range(len(model_labels)))
                ax6.set_xticklabels(model_labels, rotation=45, ha='right')
                ax6.set_ylabel('Mean Improvement')
                ax6.set_title('Improvement Over Baseline')
                ax6.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

                # Add significance markers
                for i, (bar, test_name) in enumerate(zip(bars, results['comparisons']['statistical_tests'].keys())):
                    if results['comparisons']['statistical_tests'][test_name]['significant']:
                        ax6.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                                '*', ha='center', va='bottom' if bar.get_height() > 0 else 'top',
                                fontsize=14, fontweight='bold')

        plt.tight_layout()

        # Save figure
        viz_path = self.output_dir / f"benchmark_visualizations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(viz_path, dpi=150, bbox_inches='tight')
        logger.info(f"Visualizations saved to {viz_path}")

        plt.close()

    def save_results(self, results: Dict[str, Any]):
        """Save benchmark results."""
        # Save as JSON
        results_path = self.output_dir / f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"Results saved to {results_path}")

        # Generate markdown report
        self.generate_markdown_report(results)

    def generate_markdown_report(self, results: Dict[str, Any]):
        """Generate markdown benchmark report."""
        report_path = self.output_dir / f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        with open(report_path, 'w') as f:
            f.write("# PromptEvolver 3.0 - Benchmark Report\n\n")
            f.write(f"**Generated**: {results['metadata']['timestamp']}\n\n")

            # Executive Summary
            f.write("## Executive Summary\n\n")

            if 'comparisons' in results and results['comparisons'].get('best_overall'):
                f.write(f"**Best Overall Model**: {results['comparisons']['best_overall']}\n\n")

            # Model Results
            f.write("## Model Performance\n\n")

            for model_name, model_results in results['model_results'].items():
                f.write(f"### {model_name}\n\n")

                # Find summary
                summary = next((r.get('summary') for r in model_results if 'summary' in r), None)
                if summary:
                    f.write(f"- **Average Score**: {summary['avg_score']:.4f}\n")
                    f.write(f"- **Tasks Completed**: {summary['tasks_completed']}\n")
                    f.write(f"- **Tasks Failed**: {summary['tasks_failed']}\n\n")

                # Task details
                f.write("| Task | Domain | Difficulty | Score |\n")
                f.write("|------|--------|------------|-------|\n")

                for task_result in model_results:
                    if 'task_name' in task_result and 'aggregate_score' in task_result:
                        f.write(f"| {task_result['task_name']} | "
                               f"{task_result['domain']} | "
                               f"{task_result['difficulty']} | "
                               f"{task_result['aggregate_score']:.4f} |\n")

                f.write("\n")

            # Task Summaries
            f.write("## Task Performance Comparison\n\n")

            if results['task_summaries']:
                # Create comparison table
                task_names = list(results['task_summaries'].keys())
                model_names = list(list(results['task_summaries'].values())[0].keys())

                f.write("| Task |")
                for model_name in model_names:
                    f.write(f" {model_name} |")
                f.write("\n")

                f.write("|------|")
                for _ in model_names:
                    f.write("--------|")
                f.write("\n")

                for task_name in task_names:
                    f.write(f"| {task_name} |")
                    for model_name in model_names:
                        score = results['task_summaries'][task_name].get(model_name, 0)
                        f.write(f" {score:.4f} |")
                    f.write("\n")

                f.write("\n")

            # Statistical Tests
            if 'comparisons' in results and 'statistical_tests' in results['comparisons']:
                f.write("## Statistical Significance\n\n")

                for test_name, test_results in results['comparisons']['statistical_tests'].items():
                    f.write(f"### {test_name}\n\n")
                    f.write(f"- **t-statistic**: {test_results['t_statistic']:.4f}\n")
                    f.write(f"- **p-value**: {test_results['p_value']:.4f}\n")
                    f.write(f"- **Significant**: {'Yes' if test_results['significant'] else 'No'}\n")
                    f.write(f"- **Mean Improvement**: {test_results['mean_improvement']:.4f}\n\n")

        logger.info(f"Markdown report saved to {report_path}")


def main():
    """Main entry point for benchmark suite."""
    parser = argparse.ArgumentParser(description="Run PromptEvolver benchmark suite")

    parser.add_argument(
        "--models",
        nargs="+",
        required=True,
        help="List of model paths to benchmark"
    )
    parser.add_argument(
        "--baseline",
        type=str,
        default=None,
        help="Baseline model for comparison"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./benchmark_results",
        help="Output directory for results"
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=500,
        help="Maximum samples per benchmark task"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=8,
        help="Batch size for evaluation"
    )
    parser.add_argument(
        "--tasks",
        nargs="+",
        choices=["clarity", "specificity", "creative", "technical", "instruction",
                "context", "length", "ambiguity", "all"],
        default=["all"],
        help="Benchmark tasks to run"
    )
    parser.add_argument(
        "--ablation",
        action="store_true",
        help="Run ablation study"
    )
    parser.add_argument(
        "--no-viz",
        action="store_true",
        help="Disable visualization generation"
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        help="Number of parallel workers"
    )

    args = parser.parse_args()

    # Prepare benchmark tasks
    if "all" in args.tasks:
        benchmark_tasks = StandardBenchmarks.get_standard_tasks()
    else:
        all_tasks = StandardBenchmarks.get_standard_tasks()
        task_map = {
            "clarity": "clarity_improvement",
            "specificity": "specificity_enhancement",
            "creative": "creative_expansion",
            "technical": "technical_precision",
            "instruction": "instruction_following",
            "context": "context_preservation",
            "length": "length_optimization",
            "ambiguity": "ambiguity_reduction"
        }

        benchmark_tasks = [
            task for task in all_tasks
            if any(task.name == task_map.get(t) for t in args.tasks if t != "all")
        ]

    # Create configuration
    config = BenchmarkConfig(
        output_dir=args.output_dir,
        models_to_compare=args.models,
        baseline_model=args.baseline,
        benchmark_tasks=benchmark_tasks,
        max_samples_per_task=args.max_samples,
        batch_size=args.batch_size,
        enable_ablation=args.ablation,
        enable_visualization=not args.no_viz,
        parallel_workers=args.parallel
    )

    # Run benchmarks
    runner = BenchmarkRunner(config)
    results = runner.run_all_benchmarks()

    # Run ablation study if requested
    if args.ablation and args.models:
        ablation_results = runner.run_ablation_study(args.models[0])

        # Save ablation results
        ablation_path = Path(args.output_dir) / f"ablation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(ablation_path, 'w') as f:
            json.dump(ablation_results, f, indent=2)

        logger.info(f"Ablation results saved to {ablation_path}")

    # Print summary
    print("\n" + "=" * 80)
    print("BENCHMARK SUITE COMPLETE")
    print("=" * 80)

    if 'comparisons' in results and results['comparisons'].get('best_overall'):
        print(f"Best Overall Model: {results['comparisons']['best_overall']}")

    print(f"\nResults saved to: {args.output_dir}")


if __name__ == "__main__":
    main()
