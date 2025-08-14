---
allowed-tools: Bash(gh:*), Bash(jq:*), Read(./**), Write
description: End-to-end smoke test of DriftGuard check run
---
## Context
- Default branch: !`git rev-parse --abbrev-ref origin/HEAD | cut -d/ -f2`

## Your task
Create a temp branch, open a PR, run the example workflow to upload `driftguard-capsule.json`, then verify that a DriftGuard check run appears. Clean up afterward.