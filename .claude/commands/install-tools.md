---
allowed-tools: WebSearch, WebFetch, Read(./**), Write, Bash(git:*), Bash(gh:*), Bash(jq:*), Bash(yq:*), Bash(rg:*), Bash(node:*), Bash(npm:*), Bash(actionlint:*), Bash(gitleaks:*), Bash(semgrep:*), Bash(trivy:*), Bash(shellcheck:*), Bash(shfmt:*), Bash(make:*)
description: Install the DriftGuard toolchain (MINIMAL/FULL/CUSTOM) using least-privilege and SHA256-verified binaries
argument-hint: MINIMAL | FULL | CUSTOM [comma-separated tools]
---
## Context
- OS: !`(. /etc/os-release 2>/dev/null; echo ${ID:-unknown})`
- Docker: !`command -v docker >/dev/null && echo yes || echo no`
- Existing versions: !`for t in gh jq yq rg actionlint gitleaks trivy semgrep shellcheck shfmt node npm; do command -v $t >/dev/null && echo \"$t: $($t --version | head -n1)\"; done`

## Your task
Plan then ask for approval to install the requested tool set (default MINIMAL). Use package manager when available; otherwise fetch official binaries **only after** retrieving SHA256 sums with WebFetch and verifying them. Place user binaries in `~/.local/bin`. Keep each step ≤10m; append success lines to `.orchestrator/tooling.log`.