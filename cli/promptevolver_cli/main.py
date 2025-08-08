#!/usr / bin / env python3
"""
PromptEvolver CLI Main Module
Simple Click - based CLI for prompt optimization using existing Convex backend
"""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)
from rich.prompt import Prompt
from rich.rule import Rule
from rich.table import Table

from .client import ConvexClient, ConvexError
from .config import ADVANCED_MODE_CONFIG, BATCH_DELAY, DOMAIN_CONFIGS, QUICK_MODE_CONFIG

console = Console()

# Global client instance
client = ConvexClient()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """
    PromptEvolver CLI - Terminal - based prompt optimization using Microsoft PromptWizard

    This CLI connects to your existing Convex backend to provide terminal access
    to prompt optimization features.
    """


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
            console.print("\n✅ [green]Service Available[/green]")
            console.print(f"🤖 Model: {result.get('model', 'Unknown')}")
        else:
            console.print("\n❌ [red]Service Unavailable[/red]")
            if result.get("error"):
                console.print(f"Error: {result['error']}")

    except ConvexError as e:
        console.print(f"\n❌ [red]Health check failed: {str(e)}[/red]")


@cli.command()
@click.argument("prompt", type=str, required=False)
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True, path_type=Path),
    help="Read prompt from file instead of argument",
)
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["quick", "advanced"]),
    default="quick",
    help="Optimization mode (quick: 1 iteration, advanced: 3 iterations)",
)
@click.option(
    "--domain",
    "-d",
    type=click.Choice(["general", "technical", "creative", "business", "academic"]),
    default="general",
    help="Prompt domain for specialized optimization",
)
@click.option("--reasoning/--no - reasoning", default=True, help="Generate expert reasoning")
@click.option(
    "--expert - identity/--no - expert - identity",
    default=True,
    help="Generate expert identity",
)
@click.option("--rounds", "-r", type=int, default=3, help="Number of mutation rounds")
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Save results to file (JSON format)")
@click.option("--interactive", "-i", is_flag=True, help="Interactive mode with step - by - step guidance")
@click.option("--show - comparison", is_flag=True, help="Show side - by - side comparison of original vs optimized")
def optimize(
    prompt: Optional[str],
    file: Optional[Path],
    mode: str,
    domain: str,
    reasoning: bool,
    expert_identity: bool,
    rounds: int,
    output: Optional[Path],
    interactive: bool,
    show_comparison: bool,
):
    """
    Optimize a single prompt using PromptWizard

    PROMPT: The prompt text to optimize (or use --file to read from file)
    """

    # Handle input validation and prompt source
    if not prompt and not file:
        if interactive:
            prompt = Prompt.ask("\n[bold cyan]Enter your prompt to optimize[/bold cyan]")
        else:
            console.print("\n[red]Error: Please provide a prompt as argument or use --file option[/red]")
            raise click.Abort()

    if file:
        try:
            with open(file, "r", encoding="utf - 8") as f:
                prompt = f.read().strip()
            console.print(f"\n[dim]📄 Loaded prompt from: {file}[/dim]")
        except Exception as e:
            console.print(f"\n[red]Error reading file {file}: {e}[/red]")
            raise click.Abort()

    if not prompt or not prompt.strip():
        console.print("\n[red]Error: Empty prompt provided[/red]")
        raise click.Abort()

    # Interactive domain selection if requested
    if interactive and domain == "general":
        domain_choices = ["general", "technical", "creative", "business", "academic"]
        domain_descriptions = {
            "general": "General purpose prompts",
            "technical": "Technical documentation, code, APIs",
            "creative": "Creative writing, storytelling, marketing",
            "business": "Business communication, reports, analysis",
            "academic": "Research, academic writing, education",
        }

        console.print("\n[bold cyan]Select domain for specialized optimization:[/bold cyan]")
        for i, choice in enumerate(domain_choices, 1):
            console.print(f"  {i}. {choice.title()}: {domain_descriptions[choice]}")

        selection = Prompt.ask("Domain", choices=[str(i) for i in range(1, 6)], default="1")
        domain = domain_choices[int(selection) - 1]

    # Display optimization header
    console.print(f"\n[bold blue]🚀 PromptWizard Optimization ({mode} mode, {domain} domain)[/bold blue]")
    console.print(Panel(prompt, title="📝 Original Prompt", border_style="dim"))

    try:
        # Create optimization configuration based on mode and domain
        base_config = QUICK_MODE_CONFIG.copy() if mode == "quick" else ADVANCED_MODE_CONFIG.copy()

        # Apply domain - specific configuration
        domain_config = DOMAIN_CONFIGS.get(domain, {})
        config = {**base_config, **domain_config}

        config.update(
            {
                "generate_reasoning": reasoning,
                "generate_expert_identity": expert_identity,
                "mutation_rounds": rounds,
                "domain": domain,
            }
        )

        # Enhanced progress tracking with realistic time estimates
        estimated_time = 15 if mode == "quick" else 45  # seconds
        steps = [
            ("🔧 Initializing PromptWizard", 2),
            ("🧠 Analyzing prompt structure", 3),
            ("✨ Generating optimizations", estimated_time - 8),
            ("📊 Calculating quality metrics", 2),
            ("🎯 Finalizing results", 1),
        ]

        start_time = time.time()
        result = None

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TextColumn("[dim]{task.fields[eta]}[/dim]"),
            console=console,
        ) as progress:

            main_task = progress.add_task("🚀 Starting optimization...", total=estimated_time, eta="Calculating...")

            completed_time = 0
            for step_desc, step_time in steps:
                progress.update(main_task, description=step_desc)

                if "Generating optimizations" in step_desc:
                    # This is where the actual API call happens
                    step_start = time.time()
                    result = client.optimize_prompt(prompt, config)
                    actual_time = time.time() - step_start

                    # Adjust remaining time based on actual API response
                    if actual_time < step_time:
                        time.sleep(min(2, step_time - actual_time))  # Small delay for UX
                else:
                    # Simulate other steps
                    time.sleep(min(step_time, 3))  # Cap at 3 seconds for simulation

                completed_time += step_time
                progress.update(
                    main_task,
                    advance=step_time,
                    eta=f"~{max(0, estimated_time - completed_time)}s remaining",
                )

            progress.update(main_task, description="✅ Optimization complete!", eta="Done")
            time.sleep(0.5)  # Brief pause to show completion

        if result.get("success"):
            optimization_result = result["result"]
            processing_time = time.time() - start_time

            # Display success header with timing
            console.print(f"\n✅ [green]Optimization Complete![/green] [dim]({processing_time:.1f}s)[/dim]")
            console.print(Rule(style="green"))

            # Side - by - side comparison if requested
            if show_comparison:
                _display_comparison(console, prompt, optimization_result)
            else:
                # Standard optimized prompt display
                console.print(
                    Panel(
                        optimization_result.get("best_prompt", "No optimized prompt returned"),
                        title="✨ Optimized Prompt",
                        border_style="green",
                    )
                )

            # Enhanced quality metrics display
            quality_score = optimization_result.get("quality_score", 0)
            _display_quality_metrics(console, quality_score, processing_time, mode, domain)

            # Expert insights with better formatting
            if optimization_result.get("expert_profile"):
                console.print(
                    Panel(
                        optimization_result["expert_profile"],
                        title="🧠 Expert Identity",
                        border_style="blue",
                        padding=(1, 2),
                    )
                )

            # Key improvements with better formatting
            if optimization_result.get("improvements"):
                improvements = optimization_result["improvements"]
                if isinstance(improvements, list) and improvements:
                    improvements_text = "\n".join([f"• {imp}" for imp in improvements])
                    console.print(
                        Panel(
                            improvements_text,
                            title="🚀 Key Improvements",
                            border_style="yellow",
                            padding=(1, 2),
                        )
                    )

            # Save results if output file specified
            if output:
                _save_optimization_results(output, prompt, optimization_result, processing_time, mode, domain)
                console.print(f"\n💾 [dim]Results saved to: {output}[/dim]")

        else:
            error_msg = result.get("error", "Unknown error")
            console.print(f"\n❌ [red]Optimization failed: {error_msg}[/red]")

            # Provide helpful suggestions based on error type
            if "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                console.print("\n[yellow]💡 Suggestions:[/yellow]")
                console.print("  • Check your internet connection")
                console.print("  • Verify the Convex backend is running")
                console.print("  • Try running 'promptevolver health' to check system status")
            elif "invalid" in error_msg.lower() or "format" in error_msg.lower():
                console.print("\n[yellow]💡 Suggestions:[/yellow]")
                console.print("  • Check that your prompt is properly formatted")
                console.print("  • Try a simpler prompt to test the system")
                console.print("  • Use --interactive mode for guided input")

    except ConvexError as e:
        console.print(f"\n❌ [red]Optimization failed: {str(e)}[/red]")
        _display_error_suggestions(console, str(e))
    except Exception as e:
        console.print(f"\n❌ [red]Unexpected error: {str(e)}[/red]")
        console.print("\n[yellow]💡 Please try running 'promptevolver health' to check system status[/yellow]")


@cli.command()
@click.argument("file_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output file for results (default: results.json)",
)
@click.option(
    "--format",
    type=click.Choice(["json", "jsonl", "csv", "txt"]),
    default="json",
    help="Output format for results",
)
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["quick", "advanced"]),
    default="quick",
    help="Optimization mode",
)
@click.option(
    "--domain",
    "-d",
    type=click.Choice(["general", "technical", "creative", "business", "academic"]),
    default="general",
    help="Prompt domain for specialized optimization",
)
@click.option("--parallel", "-p", type=int, default=1, help="Number of parallel optimizations (1 - 5)")
@click.option("--continue - on - error", is_flag=True, help="Continue processing even if some prompts fail")
def batch(
    file_path: Path,
    output: Optional[Path],
    format: str,
    mode: str,
    domain: str,
    parallel: int,
    continue_on_error: bool,
):
    """
    Batch optimize prompts from a file

    FILE_PATH: Path to file containing prompts (one per line)
    """
    # Determine output file with appropriate extension
    if output:
        output_file = output
    else:
        output_file = Path(f"batch_results.{format}")

    # Validate parallel setting
    parallel = max(1, min(5, parallel))  # Clamp between 1 - 5

    console.print(f"\n[bold blue]📦 Batch Optimization ({mode} mode, {domain} domain)[/bold blue]")
    console.print(f"📄 Input: {file_path} → 📝 Output: {output_file} ({format.upper()})")
    if parallel > 1:
        console.print(f"⚡ Parallel processing: {parallel} concurrent optimizations")

    try:
        # Read prompts from file with better format detection
        prompts = _read_prompts_from_file(file_path)

        if not prompts:
            console.print("❌ [red]No prompts found in file[/red]")
            return

        console.print(f"\n📊 Found {len(prompts)} prompts to optimize")
        if not continue_on_error:
            console.print(
                "[yellow]⚠️  Processing will stop on first error (use --continue - on - error to change)[/yellow]"
            )

        results = []
        failed_prompts = []
        start_time = time.time()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TextColumn("[blue]{task.fields[stats]}[/blue]"),
            console=console,
        ) as progress:

            main_task = progress.add_task("🚀 Processing batch...", total=len(prompts), stats="Starting...")

            for i, prompt in enumerate(prompts, 1):
                try:
                    # Create enhanced config based on mode and domain
                    base_config = QUICK_MODE_CONFIG.copy() if mode == "quick" else ADVANCED_MODE_CONFIG.copy()
                    domain_config = DOMAIN_CONFIGS.get(domain, {})
                    config = {**base_config, **domain_config, "domain": domain}

                    result = client.optimize_prompt(prompt, config)

                    if result.get("success"):
                        optimization_result = result["result"]
                        results.append(_format_batch_result(prompt, optimization_result, i, True))
                    else:
                        error_result = _format_batch_result(
                            prompt, None, i, False, result.get("error", "Unknown error")
                        )
                        results.append(error_result)
                        failed_prompts.append((i, prompt, result.get("error", "Unknown error")))

                        if not continue_on_error:
                            console.print(f"\n❌ [red]Stopping on error at prompt {i}: {result.get('error')}[/red]")
                            break

                    # Update progress with stats
                    successful = len([r for r in results if "error" not in r])
                    failed = len(results) - successful
                    elapsed = time.time() - start_time
                    rate = i / elapsed if elapsed > 0 else 0

                    progress.update(
                        main_task,
                        advance=1,
                        description=f"Processing prompt {i}/{len(prompts)}",
                        stats=f"✅{successful} ❌{failed} ({rate:.1f}/min)",
                    )

                    # Small delay between requests
                    time.sleep(BATCH_DELAY)

                except Exception as e:
                    error_msg = str(e)
                    error_result = _format_batch_result(prompt, None, i, False, error_msg)
                    results.append(error_result)
                    failed_prompts.append((i, prompt, error_msg))

                    if not continue_on_error:
                        console.print(f"\n❌ [red]Unexpected error at prompt {i}: {error_msg}[/red]")
                        break

        # Save results in specified format
        _save_batch_results(output_file, results, format)

        # Display enhanced summary
        total_time = time.time() - start_time
        successful = len([r for r in results if "error" not in r])
        failed = len(results) - successful
        processing_rate = len(results) / total_time if total_time > 0 else 0

        console.print("\n")
        console.print(Rule("[bold]Batch Processing Complete[/bold]"))

        # Summary table
        table = Table(title="📊 Batch Optimization Summary", show_header=True)
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        table.add_column("Details", style="dim")

        table.add_row("Total Prompts", str(len(prompts)), f"From {file_path}")
        table.add_row("Processed", str(len(results)), f"({len(results) / len(prompts) * 100:.1f}%)")
        table.add_row(
            "✅ Successful",
            str(successful),
            f"({successful / len(results) * 100:.1f}% of processed)" if results else "0%",
        )
        table.add_row(
            "❌ Failed",
            str(failed),
            f"({failed / len(results) * 100:.1f}% of processed)" if results else "0%",
        )
        table.add_row("⏱️ Total Time", f"{total_time:.1f}s", f"{processing_rate:.1f} prompts / min")
        table.add_row("📁 Output", str(output_file), f"{format.upper()} format")

        console.print(table)

        # Show failed prompts if any
        if failed_prompts:
            console.print(f"\n⚠️  [yellow]Failed Prompts ({len(failed_prompts)}):[/yellow]")
            for idx, prompt_text, error in failed_prompts[:5]:  # Show first 5 failures
                short_prompt = prompt_text[:50] + "..." if len(prompt_text) > 50 else prompt_text
                console.print(f"  {idx}: {short_prompt} → [red]{error}[/red]")
            if len(failed_prompts) > 5:
                console.print(f"  ... and {len(failed_prompts) - 5} more")

        console.print(f"\n✅ [green]Results saved to {output_file}[/green]")

    except ConvexError as e:
        console.print(f"\n❌ [red]Batch processing failed: {str(e)}[/red]")
        _display_error_suggestions(console, str(e))
    except Exception as e:
        console.print(f"\n❌ [red]Batch processing failed: {str(e)}[/red]")
        console.print("\n[yellow]💡 Please check your input file format and try again[/yellow]")


def _display_comparison(console: Console, original: str, result: Dict[str, Any]):
    """Display side - by - side comparison of original vs optimized prompt"""
    layout = Layout()
    layout.split_row(
        Layout(Panel(original, title="📝 Original", border_style="dim"), name="original"),
        Layout(
            Panel(result.get("best_prompt", "No result"), title="✨ Optimized", border_style="green"),
            name="optimized",
        ),
    )
    console.print(layout)


def _display_quality_metrics(console: Console, quality_score: float, processing_time: float, mode: str, domain: str):
    """Display enhanced quality metrics"""
    # Create metrics table
    metrics_table = Table(title="📊 Quality Metrics", show_header=False, box=None)
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Value", style="bold")
    metrics_table.add_column("Assessment", style="dim")

    # Quality score with assessment
    if quality_score >= 80:
        assessment = "Excellent"
        score_style = "green"
    elif quality_score >= 60:
        assessment = "Good"
        score_style = "yellow"
    else:
        assessment = "Needs Improvement"
        score_style = "red"

    metrics_table.add_row("Quality Score", f"[{score_style}]{quality_score:.1f}/100[/{score_style}]", assessment)
    metrics_table.add_row("Processing Time", f"{processing_time:.1f}s", "Fast" if processing_time < 10 else "Normal")
    metrics_table.add_row("Mode", mode.title(), "Single iteration" if mode == "quick" else "Multiple iterations")
    metrics_table.add_row("Domain", domain.title(), f"Specialized for {domain}")

    console.print(metrics_table)


def _display_error_suggestions(console: Console, error_msg: str):
    """Display helpful error suggestions based on error type"""
    console.print("\n[yellow]💡 Troubleshooting suggestions:[/yellow]")

    if "connection" in error_msg.lower() or "timeout" in error_msg.lower():
        console.print("  • Check your internet connection")
        console.print("  • Verify the Convex backend is accessible")
        console.print("  • Try running 'promptevolver health' first")
    elif "authentication" in error_msg.lower() or "unauthorized" in error_msg.lower():
        console.print("  • Check your API credentials")
        console.print("  • Verify your Convex deployment URL")
    elif "invalid" in error_msg.lower() or "format" in error_msg.lower():
        console.print("  • Check your prompt format")
        console.print("  • Try a simpler test prompt")
        console.print("  • Use --interactive mode for guided input")
    else:
        console.print("  • Run 'promptevolver health' to check system status")
        console.print("  • Try again with a simpler prompt")
        console.print("  • Check the Convex backend logs for more details")


def _save_optimization_results(
    output_path: Path,
    original_prompt: str,
    result: Dict[str, Any],
    processing_time: float,
    mode: str,
    domain: str,
):
    """Save single optimization results to file"""
    data = {
        "timestamp": time.time(),
        "original_prompt": original_prompt,
        "optimized_prompt": result.get("best_prompt"),
        "quality_score": result.get("quality_score"),
        "expert_profile": result.get("expert_profile"),
        "improvements": result.get("improvements", []),
        "processing_time": processing_time,
        "mode": mode,
        "domain": domain,
        "metadata": {"version": "0.1.0", "optimization_engine": "PromptWizard"},
    }

    with open(output_path, "w", encoding="utf - 8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _read_prompts_from_file(file_path: Path) -> List[str]:
    """Read prompts from file with support for different formats"""
    prompts = []

    with open(file_path, "r", encoding="utf - 8") as f:
        content = f.read()

    # Try to detect format
    if file_path.suffix.lower() == ".jsonl":
        # JSONL format - each line is a JSON object
        for line in content.strip().split("\n"):
            if line.strip():
                try:
                    data = json.loads(line)
                    # Look for common prompt field names
                    prompt = data.get("prompt") or data.get("text") or data.get("content") or str(data)
                    prompts.append(prompt)
                except json.JSONDecodeError:
                    prompts.append(line.strip())
    elif file_path.suffix.lower() == ".json":
        # JSON format - could be array or object
        try:
            data = json.loads(content)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, str):
                        prompts.append(item)
                    elif isinstance(item, dict):
                        prompt = item.get("prompt") or item.get("text") or item.get("content") or str(item)
                        prompts.append(prompt)
            elif isinstance(data, dict):
                prompt = data.get("prompt") or data.get("text") or data.get("content") or str(data)
                prompts.append(prompt)
        except json.JSONDecodeError:
            # Fall back to line - by - line
            prompts = [line.strip() for line in content.split("\n") if line.strip()]
    else:
        # Plain text format - one prompt per line
        prompts = [line.strip() for line in content.split("\n") if line.strip()]

    return prompts


def _format_batch_result(
    prompt: str,
    result: Optional[Dict[str, Any]],
    index: int,
    success: bool,
    error: Optional[str] = None,
) -> Dict[str, Any]:
    """Format batch processing result"""
    base_result = {
        "index": index,
        "original_prompt": prompt,
        "timestamp": time.time(),
    }

    if success and result:
        base_result.update(
            {
                "optimized_prompt": result.get("best_prompt"),
                "quality_score": result.get("quality_score"),
                "expert_profile": result.get("expert_profile"),
                "improvements": result.get("improvements", []),
                "success": True,
            }
        )
    else:
        base_result.update({"error": error, "success": False})

    return base_result


def _save_batch_results(output_file: Path, results: List[Dict[str, Any]], format: str):
    """Save batch results in specified format"""
    if format == "json":
        with open(output_file, "w", encoding="utf - 8") as f:
            json.dump(
                {
                    "metadata": {
                        "total_results": len(results),
                        "successful": len([r for r in results if r.get("success")]),
                        "failed": len([r for r in results if not r.get("success")]),
                        "timestamp": time.time(),
                        "version": "0.1.0",
                    },
                    "results": results,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )

    elif format == "jsonl":
        with open(output_file, "w", encoding="utf - 8") as f:
            for result in results:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")

    elif format == "csv":
        import csv

        with open(output_file, "w", newline="", encoding="utf - 8") as f:
            if results:
                fieldnames = [
                    "index",
                    "original_prompt",
                    "optimized_prompt",
                    "quality_score",
                    "success",
                    "error",
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for result in results:
                    row = {field: result.get(field, "") for field in fieldnames}
                    writer.writerow(row)

    elif format == "txt":
        with open(output_file, "w", encoding="utf - 8") as f:
            f.write("PromptEvolver Batch Results\n")
            f.write("=" * 50 + "\n\n")
            for i, result in enumerate(results, 1):
                f.write(f"Result {i}:\n")
                f.write(f"Original: {result['original_prompt']}\n")
                if result.get("success"):
                    f.write(f"Optimized: {result.get('optimized_prompt', 'N / A')}\n")
                    f.write(f"Quality Score: {result.get('quality_score', 'N / A')}\n")
                else:
                    f.write(f"Error: {result.get('error', 'Unknown error')}\n")
                f.write("\n" + "-" * 40 + "\n\n")


if __name__ == "__main__":
    cli()
