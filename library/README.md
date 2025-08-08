# PromptOps SDK

Lightweight Python package and CLI for prompt evaluation and CI/CD.

## Installation

```bash
cd library/
pip install -e .[dev]
```

## CLI Usage

```bash
# Initialize config
promptops init

# Run CI evaluation
promptops ci --config .promptops.yml --out results.json

# Evaluate single prompt
promptops eval "Write a Python function"

# Legacy alias (deprecated)
promptwizard ci  # Shows deprecation warning
```

## Python SDK Usage

```python
from promptops import Evaluator, Config

# Load config
config = Config.from_yaml(".promptops.yml")

# Create evaluator
evaluator = Evaluator(config)

# Evaluate prompt
result = evaluator.evaluate_prompt("Your prompt here")
print(f"Score: {result['score']}")

# Run CI evaluation
ci_results = evaluator.run_ci_evaluation()
if ci_results["pass"]:
    print("CI passed!")
```

## Testing

```bash
make test
```
