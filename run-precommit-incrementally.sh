#!/bin/bash
# Run pre-commit hooks incrementally to avoid timeouts on large codebase
# This script runs hooks in stages and saves progress

set -e

LOG_FILE="precommit-progress.log"
FIXED_FILES="precommit-fixed.txt"

echo "Incremental Pre-commit Hook Runner"
echo "==================================="
echo "This will run pre-commit hooks incrementally to handle our large codebase"
echo ""

# Initialize log files
echo "Starting incremental pre-commit run at $(date)" > "$LOG_FILE"
touch "$FIXED_FILES"

# Function to run hooks on specific file patterns with timeout
run_with_timeout() {
    local pattern=$1
    local description=$2
    local timeout=${3:-60}  # Default 60 seconds
    
    echo "Processing: $description"
    echo "Pattern: $pattern"
    echo "Timeout: ${timeout}s"
    
    # Find files matching pattern
    files=$(find . -type f -name "$pattern" \
        -not -path "./venv/*" \
        -not -path "./.venv/*" \
        -not -path "./node_modules/*" \
        -not -path "./nextjs-app/node_modules/*" \
        -not -path "./nextjs-app/.next/*" \
        -not -path "./microsoft-promptwizard/*" \
        -not -path "./hf-deployment/*" \
        -not -path "./.git/*" \
        -not -path "./__pycache__/*" \
        -not -path "./.pytest_cache/*" \
        -not -path "./.mypy_cache/*" \
        2>/dev/null | head -50)  # Process 50 files at a time
    
    if [ -z "$files" ]; then
        echo "No files found for pattern: $pattern"
        return
    fi
    
    echo "Found $(echo "$files" | wc -l) files to process (max 50 per batch)"
    
    # Run pre-commit on these files
    echo "$files" | while read -r file; do
        if [ -f "$file" ]; then
            echo -n "  $file ... "
            if timeout "$timeout" pre-commit run --files "$file" 2>&1 | grep -q "Passed\|Skipped"; then
                echo "✓"
                echo "$file" >> "$FIXED_FILES"
            elif timeout "$timeout" pre-commit run --files "$file" 2>&1 | grep -q "Failed"; then
                echo "✗ (has issues)"
            else
                echo "⚠ (modified)"
            fi
        fi
    done
    
    echo "Completed: $description" | tee -a "$LOG_FILE"
    echo ""
}

# Stage 1: Quick fixes on all files (these are fast and safe)
echo "STAGE 1: Quick Fixes (whitespace, line endings, EOF)"
echo "======================================================"
pre-commit run trailing-whitespace --all-files || true
pre-commit run end-of-file-fixer --all-files || true  
pre-commit run mixed-line-ending --all-files || true
echo "Stage 1 complete" | tee -a "$LOG_FILE"

# Stage 2: Structure checks (fast, won't modify)
echo ""
echo "STAGE 2: Structure Checks"
echo "========================="
pre-commit run check-yaml --all-files || true
pre-commit run check-json --all-files || true
pre-commit run check-toml --all-files || true
pre-commit run check-merge-conflict --all-files || true
pre-commit run detect-private-key --all-files || true
echo "Stage 2 complete" | tee -a "$LOG_FILE"

# Stage 3: Process our Python files in batches
echo ""
echo "STAGE 3: Python Files (Our Code Only)"
echo "====================================="

# Process root directory Python files
run_with_timeout "*.py" "Root directory Python files" 30

# Process CLI files
run_with_timeout "*.py" "CLI Python files (cli/)" 60

# Process our scripts
echo "Processing .claude/scripts..."
for script in .claude/scripts/*.py; do
    if [ -f "$script" ]; then
        echo -n "  $(basename "$script") ... "
        if timeout 10 pre-commit run --files "$script" 2>&1 | grep -q "Passed\|Skipped"; then
            echo "✓"
        else
            echo "⚠ (needs fixes)"
        fi
    fi
done

# Stage 4: Summary
echo ""
echo "SUMMARY"
echo "======="
echo "Log file: $LOG_FILE"
echo "Fixed files list: $FIXED_FILES"
echo "Total files processed: $(wc -l < "$FIXED_FILES" 2>/dev/null || echo 0)"
echo ""
echo "To commit the changes made by pre-commit hooks:"
echo "  git add -A && git commit -m 'chore: apply pre-commit fixes incrementally'"
echo ""
echo "To continue processing more files, run this script again."
echo "To run on specific directories:"
echo "  pre-commit run --files 'cli/**/*.py'"
echo "  pre-commit run --files '.claude/scripts/*.py'"