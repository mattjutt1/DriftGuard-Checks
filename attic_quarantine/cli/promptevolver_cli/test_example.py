#!/usr/bin/env python3
"""
Test script to demonstrate the CLI working with mock responses
"""

import time

from rich.console import Console
from rich.panel import Panel

console = Console()


def test_health():
    """Test health command with mock response"""
    console.print("\n[bold blue]Checking PromptWizard Health...[/bold blue]")

    # Simulate API call delay
    time.sleep(1)

    # Mock successful response
    console.print(f"\n✅ [green]Service Available[/green]")
    console.print(f"🤖 Model: Microsoft PromptWizard + Qwen3:4b")
    console.print(f"🔗 Backend: https://resilient-guanaco-29.convex.cloud")
    console.print(f"📊 Status: Ready for optimization")


def test_optimize():
    """Test optimize command with mock response"""
    prompt = "Write a Python function to calculate fibonacci numbers"

    console.print(f"\n[bold blue]Optimizing Prompt (quick mode)...[/bold blue]")
    console.print(Panel(prompt, title="Original Prompt", border_style="dim"))

    # Simulate optimization
    time.sleep(2)

    # Mock optimization result
    optimized = """You are a Python programming expert. Write a well-documented, efficient Python function to calculate Fibonacci numbers with the following requirements:

1. Function name: fibonacci()
2. Parameter: n (integer, the position in the sequence)
3. Return: The nth Fibonacci number
4. Include error handling for negative inputs
5. Add docstring with examples
6. Use an iterative approach for efficiency

Please provide the complete function with clear comments explaining the logic."""

    console.print(f"\n✅ [green]Optimization Complete![/green]")

    # Best prompt
    console.print(Panel(optimized, title="✨ Optimized Prompt", border_style="green"))

    # Quality metrics
    console.print(f"\n📊 Quality Score: [bold cyan]8.7[/bold cyan]")

    # Expert insights
    console.print(
        Panel(
            "Programming Task Specialist with expertise in Python development, code documentation, and algorithmic efficiency",
            title="🧠 Expert Identity",
            border_style="blue",
        )
    )

    # Improvements
    improvements = [
        "Added specific expert identity as Python programming expert",
        "Included detailed requirements for better clarity",
        "Specified error handling and documentation requirements",
        "Added performance optimization guidance (iterative approach)",
        "Enhanced structure with numbered requirements for better comprehension",
    ]
    improvements_text = "\n".join([f"• {imp}" for imp in improvements])
    console.print(Panel(improvements_text, title="🚀 Key Improvements", border_style="yellow"))


if __name__ == "__main__":
    console.print("\n🎯 [bold]PromptEvolver CLI Test Demo[/bold]")
    console.print("=" * 50)

    test_health()
    test_optimize()

    console.print(f"\n🎉 [green]Demo completed successfully![/green]")
    console.print("\nTo use the real CLI:")
    console.print("  [cyan]promptevolver health[/cyan]")
    console.print("  [cyan]promptevolver optimize 'your prompt here'[/cyan]")
    console.print("  [cyan]promptevolver batch prompts.txt[/cyan]")
