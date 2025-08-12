Branch Protection for Prompt Gate
=================================

Goal
- Require the CI check-run `prompt-gate-ci` on PRs to `main`, while keeping legacy status check contexts empty.

UI Steps
- Settings → Branches → Branch protection rules → Add rule
- Branch name pattern: `main` (adjust if different)
- Enable:
  - Require a pull request before merging
  - Require status checks to pass before merging
- In Status checks section:
  - Required status checks (contexts): leave empty []
  - Required check runs: add `prompt-gate-ci`
- Save changes.

Notes
- The required check name must exactly match the GitHub Actions job id: `prompt-gate-ci`.
- Keep legacy “contexts” empty to avoid conflicts with other workflows.
- If protection is already configured, just add the `prompt-gate-ci` check run entry.

CLI (optional)
- See `scripts/require-check.sh` for a helper using `gh api`.
- Dry run example:
  - `bash scripts/require-check.sh --repo <owner/repo> --branch main --check prompt-gate-ci`
- Apply changes (requires admin permissions):
  - `bash scripts/require-check.sh --repo <owner/repo> --branch main --check prompt-gate-ci --apply`

