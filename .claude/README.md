# PromptEvolver Framework Automation

This directory contains the automated systems for the PromptEvolver development framework.

## 🤖 Automation Scripts

### Core Automation Pipeline
After every code change, Claude Code MUST execute these scripts in order:

```bash
# 1. Update Knowledge Graph
python .claude/scripts/update_knowledge_graph.py

# 2. Generate Contextual Embeddings  
python .claude/scripts/generate_embeddings.py

# 3. Update CHANGELOG.md
python .claude/scripts/update_changelog.py

# 4. Commit to Git
python .claude/scripts/auto_commit.py

# 5. Update Context Vectors
python .claude/scripts/update_context_vectors.py
```

### Script Descriptions

#### `update_knowledge_graph.py`
- Scans project files for entities (files, functions, classes, agents)
- Detects changes and relationships
- Builds comprehensive knowledge graph
- Output: `.claude/knowledge_graph.json`

#### `generate_embeddings.py`
- Generates semantic embeddings for all entities
- Creates context vectors for similarity search
- Supports code, agent, and architectural embeddings
- Output: `.claude/embeddings.json`

#### `update_changelog.py`
- Automatically updates CHANGELOG.md
- Uses conventional commit format
- Categorizes changes (Added, Changed, Fixed, Technical, Knowledge Graph)
- Version management with semantic versioning
- Output: Updated `CHANGELOG.md`

#### `auto_commit.py`
- Commits all changes with conventional commit messages
- Auto-generates descriptive commit messages
- Pushes to GitHub repository
- Includes automation metadata

#### `update_context_vectors.py`
- Generates Claude Code-optimized context vectors
- Calculates quality metrics and recommendations
- Creates session context and architectural patterns
- Output: `.claude/context_vectors.json`

## 📊 Generated Files

### Knowledge Graph (`knowledge_graph.json`)
```json
{
  "entities": {
    "files": {"type": "code_file", "metadata": {}, "embeddings": []},
    "agents": {"type": "subagent", "metadata": {}, "embeddings": []},
    "decisions": {"type": "architectural", "metadata": {}}
  },
  "relationships": {
    "depends_on": {"weight": 1.0, "context": "dependency"},
    "implements": {"weight": 0.8, "context": "implementation"}
  }
}
```

### Embeddings (`embeddings.json`)
- 384-dimensional vectors for all entities
- Semantic similarity search capabilities
- Code, agent, and architectural embeddings
- Hash-based consistency tracking

### Context Vectors (`context_vectors.json`)
- Current session context
- Architectural patterns
- Quality metrics
- Claude Code optimization hints

### Version Info (`version.json`)
- Current semantic version
- Last update timestamp
- Version history tracking

## 🎯 Integration with Claude Code

The automation system is designed to optimize Claude Code CLI performance:

### Intelligent Context Loading
- Predicts needed context based on task patterns
- Pre-loads relevant embeddings
- Optimizes token usage with similarity search

### Quality-Driven Development
- Maintains quality score (target: >0.8)
- Provides recommendations for improvement
- Tracks completeness and consistency

### Session Optimization
- Tracks active agents and recent changes
- Maintains architectural pattern awareness
- Provides contextual hints for development

## 🔧 Configuration

### Repository Settings
- **GitHub Repository**: https://github.com/mattjutt1/prompt-wizard.git
- **Branch Strategy**: main (production), develop (integration)
- **Commit Convention**: Conventional Commits specification

### Quality Thresholds
- **Completeness**: >80% files with embeddings
- **Consistency**: All agents have embeddings
- **Freshness**: Recent changes tracked
- **Quality Score**: >0.8 overall

## 🚨 Framework Compliance

This automation system enforces the PromptEvolver development framework:

### Mandatory Behaviors
1. ✅ Update knowledge graph after every change
2. ✅ Generate contextual embeddings for all modifications
3. ✅ Update CHANGELOG.md with every change
4. ✅ Commit to git with conventional commit messages
5. ✅ Refresh context vectors after updates

### Quality Gates
- All scripts must complete successfully
- Knowledge graph must be consistent
- Embeddings must be generated for all entities
- Changelog must be updated
- Git commits must follow conventional format

This system ensures that PromptEvolver development follows the optimized framework while maintaining comprehensive context for Claude Code CLI.