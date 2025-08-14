---
allowed-tools: Read(./**), Bash(gitleaks:*), Write
description: Run gitleaks secret scan and save JSON
---
## Your task
Run `gitleaks detect -s . -f json -r .orchestrator/evidence/gitleaks.json` and summarize findings. Fail safely (do not delete files).