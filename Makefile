# PromptEvolver 3.0 Project Makefile
# Comprehensive automation for ML training platform
# Created: 2025-08-07

# Variables
PYTHON := python3
PIP := pip3
NPM := npm
DOCKER := docker
DOCKER_COMPOSE := docker-compose
VENV := venv
SHELL := /bin/bash

# Color output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Project directories
PROJECT_ROOT := $(shell pwd)
NEXTJS_DIR := nextjs-app
CLI_DIR := cli
HF_DIR := hf-space
SCRIPTS_DIR := .claude/scripts

# Default target
.DEFAULT_GOAL := help

# Phony targets (don't create files)
.PHONY: help clean install dev test lint format security docker pre-commit

## Help system
help: ## Show this help message
	@echo "$(BLUE)PromptEvolver 3.0 - Project Automation$(NC)"
	@echo "$(YELLOW)========================================$(NC)"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Quick Start:$(NC)"
	@echo "  make install         # Install all dependencies"
	@echo "  make dev            # Start development servers"
	@echo "  make test           # Run all tests"
	@echo ""

# ==================== SETUP & INSTALLATION ====================

install: ## Install all project dependencies
	@echo "$(BLUE)Installing project dependencies...$(NC)"
	@$(MAKE) install-python
	@$(MAKE) install-node
	@$(MAKE) install-hooks
	@echo "$(GREEN)✓ All dependencies installed!$(NC)"

install-python: ## Install Python dependencies
	@echo "$(YELLOW)Installing Python dependencies...$(NC)"
	@if [ ! -d "$(VENV)" ]; then \
		$(PYTHON) -m venv $(VENV); \
		echo "$(GREEN)✓ Virtual environment created$(NC)"; \
	fi
	@source $(VENV)/bin/activate && \
		$(PIP) install --upgrade pip setuptools wheel && \
		if [ -f requirements.txt ]; then $(PIP) install -r requirements.txt; fi && \
		if [ -f requirements-dev.txt ]; then $(PIP) install -r requirements-dev.txt; fi
	@echo "$(GREEN)✓ Python dependencies installed$(NC)"

install-node: ## Install Node.js dependencies
	@echo "$(YELLOW)Installing Node.js dependencies...$(NC)"
	@cd $(NEXTJS_DIR) && $(NPM) install
	@echo "$(GREEN)✓ Node.js dependencies installed$(NC)"

install-hooks: ## Install pre-commit hooks
	@echo "$(YELLOW)Installing pre-commit hooks...$(NC)"
	@pre-commit install
	@echo "$(GREEN)✓ Pre-commit hooks installed$(NC)"

install-ollama: ## Install Ollama and pull Qwen3:4b model
	@echo "$(YELLOW)Installing Ollama...$(NC)"
	@curl -fsSL https://ollama.com/install.sh | sh
	@ollama pull qwen3:4b
	@echo "$(GREEN)✓ Ollama installed with Qwen3:4b model$(NC)"

# ==================== DEVELOPMENT ====================

dev: ## Start all development servers
	@echo "$(BLUE)Starting development servers...$(NC)"
	@$(MAKE) -j 3 dev-convex dev-nextjs dev-ollama

dev-nextjs: ## Start Next.js development server
	@echo "$(YELLOW)Starting Next.js dev server...$(NC)"
	@cd $(NEXTJS_DIR) && $(NPM) run dev

dev-convex: ## Start Convex development server
	@echo "$(YELLOW)Starting Convex dev server...$(NC)"
	@cd $(NEXTJS_DIR) && npx convex dev

dev-ollama: ## Start Ollama server
	@echo "$(YELLOW)Starting Ollama server...$(NC)"
	@ollama serve

dev-cli: ## Run CLI in development mode
	@echo "$(YELLOW)Running CLI...$(NC)"
	@source $(VENV)/bin/activate && \
		cd $(CLI_DIR) && \
		python -m promptevolver_cli

# ==================== TESTING ====================

test: ## Run all tests
	@echo "$(BLUE)Running all tests...$(NC)"
	@$(MAKE) test-python
	@$(MAKE) test-nextjs
	@$(MAKE) test-integration
	@echo "$(GREEN)✓ All tests passed!$(NC)"

test-python: ## Run Python tests with coverage
	@echo "$(YELLOW)Running Python tests...$(NC)"
	@source $(VENV)/bin/activate && \
		pytest cli/tests/ --cov=cli --cov-report=term-missing

test-nextjs: ## Run Next.js tests
	@echo "$(YELLOW)Running Next.js tests...$(NC)"
	@cd $(NEXTJS_DIR) && $(NPM) test

test-integration: ## Run integration tests
	@echo "$(YELLOW)Running integration tests...$(NC)"
	@source $(VENV)/bin/activate && \
		python test-promptwizard-integration.py

test-watch: ## Run tests in watch mode
	@source $(VENV)/bin/activate && \
		pytest cli/tests/ --watch

# ==================== CODE QUALITY ====================

lint: ## Run all linters
	@echo "$(BLUE)Running linters...$(NC)"
	@$(MAKE) lint-python
	@$(MAKE) lint-js
	@echo "$(GREEN)✓ Linting complete!$(NC)"

lint-python: ## Run Python linters
	@echo "$(YELLOW)Running Python linters...$(NC)"
	@source $(VENV)/bin/activate && \
		flake8 $(CLI_DIR) $(SCRIPTS_DIR) --config=.flake8 && \
		mypy $(CLI_DIR) --config-file=mypy.ini
	@echo "$(GREEN)✓ Python linting passed$(NC)"

lint-js: ## Run JavaScript/TypeScript linters
	@echo "$(YELLOW)Running JS/TS linters...$(NC)"
	@cd $(NEXTJS_DIR) && $(NPM) run lint
	@echo "$(GREEN)✓ JS/TS linting passed$(NC)"

format: ## Format all code
	@echo "$(BLUE)Formatting code...$(NC)"
	@$(MAKE) format-python
	@$(MAKE) format-js
	@echo "$(GREEN)✓ Code formatted!$(NC)"

format-python: ## Format Python code with black
	@echo "$(YELLOW)Formatting Python code...$(NC)"
	@source $(VENV)/bin/activate && \
		black $(CLI_DIR) $(SCRIPTS_DIR) *.py --line-length=120 && \
		isort $(CLI_DIR) $(SCRIPTS_DIR) *.py --profile=black --line-length=120
	@echo "$(GREEN)✓ Python code formatted$(NC)"

format-js: ## Format JavaScript/TypeScript code
	@echo "$(YELLOW)Formatting JS/TS code...$(NC)"
	@cd $(NEXTJS_DIR) && npx prettier --write "**/*.{js,jsx,ts,tsx,json,css,md}"
	@echo "$(GREEN)✓ JS/TS code formatted$(NC)"

# ==================== PRE-COMMIT ====================

pre-commit: ## Run pre-commit hooks on all files
	@echo "$(BLUE)Running pre-commit hooks...$(NC)"
	@pre-commit run --all-files
	@echo "$(GREEN)✓ Pre-commit checks passed!$(NC)"

pre-commit-update: ## Update pre-commit hooks
	@echo "$(YELLOW)Updating pre-commit hooks...$(NC)"
	@pre-commit autoupdate
	@echo "$(GREEN)✓ Pre-commit hooks updated$(NC)"

# ==================== DOCKER ====================

docker-build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	@$(DOCKER_COMPOSE) build
	@echo "$(GREEN)✓ Docker images built$(NC)"

docker-up: ## Start Docker containers
	@echo "$(BLUE)Starting Docker containers...$(NC)"
	@$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)✓ Docker containers started$(NC)"

docker-down: ## Stop Docker containers
	@echo "$(YELLOW)Stopping Docker containers...$(NC)"
	@$(DOCKER_COMPOSE) down
	@echo "$(GREEN)✓ Docker containers stopped$(NC)"

docker-logs: ## View Docker logs
	@$(DOCKER_COMPOSE) logs -f

docker-clean: ## Clean Docker resources
	@echo "$(YELLOW)Cleaning Docker resources...$(NC)"
	@$(DOCKER_COMPOSE) down -v
	@docker system prune -f
	@echo "$(GREEN)✓ Docker resources cleaned$(NC)"

# ==================== DATABASE & MIGRATIONS ====================

db-push: ## Push Convex schema changes
	@echo "$(YELLOW)Pushing Convex schema...$(NC)"
	@cd $(NEXTJS_DIR) && npx convex schema push
	@echo "$(GREEN)✓ Schema pushed$(NC)"

db-deploy: ## Deploy Convex functions
	@echo "$(YELLOW)Deploying Convex functions...$(NC)"
	@cd $(NEXTJS_DIR) && npx convex deploy
	@echo "$(GREEN)✓ Functions deployed$(NC)"

db-dashboard: ## Open Convex dashboard
	@cd $(NEXTJS_DIR) && npx convex dashboard

# ==================== BUILD & DEPLOY ====================

build: ## Build production assets
	@echo "$(BLUE)Building production assets...$(NC)"
	@$(MAKE) build-nextjs
	@$(MAKE) build-python
	@echo "$(GREEN)✓ Build complete!$(NC)"

build-nextjs: ## Build Next.js production bundle
	@echo "$(YELLOW)Building Next.js...$(NC)"
	@cd $(NEXTJS_DIR) && $(NPM) run build
	@echo "$(GREEN)✓ Next.js built$(NC)"

build-python: ## Build Python package
	@echo "$(YELLOW)Building Python package...$(NC)"
	@source $(VENV)/bin/activate && \
		cd $(CLI_DIR) && \
		python setup.py sdist bdist_wheel
	@echo "$(GREEN)✓ Python package built$(NC)"

deploy: ## Deploy to production
	@echo "$(BLUE)Deploying to production...$(NC)"
	@echo "$(YELLOW)Deploying Convex...$(NC)"
	@cd $(NEXTJS_DIR) && npx convex deploy --prod
	@echo "$(YELLOW)Deploying to Vercel...$(NC)"
	@cd $(NEXTJS_DIR) && vercel --prod
	@echo "$(GREEN)✓ Deployment complete!$(NC)"

# ==================== SECURITY ====================

security: ## Run security checks
	@echo "$(BLUE)Running security checks...$(NC)"
	@source $(VENV)/bin/activate && \
		bandit -r $(CLI_DIR) -ll && \
		safety check
	@echo "$(GREEN)✓ Security checks passed!$(NC)"

secrets-check: ## Check for exposed secrets
	@echo "$(YELLOW)Checking for exposed secrets...$(NC)"
	@pre-commit run detect-private-key --all-files
	@pre-commit run check-added-large-files --all-files
	@echo "$(GREEN)✓ No secrets exposed$(NC)"

# ==================== TRAINING & ML ====================

train: ## Train PromptWizard model
	@echo "$(BLUE)Starting model training...$(NC)"
	@source $(VENV)/bin/activate && \
		python train_prompt_enhancer.py
	@echo "$(GREEN)✓ Training complete!$(NC)"

train-hf: ## Train on Hugging Face
	@echo "$(BLUE)Starting Hugging Face training...$(NC)"
	@source $(VENV)/bin/activate && \
		cd $(NEXTJS_DIR)/scripts && \
		python train_on_hf.py
	@echo "$(GREEN)✓ HF training complete!$(NC)"

validate: ## Validate training data
	@echo "$(YELLOW)Validating training data...$(NC)"
	@source $(VENV)/bin/activate && \
		python schema_validator.py
	@echo "$(GREEN)✓ Validation complete$(NC)"

# ==================== UTILITY ====================

clean: ## Clean all generated files
	@echo "$(YELLOW)Cleaning generated files...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@rm -rf build/ dist/ *.egg-info 2>/dev/null || true
	@rm -rf $(NEXTJS_DIR)/.next 2>/dev/null || true
	@echo "$(GREEN)✓ Cleaned$(NC)"

clean-all: clean ## Clean everything including dependencies
	@echo "$(YELLOW)Cleaning all including dependencies...$(NC)"
	@rm -rf $(VENV) 2>/dev/null || true
	@rm -rf $(NEXTJS_DIR)/node_modules 2>/dev/null || true
	@rm -rf ~/.cache/pre-commit 2>/dev/null || true
	@echo "$(GREEN)✓ All cleaned$(NC)"

logs: ## View application logs
	@tail -f logs/*.log

env: ## Show environment info
	@echo "$(BLUE)Environment Information:$(NC)"
	@echo "Python: $$(python3 --version)"
	@echo "Node: $$(node --version)"
	@echo "NPM: $$(npm --version)"
	@echo "Docker: $$(docker --version)"
	@echo "Git: $$(git --version)"
	@echo "Current branch: $$(git branch --show-current)"
	@echo "Project root: $(PROJECT_ROOT)"

# ==================== GIT & VERSION CONTROL ====================

commit: ## Commit changes with conventional commit
	@source $(VENV)/bin/activate && \
		git add -A && \
		cz commit

push: ## Push changes to remote
	@git push origin $$(git branch --show-current)

pull: ## Pull latest changes
	@git pull origin $$(git branch --show-current)

status: ## Show git status
	@git status

# ==================== SHORTCUTS ====================

# Shortcuts for common commands
i: install
d: dev
t: test
l: lint
f: format
b: build
c: clean

# Combined commands
check: lint test security ## Run all checks (lint, test, security)
ready: format lint test ## Get code ready for commit (format, lint, test)
fresh: clean install ## Fresh install (clean, install)
restart: docker-down docker-up ## Restart Docker containers

# ==================== DOCUMENTATION ====================

docs-serve: ## Serve documentation locally
	@echo "$(YELLOW)Serving documentation...$(NC)"
	@source $(VENV)/bin/activate && \
		mkdocs serve

docs-build: ## Build documentation
	@echo "$(YELLOW)Building documentation...$(NC)"
	@source $(VENV)/bin/activate && \
		mkdocs build
	@echo "$(GREEN)✓ Documentation built$(NC)"

# Easter egg :)
coffee: ## Take a coffee break ☕
	@echo "$(YELLOW)☕ Time for a coffee break! You've earned it!$(NC)"
	@echo "$(GREEN)   ╔════════════╗$(NC)"
	@echo "$(GREEN)   ║  ☕ COFFEE  ║$(NC)"
	@echo "$(GREEN)   ╚════════════╝$(NC)"
