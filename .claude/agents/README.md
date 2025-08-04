# PromptEvolver Specialized Sub-Agents

This directory contains 12 specialized sub-agents organized in a 4-tier hierarchy for the PromptEvolver project.

## Agent Hierarchy

### **Tier 1: Executive Agents**
- **architect-agent** - System architecture design, technical decisions, and overall system structure planning
- **orchestrator-agent** - Project coordination, task delegation, workflow management, and development timeline oversight

### **Tier 2: Specialized Development Agents**
- **backend-developer-agent** - Server-side development, API design, PromptWizard integration, and backend architecture
- **frontend-developer-agent** - User interface development, React components, user experience design, and responsive frontend
- **ai-integration-agent** - AI model integration, Ollama setup, PromptWizard configuration, and model optimization
- **database-agent** - Database design, schema optimization, query performance, and data modeling

### **Tier 3: Quality Assurance Agents**
- **testing-agent** - Comprehensive testing strategy, test automation, quality assurance, and test coverage optimization
- **security-agent** - Security implementation, vulnerability assessment, data protection, and security audit
- **performance-agent** - Performance optimization, monitoring, scalability analysis, and resource efficiency

### **Tier 4: Support Agents**
- **documentation-agent** - Technical documentation, user guides, API docs, and knowledge base maintenance
- **devops-agent** - Deployment automation, infrastructure management, CI/CD pipelines, and environment setup
- **research-agent** - Technology research, best practices, innovation discovery, and competitive analysis

## Usage

To invoke a specific agent:
```bash
claude /agents agent-name
```

For example:
```bash
claude /agents architect-agent
claude /agents backend-developer-agent
claude /agents frontend-developer-agent
```

## Agent Format

All agents follow the official Claude Code sub-agent format:
```markdown
---
name: agent-name
description: Brief description of agent responsibilities
---

[Agent system prompt and detailed specifications]
```

Each agent is specifically tailored for the PromptEvolver project requirements and includes:
- Core responsibilities
- Technical specifications
- Integration points with other project components
- Quality standards and metrics
- Implementation guidelines

## Integration

These agents work together hierarchically:
1. **Tier 1** provides strategic direction and coordination
2. **Tier 2** handles core development work
3. **Tier 3** ensures quality and security
4. **Tier 4** provides supporting infrastructure and research

All agents are designed to collaborate effectively while maintaining clear separation of concerns and expertise domains.