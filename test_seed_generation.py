#!/usr/bin/env python3
"""
Test script for PromptWizard seed pair generation
================================================

Quick test of the generate_seed_pairs.py functionality
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scripts.generate_seed_pairs import SeedPairGenerator


async def test_basic_functionality():
    """Test basic seed pair generation functionality."""
    print("🧪 Testing PromptWizard Seed Pair Generation")
    print("=" * 50)

    try:
        # Initialize generator
        generator = SeedPairGenerator()
        print("✅ Generator initialized successfully")

        # Test domain classification
        test_prompts = [
            "Analyze the sales data",
            "Write a Python function",
            "Create marketing content",
            "Help with my project",
        ]

        print("\n🔍 Testing domain classification:")
        for prompt in test_prompts:
            domain = generator.classify_domain(prompt)
            print(f"  '{prompt}' → {domain}")

        # Test weak prompt generation
        print("\n📝 Testing weak prompt generation:")
        for domain in ["Analytics", "Coding", "Content"]:
            weak_prompts = generator.generate_weak_prompts(domain, 3)
            print(f"  {domain}: {weak_prompts}")

        # Test quality score calculation
        print("\n📊 Testing quality score calculation:")
        original = "Write a report"
        enhanced = """As a senior business analyst with expertise in data analysis, create a comprehensive quarterly performance report. Structure your analysis in 3 clear sections: 1) Key Performance Metrics (revenue, growth, efficiency ratios), 2) Trend Analysis (quarterly comparisons, seasonal patterns), 3) Strategic Recommendations (actionable insights for next quarter). Use professional business language with bullet points for clarity. Target audience: Executive leadership team. Length: 800-1200 words. Include specific data visualizations and avoid generic statements."""

        quality_scores = generator.calculate_quality_scores(original, enhanced)
        print(f"  Original: '{original}'")
        print(f"  Enhanced: '{enhanced[:100]}...'")
        print(f"  Quality scores: {quality_scores}")

        # Test improvement areas generation
        improvement_areas = generator.generate_improvement_areas(original, enhanced)
        print(f"  Improvement areas: {improvement_areas}")

        # Test seed pair creation
        print("\n🔧 Testing seed pair creation:")
        domain = "Analytics"
        pair = generator.create_seed_pair(original, enhanced, domain)
        print(f"  Created pair for {domain} domain")
        print(f"  Validation: {generator.validate_pair(pair)}")

        print("\n✅ All basic tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False


async def test_mini_generation():
    """Test actual pair generation with Ollama (if available)."""
    print("\n🚀 Testing mini generation (3 pairs)")
    print("=" * 50)

    try:
        generator = SeedPairGenerator()

        # Try to generate a few pairs for Analytics domain
        pairs = await generator.generate_pairs_for_domain("Analytics", count=3, batch_size=1)

        print(f"✅ Generated {len(pairs)} pairs")
        for i, pair in enumerate(pairs[:2], 1):  # Show first 2
            print(f"\n📄 Pair {i}:")
            print(f"  Original: {pair['originalPrompt']}")
            print(f"  Enhanced: {pair['enhancedPrompt'][:100]}...")
            print(f"  Quality Score: {pair['metadata']['qualityScore']['overall']}")

        return len(pairs) > 0

    except Exception as e:
        print(f"❌ Mini generation test failed: {str(e)}")
        print("💡 This might be expected if Ollama is not running")
        return False


async def main():
    """Run all tests."""
    print("🧪 PromptWizard Integration Test Suite")
    print("=" * 60)

    # Test basic functionality
    basic_test_passed = await test_basic_functionality()

    if basic_test_passed:
        # Test mini generation (may fail if Ollama not available)
        generation_test_passed = await test_mini_generation()

        if generation_test_passed:
            print("\n🎉 All tests passed! The integration is working correctly.")
        else:
            print("\n⚠️ Basic tests passed, but generation test failed (Ollama may not be available)")
    else:
        print("\n❌ Basic tests failed. Please check the implementation.")

    print("\n📖 Usage Examples:")
    print("  python scripts/generate_seed_pairs.py --domain Analytics --count 10")
    print("  python scripts/generate_seed_pairs.py --all-domains --pairs-per-domain 50")
    print("  python scripts/generate_seed_pairs.py --resume --domain Coding")


if __name__ == "__main__":
    asyncio.run(main())
