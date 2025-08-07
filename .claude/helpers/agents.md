# AGENTS.md - Sub-Agent System and Delegation

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

**IMPORTANT**: This project uses ONLY the following streamlined specialized sub-agents located in `.claude/agents/`:

- **backend-developer** - Enhanced with architectural decision-making, Convex development, serverless functions, PromptWizard integration
- **frontend-developer** - Next.js 15/React 19 specialist with UI/UX focus, responsive design, modern performance patterns
- **ai-integration** - Ollama + PromptWizard specialist, advanced error handling, retry logic, health checking
- **security-specialist** - Security + compliance expert, input validation, authentication, data protection
- **performance-optimizer** - Performance + monitoring specialist, build optimization, resource efficiency

## 🏗️ HIERARCHICAL DECISION FRAMEWORK

### **Decision Chain Protocol**
```
Human Request → Specialized Agent → Implementation
```

**Always consult the appropriate specialist before proceeding.**

### **Authority Matrix (Streamlined 5-Agent System)**
- **backend-developer**: Convex development, serverless functions, PromptWizard integration, architectural decisions
- **frontend-developer**: Next.js 15/React 19 UI, user experience, responsive design, performance optimization
- **ai-integration**: Ollama setup, Qwen3:4b optimization, PromptWizard configuration, AI response handling
- **security-specialist**: Security implementation, vulnerability assessment, data protection, compliance
- **performance-optimizer**: Performance monitoring, optimization strategies, resource efficiency, build optimization
- **Human**: Final approval, business requirements, strategic direction

### **Agent Utilization Best Practices**

#### **Streamlined 5-Agent System Benefits**
- **Reduced Communication Overhead**: Fewer handoffs, clearer responsibilities
- **Enhanced Domain Expertise**: Each agent covers broader, more cohesive domain
- **Faster Decision Making**: Less bureaucratic processes, more action
- **Better Context Retention**: Agents maintain deeper understanding of their domains

#### **When to Delegate vs. Direct Implementation**

**Delegate to Agents When:**
- Domain-specific expertise required (security, performance, AI integration)
- Complex architectural decisions needed
- Best practices consultation required
- Quality assurance and validation needed

**Direct Implementation When:**
- Simple, straightforward changes within established patterns
- Minor bug fixes with clear solutions
- Documentation updates and maintenance tasks
- Configuration changes following established procedures

### **Sub-Agent Architecture Alignment**
- **frontend-developer**: Responsible for atoms, molecules, and feature-specific components
- **backend-developer**: Handles API endpoints (pages), services (organisms), and data models
- **ai-integration**: Manages AI-specific atoms and molecules within optimization feature
- **security-specialist**: Reviews authentication feature and cross-cutting security concerns
- **performance-optimizer**: Optimizes shared components and critical path organisms