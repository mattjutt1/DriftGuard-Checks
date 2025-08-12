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
from .budget import BudgetManager
from .cache import LLMResponseCache

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


# Budget management commands
@main.group()
def budget():
    """Budget management commands."""
    pass


@budget.command("set")
@click.option("--org", default="default", help="Organization slug")
@click.option("--project", default="default", help="Project slug")
@click.option("--limit", type=float, required=True, help="Monthly budget limit in USD")
@click.option("--alert-threshold", type=float, default=0.8, help="Alert threshold (0.0-1.0)")
def budget_set(org: str, project: str, limit: float, alert_threshold: float):
    """Set budget limit for an org/project."""
    try:
        budget_manager = BudgetManager()
        budget_manager.set_budget(org, project, limit, alert_threshold)
        console.print(f"[green]✅ Budget set: ${limit:.2f}/month for {org}/{project}[/green]")
        console.print(f"[yellow]⚠️  Alert threshold: {alert_threshold*100:.1f}%[/yellow]")
    except Exception as e:
        console.print(f"[red]Error setting budget: {e}[/red]")
        sys.exit(1)


@budget.command("status")
@click.option("--org", default="default", help="Organization slug")
@click.option("--project", default="default", help="Project slug")
def budget_status(org: str, project: str):
    """Check budget status for an org/project."""
    try:
        budget_manager = BudgetManager()
        status = budget_manager.get_budget_status(org, project)

        if not status["has_budget"]:
            console.print(f"[yellow]No budget set for {org}/{project}[/yellow]")
            console.print("Use 'promptops budget set' to create a budget")
            return

        # Create status table
        table = Table(title=f"Budget Status: {org}/{project}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="bold")

        table.add_row("Monthly Limit", f"${status['monthly_limit_usd']:.2f}")
        table.add_row("Current Spend", f"${status['current_spend_usd']:.2f}")
        table.add_row("Remaining", f"${status['remaining_usd']:.2f}")
        table.add_row("Usage", f"{status['percent_used']*100:.1f}%")

        # Status indicators
        if status["over_budget"]:
            table.add_row("Status", "🚨 OVER BUDGET", style="red bold")
        elif status["alert_triggered"]:
            table.add_row("Status", "⚠️  ALERT TRIGGERED", style="yellow bold")
        else:
            table.add_row("Status", "✅ WITHIN BUDGET", style="green bold")

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error checking budget: {e}[/red]")
        sys.exit(1)


@budget.command("report")
@click.option("--org", default="default", help="Organization slug")
@click.option("--project", default="default", help="Project slug")
@click.option("--days", type=int, default=30, help="Days to look back")
def budget_report(org: str, project: str, days: int):
    """Generate spending report."""
    try:
        budget_manager = BudgetManager()
        history = budget_manager.get_spend_history(org, project, days)

        if not history:
            console.print(f"[yellow]No spending history found for {org}/{project}[/yellow]")
            return

        # Summary stats
        total_cost = sum(record["cost_usd"] for record in history)
        total_tokens = sum(record["input_tokens"] + record["output_tokens"] for record in history)

        console.print(f"[bold]Spending Report: {org}/{project} (Last {days} days)[/bold]")
        console.print(f"Total Spend: ${total_cost:.4f}")
        console.print(f"Total Tokens: {total_tokens:,}")
        console.print(f"Average Cost per 1K Tokens: ${(total_cost / total_tokens * 1000):.4f}")
        console.print()

        # Recent transactions table
        table = Table(title="Recent Transactions")
        table.add_column("Date", style="cyan")
        table.add_column("Provider", style="blue")
        table.add_column("Model", style="green")
        table.add_column("Tokens", justify="right")
        table.add_column("Cost", justify="right", style="bold")

        for record in history[:10]:  # Show last 10 transactions
            date_str = record["timestamp"][:10]  # YYYY-MM-DD
            tokens = record["input_tokens"] + record["output_tokens"]
            table.add_row(
                date_str,
                record["provider"],
                record["model"],
                f"{tokens:,}",
                f"${record['cost_usd']:.4f}"
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error generating report: {e}[/red]")
        sys.exit(1)


@budget.command("list")
def budget_list():
    """List all budget configurations."""
    try:
        budget_manager = BudgetManager()
        budgets = budget_manager.list_budgets()

        if not budgets:
            console.print("[yellow]No budgets configured[/yellow]")
            console.print("Use 'promptops budget set' to create budgets")
            return

        table = Table(title="Budget Configurations")
        table.add_column("Org/Project", style="cyan")
        table.add_column("Limit", justify="right")
        table.add_column("Spent", justify="right")
        table.add_column("Remaining", justify="right")
        table.add_column("Usage", justify="right")
        table.add_column("Status", justify="center")

        for budget in budgets:
            org_project = f"{budget['org_slug']}/{budget['project_slug']}"
            limit_str = f"${budget['monthly_limit_usd']:.2f}"
            spent_str = f"${budget['current_spend_usd']:.2f}"
            remaining_str = f"${budget['remaining_usd']:.2f}"
            usage_str = f"{budget['percent_used']*100:.1f}%"

            # Status with color
            if budget['current_spend_usd'] > budget['monthly_limit_usd']:
                status = "🚨 OVER"
                status_style = "red bold"
            elif budget['percent_used'] >= budget.get('alert_threshold', 0.8):
                status = "⚠️  ALERT"
                status_style = "yellow bold"
            else:
                status = "✅ OK"
                status_style = "green bold"

            table.add_row(
                org_project, limit_str, spent_str, remaining_str, usage_str, status,
                style=status_style if status != "✅ OK" else None
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error listing budgets: {e}[/red]")
        sys.exit(1)


# Cache management commands
@main.group()
def cache():
    """Cache management commands."""
    pass


@cache.command("stats")
def cache_stats():
    """Show cache statistics."""
    try:
        cache = LLMResponseCache()
        stats = cache.get_stats()

        table = Table(title="Cache Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="bold")

        table.add_row("Total Entries", f"{stats['total_entries']:,}")
        table.add_row("Active Entries", f"{stats['active_entries']:,}")
        table.add_row("Expired Entries", f"{stats['expired_entries']:,}")
        table.add_row("Total Hits", f"{stats['total_hits']:,}")
        table.add_row("Hit Rate", f"{stats['hit_rate']*100:.1f}%")
        table.add_row("Storage Size", f"{stats['storage_mb']:.1f} MB")

        console.print(table)

        # Provider breakdown
        if stats["provider_stats"]:
            console.print()
            provider_table = Table(title="By Provider/Model")
            provider_table.add_column("Provider", style="blue")
            provider_table.add_column("Model", style="green")
            provider_table.add_column("Entries", justify="right")
            provider_table.add_column("Hits", justify="right")

            for provider_stat in stats["provider_stats"]:
                provider_table.add_row(
                    provider_stat["provider"],
                    provider_stat["model"],
                    f"{provider_stat['entries']:,}",
                    f"{provider_stat['hits']:,}"
                )

            console.print(provider_table)

    except Exception as e:
        console.print(f"[red]Error getting cache stats: {e}[/red]")
        sys.exit(1)


@cache.command("clear")
@click.option("--provider", help="Clear specific provider")
@click.option("--model", help="Clear specific model")
@click.option("--expired", is_flag=True, help="Clear only expired entries")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
def cache_clear(provider: Optional[str], model: Optional[str], expired: bool, confirm: bool):
    """Clear cache entries."""
    try:
        cache = LLMResponseCache()

        if expired:
            if not confirm and not click.confirm("Clear expired entries?"):
                return
            removed = cache.clear_expired()
            console.print(f"[green]✅ Cleared {removed} expired entries[/green]")

        elif provider:
            if not confirm and not click.confirm(f"Clear all entries for {provider}?"):
                return
            removed = cache.clear_provider(provider, model)
            scope = f"{provider}/{model}" if model else provider
            console.print(f"[green]✅ Cleared {removed} entries for {scope}[/green]")

        else:
            if not confirm and not click.confirm("Clear ALL cache entries?"):
                return
            removed = cache.clear_all()
            console.print(f"[green]✅ Cleared {removed} entries[/green]")

    except Exception as e:
        console.print(f"[red]Error clearing cache: {e}[/red]")
        sys.exit(1)


@cache.command("cleanup")
@click.option("--max-size", type=int, default=1000, help="Maximum cache entries")
def cache_cleanup(max_size: int):
    """Clean up cache by removing old entries."""
    try:
        cache = LLMResponseCache()

        # Clear expired first
        expired_removed = cache.clear_expired()
        console.print(f"Removed {expired_removed} expired entries")

        # Clean by size
        size_removed = cache.cleanup_by_size(max_size)
        console.print(f"Removed {size_removed} old entries to stay under {max_size} limit")

        total_removed = expired_removed + size_removed
        if total_removed > 0:
            console.print(f"[green]✅ Cache cleanup complete: {total_removed} entries removed[/green]")
        else:
            console.print("[green]✅ Cache is already clean[/green]")

    except Exception as e:
        console.print(f"[red]Error cleaning cache: {e}[/red]")
        sys.exit(1)


def deprecated_main():
    """Deprecated entry point for backward compatibility."""
    console.print(
        "[yellow]Warning: 'promptwizard' command is deprecated. "
        "Please use 'promptops' instead.[/yellow]"
    )
    main()


if __name__ == "__main__":
    main()
