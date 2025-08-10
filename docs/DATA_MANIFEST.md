# Data Manifest - PromptEvolver 3.0

**PROPRIETARY AND CONFIDENTIAL**
Copyright (c) 2025 Matthew J. Utt. All Rights Reserved.

## Overview

This document tracks all datasets used in the PromptEvolver 3.0 training pipeline, including provenance, licensing, and usage restrictions.

## Dataset Categories

### 1. Public Datasets (Commercial Use Allowed)

| Dataset | Source | License | Size | Usage | Verification |
|---------|--------|---------|------|-------|--------------|
| Example | Source URL | Apache 2.0 | 10K samples | Stage 1 Training | ✅ Verified |
| TBD | TBD | TBD | TBD | TBD | ⏳ Pending |

### 2. Synthetic Datasets (Generated)

| Dataset | Generation Method | Size | Domain | Stage | Status |
|---------|------------------|------|--------|-------|--------|
| seed_pairs | PromptWizard | 5K | Mixed | Stage 1 | ⏳ To Generate |
| domain_specific | Custom | 10K | Analytics/Coding/Content | Stage 2 | ⏳ To Generate |
| negative_examples | Rule-based | 2K | All | Validation | ⏳ To Generate |

### 3. Proprietary Datasets (Internal)

| Dataset | Source | Size | Purpose | Access Control |
|---------|--------|------|---------|----------------|
| customer_feedback | Production | TBD | Fine-tuning | Encrypted |
| a_b_test_results | Production | TBD | Evaluation | Restricted |

## Domain Distribution

Target distribution across domains:

- **Analytics**: 25%
- **Coding**: 25%
- **Content**: 25%
- **Cross-Domain**: 25%

## Data Pipeline Stages

### Stage 1: Foundational (30K samples)

- Public instruction datasets
- Basic prompt-response pairs
- General knowledge coverage

### Stage 2: Specialization (20K samples)

- Domain-specific optimization
- PromptWizard-generated pairs
- Negative examples (20%)

### Stage 3: Reasoning (10K samples)

- Chain-of-thought examples
- Multi-step reasoning
- GSM8K subset (optional)

## License Verification

All datasets must pass commercial use verification:

```python
python scripts/verify_licenses.py --manifest DATA_MANIFEST.md
```

## Quality Metrics

Target metrics per dataset:

- Schema compliance: ≥98%
- Domain balance: Within 5% of target
- Duplicate rate: <2%
- Quality score: ≥0.8

## Data Security

- All datasets stored in `data/` directory
- Sensitive data encrypted at rest
- Access logs maintained
- No customer PII in training data

## Compliance Checklist

- [ ] All datasets have verified licenses
- [ ] No PII or sensitive information
- [ ] Domain distribution meets targets
- [ ] Quality metrics achieved
- [ ] Security measures implemented
- [ ] Provenance documented
- [ ] Reproducibility ensured

## Update Log

| Date | Action | Datasets Affected | Reviewer |
|------|--------|------------------|----------|
| 2025-08-07 | Initial manifest created | All | Matthew J. Utt |

---

**Note**: This manifest must be updated whenever datasets are added, modified, or removed from the training pipeline.
