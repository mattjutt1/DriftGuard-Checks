---
allowed-tools: Read(./**), Bash(semgrep:*), Write
description: Run Semgrep with default ruleset and write semgrep.json
---
## Your task
Execute `semgrep ci --json --output .orchestrator/evidence/semgrep.json || semgrep --json -o .orchestrator/evidence/semgrep.json .` and summarize top findings.