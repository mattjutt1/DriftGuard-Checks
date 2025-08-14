# DriftGuard-Checks — Evidence PROOF (2025-08-13T01:44:37Z)

## Supply-chain
- Unpinned action tags (should be 0): **0**
- Pinned by SHA count: **8**

## Artifact actions
- Any v3 present (should be 0): **0**
- Any v4 present (should be 1): **0**

## Branch protection snapshot
```
{
  "url": "https://api.github.com/repos/mattjutt1/DriftGuard-Checks/branches/main/protection",
  "required_status_checks": {
    "url": "https://api.github.com/repos/mattjutt1/DriftGuard-Checks/branches/main/protection/required_status_checks",
    "strict": true,
    "contexts": [
      "test",
      "Analyze (javascript)"
    ],
    "contexts_url": "https://api.github.com/repos/mattjutt1/DriftGuard-Checks/branches/main/protection/required_status_checks/contexts",
    "checks": [
      {
        "context": "test",
        "app_id": 15368
      },
      {
        "context": "Analyze (javascript)",
        "app_id": 15368
      }
    ]
  },
  "required_pull_request_reviews": {
    "url": "https://api.github.com/repos/mattjutt1/DriftGuard-Checks/branches/main/protection/required_pull_request_reviews",
    "dismiss_stale_reviews": false,
    "require_code_owner_reviews": false,
    "require_last_push_approval": false,
    "required_approving_review_count": 1
  },
  "required_signatures": {
    "url": "https://api.github.com/repos/mattjutt1/DriftGuard-Checks/branches/main/protection/required_signatures",
    "enabled": false
  },
  "enforce_admins": {
    "url": "https://api.github.com/repos/mattjutt1/DriftGuard-Checks/branches/main/protection/enforce_admins",
    "enabled": true
  },
  "required_linear_history": {
    "enabled": false
  },
  "allow_force_pushes": {
    "enabled": false
  },
  "allow_deletions": {
    "enabled": false
  },
  "block_creations": {
    "enabled": false
  },
  "required_conversation_resolution": {
    "enabled": false
  },
  "lock_branch": {
    "enabled": false
  },
  "allow_fork_syncing": {
    "enabled": false
  }
}
```

## Throttling presence
- package.json @octokit/plugin-throttling: **^11.0.1**
- code refs count: **3**

## Build & tests
- build success: **1**
- tests success: **0**

## Health endpoints (if server running)
- /health 200: **0**
- /readyz 200: **0**, 503: **0**

## Webhook invalid HMAC (if server running)
- response status (expect 401/403): **404**
