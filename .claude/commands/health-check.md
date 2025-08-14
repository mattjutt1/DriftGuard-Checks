---
allowed-tools: Bash(curl:*)
description: Probe /healthz and /readyz endpoints and print JSON
---
## Your task
`curl -s http://localhost:3000/healthz; curl -s http://localhost:3000/readyz` and summarize status/uptime/connectivity.