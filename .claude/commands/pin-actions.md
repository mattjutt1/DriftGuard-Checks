---
allowed-tools: Read(./**), Edit, MultiEdit, Grep(./**), Glob(./**), Bash(rg:*), Bash(jq:*), WebSearch
description: Detect actions not pinned by SHA; propose patches; open PR if approved
---
## Context
- Non-SHA pins: !`rg -n "uses:\s+[^@]+@v[0-9]+" .github/workflows || true`

## Your task
Find non-SHA `uses:`. For each, fetch the release commit SHA, replace, and add a comment with source URL. Stage changes and prepare a PR message; only open a PR after explicit approval.