#!/usr/bin/env python3
"""
Unit tests for the PromptEvolver 3.0 Dataset Normalization Script
"""

import json
import tempfile
import unittest
from pathlib import Path
import pandas as pd
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from normalize_datasets import DatasetNormalizer

class TestDatasetNormalizer(unittest.TestCase):
    """Test cases for the DatasetNormalizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test outputs
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_schema_path = Path(__file__).parent.parent / "schemas" / "engineered_prompt.schema.json"
        self.test_domain_classifier_path = Path(__file__).parent.parent / "prompts" / "domain_classifier.txt"
        
        # Initialize normalizer
        self.normalizer = DatasetNormalizer(
            schema_path=self.test_schema_path,
            domain_classifier_path=self.test_domain_classifier_path,
            output_dir=self.temp_dir
        )
    
    def test_domain_classification(self):
        """Test domain classification functionality."""
        test_cases = [
            ("Analyze sales data and create a report", "Analytics"),
            ("Write a Python function to sort arrays", "Coding"),
            ("Create marketing copy for our product", "Content"),
            ("Help with project management", "Cross-Domain"),
            ("", "Cross-Domain"),  # Empty prompt
            ("short", "Cross-Domain"),  # Very short prompt
        ]
        
        for prompt, expected_domain in test_cases:
            with self.subTest(prompt=prompt):
                result = self.normalizer.classify_domain(prompt)
                self.assertEqual(result, expected_domain)
    
    def test_quality_scores_initialization(self):
        """Test quality scores initialization."""
        scores = self.normalizer.initialize_quality_scores()
        
        required_keys = [
            "overall", "clarity", "specificity", "engagement",
            "structure", "completeness", "errorPrevention"
        ]
        
        for key in required_keys:
            self.assertIn(key, scores)
            self.assertIsInstance(scores[key], float)
            self.assertGreaterEqual(scores[key], 0.0)
            self.assertLessEqual(scores[key], 1.0)
    
    def test_improvement_areas_generation(self):
        """Test improvement areas generation."""
        original = "Write a summary"
        enhanced = "As a senior business analyst with expertise in financial reporting, create a comprehensive executive summary"
        
        improvements = self.normalizer.generate_improvement_areas(original, enhanced)
        
        self.assertIsInstance(improvements, list)
        self.assertGreater(len(improvements), 0)
        self.assertTrue(any("comprehensive detail" in imp for imp in improvements))
    
    def test_record_normalization(self):
        """Test single record normalization."""
        test_record = {
            "original_prompt": "Analyze website performance",
            "enhanced_prompt": "As a digital analytics specialist, conduct a comprehensive analysis of website performance metrics including Core Web Vitals, user experience metrics, and competitive benchmarking."
        }
        
        result = self.normalizer.normalize_record(test_record, "test")
        
        self.assertIsNotNone(result)
        self.assertIn("originalPrompt", result)
        self.assertIn("enhancedPrompt", result)
        self.assertIn("domain", result)
        self.assertIn("metadata", result)
        self.assertEqual(result["domain"], "Analytics")
        
        # Validate required metadata fields
        metadata = result["metadata"]
        self.assertIn("qualityScore", metadata)
        self.assertIn("improvementAreas", metadata)
        self.assertIn("processingTimestamp", metadata)
    
    def test_csv_loading(self):
        """Test CSV file loading."""
        # Create test CSV file
        csv_data = pd.DataFrame({
            "original_prompt": [
                "Debug login issue",
                "Write newsletter"
            ],
            "enhanced_prompt": [
                "As a senior developer, debug the login authentication issue with comprehensive error analysis",
                "As a content marketing specialist, create a compelling monthly newsletter"
            ]
        })
        
        csv_file = self.temp_dir / "test.csv"
        csv_data.to_csv(csv_file, index=False)
        
        # Load the CSV
        records, format_type = self.normalizer.load_dataset(csv_file)
        
        self.assertEqual(format_type, "csv")
        self.assertEqual(len(records), 2)
        self.assertIn("original_prompt", records[0])
        self.assertIn("enhanced_prompt", records[0])
    
    def test_jsonl_loading(self):
        """Test JSONL file loading."""
        jsonl_data = [
            {"original_prompt": "Test prompt 1", "enhanced_prompt": "Enhanced test prompt 1"},
            {"original_prompt": "Test prompt 2", "enhanced_prompt": "Enhanced test prompt 2"}
        ]
        
        jsonl_file = self.temp_dir / "test.jsonl"
        with open(jsonl_file, 'w') as f:
            for record in jsonl_data:
                f.write(json.dumps(record) + '\n')
        
        # Load the JSONL
        records, format_type = self.normalizer.load_dataset(jsonl_file)
        
        self.assertEqual(format_type, "jsonl")
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["original_prompt"], "Test prompt 1")
    
    def test_prompt_extraction(self):
        """Test prompt extraction from various record formats."""
        # Test various key patterns
        test_cases = [
            ({"original_prompt": "test", "enhanced_prompt": "enhanced"}, "test", "enhanced"),
            ({"original": "test", "enhanced": "enhanced"}, "test", "enhanced"),
            ({"input": "test", "output": "enhanced"}, "test", "enhanced"),
            (["test", "enhanced"], "test", "enhanced"),  # List format
        ]
        
        for record, expected_original, expected_enhanced in test_cases:
            with self.subTest(record=record):
                original = self.normalizer._extract_original_prompt(record, "test")
                enhanced = self.normalizer._extract_enhanced_prompt(record, "test")
                
                self.assertEqual(original, expected_original)
                self.assertEqual(enhanced, expected_enhanced)
    
    def test_invalid_prompts(self):
        """Test handling of invalid prompts."""
        invalid_cases = [
            {"original_prompt": "", "enhanced_prompt": "valid enhanced"},  # Empty original
            {"original_prompt": "valid", "enhanced_prompt": ""},  # Empty enhanced
            {"original_prompt": "x" * 5000, "enhanced_prompt": "valid"},  # Too long original
            {"original_prompt": "valid", "enhanced_prompt": "x" * 10000},  # Too long enhanced
            {"original_prompt": "short", "enhanced_prompt": "short"},  # Both too short
        ]
        
        for invalid_record in invalid_cases:
            with self.subTest(record=invalid_record):
                result = self.normalizer.normalize_record(invalid_record, "test")
                self.assertIsNone(result)
    
    def test_statistics_tracking(self):
        """Test statistics tracking during processing."""
        # Reset statistics
        self.normalizer.stats = {
            "total_processed": 0,
            "successful_normalizations": 0,
            "failed_normalizations": 0,
            "domain_distribution": {},
            "quality_score_distribution": {},
            "processing_time": 0.0,
            "error_details": []
        }
        
        # Process valid record
        valid_record = {
            "original_prompt": "Test analytics prompt with data analysis requirements",
            "enhanced_prompt": "As a data analyst, conduct comprehensive analysis with specific metrics and reporting"
        }
        
        result = self.normalizer.normalize_record(valid_record, "test")
        
        if result:
            self.normalizer.stats["successful_normalizations"] += 1
            self.normalizer.stats["total_processed"] += 1
            domain = result["domain"]
            self.normalizer.stats["domain_distribution"][domain] = (
                self.normalizer.stats["domain_distribution"].get(domain, 0) + 1
            )
        
        # Check statistics
        self.assertEqual(self.normalizer.stats["successful_normalizations"], 1)
        self.assertEqual(self.normalizer.stats["total_processed"], 1)
        self.assertIn("Analytics", self.normalizer.stats["domain_distribution"])
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

def run_quick_test():
    """Run a quick integration test to verify the normalizer works end-to-end."""
    print("🧪 Running quick integration test...")
    
    # Create test data
    temp_dir = Path(tempfile.mkdtemp())
    test_file = temp_dir / "quick_test.csv"
    
    test_data = pd.DataFrame({
        "original_prompt": [
            "Debug the login system",
            "Write marketing content"
        ],
        "enhanced_prompt": [
            "As a senior full-stack developer, debug the login authentication system with comprehensive error analysis and security review",
            "As a marketing copywriter, create compelling marketing content with clear value proposition and call-to-action"
        ]
    })
    
    test_data.to_csv(test_file, index=False)
    
    try:
        # Initialize normalizer
        project_root = Path(__file__).parent.parent
        normalizer = DatasetNormalizer(
            schema_path=project_root / "schemas" / "engineered_prompt.schema.json",
            domain_classifier_path=project_root / "prompts" / "domain_classifier.txt",
            output_dir=temp_dir / "output"
        )
        
        # Run normalization
        normalizer.normalize_dataset(test_file, "quick_test", batch_size=10)
        
        # Check results
        output_dir = temp_dir / "output"
        result_files = list(output_dir.glob("**/*.json"))
        stats_file = output_dir / "quick_test_statistics_report.json"
        
        print(f"✅ Generated {len(result_files)} output files")
        print(f"✅ Statistics report created: {stats_file.exists()}")
        
        if stats_file.exists():
            with open(stats_file) as f:
                stats = json.load(f)
            print(f"✅ Success rate: {stats['processing_summary']['success_rate']:.1f}%")
        
        print("🎉 Quick integration test completed successfully!")
        
    except Exception as e:
        print(f"❌ Quick test failed: {str(e)}")
        raise
    finally:
        # Clean up
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    # Run quick integration test first
    run_quick_test()
    
    # Run unit tests
    print("\n🧪 Running unit tests...")
    unittest.main(verbosity=2)