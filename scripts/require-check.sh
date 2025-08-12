#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Require a GitHub check-run via branch protection (dry-run by default).

Usage:
  scripts/require-check.sh --repo <owner/repo> --branch <branch> --check <check-name> [--apply]

Examples:
  bash scripts/require-check.sh --repo owner/repo --branch main --check prompt-gate-ci
  bash scripts/require-check.sh --repo owner/repo --branch main --check prompt-gate-ci --apply

Requirements:
  - gh (GitHub CLI) authenticated with admin rights to the repo
  - jq installed
USAGE
}

REPO=""
BRANCH=""
CHECK=""
APPLY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="$2"; shift 2 ;;
    --branch) BRANCH="$2"; shift 2 ;;
    --check) CHECK="$2"; shift 2 ;;
    --apply) APPLY=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown arg: $1"; usage; exit 1 ;;
  esac
done

if [[ -z "$REPO" || -z "$BRANCH" || -z "$CHECK" ]]; then
  echo "Missing required args." >&2
  usage
  exit 1
fi

command -v gh >/dev/null 2>&1 || { echo "gh CLI not found" >&2; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "jq not found" >&2; exit 1; }

echo "# Inspecting current protection for $REPO@$BRANCH" >&2
set +e
CURR_JSON=$(gh api -H "Accept: application/vnd.github+json" \
  "/repos/$REPO/branches/$BRANCH/protection" 2>/dev/null)
RC=$?
set -e

if [[ $RC -ne 0 || -z "$CURR_JSON" ]]; then
  echo "No existing protection or unable to fetch; will create minimal payload." >&2
  CURR_JSON='{}'
fi

# Build payload preserving existing settings when possible.
PAYLOAD=$(jq -n \
  --argjson curr "$CURR_JSON" \
  --arg check "$CHECK" '
  $curr as $c |
  {
    required_status_checks: (
      {
        strict: ($c.required_status_checks.strict // false),
        contexts: [],
        checks: [ { context: $check } ]
      }
    )
  }
  + (if $c.required_pull_request_reviews then {required_pull_request_reviews: $c.required_pull_request_reviews} else {} end)
  + (if $c.enforce_admins != null then {enforce_admins: $c.enforce_admins.enabled} else {} end)
  + (if $c.restrictions != null then {restrictions: $c.restrictions} else {} end)
  ')

echo "# Proposed payload:" >&2
echo "$PAYLOAD" | jq . >&2

if [[ $APPLY -eq 1 ]]; then
  echo "# Applying protection (requires admin rights)..." >&2
  # Write payload to a temp file to avoid shell quoting issues
  TMP=$(mktemp)
  echo "$PAYLOAD" > "$TMP"
  gh api \
    --method PUT \
    -H "Accept: application/vnd.github+json" \
    "/repos/$REPO/branches/$BRANCH/protection" \
    --input "$TMP"
  rm -f "$TMP"
  echo "# Done." >&2
else
  echo "# Dry-run mode. Use --apply to make changes." >&2
fi

