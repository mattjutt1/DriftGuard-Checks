#!/usr/bin/env python3
"""
PromptEvolver 3.0 Dataset Normalization Script
===============================================

Comprehensive dataset normalization system for converting various prompt dataset 
formats into the standardized PromptEvolver 3.0 engineered prompt schema format.

Features:
- Multi-format input support (CSV, JSON, JSONL, TXT, Parquet)
- Domain classification using our specialized classifier
- Quality score initialization and metadata generation
- Batch processing with progress tracking
- Schema validation and error handling
- Statistics reporting and output segregation by domain

Copyright (c) 2025 Matthew J. Utt
Licensed under MIT License
Compatible with Microsoft PromptWizard Framework
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
import argparse
import sys
import os

# Third-party imports
try:
    import pandas as pd
    import jsonschema
    from tqdm import tqdm
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError as e:
    print(f"❌ Missing required dependency: {e}")
    print("💡 Install with: pip install pandas jsonschema tqdm pyarrow")
    sys.exit(1)

# Local imports
script_dir = Path(__file__).parent
project_root = script_dir.parent

# Add project paths
sys.path.insert(0, str(project_root))

class DatasetNormalizer:
    """
    Comprehensive dataset normalization engine for PromptEvolver 3.0.
    
    Converts various prompt dataset formats into standardized schema format
    with domain classification, quality scoring, and metadata generation.
    """
    
    def __init__(self, 
                 schema_path: Optional[Path] = None,
                 domain_classifier_path: Optional[Path] = None,
                 output_dir: Optional[Path] = None):
        """
        Initialize the dataset normalizer.
        
        Args:
            schema_path: Path to engineered_prompt.schema.json
            domain_classifier_path: Path to domain classifier prompt
            output_dir: Output directory for normalized datasets
        """
        self.project_root = project_root
        self.schema_path = schema_path or project_root / "schemas" / "engineered_prompt.schema.json"
        self.domain_classifier_path = domain_classifier_path or project_root / "prompts" / "domain_classifier.txt"
        self.output_dir = Path(output_dir) if output_dir else project_root / "data" / "processed"
        
        # Initialize components
        self._setup_logging()
        self._load_schema()
        self._load_domain_classifier()
        self._ensure_output_directories()
        
        # Processing statistics
        self.stats = {
            "total_processed": 0,
            "successful_normalizations": 0,
            "failed_normalizations": 0,
            "domain_distribution": {},
            "quality_score_distribution": {},
            "processing_time": 0.0,
            "error_details": []
        }
    
    def _setup_logging(self) -> None:
        """Configure logging for the normalization process."""
        log_dir = self.project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"normalize_datasets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("🚀 Initialized PromptEvolver 3.0 Dataset Normalizer")
    
    def _load_schema(self) -> None:
        """Load and validate the engineered prompt schema."""
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                self.schema = json.load(f)
            self.logger.info(f"✅ Loaded schema from {self.schema_path}")
        except FileNotFoundError:
            self.logger.error(f"❌ Schema file not found: {self.schema_path}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ Invalid JSON schema: {e}")
            raise
    
    def _load_domain_classifier(self) -> None:
        """Load the domain classifier prompt template."""
        try:
            with open(self.domain_classifier_path, 'r', encoding='utf-8') as f:
                self.domain_classifier_prompt = f.read()
            self.logger.info(f"✅ Loaded domain classifier from {self.domain_classifier_path}")
        except FileNotFoundError:
            self.logger.warning(f"⚠️ Domain classifier not found: {self.domain_classifier_path}")
            self.domain_classifier_prompt = None
    
    def _ensure_output_directories(self) -> None:
        """Create output directories for normalized datasets."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create domain-specific directories
        for domain in ["Analytics", "Coding", "Content", "Cross-Domain"]:
            (self.output_dir / domain.lower().replace("-", "_")).mkdir(exist_ok=True)
        
        self.logger.info(f"✅ Output directories ready at {self.output_dir}")
    
    def classify_domain(self, prompt: str) -> str:
        """
        Classify the domain of a prompt using rule-based classification.
        
        Args:
            prompt: The prompt text to classify
            
        Returns:
            Domain classification (Analytics, Coding, Content, Cross-Domain)
        """
        if not prompt or len(prompt.strip()) < 5:
            return "Cross-Domain"
        
        prompt_lower = prompt.lower()
        
        # Domain keyword patterns
        analytics_keywords = [
            'analyze', 'analysis', 'data', 'metrics', 'report', 'dashboard', 
            'insights', 'trends', 'statistics', 'kpi', 'performance', 
            'visualization', 'chart', 'graph', 'correlation', 'regression',
            'calculate', 'measure', 'evaluate', 'assess'
        ]
        
        coding_keywords = [
            'code', 'function', 'class', 'api', 'framework', 'library', 
            'debug', 'implement', 'deploy', 'test', 'algorithm', 'database',
            'frontend', 'backend', 'programming', 'software', 'development',
            'python', 'javascript', 'react', 'nodejs', 'sql', 'html', 'css'
        ]
        
        content_keywords = [
            'write', 'content', 'copy', 'blog', 'article', 'marketing', 
            'brand', 'audience', 'message', 'story', 'tone', 'style', 
            'engagement', 'campaign', 'social', 'email', 'communication',
            'creative', 'copywriting', 'seo', 'content creation'
        ]
        
        # Count keyword matches
        analytics_score = sum(1 for keyword in analytics_keywords if keyword in prompt_lower)
        coding_score = sum(1 for keyword in coding_keywords if keyword in prompt_lower)
        content_score = sum(1 for keyword in content_keywords if keyword in prompt_lower)
        
        # Determine primary domain
        scores = {
            "Analytics": analytics_score,
            "Coding": coding_score,
            "Content": content_score
        }
        
        max_score = max(scores.values())
        
        # If no clear winner or multiple domains have equal high scores
        if max_score == 0 or list(scores.values()).count(max_score) > 1:
            return "Cross-Domain"
        
        # Return domain with highest score
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def initialize_quality_scores(self) -> Dict[str, float]:
        """
        Initialize quality scores for a new prompt.
        
        Returns:
            Dictionary of quality score metrics
        """
        # Base quality scores (will be improved by actual evaluation in production)
        return {
            "overall": 0.75,
            "clarity": 0.73,
            "specificity": 0.72,
            "engagement": 0.76,
            "structure": 0.74,
            "completeness": 0.71,
            "errorPrevention": 0.70
        }
    
    def generate_improvement_areas(self, original: str, enhanced: str) -> List[str]:
        """
        Generate improvement areas based on prompt comparison.
        
        Args:
            original: Original prompt text
            enhanced: Enhanced prompt text
            
        Returns:
            List of improvement area descriptions
        """
        improvements = []
        
        # Length-based improvements
        if len(enhanced) > len(original) * 1.5:
            improvements.append("Added comprehensive detail and specificity")
        
        # Structure improvements
        if enhanced.count('\n') > original.count('\n'):
            improvements.append("Enhanced structure with clear formatting")
        
        # Context improvements
        if any(word in enhanced.lower() for word in ['role', 'expert', 'specialist', 'as a']):
            improvements.append("Added professional role context")
        
        # Specificity improvements
        if any(word in enhanced.lower() for word in ['specific', 'exactly', 'precisely', 'detailed']):
            improvements.append("Increased specificity and precision")
        
        # Audience targeting
        if any(word in enhanced.lower() for word in ['audience', 'target', 'stakeholder', 'reader']):
            improvements.append("Defined target audience clearly")
        
        # Format requirements
        if any(word in enhanced.lower() for word in ['format', 'structure', 'sections', 'bullet']):
            improvements.append("Specified output format requirements")
        
        # Constraints and requirements
        if any(word in enhanced.lower() for word in ['length', 'word', 'characters', 'limit']):
            improvements.append("Added length and constraint specifications")
        
        # Default improvement if none detected
        if not improvements:
            improvements.append("Enhanced clarity and actionability")
        
        return improvements
    
    def normalize_record(self, record: Dict[str, Any], source_format: str) -> Optional[Dict[str, Any]]:
        """
        Normalize a single record to the engineered prompt schema.
        
        Args:
            record: Input record data
            source_format: Source format identifier
            
        Returns:
            Normalized record or None if normalization fails
        """
        try:
            # Extract original and enhanced prompts based on source format
            original_prompt = self._extract_original_prompt(record, source_format)
            enhanced_prompt = self._extract_enhanced_prompt(record, source_format)
            
            if not original_prompt or not enhanced_prompt:
                self.logger.warning(f"⚠️ Missing prompts in record: {record}")
                return None
            
            # Validate prompt lengths
            if len(original_prompt) < 10 or len(original_prompt) > 4000:
                self.logger.warning(f"⚠️ Original prompt length out of range: {len(original_prompt)}")
                return None
                
            if len(enhanced_prompt) < 20 or len(enhanced_prompt) > 8000:
                self.logger.warning(f"⚠️ Enhanced prompt length out of range: {len(enhanced_prompt)}")
                return None
            
            # Classify domain
            domain = self.classify_domain(original_prompt)
            
            # Generate improvement areas
            improvement_areas = self.generate_improvement_areas(original_prompt, enhanced_prompt)
            
            # Create normalized record
            normalized_record = {
                "originalPrompt": original_prompt.strip(),
                "enhancedPrompt": enhanced_prompt.strip(),
                "domain": domain,
                "metadata": {
                    "qualityScore": self.initialize_quality_scores(),
                    "improvementAreas": improvement_areas,
                    "processingTimestamp": int(time.time()),
                    "expertIdentity": f"{domain} Specialist",
                    "optimizationConfig": {
                        "iterations": 3,
                        "rounds": 3,
                        "temperature": 0.7,
                        "generateReasoning": True,
                        "generateExpertIdentity": True
                    },
                    "reasoning": f"Prompt enhanced for {domain.lower()} domain with improved clarity, specificity, and structure."
                },
                "followUpQuestions": [],
                "tags": [domain.lower().replace("-", ""), "normalized", "training-data"],
                "version": "1.0"
            }
            
            # Validate against schema
            jsonschema.validate(normalized_record, self.schema)
            
            return normalized_record
            
        except jsonschema.ValidationError as e:
            self.logger.error(f"❌ Schema validation failed: {e.message}")
            self.stats["error_details"].append(f"Schema validation: {e.message}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Normalization error: {str(e)}")
            self.stats["error_details"].append(f"Normalization: {str(e)}")
            return None
    
    def _extract_original_prompt(self, record: Dict[str, Any], source_format: str) -> Optional[str]:
        """Extract original prompt from record based on source format."""
        # Handle list/tuple formats first
        if isinstance(record, (list, tuple)) and len(record) >= 2:
            return str(record[0]).strip()
        
        # Handle dict formats
        if isinstance(record, dict):
            possible_keys = [
                'original_prompt', 'originalPrompt', 'original', 'input', 'prompt', 'question', 'weak_prompt',
                'user_prompt', 'before', 'source', 'raw_prompt', 'initial_prompt', 'base_prompt'
            ]
            
            for key in possible_keys:
                if key in record and record[key]:
                    return str(record[key]).strip()
        
        return None
    
    def _extract_enhanced_prompt(self, record: Dict[str, Any], source_format: str) -> Optional[str]:
        """Extract enhanced prompt from record based on source format."""
        # Handle list/tuple formats first
        if isinstance(record, (list, tuple)) and len(record) >= 2:
            return str(record[1]).strip()
        
        # Handle dict formats
        if isinstance(record, dict):
            possible_keys = [
                'enhanced_prompt', 'enhancedPrompt', 'enhanced', 'output', 'improved', 'answer', 'strong_prompt',
                'optimized_prompt', 'after', 'target', 'refined_prompt', 'final_prompt', 'better_prompt'
            ]
            
            for key in possible_keys:
                if key in record and record[key]:
                    return str(record[key]).strip()
        
        return None
    
    def load_dataset(self, file_path: Path) -> Tuple[List[Dict[str, Any]], str]:
        """
        Load dataset from various file formats.
        
        Args:
            file_path: Path to the dataset file
            
        Returns:
            Tuple of (records, source_format)
        """
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()
        
        self.logger.info(f"📂 Loading dataset from {file_path}")
        
        try:
            if suffix == '.csv':
                df = pd.read_csv(file_path)
                records = df.to_dict('records')
                return records, 'csv'
                
            elif suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if isinstance(data, list):
                    return data, 'json_list'
                else:
                    return [data], 'json_object'
                    
            elif suffix == '.jsonl':
                records = []
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                records.append(json.loads(line))
                            except json.JSONDecodeError as e:
                                self.logger.warning(f"⚠️ Skipping invalid JSON line: {line[:100]}...")
                return records, 'jsonl'
                
            elif suffix == '.txt':
                records = []
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    
                # Try different delimiter patterns
                for delimiter in ['\n---\n', '\n##\n', '\n\n\n', '\t\t']:
                    if delimiter in content:
                        pairs = content.split(delimiter)
                        for i in range(0, len(pairs)-1, 2):
                            if i+1 < len(pairs):
                                records.append({
                                    'original': pairs[i].strip(),
                                    'enhanced': pairs[i+1].strip()
                                })
                        break
                else:
                    # Fallback: assume alternating lines
                    lines = [l.strip() for l in content.split('\n') if l.strip()]
                    for i in range(0, len(lines)-1, 2):
                        if i+1 < len(lines):
                            records.append({
                                'original': lines[i],
                                'enhanced': lines[i+1]
                            })
                
                return records, 'txt'
                
            elif suffix == '.parquet':
                df = pd.read_parquet(file_path)
                records = df.to_dict('records')
                return records, 'parquet'
                
            else:
                raise ValueError(f"Unsupported file format: {suffix}")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to load dataset: {str(e)}")
            raise
    
    def save_normalized_dataset(self, records: List[Dict[str, Any]], output_prefix: str) -> None:
        """
        Save normalized records to output files, segregated by domain.
        
        Args:
            records: List of normalized records
            output_prefix: Prefix for output filenames
        """
        # Group records by domain
        domain_records = {}
        for record in records:
            domain = record['domain']
            if domain not in domain_records:
                domain_records[domain] = []
            domain_records[domain].append(record)
        
        # Save each domain separately
        for domain, domain_data in domain_records.items():
            domain_dir = self.output_dir / domain.lower().replace("-", "_")
            output_file = domain_dir / f"{output_prefix}_{domain.lower().replace('-', '_')}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "metadata": {
                        "domain": domain,
                        "record_count": len(domain_data),
                        "generation_timestamp": int(time.time()),
                        "schema_version": "1.0",
                        "source": output_prefix
                    },
                    "records": domain_data
                }, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"💾 Saved {len(domain_data)} {domain} records to {output_file}")
    
    def generate_statistics_report(self, output_prefix: str) -> None:
        """Generate and save processing statistics report."""
        report = {
            "processing_summary": {
                "total_processed": self.stats["total_processed"],
                "successful_normalizations": self.stats["successful_normalizations"],
                "failed_normalizations": self.stats["failed_normalizations"],
                "success_rate": (
                    self.stats["successful_normalizations"] / max(self.stats["total_processed"], 1)
                ) * 100,
                "processing_time_seconds": self.stats["processing_time"],
                "records_per_second": (
                    self.stats["total_processed"] / max(self.stats["processing_time"], 0.1)
                )
            },
            "domain_distribution": self.stats["domain_distribution"],
            "quality_metrics": {
                "average_quality_score": (
                    sum(self.stats["quality_score_distribution"].values()) / 
                    max(len(self.stats["quality_score_distribution"]), 1)
                )
            },
            "error_analysis": {
                "error_count": len(self.stats["error_details"]),
                "error_details": self.stats["error_details"][:10]  # First 10 errors
            },
            "generation_metadata": {
                "timestamp": int(time.time()),
                "normalizer_version": "1.0",
                "schema_version": "1.0"
            }
        }
        
        report_file = self.output_dir / f"{output_prefix}_statistics_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📊 Statistics report saved to {report_file}")
        
        # Print summary to console
        print("\n" + "="*60)
        print("📊 NORMALIZATION STATISTICS SUMMARY")
        print("="*60)
        print(f"Total Records Processed: {self.stats['total_processed']}")
        print(f"Successful Normalizations: {self.stats['successful_normalizations']}")
        print(f"Failed Normalizations: {self.stats['failed_normalizations']}")
        print(f"Success Rate: {report['processing_summary']['success_rate']:.1f}%")
        print(f"Processing Time: {self.stats['processing_time']:.2f} seconds")
        print(f"Records/Second: {report['processing_summary']['records_per_second']:.1f}")
        
        print("\n📈 Domain Distribution:")
        for domain, count in self.stats["domain_distribution"].items():
            percentage = (count / max(self.stats["successful_normalizations"], 1)) * 100
            print(f"  {domain}: {count} ({percentage:.1f}%)")
        
        if self.stats["error_details"]:
            print(f"\n⚠️ Errors: {len(self.stats['error_details'])} total")
        
        print("="*60)
    
    def normalize_dataset(self, 
                         input_file: Union[str, Path], 
                         output_prefix: Optional[str] = None,
                         batch_size: int = 1000) -> None:
        """
        Main method to normalize a dataset file.
        
        Args:
            input_file: Path to input dataset file
            output_prefix: Prefix for output files (defaults to input filename)
            batch_size: Number of records to process in each batch
        """
        start_time = time.time()
        input_path = Path(input_file)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        if output_prefix is None:
            output_prefix = input_path.stem
        
        self.logger.info(f"🚀 Starting normalization of {input_path}")
        
        # Load dataset
        try:
            raw_records, source_format = self.load_dataset(input_path)
            self.logger.info(f"📊 Loaded {len(raw_records)} records from {source_format} format")
        except Exception as e:
            self.logger.error(f"❌ Failed to load dataset: {str(e)}")
            return
        
        # Process records in batches
        normalized_records = []
        
        with tqdm(total=len(raw_records), desc="Normalizing records") as pbar:
            for i, record in enumerate(raw_records):
                self.stats["total_processed"] += 1
                
                normalized_record = self.normalize_record(record, source_format)
                
                if normalized_record:
                    normalized_records.append(normalized_record)
                    self.stats["successful_normalizations"] += 1
                    
                    # Update domain distribution
                    domain = normalized_record["domain"]
                    self.stats["domain_distribution"][domain] = (
                        self.stats["domain_distribution"].get(domain, 0) + 1
                    )
                    
                    # Track quality scores
                    overall_score = normalized_record["metadata"]["qualityScore"]["overall"]
                    self.stats["quality_score_distribution"][i] = overall_score
                else:
                    self.stats["failed_normalizations"] += 1
                
                pbar.update(1)
                
                # Save batch if needed
                if batch_size and len(normalized_records) >= batch_size:
                    self.logger.info(f"💾 Saving batch of {len(normalized_records)} records")
                    self.save_normalized_dataset(normalized_records, f"{output_prefix}_batch_{i//batch_size}")
                    normalized_records = []
        
        # Save remaining records
        if normalized_records:
            self.save_normalized_dataset(normalized_records, output_prefix)
        
        # Calculate final statistics
        self.stats["processing_time"] = time.time() - start_time
        
        # Generate report
        self.generate_statistics_report(output_prefix)
        
        self.logger.info(f"✅ Normalization complete! Processed {self.stats['total_processed']} records")

def main():
    """Command-line interface for the dataset normalizer."""
    parser = argparse.ArgumentParser(
        description="PromptEvolver 3.0 Dataset Normalization Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python normalize_datasets.py input.csv
  python normalize_datasets.py data.jsonl --output-prefix "training_data"
  python normalize_datasets.py prompts.parquet --batch-size 500
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Path to the input dataset file (CSV, JSON, JSONL, TXT, Parquet)'
    )
    
    parser.add_argument(
        '--output-prefix',
        help='Prefix for output filenames (defaults to input filename)'
    )
    
    parser.add_argument(
        '--output-dir',
        help='Output directory for normalized datasets (defaults to data/processed)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=1000,
        help='Number of records to process in each batch (default: 1000)'
    )
    
    parser.add_argument(
        '--schema-path',
        help='Path to engineered_prompt.schema.json file'
    )
    
    parser.add_argument(
        '--domain-classifier-path',
        help='Path to domain classifier prompt file'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize normalizer
        normalizer = DatasetNormalizer(
            schema_path=Path(args.schema_path) if args.schema_path else None,
            domain_classifier_path=Path(args.domain_classifier_path) if args.domain_classifier_path else None,
            output_dir=Path(args.output_dir) if args.output_dir else None
        )
        
        # Set logging level
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Run normalization
        normalizer.normalize_dataset(
            input_file=args.input_file,
            output_prefix=args.output_prefix,
            batch_size=args.batch_size
        )
        
        print("\n🎉 Dataset normalization completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Normalization interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Normalization failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()