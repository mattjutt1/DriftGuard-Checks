#!/usr/bin/env python3
"""
PromptEvolver 3.0 - Evaluation Report Generator
================================================
Generate comprehensive evaluation reports combining all metrics and analyses.
Supports multiple output formats (HTML, PDF, Markdown, JSON).

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
from dataclasses import dataclass, field, asdict
import statistics

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Template, Environment, FileSystemLoader
import markdown
from weasyprint import HTML, CSS
from io import BytesIO
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ReportConfig:
    """Configuration for report generation."""

    title: str = "PromptEvolver 3.0 Evaluation Report"
    subtitle: Optional[str] = None
    author: str = "PromptEvolver Team"
    organization: str = "Matthew J. Utt"

    # Data sources
    evaluation_results: Optional[str] = None
    benchmark_results: Optional[str] = None
    human_eval_results: Optional[str] = None
    quality_metrics: Optional[str] = None

    # Output settings
    output_dir: str = "./reports"
    output_formats: List[str] = field(default_factory=lambda: ["html", "pdf", "markdown"])
    include_visualizations: bool = True
    include_raw_data: bool = False

    # Report sections
    include_executive_summary: bool = True
    include_methodology: bool = True
    include_detailed_results: bool = True
    include_recommendations: bool = True
    include_appendix: bool = False


class DataAggregator:
    """Aggregate data from multiple evaluation sources."""

    def __init__(self, config: ReportConfig):
        """Initialize data aggregator."""
        self.config = config
        self.data = {}

    def load_all_data(self) -> Dict[str, Any]:
        """Load data from all configured sources."""
        # Load evaluation results
        if self.config.evaluation_results and Path(self.config.evaluation_results).exists():
            with open(self.config.evaluation_results, 'r') as f:
                self.data['evaluation'] = json.load(f)

        # Load benchmark results
        if self.config.benchmark_results and Path(self.config.benchmark_results).exists():
            with open(self.config.benchmark_results, 'r') as f:
                self.data['benchmark'] = json.load(f)

        # Load human evaluation results
        if self.config.human_eval_results and Path(self.config.human_eval_results).exists():
            with open(self.config.human_eval_results, 'r') as f:
                self.data['human_eval'] = json.load(f)

        # Load quality metrics
        if self.config.quality_metrics and Path(self.config.quality_metrics).exists():
            with open(self.config.quality_metrics, 'r') as f:
                self.data['quality'] = json.load(f)

        return self.data

    def aggregate_metrics(self) -> Dict[str, Any]:
        """Aggregate metrics across all data sources."""
        aggregated = {
            'overall_performance': {},
            'quality_dimensions': {},
            'benchmark_scores': {},
            'human_preferences': {},
            'efficiency_metrics': {},
            'improvement_rates': {}
        }

        # Aggregate from evaluation results
        if 'evaluation' in self.data:
            eval_data = self.data['evaluation']

            aggregated['overall_performance'].update({
                'rouge_l': eval_data.get('generation_quality', {}).get('rougeL_f1', 0),
                'bleu': eval_data.get('generation_quality', {}).get('bleu', 0),
                'bert_score': eval_data.get('generation_quality', {}).get('bert_score_f1', 0),
                'diversity': eval_data.get('generation_quality', {}).get('diversity', 0),
                'fluency': eval_data.get('generation_quality', {}).get('avg_fluency', 0)
            })

            aggregated['efficiency_metrics'].update({
                'avg_inference_time': eval_data.get('efficiency', {}).get('avg_inference_time', 0),
                'throughput': eval_data.get('efficiency', {}).get('throughput_per_second', 0)
            })

        # Aggregate from benchmark results
        if 'benchmark' in self.data:
            bench_data = self.data['benchmark']

            if 'task_summaries' in bench_data:
                for task, scores in bench_data['task_summaries'].items():
                    if scores:
                        aggregated['benchmark_scores'][task] = statistics.mean(scores.values())

            if 'comparisons' in bench_data:
                aggregated['overall_performance']['best_model'] = bench_data['comparisons'].get('best_overall', 'N/A')

        # Aggregate from human evaluation
        if 'human_eval' in self.data:
            human_data = self.data['human_eval']

            if isinstance(human_data, list):
                # Calculate preference rates
                preferences = [r.get('preference', '') for r in human_data]
                total = len(preferences)
                if total > 0:
                    aggregated['human_preferences'] = {
                        'prefer_a': preferences.count('A') / total,
                        'prefer_b': preferences.count('B') / total,
                        'equal': preferences.count('equal') / total,
                        'total_evaluations': total
                    }

                # Calculate average quality scores
                quality_scores = {}
                for dim in ['clarity', 'specificity', 'actionability', 'overall']:
                    scores_a = [r.get(f'{dim}_a', 0) for r in human_data if f'{dim}_a' in r]
                    scores_b = [r.get(f'{dim}_b', 0) for r in human_data if f'{dim}_b' in r]

                    if scores_a:
                        quality_scores[f'{dim}_a'] = statistics.mean(scores_a)
                    if scores_b:
                        quality_scores[f'{dim}_b'] = statistics.mean(scores_b)

                aggregated['quality_dimensions'].update(quality_scores)

        # Calculate improvement rates
        if aggregated['overall_performance']:
            baseline = 0.5  # Assume baseline performance
            for metric, value in aggregated['overall_performance'].items():
                if isinstance(value, (int, float)):
                    improvement = ((value - baseline) / baseline) * 100
                    aggregated['improvement_rates'][metric] = improvement

        return aggregated


class VisualizationGenerator:
    """Generate visualizations for the report."""

    def __init__(self, data: Dict[str, Any]):
        """Initialize visualization generator."""
        self.data = data
        sns.set_style("whitegrid")

    def generate_all_visualizations(self) -> Dict[str, str]:
        """Generate all visualizations and return as base64 encoded strings."""
        visualizations = {}

        # Overall performance radar chart
        viz = self.create_performance_radar()
        if viz:
            visualizations['performance_radar'] = viz

        # Quality dimensions comparison
        viz = self.create_quality_comparison()
        if viz:
            visualizations['quality_comparison'] = viz

        # Benchmark scores heatmap
        viz = self.create_benchmark_heatmap()
        if viz:
            visualizations['benchmark_heatmap'] = viz

        # Human preferences pie chart
        viz = self.create_preference_pie()
        if viz:
            visualizations['preference_pie'] = viz

        # Improvement rates bar chart
        viz = self.create_improvement_bars()
        if viz:
            visualizations['improvement_bars'] = viz

        # Time series if available
        viz = self.create_time_series()
        if viz:
            visualizations['time_series'] = viz

        return visualizations

    def create_performance_radar(self) -> Optional[str]:
        """Create radar chart for overall performance metrics."""
        if 'overall_performance' not in self.data:
            return None

        metrics = self.data['overall_performance']

        # Filter numeric metrics
        numeric_metrics = {k: v for k, v in metrics.items()
                          if isinstance(v, (int, float)) and k != 'best_model'}

        if not numeric_metrics:
            return None

        # Create radar chart
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection='polar')

        # Prepare data
        categories = list(numeric_metrics.keys())
        values = list(numeric_metrics.values())

        # Normalize values to 0-1 scale
        max_val = max(values) if values else 1
        values = [v / max_val for v in values]

        # Number of variables
        num_vars = len(categories)

        # Compute angle for each axis
        angles = [n / float(num_vars) * 2 * np.pi for n in range(num_vars)]
        values += values[:1]
        angles += angles[:1]

        # Plot
        ax.plot(angles, values, 'o-', linewidth=2)
        ax.fill(angles, values, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 1)
        ax.set_title('Overall Performance Metrics', size=16, weight='bold', pad=20)
        ax.grid(True)

        # Convert to base64
        return self._fig_to_base64(fig)

    def create_quality_comparison(self) -> Optional[str]:
        """Create quality dimensions comparison chart."""
        if 'quality_dimensions' not in self.data:
            return None

        quality = self.data['quality_dimensions']

        if not quality:
            return None

        # Prepare data
        dimensions = ['clarity', 'specificity', 'actionability', 'overall']
        candidate_a = []
        candidate_b = []

        for dim in dimensions:
            candidate_a.append(quality.get(f'{dim}_a', 0))
            candidate_b.append(quality.get(f'{dim}_b', 0))

        # Create grouped bar chart
        fig, ax = plt.subplots(figsize=(10, 6))

        x = np.arange(len(dimensions))
        width = 0.35

        bars1 = ax.bar(x - width/2, candidate_a, width, label='Candidate A', color='#2196f3')
        bars2 = ax.bar(x + width/2, candidate_b, width, label='Candidate B', color='#e91e63')

        ax.set_xlabel('Quality Dimensions', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title('Quality Dimensions Comparison', fontsize=14, weight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(dimensions)
        ax.legend()
        ax.set_ylim(0, 5)

        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{height:.2f}', ha='center', va='bottom')

        plt.tight_layout()
        return self._fig_to_base64(fig)

    def create_benchmark_heatmap(self) -> Optional[str]:
        """Create benchmark scores heatmap."""
        if 'benchmark_scores' not in self.data:
            return None

        scores = self.data['benchmark_scores']

        if not scores:
            return None

        # Convert to matrix
        tasks = list(scores.keys())
        values = list(scores.values())

        # Create heatmap
        fig, ax = plt.subplots(figsize=(12, 6))

        # Reshape for heatmap (1 row for single model, or compare multiple)
        matrix = np.array(values).reshape(1, -1)

        sns.heatmap(matrix, annot=True, fmt='.3f', cmap='YlOrRd',
                   xticklabels=tasks, yticklabels=['Model'],
                   cbar_kws={'label': 'Score'}, ax=ax)

        ax.set_title('Benchmark Task Performance', fontsize=14, weight='bold')
        ax.set_xlabel('Benchmark Tasks', fontsize=12)

        plt.tight_layout()
        return self._fig_to_base64(fig)

    def create_preference_pie(self) -> Optional[str]:
        """Create human preference pie chart."""
        if 'human_preferences' not in self.data:
            return None

        prefs = self.data['human_preferences']

        if not prefs or 'total_evaluations' not in prefs:
            return None

        # Prepare data
        labels = []
        sizes = []
        colors = []

        if prefs.get('prefer_a', 0) > 0:
            labels.append(f"Prefer A ({prefs['prefer_a']:.1%})")
            sizes.append(prefs['prefer_a'])
            colors.append('#2196f3')

        if prefs.get('prefer_b', 0) > 0:
            labels.append(f"Prefer B ({prefs['prefer_b']:.1%})")
            sizes.append(prefs['prefer_b'])
            colors.append('#e91e63')

        if prefs.get('equal', 0) > 0:
            labels.append(f"Equal ({prefs['equal']:.1%})")
            sizes.append(prefs['equal'])
            colors.append('#9e9e9e')

        if not sizes:
            return None

        # Create pie chart
        fig, ax = plt.subplots(figsize=(8, 8))

        wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors,
                                          autopct='%1.1f%%', startangle=90)

        ax.set_title(f'Human Preferences (n={prefs["total_evaluations"]})',
                    fontsize=14, weight='bold')

        # Equal aspect ratio ensures circular pie
        ax.axis('equal')

        plt.tight_layout()
        return self._fig_to_base64(fig)

    def create_improvement_bars(self) -> Optional[str]:
        """Create improvement rates bar chart."""
        if 'improvement_rates' not in self.data:
            return None

        improvements = self.data['improvement_rates']

        if not improvements:
            return None

        # Prepare data
        metrics = list(improvements.keys())
        rates = list(improvements.values())

        # Create bar chart
        fig, ax = plt.subplots(figsize=(10, 6))

        colors = ['green' if r > 0 else 'red' for r in rates]
        bars = ax.bar(metrics, rates, color=colors, alpha=0.7)

        ax.set_xlabel('Metrics', fontsize=12)
        ax.set_ylabel('Improvement Rate (%)', fontsize=12)
        ax.set_title('Performance Improvement Over Baseline', fontsize=14, weight='bold')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

        # Rotate x labels if needed
        plt.xticks(rotation=45, ha='right')

        # Add value labels
        for bar, rate in zip(bars, rates):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{rate:.1f}%', ha='center',
                   va='bottom' if height > 0 else 'top')

        plt.tight_layout()
        return self._fig_to_base64(fig)

    def create_time_series(self) -> Optional[str]:
        """Create time series plot if training data available."""
        # This would plot training metrics over time if available
        # For now, return None as we don't have time series data
        return None

    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string."""
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode()
        plt.close(fig)
        return img_str


class ReportGenerator:
    """Main report generator class."""

    def __init__(self, config: ReportConfig):
        """Initialize report generator."""
        self.config = config
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load data
        self.aggregator = DataAggregator(config)
        self.raw_data = self.aggregator.load_all_data()
        self.aggregated_data = self.aggregator.aggregate_metrics()

        # Generate visualizations
        if config.include_visualizations:
            self.viz_generator = VisualizationGenerator(self.aggregated_data)
            self.visualizations = self.viz_generator.generate_all_visualizations()
        else:
            self.visualizations = {}

        # Setup Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(searchpath="./templates"),
            autoescape=True
        )

    def generate_report(self) -> Dict[str, str]:
        """Generate report in all configured formats."""
        generated_files = {}

        # Generate content
        content = self._generate_content()

        # Generate each format
        if "html" in self.config.output_formats:
            html_file = self._generate_html(content)
            generated_files['html'] = html_file

        if "pdf" in self.config.output_formats:
            pdf_file = self._generate_pdf(content)
            generated_files['pdf'] = pdf_file

        if "markdown" in self.config.output_formats:
            md_file = self._generate_markdown(content)
            generated_files['markdown'] = md_file

        if "json" in self.config.output_formats:
            json_file = self._generate_json()
            generated_files['json'] = json_file

        return generated_files

    def _generate_content(self) -> Dict[str, Any]:
        """Generate report content."""
        content = {
            'title': self.config.title,
            'subtitle': self.config.subtitle,
            'author': self.config.author,
            'organization': self.config.organization,
            'date': datetime.now().strftime('%B %d, %Y'),
            'timestamp': datetime.now().isoformat(),
            'data': self.aggregated_data,
            'visualizations': self.visualizations,
            'sections': {}
        }

        # Executive Summary
        if self.config.include_executive_summary:
            content['sections']['executive_summary'] = self._generate_executive_summary()

        # Methodology
        if self.config.include_methodology:
            content['sections']['methodology'] = self._generate_methodology()

        # Detailed Results
        if self.config.include_detailed_results:
            content['sections']['detailed_results'] = self._generate_detailed_results()

        # Recommendations
        if self.config.include_recommendations:
            content['sections']['recommendations'] = self._generate_recommendations()

        # Appendix
        if self.config.include_appendix:
            content['sections']['appendix'] = self._generate_appendix()

        return content

    def _generate_executive_summary(self) -> str:
        """Generate executive summary section."""
        summary = []

        # Overall performance
        if 'overall_performance' in self.aggregated_data:
            perf = self.aggregated_data['overall_performance']
            summary.append("## Key Performance Metrics\n")

            if 'rouge_l' in perf:
                summary.append(f"- **ROUGE-L F1**: {perf['rouge_l']:.3f}")
            if 'bleu' in perf:
                summary.append(f"- **BLEU Score**: {perf['bleu']:.3f}")
            if 'bert_score' in perf:
                summary.append(f"- **BERTScore F1**: {perf['bert_score']:.3f}")

            summary.append("")

        # Human preferences
        if 'human_preferences' in self.aggregated_data:
            prefs = self.aggregated_data['human_preferences']
            if 'total_evaluations' in prefs:
                summary.append("## Human Evaluation Results\n")
                summary.append(f"Based on {prefs['total_evaluations']} human evaluations:")

                if prefs.get('prefer_a', 0) > prefs.get('prefer_b', 0):
                    summary.append(f"- Model A preferred in {prefs['prefer_a']:.1%} of cases")
                elif prefs.get('prefer_b', 0) > prefs.get('prefer_a', 0):
                    summary.append(f"- Model B preferred in {prefs['prefer_b']:.1%} of cases")
                else:
                    summary.append(f"- No clear preference between models")

                summary.append("")

        # Key findings
        summary.append("## Key Findings\n")

        # Find best and worst metrics
        if 'overall_performance' in self.aggregated_data:
            numeric_metrics = {k: v for k, v in self.aggregated_data['overall_performance'].items()
                             if isinstance(v, (int, float))}
            if numeric_metrics:
                best_metric = max(numeric_metrics, key=numeric_metrics.get)
                worst_metric = min(numeric_metrics, key=numeric_metrics.get)

                summary.append(f"- **Strongest Performance**: {best_metric} ({numeric_metrics[best_metric]:.3f})")
                summary.append(f"- **Area for Improvement**: {worst_metric} ({numeric_metrics[worst_metric]:.3f})")

        # Efficiency
        if 'efficiency_metrics' in self.aggregated_data:
            eff = self.aggregated_data['efficiency_metrics']
            if 'avg_inference_time' in eff:
                summary.append(f"- **Average Inference Time**: {eff['avg_inference_time']:.2f} seconds")
            if 'throughput' in eff:
                summary.append(f"- **Throughput**: {eff['throughput']:.1f} samples/second")

        return "\n".join(summary)

    def _generate_methodology(self) -> str:
        """Generate methodology section."""
        methodology = [
            "## Evaluation Methodology\n",
            "### Automated Metrics\n",
            "The evaluation employed multiple automated metrics to assess prompt optimization quality:\n",
            "- **ROUGE Scores**: Measure n-gram overlap between generated and reference prompts",
            "- **BLEU Score**: Evaluate translation quality and fluency",
            "- **BERTScore**: Assess semantic similarity using contextual embeddings",
            "- **Diversity**: Measure variety in generated outputs",
            "- **Fluency**: Evaluate readability and grammatical correctness\n",

            "### Human Evaluation\n",
            "Human evaluators performed blind A/B testing to assess:",
            "- Overall preference between candidates",
            "- Quality dimensions (clarity, specificity, actionability)",
            "- Confidence levels in judgments\n",

            "### Benchmark Suite\n",
            "Models were tested on standardized benchmark tasks including:",
            "- Clarity improvement",
            "- Specificity enhancement",
            "- Creative expansion",
            "- Technical precision",
            "- Instruction following\n",

            "### Quality Metrics\n",
            "Seven-dimensional quality assessment covering:",
            "1. Clarity",
            "2. Specificity",
            "3. Actionability",
            "4. Context Relevance",
            "5. Completeness",
            "6. Coherence",
            "7. Effectiveness"
        ]

        return "\n".join(methodology)

    def _generate_detailed_results(self) -> str:
        """Generate detailed results section."""
        results = ["## Detailed Results\n"]

        # Performance metrics table
        if 'overall_performance' in self.aggregated_data:
            results.append("### Performance Metrics\n")
            results.append("| Metric | Score |")
            results.append("|--------|-------|")

            for metric, value in self.aggregated_data['overall_performance'].items():
                if isinstance(value, (int, float)):
                    results.append(f"| {metric} | {value:.3f} |")

            results.append("")

        # Quality dimensions
        if 'quality_dimensions' in self.aggregated_data:
            results.append("### Quality Dimensions\n")
            results.append("| Dimension | Candidate A | Candidate B | Difference |")
            results.append("|-----------|-------------|-------------|------------|")

            dimensions = ['clarity', 'specificity', 'actionability', 'overall']
            for dim in dimensions:
                a_score = self.aggregated_data['quality_dimensions'].get(f'{dim}_a', 0)
                b_score = self.aggregated_data['quality_dimensions'].get(f'{dim}_b', 0)
                diff = b_score - a_score
                results.append(f"| {dim.capitalize()} | {a_score:.2f} | {b_score:.2f} | {diff:+.2f} |")

            results.append("")

        # Benchmark scores
        if 'benchmark_scores' in self.aggregated_data:
            results.append("### Benchmark Performance\n")
            results.append("| Task | Score |")
            results.append("|------|-------|")

            for task, score in self.aggregated_data['benchmark_scores'].items():
                results.append(f"| {task} | {score:.3f} |")

            results.append("")

        # Improvement rates
        if 'improvement_rates' in self.aggregated_data:
            results.append("### Improvement Over Baseline\n")
            results.append("| Metric | Improvement (%) |")
            results.append("|--------|-----------------|")

            for metric, rate in self.aggregated_data['improvement_rates'].items():
                results.append(f"| {metric} | {rate:+.1f}% |")

            results.append("")

        return "\n".join(results)

    def _generate_recommendations(self) -> str:
        """Generate recommendations section."""
        recs = ["## Recommendations\n"]

        # Analyze weaknesses
        if 'overall_performance' in self.aggregated_data:
            numeric_metrics = {k: v for k, v in self.aggregated_data['overall_performance'].items()
                             if isinstance(v, (int, float))}

            # Find metrics below threshold
            weak_metrics = {k: v for k, v in numeric_metrics.items() if v < 0.7}

            if weak_metrics:
                recs.append("### Areas for Improvement\n")
                for metric, value in weak_metrics.items():
                    recs.append(f"- **{metric}** (current: {value:.3f})")

                    # Specific recommendations based on metric
                    if metric == 'clarity' or 'clarity' in metric:
                        recs.append("  - Focus on simplifying language and structure")
                        recs.append("  - Reduce ambiguous terms and jargon")
                    elif metric == 'specificity' or 'specific' in metric:
                        recs.append("  - Add more concrete details and examples")
                        recs.append("  - Include quantitative information where relevant")
                    elif metric == 'diversity':
                        recs.append("  - Increase variety in generated outputs")
                        recs.append("  - Expand training data diversity")

                recs.append("")

        # Training recommendations
        recs.append("### Training Recommendations\n")

        if 'efficiency_metrics' in self.aggregated_data:
            if self.aggregated_data['efficiency_metrics'].get('avg_inference_time', 0) > 1.0:
                recs.append("- Consider model quantization or distillation to improve inference speed")

        recs.append("- Implement iterative training with human feedback integration")
        recs.append("- Expand evaluation dataset for more comprehensive testing")
        recs.append("- Consider domain-specific fine-tuning for specialized use cases")

        # Deployment recommendations
        recs.append("\n### Deployment Recommendations\n")
        recs.append("- Implement caching for frequently optimized prompts")
        recs.append("- Set up A/B testing framework for continuous improvement")
        recs.append("- Monitor real-world performance metrics")
        recs.append("- Establish feedback collection mechanism")

        return "\n".join(recs)

    def _generate_appendix(self) -> str:
        """Generate appendix section."""
        appendix = ["## Appendix\n"]

        # Configuration details
        appendix.append("### Evaluation Configuration\n")
        appendix.append("```json")
        config_dict = asdict(self.config)
        config_dict.pop('include_raw_data', None)  # Remove sensitive fields
        appendix.append(json.dumps(config_dict, indent=2))
        appendix.append("```\n")

        # Data sources
        appendix.append("### Data Sources\n")
        for source, data in self.raw_data.items():
            if isinstance(data, dict):
                appendix.append(f"- **{source}**: {len(data)} entries")
            elif isinstance(data, list):
                appendix.append(f"- **{source}**: {len(data)} records")

        return "\n".join(appendix)

    def _generate_html(self, content: Dict[str, Any]) -> str:
        """Generate HTML report."""
        # HTML template
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        h1 { margin: 0; font-size: 2.5em; }
        h2 { color: #667eea; margin-top: 30px; }
        h3 { color: #764ba2; }
        .subtitle { font-size: 1.2em; opacity: 0.9; margin-top: 10px; }
        .meta { opacity: 0.8; margin-top: 20px; }
        .section {
            background: white;
            padding: 30px;
            margin-bottom: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .visualization {
            text-align: center;
            margin: 30px 0;
        }
        .visualization img {
            max-width: 100%;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #667eea;
            color: white;
        }
        tr:hover { background-color: #f5f5f5; }
        code {
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        pre {
            background: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
        .metric-card {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            margin: 10px;
            border-radius: 10px;
            min-width: 150px;
            text-align: center;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
        }
        .metric-label {
            opacity: 0.9;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ title }}</h1>
        {% if subtitle %}<div class="subtitle">{{ subtitle }}</div>{% endif %}
        <div class="meta">
            <div>{{ author }} | {{ organization }}</div>
            <div>{{ date }}</div>
        </div>
    </div>

    {% for section_name, section_content in sections.items() %}
    <div class="section">
        {{ section_content | markdown }}
    </div>
    {% endfor %}

    {% if visualizations %}
    <div class="section">
        <h2>Visualizations</h2>
        {% for viz_name, viz_data in visualizations.items() %}
        <div class="visualization">
            <h3>{{ viz_name | replace('_', ' ') | title }}</h3>
            <img src="data:image/png;base64,{{ viz_data }}" alt="{{ viz_name }}">
        </div>
        {% endfor %}
    </div>
    {% endif %}
</body>
</html>
        """

        # Create Jinja template
        template = Template(html_template)

        # Add markdown filter
        def markdown_filter(text):
            return markdown.markdown(text, extensions=['tables', 'fenced_code'])

        template.globals['markdown'] = markdown_filter

        # Render HTML
        html_content = template.render(**content)

        # Save to file
        output_file = self.output_dir / f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(output_file, 'w') as f:
            f.write(html_content)

        logger.info(f"HTML report saved to {output_file}")
        return str(output_file)

    def _generate_pdf(self, content: Dict[str, Any]) -> str:
        """Generate PDF report from HTML."""
        # First generate HTML
        html_file = self._generate_html(content)

        # Convert to PDF
        pdf_file = html_file.replace('.html', '.pdf')

        try:
            HTML(filename=html_file).write_pdf(pdf_file)
            logger.info(f"PDF report saved to {pdf_file}")
            return pdf_file
        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")
            logger.info("Note: PDF generation requires wkhtmltopdf to be installed")
            return ""

    def _generate_markdown(self, content: Dict[str, Any]) -> str:
        """Generate Markdown report."""
        md_content = []

        # Header
        md_content.append(f"# {content['title']}")
        if content['subtitle']:
            md_content.append(f"*{content['subtitle']}*")
        md_content.append("")
        md_content.append(f"**Author**: {content['author']}")
        md_content.append(f"**Organization**: {content['organization']}")
        md_content.append(f"**Date**: {content['date']}")
        md_content.append("")
        md_content.append("---")
        md_content.append("")

        # Sections
        for section_name, section_content in content['sections'].items():
            md_content.append(section_content)
            md_content.append("")

        # Note about visualizations
        if content['visualizations']:
            md_content.append("## Visualizations")
            md_content.append("*Note: Visualizations are available in the HTML and PDF versions of this report.*")
            md_content.append("")

        # Save to file
        output_file = self.output_dir / f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(output_file, 'w') as f:
            f.write("\n".join(md_content))

        logger.info(f"Markdown report saved to {output_file}")
        return str(output_file)

    def _generate_json(self) -> str:
        """Generate JSON report with all data."""
        # Combine all data
        json_data = {
            'metadata': {
                'title': self.config.title,
                'author': self.config.author,
                'organization': self.config.organization,
                'generated': datetime.now().isoformat()
            },
            'aggregated_metrics': self.aggregated_data
        }

        if self.config.include_raw_data:
            json_data['raw_data'] = self.raw_data

        # Save to file
        output_file = self.output_dir / f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(json_data, f, indent=2, default=str)

        logger.info(f"JSON report saved to {output_file}")
        return str(output_file)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate comprehensive evaluation reports")

    parser.add_argument(
        "--title",
        default="PromptEvolver 3.0 Evaluation Report",
        help="Report title"
    )
    parser.add_argument(
        "--subtitle",
        help="Report subtitle"
    )
    parser.add_argument(
        "--author",
        default="PromptEvolver Team",
        help="Report author"
    )
    parser.add_argument(
        "--organization",
        default="Matthew J. Utt",
        help="Organization name"
    )

    # Data sources
    parser.add_argument(
        "--evaluation",
        help="Path to evaluation results JSON"
    )
    parser.add_argument(
        "--benchmark",
        help="Path to benchmark results JSON"
    )
    parser.add_argument(
        "--human-eval",
        help="Path to human evaluation results JSON"
    )
    parser.add_argument(
        "--quality",
        help="Path to quality metrics JSON"
    )

    # Output settings
    parser.add_argument(
        "--output-dir",
        default="./reports",
        help="Output directory for reports"
    )
    parser.add_argument(
        "--formats",
        nargs="+",
        default=["html", "markdown"],
        choices=["html", "pdf", "markdown", "json"],
        help="Output formats"
    )
    parser.add_argument(
        "--no-viz",
        action="store_true",
        help="Disable visualizations"
    )
    parser.add_argument(
        "--include-raw",
        action="store_true",
        help="Include raw data in JSON output"
    )

    # Report sections
    parser.add_argument(
        "--no-summary",
        action="store_true",
        help="Exclude executive summary"
    )
    parser.add_argument(
        "--no-methodology",
        action="store_true",
        help="Exclude methodology section"
    )
    parser.add_argument(
        "--no-recommendations",
        action="store_true",
        help="Exclude recommendations"
    )
    parser.add_argument(
        "--include-appendix",
        action="store_true",
        help="Include appendix"
    )

    args = parser.parse_args()

    # Create configuration
    config = ReportConfig(
        title=args.title,
        subtitle=args.subtitle,
        author=args.author,
        organization=args.organization,
        evaluation_results=args.evaluation,
        benchmark_results=args.benchmark,
        human_eval_results=args.human_eval,
        quality_metrics=args.quality,
        output_dir=args.output_dir,
        output_formats=args.formats,
        include_visualizations=not args.no_viz,
        include_raw_data=args.include_raw,
        include_executive_summary=not args.no_summary,
        include_methodology=not args.no_methodology,
        include_recommendations=not args.no_recommendations,
        include_appendix=args.include_appendix
    )

    # Generate report
    generator = ReportGenerator(config)
    generated_files = generator.generate_report()

    # Print results
    print("\n" + "=" * 60)
    print("REPORT GENERATION COMPLETE")
    print("=" * 60)

    for format_type, file_path in generated_files.items():
        if file_path:
            print(f"{format_type.upper()}: {file_path}")

    print("\nReports saved to:", args.output_dir)


if __name__ == "__main__":
    main()
