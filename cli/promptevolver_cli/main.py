#!/usr/bin/env python3
"""
PromptEvolver CLI Main Module
Simple Click-based CLI for prompt optimization using existing Convex backend
"""

import click
import json
import time
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel

from .client import ConvexClient, ConvexError
from .config import QUICK_MODE_CONFIG, ADVANCED_MODE_CONFIG, BATCH_DELAY

console = Console()

# Global client instance
client = ConvexClient()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """
    PromptEvolver CLI - Terminal-based prompt optimization using Microsoft PromptWizard

    This CLI connects to your existing Convex backend to provide terminal access
    to prompt optimization features.
    """
    pass


@cli.command()
def health():
    """Check Ollama health and PromptWizard availability"""
    console.print("\n[bold blue]Checking PromptWizard Health...[/bold blue]")

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Connecting to backend...", total=None)

            result = client.check_health()

            progress.update(task, description="Health check complete")

        if result.get("available"):
            console.print(f"\n✅ [green]Service Available[/green]")
            console.print(f"🤖 Model: {result.get('model', 'Unknown')}")
        else:
            console.print(f"\n❌ [red]Service Unavailable[/red]")
            if result.get("error"):
                console.print(f"Error: {result['error']}")

    except ConvexError as e:
        console.print(f"\n❌ [red]Health check failed: {str(e)}[/red]")


@cli.command()
@click.argument("prompt", type=str)
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["quick", "advanced"]),
    default="quick",
    help="Optimization mode (quick: 1 iteration, advanced: 3 iterations)",
)
@click.option(
    "--reasoning/--no-reasoning", default=True, help="Generate expert reasoning"
)
@click.option(
    "--expert-identity/--no-expert-identity",
    default=True,
    help="Generate expert identity",
)
@click.option("--rounds", "-r", type=int, default=3, help="Number of mutation rounds")
def optimize(
    prompt: str, mode: str, reasoning: bool, expert_identity: bool, rounds: int
):
    """
    Optimize a single prompt using PromptWizard

    PROMPT: The prompt text to optimize
    """
    console.print(f"\n[bold blue]Optimizing Prompt ({mode} mode)...[/bold blue]")
    console.print(Panel(prompt, title="Original Prompt", border_style="dim"))

    try:
        # First create a session - this would typically call a mutation
        # For now, we'll simulate this by calling the action directly with a fake session ID

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Creating optimization session...", total=None)

            # Create optimization configuration based on mode
            config = (
                QUICK_MODE_CONFIG.copy()
                if mode == "quick"
                else ADVANCED_MODE_CONFIG.copy()
            )
            config.update(
                {
                    "generate_reasoning": reasoning,
                    "generate_expert_identity": expert_identity,
                    "mutation_rounds": rounds,
                }
            )

            progress.update(task, description="Running optimization...")

            # Use the client's optimize_prompt method
            result = client.optimize_prompt(prompt, config)

            progress.update(task, description="Optimization complete!")

        if result.get("success"):
            optimization_result = result["result"]

            # Display results
            console.print(f"\n✅ [green]Optimization Complete![/green]")

            # Best prompt
            console.print(
                Panel(
                    optimization_result.get(
                        "best_prompt", "No optimized prompt returned"
                    ),
                    title="✨ Optimized Prompt",
                    border_style="green",
                )
            )

            # Quality metrics
            quality_score = optimization_result.get("quality_score", 0)
            console.print(
                f"\n📊 Quality Score: [bold cyan]{quality_score:.2f}[/bold cyan]"
            )

            # Expert insights
            if optimization_result.get("expert_profile"):
                console.print(
                    Panel(
                        optimization_result["expert_profile"],
                        title="🧠 Expert Identity",
                        border_style="blue",
                    )
                )

            # Improvements
            if optimization_result.get("improvements"):
                improvements_text = "\n".join(
                    [f"• {imp}" for imp in optimization_result["improvements"]]
                )
                console.print(
                    Panel(
                        improvements_text,
                        title="🚀 Key Improvements",
                        border_style="yellow",
                    )
                )

        else:
            console.print(
                f"\n❌ [red]Optimization failed: {result.get('error', 'Unknown error')}[/red]"
            )

    except ConvexError as e:
        console.print(f"\n❌ [red]Optimization failed: {str(e)}[/red]")


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file for results (default: results.json)",
)
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["quick", "advanced"]),
    default="quick",
    help="Optimization mode",
)
def batch(file_path: str, output: Optional[str], mode: str):
    """
    Batch optimize prompts from a file

    FILE_PATH: Path to file containing prompts (one per line)
    """
    output_file = output or "results.json"

    console.print(f"\n[bold blue]Batch Optimization ({mode} mode)[/bold blue]")
    console.print(f"📄 Input: {file_path}")
    console.print(f"📝 Output: {output_file}")

    try:
        # Read prompts from file
        with open(file_path, "r", encoding="utf-8") as f:
            prompts = [line.strip() for line in f if line.strip()]

        if not prompts:
            console.print("❌ [red]No prompts found in file[/red]")
            return

        console.print(f"\n📊 Found {len(prompts)} prompts to optimize")

        results = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:

            for i, prompt in enumerate(prompts, 1):
                task = progress.add_task(
                    f"Optimizing prompt {i}/{len(prompts)}...", total=None
                )

                try:
                    # Create config based on mode
                    config = (
                        QUICK_MODE_CONFIG.copy()
                        if mode == "quick"
                        else ADVANCED_MODE_CONFIG.copy()
                    )

                    result = client.optimize_prompt(prompt, config)

                    # Add small delay between requests to be nice to the API
                    time.sleep(BATCH_DELAY)

                    if result.get("success"):
                        results.append(
                            {
                                "original_prompt": prompt,
                                "optimized_prompt": result["result"].get("best_prompt"),
                                "quality_score": result["result"].get("quality_score"),
                                "expert_profile": result["result"].get(
                                    "expert_profile"
                                ),
                                "improvements": result["result"].get(
                                    "improvements", []
                                ),
                            }
                        )
                    else:
                        results.append(
                            {
                                "original_prompt": prompt,
                                "error": result.get("error", "Unknown error"),
                            }
                        )

                except Exception as e:
                    results.append({"original_prompt": prompt, "error": str(e)})

                progress.update(
                    task, description=f"Completed prompt {i}/{len(prompts)}"
                )

        # Save results
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        # Display summary
        successful = len([r for r in results if "error" not in r])
        failed = len(results) - successful

        table = Table(title="Batch Optimization Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="green")

        table.add_row("Total Prompts", str(len(prompts)))
        table.add_row("Successful", str(successful))
        table.add_row("Failed", str(failed))
        table.add_row("Output File", output_file)

        console.print(f"\n")
        console.print(table)

        if failed > 0:
            console.print(f"\n⚠️  [yellow]{failed} prompts failed to optimize[/yellow]")

        console.print(f"\n✅ [green]Results saved to {output_file}[/green]")

    except ConvexError as e:
        console.print(f"\n❌ [red]Batch processing failed: {str(e)}[/red]")
    except Exception as e:
        console.print(f"\n❌ [red]Batch processing failed: {str(e)}[/red]")


if __name__ == "__main__":
    cli()
