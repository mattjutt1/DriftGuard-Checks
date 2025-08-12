DriftGuard Probot App
=====================

Minimal Probot app that responds to `/driftguard run <dataset>` on pull requests and creates a stub GitHub Check Run with a short summary.

Setup
- Create a GitHub App (Settings → Developer settings → GitHub Apps):
  - Webhook: your dev tunnel (e.g. smee) or deployment URL
  - Permissions (minimum):
    - Checks: Read & write
    - Pull requests: Read
    - Issues: Read & write (to reply to the command)
    - Contents: Read
  - Subscribe to events: Issue comment
  - Install the app on this repository

Local dev
1) Copy `.env.example` to `.env` and fill values
2) Install deps: `npm install`
3) Start: `npm start`

Usage
- Comment on a PR: `/driftguard run smoke-dataset`
- The app creates a `driftguard-run` Check Run on the PR head SHA and replies to the comment.

Notes
- This is a stub; replace the check run body with real evaluation logic and links to artifacts.
- Requires Node 18+.

