# Claude.md - PromptEvolver Development Framework

## AI Development Framework & Workflow Hierarchy

This document defines the structured approach for building PromptEvolver using Claude Code with specialized subagents and automated hooks. Follow this framework strictly to ensure consistency, quality, and efficient development.

---

## 🏗️ SUBAGENT WORKFLOW HIERARCHY

### **Tier 1: Executive Agents (Strategic Level)**

#### 1. **Architect Agent**
- **Role**: System architecture design and technical decision making
- **Responsibilities**: Define overall system structure, technology stack decisions, integration patterns
- **Authority**: Can override technical decisions, defines coding standards
- **Reports to**: Human developer
- **Manages**: All Tier 2 agents

#### 2. **Orchestrator Agent** 
- **Role**: Project coordination and workflow management
- **Responsibilities**: Task delegation, progress tracking, resource allocation, timeline management
- **Authority**: Assigns tasks to specialized agents, manages dependencies
- **Reports to**: Architect Agent
- **Manages**: All development agents

### **Tier 2: Specialized Development Agents**

#### 3. **Backend Developer Agent**
- **Role**: Server-side development and API design
- **Responsibilities**: FastAPI implementation, database integration, PromptWizard integration
- **Specialization**: Python, FastAPI, SQLite/PostgreSQL, API design
- **Reports to**: Orchestrator Agent

#### 4. **Frontend Developer Agent**
- **Role**: User interface development and user experience
- **Responsibilities**: React components, state management, responsive design
- **Specialization**: React, TypeScript, Tailwind CSS, responsive design
- **Reports to**: Orchestrator Agent

#### 5. **AI Integration Agent**
- **Role**: AI model integration and optimization
- **Responsibilities**: Ollama setup, PromptWizard configuration, model optimization
- **Specialization**: LLM integration, prompt optimization, model fine-tuning
- **Reports to**: Orchestrator Agent

#### 6. **Database Agent**
- **Role**: Data modeling and database optimization
- **Responsibilities**: Schema design, query optimization, data migration
- **Specialization**: SQLite, PostgreSQL, data modeling, performance tuning
- **Reports to**: Backend Developer Agent

### **Tier 3: Quality Assurance Agents**

#### 7. **Testing Agent**
- **Role**: Comprehensive testing strategy and implementation
- **Responsibilities**: Unit tests, integration tests, E2E testing, test automation
- **Specialization**: Pytest, Jest, Playwright, test-driven development
- **Reports to**: Orchestrator Agent

#### 8. **Security Agent**
- **Role**: Security implementation and vulnerability assessment
- **Responsibilities**: Security audits, input validation, encryption, threat modeling
- **Specialization**: Application security, data protection, vulnerability assessment
- **Reports to**: Architect Agent

#### 9. **Performance Agent**
- **Role**: Performance optimization and monitoring
- **Responsibilities**: Code optimization, resource monitoring, scalability analysis
- **Specialization**: Performance profiling, optimization techniques, monitoring
- **Reports to**: Backend Developer Agent

### **Tier 4: Support Agents**

#### 10. **Documentation Agent**
- **Role**: Comprehensive documentation creation and maintenance
- **Responsibilities**: API docs, user guides, technical documentation, knowledge graph updates
- **Specialization**: Technical writing, API documentation, user experience documentation
- **Reports to**: Orchestrator Agent

#### 11. **DevOps Agent**
- **Role**: Deployment and infrastructure management
- **Responsibilities**: Docker configuration, CI/CD pipelines, environment setup
- **Specialization**: Docker, deployment automation, environment management
- **Reports to**: Architect Agent

#### 12. **Research Agent**
- **Role**: Technology research and best practices
- **Responsibilities**: Technology evaluation, best practice research, innovation discovery
- **Specialization**: Technology trends, research methodology, competitive analysis
- **Reports to**: Architect Agent

---

## 🔄 AUTOMATED HOOKS CONFIGURATION

### **PostToolUse Hooks (After every code change)**

#### 1. **Changelog Update Hook**
```bash
# Auto-update CHANGELOG.md after any file modification
jq -r '.tool_input.file_path' | {
  read file_path;
  if [ -n "$file_path" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Modified: $file_path" >> CHANGELOG.md;
    echo "  - $(jq -r '.tool_input.description // "File modification"')" >> CHANGELOG.md;
  fi;
}
```

#### 2. **Claude.md Update Hook**
```bash
# Update this document with latest context and decisions
jq -r '.tool_input' | {
  read tool_data;
  echo "## Latest Development Context" > /tmp/claude_update.md;
  echo "**Updated**: $(date '+%Y-%m-%d %H:%M:%S')" >> /tmp/claude_update.md;
  echo "**Last Action**: $(echo $tool_data | jq -r '.description // "Unknown action"')" >> /tmp/claude_update.md;
  echo "" >> /tmp/claude_update.md;
  cat /tmp/claude_update.md claude.md > /tmp/claude_new.md && mv /tmp/claude_new.md claude.md;
}
```

#### 3. **Knowledge Graph Update Hook**
```bash
# Update knowledge graph with new relationships and entities
python3 << 'EOF'
import json, sys, datetime
from pathlib import Path

# Read tool input
tool_data = json.load(sys.stdin)
file_path = tool_data.get('tool_input', {}).get('file_path', '')
description = tool_data.get('tool_input', {}).get('description', '')

if file_path:
    # Determine file type and relationships
    file_type = Path(file_path).suffix
    timestamp = datetime.datetime.now().isoformat()
    
    # Load or create knowledge graph
    kg_file = Path('knowledgegraph.md')
    kg_content = kg_file.read_text() if kg_file.exists() else "# PromptEvolver Knowledge Graph\n\n"
    
    # Add new entity and relationships
    entity_section = f"\n## File Entity: {file_path}\n"
    entity_section += f"- **Type**: {file_type}\n"
    entity_section += f"- **Last Modified**: {timestamp}\n"
    entity_section += f"- **Description**: {description}\n"
    entity_section += f"- **Dependencies**: [To be analyzed]\n"
    entity_section += f"- **Related Components**: [To be mapped]\n\n"
    
    kg_content += entity_section
    kg_file.write_text(kg_content)
EOF
```

#### 4. **Code Quality Hook**
```bash
# Run code formatting and linting after changes
jq -r '.tool_input.file_path' | {
  read file_path;
  if echo "$file_path" | grep -q '\.py$'; then
    black "$file_path" 2>/dev/null || echo "Black formatting failed";
    flake8 "$file_path" 2>/dev/null || echo "Flake8 linting completed";
  elif echo "$file_path" | grep -q '\.(ts|tsx|js|jsx)$'; then
    npx prettier --write "$file_path" 2>/dev/null || echo "Prettier formatting failed";
    npx eslint "$file_path" --fix 2>/dev/null || echo "ESLint completed";
  fi;
}
```

### **PreToolUse Hooks (Before actions)**

#### 1. **Context Validation Hook**
```bash
# Validate context before major operations
jq -r '.tool_name' | {
  read tool_name;
  if [ "$tool_name" = "Write" ] || [ "$tool_name" = "MultiEdit" ]; then
    echo "🔍 Validating context for $tool_name operation...";
    echo "📋 Current agent context: $(echo $CLAUDE_AGENT_CONTEXT)";
    echo "✅ Context validation complete";
  fi;
}
```

#### 2. **Backup Hook**
```bash
# Create backups before significant changes
jq -r '.tool_input.file_path' | {
  read file_path;
  if [ -f "$file_path" ]; then
    backup_dir=".backups/$(date '+%Y%m%d')";
    mkdir -p "$backup_dir";
    cp "$file_path" "$backup_dir/$(basename $file_path).$(date '+%H%M%S').bak";
    echo "📦 Backup created for $file_path";
  fi;
}
```

### **Stop Hooks (After task completion)**

#### 1. **Knowledge Graph Synthesis Hook**
```bash
# Synthesize knowledge graph after major development sessions
python3 << 'EOF'
import re
from pathlib import Path
from collections import defaultdict
import datetime

def analyze_codebase():
    """Analyze codebase and update knowledge graph relationships"""
    
    # File relationships
    relationships = defaultdict(list)
    
    # Scan Python files for imports
    for py_file in Path('.').rglob('*.py'):
        if py_file.is_file():
            content = py_file.read_text()
            imports = re.findall(r'from\s+(\S+)\s+import|import\s+(\S+)', content)
            for imp in imports:
                module = imp[0] or imp[1]
                if module:
                    relationships[str(py_file)].append(f"imports:{module}")
    
    # Scan React files for imports
    for js_file in Path('.').rglob('*.{ts,tsx,js,jsx}'):
        if js_file.is_file():
            content = js_file.read_text()
            imports = re.findall(r'import.*from\s+[\'"]([^\'"]+)[\'"]', content)
            for imp in imports:
                relationships[str(js_file)].append(f"imports:{imp}")
    
    # Update knowledge graph
    kg_content = "# PromptEvolver Knowledge Graph\n\n"
    kg_content += f"**Last Updated**: {datetime.datetime.now().isoformat()}\n\n"
    
    kg_content += "## System Architecture\n"
    kg_content += "- **Frontend**: React + TypeScript + Tailwind CSS\n"
    kg_content += "- **Backend**: FastAPI + Python\n"
    kg_content += "- **AI**: Ollama + Qwen2.5-7B-Instruct + PromptWizard\n"
    kg_content += "- **Database**: SQLite (dev) / PostgreSQL (prod)\n\n"
    
    kg_content += "## Component Relationships\n"
    for file_path, deps in relationships.items():
        kg_content += f"\n### {file_path}\n"
        for dep in deps:
            kg_content += f"- {dep}\n"
    
    Path('knowledgegraph.md').write_text(kg_content)
    print("📊 Knowledge graph updated with current relationships")

analyze_codebase()
EOF
```

#### 2. **Progress Report Hook**
```bash
# Generate development progress report
python3 << 'EOF'
import datetime
from pathlib import Path

def generate_progress_report():
    """Generate comprehensive progress report"""
    
    report = f"# Development Progress Report\n"
    report += f"**Generated**: {datetime.datetime.now().isoformat()}\n\n"
    
    # Count files by type
    file_counts = {}
    for file_path in Path('.').rglob('*'):
        if file_path.is_file() and not file_path.name.startswith('.'):
            suffix = file_path.suffix or 'no_extension'
            file_counts[suffix] = file_counts.get(suffix, 0) + 1
    
    report += "## File Statistics\n"
    for ext, count in sorted(file_counts.items()):
        report += f"- {ext}: {count} files\n"
    
    report += "\n## Recent Changes\n"
    if Path('CHANGELOG.md').exists():
        changelog = Path('CHANGELOG.md').read_text()
        recent_changes = '\n'.join(changelog.split('\n')[:20])  # Last 20 lines
        report += f"```\n{recent_changes}\n```\n"
    
    Path('progress_report.md').write_text(report)
    print("📈 Progress report generated")

generate_progress_report()
EOF
```

---

## 📋 DEVELOPMENT WORKFLOW

### **Phase 1: Initialization**
1. **Architect Agent** defines system architecture
2. **Orchestrator Agent** creates development roadmap
3. Initialize hooks configuration
4. Create initial project structure

### **Phase 2: Core Development**
1. **Backend Developer Agent** implements API structure
2. **AI Integration Agent** sets up Ollama and PromptWizard
3. **Frontend Developer Agent** creates React components
4. **Database Agent** designs and implements schema

### **Phase 3: Integration & Testing**
1. **Testing Agent** implements comprehensive test suite
2. **Security Agent** performs security audit
3. **Performance Agent** optimizes system performance
4. Integration testing across all components

### **Phase 4: Documentation & Deployment**
1. **Documentation Agent** creates comprehensive docs
2. **DevOps Agent** sets up deployment pipeline
3. **Research Agent** evaluates final implementation
4. Final knowledge graph synthesis

---

## 🎯 QUALITY GATES

### **Code Quality**
- All code must pass automated formatting (Black, Prettier)
- Unit test coverage >90%
- Security scan must pass
- Performance benchmarks must meet requirements

### **Documentation Quality**
- All APIs documented
- User guides complete
- Knowledge graph updated
- Progress reports generated

### **Architecture Quality**
- Design patterns followed
- SOLID principles applied
- Security best practices implemented
- Performance requirements met

---

## 🔧 TOOLS & INTEGRATIONS

### **Required Tools**
- **Ollama**: Local LLM deployment
- **PromptWizard**: Microsoft's prompt optimization framework
- **Docker**: Containerization
- **Git**: Version control with automated hooks

### **Development Stack**
- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Frontend**: React, TypeScript, Tailwind CSS, Zustand
- **AI**: Qwen2.5-7B-Instruct (quantized)
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Testing**: Pytest, Jest, Playwright

---

## 📊 MONITORING & METRICS

### **Development Metrics**
- Lines of code per component
- Test coverage percentage
- Security vulnerabilities count
- Performance benchmark results

### **AI Metrics**
- Prompt optimization success rate
- Model response time
- Memory usage
- User satisfaction scores

---

## 🚀 DEPLOYMENT STRATEGY

### **Local Development**
- Docker Compose for multi-service orchestration
- Hot reloading for rapid development
- Local Ollama instance for AI processing

### **Production**
- Containerized deployment
- Load balancing for high availability
- Monitoring and logging integration
- Automated backup systems

---

## Latest Development Context
**Updated**: 2025-08-04 06:00:00
**Current Phase**: Initialization
**Active Agents**: All agents initialized and ready
**Next Milestone**: Core development phase initiation

---

*This document is automatically updated by Claude Code hooks and should be referenced by all agents during development.*