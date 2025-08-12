#!/usr/bin/env python3
"""
Example usage of the PromptEvolver 3.0 Dataset Normalization Script
===================================================================

This script demonstrates various ways to use the normalize_datasets.py script
for different data formats and use cases.
"""

import json
import pandas as pd
from pathlib import Path
import tempfile
import os
import subprocess
import sys

def create_sample_datasets():
    """Create sample datasets in different formats for demonstration."""
    print("📂 Creating sample datasets...")
    
    temp_dir = Path(tempfile.mkdtemp())
    print(f"📁 Sample datasets will be created in: {temp_dir}")
    
    # Sample data for different domains
    sample_data = [
        {
            "original": "Make a report about sales",
            "enhanced": "As a senior business analyst with expertise in sales analytics, create a comprehensive quarterly sales performance report. Structure your analysis in 4 sections: 1) Executive Summary (key findings, growth metrics), 2) Sales Performance Analysis (revenue by region, product categories, YoY comparisons), 3) Customer Insights (acquisition trends, retention rates, segment analysis), 4) Strategic Recommendations (actionable next steps, resource allocation suggestions). Include specific KPIs, visualizations, and data-driven insights. Target audience: C-suite executives and sales leadership. Format: Professional presentation with charts and bullet points."
        },
        {
            "original": "Fix the bug in my code",
            "enhanced": "As a senior software engineer with expertise in debugging and code quality, systematically identify and resolve the software bug. Follow this debugging methodology: 1) Issue Reproduction (steps to reproduce, environment details, error logs), 2) Root Cause Analysis (code review, dependency check, data flow analysis), 3) Impact Assessment (affected functionality, user impact, performance implications), 4) Solution Implementation (fix strategy, code changes, testing approach), 5) Quality Assurance (unit tests, integration tests, regression testing), 6) Documentation (bug report, solution notes, prevention measures). Include specific error messages, code snippets, and testing procedures."
        },
        {
            "original": "Write social media posts",
            "enhanced": "As a social media marketing specialist with expertise in engagement optimization, create a comprehensive social media content strategy for our brand. Develop content for multiple platforms: 1) LinkedIn Posts (thought leadership, industry insights, professional tone), 2) Twitter/X Content (trending topics, quick tips, conversational style), 3) Instagram Posts (visual storytelling, behind-the-scenes, brand personality), 4) Facebook Updates (community building, longer-form content, engagement-driven). Include hashtag strategy, posting schedule, engagement tactics, and performance metrics. Target audience: our key demographics across platforms. Maintain consistent brand voice while platform-specific optimization."
        },
        {
            "original": "Plan the project",
            "enhanced": "As a certified project manager with expertise in cross-functional team leadership, develop a comprehensive project plan integrating technical, marketing, and operational requirements. Structure your plan: 1) Project Charter (objectives, scope, stakeholders, success criteria), 2) Work Breakdown Structure (deliverables, tasks, dependencies), 3) Resource Planning (team roles, skills matrix, budget allocation), 4) Timeline & Milestones (critical path, risk buffers, delivery dates), 5) Communication Plan (stakeholder updates, meeting cadence, reporting structure), 6) Risk Management (risk assessment, mitigation strategies, contingency plans). Include Gantt charts, responsibility matrices, and performance indicators. Accommodate agile methodology with iterative reviews."
        }
    ]
    
    # Create CSV format
    csv_data = pd.DataFrame([
        {"original_prompt": item["original"], "enhanced_prompt": item["enhanced"]} 
        for item in sample_data
    ])
    csv_file = temp_dir / "sample_prompts.csv"
    csv_data.to_csv(csv_file, index=False)
    print(f"✅ Created CSV file: {csv_file}")
    
    # Create JSONL format
    jsonl_file = temp_dir / "sample_prompts.jsonl"
    with open(jsonl_file, 'w', encoding='utf-8') as f:
        for item in sample_data[:2]:  # Just first 2 for JSONL example
            json.dump({
                "input": item["original"],
                "output": item["enhanced"]
            }, f)
            f.write('\n')
    print(f"✅ Created JSONL file: {jsonl_file}")
    
    # Create JSON format
    json_file = temp_dir / "sample_prompts.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump([
            {"user_prompt": item["original"], "optimized_prompt": item["enhanced"]} 
            for item in sample_data[:3]  # First 3 for JSON example
        ], f, indent=2)
    print(f"✅ Created JSON file: {json_file}")
    
    # Create TXT format with delimiter
    txt_file = temp_dir / "sample_prompts.txt"
    with open(txt_file, 'w', encoding='utf-8') as f:
        for i, item in enumerate(sample_data):
            f.write(item["original"])
            f.write('\n---\n')
            f.write(item["enhanced"])
            if i < len(sample_data) - 1:
                f.write('\n---\n')
    print(f"✅ Created TXT file: {txt_file}")
    
    return temp_dir

def run_normalization_examples(sample_dir):
    """Run normalization examples with different options."""
    print("\n🚀 Running normalization examples...")
    
    script_path = Path(__file__).parent / "normalize_datasets.py"
    
    # Get the Python executable from the current environment
    python_exe = sys.executable
    
    examples = [
        {
            "name": "Basic CSV Normalization",
            "cmd": [python_exe, str(script_path), str(sample_dir / "sample_prompts.csv")],
            "description": "Simple normalization of CSV file with default settings"
        },
        {
            "name": "JSONL with Custom Prefix",
            "cmd": [python_exe, str(script_path), str(sample_dir / "sample_prompts.jsonl"), "--output-prefix", "custom_jsonl"],
            "description": "Normalize JSONL with custom output filename prefix"
        },
        {
            "name": "JSON with Verbose Output",
            "cmd": [python_exe, str(script_path), str(sample_dir / "sample_prompts.json"), "--verbose", "--output-prefix", "verbose_json"],
            "description": "Normalize JSON with detailed logging output"
        },
        {
            "name": "TXT with Small Batch Size",
            "cmd": [python_exe, str(script_path), str(sample_dir / "sample_prompts.txt"), "--batch-size", "2", "--output-prefix", "batch_txt"],
            "description": "Normalize TXT file with small batch size for demonstration"
        }
    ]
    
    for example in examples:
        print(f"\n📋 Example: {example['name']}")
        print(f"📖 Description: {example['description']}")
        print(f"🔧 Command: {' '.join(example['cmd'])}")
        
        try:
            # Change to the correct directory
            result = subprocess.run(
                example['cmd'], 
                cwd=Path(__file__).parent.parent,  # Run from project root
                capture_output=True, 
                text=True, 
                timeout=60
            )
            
            if result.returncode == 0:
                print("✅ Success!")
                # Extract key statistics from output
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if 'Success Rate:' in line or 'Domain Distribution:' in line or 'Records/Second:' in line:
                        print(f"   {line.strip()}")
            else:
                print(f"❌ Failed with return code {result.returncode}")
                if result.stderr:
                    print(f"   Error: {result.stderr[:200]}...")
                    
        except subprocess.TimeoutExpired:
            print("❌ Timeout - command took too long")
        except Exception as e:
            print(f"❌ Exception: {str(e)}")

def analyze_results(sample_dir):
    """Analyze the results of normalization."""
    print("\n📊 Analyzing normalization results...")
    
    # Look for processed data directory
    processed_dir = Path(__file__).parent.parent / "data" / "processed"
    
    if not processed_dir.exists():
        print("⚠️ No processed data directory found")
        return
    
    # Find all JSON files (excluding statistics)
    result_files = list(processed_dir.glob("**/*.json"))
    result_files = [f for f in result_files if "statistics" not in f.name]
    
    print(f"📁 Found {len(result_files)} result files:")
    
    domain_counts = {}
    total_records = 0
    
    for file_path in result_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'records' in data and 'metadata' in data:
                domain = data['metadata']['domain']
                record_count = data['metadata']['record_count']
                
                domain_counts[domain] = domain_counts.get(domain, 0) + record_count
                total_records += record_count
                
                print(f"   📄 {file_path.name}: {record_count} {domain} records")
                
        except Exception as e:
            print(f"   ❌ Error reading {file_path.name}: {str(e)}")
    
    print(f"\n📈 Summary:")
    print(f"   Total Records Normalized: {total_records}")
    for domain, count in domain_counts.items():
        percentage = (count / total_records * 100) if total_records > 0 else 0
        print(f"   {domain}: {count} records ({percentage:.1f}%)")
    
    # Find and analyze statistics files
    stats_files = list(processed_dir.glob("**/*statistics*.json"))
    if stats_files:
        print(f"\n📊 Statistics files found: {len(stats_files)}")
        
        for stats_file in stats_files[-2:]:  # Show last 2 statistics files
            try:
                with open(stats_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
                
                summary = stats.get('processing_summary', {})
                print(f"\n   📋 {stats_file.name}:")
                print(f"      Success Rate: {summary.get('success_rate', 'N/A'):.1f}%")
                print(f"      Processing Speed: {summary.get('records_per_second', 'N/A'):.1f} records/sec")
                print(f"      Total Processed: {summary.get('total_processed', 'N/A')}")
                
            except Exception as e:
                print(f"   ❌ Error reading statistics {stats_file.name}: {str(e)}")

def demonstrate_error_handling():
    """Demonstrate error handling capabilities."""
    print("\n🧪 Demonstrating error handling...")
    
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create a CSV with various problematic records
    problematic_data = [
        {"original_prompt": "", "enhanced_prompt": "Valid enhanced prompt"},  # Empty original
        {"original_prompt": "Valid original", "enhanced_prompt": ""},  # Empty enhanced  
        {"original_prompt": "x" * 5000, "enhanced_prompt": "Valid enhanced"},  # Too long original
        {"original_prompt": "Valid original", "enhanced_prompt": "Short"},  # Too short enhanced
        {"original_prompt": "Good original prompt with sufficient length", "enhanced_prompt": "Good enhanced prompt with comprehensive improvements and detailed explanations"},  # Valid record
    ]
    
    csv_file = temp_dir / "problematic_prompts.csv"
    pd.DataFrame(problematic_data).to_csv(csv_file, index=False)
    
    print(f"📁 Created problematic dataset: {csv_file}")
    
    # Run normalization
    script_path = Path(__file__).parent / "normalize_datasets.py"
    python_exe = sys.executable
    
    cmd = [python_exe, str(script_path), str(csv_file), "--output-prefix", "error_test", "--verbose"]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"🔍 Command completed with return code: {result.returncode}")
        
        # Extract error information from output
        output_lines = result.stdout.split('\n')
        for line in output_lines:
            if 'Success Rate:' in line or 'Failed Normalizations:' in line or 'Errors:' in line:
                print(f"   📊 {line.strip()}")
        
        # Look for warnings in stderr
        if result.stderr:
            stderr_lines = result.stderr.split('\n')[:10]  # First 10 lines
            print("   ⚠️ Warnings/Errors detected:")
            for line in stderr_lines:
                if line.strip() and 'WARNING' in line:
                    print(f"      {line.strip()}")
                    
    except Exception as e:
        print(f"❌ Error running demonstration: {str(e)}")
    
    # Clean up
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    """Main demonstration function."""
    print("🎯 PromptEvolver 3.0 Dataset Normalization - Usage Examples")
    print("=" * 65)
    
    try:
        # Create sample datasets
        sample_dir = create_sample_datasets()
        
        # Run normalization examples
        run_normalization_examples(sample_dir)
        
        # Analyze results
        analyze_results(sample_dir)
        
        # Demonstrate error handling
        demonstrate_error_handling()
        
        print("\n🎉 All examples completed successfully!")
        print(f"📁 Sample datasets are available in: {sample_dir}")
        print("📁 Normalized results are in: data/processed/")
        
        # Clean up sample directory
        cleanup = input("\n🗑️ Clean up sample datasets? (y/n): ").lower().strip()
        if cleanup == 'y':
            import shutil
            shutil.rmtree(sample_dir, ignore_errors=True)
            print("✅ Sample datasets cleaned up")
        else:
            print(f"📁 Sample datasets preserved in: {sample_dir}")
            
    except KeyboardInterrupt:
        print("\n⏹️ Demonstration interrupted by user")
    except Exception as e:
        print(f"\n❌ Demonstration failed: {str(e)}")

if __name__ == "__main__":
    main()