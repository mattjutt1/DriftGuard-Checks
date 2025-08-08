#!/usr/bin/env python3
"""
PromptEvolver 3.0 - Human Evaluation Interface
===============================================
Interactive interface for human evaluation of prompt optimizations.
Supports A/B testing, blind evaluation, and preference collection.

Copyright (c) 2025 Matthew J. Utt
"""

import os
import sys
import json
import random
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field, asdict
import hashlib
import statistics
from collections import defaultdict

import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.text import Text
from rich.markdown import Markdown
import streamlit as st

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rich console for CLI interface
console = Console()


@dataclass
class EvaluationTask:
    """Single evaluation task for human review."""

    task_id: str
    original_prompt: str
    candidate_a: str
    candidate_b: str
    context: Optional[str] = None
    domain: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EvaluationTask':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class EvaluationResult:
    """Result of human evaluation."""

    task_id: str
    evaluator_id: str
    timestamp: str
    preference: str  # 'A', 'B', or 'equal'
    confidence: int  # 1-5 scale

    # Quality scores (1-5 scale)
    clarity_a: Optional[int] = None
    clarity_b: Optional[int] = None
    specificity_a: Optional[int] = None
    specificity_b: Optional[int] = None
    actionability_a: Optional[int] = None
    actionability_b: Optional[int] = None
    overall_a: Optional[int] = None
    overall_b: Optional[int] = None

    # Optional feedback
    comments: Optional[str] = None
    issues_a: Optional[List[str]] = None
    issues_b: Optional[List[str]] = None

    time_spent_seconds: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class HumanEvaluationCLI:
    """Command-line interface for human evaluation."""

    def __init__(self, tasks_file: str, output_file: str = "evaluation_results.json"):
        """
        Initialize CLI evaluator.

        Args:
            tasks_file: Path to JSON file with evaluation tasks
            output_file: Path to save results
        """
        self.tasks_file = Path(tasks_file)
        self.output_file = Path(output_file)
        self.console = Console()

        # Load tasks
        self.tasks = self._load_tasks()
        self.current_task_index = 0

        # Load existing results if any
        self.results = self._load_results()

        # Evaluator info
        self.evaluator_id = None

    def _load_tasks(self) -> List[EvaluationTask]:
        """Load evaluation tasks from file."""
        if not self.tasks_file.exists():
            logger.error(f"Tasks file not found: {self.tasks_file}")
            return []

        with open(self.tasks_file, 'r') as f:
            data = json.load(f)

        tasks = []
        for task_data in data:
            # Randomize A/B assignment
            if random.random() < 0.5:
                # Swap candidates for blind evaluation
                task_data['candidate_a'], task_data['candidate_b'] = \
                    task_data.get('candidate_b', ''), task_data.get('candidate_a', '')
                task_data['metadata'] = task_data.get('metadata', {})
                task_data['metadata']['swapped'] = True

            tasks.append(EvaluationTask.from_dict(task_data))

        return tasks

    def _load_results(self) -> List[EvaluationResult]:
        """Load existing results if file exists."""
        if not self.output_file.exists():
            return []

        with open(self.output_file, 'r') as f:
            data = json.load(f)

        return [EvaluationResult(**r) for r in data]

    def _save_results(self):
        """Save results to file."""
        with open(self.output_file, 'w') as f:
            json.dump([r.to_dict() for r in self.results], f, indent=2)

        logger.info(f"Results saved to {self.output_file}")

    def _display_task(self, task: EvaluationTask):
        """Display evaluation task in terminal."""
        self.console.clear()

        # Header
        self.console.print(Panel.fit(
            f"[bold cyan]Evaluation Task {self.current_task_index + 1} of {len(self.tasks)}[/bold cyan]",
            title="PromptEvolver Human Evaluation",
            border_style="cyan"
        ))

        # Context if available
        if task.context:
            self.console.print("\n[bold yellow]Context:[/bold yellow]")
            self.console.print(Panel(task.context, border_style="yellow"))

        # Original prompt
        self.console.print("\n[bold green]Original Prompt:[/bold green]")
        self.console.print(Panel(task.original_prompt, border_style="green"))

        # Candidate A
        self.console.print("\n[bold blue]Candidate A:[/bold blue]")
        self.console.print(Panel(task.candidate_a, border_style="blue"))

        # Candidate B
        self.console.print("\n[bold magenta]Candidate B:[/bold magenta]")
        self.console.print(Panel(task.candidate_b, border_style="magenta"))

    def _collect_preference(self) -> Tuple[str, int]:
        """Collect preference and confidence."""
        # Preference
        preference = Prompt.ask(
            "\n[bold]Which candidate is better?[/bold]",
            choices=["A", "B", "equal"],
            default="equal"
        )

        # Confidence
        confidence = IntPrompt.ask(
            "[bold]Confidence level?[/bold] (1=very low, 5=very high)",
            default=3
        )
        confidence = max(1, min(5, confidence))

        return preference, confidence

    def _collect_quality_scores(self) -> Dict[str, int]:
        """Collect detailed quality scores."""
        scores = {}

        self.console.print("\n[bold]Rate each candidate (1-5 scale):[/bold]")

        dimensions = [
            ("clarity", "How clear and understandable?"),
            ("specificity", "How specific and detailed?"),
            ("actionability", "How actionable and directive?"),
            ("overall", "Overall quality?")
        ]

        for dim, description in dimensions:
            self.console.print(f"\n[yellow]{description}[/yellow]")

            scores[f"{dim}_a"] = IntPrompt.ask(
                f"  Candidate A {dim}",
                default=3
            )
            scores[f"{dim}_a"] = max(1, min(5, scores[f"{dim}_a"]))

            scores[f"{dim}_b"] = IntPrompt.ask(
                f"  Candidate B {dim}",
                default=3
            )
            scores[f"{dim}_b"] = max(1, min(5, scores[f"{dim}_b"]))

        return scores

    def _collect_feedback(self) -> Tuple[str, List[str], List[str]]:
        """Collect optional feedback."""
        # Comments
        comments = Prompt.ask(
            "\n[bold]Any comments?[/bold] (press Enter to skip)",
            default=""
        )

        # Issues
        issues_a = []
        issues_b = []

        if Confirm.ask("Any issues with Candidate A?", default=False):
            issue_types = ["unclear", "too_vague", "too_long", "missing_info", "other"]
            for issue in issue_types:
                if Confirm.ask(f"  {issue}?", default=False):
                    issues_a.append(issue)

        if Confirm.ask("Any issues with Candidate B?", default=False):
            issue_types = ["unclear", "too_vague", "too_long", "missing_info", "other"]
            for issue in issue_types:
                if Confirm.ask(f"  {issue}?", default=False):
                    issues_b.append(issue)

        return comments, issues_a, issues_b

    def evaluate_task(self, task: EvaluationTask) -> EvaluationResult:
        """Evaluate a single task."""
        start_time = datetime.now()

        # Display task
        self._display_task(task)

        # Collect evaluation
        preference, confidence = self._collect_preference()

        # Detailed scores
        if Confirm.ask("\nProvide detailed quality scores?", default=True):
            scores = self._collect_quality_scores()
        else:
            scores = {}

        # Feedback
        if Confirm.ask("\nProvide additional feedback?", default=False):
            comments, issues_a, issues_b = self._collect_feedback()
        else:
            comments, issues_a, issues_b = "", [], []

        # Calculate time spent
        time_spent = (datetime.now() - start_time).total_seconds()

        # Create result
        result = EvaluationResult(
            task_id=task.task_id,
            evaluator_id=self.evaluator_id,
            timestamp=datetime.now().isoformat(),
            preference=preference,
            confidence=confidence,
            comments=comments,
            issues_a=issues_a,
            issues_b=issues_b,
            time_spent_seconds=time_spent,
            **scores
        )

        return result

    def run(self):
        """Run the evaluation interface."""
        # Welcome
        self.console.print(Panel.fit(
            "[bold green]Welcome to PromptEvolver Human Evaluation Interface[/bold green]\n\n"
            "You will be shown pairs of optimized prompts and asked to evaluate them.\n"
            "The evaluation is blind - you won't know which model generated which prompt.",
            title="Instructions",
            border_style="green"
        ))

        # Get evaluator ID
        self.evaluator_id = Prompt.ask("\n[bold]Enter your evaluator ID[/bold]")

        # Check for resume
        completed_tasks = {r.task_id for r in self.results
                          if r.evaluator_id == self.evaluator_id}

        if completed_tasks:
            self.console.print(f"\n[yellow]You have already evaluated {len(completed_tasks)} tasks.[/yellow]")
            if Confirm.ask("Resume from where you left off?", default=True):
                self.tasks = [t for t in self.tasks if t.task_id not in completed_tasks]

        # Main evaluation loop
        for i, task in enumerate(self.tasks):
            self.current_task_index = i

            result = self.evaluate_task(task)
            self.results.append(result)

            # Save after each task
            self._save_results()

            # Ask to continue
            if i < len(self.tasks) - 1:
                if not Confirm.ask("\n[bold]Continue to next task?[/bold]", default=True):
                    break

        # Summary
        self.console.print("\n" + "=" * 60)
        self.console.print("[bold green]Evaluation Complete![/bold green]")
        self.console.print(f"Tasks evaluated: {len([r for r in self.results if r.evaluator_id == self.evaluator_id])}")
        self.console.print(f"Results saved to: {self.output_file}")


class HumanEvaluationWeb:
    """Streamlit web interface for human evaluation."""

    @staticmethod
    def create_app():
        """Create Streamlit application."""
        st.set_page_config(
            page_title="PromptEvolver Human Evaluation",
            page_icon="🎯",
            layout="wide"
        )

        # Custom CSS
        st.markdown("""
        <style>
        .prompt-box {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }
        .candidate-a {
            background-color: #e3f2fd;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #2196f3;
        }
        .candidate-b {
            background-color: #fce4ec;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #e91e63;
        }
        </style>
        """, unsafe_allow_html=True)

        # Title
        st.title("🎯 PromptEvolver Human Evaluation Interface")
        st.markdown("---")

        # Sidebar
        with st.sidebar:
            st.header("Evaluation Settings")

            evaluator_id = st.text_input("Evaluator ID", key="evaluator_id")

            # Load tasks
            tasks_file = st.file_uploader(
                "Upload evaluation tasks (JSON)",
                type=['json'],
                key="tasks_file"
            )

            if tasks_file:
                tasks_data = json.load(tasks_file)
                st.success(f"Loaded {len(tasks_data)} tasks")

                # Task selector
                task_index = st.number_input(
                    "Task Number",
                    min_value=1,
                    max_value=len(tasks_data),
                    value=1,
                    key="task_index"
                ) - 1
            else:
                tasks_data = []
                task_index = 0

            st.markdown("---")
            st.header("Progress")

            if 'results' not in st.session_state:
                st.session_state.results = []

            completed = len(st.session_state.results)
            total = len(tasks_data)

            if total > 0:
                progress = completed / total
                st.progress(progress)
                st.text(f"{completed} / {total} completed")

        # Main content
        if tasks_data and evaluator_id:
            task = tasks_data[task_index]

            # Context
            if 'context' in task and task['context']:
                st.info("**Context:**")
                st.markdown(f"<div class='prompt-box'>{task['context']}</div>",
                          unsafe_allow_html=True)

            # Original prompt
            st.success("**Original Prompt:**")
            st.markdown(f"<div class='prompt-box'>{task['original_prompt']}</div>",
                      unsafe_allow_html=True)

            # Candidates in columns
            col1, col2 = st.columns(2)

            with col1:
                st.info("**Candidate A:**")
                st.markdown(f"<div class='candidate-a'>{task.get('candidate_a', '')}</div>",
                          unsafe_allow_html=True)

            with col2:
                st.warning("**Candidate B:**")
                st.markdown(f"<div class='candidate-b'>{task.get('candidate_b', '')}</div>",
                          unsafe_allow_html=True)

            st.markdown("---")

            # Evaluation form
            st.header("Your Evaluation")

            col1, col2, col3 = st.columns(3)

            with col1:
                preference = st.radio(
                    "Which candidate is better?",
                    ["A", "B", "Equal"],
                    key=f"pref_{task_index}"
                )

            with col2:
                confidence = st.slider(
                    "Confidence level",
                    min_value=1,
                    max_value=5,
                    value=3,
                    key=f"conf_{task_index}"
                )

            with col3:
                st.write("Confidence Scale:")
                st.caption("1 = Very Low")
                st.caption("3 = Moderate")
                st.caption("5 = Very High")

            # Detailed scores
            with st.expander("Detailed Quality Scores (Optional)"):
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Candidate A")
                    clarity_a = st.slider("Clarity", 1, 5, 3, key=f"clarity_a_{task_index}")
                    specificity_a = st.slider("Specificity", 1, 5, 3, key=f"spec_a_{task_index}")
                    actionability_a = st.slider("Actionability", 1, 5, 3, key=f"action_a_{task_index}")
                    overall_a = st.slider("Overall", 1, 5, 3, key=f"overall_a_{task_index}")

                with col2:
                    st.subheader("Candidate B")
                    clarity_b = st.slider("Clarity", 1, 5, 3, key=f"clarity_b_{task_index}")
                    specificity_b = st.slider("Specificity", 1, 5, 3, key=f"spec_b_{task_index}")
                    actionability_b = st.slider("Actionability", 1, 5, 3, key=f"action_b_{task_index}")
                    overall_b = st.slider("Overall", 1, 5, 3, key=f"overall_b_{task_index}")

            # Comments
            comments = st.text_area(
                "Additional comments (optional)",
                key=f"comments_{task_index}"
            )

            # Submit button
            col1, col2, col3 = st.columns(3)

            with col2:
                if st.button("Submit Evaluation", type="primary", key=f"submit_{task_index}"):
                    # Create result
                    result = {
                        'task_id': task.get('task_id', f"task_{task_index}"),
                        'evaluator_id': evaluator_id,
                        'timestamp': datetime.now().isoformat(),
                        'preference': preference.lower(),
                        'confidence': confidence,
                        'clarity_a': clarity_a,
                        'clarity_b': clarity_b,
                        'specificity_a': specificity_a,
                        'specificity_b': specificity_b,
                        'actionability_a': actionability_a,
                        'actionability_b': actionability_b,
                        'overall_a': overall_a,
                        'overall_b': overall_b,
                        'comments': comments
                    }

                    st.session_state.results.append(result)
                    st.success("✅ Evaluation submitted!")

                    # Auto-advance to next task
                    if task_index < len(tasks_data) - 1:
                        st.rerun()

            # Export results
            if st.session_state.results:
                st.markdown("---")
                st.header("Export Results")

                results_json = json.dumps(st.session_state.results, indent=2)

                st.download_button(
                    label="📥 Download Results (JSON)",
                    data=results_json,
                    file_name=f"evaluation_results_{evaluator_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

        elif not evaluator_id:
            st.warning("Please enter your Evaluator ID in the sidebar")

        elif not tasks_data:
            st.info("Please upload evaluation tasks JSON file in the sidebar")


class EvaluationAnalyzer:
    """Analyze human evaluation results."""

    def __init__(self, results_file: str):
        """
        Initialize analyzer.

        Args:
            results_file: Path to results JSON file
        """
        self.results_file = Path(results_file)
        self.results = self._load_results()

    def _load_results(self) -> List[EvaluationResult]:
        """Load evaluation results."""
        with open(self.results_file, 'r') as f:
            data = json.load(f)

        return [EvaluationResult(**r) if isinstance(r, dict) else r for r in data]

    def calculate_agreement(self) -> Dict[str, Any]:
        """Calculate inter-rater agreement metrics."""
        # Group by task
        task_results = defaultdict(list)
        for result in self.results:
            task_results[result.task_id].append(result)

        # Calculate agreement
        agreements = []
        for task_id, evaluations in task_results.items():
            if len(evaluations) > 1:
                preferences = [e.preference for e in evaluations]
                # Simple agreement rate
                most_common = max(set(preferences), key=preferences.count)
                agreement_rate = preferences.count(most_common) / len(preferences)
                agreements.append(agreement_rate)

        return {
            'mean_agreement': statistics.mean(agreements) if agreements else 0,
            'median_agreement': statistics.median(agreements) if agreements else 0,
            'min_agreement': min(agreements) if agreements else 0,
            'max_agreement': max(agreements) if agreements else 0,
            'tasks_with_full_agreement': sum(1 for a in agreements if a == 1.0),
            'tasks_with_disagreement': sum(1 for a in agreements if a < 1.0)
        }

    def calculate_preferences(self) -> Dict[str, Any]:
        """Calculate preference statistics."""
        preferences = [r.preference for r in self.results]

        return {
            'total_evaluations': len(preferences),
            'prefer_a': preferences.count('A') + preferences.count('a'),
            'prefer_b': preferences.count('B') + preferences.count('b'),
            'prefer_equal': preferences.count('equal'),
            'preference_rate_a': (preferences.count('A') + preferences.count('a')) / len(preferences) if preferences else 0,
            'preference_rate_b': (preferences.count('B') + preferences.count('b')) / len(preferences) if preferences else 0,
            'equal_rate': preferences.count('equal') / len(preferences) if preferences else 0
        }

    def calculate_quality_scores(self) -> Dict[str, Any]:
        """Calculate average quality scores."""
        scores = {
            'clarity_a': [],
            'clarity_b': [],
            'specificity_a': [],
            'specificity_b': [],
            'actionability_a': [],
            'actionability_b': [],
            'overall_a': [],
            'overall_b': []
        }

        for result in self.results:
            for key in scores:
                value = getattr(result, key, None)
                if value is not None:
                    scores[key].append(value)

        averages = {}
        for key, values in scores.items():
            if values:
                averages[f'avg_{key}'] = statistics.mean(values)
                averages[f'std_{key}'] = statistics.stdev(values) if len(values) > 1 else 0

        return averages

    def calculate_confidence(self) -> Dict[str, Any]:
        """Calculate confidence statistics."""
        confidences = [r.confidence for r in self.results if r.confidence is not None]

        if not confidences:
            return {}

        return {
            'mean_confidence': statistics.mean(confidences),
            'median_confidence': statistics.median(confidences),
            'std_confidence': statistics.stdev(confidences) if len(confidences) > 1 else 0,
            'high_confidence_rate': sum(1 for c in confidences if c >= 4) / len(confidences)
        }

    def calculate_time_stats(self) -> Dict[str, Any]:
        """Calculate time statistics."""
        times = [r.time_spent_seconds for r in self.results
                if r.time_spent_seconds is not None]

        if not times:
            return {}

        return {
            'mean_time_seconds': statistics.mean(times),
            'median_time_seconds': statistics.median(times),
            'total_time_minutes': sum(times) / 60,
            'evaluations_per_hour': 3600 / statistics.mean(times) if times else 0
        }

    def generate_report(self) -> str:
        """Generate analysis report."""
        report = []
        report.append("=" * 60)
        report.append("HUMAN EVALUATION ANALYSIS REPORT")
        report.append("=" * 60)
        report.append("")

        # Preferences
        prefs = self.calculate_preferences()
        report.append("PREFERENCE STATISTICS")
        report.append("-" * 40)
        report.append(f"Total Evaluations: {prefs.get('total_evaluations', 0)}")
        report.append(f"Prefer A: {prefs.get('prefer_a', 0)} ({prefs.get('preference_rate_a', 0):.1%})")
        report.append(f"Prefer B: {prefs.get('prefer_b', 0)} ({prefs.get('preference_rate_b', 0):.1%})")
        report.append(f"Equal: {prefs.get('prefer_equal', 0)} ({prefs.get('equal_rate', 0):.1%})")
        report.append("")

        # Quality scores
        quality = self.calculate_quality_scores()
        if quality:
            report.append("QUALITY SCORES (1-5 scale)")
            report.append("-" * 40)

            dimensions = ['clarity', 'specificity', 'actionability', 'overall']
            for dim in dimensions:
                a_key = f'avg_{dim}_a'
                b_key = f'avg_{dim}_b'
                if a_key in quality and b_key in quality:
                    report.append(f"{dim.capitalize()}:")
                    report.append(f"  Candidate A: {quality[a_key]:.2f}")
                    report.append(f"  Candidate B: {quality[b_key]:.2f}")
                    diff = quality[b_key] - quality[a_key]
                    report.append(f"  Difference: {diff:+.2f}")
            report.append("")

        # Agreement
        agreement = self.calculate_agreement()
        if agreement.get('mean_agreement') is not None:
            report.append("INTER-RATER AGREEMENT")
            report.append("-" * 40)
            report.append(f"Mean Agreement: {agreement['mean_agreement']:.1%}")
            report.append(f"Tasks with Full Agreement: {agreement['tasks_with_full_agreement']}")
            report.append(f"Tasks with Disagreement: {agreement['tasks_with_disagreement']}")
            report.append("")

        # Confidence
        confidence = self.calculate_confidence()
        if confidence:
            report.append("CONFIDENCE LEVELS")
            report.append("-" * 40)
            report.append(f"Mean Confidence: {confidence['mean_confidence']:.2f}/5")
            report.append(f"High Confidence Rate: {confidence['high_confidence_rate']:.1%}")
            report.append("")

        # Time stats
        time_stats = self.calculate_time_stats()
        if time_stats:
            report.append("TIME STATISTICS")
            report.append("-" * 40)
            report.append(f"Mean Time per Evaluation: {time_stats['mean_time_seconds']:.1f} seconds")
            report.append(f"Total Time: {time_stats['total_time_minutes']:.1f} minutes")
            report.append(f"Evaluations per Hour: {time_stats['evaluations_per_hour']:.1f}")
            report.append("")

        report.append("=" * 60)

        return "\n".join(report)


def create_evaluation_tasks(
    test_data_file: str,
    model_a_results: str,
    model_b_results: str,
    output_file: str,
    num_tasks: int = 100
):
    """
    Create evaluation tasks from model outputs.

    Args:
        test_data_file: Path to test data
        model_a_results: Path to model A results
        model_b_results: Path to model B results
        output_file: Path to save tasks
        num_tasks: Number of tasks to create
    """
    # Load data
    with open(test_data_file, 'r') as f:
        test_data = json.load(f)

    with open(model_a_results, 'r') as f:
        results_a = json.load(f)

    with open(model_b_results, 'r') as f:
        results_b = json.load(f)

    # Create tasks
    tasks = []

    # Sample if needed
    if len(test_data) > num_tasks:
        indices = random.sample(range(len(test_data)), num_tasks)
    else:
        indices = range(len(test_data))

    for i in indices:
        task_id = hashlib.md5(f"task_{i}".encode()).hexdigest()[:8]

        task = {
            'task_id': task_id,
            'original_prompt': test_data[i].get('original_prompt', ''),
            'candidate_a': results_a[i] if i < len(results_a) else '',
            'candidate_b': results_b[i] if i < len(results_b) else '',
            'context': test_data[i].get('context', ''),
            'domain': test_data[i].get('domain', 'general'),
            'metadata': {
                'source_index': i
            }
        }

        tasks.append(task)

    # Save tasks
    with open(output_file, 'w') as f:
        json.dump(tasks, f, indent=2)

    logger.info(f"Created {len(tasks)} evaluation tasks in {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Human evaluation interface for PromptEvolver")

    subparsers = parser.add_subparsers(dest='mode', help='Operation mode')

    # CLI evaluation mode
    cli_parser = subparsers.add_parser('evaluate', help='Run CLI evaluation')
    cli_parser.add_argument('tasks_file', help='Path to evaluation tasks JSON')
    cli_parser.add_argument('--output', default='evaluation_results.json',
                           help='Output file for results')

    # Web interface mode
    web_parser = subparsers.add_parser('web', help='Run web interface')
    web_parser.add_argument('--port', type=int, default=8501,
                           help='Port for web server')

    # Create tasks mode
    create_parser = subparsers.add_parser('create-tasks', help='Create evaluation tasks')
    create_parser.add_argument('test_data', help='Path to test data')
    create_parser.add_argument('model_a', help='Path to model A results')
    create_parser.add_argument('model_b', help='Path to model B results')
    create_parser.add_argument('--output', default='evaluation_tasks.json',
                              help='Output file for tasks')
    create_parser.add_argument('--num-tasks', type=int, default=100,
                              help='Number of tasks to create')

    # Analyze mode
    analyze_parser = subparsers.add_parser('analyze', help='Analyze evaluation results')
    analyze_parser.add_argument('results_file', help='Path to results JSON')
    analyze_parser.add_argument('--output', help='Output file for report')

    args = parser.parse_args()

    if args.mode == 'evaluate':
        # Run CLI evaluation
        evaluator = HumanEvaluationCLI(args.tasks_file, args.output)
        evaluator.run()

    elif args.mode == 'web':
        # Run web interface
        print(f"Starting web interface on port {args.port}")
        print("Run: streamlit run human_eval_interface.py web")
        HumanEvaluationWeb.create_app()

    elif args.mode == 'create-tasks':
        # Create evaluation tasks
        create_evaluation_tasks(
            args.test_data,
            args.model_a,
            args.model_b,
            args.output,
            args.num_tasks
        )

    elif args.mode == 'analyze':
        # Analyze results
        analyzer = EvaluationAnalyzer(args.results_file)
        report = analyzer.generate_report()

        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"Report saved to {args.output}")
        else:
            print(report)

    else:
        parser.print_help()


if __name__ == "__main__":
    # Check if running in Streamlit
    if 'streamlit' in sys.modules:
        HumanEvaluationWeb.create_app()
    else:
        main()
