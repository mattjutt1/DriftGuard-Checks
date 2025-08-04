# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# PromptEvolver Development Framework
## Optimized Claude Code Agentic Development Protocol

### 🎯 FRAMEWORK OVERVIEW

This framework guides Claude Code through intelligent, hierarchical development of PromptEvolver using specialized subagents, MCP servers, and anti-over-engineering principles. Follow this protocol exactly to ensure efficient, quality-driven development.

## Project Overview

PromptEvolver is an AI-powered prompt optimization application that leverages Microsoft's PromptWizard framework with Qwen2.5-7B-Instruct to create a self-evolving prompt generation system.

## Technology Stack

- **Backend**: FastAPI, SQLAlchemy, Pydantic, Python 3.11
- **Frontend**: React 18+, TypeScript, Tailwind CSS, Zustand
- **AI Model**: Qwen2.5-7B-Instruct (Q4 quantization) via Ollama
- **Framework**: Microsoft PromptWizard (MIT license)
- **Database**: SQLite (development), PostgreSQL (production)
- **Caching**: Redis
- **Testing**: Pytest, Jest, Playwright
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions / GitLab CI

---

## 🏗️ HIERARCHICAL DECISION FRAMEWORK

### **Decision Chain Protocol**
```
Human Request → Specialized Agent → Implementation
```

**Always consult the appropriate specialist before proceeding.**

### **Authority Matrix**
- **backend-developer**: FastAPI development, API design, PromptWizard integration
- **frontend-developer**: React/TypeScript UI, user experience, responsive design  
- **ai-integration**: Ollama setup, model optimization, PromptWizard configuration
- **security-specialist**: Security implementation, vulnerability assessment, data protection
- **performance-optimizer**: Performance optimization, monitoring, resource efficiency
- **Human**: Final approval, business requirements, strategic direction

---

## 🤖 SUBAGENT INVOCATION PROTOCOL

### **Mandatory Subagent Usage**
Claude Code MUST use subagents for ALL specialized tasks. No exceptions.

```bash
# Correct approach - Always delegate to specialists
/agents backend-developer
/agents frontend-developer
/agents ai-integration
/agents security-specialist
/agents performance-optimizer

# WRONG - Never do direct implementation without agent consultation
# Writing code directly without subagent involvement
```

### **Available Specialized Sub-Agents**

**IMPORTANT**: This project uses ONLY the following specialized sub-agents located in `.claude/agents/`:

- **backend-developer** - FastAPI development, API design, PromptWizard integration
- **frontend-developer** - React/TypeScript UI, user experience, responsive design
- **ai-integration** - Ollama setup, model optimization, PromptWizard configuration
- **security-specialist** - Security implementation, vulnerability assessment, data protection
- **performance-optimizer** - Performance optimization, monitoring, resource efficiency

---

## 🚫 ANTI-OVER-ENGINEERING PROTOCOL

### **KISS Principle Enforcement**
Keep It Simple, Stupid - Every decision must pass the simplicity test.

#### **Over-Engineering Prevention Rules**
1. **YAGNI (You Aren't Gonna Need It)**: Don't implement features until they're actually needed
2. **DRY (Don't Repeat Yourself)**: But don't abstract until you have 3+ repetitions
3. **Single Responsibility**: Each component should do ONE thing well
4. **Minimal Viable Solution**: Start with the simplest solution that works
5. **Evidence-Based Complexity**: Only add complexity when data shows it's needed

### **Solution Validation Process**
Before implementing any solution, validate:
1. Does this solve the CURRENT problem? (not future problems)
2. Can this be implemented in <50 lines of code?
3. Does this use standard patterns without exotic abstractions?
4. Will a new developer understand this in 5 minutes?
5. Is this the simplest solution that could possibly work?

---

## 🎮 NO-CODE VIBE DEVELOPMENT APPROACH

### **Natural Language First Development**
Treat Claude Code as a no-code platform where you describe what you want, not how to build it.

#### **Communication Pattern**
```bash
# Good: Natural language requirements
"Create a prompt optimization endpoint that takes user input and returns improved prompts using PromptWizard"

# Bad: Technical implementation details
"Implement a FastAPI POST endpoint at /api/v1/optimize with request validation using Pydantic models and async processing with Celery workers"
```

### **Vibe-Driven Development Principles**
- **Intuitive First**: If it doesn't feel right, it probably isn't
- **User-Centric**: Always think from the user's perspective
- **Elegant Simplicity**: Beautiful solutions are usually simple solutions
- **Natural Flow**: Development should feel effortless and natural
- **Continuous Polish**: Small, continuous improvements over big rewrites

---

## 📋 DEVELOPMENT WORKFLOW PROTOCOL

### **Session Initialization**
Start every Claude Code session with this checklist:
1. Load CLAUDE.md context
2. Identify primary task and complexity
3. Select appropriate subagent
4. Validate against over-engineering principles
5. Begin development with KISS approach

### **Task Execution Pattern**
Mandatory workflow for every task:
1. **Complexity assessment** - Validate solution simplicity
2. **Specialized implementation** - Use appropriate sub-agent
3. **Quality verification** - Ensure standards are met

---

## Common Development Commands

### Backend Development
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run backend server locally
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run backend tests
pytest --cov=app --cov-report=html

# Format Python code
black app/

# Lint Python code
flake8 app/

# Security scan
bandit -r app/
safety check
```

### Frontend Development
```bash
# Install Node dependencies
npm install

# Run frontend development server
npm run dev

# Build for production
npm run build

# Run frontend tests
npm test

# Run E2E tests
npm run test:e2e

# Format JavaScript/TypeScript code
npx prettier --write "src/**/*.{js,jsx,ts,tsx}"

# Lint frontend code
npx eslint src/ --fix
```

### Docker Operations
```bash
# Start all services (development)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f [service_name]

# Rebuild containers
docker-compose build --no-cache

# Install Ollama model
docker exec ollama ollama pull qwen2.5:7b-instruct-q4_0
```

### Database Operations
```bash
# Run database migrations
alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "Description"

# Rollback migration
alembic downgrade -1

# Database backup
docker exec postgres pg_dump -U user promptevolver | gzip > backup.sql.gz

# Restore database
gunzip -c backup.sql.gz | docker exec -i postgres psql -U user -d promptevolver
```

---

## Architecture Overview

### System Components

```
Frontend (React/Next.js)
├── AI-Enhanced UI Components
├── Real-time WebSocket communication
├── State management with Zustand
└── Responsive Tailwind CSS design

Backend (FastAPI)  
├── RESTful API endpoints
├── PromptWizard integration layer
├── Async request processing
├── JWT authentication
└── Redis caching layer

AI Layer (Ollama)
├── Qwen2.5-7B-Instruct model
├── PromptWizard optimization framework
├── Batch processing capabilities
└── Learning system with feedback loop

Database (PostgreSQL/SQLite)
├── User management
├── Prompt storage and history
├── Optimization sessions tracking
├── Template library
└── Feedback collection
```

### Key API Endpoints

- **POST /api/v1/optimize** - Main prompt optimization endpoint
- **GET /api/v1/optimize/{task_id}** - Check optimization progress
- **POST /api/v1/feedback** - Submit user feedback for learning
- **GET /api/v1/history** - Retrieve user optimization history
- **GET /api/v1/templates** - Access prompt template library
- **GET /api/v1/health** - Health check and system status

### Database Schema

Primary tables:
- `users` - User authentication and preferences
- `prompts` - Original and optimized prompt pairs
- `optimization_sessions` - Processing sessions with metrics
- `user_feedback` - Ratings and improvement suggestions
- `prompt_templates` - Reusable prompt templates

---

## Quality Standards

- **Code Coverage**: Minimum 90% test coverage
- **Performance**: API responses <200ms, AI processing <5 seconds
- **Security**: All inputs validated, JWT authentication, rate limiting
- **Documentation**: All APIs documented with examples
- **Code Quality**: Passes linting, formatting, and security scans

## PromptWizard Configuration

```python
PROMPTWIZARD_CONFIG = {
    "mutate_refine_iterations": 3,
    "mutation_rounds": 3,
    "seen_set_size": 25,
    "few_shot_count": 3,
    "generate_reasoning": True,
    "generate_expert_identity": True,
    "temperature": 0.7,
    "max_tokens": 1024
}
```

## Performance Targets

- **API Response Time**: <200ms (excluding AI processing)
- **AI Processing Time**: <5 seconds for prompt optimization
- **Memory Usage**: <8GB VRAM for AI model, <2GB RAM for application
- **Concurrent Users**: Support 100+ simultaneous optimizations
- **Database Queries**: <10ms for simple, <100ms for complex

## Security Considerations

- JWT authentication with refresh tokens
- Input validation and sanitization
- Rate limiting on all endpoints
- Encrypted data at rest and in transit
- Regular security scanning and updates
- Docker security best practices

---

## 📋 AUTOMATED VERSION CONTROL & KNOWLEDGE GRAPH PROTOCOL

### **Repository Integration**
- **GitHub Repository**: https://github.com/mattjutt1/prompt-wizard.git
- **Branch Strategy**: main (production), develop (integration), feature/* (development)
- **Commit Convention**: Conventional Commits specification

### **Mandatory Post-Update Actions**
After EVERY code change, file modification, or task completion, Claude Code MUST execute:

```bash
# 1. Update Contextual Knowledge Graph
python .claude/scripts/update_knowledge_graph.py

# 2. Generate Contextual Embeddings  
python .claude/scripts/generate_embeddings.py

# 3. Update CHANGELOG.md
python .claude/scripts/update_changelog.py

# 4. Commit Changes to Git
python .claude/scripts/auto_commit.py

# 5. Update Context Vectors
python .claude/scripts/update_context_vectors.py
```

### **Knowledge Graph Architecture**
```python
# Contextual Knowledge Graph Structure
KNOWLEDGE_GRAPH = {
    "entities": {
        "files": {"type": "code_file", "metadata": {}, "embeddings": []},
        "functions": {"type": "function", "metadata": {}, "embeddings": []},
        "classes": {"type": "class", "metadata": {}, "embeddings": []},
        "agents": {"type": "subagent", "metadata": {}, "embeddings": []},
        "decisions": {"type": "architectural", "metadata": {}, "embeddings": []}
    },
    "relationships": {
        "depends_on": {"weight": 1.0, "context": "dependency"},
        "implements": {"weight": 0.8, "context": "implementation"},
        "uses": {"weight": 0.6, "context": "usage"},
        "modifies": {"weight": 0.9, "context": "modification"},
        "related_to": {"weight": 0.4, "context": "semantic"}
    },
    "context_vectors": {
        "current_session": [],
        "recent_changes": [],
        "architectural_patterns": [],
        "quality_metrics": []
    }
}
```

### **Embedding-Based Context Management**
```python
# Context Vector Generation
def generate_context_embeddings():
    contexts = {
        "code_context": extract_code_semantics(),
        "architectural_context": extract_design_patterns(),
        "decision_context": extract_decision_rationale(),
        "quality_context": extract_quality_metrics(),
        "temporal_context": extract_change_history()
    }
    
    for context_type, data in contexts.items():
        embedding = create_embedding(data)
        update_knowledge_graph(context_type, embedding)
```

### **Automated CHANGELOG Management**
```markdown
# CHANGELOG.md Format
## [Version] - Date

### Added
- New features and capabilities

### Changed  
- Modifications to existing functionality

### Fixed
- Bug fixes and corrections

### Technical
- Architecture changes, refactoring, dependencies

### Knowledge Graph
- Context updates, embedding improvements, relationship changes
```

### **Git Commit Automation**
```python
# Conventional Commit Format
COMMIT_TYPES = {
    "feat": "New feature or enhancement",
    "fix": "Bug fix or correction",
    "docs": "Documentation updates",
    "style": "Code formatting changes",
    "refactor": "Code refactoring without feature changes",
    "test": "Test additions or modifications",
    "chore": "Maintenance tasks",
    "graph": "Knowledge graph updates",
    "embed": "Embedding generation and updates"
}

# Auto-commit template
def generate_commit_message(changes):
    return f"{commit_type}({scope}): {description}\n\n🤖 Auto-generated by Claude Code\n📊 Knowledge graph updated\n🧠 Context embeddings refreshed"
```

---

## 🧠 CONTEXTUAL KNOWLEDGE GRAPH SYSTEM

### **Graph Database Schema**
```json
{
  "nodes": {
    "code_entities": ["files", "functions", "classes", "variables"],
    "architectural_entities": ["patterns", "decisions", "constraints"],
    "process_entities": ["tasks", "sessions", "commits"],
    "quality_entities": ["metrics", "tests", "reviews"],
    "context_entities": ["embeddings", "vectors", "relationships"]
  },
  "edges": {
    "structural": ["inherits", "implements", "contains", "imports"],
    "temporal": ["precedes", "follows", "triggers", "depends_on"],
    "semantic": ["similar_to", "related_to", "influences"],
    "quality": ["improves", "validates", "measures"]
  }
}
```

### **Embedding Strategy**
```python
# Multi-Modal Embedding Generation
EMBEDDING_MODELS = {
    "code_semantic": "microsoft/codebert-base",
    "architectural": "sentence-transformers/all-MiniLM-L6-v2", 
    "temporal": "custom_temporal_transformer",
    "quality": "custom_quality_embedder"
}

# Context Vector Dimensions
CONTEXT_DIMENSIONS = {
    "semantic_similarity": 384,
    "architectural_alignment": 256,
    "temporal_relevance": 128,
    "quality_correlation": 64
}
```

### **Claude Code Optimization Features**
```python
# Intelligent Context Retrieval
def get_relevant_context(query, max_tokens=4000):
    """Retrieve most relevant context based on embeddings"""
    query_embedding = generate_embedding(query)
    
    # Semantic search through knowledge graph
    relevant_nodes = graph.similarity_search(
        query_embedding, 
        top_k=20,
        filters=["recent", "high_quality", "architectural"]
    )
    
    # Contextual ranking
    ranked_context = rank_by_relevance(relevant_nodes, query_embedding)
    
    # Token-optimized context assembly
    return assemble_context(ranked_context, max_tokens)

# Predictive Context Loading  
def predict_needed_context(current_task):
    """Predict what context will be needed based on task patterns"""
    task_embedding = generate_embedding(current_task)
    
    # Find similar historical tasks
    similar_tasks = graph.find_similar_tasks(task_embedding)
    
    # Extract context patterns from successful completions
    context_patterns = extract_context_patterns(similar_tasks)
    
    # Pre-load predicted context
    return load_predicted_context(context_patterns)
```

---

## 🚨 MANDATORY BEHAVIORS

### **Things Claude Code MUST Always Do**
1. **Consult subagents** for ALL specialized tasks - no exceptions
2. **Apply KISS principles** to every solution
3. **Run quality gates** before and after implementation
4. **Update knowledge graph** after every change
5. **Generate contextual embeddings** for all modifications
6. **Update CHANGELOG.md** with every change
7. **Commit to git** with conventional commit messages
8. **Refresh context vectors** after updates
9. **Keep context focused** using natural language requirements
10. **Validate simplicity** before implementing complexity

### **Things Claude Code MUST Never Do**
1. **Never bypass subagent hierarchy** - always consult specialists
2. **Never over-engineer** - apply complexity assessment first
3. **Never skip quality gates** - maintain quality standards
4. **Never implement without specialist review** - consult appropriate agent
5. **Never create manual processes** - automate everything possible
6. **Never accumulate technical debt** - address issues immediately
7. **Never skip version control** - every change must be committed
8. **Never ignore knowledge graph updates** - context must stay current
9. **Never skip changelog updates** - maintain complete change history
10. **Never commit without embeddings** - ensure context vectors are updated

---

## 🎮 DEVELOPMENT VIBE CHECK

### **Continuous Vibe Assessment**
Does this feel effortless and natural?
Are we solving real problems elegantly?
Is the solution beautifully simple?
Would a new developer smile when seeing this?
Are we using the full power of our agent team?

### **Flow State Indicators**
- Subagents working in harmony
- Code emerging naturally from requirements
- Quality gates passing automatically
- Solutions feeling obvious in retrospect

---

**Remember: This framework is your bible. Follow it religiously. Every decision, every line of code, every architectural choice must align with these principles. We're building the future of prompt optimization through intelligent, hierarchical, anti-over-engineered, vibe-driven development.**

**Let the agents do what they do best. Keep it simple. Keep it beautiful. Keep it working.**

🚀 **Ready to build PromptEvolver the right way? Let's make magic happen.**