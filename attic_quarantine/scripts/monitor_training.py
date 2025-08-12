#!/usr/bin/env python3
"""
PromptEvolver 3.0 - Training Monitor
=====================================
Real-time monitoring of training progress with TensorBoard, W&B, and custom metrics.

Copyright (c) 2025 Matthew J. Utt
"""

import os
import sys
import json
import time
import psutil
import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from collections import deque
import subprocess

import torch
import numpy as np
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rich console for pretty output
console = Console()


class TrainingMonitor:
    """Monitor training progress and system resources."""

    def __init__(self, log_dir: str, refresh_rate: int = 5):
        """
        Initialize training monitor.

        Args:
            log_dir: Directory containing training logs
            refresh_rate: Refresh rate in seconds
        """
        self.log_dir = Path(log_dir)
        self.refresh_rate = refresh_rate
        self.console = Console()

        # Metrics storage
        self.metrics_history = {
            'loss': deque(maxlen=100),
            'eval_loss': deque(maxlen=100),
            'learning_rate': deque(maxlen=100),
            'gradient_norm': deque(maxlen=100),
        }

        # System metrics
        self.system_history = {
            'cpu_percent': deque(maxlen=100),
            'memory_percent': deque(maxlen=100),
            'gpu_memory': deque(maxlen=100),
            'gpu_utilization': deque(maxlen=100),
        }

        # Training state
        self.current_epoch = 0
        self.current_step = 0
        self.total_steps = 0
        self.best_eval_loss = float('inf')
        self.training_start_time = None

    def get_tensorboard_metrics(self) -> Dict[str, float]:
        """Read metrics from TensorBoard logs."""
        metrics = {}

        # Find the latest event file
        event_files = list(self.log_dir.glob("events.out.tfevents.*"))
        if not event_files:
            return metrics

        latest_event_file = max(event_files, key=lambda p: p.stat().st_mtime)

        try:
            # Load events
            ea = EventAccumulator(str(latest_event_file))
            ea.Reload()

            # Get scalar tags
            scalar_tags = ea.Tags().get('scalars', [])

            # Extract latest values for each metric
            for tag in scalar_tags:
                events = ea.Scalars(tag)
                if events:
                    latest_event = events[-1]
                    metrics[tag] = latest_event.value

                    # Update step count
                    if latest_event.step > self.current_step:
                        self.current_step = latest_event.step

        except Exception as e:
            logger.warning(f"Failed to read TensorBoard logs: {e}")

        return metrics

    def get_checkpoint_info(self) -> Dict[str, Any]:
        """Get information about saved checkpoints."""
        checkpoint_info = {
            'latest_checkpoint': None,
            'best_checkpoint': None,
            'num_checkpoints': 0,
            'checkpoint_sizes': []
        }

        # Find checkpoint directories
        checkpoint_dirs = [d for d in self.log_dir.parent.glob("checkpoint-*") if d.is_dir()]

        if checkpoint_dirs:
            checkpoint_info['num_checkpoints'] = len(checkpoint_dirs)

            # Get latest checkpoint
            latest = max(checkpoint_dirs, key=lambda p: p.stat().st_mtime)
            checkpoint_info['latest_checkpoint'] = latest.name

            # Get checkpoint sizes
            for ckpt_dir in checkpoint_dirs:
                size = sum(f.stat().st_size for f in ckpt_dir.rglob("*") if f.is_file())
                checkpoint_info['checkpoint_sizes'].append({
                    'name': ckpt_dir.name,
                    'size_mb': size / (1024 * 1024)
                })

        return checkpoint_info

    def get_system_metrics(self) -> Dict[str, float]:
        """Get current system resource usage."""
        metrics = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
        }

        # Try to get GPU metrics
        if torch.cuda.is_available():
            try:
                # Use nvidia-smi for GPU metrics
                result = subprocess.run(
                    ['nvidia-smi', '--query-gpu=memory.used,memory.total,utilization.gpu',
                     '--format=csv,noheader,nounits'],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    values = result.stdout.strip().split(', ')
                    if len(values) >= 3:
                        mem_used = float(values[0])
                        mem_total = float(values[1])
                        gpu_util = float(values[2])

                        metrics['gpu_memory_mb'] = mem_used
                        metrics['gpu_memory_percent'] = (mem_used / mem_total) * 100
                        metrics['gpu_utilization'] = gpu_util

            except Exception as e:
                logger.debug(f"Failed to get GPU metrics: {e}")

        return metrics

    def estimate_time_remaining(self) -> Optional[timedelta]:
        """Estimate time remaining for training."""
        if not self.training_start_time or self.current_step == 0:
            return None

        elapsed = datetime.now() - self.training_start_time
        steps_per_second = self.current_step / elapsed.total_seconds()

        if steps_per_second > 0 and self.total_steps > 0:
            remaining_steps = self.total_steps - self.current_step
            remaining_seconds = remaining_steps / steps_per_second
            return timedelta(seconds=int(remaining_seconds))

        return None

    def create_dashboard(self) -> Layout:
        """Create rich dashboard layout."""
        layout = Layout()

        # Main layout structure
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )

        # Body layout
        layout["body"].split_row(
            Layout(name="metrics", ratio=2),
            Layout(name="system", ratio=1)
        )

        # Metrics layout
        layout["metrics"].split_column(
            Layout(name="training_metrics"),
            Layout(name="evaluation_metrics")
        )

        return layout

    def render_header(self) -> Panel:
        """Render dashboard header."""
        elapsed = ""
        if self.training_start_time:
            elapsed_time = datetime.now() - self.training_start_time
            elapsed = f"Elapsed: {str(elapsed_time).split('.')[0]}"

        remaining = ""
        time_remaining = self.estimate_time_remaining()
        if time_remaining:
            remaining = f"Remaining: {str(time_remaining).split('.')[0]}"

        header_text = Text(
            f"🚀 PromptEvolver 3.0 Training Monitor | Step {self.current_step}/{self.total_steps} | {elapsed} | {remaining}",
            style="bold cyan"
        )

        return Panel(header_text, box_style="blue")

    def render_training_metrics(self, metrics: Dict[str, float]) -> Panel:
        """Render training metrics panel."""
        table = Table(title="Training Metrics", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Value", style="green")
        table.add_column("Trend", style="yellow", width=10)

        # Add metrics to table
        metric_mapping = {
            'train/loss': ('Training Loss', '{:.4f}'),
            'train/learning_rate': ('Learning Rate', '{:.2e}'),
            'train/grad_norm': ('Gradient Norm', '{:.4f}'),
            'train/epoch': ('Epoch', '{:.2f}'),
        }

        for key, (display_name, fmt) in metric_mapping.items():
            if key in metrics:
                value = metrics[key]
                formatted_value = fmt.format(value)

                # Calculate trend
                trend = "→"
                history_key = key.split('/')[-1]
                if history_key in self.metrics_history:
                    history = self.metrics_history[history_key]
                    history.append(value)

                    if len(history) > 1:
                        if value > history[-2]:
                            trend = "↑"
                        elif value < history[-2]:
                            trend = "↓"

                table.add_row(display_name, formatted_value, trend)

        return Panel(table, title="📊 Training Progress", border_style="green")

    def render_evaluation_metrics(self, metrics: Dict[str, float]) -> Panel:
        """Render evaluation metrics panel."""
        table = Table(title="Evaluation Metrics", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Value", style="green")
        table.add_column("Best", style="blue")

        # Add evaluation metrics
        eval_loss = metrics.get('eval/loss', None)
        if eval_loss is not None:
            if eval_loss < self.best_eval_loss:
                self.best_eval_loss = eval_loss
                best_marker = "🏆"
            else:
                best_marker = ""

            table.add_row("Eval Loss", f"{eval_loss:.4f}", f"{self.best_eval_loss:.4f} {best_marker}")

        # Add other eval metrics if available
        eval_metrics = {
            'eval/perplexity': 'Perplexity',
            'eval/accuracy': 'Accuracy',
            'eval/bleu': 'BLEU Score',
        }

        for key, name in eval_metrics.items():
            if key in metrics:
                table.add_row(name, f"{metrics[key]:.4f}", "-")

        return Panel(table, title="📈 Evaluation Results", border_style="yellow")

    def render_system_metrics(self, system_metrics: Dict[str, float]) -> Panel:
        """Render system resource usage panel."""
        table = Table(title="System Resources", show_header=True, header_style="bold magenta")
        table.add_column("Resource", style="cyan", width=20)
        table.add_column("Usage", style="green")
        table.add_column("Status", width=10)

        # CPU usage
        cpu_percent = system_metrics.get('cpu_percent', 0)
        cpu_status = "🟢" if cpu_percent < 70 else "🟡" if cpu_percent < 90 else "🔴"
        table.add_row("CPU", f"{cpu_percent:.1f}%", cpu_status)

        # Memory usage
        mem_percent = system_metrics.get('memory_percent', 0)
        mem_status = "🟢" if mem_percent < 70 else "🟡" if mem_percent < 90 else "🔴"
        table.add_row("Memory", f"{mem_percent:.1f}%", mem_status)

        # GPU usage
        if 'gpu_memory_percent' in system_metrics:
            gpu_mem = system_metrics['gpu_memory_percent']
            gpu_status = "🟢" if gpu_mem < 70 else "🟡" if gpu_mem < 90 else "🔴"
            table.add_row("GPU Memory", f"{gpu_mem:.1f}%", gpu_status)

            gpu_util = system_metrics.get('gpu_utilization', 0)
            gpu_util_status = "🟢" if gpu_util > 50 else "🟡" if gpu_util > 20 else "🔴"
            table.add_row("GPU Utilization", f"{gpu_util:.1f}%", gpu_util_status)

        # Disk usage
        disk_percent = system_metrics.get('disk_usage', 0)
        disk_status = "🟢" if disk_percent < 80 else "🟡" if disk_percent < 90 else "🔴"
        table.add_row("Disk", f"{disk_percent:.1f}%", disk_status)

        return Panel(table, title="💻 System Status", border_style="blue")

    def render_footer(self, checkpoint_info: Dict[str, Any]) -> Panel:
        """Render dashboard footer."""
        footer_text = f"Latest Checkpoint: {checkpoint_info.get('latest_checkpoint', 'None')} | "
        footer_text += f"Total Checkpoints: {checkpoint_info.get('num_checkpoints', 0)} | "
        footer_text += f"Log Dir: {self.log_dir}"

        return Panel(Text(footer_text, style="dim"), box_style="dim")

    def run(self):
        """Run the training monitor."""
        console.print("[bold green]Starting PromptEvolver Training Monitor...[/bold green]")
        console.print(f"Monitoring logs in: {self.log_dir}")

        # Set training start time
        self.training_start_time = datetime.now()

        # Create dashboard layout
        layout = self.create_dashboard()

        with Live(layout, refresh_per_second=1, console=console) as live:
            while True:
                try:
                    # Get metrics
                    tb_metrics = self.get_tensorboard_metrics()
                    system_metrics = self.get_system_metrics()
                    checkpoint_info = self.get_checkpoint_info()

                    # Update layout
                    layout["header"].update(self.render_header())
                    layout["training_metrics"].update(self.render_training_metrics(tb_metrics))
                    layout["evaluation_metrics"].update(self.render_evaluation_metrics(tb_metrics))
                    layout["system"].update(self.render_system_metrics(system_metrics))
                    layout["footer"].update(self.render_footer(checkpoint_info))

                    # Sleep before next update
                    time.sleep(self.refresh_rate)

                except KeyboardInterrupt:
                    console.print("\n[bold yellow]Monitoring stopped by user.[/bold yellow]")
                    break
                except Exception as e:
                    console.print(f"[bold red]Error: {e}[/bold red]")
                    time.sleep(self.refresh_rate)


class MetricsAnalyzer:
    """Analyze and visualize training metrics."""

    def __init__(self, log_dir: str):
        """Initialize metrics analyzer."""
        self.log_dir = Path(log_dir)
        self.metrics_df = None

    def load_metrics(self) -> pd.DataFrame:
        """Load metrics from TensorBoard logs into DataFrame."""
        metrics_data = []

        # Find event files
        event_files = list(self.log_dir.glob("events.out.tfevents.*"))

        for event_file in event_files:
            try:
                ea = EventAccumulator(str(event_file))
                ea.Reload()

                # Get all scalar tags
                scalar_tags = ea.Tags().get('scalars', [])

                for tag in scalar_tags:
                    events = ea.Scalars(tag)
                    for event in events:
                        metrics_data.append({
                            'metric': tag,
                            'step': event.step,
                            'value': event.value,
                            'wall_time': event.wall_time
                        })

            except Exception as e:
                logger.warning(f"Failed to load metrics from {event_file}: {e}")

        self.metrics_df = pd.DataFrame(metrics_data)
        return self.metrics_df

    def plot_training_curves(self, output_path: str = None):
        """Plot training curves."""
        if self.metrics_df is None:
            self.load_metrics()

        if self.metrics_df.empty:
            logger.warning("No metrics to plot")
            return

        # Set up the plot style
        sns.set_style("whitegrid")

        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('PromptEvolver Training Metrics', fontsize=16)

        # Plot training loss
        loss_data = self.metrics_df[self.metrics_df['metric'] == 'train/loss']
        if not loss_data.empty:
            axes[0, 0].plot(loss_data['step'], loss_data['value'])
            axes[0, 0].set_title('Training Loss')
            axes[0, 0].set_xlabel('Step')
            axes[0, 0].set_ylabel('Loss')

        # Plot evaluation loss
        eval_loss_data = self.metrics_df[self.metrics_df['metric'] == 'eval/loss']
        if not eval_loss_data.empty:
            axes[0, 1].plot(eval_loss_data['step'], eval_loss_data['value'], color='orange')
            axes[0, 1].set_title('Evaluation Loss')
            axes[0, 1].set_xlabel('Step')
            axes[0, 1].set_ylabel('Loss')

        # Plot learning rate
        lr_data = self.metrics_df[self.metrics_df['metric'] == 'train/learning_rate']
        if not lr_data.empty:
            axes[1, 0].plot(lr_data['step'], lr_data['value'], color='green')
            axes[1, 0].set_title('Learning Rate')
            axes[1, 0].set_xlabel('Step')
            axes[1, 0].set_ylabel('Learning Rate')

        # Plot gradient norm
        grad_data = self.metrics_df[self.metrics_df['metric'] == 'train/grad_norm']
        if not grad_data.empty:
            axes[1, 1].plot(grad_data['step'], grad_data['value'], color='red')
            axes[1, 1].set_title('Gradient Norm')
            axes[1, 1].set_xlabel('Step')
            axes[1, 1].set_ylabel('Gradient Norm')

        plt.tight_layout()

        # Save or show the plot
        if output_path:
            plt.savefig(output_path, dpi=100, bbox_inches='tight')
            logger.info(f"Saved training curves to {output_path}")
        else:
            plt.show()

    def generate_report(self, output_path: str = None):
        """Generate a training report."""
        if self.metrics_df is None:
            self.load_metrics()

        report = {
            'training_summary': {},
            'final_metrics': {},
            'best_metrics': {},
            'convergence_analysis': {}
        }

        if not self.metrics_df.empty:
            # Get final metrics
            for metric in self.metrics_df['metric'].unique():
                metric_data = self.metrics_df[self.metrics_df['metric'] == metric]
                if not metric_data.empty:
                    final_value = metric_data.iloc[-1]['value']
                    report['final_metrics'][metric] = float(final_value)

                    # Get best value for loss metrics
                    if 'loss' in metric:
                        best_value = metric_data['value'].min()
                        best_step = metric_data[metric_data['value'] == best_value]['step'].iloc[0]
                        report['best_metrics'][metric] = {
                            'value': float(best_value),
                            'step': int(best_step)
                        }

            # Training summary
            total_steps = self.metrics_df['step'].max()
            training_time = self.metrics_df['wall_time'].max() - self.metrics_df['wall_time'].min()

            report['training_summary'] = {
                'total_steps': int(total_steps),
                'training_time_seconds': float(training_time),
                'training_time_hours': float(training_time / 3600),
                'metrics_logged': len(self.metrics_df['metric'].unique())
            }

            # Convergence analysis
            train_loss = self.metrics_df[self.metrics_df['metric'] == 'train/loss']
            if not train_loss.empty:
                # Check if loss is still decreasing
                recent_loss = train_loss.tail(10)['value'].mean()
                earlier_loss = train_loss.iloc[-20:-10]['value'].mean() if len(train_loss) > 20 else recent_loss

                report['convergence_analysis'] = {
                    'final_train_loss': float(train_loss.iloc[-1]['value']),
                    'loss_still_decreasing': bool(recent_loss < earlier_loss),
                    'recent_loss_change': float(recent_loss - earlier_loss)
                }

        # Save report
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Saved training report to {output_path}")

        return report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Monitor PromptEvolver training")
    parser.add_argument(
        "--log-dir",
        type=str,
        default="./logs",
        help="Directory containing training logs"
    )
    parser.add_argument(
        "--refresh-rate",
        type=int,
        default=5,
        help="Refresh rate in seconds"
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze metrics and generate report instead of live monitoring"
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Generate training curve plots"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output path for reports or plots"
    )

    args = parser.parse_args()

    if args.analyze:
        # Run analysis mode
        analyzer = MetricsAnalyzer(args.log_dir)

        if args.plot:
            output_path = args.output or "training_curves.png"
            analyzer.plot_training_curves(output_path)

        # Generate report
        report_path = args.output or "training_report.json"
        report = analyzer.generate_report(report_path)

        # Print summary
        console.print("[bold green]Training Analysis Complete![/bold green]")
        console.print(f"Total Steps: {report['training_summary'].get('total_steps', 'N/A')}")
        console.print(f"Training Time: {report['training_summary'].get('training_time_hours', 0):.2f} hours")

        if 'final_train_loss' in report['convergence_analysis']:
            console.print(f"Final Training Loss: {report['convergence_analysis']['final_train_loss']:.4f}")
    else:
        # Run live monitoring mode
        monitor = TrainingMonitor(args.log_dir, args.refresh_rate)
        monitor.run()


if __name__ == "__main__":
    main()
