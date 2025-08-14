---
allowed-tools: Read(./**), Write, WebSearch, Bash(rg:*), Bash(jq:*), Bash(yq:*), Bash(actionlint:*), Bash(gitleaks:*), Bash(semgrep:*), Bash(trivy:*), Bash(gh:*)
description: Verify toolchain, capture versions, lint workflows, and emit JSON evidence
---
## Context
- Targets: versions, actionlint, artifact@v4, pinned SHAs, secret/SAST/vuln scans

## Your task
1) Capture versions to `.orchestrator/runlog.jsonl`.
2) `actionlint` on `.github/workflows/*.yml`.
3) `rg` to ensure `upload-artifact@v4`/`download-artifact@v4` and **no** `@v3`.
4) `rg` to detect `uses:` not pinned to a 40-hex SHA; summarize.
5) Run `gitleaks`, `semgrep`, `trivy fs .` and write JSON outputs to `.orchestrator/evidence/`.