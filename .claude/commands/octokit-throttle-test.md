---
allowed-tools: Bash(node:*), Bash(gh:*)
description: Exercise Octokit throttling callbacks and ensure no 403 under burst
---
## Your task
Burst GitHub API calls (read-only) and verify backoff/retry with logs. Do not mutate repository state.