---
allowed-tools: Bash(gh:*), Read(./**)
description: Apply minimal branch protection (Test + CodeQL; optional DriftGuard)
---
## Your task
PUT `bp.minimal.json` via `gh api -X PUT /repos/:owner/:repo/branches/main/protection --input bp.minimal.json`, then GET and summarize. Ask before applying.