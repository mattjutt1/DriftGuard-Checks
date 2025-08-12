#!/bin/bash

# =============================================================================
# PromptEvolver CLI Comprehensive Testing Framework
# Executes complete test suite with quality analysis and evidence generation
# =============================================================================

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
VENV_PATH="$PROJECT_ROOT/venv"
REPORTS_DIR="$PROJECT_ROOT/tests/reports"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
EVIDENCE_FILE="$REPORTS_DIR/test_evidence_$TIMESTAMP.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_section() {
    echo -e "\n${PURPLE}======================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}======================================${NC}\n"
}

# Initialize test environment
initialize_environment() {
    log_section "INITIALIZING TEST ENVIRONMENT"

    cd "$PROJECT_ROOT"

    # Activate virtual environment
    if [[ -f "$VENV_PATH/bin/activate" ]]; then
        log_info "Activating virtual environment..."
        source "$VENV_PATH/bin/activate"
    else
        log_error "Virtual environment not found at $VENV_PATH"
        exit 1
    fi

    # Create reports directory
    mkdir -p "$REPORTS_DIR"

    # Install package in development mode
    log_info "Installing package in development mode..."
    pip install -e . > /dev/null 2>&1

    log_success "Environment initialized successfully"
}

# Run pytest with comprehensive coverage
run_pytest_suite() {
    log_section "RUNNING PYTEST COMPREHENSIVE SUITE"

    log_info "Starting pytest execution with full coverage analysis..."

    # Run pytest with all configured options
    pytest \
        --verbose \
        --tb=short \
        --cov=promptevolver_cli \
        --cov-report=html:tests/reports/coverage_html \
        --cov-report=json:tests/reports/coverage.json \
        --cov-report=term-missing \
        --cov-fail-under=80 \
        --html=tests/reports/pytest_report_$TIMESTAMP.html \
        --self-contained-html \
        --json-report \
        --json-report-file=tests/reports/pytest_report_$TIMESTAMP.json \
        tests/ \
        || {
            log_error "Pytest execution failed"
            return 1
        }

    log_success "Pytest suite completed successfully"
}

# Run code quality analysis
run_code_quality_analysis() {
    log_section "RUNNING CODE QUALITY ANALYSIS"

    # Run pylint
    log_info "Running pylint analysis..."
    pylint promptevolver_cli/ --output-format=json > "$REPORTS_DIR/pylint_report_$TIMESTAMP.json" 2>/dev/null || {
        log_warning "Pylint completed with warnings (see report for details)"
    }

    # Generate pylint summary
    pylint promptevolver_cli/ --output-format=text > "$REPORTS_DIR/pylint_summary_$TIMESTAMP.txt" 2>/dev/null || true

    # Run mypy type checking
    log_info "Running mypy type checking..."
    mypy promptevolver_cli/ --json-report "$REPORTS_DIR/mypy_report_$TIMESTAMP" --html-report "$REPORTS_DIR/mypy_html_$TIMESTAMP" || {
        log_warning "MyPy type checking completed with issues (see report for details)"
    }

    # Run black code formatting check
    log_info "Running black code formatting check..."
    black --check --diff promptevolver_cli/ > "$REPORTS_DIR/black_report_$TIMESTAMP.txt" 2>&1 || {
        log_warning "Code formatting issues found (see black report)"
    }

    # Run radon complexity analysis
    log_info "Running radon complexity analysis..."
    radon cc promptevolver_cli/ --json > "$REPORTS_DIR/radon_complexity_$TIMESTAMP.json"
    radon mi promptevolver_cli/ --json > "$REPORTS_DIR/radon_maintainability_$TIMESTAMP.json"
    radon hal promptevolver_cli/ --json > "$REPORTS_DIR/radon_halstead_$TIMESTAMP.json"

    # Run bandit security analysis
    log_info "Running bandit security analysis..."
    bandit -r promptevolver_cli/ -f json -o "$REPORTS_DIR/bandit_security_$TIMESTAMP.json" 2>/dev/null || {
        log_warning "Security analysis completed with findings (see bandit report)"
    }

    log_success "Code quality analysis completed"
}

# Generate comprehensive test evidence
generate_test_evidence() {
    log_section "GENERATING TEST EVIDENCE"

    local evidence_data="{
        \"timestamp\": \"$(date -Iseconds)\",
        \"test_execution\": {
            \"framework\": \"comprehensive\",
            \"version\": \"1.0.0\",
            \"environment\": \"$(python --version)\",
            \"platform\": \"$(uname -s -r)\"
        },
        \"reports_generated\": []
    }"

    # List all generated reports
    local reports=()
    for report in "$REPORTS_DIR"/*_$TIMESTAMP.*; do
        if [[ -f "$report" ]]; then
            reports+=(\"$(basename "$report")\")
        fi
    done

    # Update evidence with report list
    echo "$evidence_data" | jq --argjson reports "[$(IFS=,; echo "${reports[*]}")]" \
        '.reports_generated = $reports' > "$EVIDENCE_FILE"

    log_info "Test evidence saved to: $EVIDENCE_FILE"
}

# Extract and display test metrics
display_test_metrics() {
    log_section "TEST EXECUTION METRICS"

    # Extract pytest metrics if available
    local pytest_report="$REPORTS_DIR/pytest_report_$TIMESTAMP.json"
    if [[ -f "$pytest_report" ]]; then
        local total_tests=$(jq -r '.summary.total // 0' "$pytest_report")
        local passed_tests=$(jq -r '.summary.passed // 0' "$pytest_report")
        local failed_tests=$(jq -r '.summary.failed // 0' "$pytest_report")
        local skipped_tests=$(jq -r '.summary.skipped // 0' "$pytest_report")
        local duration=$(jq -r '.duration // 0' "$pytest_report")

        echo -e "${CYAN}Pytest Results:${NC}"
        echo -e "  Total Tests: $total_tests"
        echo -e "  Passed: ${GREEN}$passed_tests${NC}"
        echo -e "  Failed: ${RED}$failed_tests${NC}"
        echo -e "  Skipped: ${YELLOW}$skipped_tests${NC}"
        echo -e "  Duration: ${duration}s"

        if [[ $failed_tests -gt 0 ]]; then
            log_warning "$failed_tests tests failed - check detailed report"
        fi
        echo
    fi

    # Extract coverage metrics if available
    local coverage_report="$REPORTS_DIR/coverage.json"
    if [[ -f "$coverage_report" ]]; then
        local coverage_percent=$(jq -r '.totals.percent_covered_display // "N/A"' "$coverage_report")
        local lines_covered=$(jq -r '.totals.covered_lines // 0' "$coverage_report")
        local total_lines=$(jq -r '.totals.num_statements // 0' "$coverage_report")
        local missing_lines=$(jq -r '.totals.missing_lines // 0' "$coverage_report")

        echo -e "${CYAN}Coverage Results:${NC}"
        echo -e "  Overall Coverage: ${GREEN}$coverage_percent%${NC}"
        echo -e "  Lines Covered: $lines_covered / $total_lines"
        echo -e "  Missing Lines: ${RED}$missing_lines${NC}"
        echo
    fi

    # Display file counts and sizes
    echo -e "${CYAN}Report Files Generated:${NC}"
    find "$REPORTS_DIR" -name "*_$TIMESTAMP.*" -type f | while read -r file; do
        local size=$(ls -lh "$file" | awk '{print $5}')
        echo -e "  $(basename "$file") (${size})"
    done
    echo
}

# Validate test results against quality thresholds
validate_quality_thresholds() {
    log_section "VALIDATING QUALITY THRESHOLDS"

    local validation_passed=true

    # Check coverage threshold
    local coverage_report="$REPORTS_DIR/coverage.json"
    if [[ -f "$coverage_report" ]]; then
        local coverage_percent=$(jq -r '.totals.percent_covered // 0' "$coverage_report")
        if (( $(echo "$coverage_percent < 80" | bc -l) )); then
            log_warning "Coverage ($coverage_percent%) below threshold (80%)"
            validation_passed=false
        else
            log_success "Coverage threshold met: $coverage_percent%"
        fi
    fi

    # Check pytest results
    local pytest_report="$REPORTS_DIR/pytest_report_$TIMESTAMP.json"
    if [[ -f "$pytest_report" ]]; then
        local failed_tests=$(jq -r '.summary.failed // 0' "$pytest_report")
        if [[ $failed_tests -gt 0 ]]; then
            log_warning "$failed_tests tests failed"
            validation_passed=false
        else
            log_success "All tests passed"
        fi
    fi

    # Check security issues
    local bandit_report="$REPORTS_DIR/bandit_security_$TIMESTAMP.json"
    if [[ -f "$bandit_report" ]]; then
        local high_severity=$(jq -r '.results[] | select(.issue_severity == "HIGH") | length' "$bandit_report" 2>/dev/null | wc -l)
        if [[ $high_severity -gt 0 ]]; then
            log_warning "$high_severity high-severity security issues found"
            validation_passed=false
        else
            log_success "No high-severity security issues found"
        fi
    fi

    if [[ $validation_passed == true ]]; then
        log_success "All quality thresholds met!"
        return 0
    else
        log_warning "Some quality thresholds not met - review reports"
        return 1
    fi
}

# Generate executive summary
generate_executive_summary() {
    log_section "EXECUTIVE SUMMARY"

    local summary_file="$REPORTS_DIR/executive_summary_$TIMESTAMP.md"

    cat > "$summary_file" << EOF
# PromptEvolver CLI Test Execution Summary

**Date:** $(date)
**Timestamp:** $TIMESTAMP
**Framework:** Comprehensive Testing Framework v1.0.0

## Test Results Overview

EOF

    # Add pytest summary
    local pytest_report="$REPORTS_DIR/pytest_report_$TIMESTAMP.json"
    if [[ -f "$pytest_report" ]]; then
        local total=$(jq -r '.summary.total // 0' "$pytest_report")
        local passed=$(jq -r '.summary.passed // 0' "$pytest_report")
        local failed=$(jq -r '.summary.failed // 0' "$pytest_report")
        local duration=$(jq -r '.duration // 0' "$pytest_report")

        cat >> "$summary_file" << EOF
### Pytest Results
- **Total Tests:** $total
- **Passed:** $passed
- **Failed:** $failed
- **Execution Time:** ${duration}s
- **Success Rate:** $(echo "scale=1; $passed * 100 / $total" | bc)%

EOF
    fi

    # Add coverage summary
    local coverage_report="$REPORTS_DIR/coverage.json"
    if [[ -f "$coverage_report" ]]; then
        local coverage=$(jq -r '.totals.percent_covered_display // "N/A"' "$coverage_report")

        cat >> "$summary_file" << EOF
### Code Coverage
- **Overall Coverage:** $coverage%
- **Threshold:** 80% ($(if (( $(echo "${coverage%\%} >= 80" | bc -l) )); then echo "✅ PASS"; else echo "❌ FAIL"; fi))

EOF
    fi

    # Add quality analysis summary
    cat >> "$summary_file" << EOF
### Quality Analysis
- **Pylint:** Code quality analysis completed
- **MyPy:** Type checking completed
- **Black:** Code formatting analysis completed
- **Radon:** Complexity analysis completed
- **Bandit:** Security analysis completed

### Generated Reports
EOF

    # List all reports
    find "$REPORTS_DIR" -name "*_$TIMESTAMP.*" -type f | while read -r file; do
        echo "- $(basename "$file")" >> "$summary_file"
    done

    cat >> "$summary_file" << EOF

### Evidence File
- **Location:** $EVIDENCE_FILE
- **Format:** JSON with complete test execution metadata

---
*Generated by PromptEvolver CLI Comprehensive Testing Framework*
EOF

    log_success "Executive summary generated: $summary_file"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up temporary files..."
    # Add any cleanup operations here
}

# Main execution function
main() {
    local start_time=$(date +%s)

    echo -e "${PURPLE}"
    echo "=========================================="
    echo "PromptEvolver CLI Comprehensive Test Suite"
    echo "=========================================="
    echo -e "${NC}\n"

    # Set up cleanup trap
    trap cleanup EXIT

    # Execute test pipeline
    initialize_environment

    # Run all test components
    if run_pytest_suite; then
        run_code_quality_analysis
        generate_test_evidence
        display_test_metrics
        generate_executive_summary

        if validate_quality_thresholds; then
            local end_time=$(date +%s)
            local duration=$((end_time - start_time))

            log_section "TEST EXECUTION COMPLETED SUCCESSFULLY"
            log_success "Total execution time: ${duration}s"
            log_success "All reports available in: $REPORTS_DIR"
            log_success "Evidence file: $EVIDENCE_FILE"

            exit 0
        else
            log_warning "Test execution completed with quality threshold violations"
            exit 1
        fi
    else
        log_error "Test execution failed during pytest phase"
        exit 1
    fi
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
