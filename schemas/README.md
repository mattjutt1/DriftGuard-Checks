# PromptEvolver 3.0 Schemas

This directory contains JSON schemas for the PromptEvolver 3.0 training system.

## Engineered Prompt Schema

### File: `engineered_prompt.schema.json`

**Purpose**: Defines the structure for engineered prompt training data and API responses in PromptEvolver 3.0.

**Schema Version**: 1.0
**JSON Schema Draft**: 2020-12
**Copyright**: Matthew J. Utt 2025

### Supported Domains

- **Analytics**: Business intelligence, data analysis, reporting prompts
- **Coding**: Programming, software development, technical documentation
- **Content**: Marketing, writing, creative content generation
- **Cross-Domain**: Multi-disciplinary prompts spanning multiple domains

### Key Features

#### Quality Scoring (7 Dimensions)

- **Clarity**: How clear and unambiguous the prompt is (0.0-1.0)
- **Specificity**: How specific and detailed the requirements are (0.0-1.0)
- **Engagement**: How engaging and motivating the prompt is (0.0-1.0)
- **Structure**: How well-organized and logically structured (0.0-1.0)
- **Completeness**: How complete and comprehensive (0.0-1.0)
- **Error Prevention**: How well it prevents mistakes (0.0-1.0)
- **Overall**: Composite quality score (0.0-1.0)

#### Follow-up Questions Mechanism

Supports up to 5 follow-up questions with purpose classification:

- `clarification`: Questions to clarify ambiguous requirements
- `context`: Questions to understand the broader context
- `specificity`: Questions to make requirements more specific
- `constraints`: Questions about limitations or restrictions
- `audience`: Questions about the target audience
- `format`: Questions about output format requirements
- `examples`: Questions requesting examples or samples
- `validation`: Questions about success criteria

#### Metadata Tracking

- Processing timestamps
- Expert identity assignment
- Optimization configuration parameters
- Detailed reasoning explanations
- Improvement area documentation

### Usage

#### Validation

Use the provided validation script:

```bash
source venv/bin/activate
python validate_schema.py
```

#### Integration

Import the schema in your application:

```python
import json
import jsonschema

# Load schema
with open('schemas/engineered_prompt.schema.json', 'r') as f:
    schema = json.load(f)

# Validate data
validator = jsonschema.Draft202012Validator(schema)
validator.validate(your_data)
```

### Example Data Structure

```json
{
  "originalPrompt": "Write a summary of the quarterly report",
  "enhancedPrompt": "As a senior business analyst...",
  "domain": "Analytics",
  "metadata": {
    "qualityScore": {
      "overall": 0.92,
      "clarity": 0.95,
      "specificity": 0.90,
      "engagement": 0.88,
      "structure": 0.94,
      "completeness": 0.91,
      "errorPrevention": 0.89
    },
    "improvementAreas": [...],
    "processingTimestamp": 1735689600,
    "expertIdentity": "Senior Business Analyst",
    "reasoning": "The original prompt was enhanced..."
  },
  "followUpQuestions": [...],
  "tags": ["business-analysis", "reporting"],
  "version": "1.0"
}
```

### Schema Validation Results

✅ **All validation tests pass**
✅ **7 quality metric dimensions**
✅ **4 supported domains**
✅ **5 follow-up question types**
✅ **Comprehensive examples included**
✅ **Ready for production use**

### Integration Points

This schema integrates with:

- PromptEvolver 3.0 training pipeline
- Convex database schema
- API response formatting
- Quality assessment algorithms
- Machine learning training data preparation

### Versioning

The schema includes version tracking to support future evolution:

- **v1.0**: Initial release with core functionality
- Future versions will maintain backward compatibility

---

*Copyright (c) 2025 Matthew J. Utt. Part of the PromptEvolver 3.0 training system.*
