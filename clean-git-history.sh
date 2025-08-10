#!/bin/bash

# Git History Cleanup Script for DriftGuard
# This script removes sensitive data from git history
# WARNING: This will rewrite git history!

set -e

echo "🔐 Git History Cleanup Script"
echo "============================="
echo ""
echo "⚠️  WARNING: This will rewrite git history!"
echo "⚠️  Make sure you have a backup before proceeding!"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "Creating backup branch..."
git branch backup-before-cleanup-$(date +%Y%m%d-%H%M%S)

echo ""
echo "Removing sensitive files from history..."

# Method 1: Using git filter-branch (built-in)
echo "Using git filter-branch to remove sensitive files..."

# Remove private-key.pem
git filter-branch --force --index-filter \
    'git rm --cached --ignore-unmatch apps/driftguard-checks-app/private-key.pem' \
    --prune-empty --tag-name-filter cat -- --all 2>/dev/null || true

# Remove .env files
git filter-branch --force --index-filter \
    'git rm --cached --ignore-unmatch apps/driftguard-checks-app/.env' \
    --prune-empty --tag-name-filter cat -- --all 2>/dev/null || true

echo ""
echo "Cleaning up refs..."
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo ""
echo "Verifying cleanup..."
echo "Checking for private-key.pem in history..."
if git log --all --full-history -- "*private-key.pem" | grep -q "private-key.pem"; then
    echo "⚠️  WARNING: private-key.pem may still be in history"
else
    echo "✅ private-key.pem removed from history"
fi

echo "Checking for .env in history..."
if git log --all --full-history -- "*.env" | grep -q ".env"; then
    echo "⚠️  WARNING: .env files may still be in history"
else
    echo "✅ .env files removed from history"
fi

echo ""
echo "========================================="
echo "🔐 Git History Cleanup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Review the changes carefully"
echo "2. Force push to remote (THIS WILL REWRITE HISTORY):"
echo "   git push origin --force --all"
echo "   git push origin --force --tags"
echo ""
echo "3. Notify all team members to:"
echo "   - Delete their local repositories"
echo "   - Re-clone from remote"
echo ""
echo "4. Update GitHub App with new credentials:"
echo "   - Go to https://github.com/settings/apps/driftguard-checks"
echo "   - Generate new private key"
echo "   - Generate new webhook secret"
echo ""
echo "⚠️  IMPORTANT: Old clones will be incompatible after force push!"