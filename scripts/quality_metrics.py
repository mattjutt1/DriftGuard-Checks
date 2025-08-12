#!/usr/bin/env python3
"""
PromptEvolver 3.0 - Quality Metrics Calculator
===============================================
Comprehensive quality metrics for evaluating prompt optimizations.
Implements the 7-dimensional quality scoring system from the PRD.

Copyright (c) 2025 Matthew J. Utt
"""

import os
import sys
import json
import re
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field, asdict
from collections import Counter, defaultdict
import statistics

import numpy as np
from scipy import stats
from textstat import flesch_reading_ease, flesch_kincaid_grade
import spacy
from sentence_transformers import SentenceTransformer
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class QualityDimensions:
    """The 7 quality dimensions for prompt evaluation."""

    clarity: float = 0.0  # 0-1 score
    specificity: float = 0.0
    actionability: float = 0.0
    context_relevance: float = 0.0
    completeness: float = 0.0
    coherence: float = 0.0
    effectiveness: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return asdict(self)

    def overall_score(self, weights: Optional[Dict[str, float]] = None) -> float:
        """Calculate weighted overall score."""
        if weights is None:
            # Default equal weights
            weights = {
                'clarity': 1.0,
                'specificity': 1.0,
                'actionability': 1.0,
                'context_relevance': 1.0,
                'completeness': 1.0,
                'coherence': 1.0,
                'effectiveness': 1.0
            }

        total_weight = sum(weights.values())
        weighted_sum = (
            self.clarity * weights.get('clarity', 1.0) +
            self.specificity * weights.get('specificity', 1.0) +
            self.actionability * weights.get('actionability', 1.0) +
            self.context_relevance * weights.get('context_relevance', 1.0) +
            self.completeness * weights.get('completeness', 1.0) +
            self.coherence * weights.get('coherence', 1.0) +
            self.effectiveness * weights.get('effectiveness', 1.0)
        )

        return weighted_sum / total_weight if total_weight > 0 else 0.0


class QualityMetricsCalculator:
    """Calculate comprehensive quality metrics for prompts."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize quality metrics calculator.

        Args:
            model_name: Name of sentence transformer model for embeddings
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load models
        try:
            self.sentence_model = SentenceTransformer(model_name)
            self.sentence_model.to(self.device)
        except Exception as e:
            logger.warning(f"Failed to load sentence transformer: {e}")
            self.sentence_model = None

        # Load spaCy for linguistic analysis
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            logger.warning("spaCy model not found. Installing...")
            os.system("python -m spacy download en_core_web_sm")
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except:
                logger.error("Failed to load spaCy model")
                self.nlp = None

        # Define quality indicators
        self._initialize_quality_indicators()

    def _initialize_quality_indicators(self):
        """Initialize quality indicator lists and patterns."""

        # Clarity indicators
        self.clarity_positive = {
            'simple_connectors': ['and', 'but', 'or', 'so', 'because'],
            'clear_structure': ['first', 'second', 'then', 'finally', 'next'],
            'explicit_markers': ['specifically', 'exactly', 'precisely']
        }

        self.clarity_negative = {
            'vague_terms': ['thing', 'stuff', 'whatever', 'something', 'somehow'],
            'complex_jargon': ['utilize', 'leverage', 'synergize', 'paradigm'],
            'ambiguous': ['maybe', 'possibly', 'might', 'could', 'perhaps']
        }

        # Specificity indicators
        self.specificity_patterns = {
            'numbers': r'\d+',
            'measurements': r'\d+\s*(mb|gb|kb|ms|s|min|hour|day|week|month|year)',
            'technical_terms': r'\b(api|database|algorithm|function|class|method|variable)\b',
            'proper_nouns': r'\b[A-Z][a-z]+\b'
        }

        # Actionability indicators
        self.action_verbs = {
            'create', 'build', 'implement', 'design', 'develop',
            'write', 'generate', 'analyze', 'evaluate', 'optimize',
            'configure', 'setup', 'install', 'deploy', 'test',
            'refactor', 'debug', 'fix', 'improve', 'enhance'
        }

        self.requirement_terms = {
            'must', 'should', 'shall', 'need', 'require',
            'ensure', 'verify', 'validate', 'confirm', 'check'
        }

        # Completeness indicators
        self.completeness_aspects = {
            'input': ['input', 'data', 'parameters', 'arguments'],
            'output': ['output', 'result', 'return', 'response'],
            'process': ['process', 'method', 'approach', 'algorithm'],
            'constraints': ['constraint', 'limit', 'requirement', 'condition'],
            'examples': ['example', 'instance', 'sample', 'demonstration']
        }

    def calculate_clarity(self, text: str) -> float:
        """
        Calculate clarity score based on readability and structure.

        Args:
            text: Text to evaluate

        Returns:
            Clarity score (0-1)
        """
        if not text:
            return 0.0

        scores = []

        # Readability score
        try:
            flesch_score = flesch_reading_ease(text)
            # Normalize Flesch score (0-100) to 0-1
            readability = max(0, min(1, flesch_score / 100))
            scores.append(readability)
        except:
            scores.append(0.5)  # Default if calculation fails

        # Check for vague terms (negative impact)
        words = text.lower().split()
        vague_count = sum(1 for word in words
                         for vague_list in self.clarity_negative['vague_terms']
                         if word == vague_list)
        vagueness_penalty = 1.0 - min(1.0, vague_count / (len(words) + 1))
        scores.append(vagueness_penalty)

        # Check for clear structure markers (positive impact)
        structure_markers = sum(1 for marker in self.clarity_positive['clear_structure']
                               if marker in text.lower())
        structure_bonus = min(1.0, structure_markers / 3)
        scores.append(structure_bonus)

        # Sentence complexity
        if self.nlp:
            doc = self.nlp(text)
            sentences = list(doc.sents)
            if sentences:
                avg_length = np.mean([len(sent.text.split()) for sent in sentences])
                # Optimal sentence length is 15-20 words
                if 15 <= avg_length <= 20:
                    complexity_score = 1.0
                elif avg_length < 10 or avg_length > 30:
                    complexity_score = 0.5
                else:
                    complexity_score = 0.75
                scores.append(complexity_score)

        return np.mean(scores) if scores else 0.5

    def calculate_specificity(self, text: str) -> float:
        """
        Calculate specificity score based on concrete details.

        Args:
            text: Text to evaluate

        Returns:
            Specificity score (0-1)
        """
        if not text:
            return 0.0

        scores = []
        words = text.split()

        # Check for numbers
        numbers = len(re.findall(self.specificity_patterns['numbers'], text))
        number_score = min(1.0, numbers / 5)  # Expect up to 5 numbers for full score
        scores.append(number_score)

        # Check for measurements
        measurements = len(re.findall(self.specificity_patterns['measurements'], text))
        measurement_score = min(1.0, measurements / 3)
        scores.append(measurement_score)

        # Check for technical terms
        technical = len(re.findall(self.specificity_patterns['technical_terms'], text.lower()))
        technical_score = min(1.0, technical / 5)
        scores.append(technical_score)

        # Check for proper nouns (specific names)
        proper_nouns = len(re.findall(self.specificity_patterns['proper_nouns'], text))
        proper_score = min(1.0, proper_nouns / 3)
        scores.append(proper_score)

        # Word variety (more unique words = more specific)
        unique_ratio = len(set(words)) / len(words) if words else 0
        scores.append(unique_ratio)

        return np.mean(scores) if scores else 0.0

    def calculate_actionability(self, text: str) -> float:
        """
        Calculate actionability score based on action verbs and directives.

        Args:
            text: Text to evaluate

        Returns:
            Actionability score (0-1)
        """
        if not text:
            return 0.0

        scores = []
        words = text.lower().split()

        # Check for action verbs
        action_count = sum(1 for word in words if word in self.action_verbs)
        action_score = min(1.0, action_count / 3)  # Expect 3 action verbs for full score
        scores.append(action_score)

        # Check for requirement terms
        requirement_count = sum(1 for word in words if word in self.requirement_terms)
        requirement_score = min(1.0, requirement_count / 2)
        scores.append(requirement_score)

        # Check for imperative mood (commands)
        if self.nlp:
            doc = self.nlp(text)
            imperative_count = 0
            for sent in doc.sents:
                # Simple heuristic: sentence starts with verb
                if sent and sent[0].pos_ == "VERB":
                    imperative_count += 1

            if list(doc.sents):
                imperative_score = imperative_count / len(list(doc.sents))
            else:
                imperative_score = 0
            scores.append(imperative_score)

        # Check for clear goals/objectives
        goal_indicators = ['to', 'in order to', 'so that', 'goal', 'objective', 'purpose']
        goal_count = sum(1 for indicator in goal_indicators if indicator in text.lower())
        goal_score = min(1.0, goal_count / 2)
        scores.append(goal_score)

        return np.mean(scores) if scores else 0.0

    def calculate_context_relevance(self, text: str, context: Optional[str] = None) -> float:
        """
        Calculate context relevance score.

        Args:
            text: Text to evaluate
            context: Optional context to compare against

        Returns:
            Context relevance score (0-1)
        """
        if not text:
            return 0.0

        # If no context provided, check for internal context markers
        if not context:
            scores = []

            # Check for context-setting phrases
            context_phrases = [
                'given', 'assuming', 'considering', 'based on',
                'in the context of', 'with respect to', 'regarding'
            ]
            context_count = sum(1 for phrase in context_phrases if phrase in text.lower())
            context_score = min(1.0, context_count / 2)
            scores.append(context_score)

            # Check for background information
            background_markers = ['background:', 'context:', 'setup:', 'scenario:']
            has_background = any(marker in text.lower() for marker in background_markers)
            scores.append(1.0 if has_background else 0.5)

            return np.mean(scores)

        # If context provided, calculate similarity
        if self.sentence_model:
            embeddings = self.sentence_model.encode([text, context])
            similarity = torch.nn.functional.cosine_similarity(
                torch.tensor(embeddings[0]),
                torch.tensor(embeddings[1]),
                dim=0
            )
            return float(similarity)

        # Fallback: word overlap
        text_words = set(text.lower().split())
        context_words = set(context.lower().split())

        if not context_words:
            return 0.5

        overlap = text_words & context_words
        return len(overlap) / len(context_words)

    def calculate_completeness(self, text: str) -> float:
        """
        Calculate completeness score based on coverage of essential aspects.

        Args:
            text: Text to evaluate

        Returns:
            Completeness score (0-1)
        """
        if not text:
            return 0.0

        scores = []
        text_lower = text.lower()

        # Check coverage of essential aspects
        for aspect, keywords in self.completeness_aspects.items():
            has_aspect = any(keyword in text_lower for keyword in keywords)
            scores.append(1.0 if has_aspect else 0.0)

        # Check for edge cases mentioned
        edge_indicators = ['edge case', 'exception', 'error', 'invalid', 'boundary']
        has_edge = any(indicator in text_lower for indicator in edge_indicators)
        scores.append(1.0 if has_edge else 0.5)

        # Check for success criteria
        success_indicators = ['success', 'complete', 'done', 'finish', 'achieve']
        has_success = any(indicator in text_lower for indicator in success_indicators)
        scores.append(1.0 if has_success else 0.5)

        # Length as a proxy for completeness (longer usually more complete)
        word_count = len(text.split())
        if word_count < 20:
            length_score = 0.3
        elif word_count < 50:
            length_score = 0.6
        elif word_count < 100:
            length_score = 0.8
        else:
            length_score = 1.0
        scores.append(length_score)

        return np.mean(scores) if scores else 0.0

    def calculate_coherence(self, text: str) -> float:
        """
        Calculate coherence score based on logical flow and consistency.

        Args:
            text: Text to evaluate

        Returns:
            Coherence score (0-1)
        """
        if not text:
            return 0.0

        scores = []

        # Check for logical connectors
        connectors = [
            'therefore', 'thus', 'hence', 'consequently',
            'however', 'moreover', 'furthermore', 'additionally',
            'first', 'second', 'then', 'finally', 'next'
        ]
        connector_count = sum(1 for conn in connectors if conn in text.lower())
        connector_score = min(1.0, connector_count / 3)
        scores.append(connector_score)

        # Check for consistent terminology
        if self.nlp:
            doc = self.nlp(text)

            # Extract noun phrases
            noun_phrases = [chunk.text.lower() for chunk in doc.noun_chunks]

            if noun_phrases:
                # Check for repeated concepts (good for coherence)
                phrase_counts = Counter(noun_phrases)
                repeated = sum(1 for count in phrase_counts.values() if count > 1)
                consistency_score = min(1.0, repeated / 3)
                scores.append(consistency_score)

            # Check sentence-to-sentence similarity
            sentences = list(doc.sents)
            if len(sentences) > 1 and self.sentence_model:
                sent_texts = [sent.text for sent in sentences]
                embeddings = self.sentence_model.encode(sent_texts)

                similarities = []
                for i in range(len(embeddings) - 1):
                    sim = torch.nn.functional.cosine_similarity(
                        torch.tensor(embeddings[i]),
                        torch.tensor(embeddings[i + 1]),
                        dim=0
                    )
                    similarities.append(float(sim))

                # Moderate similarity is good (not too high, not too low)
                avg_sim = np.mean(similarities)
                if 0.3 <= avg_sim <= 0.7:
                    flow_score = 1.0
                elif avg_sim < 0.2 or avg_sim > 0.8:
                    flow_score = 0.5
                else:
                    flow_score = 0.75
                scores.append(flow_score)

        # Check for consistent verb tense
        if self.nlp:
            doc = self.nlp(text)
            tenses = []
            for token in doc:
                if token.pos_ == "VERB":
                    if "Past" in token.morph.get("Tense", []):
                        tenses.append("past")
                    elif "Pres" in token.morph.get("Tense", []):
                        tenses.append("present")
                    elif "Fut" in token.morph.get("Tense", []):
                        tenses.append("future")

            if tenses:
                # Check if most verbs are in the same tense
                tense_counts = Counter(tenses)
                most_common_tense_count = tense_counts.most_common(1)[0][1]
                tense_consistency = most_common_tense_count / len(tenses)
                scores.append(tense_consistency)

        return np.mean(scores) if scores else 0.5

    def calculate_effectiveness(self, text: str, purpose: Optional[str] = None) -> float:
        """
        Calculate effectiveness score based on likely achievement of purpose.

        Args:
            text: Text to evaluate
            purpose: Optional stated purpose of the prompt

        Returns:
            Effectiveness score (0-1)
        """
        if not text:
            return 0.0

        scores = []

        # General effectiveness indicators
        effectiveness_indicators = {
            'clear_objective': ['objective', 'goal', 'aim', 'purpose', 'target'],
            'measurable': ['measure', 'metric', 'evaluate', 'assess', 'quantify'],
            'achievable': ['achievable', 'feasible', 'possible', 'realistic'],
            'relevant': ['relevant', 'important', 'critical', 'essential'],
            'time_bound': ['deadline', 'by', 'within', 'timeframe', 'schedule']
        }

        text_lower = text.lower()

        # Check SMART criteria
        for criterion, keywords in effectiveness_indicators.items():
            has_criterion = any(keyword in text_lower for keyword in keywords)
            scores.append(1.0 if has_criterion else 0.5)

        # Check for clear instructions
        instruction_patterns = [
            r'\d+\.',  # Numbered lists
            r'[a-z]\)',  # Lettered lists
            r'step \d+',  # Step indicators
            r'•',  # Bullet points
        ]

        has_structure = any(re.search(pattern, text_lower) for pattern in instruction_patterns)
        scores.append(1.0 if has_structure else 0.6)

        # If purpose is provided, check alignment
        if purpose and self.sentence_model:
            embeddings = self.sentence_model.encode([text, purpose])
            alignment = torch.nn.functional.cosine_similarity(
                torch.tensor(embeddings[0]),
                torch.tensor(embeddings[1]),
                dim=0
            )
            scores.append(float(alignment))

        # Check for actionable outcomes
        outcome_indicators = ['result', 'output', 'produce', 'create', 'deliver']
        has_outcomes = any(indicator in text_lower for indicator in outcome_indicators)
        scores.append(1.0 if has_outcomes else 0.6)

        return np.mean(scores) if scores else 0.5

    def calculate_quality_dimensions(self,
                                   text: str,
                                   context: Optional[str] = None,
                                   purpose: Optional[str] = None) -> QualityDimensions:
        """
        Calculate all quality dimensions for a text.

        Args:
            text: Text to evaluate
            context: Optional context for relevance calculation
            purpose: Optional purpose for effectiveness calculation

        Returns:
            QualityDimensions object with all scores
        """
        return QualityDimensions(
            clarity=self.calculate_clarity(text),
            specificity=self.calculate_specificity(text),
            actionability=self.calculate_actionability(text),
            context_relevance=self.calculate_context_relevance(text, context),
            completeness=self.calculate_completeness(text),
            coherence=self.calculate_coherence(text),
            effectiveness=self.calculate_effectiveness(text, purpose)
        )

    def compare_quality(self,
                       original: str,
                       optimized: str,
                       context: Optional[str] = None) -> Dict[str, Any]:
        """
        Compare quality between original and optimized prompts.

        Args:
            original: Original prompt
            optimized: Optimized prompt
            context: Optional context

        Returns:
            Dictionary with comparison results
        """
        original_quality = self.calculate_quality_dimensions(original, context)
        optimized_quality = self.calculate_quality_dimensions(optimized, context)

        improvements = QualityDimensions(
            clarity=optimized_quality.clarity - original_quality.clarity,
            specificity=optimized_quality.specificity - original_quality.specificity,
            actionability=optimized_quality.actionability - original_quality.actionability,
            context_relevance=optimized_quality.context_relevance - original_quality.context_relevance,
            completeness=optimized_quality.completeness - original_quality.completeness,
            coherence=optimized_quality.coherence - original_quality.coherence,
            effectiveness=optimized_quality.effectiveness - original_quality.effectiveness
        )

        return {
            'original': original_quality.to_dict(),
            'optimized': optimized_quality.to_dict(),
            'improvements': improvements.to_dict(),
            'original_overall': original_quality.overall_score(),
            'optimized_overall': optimized_quality.overall_score(),
            'overall_improvement': optimized_quality.overall_score() - original_quality.overall_score(),
            'improvement_rate': sum(1 for v in improvements.to_dict().values() if v > 0) / 7
        }

    def batch_evaluate(self,
                      prompts: List[str],
                      contexts: Optional[List[str]] = None) -> List[QualityDimensions]:
        """
        Evaluate multiple prompts in batch.

        Args:
            prompts: List of prompts to evaluate
            contexts: Optional list of contexts

        Returns:
            List of QualityDimensions
        """
        results = []

        if contexts is None:
            contexts = [None] * len(prompts)

        for prompt, context in zip(prompts, contexts):
            quality = self.calculate_quality_dimensions(prompt, context)
            results.append(quality)

        return results

    def generate_quality_report(self,
                               prompt: str,
                               context: Optional[str] = None,
                               purpose: Optional[str] = None) -> str:
        """
        Generate a detailed quality report for a prompt.

        Args:
            prompt: Prompt to evaluate
            context: Optional context
            purpose: Optional purpose

        Returns:
            Formatted quality report
        """
        quality = self.calculate_quality_dimensions(prompt, context, purpose)

        report = []
        report.append("=" * 60)
        report.append("PROMPT QUALITY ANALYSIS REPORT")
        report.append("=" * 60)
        report.append("")

        report.append("PROMPT:")
        report.append("-" * 40)
        report.append(prompt[:200] + "..." if len(prompt) > 200 else prompt)
        report.append("")

        report.append("QUALITY DIMENSIONS:")
        report.append("-" * 40)

        dimensions = [
            ("Clarity", quality.clarity, "How clear and understandable the prompt is"),
            ("Specificity", quality.specificity, "Level of concrete details and precision"),
            ("Actionability", quality.actionability, "How well it guides toward action"),
            ("Context Relevance", quality.context_relevance, "Alignment with context"),
            ("Completeness", quality.completeness, "Coverage of necessary information"),
            ("Coherence", quality.coherence, "Logical flow and consistency"),
            ("Effectiveness", quality.effectiveness, "Likelihood of achieving purpose")
        ]

        for name, score, description in dimensions:
            bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
            report.append(f"{name:18} [{bar}] {score:.2f}")
            report.append(f"                   {description}")
            report.append("")

        report.append("OVERALL SCORE:")
        report.append("-" * 40)
        overall = quality.overall_score()
        grade = self._score_to_grade(overall)
        report.append(f"Score: {overall:.2f}/1.00 ({grade})")
        report.append("")

        report.append("RECOMMENDATIONS:")
        report.append("-" * 40)
        recommendations = self._generate_recommendations(quality)
        for i, rec in enumerate(recommendations, 1):
            report.append(f"{i}. {rec}")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)

    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 0.9:
            return "A+ (Excellent)"
        elif score >= 0.8:
            return "A (Very Good)"
        elif score >= 0.7:
            return "B (Good)"
        elif score >= 0.6:
            return "C (Satisfactory)"
        elif score >= 0.5:
            return "D (Needs Improvement)"
        else:
            return "F (Poor)"

    def _generate_recommendations(self, quality: QualityDimensions) -> List[str]:
        """Generate improvement recommendations based on quality scores."""
        recommendations = []

        # Check each dimension and provide specific recommendations
        if quality.clarity < 0.7:
            recommendations.append(
                "Improve clarity by using simpler language and avoiding vague terms"
            )

        if quality.specificity < 0.7:
            recommendations.append(
                "Add more specific details, numbers, and concrete examples"
            )

        if quality.actionability < 0.7:
            recommendations.append(
                "Include clear action verbs and explicit requirements"
            )

        if quality.context_relevance < 0.7:
            recommendations.append(
                "Provide more context or background information"
            )

        if quality.completeness < 0.7:
            recommendations.append(
                "Address all aspects including inputs, outputs, and constraints"
            )

        if quality.coherence < 0.7:
            recommendations.append(
                "Improve logical flow with better transitions and consistent terminology"
            )

        if quality.effectiveness < 0.7:
            recommendations.append(
                "Clarify objectives and include measurable success criteria"
            )

        if not recommendations:
            recommendations.append("Prompt quality is excellent - minor refinements only")

        return recommendations


def main():
    """Main entry point for quality metrics."""
    parser = argparse.ArgumentParser(description="Calculate prompt quality metrics")

    parser.add_argument(
        "prompt",
        type=str,
        help="Prompt to evaluate (or path to file)"
    )
    parser.add_argument(
        "--context",
        type=str,
        default=None,
        help="Optional context for evaluation"
    )
    parser.add_argument(
        "--purpose",
        type=str,
        default=None,
        help="Optional purpose statement"
    )
    parser.add_argument(
        "--compare",
        type=str,
        default=None,
        help="Second prompt for comparison"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate detailed report"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    # Load prompt from file if path provided
    if os.path.isfile(args.prompt):
        with open(args.prompt, 'r') as f:
            prompt_text = f.read()
    else:
        prompt_text = args.prompt

    # Initialize calculator
    calculator = QualityMetricsCalculator()

    if args.compare:
        # Load comparison prompt
        if os.path.isfile(args.compare):
            with open(args.compare, 'r') as f:
                compare_text = f.read()
        else:
            compare_text = args.compare

        # Compare quality
        results = calculator.compare_quality(prompt_text, compare_text, args.context)

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print("\n" + "=" * 60)
            print("QUALITY COMPARISON")
            print("=" * 60)
            print(f"\nOriginal Overall Score: {results['original_overall']:.3f}")
            print(f"Optimized Overall Score: {results['optimized_overall']:.3f}")
            print(f"Overall Improvement: {results['overall_improvement']:+.3f}")
            print(f"Dimensions Improved: {results['improvement_rate']*100:.1f}%")

            print("\nDimension Improvements:")
            for dim, improvement in results['improvements'].items():
                if improvement != 0:
                    print(f"  {dim}: {improvement:+.3f}")

    elif args.report:
        # Generate detailed report
        report = calculator.generate_quality_report(prompt_text, args.context, args.purpose)
        print(report)

    else:
        # Calculate quality dimensions
        quality = calculator.calculate_quality_dimensions(prompt_text, args.context, args.purpose)

        if args.json:
            results = {
                'dimensions': quality.to_dict(),
                'overall_score': quality.overall_score()
            }
            print(json.dumps(results, indent=2))
        else:
            print("\n" + "=" * 60)
            print("QUALITY METRICS")
            print("=" * 60)

            for name, value in quality.to_dict().items():
                bar = "█" * int(value * 20) + "░" * (20 - int(value * 20))
                print(f"{name:18} [{bar}] {value:.3f}")

            print("-" * 60)
            print(f"Overall Score: {quality.overall_score():.3f}")


if __name__ == "__main__":
    main()
