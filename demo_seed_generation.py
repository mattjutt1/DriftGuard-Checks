#!/usr/bin/env python3
"""
Demo script showing PromptWizard integration functionality
=========================================================
"""

import json
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scripts.generate_seed_pairs import SeedPairGenerator

def demo_basic_functionality():
    """Demonstrate basic seed pair generation functionality."""
    print("🚀 PromptWizard Integration Demo")
    print("=" * 50)
    
    # Initialize generator
    generator = SeedPairGenerator()
    print("✅ Generator initialized successfully")
    
    # Demo 1: Domain Classification
    print("\n🎯 Domain Classification Demo:")
    test_cases = [
        ("Analyze quarterly sales performance", "Analytics"),
        ("Create a Python REST API", "Coding"), 
        ("Write engaging blog content", "Content"),
        ("Design a project management workflow", "Cross-Domain")
    ]
    
    for prompt, expected in test_cases:
        classified = generator.classify_domain(prompt)
        status = "✅" if classified == expected else "❌"
        print(f"  {status} '{prompt}' → {classified}")
    
    # Demo 2: Weak Prompt Generation
    print("\n📝 Weak Prompt Generation Demo:")
    for domain in ["Analytics", "Coding", "Content"]:
        weak_prompts = generator.generate_weak_prompts(domain, 3)
        print(f"  {domain}: {weak_prompts}")
    
    # Demo 3: Quality Score Calculation
    print("\n📊 Quality Score Demo:")
    original = "Create a report"
    enhanced = """As a senior business analyst with expertise in data visualization and executive reporting, create a comprehensive quarterly performance report for the leadership team. 

Structure your analysis in 4 clear sections:
1. Executive Summary (key findings and recommendations)
2. Performance Metrics (revenue, growth, market share with YoY comparisons)  
3. Trend Analysis (quarterly patterns, seasonal impacts, forecast implications)
4. Strategic Recommendations (actionable insights for next quarter with success metrics)

Requirements:
- Professional business language with clear, concise bullet points
- Include 3-5 data visualizations (charts, graphs, tables)
- Target audience: C-suite executives and board members
- Length: 1,200-1,500 words
- Format: Executive briefing document with appendices for detailed data
- Timeline: Focus on Q3 results with Q4 projections"""
    
    quality_scores = generator.calculate_quality_scores(original, enhanced)
    improvement_areas = generator.generate_improvement_areas(original, enhanced)
    
    print(f"  Original: '{original}'")
    print(f"  Enhanced length: {len(enhanced)} characters")
    print(f"  Quality scores: {json.dumps(quality_scores, indent=2)}")
    print(f"  Improvements: {improvement_areas}")
    
    # Demo 4: Complete Seed Pair Creation
    print("\n🔧 Complete Seed Pair Creation Demo:")
    domain = "Analytics"
    pair = generator.create_seed_pair(original, enhanced, domain)
    
    print(f"  Domain: {pair['domain']}")
    print(f"  Overall Quality: {pair['metadata']['qualityScore']['overall']}")
    print(f"  Expert Identity: {pair['metadata']['expertIdentity']}")
    print(f"  Validation: {'✅ PASS' if generator.validate_pair(pair) else '❌ FAIL'}")
    print(f"  Tags: {pair['tags']}")
    
    # Demo 5: Configuration Management
    print("\n⚙️ Configuration Demo:")
    config = generator.promptwizard_config
    print(f"  Iterations: {config['mutate_refine_iterations']}")
    print(f"  Temperature: {config['temperature']}")
    print(f"  Generate Reasoning: {config['generate_reasoning']}")
    print(f"  Generate Expert Identity: {config['generate_expert_identity']}")
    
    # Demo 6: Schema Compliance
    print("\n✅ Schema Validation Demo:")
    try:
        import jsonschema
        jsonschema.validate(pair, generator.schema)
        print("  ✅ Generated pair fully complies with engineered_prompt.schema.json")
    except Exception as e:
        print(f"  ❌ Schema validation failed: {e}")
    
    print("\n🎉 Demo completed successfully!")
    
    # Show usage examples
    print("\n📖 Usage Examples:")
    print("  # Generate 10 Analytics pairs")
    print("  python scripts/generate_seed_pairs.py --domain Analytics --count 10")
    print("  ")
    print("  # Generate pairs for all domains")
    print("  python scripts/generate_seed_pairs.py --all-domains --pairs-per-domain 25")
    print("  ")
    print("  # Resume interrupted generation")
    print("  python scripts/generate_seed_pairs.py --resume --domain Coding")
    print("  ")
    print("  # Use custom configuration")
    print("  python scripts/generate_seed_pairs.py --config-path configs/my_config.yaml")
    
    print("\n💡 Note: For actual prompt generation, ensure Ollama is running with qwen2.5:7b model")
    print("     ollama pull qwen2.5:7b")
    print("     ollama serve")

if __name__ == "__main__":
    demo_basic_functionality()