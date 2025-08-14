---
allowed-tools: Bash(gh:*), Write, Read(./**)
description: Backup main branch protection to bp.backup.json
---
## Your task
Run `gh api /repos/:owner/:repo/branches/main/protection > .orchestrator/evidence/bp.backup.json` and print a concise summary of required checks.