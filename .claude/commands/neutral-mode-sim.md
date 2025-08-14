---
allowed-tools: Bash(gh:*), Read(./**)
description: Simulate missing artifact to confirm neutral check
---
## Your task
Trigger a workflow without uploading the artifact and verify the app posts a `conclusion: neutral` check that does not block merger.