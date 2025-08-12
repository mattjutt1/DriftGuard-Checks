#!/usr/bin/env python3
"""
Schema validation script for engineered_prompt.schema.json
Copyright (c) 2025 Matthew J. Utt

This script validates the engineered prompt JSON schema against sample data
to ensure the schema is correctly defined and functional.
"""

import json
from pathlib import Path

import jsonschema


def load_schema():
    """Load the engineered prompt schema"""
    schema_path = Path("schemas/engineered_prompt.schema.json")
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with open(schema_path, "r") as f:
        return json.load(f)


def create_sample_data():
    """Create sample data for validation testing"""
    return [
        {
            "originalPrompt": "Write a Python function to sort data",
            "enhancedPrompt": "As an experienced Python developer, create a comprehensive sorting function that handles multiple data types. Requirements: 1) Accept list/tuple input, 2) Support custom sort keys via lambda functions, 3) Handle edge cases (empty lists, None values), 4) Include type hints and docstring with examples, 5) Implement both ascending/descending options, 6) Add error handling for invalid inputs. Format: Complete function with unit tests. Target: intermediate Python developers. Style: PEP 8 compliant with clear variable names.",
            "domain": "Coding",
            "metadata": {
                "qualityScore": {
                    "overall": 0.89,
                    "clarity": 0.92,
                    "specificity": 0.91,
                    "engagement": 0.85,
                    "structure": 0.88,
                    "completeness": 0.90,
                    "errorPrevention": 0.87,
                },
                "improvementAreas": [
                    "Added specific role context (experienced Python developer)",
                    "Defined comprehensive requirements with numbered list",
                    "Specified target audience (intermediate Python developers)",
                    "Added style and formatting requirements (PEP 8)",
                    "Enhanced with unit testing requirement",
                ],
                "processingTimestamp": 1735689600,
                "expertIdentity": "Senior Python Developer",
                "optimizationConfig": {
                    "iterations": 3,
                    "rounds": 3,
                    "temperature": 0.7,
                    "generateReasoning": True,
                    "generateExpertIdentity": True,
                },
                "reasoning": "The original prompt was too basic and lacked technical depth. I enhanced it by adding professional context, comprehensive requirements, error handling considerations, and code quality standards that would produce production-ready code suitable for intermediate developers.",
            },
            "followUpQuestions": [
                {"question": "What specific data types should the function prioritize?", "purpose": "specificity"},
                {"question": "Should the function handle large datasets efficiently?", "purpose": "constraints"},
            ],
            "tags": ["python", "coding", "sorting", "data-structures", "functions"],
            "version": "1.0",
        },
        {
            "originalPrompt": "Create content for social media",
            "enhancedPrompt": "As a digital marketing specialist with expertise in social media engagement, create a comprehensive content strategy for our B2B SaaS product launch. Deliverables: 1) 5 LinkedIn posts (professional tone, 150-200 words each), 2) 3 Twitter threads (casual, engaging, with relevant hashtags), 3) 1 detailed blog post outline (1500 words, SEO-optimized), 4) Content calendar scheduling recommendations. Focus: thought leadership, product benefits, customer success stories. Target audience: decision-makers in mid-market companies. Include CTAs and engagement hooks. Brand voice: knowledgeable yet approachable.",
            "domain": "Content",
            "metadata": {
                "qualityScore": {
                    "overall": 0.94,
                    "clarity": 0.96,
                    "specificity": 0.95,
                    "engagement": 0.93,
                    "structure": 0.94,
                    "completeness": 0.92,
                    "errorPrevention": 0.91,
                },
                "improvementAreas": [
                    "Added specific expert role (digital marketing specialist)",
                    "Defined comprehensive deliverables with quantities and specifications",
                    "Specified target audience and brand voice",
                    "Included strategic elements (SEO, CTAs, engagement hooks)",
                    "Added content calendar planning component",
                ],
                "processingTimestamp": 1735689700,
                "expertIdentity": "Digital Marketing Specialist",
            },
            "followUpQuestions": [
                {"question": "What are the key differentiators of your SaaS product?", "purpose": "context"},
                {"question": "Do you have existing brand guidelines for tone and style?", "purpose": "constraints"},
            ],
            "tags": ["content-marketing", "social-media", "b2b", "saas", "digital-marketing"],
            "version": "1.0",
        },
    ]


def validate_schema(schema, sample_data):
    """Validate sample data against the schema"""
    print("🔍 Validating engineered prompt schema...")
    print(f"📋 Schema: {schema.get('title', 'Unknown')}")
    print(f"🌐 Schema ID: {schema.get('$id', 'Unknown')}")
    print(f"📄 Description: {schema.get('description', 'No description')}")
    print()

    try:
        # Validate the schema itself
        jsonschema.Draft202012Validator.check_schema(schema)
        print("✅ Schema structure is valid")

        # Create validator
        validator = jsonschema.Draft202012Validator(schema)

        # Test each sample
        for i, sample in enumerate(sample_data, 1):
            print(f"\n🧪 Testing sample {i}...")
            print(f"   Domain: {sample.get('domain', 'Unknown')}")
            print(f"   Original: {sample.get('originalPrompt', 'Unknown')[:50]}...")

            try:
                validator.validate(sample)
                print(f"   ✅ Sample {i} passed validation")
            except jsonschema.exceptions.ValidationError as e:
                print(f"   ❌ Sample {i} failed validation:")
                print(f"      Error: {e.message}")
                print(f"      Path: {' -> '.join(str(p) for p in e.path) if e.path else 'root'}")
                return False

    except jsonschema.exceptions.SchemaError as e:
        print(f"❌ Schema is invalid: {e.message}")
        return False
    except Exception as e:
        print(f"❌ Validation error: {str(e)}")
        return False

    print(f"\n🎉 All {len(sample_data)} samples passed validation!")
    print("📊 Schema validation summary:")
    print(f"   • Supported domains: {', '.join(schema['properties']['domain']['enum'])}")
    print(
        f"   • Quality metrics: {len(schema['properties']['metadata']['properties']['qualityScore']['properties'])} dimensions"
    )
    print(f"   • Follow-up questions: Up to {schema['properties']['followUpQuestions']['maxItems']} questions")
    print(f"   • Schema version: {schema['properties']['version']['default']}")

    return True


def main():
    """Main validation function"""
    try:
        # Load schema and sample data
        schema = load_schema()
        sample_data = create_sample_data()

        # Validate
        success = validate_schema(schema, sample_data)

        if success:
            print("\n✨ Schema validation completed successfully!")
            print("🚀 Ready for use in PromptEvolver 3.0 training system")
            return 0
        else:
            print("\n💥 Schema validation failed!")
            return 1

    except Exception as e:
        print(f"💥 Validation script error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())
