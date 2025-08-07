# PromptEvolver Development Aliases

# Infisical shortcuts
alias inf-start='./infisical-manage.sh start'
alias inf-stop='./infisical-manage.sh stop'
alias inf-status='./infisical-manage.sh status'
alias inf-logs='./infisical-manage.sh logs'
alias inf-web='echo "🌐 Opening http://localhost:8080" && open http://localhost:8080 2>/dev/null || xdg-open http://localhost:8080 2>/dev/null || echo "Open http://localhost:8080 in your browser"'

# Development shortcuts
alias dev-backend='source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000'
alias dev-frontend='npm run dev'
alias dev-docs='./serve-docs.sh'

# Knowledge graph updates
alias kg-update='python .claude/scripts/update_knowledge_graph.py'
alias cv-update='python .claude/scripts/update_context_vectors.py'
alias knowledge-sync='kg-update && cv-update'

# Testing shortcuts
alias test-backend='pytest --cov=app --cov-report=html'
alias test-frontend='npm test'
alias test-all='test-backend && test-frontend'

# Code quality
alias lint-python='black app/ && flake8 app/'
alias lint-js='npx prettier --write "src/**/*.{js,jsx,ts,tsx}" && npx eslint src/ --fix'
alias security-scan='bandit -r app/ && safety check'

# Git helpers
alias git-setup-hooks='./setup-git-hooks.sh'
alias git-knowledge='git add .claude/knowledge_graph.json .claude/context_vectors.json 2>/dev/null || echo "No knowledge files to add"'

# Project shortcuts
alias activate='source venv/bin/activate'
alias requirements='pip freeze > requirements.txt'

# Claude Code helpers
alias claude-backend='claude /agents backend-developer'
alias claude-frontend='claude /agents frontend-developer'
alias claude-ai='claude /agents ai-integration'
alias claude-security='claude /agents security-specialist'
alias claude-perf='claude /agents performance-optimizer'

# Enhanced CLI tools
alias fd='fdfind'
alias bat='batcat'
alias ls='eza --color=always --group-directories-first'
alias ll='eza -la --color=always --group-directories-first'
alias tree='eza --tree --color=always'
alias cat='batcat --paging=never'

# Development file operations
alias find-code='fdfind -e py -e js -e ts -e jsx -e tsx -e vue -e go -e rust'
alias find-config='fdfind -e json -e yaml -e yml -e toml -e ini -e env'
alias search='rg --type-add "web:*.{html,css,js,ts,jsx,tsx,vue}" --smart-case'
alias disk-usage='ncdu'

# Quick project status
alias dev-status='echo "📊 Development Status:" && inf-status && echo "" && git status --short && echo "" && ps aux | grep -E "(uvicorn|npm|python)" | grep -v grep || echo "No dev servers running"'

echo "✅ PromptEvolver development aliases loaded!"
echo "💡 Type 'alias | grep -E \"(inf-|dev-|claude-)\"' to see all shortcuts"
