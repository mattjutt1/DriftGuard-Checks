---
allowed-tools: Read(./**), Bash(trivy:*), Write
description: Run Trivy filesystem scan and write trivy.json
---
## Your task
Run `trivy fs --security-checks vuln,secret,misconfig --format json --output .orchestrator/evidence/trivy.json .` and summarize CVEs by severity.