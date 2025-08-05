"""
Test data generator for creating realistic test scenarios
Generates sample prompts, configurations, and expected responses
"""

import json
import random
import time
from pathlib import Path
from typing import Dict, List, Any, Optional


class TestDataGenerator:
    """Generate realistic test data for CLI testing"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path("tests/fixtures/generated")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_sample_prompts(self, count: int = 50) -> List[str]:
        """Generate sample prompts of varying complexity"""
        templates = [
            "Write a {type} about {topic}",
            "Explain {concept} to a {audience}",
            "Create a {document} for {purpose}",
            "Debug this {language} {issue}",
            "Optimize {system} for {metric}",
            "Design a {solution} that {requirement}",
            "Analyze {data} and provide {output}",
            "Generate {content} for {platform}",
            "Translate {text} to {language}",
            "Summarize {source} in {format}"
        ]
        
        variables = {
            "type": ["story", "poem", "article", "report", "guide", "tutorial"],
            "topic": ["technology", "nature", "business", "education", "health", "travel"],
            "concept": ["machine learning", "blockchain", "quantum computing", "artificial intelligence", "data science"],
            "audience": ["beginner", "expert", "child", "professional", "student"],
            "document": ["plan", "strategy", "proposal", "specification", "manual"],
            "purpose": ["marketing", "training", "compliance", "optimization", "analysis"],
            "language": ["Python", "JavaScript", "Java", "C++", "SQL"],
            "issue": ["memory leak", "performance problem", "syntax error", "logic bug"],
            "system": ["database", "API", "website", "application", "algorithm"],
            "metric": ["performance", "security", "usability", "scalability", "reliability"],
            "solution": ["architecture", "framework", "system", "process", "workflow"],
            "requirement": ["scales well", "is secure", "is user-friendly", "is maintainable"],
            "data": ["sales data", "user feedback", "performance metrics", "market research"],
            "output": ["insights", "recommendations", "visualization", "summary"],
            "content": ["blog post", "social media", "documentation", "presentation"],
            "platform": ["LinkedIn", "Twitter", "website", "mobile app"],
            "text": ["technical document", "legal contract", "user manual", "research paper"],
            "source": ["research paper", "meeting notes", "user feedback", "data report"],
            "format": ["bullet points", "executive summary", "detailed analysis", "key findings"]
        }
        
        prompts = []
        for _ in range(count):
            template = random.choice(templates)
            # Replace placeholders with random values
            prompt = template
            for placeholder, options in variables.items():
                if f"{{{placeholder}}}" in prompt:
                    prompt = prompt.replace(f"{{{placeholder}}}", random.choice(options))
            prompts.append(prompt)
        
        return prompts
    
    def generate_optimization_responses(self, prompts: List[str]) -> List[Dict[str, Any]]:
        """Generate realistic optimization responses for prompts"""
        responses = []
        
        for i, prompt in enumerate(prompts):
            # Generate realistic quality score
            base_score = random.uniform(75, 95)
            quality_score = round(base_score + random.uniform(-5, 10), 1)
            quality_score = max(60, min(100, quality_score))  # Clamp to reasonable range
            
            # Generate improvements based on prompt type
            improvements = self._generate_improvements(prompt)
            
            # Generate expert profile
            expert_profile = self._generate_expert_profile(prompt)
            
            # Generate optimized prompt
            optimized_prompt = self._generate_optimized_prompt(prompt, improvements)
            
            response = {
                "success": True,
                "result": {
                    "best_prompt": optimized_prompt,
                    "quality_score": quality_score,
                    "expert_profile": expert_profile,
                    "improvements": improvements,
                    "metadata": {
                        "processing_time": round(random.uniform(1.5, 8.0), 2),
                        "iterations": random.choice([1, 2, 3]),
                        "original_length": len(prompt),
                        "optimized_length": len(optimized_prompt),
                        "domain": self._detect_domain(prompt)
                    }
                }
            }
            
            # Occasionally generate failures for testing
            if random.random() < 0.05:  # 5% failure rate
                response = {
                    "success": False,
                    "error": random.choice([
                        "Rate limit exceeded - please try again later",
                        "Prompt too complex for current processing capacity",
                        "Service temporarily unavailable",
                        "Invalid prompt format detected"
                    ])
                }
            
            responses.append(response)
        
        return responses
    
    def _generate_improvements(self, prompt: str) -> List[str]:
        """Generate realistic improvement descriptions"""
        improvement_templates = [
            "Enhanced clarity and specificity",
            "Added expert context and authority",
            "Improved task structure and organization",
            "Strengthened guidance and direction",
            "Added relevant examples and context",
            "Enhanced technical precision",
            "Improved user engagement factors",
            "Added step-by-step methodology",
            "Strengthened outcome specifications",
            "Enhanced domain-specific language"
        ]
        
        # Select 2-5 improvements based on prompt complexity
        num_improvements = min(len(improvement_templates), random.randint(2, 5))
        return random.sample(improvement_templates, num_improvements)
    
    def _generate_expert_profile(self, prompt: str) -> str:
        """Generate expert profile based on prompt content"""
        domain = self._detect_domain(prompt)
        
        profiles = {
            "technical": [
                "Senior Software Engineer with expertise in system optimization",
                "Technical Architect specializing in scalable solutions",
                "Data Scientist with machine learning expertise",
                "DevOps Engineer focused on performance optimization"
            ],
            "creative": [
                "Professional Writer and Content Strategist",
                "Creative Director with storytelling expertise",
                "Marketing Specialist in engaging content creation",
                "Communications Expert in audience engagement"
            ],
            "business": [
                "Business Strategy Consultant with industry expertise",
                "Management Professional with operational excellence focus",
                "Business Analyst specializing in process optimization",
                "Executive Leader with strategic planning experience"
            ],
            "academic": [
                "Research Specialist with academic writing expertise",
                "Educational Content Developer and Curriculum Designer",
                "Subject Matter Expert with teaching experience",
                "Academic Researcher with publication experience"
            ],
            "general": [
                "Expert AI Assistant with broad knowledge base",
                "Professional Consultant with multi-domain expertise",
                "Experienced Analyst with problem-solving focus",
                "Knowledgeable Advisor with comprehensive understanding"
            ]
        }
        
        return random.choice(profiles.get(domain, profiles["general"]))
    
    def _generate_optimized_prompt(self, original: str, improvements: List[str]) -> str:
        """Generate an optimized version of the prompt"""
        # Simple optimization: add structure and expert context
        optimization_prefixes = [
            "You are an expert professional in this domain. Please",
            "As a specialist with relevant expertise, please",
            "You are a knowledgeable assistant. Please provide a comprehensive response that",
            "Acting as an expert advisor, please"
        ]
        
        optimization_suffixes = [
            "Ensure your response is clear, well-structured, and actionable.",
            "Provide specific examples and practical guidance where appropriate.",
            "Structure your response logically and include relevant details.",
            "Focus on practical application and clear explanation."
        ]
        
        prefix = random.choice(optimization_prefixes)
        suffix = random.choice(optimization_suffixes)
        
        # Clean up the original prompt
        cleaned_original = original.strip().lower()
        if not cleaned_original.endswith('.'):
            cleaned_original += '.'
        
        return f"{prefix} {cleaned_original} {suffix}"
    
    def _detect_domain(self, prompt: str) -> str:
        """Detect the domain of a prompt"""
        prompt_lower = prompt.lower()
        
        technical_keywords = ["code", "debug", "optimize", "api", "database", "algorithm", "python", "javascript"]
        creative_keywords = ["write", "story", "creative", "content", "blog", "social media"]
        business_keywords = ["business", "strategy", "marketing", "plan", "analysis", "report"]
        academic_keywords = ["research", "study", "academic", "paper", "analysis", "explain"]
        
        if any(keyword in prompt_lower for keyword in technical_keywords):
            return "technical"
        elif any(keyword in prompt_lower for keyword in creative_keywords):
            return "creative"
        elif any(keyword in prompt_lower for keyword in business_keywords):
            return "business"
        elif any(keyword in prompt_lower for keyword in academic_keywords):
            return "academic"
        else:
            return "general"
    
    def generate_test_files(self) -> Dict[str, Path]:
        """Generate comprehensive test data files"""
        generated_files = {}
        
        # Generate sample prompts
        prompts = self.generate_sample_prompts(100)
        
        # Create different file formats
        # Plain text format
        txt_file = self.output_dir / "sample_prompts.txt"
        with open(txt_file, 'w') as f:
            for prompt in prompts[:20]:
                f.write(f"{prompt}\n")
        generated_files["txt"] = txt_file
        
        # JSON format
        json_data = [{"prompt": prompt, "id": i+1} for i, prompt in enumerate(prompts[:15])]
        json_file = self.output_dir / "sample_prompts.json"
        with open(json_file, 'w') as f:
            json.dump(json_data, f, indent=2)
        generated_files["json"] = json_file
        
        # JSONL format
        jsonl_file = self.output_dir / "sample_prompts.jsonl"
        with open(jsonl_file, 'w') as f:
            for i, prompt in enumerate(prompts[:25]):
                f.write(json.dumps({"prompt": prompt, "index": i+1}) + "\n")
        generated_files["jsonl"] = jsonl_file
        
        # Generate expected responses
        responses = self.generate_optimization_responses(prompts[:10])
        responses_file = self.output_dir / "expected_responses.json"
        with open(responses_file, 'w') as f:
            json.dump(responses, f, indent=2)
        generated_files["responses"] = responses_file
        
        # Generate test scenarios
        scenarios = self._generate_test_scenarios()
        scenarios_file = self.output_dir / "test_scenarios.json"
        with open(scenarios_file, 'w') as f:
            json.dump(scenarios, f, indent=2)
        generated_files["scenarios"] = scenarios_file
        
        return generated_files
    
    def _generate_test_scenarios(self) -> Dict[str, Any]:
        """Generate test scenarios for different testing needs"""
        return {
            "edge_cases": {
                "empty_prompt": "",
                "single_char": "a",
                "very_long": "A" * 2000,
                "special_chars": "Test with special chars: !@#$%^&*()_+-={}[]|\\:;\"'<>?,./",
                "unicode": "Test Unicode: 你好 🌍 Здравствуй",
                "multiline": "Line 1\nLine 2\nLine 3"
            },
            "error_scenarios": [
                {
                    "trigger": "rate_limit_test",
                    "expected_error": "Rate limit exceeded",
                    "retry_after": 60
                },
                {
                    "trigger": "service_unavailable",
                    "expected_error": "Service temporarily unavailable",
                    "suggested_action": "Please try again later"
                },
                {
                    "trigger": "invalid_format",
                    "expected_error": "Invalid prompt format",
                    "suggested_action": "Check prompt formatting"
                }
            ],
            "performance_benchmarks": {
                "quick_mode_max_time": 15,
                "advanced_mode_max_time": 45,
                "batch_processing_rate": 10,  # prompts per minute
                "max_memory_usage": 100  # MB
            },
            "quality_thresholds": {
                "min_quality_score": 70.0,
                "expected_improvement_count": 3,
                "min_optimization_ratio": 1.2
            }
        }


def main():
    """Generate test data files"""
    generator = TestDataGenerator()
    
    print("Generating comprehensive test data...")
    generated_files = generator.generate_test_files()
    
    print("\nGenerated files:")
    for file_type, file_path in generated_files.items():
        size = file_path.stat().st_size
        print(f"  {file_type}: {file_path} ({size} bytes)")
    
    print(f"\nAll files saved to: {generator.output_dir}")


if __name__ == "__main__":
    main()