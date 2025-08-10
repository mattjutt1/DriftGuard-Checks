#!/bin/bash
# Setup git hooks for automatic knowledge graph updates

echo "🔗 Setting up git hooks..."

# Create hooks directory if it doesn't exist
mkdir -p .git/hooks

# Copy our pre-commit hook
cp .githooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

echo "✅ Git hooks installed!"
echo "📝 Knowledge graph will now update automatically on commits"
