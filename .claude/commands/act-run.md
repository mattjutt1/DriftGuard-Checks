---
allowed-tools: Bash(act:*), Read(./**)
description: Run a named GitHub Actions workflow locally via act
argument-hint: [workflow-name]
---
## Your task
Execute `act -W .github/workflows/$ARGUMENTS` and stream results.