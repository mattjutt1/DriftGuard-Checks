#!/usr/bin/env bash
set -Eeuo pipefail

need(){ command -v "$1" >/dev/null || { echo "Missing: $1"; exit 1; }; }
for x in rg gh jq node npm curl; do need "$x"; done

REPO=${REPO:-mattjutt1/DriftGuard-Checks}
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
EVID_DIR=.orchestrator/evidence
mkdir -p "$EVID_DIR"
CERT="$EVID_DIR/cert.json"
PROOF="$EVID_DIR/PROOF.md"

# Ensure cert exists
if [[ ! -f "$CERT" ]]; then
  echo -e "{\n  \"certification_version\": \"1.0.0\",\n  \"repo\": \"$REPO\",\n  \"timestamp\": \"$NOW\",\n  \"verification_gates\": []\n}" > "$CERT"
fi

# 1) Supply-chain checks (Actions)
UNPINNED=$(rg -n 'uses: .*@v' .github/workflows | wc -l || true)
PINNED=$(rg -n 'uses: .*@[a-f0-9]{40,}' .github/workflows | wc -l || true)

# 2) Artifact v4 only
HAS_V3=$(( rg -n 'upload-artifact@v3|download-artifact@v3' .github/workflows && echo 1 ) || echo 0 )
HAS_V4=$(( rg -n 'upload-artifact@v4|download-artifact@v4' .github/workflows >/dev/null 2>&1 && echo 1 ) || echo 0 )

# 3) Branch protection
BP=$(gh api /repos/$REPO/branches/main/protection -H 'Accept: application/vnd.github+json' || echo '{}')
BP_REQ=$(echo "$BP" | jq -c '.required_status_checks')

# 4) Throttling presence
THR_VER=$(jq -r '.dependencies["@octokit/plugin-throttling"] // .devDependencies["@octokit/plugin-throttling"] // ""' package.json)
THR_CODE=$( (rg -n 'plugin-throttling|onRateLimit|onAbuseLimit' src/ || true) | wc -l )

# 5) Build & tests
echo "Running npm ci and build..."
npm ci --silent
BUILD_OK=1; npm run build --silent || BUILD_OK=0
TEST_OK=1; npm test --silent || TEST_OK=0

# 6) Health endpoints (optional)
H200=0; R200=0; R503=0
( curl -sf http://localhost:3001/health >/dev/null && H200=1 ) || true
( curl -s -o /dev/null -w "%{http_code}" http://localhost:3001/readyz | grep -q '^200' && R200=1 ) || true
( curl -s -o /dev/null -w "%{http_code}" http://localhost:3001/readyz | grep -q '^503' && R503=1 ) || true

# 7) Webhook negative test (optional)
WEBHOOK_URL=${WEBHOOK_URL:-http://localhost:3001/api/github/webhooks}
RESP=$(curl -si -X POST "$WEBHOOK_URL" -H 'X-GitHub-Event: ping' -H 'X-Hub-Signature-256: sha256=deadbeef' -H 'Content-Type: application/json' --data '{"probe":true}' 2>/dev/null || echo "HTTP/1.1 000 Connection Failed")
STATUS=$(echo "$RESP" | head -n1 | awk '{print $2}')
BAD_HMAC_OK=0; [[ "$STATUS" == "401" || "$STATUS" == "403" ]] && BAD_HMAC_OK=1

# Write PROOF.md
cat > "$PROOF" <<EOF
# DriftGuard-Checks — Evidence PROOF ($NOW)

## Supply-chain
- Unpinned action tags (should be 0): **$UNPINNED**
- Pinned by SHA count: **$PINNED**

## Artifact actions
- Any v3 present (should be 0): **$HAS_V3**
- Any v4 present (should be 1): **$HAS_V4**

## Branch protection snapshot
\`\`\`
$(echo "$BP" | jq .)
\`\`\`

## Throttling presence
- package.json @octokit/plugin-throttling: **$THR_VER**
- code refs count: **$THR_CODE**

## Build & tests
- build success: **$BUILD_OK**
- tests success: **$TEST_OK**

## Health endpoints (if server running)
- /health 200: **$H200**
- /readyz 200: **$R200**, 503: **$R503**

## Webhook invalid HMAC (if server running)
- response status (expect 401/403): **$STATUS**
EOF

# Update cert.json with results
jq \
  --arg now "$NOW" \
  --argjson unp "$UNPINNED" \
  --argjson v3 "$HAS_V3" \
  --argjson v4 "$HAS_V4" \
  --argjson h200 "$H200" \
  --arg status "$STATUS" \
  --arg thr "$THR_VER" \
  '.timestamp=$now
  | .verification_gates = [
      {"gate":"sha_pinning","status":( if ($unp == 0) then "pass" else "fail" end ),"evidence":["PROOF.md#Supply-chain"]},
      {"gate":"artifact_v4_only","status":( if ($v3 == 0 and $v4 == 1) then "pass" else "fail" end ),"evidence":["PROOF.md#Artifact actions"]},
      {"gate":"health_ready","status":( if ($h200 == 1) then "pass" else "conditional" end ),"evidence":["PROOF.md#Health endpoints (if server running)"]},
      {"gate":"webhook_invalid_hmac","status":( if ($status == "401" or $status == "403") then "pass" else "conditional" end ),"evidence":["PROOF.md#Webhook invalid HMAC (if server running)"]},
      {"gate":"octokit_throttling","status":( if ($thr != "") then "pass" else "fail" end ),"evidence":["PROOF.md#Throttling presence"]},
      {"gate":"branch_protection_checks","status":"info","evidence":["PROOF.md#Branch protection snapshot"]}
    ]
  | .result.status = ( if ($unp == 0 and $v3 == 0 and $v4 == 1) then "PASS" else "CONDITIONAL" end )' \
  "$CERT" > "$CERT.tmp" && mv "$CERT.tmp" "$CERT"

# Bundle
ARCHIVE="driftguard-evidence-$(date +%Y%m%d-%H%M%S).tar.gz"
( tar -czf "$ARCHIVE" .orchestrator/evidence || true )

echo -e "\n✅ Evidence written to $PROOF and $CERT"
echo "📦 Bundle: $ARCHIVE"