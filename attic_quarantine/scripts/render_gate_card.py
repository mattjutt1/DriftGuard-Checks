#!/usr/bin/env python3
"""
Prompt Gate Card Renderer

Generates 1200x630 PNG cards from results.json artifacts for documentation.
Used to create real pass/fail images from actual workflow runs.
"""

import json
import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.patches import FancyBboxPatch
    import numpy as np
except ImportError as e:
    print(f"Missing dependencies: {e}")
    print("Install with: pip install Pillow matplotlib")
    sys.exit(1)


def load_results(results_path):
    """Load results.json from workflow artifact."""
    try:
        with open(results_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {results_path} not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        sys.exit(1)


def create_pass_card(results, output_path):
    """Create a PASS status card."""
    fig, ax = plt.subplots(figsize=(12, 6.3), facecolor='white')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Green gradient background
    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    gradient = np.vstack((gradient, gradient))
    ax.imshow(gradient, extent=[0, 100, 0, 100], aspect='auto', cmap='Greens', alpha=0.1)

    # Main container
    container = FancyBboxPatch((5, 15), 90, 70,
                              boxstyle="round,pad=2",
                              facecolor='#f8fff8',
                              edgecolor='#22c55e',
                              linewidth=3)
    ax.add_patch(container)

    # Header
    ax.text(50, 75, "🚀 Prompt Gate", fontsize=24, weight='bold',
            ha='center', va='center', color='#166534')

    # Status
    ax.text(50, 60, "✅ PASSED", fontsize=32, weight='bold',
            ha='center', va='center', color='#22c55e')

    # Metrics
    win_rate = results["metrics"]["win_rate"]
    threshold = results["threshold"]

    ax.text(50, 45, f"Win Rate: {win_rate:.1%}", fontsize=18, weight='bold',
            ha='center', va='center', color='#166534')

    ax.text(50, 35, f"Threshold: {threshold:.1%}", fontsize=16,
            ha='center', va='center', color='#16a34a')

    # Footer
    ax.text(50, 22, "Prompt quality meets requirements", fontsize=14,
            ha='center', va='center', color='#166534', style='italic')

    plt.tight_layout()
    plt.savefig(output_path, dpi=100, bbox_inches='tight', facecolor='white')
    plt.close()


def create_fail_card(results, output_path):
    """Create a FAIL status card."""
    fig, ax = plt.subplots(figsize=(12, 6.3), facecolor='white')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Red gradient background
    gradient = np.linspace(0, 1, 256).reshape(1, -1)
    gradient = np.vstack((gradient, gradient))
    ax.imshow(gradient, extent=[0, 100, 0, 100], aspect='auto', cmap='Reds', alpha=0.1)

    # Main container
    container = FancyBboxPatch((5, 15), 90, 70,
                              boxstyle="round,pad=2",
                              facecolor='#fff8f8',
                              edgecolor='#ef4444',
                              linewidth=3)
    ax.add_patch(container)

    # Header
    ax.text(50, 75, "🚧 Prompt Gate", fontsize=24, weight='bold',
            ha='center', va='center', color='#991b1b')

    # Status
    ax.text(50, 60, "❌ FAILED", fontsize=32, weight='bold',
            ha='center', va='center', color='#ef4444')

    # Metrics
    win_rate = results["metrics"]["win_rate"]
    threshold = results["threshold"]

    ax.text(50, 45, f"Win Rate: {win_rate:.1%}", fontsize=18, weight='bold',
            ha='center', va='center', color='#991b1b')

    ax.text(50, 35, f"Threshold: {threshold:.1%}", fontsize=16,
            ha='center', va='center', color='#dc2626')

    # Footer
    ax.text(50, 22, "Prompt quality below requirements", fontsize=14,
            ha='center', va='center', color='#991b1b', style='italic')

    plt.tight_layout()
    plt.savefig(output_path, dpi=100, bbox_inches='tight', facecolor='white')
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Generate Prompt Gate status cards')
    parser.add_argument('results_json', help='Path to results.json from workflow artifact')
    parser.add_argument('-o', '--output-dir', default='./cards',
                       help='Output directory for generated cards')
    parser.add_argument('--pass-card', default='prompt-gate-passed.png',
                       help='Filename for PASS card')
    parser.add_argument('--fail-card', default='prompt-gate-failed.png',
                       help='Filename for FAIL card')

    args = parser.parse_args()

    # Load results
    results = load_results(args.results_json)

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    # Determine actual status and generate appropriate card
    passed = results["metrics"]["win_rate"] >= results["threshold"]

    if passed:
        output_path = output_dir / args.pass_card
        create_pass_card(results, output_path)
        print(f"✅ Generated PASS card: {output_path}")
    else:
        output_path = output_dir / args.fail_card
        create_fail_card(results, output_path)
        print(f"❌ Generated FAIL card: {output_path}")

    # Also generate both cards for documentation purposes
    pass_path = output_dir / "prompt-gate-passed-example.png"
    fail_path = output_dir / "prompt-gate-failed-example.png"

    # Create example PASS result
    example_pass = {
        "metrics": {"win_rate": 0.85},
        "threshold": 0.80
    }
    create_pass_card(example_pass, pass_path)
    print(f"📄 Generated PASS example: {pass_path}")

    # Create example FAIL result
    example_fail = {
        "metrics": {"win_rate": 0.65},
        "threshold": 0.80
    }
    create_fail_card(example_fail, fail_path)
    print(f"📄 Generated FAIL example: {fail_path}")


if __name__ == "__main__":
    main()
