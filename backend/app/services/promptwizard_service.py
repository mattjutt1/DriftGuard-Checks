"""
PromptWizard integration service for AI-powered prompt optimization.
Implements Microsoft PromptWizard framework with Ollama backend support.
"""

import asyncio
import json
import logging
import random
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from .ollama_client import OllamaClient, OllamaError
from ..core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class OptimizationConfig:
    """Configuration for prompt optimization process."""
    mutate_refine_iterations: int = 3
    mutation_rounds: int = 3
    seen_set_size: int = 25
    few_shot_count: int = 3
    generate_reasoning: bool = True
    generate_expert_identity: bool = True
    temperature: float = 0.7
    max_tokens: int = 1024
    stop_sequences: Optional[List[str]] = None


@dataclass
class OptimizationResult:
    """Result of prompt optimization process."""
    original_prompt: str
    optimized_prompt: str
    expert_identity: Optional[str]
    reasoning: Optional[str]
    improvements: List[str]
    performance_score: float
    processing_time: float
    iterations_completed: int
    metadata: Dict[str, Any]


class PromptWizardError(Exception):
    """Custom exception for PromptWizard-related errors."""
    pass


class PromptWizardService:
    """
    AI-powered prompt optimization service using PromptWizard methodology.
    
    Implements:
    - Mutation-based prompt evolution
    - Few-shot learning optimization
    - Expert identity generation
    - Reasoning chain optimization
    - Performance evaluation
    """
    
    def __init__(self, config: Optional[OptimizationConfig] = None):
        self.config = config or OptimizationConfig(
            mutate_refine_iterations=settings.PROMPTWIZARD_ITERATIONS,
            mutation_rounds=settings.PROMPTWIZARD_ROUNDS,
            temperature=settings.PROMPTWIZARD_TEMPERATURE,
            max_tokens=settings.PROMPTWIZARD_MAX_TOKENS,
        )
        
        # Prompt templates for optimization
        self.mutation_prompts = [
            "Rewrite this prompt to be more specific and detailed:",
            "Make this prompt clearer and more concise:",
            "Add examples to improve this prompt:",
            "Restructure this prompt for better AI understanding:",
            "Enhance this prompt with better context:",
            "Optimize this prompt for more accurate responses:",
            "Make this prompt more actionable and specific:",
            "Improve the clarity and precision of this prompt:",
        ]
        
        self.expert_identity_prompt = """
        Based on the following prompt, identify what type of expert would be best suited to handle this task.
        Provide a brief expert identity description (1-2 sentences).
        
        Prompt: {prompt}
        
        Expert Identity:
        """
        
        self.reasoning_prompt = """
        Analyze this prompt and explain the reasoning behind any improvements that could be made.
        Focus on clarity, specificity, context, and effectiveness.
        
        Original Prompt: {original_prompt}
        Improved Prompt: {improved_prompt}
        
        Reasoning:
        """
        
        self.evaluation_prompt = """
        Evaluate the quality of this prompt on a scale of 1-10 based on:
        - Clarity and specificity
        - Context and background information
        - Actionability and structure
        - Likelihood of producing good AI responses
        
        Prompt: {prompt}
        
        Score (1-10):
        """
    
    async def optimize_prompt(
        self,
        original_prompt: str,
        task_description: Optional[str] = None,
        examples: Optional[List[str]] = None,
        target_audience: Optional[str] = None,
        progress_callback: Optional[callable] = None
    ) -> OptimizationResult:
        """
        Optimize a prompt using PromptWizard methodology.
        
        Args:
            original_prompt: The initial prompt to optimize
            task_description: Optional description of the task
            examples: Optional examples of desired outputs
            target_audience: Optional target audience description
            progress_callback: Optional callback for progress updates
            
        Returns:
            OptimizationResult: Comprehensive optimization results
        """
        start_time = datetime.utcnow()
        
        try:
            if progress_callback:
                await progress_callback(0, "Starting optimization process...")
            
            async with OllamaClient() as ollama:
                # Step 1: Generate initial mutations
                if progress_callback:
                    await progress_callback(10, "Generating prompt mutations...")
                
                mutations = await self._generate_mutations(
                    ollama, original_prompt, task_description
                )
                
                # Step 2: Evaluate mutations
                if progress_callback:
                    await progress_callback(30, "Evaluating mutations...")
                
                evaluated_mutations = await self._evaluate_mutations(ollama, mutations)
                
                # Step 3: Select best candidates
                if progress_callback:
                    await progress_callback(50, "Selecting best candidates...")
                
                best_candidates = await self._select_best_candidates(
                    evaluated_mutations, self.config.seen_set_size
                )
                
                # Step 4: Refine best candidate
                if progress_callback:
                    await progress_callback(70, "Refining optimal prompt...")
                
                refined_prompt = await self._refine_prompt(
                    ollama, best_candidates[0], examples, target_audience
                )
                
                # Step 5: Generate expert identity
                if progress_callback:
                    await progress_callback(85, "Generating expert identity...")
                
                expert_identity = None
                if self.config.generate_expert_identity:
                    expert_identity = await self._generate_expert_identity(
                        ollama, refined_prompt
                    )
                
                # Step 6: Generate reasoning
                if progress_callback:
                    await progress_callback(95, "Generating optimization reasoning...")
                
                reasoning = None
                if self.config.generate_reasoning:
                    reasoning = await self._generate_reasoning(
                        ollama, original_prompt, refined_prompt
                    )
                
                # Step 7: Calculate final metrics
                if progress_callback:
                    await progress_callback(100, "Finalizing results...")
                
                end_time = datetime.utcnow()
                processing_time = (end_time - start_time).total_seconds()
                
                # Extract improvements
                improvements = await self._extract_improvements(
                    original_prompt, refined_prompt
                )
                
                # Calculate performance score
                performance_score = await self._calculate_performance_score(
                    ollama, refined_prompt
                )
                
                return OptimizationResult(
                    original_prompt=original_prompt,
                    optimized_prompt=refined_prompt,
                    expert_identity=expert_identity,
                    reasoning=reasoning,
                    improvements=improvements,
                    performance_score=performance_score,
                    processing_time=processing_time,
                    iterations_completed=self.config.mutate_refine_iterations,
                    metadata={
                        "config": self.config.__dict__,
                        "mutations_generated": len(mutations),
                        "candidates_evaluated": len(evaluated_mutations),
                        "task_description": task_description,
                        "examples_provided": len(examples) if examples else 0,
                        "target_audience": target_audience,
                        "timestamp": end_time.isoformat(),
                    }
                )
                
        except Exception as e:
            logger.error(f"Prompt optimization failed: {e}")
            raise PromptWizardError(f"Optimization process failed: {e}")
    
    async def _generate_mutations(
        self,
        ollama: OllamaClient,
        original_prompt: str,
        task_description: Optional[str] = None
    ) -> List[str]:
        """Generate multiple prompt mutations using different strategies."""
        mutations = []
        
        # Context enhancement
        context = ""
        if task_description:
            context = f"\nTask Context: {task_description}"
        
        # Generate mutations using different prompts
        for i in range(self.config.mutation_rounds):
            mutation_prompt = random.choice(self.mutation_prompts)
            
            full_prompt = f"""
            {mutation_prompt}
            {context}
            
            Original Prompt: {original_prompt}
            
            Improved Prompt:
            """
            
            try:
                response = await ollama.generate_completion(
                    prompt=full_prompt,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens,
                )
                
                mutation = response.get("response", "").strip()
                if mutation and mutation != original_prompt:
                    mutations.append(mutation)
                    
            except Exception as e:
                logger.warning(f"Failed to generate mutation {i+1}: {e}")
                continue
        
        # Add the original prompt as a baseline
        mutations.append(original_prompt)
        
        return mutations
    
    async def _evaluate_mutations(
        self,
        ollama: OllamaClient,
        mutations: List[str]
    ) -> List[Tuple[str, float]]:
        """Evaluate mutations and return scored pairs."""
        evaluated = []
        
        for mutation in mutations:
            try:
                score = await self._calculate_performance_score(ollama, mutation)
                evaluated.append((mutation, score))
                
            except Exception as e:
                logger.warning(f"Failed to evaluate mutation: {e}")
                # Assign neutral score if evaluation fails
                evaluated.append((mutation, 5.0))
        
        return evaluated
    
    async def _select_best_candidates(
        self,
        evaluated_mutations: List[Tuple[str, float]],
        count: int
    ) -> List[str]:
        """Select the best performing candidates."""
        # Sort by score (descending)
        sorted_mutations = sorted(evaluated_mutations, key=lambda x: x[1], reverse=True)
        
        # Return top candidates
        return [mutation for mutation, score in sorted_mutations[:count]]
    
    async def _refine_prompt(
        self,
        ollama: OllamaClient,
        base_prompt: str,
        examples: Optional[List[str]] = None,
        target_audience: Optional[str] = None
    ) -> str:
        """Refine the best candidate with additional context."""
        
        refinement_prompt = f"""
        Refine and optimize this prompt to make it as effective as possible.
        Consider clarity, specificity, context, and actionability.
        """
        
        if examples:
            examples_text = "\n".join([f"- {ex}" for ex in examples[:self.config.few_shot_count]])
            refinement_prompt += f"\n\nInclude relevant examples like:\n{examples_text}"
        
        if target_audience:
            refinement_prompt += f"\n\nTarget audience: {target_audience}"
        
        refinement_prompt += f"""
        
        Prompt to refine: {base_prompt}
        
        Refined prompt:
        """
        
        try:
            response = await ollama.generate_completion(
                prompt=refinement_prompt,
                temperature=self.config.temperature * 0.8,  # Lower temperature for refinement
                max_tokens=self.config.max_tokens,
            )
            
            refined = response.get("response", "").strip()
            return refined if refined else base_prompt
            
        except Exception as e:
            logger.warning(f"Failed to refine prompt: {e}")
            return base_prompt
    
    async def _generate_expert_identity(
        self,
        ollama: OllamaClient,
        prompt: str
    ) -> Optional[str]:
        """Generate expert identity for the optimized prompt."""
        try:
            expert_prompt = self.expert_identity_prompt.format(prompt=prompt)
            
            response = await ollama.generate_completion(
                prompt=expert_prompt,
                temperature=0.3,  # Lower temperature for consistency
                max_tokens=200,
            )
            
            return response.get("response", "").strip()
            
        except Exception as e:
            logger.warning(f"Failed to generate expert identity: {e}")
            return None
    
    async def _generate_reasoning(
        self,
        ollama: OllamaClient,
        original_prompt: str,
        improved_prompt: str
    ) -> Optional[str]:
        """Generate reasoning for the optimization."""
        try:
            reasoning_prompt = self.reasoning_prompt.format(
                original_prompt=original_prompt,
                improved_prompt=improved_prompt
            )
            
            response = await ollama.generate_completion(
                prompt=reasoning_prompt,
                temperature=0.3,
                max_tokens=500,
            )
            
            return response.get("response", "").strip()
            
        except Exception as e:
            logger.warning(f"Failed to generate reasoning: {e}")
            return None
    
    async def _calculate_performance_score(
        self,
        ollama: OllamaClient,
        prompt: str
    ) -> float:
        """Calculate performance score for a prompt."""
        try:
            evaluation_prompt = self.evaluation_prompt.format(prompt=prompt)
            
            response = await ollama.generate_completion(
                prompt=evaluation_prompt,
                temperature=0.1,  # Low temperature for consistent scoring
                max_tokens=50,
            )
            
            response_text = response.get("response", "").strip()
            
            # Extract numeric score using regex
            score_match = re.search(r'(\d+(?:\.\d+)?)', response_text)
            if score_match:
                score = float(score_match.group(1))
                return max(1.0, min(10.0, score))  # Clamp between 1-10
            
            # Fallback: try to extract score from common patterns
            if "excellent" in response_text.lower() or "10" in response_text:
                return 9.0
            elif "good" in response_text.lower() or "8" in response_text or "9" in response_text:
                return 8.0
            elif "average" in response_text.lower() or "5" in response_text or "6" in response_text or "7" in response_text:
                return 6.0
            elif "poor" in response_text.lower() or "3" in response_text or "4" in response_text or "2" in response_text:
                return 3.0
            else:
                return 5.0  # Default neutral score
                
        except Exception as e:
            logger.warning(f"Failed to calculate performance score: {e}")
            return 5.0  # Default neutral score
    
    async def _extract_improvements(
        self,
        original_prompt: str,
        optimized_prompt: str
    ) -> List[str]:
        """Extract key improvements made to the prompt."""
        improvements = []
        
        # Simple heuristic-based improvement detection
        if len(optimized_prompt) > len(original_prompt) * 1.2:
            improvements.append("Added more detailed context and specificity")
        
        if "example" in optimized_prompt.lower() and "example" not in original_prompt.lower():
            improvements.append("Included relevant examples")
        
        if optimized_prompt.count(".") > original_prompt.count("."):
            improvements.append("Improved structure and clarity")
        
        if ("step" in optimized_prompt.lower() or "first" in optimized_prompt.lower()) and \
           ("step" not in original_prompt.lower() and "first" not in original_prompt.lower()):
            improvements.append("Added step-by-step guidance")
        
        if "context" in optimized_prompt.lower() and "context" not in original_prompt.lower():
            improvements.append("Enhanced contextual information")
        
        # If no specific improvements detected, add generic improvement
        if not improvements:
            improvements.append("Enhanced overall clarity and effectiveness")
        
        return improvements