#!/usr/bin/env python3
"""
Split Training Data into Train/Validation/Test Sets
====================================================
This script splits the generated and synthesized training pairs into:
- Training set (70%)
- Validation set (15%)
- Test set (15%)

Ensures balanced domain distribution across all splits.

Copyright (c) 2025 Matthew J. Utt
"""

import json
import logging
import random
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Split configuration
SPLIT_CONFIG = {
    "train_ratio": 0.70,
    "val_ratio": 0.15,
    "test_ratio": 0.15,
    "random_seed": 42,
    "stratify_by_domain": True,
    "stratify_by_quality": True,
    "quality_bins": 3,  # Low, Medium, High
    "min_samples_per_domain": 5,
    "ensure_balance": True
}

@dataclass
class DataSplit:
    """Represents a data split"""
    name: str
    data: List[Dict]
    statistics: Dict[str, Any]

class DataSplitter:
    """Main class for splitting training data"""
    
    def __init__(self):
        self.all_pairs = []
        self.train_data = []
        self.val_data = []
        self.test_data = []
        self.output_dir = Path(__file__).parent.parent / "data" / "processed" / "splits"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set random seed for reproducibility
        random.seed(SPLIT_CONFIG["random_seed"])
    
    def load_all_pairs(self) -> List[Dict]:
        """Load all pairs from seed and synthesized directories"""
        all_pairs = []
        
        # Load seed pairs
        seed_dir = Path(__file__).parent.parent / "data" / "processed" / "seed_pairs"
        if seed_dir.exists():
            for json_file in seed_dir.glob("*.json"):
                if "stats" not in json_file.name:
                    with open(json_file, 'r') as f:
                        pairs = json.load(f)
                        if isinstance(pairs, list):
                            for pair in pairs:
                                pair['source'] = 'seed'
                            all_pairs.extend(pairs)
                            logger.info(f"Loaded {len(pairs)} seed pairs from {json_file.name}")
        
        # Load synthesized pairs
        synth_dir = Path(__file__).parent.parent / "data" / "processed" / "synthesized_pairs"
        if synth_dir.exists():
            for json_file in synth_dir.glob("*.json"):
                if "stats" not in json_file.name:
                    with open(json_file, 'r') as f:
                        pairs = json.load(f)
                        if isinstance(pairs, list):
                            for pair in pairs:
                                pair['source'] = 'synthesized'
                            all_pairs.extend(pairs)
                            logger.info(f"Loaded {len(pairs)} synthesized pairs from {json_file.name}")
        
        self.all_pairs = all_pairs
        logger.info(f"Total pairs loaded: {len(all_pairs)}")
        return all_pairs
    
    def stratify_by_domain_and_quality(self, pairs: List[Dict]) -> Dict[str, Dict[str, List[Dict]]]:
        """Stratify pairs by domain and quality score"""
        stratified = defaultdict(lambda: defaultdict(list))
        
        for pair in pairs:
            domain = pair.get('domain', 'Unknown')
            
            # Get quality score
            quality_scores = pair.get('quality_scores', {})
            overall_score = quality_scores.get('overall', 0.5)
            
            # Bin quality score
            if overall_score < 0.6:
                quality_bin = 'low'
            elif overall_score < 0.8:
                quality_bin = 'medium'
            else:
                quality_bin = 'high'
            
            stratified[domain][quality_bin].append(pair)
        
        return stratified
    
    def split_stratified(self, pairs: List[Dict]) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """Split data with stratification"""
        if SPLIT_CONFIG["stratify_by_domain"] and SPLIT_CONFIG["stratify_by_quality"]:
            return self.split_with_double_stratification(pairs)
        elif SPLIT_CONFIG["stratify_by_domain"]:
            return self.split_with_domain_stratification(pairs)
        else:
            return self.split_random(pairs)
    
    def split_with_double_stratification(self, pairs: List[Dict]) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """Split with both domain and quality stratification"""
        stratified = self.stratify_by_domain_and_quality(pairs)
        
        train, val, test = [], [], []
        
        for domain, quality_bins in stratified.items():
            for quality_bin, bin_pairs in quality_bins.items():
                if not bin_pairs:
                    continue
                
                # Shuffle pairs
                random.shuffle(bin_pairs)
                
                # Calculate split sizes
                n_total = len(bin_pairs)
                n_train = int(n_total * SPLIT_CONFIG["train_ratio"])
                n_val = int(n_total * SPLIT_CONFIG["val_ratio"])
                
                # Split
                train.extend(bin_pairs[:n_train])
                val.extend(bin_pairs[n_train:n_train + n_val])
                test.extend(bin_pairs[n_train + n_val:])
                
                logger.info(f"  {domain}/{quality_bin}: {n_total} total -> "
                           f"{n_train} train, {n_val} val, {n_total - n_train - n_val} test")
        
        return train, val, test
    
    def split_with_domain_stratification(self, pairs: List[Dict]) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """Split with domain stratification only"""
        domain_pairs = defaultdict(list)
        
        for pair in pairs:
            domain = pair.get('domain', 'Unknown')
            domain_pairs[domain].append(pair)
        
        train, val, test = [], [], []
        
        for domain, dpairs in domain_pairs.items():
            # Shuffle pairs
            random.shuffle(dpairs)
            
            # Calculate split sizes
            n_total = len(dpairs)
            n_train = int(n_total * SPLIT_CONFIG["train_ratio"])
            n_val = int(n_total * SPLIT_CONFIG["val_ratio"])
            
            # Split
            train.extend(dpairs[:n_train])
            val.extend(dpairs[n_train:n_train + n_val])
            test.extend(dpairs[n_train + n_val:])
            
            logger.info(f"  {domain}: {n_total} total -> "
                       f"{n_train} train, {n_val} val, {n_total - n_train - n_val} test")
        
        return train, val, test
    
    def split_random(self, pairs: List[Dict]) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """Random split without stratification"""
        # Shuffle all pairs
        shuffled = pairs.copy()
        random.shuffle(shuffled)
        
        # Calculate split sizes
        n_total = len(shuffled)
        n_train = int(n_total * SPLIT_CONFIG["train_ratio"])
        n_val = int(n_total * SPLIT_CONFIG["val_ratio"])
        
        # Split
        train = shuffled[:n_train]
        val = shuffled[n_train:n_train + n_val]
        test = shuffled[n_train + n_val:]
        
        return train, val, test
    
    def validate_splits(self, train: List[Dict], val: List[Dict], test: List[Dict]) -> bool:
        """Validate that splits meet requirements"""
        logger.info("\nValidating splits...")
        
        # Check sizes
        total = len(train) + len(val) + len(test)
        train_pct = len(train) / total
        val_pct = len(val) / total
        test_pct = len(test) / total
        
        logger.info(f"Split sizes: Train={len(train)} ({train_pct:.1%}), "
                   f"Val={len(val)} ({val_pct:.1%}), Test={len(test)} ({test_pct:.1%})")
        
        # Check domain distribution
        for split_name, split_data in [("Train", train), ("Val", val), ("Test", test)]:
            domains = defaultdict(int)
            for pair in split_data:
                domains[pair.get('domain', 'Unknown')] += 1
            
            logger.info(f"{split_name} domain distribution:")
            for domain, count in sorted(domains.items()):
                pct = count / len(split_data) if split_data else 0
                logger.info(f"  {domain}: {count} ({pct:.1%})")
            
            # Check minimum samples per domain
            if SPLIT_CONFIG["min_samples_per_domain"] > 0:
                for domain, count in domains.items():
                    if count < SPLIT_CONFIG["min_samples_per_domain"] and split_name == "Train":
                        logger.warning(f"  ⚠️ {domain} has only {count} samples in {split_name} "
                                     f"(minimum: {SPLIT_CONFIG['min_samples_per_domain']})")
        
        # Check for data leakage (no duplicate prompts across splits)
        train_prompts = set(p.get('original_prompt', '') for p in train)
        val_prompts = set(p.get('original_prompt', '') for p in val)
        test_prompts = set(p.get('original_prompt', '') for p in test)
        
        train_val_overlap = train_prompts & val_prompts
        train_test_overlap = train_prompts & test_prompts
        val_test_overlap = val_prompts & test_prompts
        
        if train_val_overlap:
            logger.warning(f"⚠️ Found {len(train_val_overlap)} overlapping prompts between train and val")
        if train_test_overlap:
            logger.warning(f"⚠️ Found {len(train_test_overlap)} overlapping prompts between train and test")
        if val_test_overlap:
            logger.warning(f"⚠️ Found {len(val_test_overlap)} overlapping prompts between val and test")
        
        return not (train_val_overlap or train_test_overlap or val_test_overlap)
    
    def calculate_statistics(self, split_data: List[Dict]) -> Dict[str, Any]:
        """Calculate statistics for a split"""
        stats = {
            "total_samples": len(split_data),
            "domain_distribution": {},
            "quality_distribution": {},
            "source_distribution": {},
            "average_quality_scores": {}
        }
        
        if not split_data:
            return stats
        
        # Domain distribution
        for pair in split_data:
            domain = pair.get('domain', 'Unknown')
            stats["domain_distribution"][domain] = stats["domain_distribution"].get(domain, 0) + 1
        
        # Source distribution
        for pair in split_data:
            source = pair.get('source', 'unknown')
            stats["source_distribution"][source] = stats["source_distribution"].get(source, 0) + 1
        
        # Quality distribution and averages
        score_sums = defaultdict(float)
        quality_counts = {'low': 0, 'medium': 0, 'high': 0}
        
        for pair in split_data:
            quality_scores = pair.get('quality_scores', {})
            overall = quality_scores.get('overall', 0.5)
            
            # Bin quality
            if overall < 0.6:
                quality_counts['low'] += 1
            elif overall < 0.8:
                quality_counts['medium'] += 1
            else:
                quality_counts['high'] += 1
            
            # Sum scores
            for metric, score in quality_scores.items():
                score_sums[metric] += score
        
        stats["quality_distribution"] = quality_counts
        
        # Calculate averages
        for metric, total in score_sums.items():
            stats["average_quality_scores"][metric] = round(total / len(split_data), 3)
        
        return stats
    
    def save_splits(self):
        """Save train, validation, and test splits"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        splits = [
            DataSplit("train", self.train_data, self.calculate_statistics(self.train_data)),
            DataSplit("val", self.val_data, self.calculate_statistics(self.val_data)),
            DataSplit("test", self.test_data, self.calculate_statistics(self.test_data))
        ]
        
        for split in splits:
            # Save data
            output_file = self.output_dir / f"{split.name}_{timestamp}.json"
            with open(output_file, 'w') as f:
                json.dump(split.data, f, indent=2)
            logger.info(f"Saved {len(split.data)} samples to {output_file}")
            
            # Save latest link
            latest_link = self.output_dir / f"{split.name}_latest.json"
            if latest_link.exists():
                latest_link.unlink()
            latest_link.symlink_to(output_file.name)
        
        # Save combined statistics
        all_stats = {
            "timestamp": timestamp,
            "configuration": SPLIT_CONFIG,
            "splits": {
                split.name: split.statistics for split in splits
            }
        }
        
        stats_file = self.output_dir / f"split_statistics_{timestamp}.json"
        with open(stats_file, 'w') as f:
            json.dump(all_stats, f, indent=2)
        logger.info(f"Saved statistics to {stats_file}")
    
    def run(self):
        """Main execution method"""
        logger.info("="*80)
        logger.info("DATA SPLITTING PIPELINE")
        logger.info("="*80)
        
        # Load all pairs
        self.load_all_pairs()
        
        if not self.all_pairs:
            logger.error("No training pairs found. Run generate_seed_pairs.py and synthesize_pairs.py first.")
            return False
        
        # Perform split
        logger.info(f"\nSplitting {len(self.all_pairs)} pairs...")
        self.train_data, self.val_data, self.test_data = self.split_stratified(self.all_pairs)
        
        # Validate splits
        is_valid = self.validate_splits(self.train_data, self.val_data, self.test_data)
        
        if not is_valid:
            logger.warning("⚠️ Validation detected potential issues (see warnings above)")
        
        # Save splits
        self.save_splits()
        
        logger.info("\n" + "="*80)
        logger.info("✅ DATA SPLITTING COMPLETE")
        logger.info("="*80)
        
        return True

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Split training data into train/val/test sets")
    parser.add_argument("--train-ratio", type=float, default=0.70,
                       help="Training set ratio")
    parser.add_argument("--val-ratio", type=float, default=0.15,
                       help="Validation set ratio")
    parser.add_argument("--test-ratio", type=float, default=0.15,
                       help="Test set ratio")
    parser.add_argument("--seed", type=int, default=42,
                       help="Random seed for reproducibility")
    parser.add_argument("--no-stratify", action="store_true",
                       help="Disable stratification")
    
    args = parser.parse_args()
    
    # Update config
    SPLIT_CONFIG["train_ratio"] = args.train_ratio
    SPLIT_CONFIG["val_ratio"] = args.val_ratio
    SPLIT_CONFIG["test_ratio"] = args.test_ratio
    SPLIT_CONFIG["random_seed"] = args.seed
    
    if args.no_stratify:
        SPLIT_CONFIG["stratify_by_domain"] = False
        SPLIT_CONFIG["stratify_by_quality"] = False
    
    # Validate ratios
    total_ratio = args.train_ratio + args.val_ratio + args.test_ratio
    if abs(total_ratio - 1.0) > 0.001:
        logger.error(f"Split ratios must sum to 1.0 (current sum: {total_ratio})")
        return
    
    # Run splitter
    splitter = DataSplitter()
    success = splitter.run()
    
    if success:
        print("\n" + "="*80)
        print("SPLIT SUMMARY")
        print("="*80)
        print(f"Training:   {len(splitter.train_data)} samples ({SPLIT_CONFIG['train_ratio']:.0%})")
        print(f"Validation: {len(splitter.val_data)} samples ({SPLIT_CONFIG['val_ratio']:.0%})")
        print(f"Test:       {len(splitter.test_data)} samples ({SPLIT_CONFIG['test_ratio']:.0%})")
        print("="*80)

if __name__ == "__main__":
    main()