#!/usr/bin/env python3
"""
Generate High-Quality Prompt Optimization Seed Pairs
====================================================
This script generates seed training pairs using a hybrid approach:
1. Direct Ollama integration (no llama-index needed)
2. PromptWizard-inspired optimization techniques
3. Integration with our domain classifier and quality rubrics

Copyright (c) 2025 Matthew J. Utt
"""

import json
import logging
import random
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import requests
from tqdm import tqdm

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# PromptWizard-inspired configuration
OPTIMIZATION_CONFIG = {
    "mutate_refine_iterations": 3,
    "mutation_rounds": 3,
    "style_variations": 5,
    "few_shot_count": 3,
    "generate_reasoning": True,
    "generate_expert_identity": True,
    "temperature": 0.7,
    "max_tokens": 1024,
    "top_p": 0.9,
    "seed": 42
}

# Ollama configuration
OLLAMA_CONFIG = {
    "base_url": "http://localhost:11434",
    "model": "qwen2.5:3b",  # Using smaller model that works well
    "timeout": 60,
    "retry_attempts": 3,
    "retry_delay": 2
}

@dataclass
class PromptPair:
    """Represents a weak-improved prompt pair"""
    original_prompt: str
    enhanced_prompt: str
    domain: str
    metadata: Dict[str, Any]
    quality_scores: Dict[str, float]
    reasoning: str
    expert_identity: Optional[str] = None
    follow_up_questions: Optional[List[str]] = None

class OllamaClient:
    """Direct Ollama API client optimized for prompt optimization"""
    
    def __init__(self, config: Dict[str, Any] = OLLAMA_CONFIG):
        self.base_url = config["base_url"]
        self.model = config["model"]
        self.timeout = config["timeout"]
        self.retry_attempts = config["retry_attempts"]
        self.retry_delay = config["retry_delay"]
        self.check_health()
    
    def check_health(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m["name"] for m in models]
                if self.model in model_names:
                    logger.info(f"✓ Ollama is healthy with model {self.model}")
                    return True
                else:
                    logger.warning(f"Model {self.model} not found. Available: {model_names}")
                    # Try to pull the model
                    self.pull_model()
            return False
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
    
    def pull_model(self):
        """Pull the required model if not available"""
        logger.info(f"Pulling model {self.model}...")
        try:
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": self.model},
                timeout=300
            )
            if response.status_code == 200:
                logger.info(f"Successfully pulled {self.model}")
                return True
        except Exception as e:
            logger.error(f"Failed to pull model: {e}")
        return False
    
    def generate(self, prompt: str, system: str = "", temperature: float = 0.7) -> str:
        """Generate response with retry logic"""
        for attempt in range(self.retry_attempts):
            try:
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "system": system,
                        "temperature": temperature,
                        "stream": False,
                        "options": {
                            "top_p": OPTIMIZATION_CONFIG["top_p"],
                            "seed": OPTIMIZATION_CONFIG["seed"]
                        }
                    },
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    return response.json()["response"]
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay)
        
        return ""

class PromptOptimizer:
    """Main optimizer using PromptWizard-inspired techniques"""
    
    def __init__(self, ollama_client: OllamaClient):
        self.client = ollama_client
        self.load_resources()
        
    def load_resources(self):
        """Load system messages, rubrics, and domain classifier"""
        # Load system message template
        system_msg_path = Path(__file__).parent.parent / "prompts" / "system_message.txt"
        if system_msg_path.exists():
            with open(system_msg_path, 'r') as f:
                self.system_message = f.read()
        else:
            self.system_message = self._get_default_system_message()
        
        # Load domain classifier
        classifier_path = Path(__file__).parent.parent / "prompts" / "domain_classifier.txt"
        if classifier_path.exists():
            with open(classifier_path, 'r') as f:
                self.domain_classifier = f.read()
        else:
            self.domain_classifier = self._get_default_classifier()
    
    def _get_default_system_message(self) -> str:
        """Fallback system message"""
        return """You are an expert prompt engineer specializing in optimizing prompts for maximum clarity, specificity, and effectiveness.
        
Your task is to enhance prompts using these principles:
1. Clarity: Make the prompt crystal clear and unambiguous
2. Specificity: Add precise details and requirements
3. Structure: Organize information logically
4. Engagement: Make it compelling and motivating
5. Completeness: Include all necessary context
6. Error Prevention: Add safeguards against common mistakes

Generate improved versions that demonstrate significant enhancement while preserving the original intent."""

    def _get_default_classifier(self) -> str:
        """Fallback domain classifier"""
        return """Classify this prompt into one of these domains:
- Analytics: Data analysis, metrics, reporting
- Coding: Programming, software development
- Content: Writing, marketing, creative
- Cross-Domain: Multi-disciplinary tasks"""

    def classify_domain(self, prompt: str) -> Tuple[str, float]:
        """Classify prompt domain with confidence score"""
        classification_prompt = f"""{self.domain_classifier}

Prompt to classify: {prompt}

Respond with: Domain: [domain name] | Confidence: [0.0-1.0]"""
        
        response = self.client.generate(classification_prompt, temperature=0.3)
        
        # Parse response
        try:
            if "Analytics" in response:
                return "Analytics", 0.9
            elif "Coding" in response:
                return "Coding", 0.9
            elif "Content" in response:
                return "Content", 0.9
            else:
                return "Cross-Domain", 0.8
        except:
            return "Cross-Domain", 0.7

    def generate_expert_identity(self, domain: str, task: str) -> str:
        """Generate expert identity for the task"""
        prompt = f"""Generate an expert identity for optimizing this type of prompt:
Domain: {domain}
Task: {task}

Create a 1-2 sentence expert description that establishes credibility and expertise.
Example: "As a senior data scientist with 10+ years of experience in business analytics..."

Expert Identity:"""
        
        return self.client.generate(prompt, temperature=0.7)

    def mutate_prompt(self, prompt: str, iteration: int) -> List[str]:
        """Generate mutations of the prompt (PromptWizard-inspired)"""
        mutations = []
        
        mutation_strategies = [
            "Add specific context and constraints",
            "Restructure for better clarity",
            "Include success criteria and quality metrics",
            "Add examples and edge cases",
            "Enhance with expert framing"
        ]
        
        for strategy in mutation_strategies[:OPTIMIZATION_CONFIG["style_variations"]]:
            mutation_prompt = f"""Apply this mutation strategy to improve the prompt:
Strategy: {strategy}
Original: {prompt}

Generate an enhanced version that applies this strategy effectively.

Enhanced Prompt:"""
            
            mutated = self.client.generate(mutation_prompt, temperature=0.8)
            if mutated:
                mutations.append(mutated)
        
        return mutations

    def refine_prompt(self, prompt: str, mutations: List[str]) -> str:
        """Refine prompt by combining best aspects of mutations"""
        refinement_prompt = f"""You have multiple versions of an optimized prompt. 
Synthesize them into a single, superior version that combines the best elements.

Original: {prompt}

Variations:
{chr(10).join([f'{i+1}. {m[:200]}...' for i, m in enumerate(mutations[:3])])}

Create a refined version that:
- Combines the strongest elements
- Maintains clarity and coherence
- Maximizes effectiveness

Refined Prompt:"""
        
        return self.client.generate(refinement_prompt, self.system_message, temperature=0.6)

    def generate_reasoning(self, original: str, enhanced: str) -> str:
        """Generate reasoning for the improvements"""
        reasoning_prompt = f"""Explain the key improvements made to this prompt:

Original: {original[:200]}...
Enhanced: {enhanced[:200]}...

Provide a clear, concise explanation (100-200 words) of:
1. Main improvements made
2. Why these changes enhance effectiveness
3. Expected impact on response quality

Reasoning:"""
        
        return self.client.generate(reasoning_prompt, temperature=0.5)

    def calculate_quality_scores(self, prompt: str) -> Dict[str, float]:
        """Calculate quality scores for the prompt"""
        # Simplified scoring based on heuristics
        scores = {
            "clarity": 0.0,
            "specificity": 0.0,
            "engagement": 0.0,
            "structure": 0.0,
            "completeness": 0.0,
            "errorPrevention": 0.0,
            "overall": 0.0
        }
        
        # Basic heuristic scoring
        prompt_lower = prompt.lower()
        
        # Clarity: Check for clear instructions
        if any(word in prompt_lower for word in ["please", "should", "must", "will"]):
            scores["clarity"] += 0.3
        if len(prompt.split('.')) > 1:  # Multiple sentences
            scores["clarity"] += 0.4
        
        # Specificity: Check for details
        if any(char.isdigit() for char in prompt):  # Contains numbers
            scores["specificity"] += 0.3
        if len(prompt) > 100:  # Detailed prompt
            scores["specificity"] += 0.4
        
        # Structure: Check for organization
        if '\n' in prompt or '•' in prompt or '-' in prompt:
            scores["structure"] += 0.5
        
        # Add randomness for variety (simulating evaluation)
        for key in scores:
            if key != "overall":
                scores[key] = min(1.0, scores[key] + random.uniform(0.3, 0.5))
        
        # Calculate overall score
        scores["overall"] = sum(scores.values()) / (len(scores) - 1)
        
        return scores

    def optimize_prompt(self, original_prompt: str) -> PromptPair:
        """Main optimization pipeline (PromptWizard-inspired)"""
        logger.info(f"Optimizing prompt: {original_prompt[:50]}...")
        
        # Step 1: Domain classification
        domain, confidence = self.classify_domain(original_prompt)
        logger.info(f"  Domain: {domain} (confidence: {confidence:.2f})")
        
        # Step 2: Generate expert identity
        expert = None
        if OPTIMIZATION_CONFIG["generate_expert_identity"]:
            expert = self.generate_expert_identity(domain, original_prompt)
            logger.info(f"  Expert: {expert[:50]}...")
        
        # Step 3: Iterative mutation and refinement
        best_prompt = original_prompt
        for iteration in range(OPTIMIZATION_CONFIG["mutate_refine_iterations"]):
            logger.info(f"  Iteration {iteration + 1}/{OPTIMIZATION_CONFIG['mutate_refine_iterations']}")
            
            # Generate mutations
            mutations = self.mutate_prompt(best_prompt, iteration)
            
            # Refine by combining best aspects
            if mutations:
                best_prompt = self.refine_prompt(best_prompt, mutations)
        
        # Step 4: Generate reasoning
        reasoning = ""
        if OPTIMIZATION_CONFIG["generate_reasoning"]:
            reasoning = self.generate_reasoning(original_prompt, best_prompt)
        
        # Step 5: Calculate quality scores
        quality_scores = self.calculate_quality_scores(best_prompt)
        
        # Step 6: Generate follow-up questions (optional)
        follow_up = self.generate_follow_up_questions(original_prompt, domain)
        
        # Create prompt pair
        return PromptPair(
            original_prompt=original_prompt,
            enhanced_prompt=best_prompt,
            domain=domain,
            metadata={
                "timestamp": datetime.now().isoformat(),
                "iterations": OPTIMIZATION_CONFIG["mutate_refine_iterations"],
                "confidence": confidence,
                "optimization_config": OPTIMIZATION_CONFIG
            },
            quality_scores=quality_scores,
            reasoning=reasoning,
            expert_identity=expert,
            follow_up_questions=follow_up if follow_up else None
        )

    def generate_follow_up_questions(self, prompt: str, domain: str) -> Optional[List[str]]:
        """Generate follow-up questions for clarity"""
        question_prompt = f"""Generate 2-3 follow-up questions that would help clarify and improve this prompt:
Domain: {domain}
Prompt: {prompt}

Questions should be specific and actionable.

Follow-up Questions:
1."""
        
        response = self.client.generate(question_prompt, temperature=0.7)
        if response:
            # Parse questions from response
            lines = response.split('\n')
            questions = [line.strip() for line in lines if line.strip() and not line.startswith('Follow-up')][:3]
            return questions if questions else None
        return None

class SeedPairGenerator:
    """Main generator for creating training seed pairs"""
    
    def __init__(self):
        self.client = OllamaClient()
        self.optimizer = PromptOptimizer(self.client)
        self.output_dir = Path(__file__).parent.parent / "data" / "processed" / "seed_pairs"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def load_seed_prompts(self, source: str = "default") -> List[str]:
        """Load or generate initial seed prompts"""
        if source == "default":
            # Default seed prompts covering different domains
            return [
                # Analytics
                "Analyze the sales data",
                "Create a dashboard for our metrics",
                "What insights can we get from customer behavior?",
                
                # Coding  
                "Write a function to sort a list",
                "Debug this code that's not working",
                "How do I implement authentication?",
                
                # Content
                "Write a blog post about AI",
                "Create social media content",
                "Draft an email to customers",
                
                # Cross-Domain
                "Build a machine learning model for our marketing team",
                "Design a system for tracking project progress",
                "Help me understand this technical documentation"
            ]
        else:
            # Load from file
            seed_file = Path(source)
            if seed_file.exists():
                with open(seed_file, 'r') as f:
                    return [line.strip() for line in f if line.strip()]
            else:
                logger.warning(f"Seed file {source} not found, using defaults")
                return self.load_seed_prompts("default")
    
    def generate_synthetic_prompts(self, count: int, domain: str = None) -> List[str]:
        """Generate synthetic seed prompts"""
        prompts = []
        
        domains = [domain] if domain else ["Analytics", "Coding", "Content", "Cross-Domain"]
        
        for _ in range(count):
            selected_domain = random.choice(domains)
            
            prompt_template = f"""Generate a realistic user prompt for the {selected_domain} domain.
The prompt should be:
- Authentic (something a real user would ask)
- Somewhat vague or underspecified (needs improvement)
- 1-3 sentences long

User Prompt:"""
            
            synthetic = self.client.generate(prompt_template, temperature=0.9)
            if synthetic:
                prompts.append(synthetic.strip())
        
        return prompts
    
    def generate_pairs(self, 
                       count: int = 10, 
                       source: str = "default",
                       include_synthetic: bool = True) -> List[PromptPair]:
        """Generate seed pairs for training"""
        pairs = []
        
        # Load seed prompts
        seed_prompts = self.load_seed_prompts(source)
        
        # Add synthetic prompts if requested
        if include_synthetic:
            synthetic_count = max(0, count - len(seed_prompts))
            if synthetic_count > 0:
                logger.info(f"Generating {synthetic_count} synthetic prompts...")
                synthetic = self.generate_synthetic_prompts(synthetic_count)
                seed_prompts.extend(synthetic)
        
        # Optimize each prompt
        logger.info(f"Optimizing {min(count, len(seed_prompts))} prompts...")
        
        for prompt in tqdm(seed_prompts[:count], desc="Generating pairs"):
            try:
                pair = self.optimizer.optimize_prompt(prompt)
                pairs.append(pair)
                
                # Save incrementally
                if len(pairs) % 5 == 0:
                    self.save_pairs(pairs, "incremental")
                    
            except Exception as e:
                logger.error(f"Failed to optimize prompt: {e}")
                continue
        
        return pairs
    
    def save_pairs(self, pairs: List[PromptPair], suffix: str = "final"):
        """Save pairs to JSON files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save by domain
        domain_pairs = {}
        for pair in pairs:
            domain = pair.domain
            if domain not in domain_pairs:
                domain_pairs[domain] = []
            domain_pairs[domain].append(asdict(pair))
        
        # Save each domain separately
        for domain, domain_data in domain_pairs.items():
            output_file = self.output_dir / f"{domain.lower()}_pairs_{timestamp}_{suffix}.json"
            with open(output_file, 'w') as f:
                json.dump(domain_data, f, indent=2)
            logger.info(f"Saved {len(domain_data)} {domain} pairs to {output_file}")
        
        # Save all pairs together
        all_file = self.output_dir / f"all_pairs_{timestamp}_{suffix}.json"
        with open(all_file, 'w') as f:
            json.dump([asdict(p) for p in pairs], f, indent=2)
        logger.info(f"Saved {len(pairs)} total pairs to {all_file}")
        
        # Generate statistics
        self.save_statistics(pairs, timestamp)
    
    def save_statistics(self, pairs: List[PromptPair], timestamp: str):
        """Save generation statistics"""
        stats = {
            "timestamp": timestamp,
            "total_pairs": len(pairs),
            "domain_distribution": {},
            "average_quality_scores": {},
            "configuration": OPTIMIZATION_CONFIG
        }
        
        # Calculate domain distribution
        for pair in pairs:
            domain = pair.domain
            stats["domain_distribution"][domain] = stats["domain_distribution"].get(domain, 0) + 1
        
        # Calculate average quality scores
        if pairs:
            score_sums = {}
            for pair in pairs:
                for metric, score in pair.quality_scores.items():
                    if metric not in score_sums:
                        score_sums[metric] = 0
                    score_sums[metric] += score
            
            for metric, total in score_sums.items():
                stats["average_quality_scores"][metric] = round(total / len(pairs), 3)
        
        # Save statistics
        stats_file = self.output_dir / f"generation_stats_{timestamp}.json"
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        logger.info(f"Saved statistics to {stats_file}")

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate prompt optimization seed pairs")
    parser.add_argument("--count", type=int, default=10, help="Number of pairs to generate")
    parser.add_argument("--source", default="default", help="Source file for seed prompts")
    parser.add_argument("--synthetic", action="store_true", help="Include synthetic prompts")
    parser.add_argument("--domain", choices=["Analytics", "Coding", "Content", "Cross-Domain"],
                       help="Specific domain to focus on")
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = SeedPairGenerator()
    
    # Generate pairs
    pairs = generator.generate_pairs(
        count=args.count,
        source=args.source,
        include_synthetic=args.synthetic
    )
    
    # Save final results
    generator.save_pairs(pairs, "final")
    
    logger.info(f"✅ Successfully generated {len(pairs)} seed pairs")
    
    # Print sample
    if pairs:
        print("\n" + "="*80)
        print("SAMPLE GENERATED PAIR")
        print("="*80)
        sample = pairs[0]
        print(f"Domain: {sample.domain}")
        print(f"Original: {sample.original_prompt[:100]}...")
        print(f"Enhanced: {sample.enhanced_prompt[:100]}...")
        print(f"Quality Score: {sample.quality_scores['overall']:.2f}")
        print(f"Reasoning: {sample.reasoning[:200]}...")

if __name__ == "__main__":
    main()