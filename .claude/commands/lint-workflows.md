---
allowed-tools: Read(./**), Bash(actionlint:*)
description: Lint GitHub Actions workflows with actionlint before pushing or merging
---
## Context
- Workflow files: !`ls -1 .github/workflows/*.yml 2>/dev/null || echo none`

## Your task
Run `actionlint` and report any findings with line numbers and remediation.