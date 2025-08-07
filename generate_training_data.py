#!/usr/bin/env python3
"""
Generate Training Data for Prompt Enhancement Model
Based on PRD requirements and Evol-Instruct methodology
"""

import json
import random
import os
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum

class Domain(Enum):
    ANALYTICS = "analytics"
    CODING = "coding"
    CONTENT = "content"
    CROSS_DOMAIN = "cross_domain"

@dataclass
class PromptPair:
    """Represents a vague -> enhanced prompt transformation"""
    domain: Domain
    vague_prompt: str
    enhanced_prompt: str
    schema_version: str = "1.2"

class PromptEnhancementGenerator:
    """Generate training data for prompt enhancement using Evol-Instruct methodology"""
    
    # Domain distribution as per PRD
    DOMAIN_WEIGHTS = {
        Domain.ANALYTICS: 0.30,
        Domain.CODING: 0.30,
        Domain.CONTENT: 0.25,
        Domain.CROSS_DOMAIN: 0.15
    }
    
    def __init__(self):
        self.seed_prompts = self._load_seed_prompts()
        self.evolution_strategies = [
            self._add_constraints,
            self._add_context,
            self._add_output_format,
            self._add_evaluation_criteria,
            self._deepen_reasoning,
            self._concretize,
            self._increase_complexity
        ]
    
    def _load_seed_prompts(self) -> Dict[Domain, List[str]]:
        """Load seed prompts for each domain"""
        return {
            Domain.ANALYTICS: [
                "Analyze the data",
                "Show me trends",
                "What are the insights",
                "Calculate metrics",
                "Make a report"
            ],
            Domain.CODING: [
                "Make this faster",
                "Fix the bug",
                "Write a function",
                "Optimize this code",
                "Add error handling"
            ],
            Domain.CONTENT: [
                "Write about AI",
                "Create a blog post",
                "Explain this concept",
                "Draft an email",
                "Write documentation"
            ],
            Domain.CROSS_DOMAIN: [
                "Help me plan",
                "Create a strategy",
                "Build a system",
                "Design a solution",
                "Improve the process"
            ]
        }
    
    def _add_constraints(self, prompt: str, domain: Domain) -> str:
        """Add constraints to the prompt"""
        constraints = {
            Domain.ANALYTICS: "within 95% confidence interval, handle missing values, limit to last 12 months",
            Domain.CODING: "O(n log n) complexity, Python 3.10+, memory efficient, type-safe",
            Domain.CONTENT: "1500-2000 words, SEO optimized, include 3 examples, APA citations",
            Domain.CROSS_DOMAIN: "budget under $50k, 90-day timeline, 5-person team, measurable KPIs"
        }
        return f"{prompt} with constraints: {constraints.get(domain, 'standard constraints')}"
    
    def _add_context(self, prompt: str, domain: Domain) -> str:
        """Add relevant context"""
        contexts = {
            Domain.ANALYTICS: "using sales_data.csv with columns [date, product_id, revenue, region], 50k rows",
            Domain.CODING: "for a REST API handling 1000 req/s, Node.js environment, PostgreSQL database",
            Domain.CONTENT: "for technical audience, B2B SaaS product, thought leadership piece",
            Domain.CROSS_DOMAIN: "for enterprise client, digital transformation initiative, Fortune 500 company"
        }
        return f"{prompt}. Context: {contexts.get(domain, 'general business context')}"
    
    def _add_output_format(self, prompt: str, domain: Domain) -> str:
        """Add specific output format requirements"""
        formats = {
            Domain.ANALYTICS: 'JSON format: {"summary": str, "metrics": dict, "visualizations": list}',
            Domain.CODING: "unified diff format with inline comments explaining changes",
            Domain.CONTENT: "markdown with headers, bullet points, code blocks where relevant",
            Domain.CROSS_DOMAIN: "structured plan with phases, milestones, deliverables, risk matrix"
        }
        return f"{prompt}. Output format: {formats.get(domain, 'structured format')}"
    
    def _add_evaluation_criteria(self, prompt: str, domain: Domain) -> str:
        """Add evaluation criteria"""
        criteria = {
            Domain.ANALYTICS: "statistical accuracy, actionable insights, visual clarity, data quality handling",
            Domain.CODING: "performance improvement ≥20%, all tests pass, code readability maintained",
            Domain.CONTENT: "engagement score >7/10, readability grade 8-10, factual accuracy, originality",
            Domain.CROSS_DOMAIN: "feasibility, ROI projection, risk mitigation, stakeholder alignment"
        }
        return f"{prompt}. Evaluation criteria: {criteria.get(domain, 'quality and effectiveness')}"
    
    def _deepen_reasoning(self, prompt: str, domain: Domain) -> str:
        """Add reasoning requirements"""
        return f"{prompt}. Provide step-by-step reasoning, explain assumptions, justify decisions"
    
    def _concretize(self, prompt: str, domain: Domain) -> str:
        """Make abstract concepts concrete"""
        examples = {
            Domain.ANALYTICS: "specifically for Q3 2024 sales performance vs Q2 2024",
            Domain.CODING: "for the UserAuthentication class in auth.py line 145-200",
            Domain.CONTENT: "focusing on GPT-4 vs Claude 3 capabilities comparison",
            Domain.CROSS_DOMAIN: "for launching AI-powered CRM product in North American market"
        }
        return f"{prompt}, {examples.get(domain, 'with specific examples')}"
    
    def _increase_complexity(self, prompt: str, domain: Domain) -> str:
        """Add multiple requirements"""
        additions = {
            Domain.ANALYTICS: "include correlation analysis, predictive modeling, and anomaly detection",
            Domain.CODING: "with unit tests, documentation, backwards compatibility",
            Domain.CONTENT: "addressing beginners, intermediates, and experts differently",
            Domain.CROSS_DOMAIN: "considering technical, financial, and organizational aspects"
        }
        return f"{prompt}, {additions.get(domain, 'covering all aspects')}"
    
    def generate_enhanced_prompt(self, vague_prompt: str, domain: Domain) -> str:
        """Generate a fully enhanced prompt with schema tags"""
        
        # Apply evolution strategies
        evolved = vague_prompt
        strategies = random.sample(self.evolution_strategies, k=random.randint(3, 5))
        for strategy in strategies:
            evolved = strategy(evolved, domain)
        
        # Format with schema tags
        template = f"""<SCHEMA_VERSION>1.2</SCHEMA_VERSION>
<DOMAIN>{domain.value}</DOMAIN>
<OBJECTIVE>{evolved}</OBJECTIVE>
<CONTEXT>{self._get_domain_context(domain)}</CONTEXT>
<REQUIREMENTS>{self._get_domain_requirements(domain)}</REQUIREMENTS>
<CONSTRAINTS>{self._get_domain_constraints(domain)}</CONSTRAINTS>
<OUTPUT_FORMAT>{self._get_output_format(domain)}</OUTPUT_FORMAT>
<EVALUATION_CRITERIA>{self._get_evaluation_criteria(domain)}</EVALUATION_CRITERIA>"""
        
        return template
    
    def _get_domain_context(self, domain: Domain) -> str:
        contexts = {
            Domain.ANALYTICS: "Working with enterprise data warehouse, multiple data sources, business stakeholders need actionable insights",
            Domain.CODING: "Production codebase, microservices architecture, CI/CD pipeline, high-traffic application",
            Domain.CONTENT: "Brand voice guidelines, target audience demographics, content marketing strategy",
            Domain.CROSS_DOMAIN: "Multiple departments involved, competing priorities, resource constraints"
        }
        return contexts.get(domain, "Standard business context")
    
    def _get_domain_requirements(self, domain: Domain) -> str:
        requirements = {
            Domain.ANALYTICS: "1) Descriptive statistics 2) Trend analysis 3) Predictive insights 4) Actionable recommendations",
            Domain.CODING: "1) Performance benchmarks 2) Unit tests 3) Documentation 4) Code review checklist",
            Domain.CONTENT: "1) Engaging introduction 2) Clear structure 3) Supporting evidence 4) Call-to-action",
            Domain.CROSS_DOMAIN: "1) Stakeholder mapping 2) Timeline 3) Resource allocation 4) Success metrics"
        }
        return requirements.get(domain, "Standard requirements")
    
    def _get_domain_constraints(self, domain: Domain) -> str:
        constraints = {
            Domain.ANALYTICS: "Max 500ms query time, GDPR compliant, handle NULL values, confidence intervals",
            Domain.CODING: "Backwards compatible, <100ms response time, <50MB memory, security best practices",
            Domain.CONTENT: "SEO friendly, brand compliant, fact-checked, accessibility standards",
            Domain.CROSS_DOMAIN: "Budget limits, regulatory compliance, timeline constraints, resource availability"
        }
        return constraints.get(domain, "Standard constraints")
    
    def _get_output_format(self, domain: Domain) -> str:
        formats = {
            Domain.ANALYTICS: '{"summary": {"key_findings": [], "metrics": {}}, "visualizations": [], "recommendations": []}',
            Domain.CODING: "```diff\\n+ additions\\n- deletions\\n```\\nWith inline comments",
            Domain.CONTENT: "# Title\\n## Introduction\\n## Main Points\\n### Subpoints\\n## Conclusion",
            Domain.CROSS_DOMAIN: '{"phases": [], "milestones": [], "deliverables": [], "risks": []}'
        }
        return formats.get(domain, "Structured format")
    
    def _get_evaluation_criteria(self, domain: Domain) -> str:
        criteria = {
            Domain.ANALYTICS: "Statistical accuracy, business relevance, actionability, clarity of insights",
            Domain.CODING: "Performance improvement, test coverage, code quality, documentation completeness",
            Domain.CONTENT: "Engagement metrics, readability score, accuracy, brand alignment",
            Domain.CROSS_DOMAIN: "Feasibility, completeness, risk assessment, stakeholder value"
        }
        return criteria.get(domain, "Quality and completeness")
    
    def generate_dataset(self, num_examples: int = 1000) -> List[PromptPair]:
        """Generate a complete dataset with proper domain distribution"""
        dataset = []
        
        for domain, weight in self.DOMAIN_WEIGHTS.items():
            domain_count = int(num_examples * weight)
            domain_prompts = self.seed_prompts[domain]
            
            for _ in range(domain_count):
                vague = random.choice(domain_prompts)
                # Add some variation to vague prompts
                if random.random() > 0.5:
                    vague = f"{vague} {random.choice(['quickly', 'for me', 'please', 'now', 'ASAP'])}"
                
                enhanced = self.generate_enhanced_prompt(vague, domain)
                dataset.append(PromptPair(
                    domain=domain,
                    vague_prompt=vague,
                    enhanced_prompt=enhanced
                ))
        
        # Add negative examples (20% as per PRD)
        num_negative = int(num_examples * 0.2)
        for _ in range(num_negative):
            domain = random.choice(list(Domain))
            vague = random.choice(self.seed_prompts[domain])
            # Create intentionally bad enhanced prompts (missing tags, over-constrained, etc.)
            enhanced = f"Just {vague} with no proper structure or requirements"
            dataset.append(PromptPair(
                domain=domain,
                vague_prompt=vague,
                enhanced_prompt=enhanced  # Intentionally bad for robustness training
            ))
        
        random.shuffle(dataset)
        return dataset
    
    def save_dataset(self, dataset: List[PromptPair], output_path: str):
        """Save dataset in JSONL format for training"""
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        with open(output_path, 'w') as f:
            for pair in dataset:
                record = {
                    "instruction": "Transform this vague user prompt into a well-structured, detailed prompt for an LLM",
                    "input": pair.vague_prompt,
                    "output": pair.enhanced_prompt,
                    "domain": pair.domain.value,
                    "schema_version": pair.schema_version
                }
                f.write(json.dumps(record) + '\n')
        
        print(f"✅ Saved {len(dataset)} examples to {output_path}")
        
        # Print statistics
        domain_counts = {}
        for pair in dataset:
            domain_counts[pair.domain.value] = domain_counts.get(pair.domain.value, 0) + 1
        
        print("\n📊 Dataset Statistics:")
        for domain, count in domain_counts.items():
            percentage = (count / len(dataset)) * 100
            print(f"  - {domain}: {count} examples ({percentage:.1f}%)")

def main():
    """Generate training datasets"""
    print("🧙 PromptWizard Training Data Generator")
    print("="*50)
    
    generator = PromptEnhancementGenerator()
    
    # Generate datasets
    print("\n📚 Generating Stage 1 Training Data (Foundational)...")
    stage1_data = generator.generate_dataset(num_examples=500)  # Smaller for demo
    generator.save_dataset(stage1_data, "data/stage1_foundational.jsonl")
    
    print("\n📚 Generating Stage 2 Training Data (Specialization)...")
    stage2_data = generator.generate_dataset(num_examples=200)  # Focused dataset
    generator.save_dataset(stage2_data, "data/stage2_specialization.jsonl")
    
    print("\n📚 Generating Validation Data...")
    val_data = generator.generate_dataset(num_examples=100)
    generator.save_dataset(val_data, "data/validation.jsonl")
    
    # Create a sample for review
    print("\n📝 Sample Enhanced Prompts:")
    for i, pair in enumerate(stage2_data[:3]):
        print(f"\n--- Example {i+1} ({pair.domain.value}) ---")
        print(f"VAGUE: {pair.vague_prompt}")
        print(f"ENHANCED: {pair.enhanced_prompt[:500]}...")

if __name__ == "__main__":
    main()