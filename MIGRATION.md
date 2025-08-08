# Migration Guide: PromptWizard → PromptOps

## Overview

We're evolving from a CLI-based prompt evaluation tool to a comprehensive Prompt Operations platform with two surfaces:

1. **DriftGuard** (Platform): FastAPI service for prompt registry, drift monitoring, and budget management
2. **PromptOps SDK** (Library): Lightweight Python package with CLI for local evaluation and CI/CD

## Why the Pivot?

- **ROI Focus**: Workflow, compliance, and cost control deliver measurable business value
- **Market Differentiation**: Eval-only tools commoditize; Prompt Ops creates a moat
- **Enterprise Ready**: CI/CD gates, drift monitoring, and budget controls meet enterprise needs

## Migration Steps

### For CLI Users

The `promptwizard` command is deprecated but still works with a warning. Migrate to `promptops`:

```bash
# Old (deprecated)
promptwizard eval "Your prompt"

# New
promptops eval "Your prompt"
```

### For Python SDK Users

```python
# Old (if using internal APIs)
from promptwizard import evaluate_prompt

# New
from promptops import Evaluator, Config

config = Config()
evaluator = Evaluator(config)
result = evaluator.evaluate_prompt("Your prompt")
```

### For CI/CD Pipelines

Update your GitHub Actions or CI configuration:

```yaml
# Old workflow (if any)
- run: promptwizard evaluate --threshold 0.8

# New workflow
- run: promptops ci --config .promptops.yml --out results.json
```

### New Features Available

1. **Prompt Registry**: Register and version your prompts
2. **Drift Monitoring**: Track prompt performance over time
3. **Cost Budgets**: Set and monitor cost/latency limits
4. **CI Gates**: Automated quality checks in PR workflows

## Configuration Changes

### Old Format (if any)

```yaml
# promptwizard.yml
threshold: 0.8
prompts:
  - "Test prompt"
```

### New Format

```yaml
# .promptops.yml
version: "1.0"
threshold: 0.85
model: "mock"
test_prompts:
  - "Test prompt"
evaluation:
  metrics: ["clarity", "specificity", "completeness"]
  timeout: 30
```

## API Migration (for Platform Users)

The new DriftGuard platform provides REST APIs:

```bash
# Register a prompt
curl -X POST http://localhost:8000/api/v1/prompts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_prompt",
    "version": "1.0.0",
    "template": "Generate {type} for {topic}"
  }'

# Check drift
curl -X POST http://localhost:8000/api/v1/drift/check \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_id": "my_prompt",
    "version": "1.0.0",
    "drift_score": 0.15
  }'
```

## Backward Compatibility

- The `promptwizard` CLI command remains available with deprecation warning
- Existing evaluation logic preserved in the new SDK
- Zero breaking changes for basic evaluation workflows

## Support

For questions or issues during migration:

- Open an issue on GitHub
- Check the updated documentation in `/platform/README.md` and `/library/README.md`

## Timeline

- **Phase 1** (Current): Both commands work, deprecation warnings shown
- **Phase 2** (Q2 2025): `promptwizard` command removed, full migration required
- **Phase 3** (Q3 2025): Enhanced platform features, enterprise integrations
