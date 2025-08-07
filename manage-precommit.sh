#!/bin/bash
# Script to manage pre-commit hooks incrementally

set -e

echo "Pre-commit Hook Management Script"
echo "================================="

# Function to run specific hooks
run_hook() {
    local hook_id=$1
    echo "Running hook: $hook_id"
    pre-commit run "$hook_id" --all-files || true
}

# Function to run hooks on specific directories
run_on_directory() {
    local dir=$1
    echo "Running all hooks on directory: $dir"
    pre-commit run --files "$dir"/**/*.py || true
}

# Function to switch configurations
switch_config() {
    local config=$1
    if [ "$config" = "minimal" ]; then
        cp .pre-commit-config-minimal.yaml .pre-commit-config.yaml
        echo "Switched to minimal configuration"
    elif [ "$config" = "full" ]; then
        cp .pre-commit-config-full.yaml .pre-commit-config.yaml
        echo "Switched to full configuration"
    else
        echo "Unknown configuration: $config"
        return 1
    fi
}

# Main menu
case "$1" in
    minimal)
        echo "Switching to minimal pre-commit configuration..."
        switch_config minimal
        pre-commit install
        ;;
    
    full)
        echo "Switching to full pre-commit configuration..."
        switch_config full
        pre-commit install
        ;;
    
    quick)
        echo "Running quick checks (trailing whitespace, EOF, line endings)..."
        run_hook trailing-whitespace
        run_hook end-of-file-fixer
        run_hook mixed-line-ending
        ;;
    
    security)
        echo "Running security checks..."
        run_hook detect-private-key
        run_hook check-added-large-files
        ;;
    
    python-format)
        echo "Running Python formatting (black, isort) on our code only..."
        pre-commit run black --files 'cli/**/*.py' || true
        pre-commit run black --files '.claude/scripts/*.py' || true
        pre-commit run black --files '*.py' || true
        pre-commit run isort --files 'cli/**/*.py' || true
        pre-commit run isort --files '.claude/scripts/*.py' || true
        pre-commit run isort --files '*.py' || true
        ;;
    
    python-lint)
        echo "Running Python linting (flake8) on our code only..."
        pre-commit run flake8 --files 'cli/**/*.py' || true
        pre-commit run flake8 --files '.claude/scripts/*.py' || true
        pre-commit run flake8 --files '*.py' || true
        ;;
    
    cli-only)
        echo "Running all hooks on CLI directory only..."
        run_on_directory "cli"
        ;;
    
    scripts-only)
        echo "Running all hooks on scripts only..."
        run_on_directory ".claude/scripts"
        ;;
    
    status)
        echo "Current configuration:"
        if diff -q .pre-commit-config.yaml .pre-commit-config-minimal.yaml >/dev/null 2>&1; then
            echo "Using MINIMAL configuration"
        elif diff -q .pre-commit-config.yaml .pre-commit-config-full.yaml >/dev/null 2>&1; then
            echo "Using FULL configuration"
        else
            echo "Using CUSTOM configuration"
        fi
        echo ""
        echo "Installed hooks:"
        pre-commit --version
        ;;
    
    *)
        echo "Usage: $0 {minimal|full|quick|security|python-format|python-lint|cli-only|scripts-only|status}"
        echo ""
        echo "Commands:"
        echo "  minimal       - Switch to minimal pre-commit config (fast, essential checks)"
        echo "  full          - Switch to full pre-commit config (all checks)"
        echo "  quick         - Run quick formatting fixes (whitespace, EOF, line endings)"
        echo "  security      - Run security checks only"
        echo "  python-format - Format Python code with black and isort"
        echo "  python-lint   - Lint Python code with flake8"
        echo "  cli-only      - Run all hooks on CLI directory only"
        echo "  scripts-only  - Run all hooks on .claude/scripts only"
        echo "  status        - Show current configuration status"
        exit 1
        ;;
esac

echo "Done!"