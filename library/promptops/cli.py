"""PromptOps CLI interface."""

import json
import sys
from pathlib import Path
from typing import Optional

import click
import yaml
from rich.console import Console
from rich.table import Table

from .evaluator import Evaluator
from .config import Config

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main():
    """PromptOps CLI - Lightweight prompt evaluation and CI/CD."""
    pass


@main.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    default=".promptops.yml",
    help="Path to config file",
)
@click.option(
    "--out",
    "-o",
    type=click.Path(),
    help="Output file for results (JSON)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Verbose output",
)
def ci(config: str, out: Optional[str], verbose: bool):
    """Run CI evaluation against configured thresholds."""
    try:
        # Load config
        config_path = Path(config)
        if not config_path.exists():
            console.print(f"[red]Config file not found: {config}[/red]")
            sys.exit(1)

        with open(config_path) as f:
            config_data = yaml.safe_load(f)

        cfg = Config(**config_data)

        # Run evaluation (mocked for now)
        evaluator = Evaluator(cfg)
        results = evaluator.run_ci_evaluation()

        # Display results
        if verbose:
            table = Table(title="Evaluation Results")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            table.add_column("Threshold", style="yellow")
            table.add_column("Status", style="bold")

            for metric, value in results["metrics"].items():
                threshold = cfg.threshold if metric == "win_rate" else "N/A"
                status = "✅ PASS" if value >= cfg.threshold else "❌ FAIL"
                table.add_row(metric, f"{value:.3f}", str(threshold), status)

            console.print(table)

        # Save results
        if out:
            with open(out, "w") as f:
                json.dump(results, f, indent=2)
            console.print(f"[green]Results saved to {out}[/green]")

        # Exit with appropriate code
        if results["pass"]:
            console.print("[green bold]✅ CI evaluation PASSED[/green bold]")
            sys.exit(0)
        else:
            console.print("[red bold]❌ CI evaluation FAILED[/red bold]")
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.command()
@click.argument("prompt", type=str)
@click.option(
    "--model",
    "-m",
    default="mock",
    help="Model to use for evaluation",
)
def eval(prompt: str, model: str):
    """Evaluate a single prompt."""
    try:
        cfg = Config(model=model)
        evaluator = Evaluator(cfg)

        # Mock evaluation
        result = evaluator.evaluate_prompt(prompt)

        console.print("[bold]Evaluation Result:[/bold]")
        console.print(f"Original: {prompt}")
        console.print(f"Score: {result['score']:.3f}")
        console.print(f"Improved: {result['improved']}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.command()
def init():
    """Initialize a new .promptops.yml config file."""
    config_path = Path(".promptops.yml")

    if config_path.exists():
        console.print("[yellow]Config file already exists[/yellow]")
        if not click.confirm("Overwrite?"):
            return

    default_config = {
        "version": "1.0",
        "threshold": 0.85,
        "model": "mock",
        "test_prompts": [
            "Write a function to calculate fibonacci",
            "Explain quantum computing",
        ],
        "evaluation": {
            "metrics": ["clarity", "specificity", "completeness"],
            "timeout": 30,
        },
    }

    with open(config_path, "w") as f:
        yaml.dump(default_config, f, default_flow_style=False)

    console.print(f"[green]Created {config_path}[/green]")


def deprecated_main():
    """Deprecated entry point for backward compatibility."""
    console.print(
        "[yellow]Warning: 'promptwizard' command is deprecated. "
        "Please use 'promptops' instead.[/yellow]"
    )
    main()


if __name__ == "__main__":
    main()
