#!/bin/bash
# Development environment setup script

echo "🚀 Setting up PromptEvolver development environment..."

# Load aliases
if [ -f ".bash_aliases" ]; then
    echo "📝 Loading development aliases..."
    source .bash_aliases

    # Add to bashrc if not already there
    if ! grep -q "source.*\.bash_aliases" ~/.bashrc; then
        echo "" >> ~/.bashrc
        echo "# PromptEvolver aliases" >> ~/.bashrc
        echo "if [ -f ~/prompt-wizard/.bash_aliases ]; then" >> ~/.bashrc
        echo "    source ~/prompt-wizard/.bash_aliases" >> ~/.bashrc
        echo "fi" >> ~/.bashrc
        echo "✅ Added aliases to ~/.bashrc"
    fi
else
    echo "⚠️  .bash_aliases not found"
fi

# Setup git hooks
if [ -f "setup-git-hooks.sh" ]; then
    echo "🔗 Setting up git hooks..."
    ./setup-git-hooks.sh
else
    echo "⚠️  setup-git-hooks.sh not found"
fi

# Create python virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    echo "✅ Python environment ready"
else
    echo "✅ Python virtual environment already exists"
fi

# Install npm dependencies if package.json exists
if [ -f "package.json" ] && [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
    echo "✅ npm dependencies installed"
fi

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Run: source ~/.bashrc (to load aliases)"
echo "2. Run: inf-start (to start Infisical)"
echo "3. Run: dev-docs (to start documentation server)"
echo "4. Run: dev-status (to check everything is working)"
echo ""
echo "💡 Useful aliases:"
echo "  inf-start/stop    - Manage Infisical"
echo "  dev-backend       - Start backend server"
echo "  dev-docs          - Local documentation"
echo "  knowledge-sync    - Update knowledge graph"
echo "  claude-*          - Quick sub-agent access"
echo ""
