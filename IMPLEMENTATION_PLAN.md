# 🎯 PromptEvolver 3.0 - Systematic Implementation Plan

## 📋 Overview
This plan breaks down the PRD into **102 micro-tasks** organized in **6 phases**. Each task is designed to be completed in 15-30 minutes with full testing and documentation.

## 🛠️ Pre-Implementation Setup

### PHASE 0: Environment Preparation & Cleanup
**Goal**: Clean workspace and install all necessary tools for success

#### Task 0.1: Workspace Cleanup [15 min]
- **Agent**: devops-agent
- **Pre-task**:
  - `mcp__ide__getDiagnostics` - Check current errors
  - `Bash: df -h` - Check disk space before/after
- **Actions**:
  ```bash
  # DELETE Windows artifacts
  find . -name "*Zone.Identifier" -delete

  # DELETE redundant deployment docs (keep one comprehensive guide)
  rm -f DEPLOYMENT-GUIDE.md CORRECT-DEPLOYMENT-GUIDE.md DEPLOYMENT_SUCCESS.md
  rm -f RAILWAY-DEPLOYMENT-STEPS.md RAILWAY_DEPLOYMENT.md HF-DEPLOYMENT-QUICK-GUIDE.md
  rm -f HF-SPACES-DEPLOYMENT-PLAN.md HF_SPACE_FIX.md
  # Keep only: DEPLOYMENT_GUIDE.md as the main guide

  # DELETE multiple Dockerfiles (keep one main)
  rm -f Dockerfile.build Dockerfile.direct Dockerfile.minimal Dockerfile.ollama Dockerfile.socat
  # Keep only: Dockerfile

  # DELETE test artifacts and result JSONs
  rm -f cli/*.json
  rm -f loggies.txt
  rm -rf cli/test_env
  find . -name "*.pyc" -delete
  find . -name "__pycache__" -delete
  find . -name ".pytest_cache" -delete

  # DELETE redundant virtual environments
  rm -rf test_env hf_env cli/test_env nextjs-app/test_env nextjs-app/hf_training/venv
  rm -rf nextjs-app/hf_training/hf_env nextjs-app/hf_training/venv_train
  rm -rf hf-deployment/venv hf-space/venv
  # Keep only: venv/ at root level

  # DELETE duplicate/backup files
  rm -f claude.md optimized-claude-framework.md.integrated
  rm -f hf-space/app_fixed.py hf-space/app_minimal.py hf-space/app_backup.py
  rm -f hf-deployment/app_backup.py
  rm -f nextjs-app/convex/promptwizard.ts.backup

  # DELETE old test reports
  rm -rf cli/tests/reports/
  rm -f *TEST*.md *TEST*.json

  # DELETE duplicate nextjs-app inside nextjs-app
  rm -rf nextjs-app/nextjs-app/

  # DELETE egg-info directories
  rm -rf *.egg-info
  rm -rf cli/*.egg-info

  # Check space saved
  df -h .
  ```
- **Test**: `ls -la` shows cleaner structure
- **Commit**: "chore: delete redundant files and clean workspace"

#### Task 0.2: Install Development Tools [20 min]
- **Agent**: devops-agent
- **Pre-task**:
  - `Context7: Python development tools 2024`
  - `WebSearch: "best python ML development tools 2024"`
- **Actions**:
  ```bash
  # Core Python tools
  pip install --upgrade pip setuptools wheel
  pip install pytest pytest-cov pytest-asyncio pytest-mock
  pip install black isort mypy pylint flake8
  pip install pre-commit commitizen

  # ML/AI tools
  pip install tensorboard wandb
  pip install memory_profiler py-spy

  # Documentation tools
  pip install sphinx mkdocs mkdocs-material
  pip install pydoc-markdown

  # CLI tools
  sudo apt-get update
  sudo apt-get install -y jq yq httpie tree

  # Node.js tools (for frontend)
  npm install -g prettier eslint jest husky commitizen

  # Create requirements-dev.txt
  pip freeze > requirements-dev.txt
  ```
- **Test**: `pytest --version && black --version && jq --version`
- **Commit**: "chore: install development tools and dependencies"

#### Task 0.3: Setup Pre-commit Hooks [15 min]
- **Agent**: devops-agent
- **Pre-task**: `Context7: pre-commit configuration best practices`
- **Actions**:
  ```yaml
  # Create .pre-commit-config.yaml
  repos:
    - repo: https://github.com/pre-commit/pre-commit-hooks
      rev: v4.5.0
      hooks:
        - id: trailing-whitespace
        - id: end-of-file-fixer
        - id: check-yaml
        - id: check-json
        - id: check-added-large-files
    - repo: https://github.com/psf/black
      rev: 24.1.0
      hooks:
        - id: black
    - repo: https://github.com/pycqa/isort
      rev: 5.13.0
      hooks:
        - id: isort
    - repo: https://github.com/pycqa/flake8
      rev: 7.0.0
      hooks:
        - id: flake8
          args: ['--max-line-length=100']
  ```
  ```bash
  pre-commit install
  pre-commit run --all-files
  ```
- **Test**: Make a test commit and verify hooks run
- **Commit**: "chore: setup pre-commit hooks for code quality"

#### Task 0.4: Create Project Makefile [15 min]
- **Agent**: devops-agent
- **Pre-task**: `Context7: Makefile best practices for Python ML projects`
- **Actions**: Create comprehensive Makefile with all commands
- **Test**: `make help` shows all available commands
- **Commit**: "chore: add Makefile for project automation"

---

## 📁 PHASE 1: Foundation Setup (Milestone 1-2)

### Milestone 1: Repository Scaffold

#### Task 1.1: Create Directory Structure [10 min]
- **Agent**: backend-developer-agent
- **Pre-task**: `Context7: Python ML project structure`
- **Actions**:
  ```bash
  mkdir -p data/{raw,interim,processed}
  mkdir -p schemas
  mkdir -p scripts
  mkdir -p configs
  mkdir -p server
  mkdir -p prompts
  mkdir -p results
  mkdir -p docs
  mkdir -p tests/{unit,integration,e2e}
  ```
- **Test**: `tree -L 2` shows correct structure
- **Update**: TodoWrite, CHANGELOG.md
- **Commit**: "feat: create PRD-compliant directory structure"

#### Task 1.2: Create Core Documentation Files [20 min]
- **Agent**: documentation-agent
- **Pre-task**:
  - `Context7: README best practices`
  - `Read: PRD section 1-3`
- **Actions**:
  - Create README.md with project overview
  - Create LICENSE (Apache 2.0)
  - Create DATA_MANIFEST.md template
  - Create .gitignore
- **Test**: `mcp__ide__getDiagnostics` shows no errors
- **Commit**: "docs: add core documentation files"

#### Task 1.3: Create requirements.txt [15 min]
- **Agent**: backend-developer-agent
- **Pre-task**: `Read: PRD section 9 - dependencies`
- **Actions**: Create requirements.txt with core dependencies
  ```
  transformers>=4.36.0
  peft>=0.7.0
  datasets>=2.14.0
  fastapi>=0.104.0
  uvicorn>=0.24.0
  pydantic>=2.5.0
  pyyaml>=6.0
  torch>=2.1.0
  accelerate>=0.25.0
  ```
- **Test**: `pip install -r requirements.txt --dry-run`
- **Commit**: "feat: add project dependencies"

### Milestone 2: Schemas and Prompts

#### Task 2.1: Create JSON Schema [25 min]
- **Agent**: backend-developer-agent
- **Pre-task**:
  - `Context7: JSON schema validation`
  - `Read: PRD FR1 - schema requirements`
- **Actions**: Create `schemas/engineered_prompt.schema.json`
- **Test**: Validate with sample data
- **Commit**: "feat: add engineered prompt JSON schema"

#### Task 2.2: Create System Message Template [20 min]
- **Agent**: ai-integration-agent
- **Pre-task**: `Read: PRD examples section 14`
- **Actions**: Create `prompts/system_message.txt`
- **Test**: Check all required tags present
- **Commit**: "feat: add system message prompt template"

#### Task 2.3: Create Judge Rubric Templates [25 min]
- **Agent**: ai-integration-agent
- **Pre-task**: `Context7: LLM-as-judge best practices`
- **Actions**: Create domain-specific rubrics in `prompts/judge_rubric.txt`
- **Test**: Validate rubric structure
- **Commit**: "feat: add domain-specific judge rubrics"

#### Task 2.4: Create Domain Classifier Prompt [20 min]
- **Agent**: ai-integration-agent
- **Actions**: Create `prompts/domain_classifier.txt`
- **Test**: Test with sample inputs
- **Commit**: "feat: add domain classification prompt"

---

## 📊 PHASE 2: Data Pipeline (Milestone 3-3.5)

### Milestone 3: Data Processing Scripts

#### Task 3.1: Create normalize_datasets.py [30 min]
- **Agent**: backend-developer-agent
- **Pre-task**:
  - `Context7: data normalization pandas`
  - `WebSearch: "prompt dataset formats 2024"`
- **Actions**: Implement weak→improved format converter
- **Test**: `pytest tests/unit/test_normalize.py`
- **Commit**: "feat: add dataset normalization script"

#### Task 3.2: Create generate_seed_pairs.py [35 min]
- **Agent**: ai-integration-agent
- **Pre-task**:
  - `Read: microsoft-promptwizard/README.md`
  - `Context7: PromptWizard usage`
- **Actions**: Integrate PromptWizard for offline generation
- **Test**: Generate 10 sample pairs
- **Commit**: "feat: add PromptWizard seed generation"

#### Task 3.3: Create synthesize_pairs.py [30 min]
- **Agent**: ai-integration-agent
- **Actions**: Implement synthetic pair generation with domain weighting
- **Test**: Verify domain distribution matches PRD
- **Commit**: "feat: add synthetic data generation"

#### Task 3.4: Create split_data.py [20 min]
- **Agent**: backend-developer-agent
- **Pre-task**: `Context7: stratified train test split`
- **Actions**: Implement stratified splitting with seed=42
- **Test**: Verify splits maintain domain ratios
- **Commit**: "feat: add data splitting with stratification"

#### Task 3.5: Create verify_licenses.py [25 min]
- **Agent**: security-specialist-agent
- **Pre-task**: `WebSearch: "dataset licenses commercial use"`
- **Actions**: Implement license verification
- **Test**: Test with known licenses
- **Commit**: "feat: add license verification script"

### Milestone 3.5: Domain-Specific Generation

#### Task 3.6: Implement Domain Router [25 min]
- **Agent**: backend-developer-agent
- **Actions**: Enhance domain_router.py with weighted sampling
- **Test**: `pytest tests/unit/test_domain_router.py`
- **Commit**: "feat: enhance domain routing with weights"

#### Task 3.7: Create Negative Examples [30 min]
- **Agent**: ai-integration-agent
- **Actions**: Generate 20% negative examples per domain
- **Test**: Verify negative example quality
- **Commit**: "feat: add negative example generation"

---

## 🚀 PHASE 3: Training System (Milestone 4-4.5)

### Milestone 4: Training Scripts

#### Task 4.1: Create train_stage1.py [35 min]
- **Agent**: ai-integration-agent
- **Pre-task**:
  - `Context7: LoRA fine-tuning transformers`
  - `Read: PRD section 10 - model specs`
- **Actions**: Implement foundational instruction tuning
- **Test**: Dry run with 100 samples
- **Commit**: "feat: add stage 1 foundational training"

#### Task 4.2: Create train_stage2.py [35 min]
- **Agent**: ai-integration-agent
- **Actions**: Implement prompt transformation specialization
- **Test**: Verify LoRA configuration
- **Commit**: "feat: add stage 2 specialization training"

#### Task 4.3: Create train_stage3.py [30 min]
- **Agent**: ai-integration-agent
- **Actions**: Implement optional reasoning enhancement
- **Test**: Test with GSM8K subset
- **Commit**: "feat: add stage 3 reasoning enhancement"

#### Task 4.4: Create training_config.yaml [20 min]
- **Agent**: backend-developer-agent
- **Actions**: Create `configs/training_config.yaml` with PRD settings
- **Test**: Validate YAML structure
- **Commit**: "feat: add training configuration"

#### Task 4.5: Add Module Coverage Assertion [25 min]
- **Agent**: backend-developer-agent
- **Pre-task**: `Context7: PyTorch model introspection`
- **Actions**: Implement target_modules validation
- **Test**: Test with Qwen model
- **Commit**: "feat: add LoRA module coverage validation"

### Milestone 4.5: Multi-Stage Pipeline

#### Task 4.6: Stage Transition Verification [30 min]
- **Agent**: backend-developer-agent
- **Actions**: Implement transition metrics checks
- **Test**: Verify stage 1→2 metrics
- **Commit**: "feat: add stage transition verification"

#### Task 4.7: Domain-Specific Loss Weighting [30 min]
- **Agent**: ai-integration-agent
- **Actions**: Implement weighted loss by domain
- **Test**: Verify loss calculation
- **Commit**: "feat: add domain-specific loss weighting"

---

## 🧪 PHASE 4: Evaluation Framework (Milestone 5)

### Milestone 5: Evaluation Suite

#### Task 5.1: Create eval_suite.py [40 min]
- **Agent**: backend-developer-agent
- **Pre-task**:
  - `Context7: ML evaluation metrics`
  - `Read: PRD section 12 - acceptance tests`
- **Actions**: Implement comprehensive evaluation framework
- **Test**: Run on validation set
- **Commit**: "feat: add evaluation suite framework"

#### Task 5.2: Analytics Metrics Calculator [30 min]
- **Agent**: backend-developer-agent
- **Actions**: Create `analytics_metrics.py`
- **Test**: Test with analytics examples
- **Commit**: "feat: add analytics-specific metrics"

#### Task 5.3: Coding Metrics Calculator [30 min]
- **Agent**: backend-developer-agent
- **Actions**: Create `coding_metrics.py`
- **Test**: Test with coding examples
- **Commit**: "feat: add coding-specific metrics"

#### Task 5.4: Content Metrics Calculator [30 min]
- **Agent**: backend-developer-agent
- **Actions**: Create `content_metrics.py`
- **Test**: Test with content examples
- **Commit**: "feat: add content-specific metrics"

#### Task 5.5: Cross-Domain Metrics [30 min]
- **Agent**: backend-developer-agent
- **Actions**: Create `cross_domain_metrics.py`
- **Test**: Test with cross-domain examples
- **Commit**: "feat: add cross-domain metrics"

#### Task 5.6: Failure Mode Analyzer [35 min]
- **Agent**: backend-developer-agent
- **Pre-task**: `Context7: error analysis ML`
- **Actions**: Implement failure pattern detection
- **Test**: Test with known failure cases
- **Commit**: "feat: add failure mode analysis"

#### Task 5.7: LLM-as-Judge Integration [40 min]
- **Agent**: ai-integration-agent
- **Pre-task**:
  - `Context7: LLM-as-judge implementation`
  - `WebSearch: "GPT-4 judge evaluation 2024"`
- **Actions**: Integrate judge model for quality scoring
- **Test**: Score 10 sample outputs
- **Commit**: "feat: add LLM-as-judge integration"

#### Task 5.8: Downstream A/B Testing [35 min]
- **Agent**: backend-developer-agent
- **Actions**: Implement GSM8K/HumanEval testing
- **Test**: Run on small subset
- **Commit**: "feat: add downstream uplift testing"

#### Task 5.9: Create eval_config.yaml [20 min]
- **Agent**: backend-developer-agent
- **Actions**: Create `configs/eval_config.yaml`
- **Test**: Validate configuration
- **Commit**: "feat: add evaluation configuration"

---

## 🖥️ PHASE 5: Serving Infrastructure (Milestone 6-6.5)

### Milestone 6: Inference Server

#### Task 6.1: Create FastAPI App [35 min]
- **Agent**: backend-developer-agent
- **Pre-task**:
  - `Context7: FastAPI best practices 2024`
  - `Read: PRD FR2 - modes`
- **Actions**: Create `server/app.py` with basic structure
- **Test**: `uvicorn server.app:app --reload`
- **Commit**: "feat: add FastAPI server foundation"

#### Task 6.2: Implement /enhance Endpoint [40 min]
- **Agent**: backend-developer-agent
- **Actions**: Add enhancement endpoint with lite/full modes
- **Test**: `httpie POST localhost:8000/enhance`
- **Commit**: "feat: add /enhance endpoint"

#### Task 6.3: Implement /health Endpoint [20 min]
- **Agent**: backend-developer-agent
- **Actions**: Add health check with version info
- **Test**: `httpie GET localhost:8000/health`
- **Commit**: "feat: add health check endpoint"

#### Task 6.4: Add Request Validation [30 min]
- **Agent**: security-specialist-agent
- **Pre-task**: `Context7: API input validation`
- **Actions**: Implement Pydantic models for validation
- **Test**: Test with invalid inputs
- **Commit**: "feat: add request validation"

#### Task 6.5: Implement Token Budgeting [35 min]
- **Agent**: performance-optimizer-agent
- **Actions**: Add token counting and limits for lite mode
- **Test**: Verify token limits enforced
- **Commit**: "feat: add token budgeting for lite mode"

### Milestone 6.5: Operational Framework

#### Task 6.6: Create Fallback Handler [35 min]
- **Agent**: backend-developer-agent
- **Pre-task**: `Context7: fallback patterns microservices`
- **Actions**: Create `server/fallback.py` with tiered fallback
- **Test**: Simulate primary model failure
- **Commit**: "feat: add tiered fallback mechanisms"

#### Task 6.7: Add Feedback Collection [30 min]
- **Agent**: backend-developer-agent
- **Actions**: Create `server/feedback.py` endpoint
- **Test**: Submit test feedback
- **Commit**: "feat: add user feedback collection"

#### Task 6.8: Schema Version Compatibility [30 min]
- **Agent**: backend-developer-agent
- **Actions**: Implement version upgrade logic
- **Test**: Test 1.0→1.2 upgrade
- **Commit**: "feat: add schema version compatibility"

#### Task 6.9: Add Monitoring Metrics [30 min]
- **Agent**: devops-agent
- **Pre-task**: `Context7: prometheus metrics fastapi`
- **Actions**: Add performance and usage metrics
- **Test**: Check metrics endpoint
- **Commit**: "feat: add monitoring metrics"

---

## 📚 PHASE 6: Production Readiness (Milestone 7)

### CI/CD Pipeline

#### Task 7.1: Setup GitHub Actions [30 min]
- **Agent**: devops-agent
- **Pre-task**: `Context7: GitHub Actions Python`
- **Actions**: Create `.github/workflows/ci.yml`
- **Test**: Push and verify CI runs
- **Commit**: "ci: add GitHub Actions workflow"

#### Task 7.2: Add License Verification [25 min]
- **Agent**: security-specialist-agent
- **Actions**: Add license check to CI
- **Test**: Test with non-commercial license
- **Commit**: "ci: add license verification gate"

#### Task 7.3: Add Schema Checks [25 min]
- **Agent**: backend-developer-agent
- **Actions**: Add schema validation to CI
- **Test**: Test with invalid schema
- **Commit**: "ci: add schema validation checks"

#### Task 7.4: Add Unit Tests [35 min]
- **Agent**: backend-developer-agent
- **Actions**: Create comprehensive unit tests
- **Test**: `pytest tests/unit --cov`
- **Commit**: "test: add comprehensive unit tests"

#### Task 7.5: Add Integration Tests [35 min]
- **Agent**: backend-developer-agent
- **Actions**: Create integration tests
- **Test**: `pytest tests/integration`
- **Commit**: "test: add integration tests"

### Documentation

#### Task 7.6: Create GETTING_STARTED.md [30 min]
- **Agent**: documentation-agent
- **Pre-task**: `Context7: technical documentation best practices`
- **Actions**: Write comprehensive getting started guide
- **Test**: Follow guide in fresh environment
- **Commit**: "docs: add getting started guide"

#### Task 7.7: Create REPRODUCIBILITY.md [25 min]
- **Agent**: documentation-agent
- **Actions**: Document seeds, versions, reproducibility
- **Test**: Verify all parameters documented
- **Commit**: "docs: add reproducibility guide"

#### Task 7.8: Create INTERNAL_AUDIT.md [25 min]
- **Agent**: documentation-agent
- **Actions**: Create pre-release checklists
- **Test**: Run through checklist
- **Commit**: "docs: add internal audit checklist"

#### Task 7.9: Create OPERATIONS.md [30 min]
- **Agent**: documentation-agent
- **Actions**: Document operational procedures
- **Test**: Verify all procedures covered
- **Commit**: "docs: add operations guide"

#### Task 7.10: Update DATA_MANIFEST.md [25 min]
- **Agent**: documentation-agent
- **Actions**: Complete dataset provenance documentation
- **Test**: Verify all datasets documented
- **Commit**: "docs: complete data manifest"

---

## 🎬 Final Tasks

#### Task F.1: End-to-End Testing [45 min]
- **Agent**: backend-developer-agent
- **Actions**: Run complete pipeline test
- **Test**: All acceptance tests pass
- **Commit**: "test: complete end-to-end validation"

#### Task F.2: Performance Benchmarking [40 min]
- **Agent**: performance-optimizer-agent
- **Pre-task**: `Context7: ML model benchmarking`
- **Actions**: Benchmark latency and throughput
- **Test**: Meet PRD performance targets
- **Commit**: "perf: add performance benchmarks"

#### Task F.3: Security Audit [35 min]
- **Agent**: security-specialist-agent
- **Pre-task**: `WebSearch: "ML API security checklist 2024"`
- **Actions**: Run security scan and fix issues
- **Test**: `bandit -r . && safety check`
- **Commit**: "security: complete security audit"

#### Task F.4: Docker Containerization [30 min]
- **Agent**: devops-agent
- **Pre-task**: `Context7: Docker best practices ML`
- **Actions**: Create production Dockerfile
- **Test**: `docker build && docker run`
- **Commit**: "feat: add Docker containerization"

#### Task F.5: Final Documentation Review [30 min]
- **Agent**: documentation-agent
- **Actions**: Review and update all documentation
- **Test**: Documentation complete and accurate
- **Commit**: "docs: final documentation review"

---

## 📊 Execution Tracking

### Success Metrics
- ✅ All 102 tasks completed
- ✅ Schema compliance ≥98%
- ✅ Domain-specific scores meet PRD targets
- ✅ All tests passing
- ✅ Documentation complete
- ✅ Performance targets met

### Daily Progress Tracking
```python
# Use this script to track progress
tasks_total = 102
tasks_completed = 0  # Update daily
progress = (tasks_completed / tasks_total) * 100
print(f"Progress: {progress:.1f}% ({tasks_completed}/{tasks_total} tasks)")
```

### Git Commit Convention
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `test:` Testing
- `perf:` Performance
- `ci:` CI/CD
- `chore:` Maintenance
- `security:` Security

---

## 🚦 Quality Gates

Each phase must pass these gates before proceeding:

### Phase 1 Gate (Foundation)
- [ ] Directory structure created
- [ ] All schemas valid
- [ ] Documentation templates ready

### Phase 2 Gate (Data)
- [ ] Data pipeline scripts working
- [ ] License verification passing
- [ ] Domain distribution correct

### Phase 3 Gate (Training)
- [ ] All training stages functional
- [ ] LoRA configuration verified
- [ ] Stage transitions working

### Phase 4 Gate (Evaluation)
- [ ] Evaluation metrics implemented
- [ ] LLM-as-judge integrated
- [ ] Downstream testing working

### Phase 5 Gate (Serving)
- [ ] API endpoints functional
- [ ] Fallback mechanisms tested
- [ ] Performance targets met

### Phase 6 Gate (Production)
- [ ] CI/CD pipeline green
- [ ] All documentation complete
- [ ] Security audit passed

---

## 🎯 Final Checklist (PRD Section 16)

- [ ] Verify Qwen3-30B A3B model ID and target_modules
- [ ] Confirm judge model availability
- [ ] Stand up repo skeleton with CI
- [ ] Prepare 1k-2k synthetic pilot dataset
- [ ] Review token budgets
- [ ] Document everything
- [ ] Implement domain router
- [ ] Set up fallback mechanisms
- [ ] Configure schema versioning
- [ ] Establish monitoring dashboard

---

## Notes

- Each task includes Context7 queries for latest best practices
- All code changes trigger `mcp__ide__getDiagnostics`
- Every task updates TodoWrite for progress tracking
- Git commits follow conventional commit format
- Tests must pass before moving to next task
- Documentation updated continuously
- CHANGELOG.md updated after each task
