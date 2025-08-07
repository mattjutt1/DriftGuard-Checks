# DEVELOPMENT.md - Development Workflow and Commands

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

## Common Development Commands

### Backend Development (Convex)
```bash
# Install dependencies
npm install

# Start Convex development server
npx convex dev

# Deploy Convex functions
npx convex deploy

# Push schema changes
npx convex schema push

# View Convex dashboard
npx convex dashboard
```

### Frontend Development (Next.js 15.4.5 + React 19)
```bash
# Install dependencies
npm install

# Run development server (with Turbopack)
npm run dev --turbo

# Build for production
npm run build

# Start production server
npm run start

# Run tests
npm test

# Run E2E tests
npm run test:e2e

# Quality tools (pragmatic approach)
npx eslint src/ --fix  # ESLint + TypeScript sufficient
# Note: Prettier optional - focus on working quality over rigid formatting
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
ollama pull qwen3:4b
```

### Convex Operations
```bash
# View Convex functions
npx convex functions list

# Run Convex function locally
npx convex run myFunction --args '{"key": "value"}'

# Import data to Convex
npx convex import --table myTable data.jsonl

# Export data from Convex
npx convex export --table myTable --output data.jsonl

# Clear all data (development only)
npx convex run _system/clear --table myTable
```

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

## 🧠 CONTEXTUAL KNOWLEDGE GRAPH SYSTEM

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