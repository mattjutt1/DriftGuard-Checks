Datasets
========

Add dataset JSON files in this directory to be validated in CI.

Schema
- Schema lives at `schemas/dataset.schema.json` (Draft 2020-12)
- Minimal example:

```
{
  "name": "example",
  "description": "Sample dataset for CI validation",
  "items": [
    {"id": "1", "input": "hello", "expected": "world", "tags": ["smoke"]}
  ]
}
```

CI Validation
- On PRs touching `datasets/*.json`, CI validates with `ajv-cli` and falls back to Python `jsonschema` if needed.
- Validation errors point to the offending field for quick fixes.

