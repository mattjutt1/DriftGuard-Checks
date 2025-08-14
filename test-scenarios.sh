#!/bin/bash
# E2E Scenario Testing for DriftGuard-Checks
# Tests PASS/NEUTRAL/FAIL scenarios with mock data

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎭 DriftGuard-Checks Scenario Testing${NC}"
echo "===================================="
echo ""

# Test scenario data
create_mock_evaluation() {
    local win_rate=$1
    local threshold=$2
    local scenario_name=$3
    
    cat > "mock-evaluation-${scenario_name}.json" <<EOF
{
  "metrics": {
    "win_rate": ${win_rate}
  },
  "threshold": ${threshold},
  "scenario": "${scenario_name}",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF
}

# Scenario 1: PASS - Win rate above threshold
echo -e "${GREEN}Scenario 1: PASS (Win Rate Above Threshold)${NC}"
echo "--------------------------------------------"
create_mock_evaluation 0.85 0.80 "pass"
echo "Created mock evaluation: win_rate=0.85, threshold=0.80"
echo "Expected outcome: ✅ SUCCESS conclusion, merge allowed"
echo "Mock data: mock-evaluation-pass.json"
echo ""

# Scenario 2: NEUTRAL - Win rate below threshold  
echo -e "${YELLOW}Scenario 2: NEUTRAL (Win Rate Below Threshold)${NC}"
echo "----------------------------------------------"
create_mock_evaluation 0.75 0.80 "neutral"
echo "Created mock evaluation: win_rate=0.75, threshold=0.80"
echo "Expected outcome: ⚠️ NEUTRAL conclusion, informational only"
echo "Mock data: mock-evaluation-neutral.json"
echo ""

# Scenario 3: FAIL - Missing artifact
echo -e "${RED}Scenario 3: FAIL (Missing Artifact)${NC}"
echo "-----------------------------------"
echo "Simulated condition: No evaluation artifact found"
echo "Expected outcome: ❌ FAILURE conclusion, clear error message"
echo "Error type: ERROR / MISSING_ARTIFACT"
echo ""

# Scenario 4: FAIL - API Error
echo -e "${RED}Scenario 4: FAIL (API Error)${NC}"
echo "-----------------------------"
echo "Simulated condition: GitHub API rate limiting or network error"
echo "Expected outcome: ❌ FAILURE conclusion with error boundary handling"
echo "Error type: ERROR / EVALUATION_FETCH_FAILED"
echo ""

# Scenario 5: CRITICAL FAIL - Complete system failure
echo -e "${RED}Scenario 5: CRITICAL FAIL (System Error)${NC}"
echo "------------------------------------------"
echo "Simulated condition: Unexpected system-level error"
echo "Expected outcome: ❌ FAILURE with critical error message"
echo "Error type: ERROR / CRITICAL_FAILURE"
echo ""

# Create test data for webhook simulation
echo -e "${BLUE}🔧 Test Data Generation${NC}"
echo "========================"

# Create sample webhook payloads
cat > "webhook-payload-pr-opened.json" <<EOF
{
  "action": "opened",
  "pull_request": {
    "number": 1,
    "head": {
      "sha": "test-sha-123456789abcdef"
    },
    "base": {
      "repo": {
        "name": "DriftGuard-Checks",
        "owner": {
          "login": "mattjutt1"
        }
      }
    }
  }
}
EOF

cat > "webhook-payload-workflow-completed.json" <<EOF
{
  "action": "completed",
  "workflow_run": {
    "id": 12345678,
    "head_sha": "test-sha-123456789abcdef",
    "head_branch": "feature/test-branch",
    "conclusion": "success",
    "html_url": "https://github.com/mattjutt1/DriftGuard-Checks/actions/runs/12345678"
  }
}
EOF

echo "✅ Generated webhook payload samples:"
echo "   - webhook-payload-pr-opened.json (pull_request.opened event)"
echo "   - webhook-payload-workflow-completed.json (workflow_run.completed event)"
echo ""

# Create test artifacts
echo -e "${BLUE}📦 Test Artifacts${NC}"
echo "================"

# Create ZIP artifact with evaluation results (simulating GitHub Actions artifact)
mkdir -p test-artifacts
cp mock-evaluation-pass.json test-artifacts/results.json
cd test-artifacts && zip -q "../test-artifact-pass.zip" results.json && cd ..

cp mock-evaluation-neutral.json test-artifacts/results.json  
cd test-artifacts && zip -q "../test-artifact-neutral.zip" results.json && cd ..

echo "✅ Generated test artifacts:"
echo "   - test-artifact-pass.zip (contains passing evaluation)"
echo "   - test-artifact-neutral.zip (contains neutral evaluation)"
echo ""

# Test execution guide
echo -e "${BLUE}🧪 Test Execution Guide${NC}"
echo "======================="
echo ""
echo "To test different scenarios:"
echo ""
echo "1. ${GREEN}PASS Scenario${NC}:"
echo "   - Use test-artifact-pass.zip as mock evaluation"
echo "   - Expected: Green check, merge allowed"
echo ""
echo "2. ${YELLOW}NEUTRAL Scenario${NC}:"
echo "   - Use test-artifact-neutral.zip as mock evaluation"  
echo "   - Expected: Yellow warning, informational only"
echo ""
echo "3. ${RED}FAIL Scenarios${NC}:"
echo "   - Missing artifact: No ZIP file available"
echo "   - API error: Simulate network/rate limit issues"
echo "   - Critical error: Unexpected system failures"
echo ""
echo "Test files created:"
ls -la mock-evaluation-*.json webhook-payload-*.json test-artifact-*.zip 2>/dev/null || echo "Some files may not have been created"
echo ""

# Validation checklist
echo -e "${BLUE}✅ Validation Checklist${NC}"
echo "====================="
echo ""
echo "For each scenario, verify:"
echo "□ Correct check run conclusion (success/neutral/failure)"
echo "□ Appropriate emoji and status message"
echo "□ Error boundaries prevent cascading failures"
echo "□ Structured logging captures all events"
echo "□ Health endpoints remain responsive"
echo "□ Memory usage stays within bounds"
echo "□ No sensitive data in logs"
echo ""

echo -e "${GREEN}🎯 Scenario testing setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Run the main E2E smoke test: ./e2e-smoke-test.sh"
echo "2. Use these test files to manually verify scenarios"
echo "3. Monitor logs during testing for proper event capture"

# Cleanup function
cleanup_test_files() {
    echo "Cleaning up test files..."
    rm -f mock-evaluation-*.json
    rm -f webhook-payload-*.json  
    rm -f test-artifact-*.zip
    rm -rf test-artifacts
    echo "Test files cleaned up."
}

# Optionally clean up (uncomment to auto-cleanup)
# cleanup_test_files