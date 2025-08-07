#!/usr/bin/env python3
"""
Schema Validation System for Prompt Enhancement
Ensures compliance with PRD-specified schema requirements
"""

import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple


class SchemaVersion(Enum):
    """Supported schema versions"""

    V1_0 = "1.0"
    V1_1 = "1.1"
    V1_2 = "1.2"  # Current version per PRD


@dataclass
class ValidationResult:
    """Result of schema validation"""

    is_valid: bool
    score: float  # 0.0 to 1.0
    missing_tags: List[str]
    invalid_formats: List[str]
    warnings: List[str]
    version: str


class PromptSchemaValidator:
    """Validates enhanced prompts against PRD schema requirements"""

    # Required tags per PRD FR1
    REQUIRED_TAGS = [
        "OBJECTIVE",
        "CONTEXT",
        "REQUIREMENTS",
        "CONSTRAINTS",
        "OUTPUT_FORMAT",
        "EVALUATION_CRITERIA",
        "DOMAIN",
    ]

    # Optional tags
    OPTIONAL_TAGS = ["EDGE_CASES", "EXAMPLES", "RATIONALE", "FAILURE_MODES"]

    # Valid domains per PRD
    VALID_DOMAINS = ["analytics", "coding", "content", "cross_domain"]

    def __init__(self, version: SchemaVersion = SchemaVersion.V1_2):
        self.version = version
        self.tag_pattern = re.compile(r"<([A-Z_]+)>(.*?)</\1>", re.DOTALL)

    def validate(self, prompt: str) -> ValidationResult:
        """Validate a prompt against schema requirements"""

        missing_tags = []
        invalid_formats = []
        warnings = []

        # Extract schema version
        version = self._extract_version(prompt)
        if not version:
            warnings.append("No SCHEMA_VERSION tag found")
            version = self.version.value

        # Extract all tags
        tags_found = self._extract_tags(prompt)

        # Check required tags
        for tag in self.REQUIRED_TAGS:
            if tag not in tags_found:
                missing_tags.append(tag)

        # Validate domain
        if "DOMAIN" in tags_found:
            domain = tags_found["DOMAIN"].strip().lower()
            if domain not in self.VALID_DOMAINS:
                invalid_formats.append(f"Invalid domain: {domain}")

        # Validate OUTPUT_FORMAT (should be parseable)
        if "OUTPUT_FORMAT" in tags_found:
            output_format = tags_found["OUTPUT_FORMAT"]
            if not self._validate_output_format(output_format):
                warnings.append("OUTPUT_FORMAT may not be properly structured")

        # Check for proper tag closure
        if not self._check_tag_closure(prompt):
            invalid_formats.append("Unclosed or malformed tags detected")

        # Calculate compliance score
        total_checks = len(self.REQUIRED_TAGS) + 2  # +2 for domain and format
        passed_checks = len(self.REQUIRED_TAGS) - len(missing_tags)
        if not invalid_formats:
            passed_checks += 2

        score = passed_checks / total_checks

        # Determine validity (≥98% compliance per PRD)
        is_valid = score >= 0.98 and len(missing_tags) == 0

        return ValidationResult(
            is_valid=is_valid,
            score=score,
            missing_tags=missing_tags,
            invalid_formats=invalid_formats,
            warnings=warnings,
            version=version,
        )

    def _extract_version(self, prompt: str) -> Optional[str]:
        """Extract schema version from prompt"""
        match = re.search(r"<SCHEMA_VERSION>(.*?)</SCHEMA_VERSION>", prompt)
        return match.group(1) if match else None

    def _extract_tags(self, prompt: str) -> Dict[str, str]:
        """Extract all tags and their content"""
        tags = {}
        for match in self.tag_pattern.finditer(prompt):
            tag_name = match.group(1)
            tag_content = match.group(2).strip()
            tags[tag_name] = tag_content
        return tags

    def _validate_output_format(self, format_str: str) -> bool:
        """Validate OUTPUT_FORMAT content"""
        # Check if it's JSON-like
        if format_str.strip().startswith("{"):
            try:
                # Try to parse as JSON
                json.loads(format_str)
                return True
            except:
                pass

        # Check for other structured formats
        structured_indicators = ["```", "format:", "structure:", "{", "["]
        return any(indicator in format_str.lower() for indicator in structured_indicators)

    def _check_tag_closure(self, prompt: str) -> bool:
        """Check if all tags are properly closed"""
        # Find all opening tags
        opening_tags = re.findall(r"<([A-Z_]+)>", prompt)
        # Find all closing tags
        closing_tags = re.findall(r"</([A-Z_]+)>", prompt)

        # Check if counts match
        return len(opening_tags) == len(closing_tags)

    def upgrade_schema(self, prompt: str, from_version: str, to_version: str) -> str:
        """Upgrade prompt from one schema version to another"""

        if from_version == "1.0" and to_version == "1.2":
            # Add DOMAIN tag if missing
            if "<DOMAIN>" not in prompt:
                # Try to infer domain from content
                domain = self._infer_domain(prompt)
                prompt = f"<DOMAIN>{domain}</DOMAIN>\n{prompt}"

            # Update version tag
            prompt = re.sub(
                r"<SCHEMA_VERSION>.*?</SCHEMA_VERSION>",
                f"<SCHEMA_VERSION>{to_version}</SCHEMA_VERSION>",
                prompt,
            )

        return prompt

    def _infer_domain(self, prompt: str) -> str:
        """Infer domain from prompt content"""
        prompt_lower = prompt.lower()

        if any(
            word in prompt_lower for word in ["data", "metric", "analysis", "report", "statistics"]
        ):
            return "analytics"
        elif any(word in prompt_lower for word in ["code", "function", "bug", "optimize", "api"]):
            return "coding"
        elif any(
            word in prompt_lower for word in ["write", "blog", "article", "content", "document"]
        ):
            return "content"
        else:
            return "cross_domain"

    def generate_report(self, validation_result: ValidationResult) -> str:
        """Generate human-readable validation report"""

        report = []
        report.append("=" * 50)
        report.append("📋 Schema Validation Report")
        report.append("=" * 50)

        # Overall status
        status = "✅ VALID" if validation_result.is_valid else "❌ INVALID"
        report.append(f"\nStatus: {status}")
        report.append(f"Score: {validation_result.score:.1%}")
        report.append(f"Schema Version: {validation_result.version}")

        # Missing tags
        if validation_result.missing_tags:
            report.append(f"\n❌ Missing Required Tags ({len(validation_result.missing_tags)}):")
            for tag in validation_result.missing_tags:
                report.append(f"  - {tag}")
        else:
            report.append("\n✅ All required tags present")

        # Format issues
        if validation_result.invalid_formats:
            report.append(f"\n❌ Format Issues ({len(validation_result.invalid_formats)}):")
            for issue in validation_result.invalid_formats:
                report.append(f"  - {issue}")

        # Warnings
        if validation_result.warnings:
            report.append(f"\n⚠️ Warnings ({len(validation_result.warnings)}):")
            for warning in validation_result.warnings:
                report.append(f"  - {warning}")

        # Compliance check
        report.append(f"\n📊 PRD Compliance:")
        if validation_result.score >= 0.98:
            report.append("  ✅ Meets ≥98% schema compliance requirement")
        else:
            report.append(f"  ❌ Below 98% compliance (current: {validation_result.score:.1%})")

        return "\n".join(report)


class DomainRouter:
    """Routes prompts to appropriate domain-specific handling"""

    def __init__(self):
        self.domain_keywords = {
            "analytics": [
                "data",
                "analyze",
                "metric",
                "report",
                "insight",
                "trend",
                "statistics",
                "dashboard",
                "kpi",
                "visualization",
            ],
            "coding": [
                "code",
                "function",
                "bug",
                "optimize",
                "api",
                "debug",
                "implement",
                "algorithm",
                "class",
                "method",
                "performance",
            ],
            "content": [
                "write",
                "blog",
                "article",
                "content",
                "document",
                "explain",
                "describe",
                "summary",
                "email",
                "copy",
                "text",
            ],
            "cross_domain": [
                "plan",
                "strategy",
                "process",
                "system",
                "design",
                "build",
                "create",
                "develop",
                "improve",
                "help",
            ],
        }

    def classify_domain(self, prompt: str) -> Tuple[str, float]:
        """Classify prompt into domain with confidence score"""

        prompt_lower = prompt.lower()
        domain_scores = {}

        # Calculate keyword matches for each domain
        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in prompt_lower)
            domain_scores[domain] = score

        # Get domain with highest score
        best_domain = max(domain_scores, key=domain_scores.get)
        max_score = domain_scores[best_domain]

        # Calculate confidence (0.0 to 1.0)
        total_matches = sum(domain_scores.values())
        confidence = max_score / total_matches if total_matches > 0 else 0.0

        # Default to cross_domain if confidence is too low
        if confidence < 0.3:
            return "cross_domain", confidence

        return best_domain, confidence


def main():
    """Test schema validation"""

    # Create validator
    validator = PromptSchemaValidator()
    router = DomainRouter()

    # Test with a sample enhanced prompt
    test_prompt = """<SCHEMA_VERSION>1.2</SCHEMA_VERSION>
<DOMAIN>analytics</DOMAIN>
<OBJECTIVE>Analyze sales data to identify trends and patterns</OBJECTIVE>
<CONTEXT>Working with Q3 2024 sales data from e-commerce platform</CONTEXT>
<REQUIREMENTS>1) Monthly trend analysis 2) Top products 3) Regional breakdown</REQUIREMENTS>
<CONSTRAINTS>Data from last 90 days only, GDPR compliant</CONSTRAINTS>
<OUTPUT_FORMAT>{"summary": "text", "metrics": {}, "charts": []}</OUTPUT_FORMAT>
<EVALUATION_CRITERIA>Statistical accuracy, actionable insights, visual clarity</EVALUATION_CRITERIA>"""

    # Validate
    result = validator.validate(test_prompt)
    report = validator.generate_report(result)
    print(report)

    # Test domain routing
    test_prompts = [
        "Analyze the sales data",
        "Fix the bug in my code",
        "Write a blog post about AI",
        "Help me plan a project",
    ]

    print("\n" + "=" * 50)
    print("🎯 Domain Classification Tests")
    print("=" * 50)

    for prompt in test_prompts:
        domain, confidence = router.classify_domain(prompt)
        print(f"\nPrompt: {prompt}")
        print(f"Domain: {domain} (confidence: {confidence:.1%})")


if __name__ == "__main__":
    main()
