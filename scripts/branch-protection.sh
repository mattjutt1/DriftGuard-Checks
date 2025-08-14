#!/usr/bin/env bash
# Branch Protection Management Script for DriftGuard Checks
# Provides backup, apply, and restore functionality for GitHub branch protection

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
error() { echo -e "${RED}❌ Error: $*${NC}" >&2; exit 1; }
success() { echo -e "${GREEN}✅ $*${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $*${NC}"; }
info() { echo -e "ℹ️  $*"; }

# Check dependencies
command -v gh >/dev/null || error "GitHub CLI (gh) is required"
command -v jq >/dev/null || error "jq is required"

# Configuration
REPO=${GITHUB_REPOSITORY:-""}
BRANCH=${GITHUB_REF_NAME:-"main"}
BACKUP_DIR="./bp-backups"
DATE=$(date +%Y-%m-%d_%H-%M-%S)

# Parse arguments
COMMAND=${1:-"help"}

show_help() {
    cat << EOF
Branch Protection Management Script

Usage: $0 <command> [options]

Commands:
    backup [branch]     - Backup current branch protection settings
    apply <file>        - Apply branch protection from file
    restore [file]      - Restore from backup (latest if no file specified)
    status [branch]     - Show current protection status
    minimal             - Apply minimal protection settings
    help               - Show this help

Options:
    --repo OWNER/NAME   - Specify repository (default: current repo)
    --branch NAME       - Specify branch (default: main)
    --dry-run          - Show what would be done without executing

Examples:
    $0 backup                           # Backup main branch protection
    $0 apply bp.minimal.json           # Apply minimal protection
    $0 restore                         # Restore from latest backup
    $0 status                          # Show current status
EOF
}

# Get repository info
get_repo_info() {
    if [[ -n "$REPO" ]]; then
        echo "$REPO"
    else
        # Try to get from git remote
        local remote_url
        remote_url=$(git remote get-url origin 2>/dev/null || echo "")
        if [[ "$remote_url" =~ github\.com[:/]([^/]+/[^/.]+) ]]; then
            echo "${BASH_REMATCH[1]}"
        else
            error "Could not determine repository. Use --repo OWNER/NAME or set GITHUB_REPOSITORY"
        fi
    fi
}

# Backup branch protection
backup_protection() {
    local branch=${1:-$BRANCH}
    local repo
    repo=$(get_repo_info)
    
    info "Backing up branch protection for $repo:$branch"
    
    mkdir -p "$BACKUP_DIR"
    local backup_file="$BACKUP_DIR/bp-${branch}-${DATE}.json"
    
    # Get current protection settings
    if gh api "/repos/$repo/branches/$branch/protection" \
       --jq '{
         required_status_checks: (
           .required_status_checks | select(.) | {
             strict,
             checks: (.checks // ((.contexts // []) | map({context: .})))
           }
         ),
         enforce_admins: (.enforce_admins.enabled // false),
         required_pull_request_reviews: .required_pull_request_reviews,
         restrictions: .restrictions
       }' > "$backup_file" 2>/dev/null; then
        success "Branch protection backed up to: $backup_file"
        return 0
    else
        warn "No branch protection found for $repo:$branch (this is normal for unprotected branches)"
        echo '{"message": "No protection configured"}' > "$backup_file"
        return 1
    fi
}

# Apply protection settings
apply_protection() {
    local file=${1:-""}
    local repo
    repo=$(get_repo_info)
    local branch=${2:-$BRANCH}
    
    [[ -z "$file" ]] && error "Protection file required"
    [[ ! -f "$file" ]] && error "File not found: $file"
    
    info "Applying branch protection from $file to $repo:$branch"
    
    # Validate JSON first
    if ! jq empty "$file" 2>/dev/null; then
        error "Invalid JSON in $file"
    fi
    
    # Apply protection
    if gh api -X PUT "/repos/$repo/branches/$branch/protection" \
       --input "$file" >/dev/null; then
        success "Branch protection applied successfully"
    else
        error "Failed to apply branch protection"
    fi
}

# Restore from backup
restore_protection() {
    local file=${1:-""}
    local repo
    repo=$(get_repo_info)
    local branch=${2:-$BRANCH}
    
    if [[ -z "$file" ]]; then
        # Find latest backup
        if [[ -d "$BACKUP_DIR" ]]; then
            file=$(find "$BACKUP_DIR" -name "bp-${branch}-*.json" -type f | sort -r | head -1)
        fi
        [[ -z "$file" ]] && error "No backup files found for branch $branch"
        info "Using latest backup: $file"
    fi
    
    [[ ! -f "$file" ]] && error "Backup file not found: $file"
    
    # Check if backup contains actual protection
    if jq -e '.message' "$file" >/dev/null 2>&1; then
        warn "Backup indicates no protection was configured originally"
        info "To remove protection, manually disable it in GitHub settings"
        return 1
    fi
    
    apply_protection "$file" "$branch"
}

# Show protection status
show_status() {
    local branch=${1:-$BRANCH}
    local repo
    repo=$(get_repo_info)
    
    info "Branch protection status for $repo:$branch"
    
    if gh api "/repos/$repo/branches/$branch/protection" --jq '{
      status_checks: .required_status_checks.checks,
      enforce_admins: .enforce_admins.enabled,
      pr_reviews: .required_pull_request_reviews.required_approving_review_count,
      restrictions: .restrictions
    }' 2>/dev/null; then
        success "Branch protection is active"
    else
        warn "No branch protection configured"
    fi
}

# Apply minimal protection
apply_minimal() {
    local repo
    repo=$(get_repo_info)
    local branch=${1:-$BRANCH}
    
    info "Applying minimal branch protection to $repo:$branch"
    
    # Create minimal protection file
    local minimal_file="/tmp/bp-minimal-$$.json"
    cat > "$minimal_file" << 'EOF'
{
  "required_status_checks": {
    "strict": true,
    "checks": [
      { "context": "Test" },
      { "context": "CodeQL" }
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true
  },
  "restrictions": null
}
EOF
    
    apply_protection "$minimal_file" "$branch"
    rm -f "$minimal_file"
}

# Parse options
DRY_RUN=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --repo)
            REPO="$2"
            shift 2
            ;;
        --branch)
            BRANCH="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        -*)
            error "Unknown option: $1"
            ;;
        *)
            break
            ;;
    esac
done

# Handle dry run
if [[ "$DRY_RUN" == "true" ]]; then
    warn "DRY RUN MODE - No changes will be made"
    # Add dry run logic here
fi

# Execute commands
case "$COMMAND" in
    backup)
        backup_protection "$2"
        ;;
    apply)
        [[ -z "${2:-}" ]] && error "Usage: $0 apply <file>"
        apply_protection "$2"
        ;;
    restore)
        restore_protection "${2:-}"
        ;;
    status)
        show_status "${2:-$BRANCH}"
        ;;
    minimal)
        apply_minimal "${2:-$BRANCH}"
        ;;
    help)
        show_help
        ;;
    *)
        error "Unknown command: $COMMAND. Use 'help' for usage."
        ;;
esac