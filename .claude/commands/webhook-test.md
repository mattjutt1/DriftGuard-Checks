---
allowed-tools: Bash(node:*), Bash(curl:*)
description: Send invalid webhook signatures to confirm 401/403
---
## Your task
Start the local app, then POST with an invalid `X-Hub-Signature-256` and expect a 401/403. Log results to `.orchestrator/evidence/webhook-negative.log`.