# DriftGuard-Checks Makefile
# Branch Protection and Development Helpers

.PHONY: help bp-backup bp-apply bp-restore bp-status bp-minimal test build

# Default target
help:
	@echo "Available targets:"
	@echo "  help        - Show this help message"
	@echo "  bp-backup   - Backup current branch protection settings"
	@echo "  bp-apply    - Apply minimal branch protection"
	@echo "  bp-restore  - Restore from latest backup"
	@echo "  bp-status   - Show current branch protection status"
	@echo "  bp-minimal  - Apply minimal protection configuration"
	@echo "  test        - Run test suite"
	@echo "  build       - Build TypeScript"
	@echo ""
	@echo "Branch Protection Examples:"
	@echo "  make bp-backup                 # Backup current settings"
	@echo "  make bp-apply                  # Apply minimal protection"
	@echo "  make bp-restore                # Restore from backup"

# Branch Protection Targets
bp-backup:
	@echo "Backing up branch protection..."
	@./scripts/branch-protection.sh backup

bp-apply:
	@echo "Applying minimal branch protection..."
	@./scripts/branch-protection.sh apply bp-minimal.json

bp-restore:
	@echo "Restoring branch protection from backup..."
	@./scripts/branch-protection.sh restore

bp-status:
	@echo "Checking branch protection status..."
	@./scripts/branch-protection.sh status

bp-minimal:
	@echo "Applying minimal branch protection..."
	@./scripts/branch-protection.sh minimal

# Development Targets
test:
	@echo "Running tests..."
	@npm test

build:
	@echo "Building TypeScript..."
	@npm run build

# Security Testing
test-security:
	@echo "Running security tests..."
	@npm run test:security

# Health Check
health-check:
	@echo "Checking health endpoints..."
	@curl -s http://localhost:3001/health | jq '.status' || echo "Health server not running"
	@curl -s http://localhost:3001/readyz | jq '.status' || echo "Readiness check failed"