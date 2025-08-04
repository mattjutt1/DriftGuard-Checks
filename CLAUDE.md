# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# PromptEvolver Development Framework
## Optimized Claude Code Agentic Development Protocol

### 🎯 FRAMEWORK OVERVIEW

This framework guides Claude Code through intelligent, hierarchical development of PromptEvolver using specialized subagents, MCP servers, and anti-over-engineering principles. Follow this protocol exactly to ensure efficient, quality-driven development.

## Project Overview

PromptEvolver is an AI-powered prompt optimization application that leverages Microsoft's PromptWizard framework with Qwen3-4B to create a self-evolving prompt generation system.

## Technology Stack

- **Backend**: Convex (serverless database with real-time updates)
- **Frontend**: Next.js 14, React 18+, TypeScript, Tailwind CSS
- **AI Model**: Qwen3-4B (Q4 quantization) via Ollama
- **Framework**: Microsoft PromptWizard (MIT license)
- **Database**: Convex (serverless, real-time)
- **Deployment**: Vercel (frontend), Convex (backend)
- **Testing**: Jest, Playwright
- **Local AI**: Ollama for zero-cost AI processing

---

## 🏗️ HIERARCHICAL DECISION FRAMEWORK

### **Decision Chain Protocol**
```
Human Request → Specialized Agent → Implementation
```

**Always consult the appropriate specialist before proceeding.**

### **Authority Matrix**
- **backend-developer**: Convex development, serverless functions, PromptWizard integration
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

- **backend-developer** - Convex development, serverless functions, PromptWizard integration
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

### Frontend Development (Next.js 14)
```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm run start

# Run tests
npm test

# Run E2E tests
npm run test:e2e

# Format code
npx prettier --write "src/**/*.{js,jsx,ts,tsx}"

# Lint code
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

---

## Architecture Overview

### System Components

```
Frontend (Next.js 14)
├── Server and Client Components
├── Real-time updates via Convex
├── TypeScript with Tailwind CSS
└── Responsive design patterns

Backend (Convex)  
├── Serverless functions
├── Real-time database
├── TypeScript-first development
├── Built-in authentication
└── Automatic scaling

AI Layer (Ollama)
├── Qwen3-4B model (2.6GB)
├── PromptWizard optimization framework
├── Local processing capabilities
└── Learning system with feedback loop

Database (Convex)
├── User management
├── Prompt storage and history
├── Optimization sessions tracking
├── Template library
└── Feedback collection
```

### Key Convex Functions

- **optimizations.createOptimizationRequest** - Create new optimization session
- **actions.optimizePromptWithOllama** - Execute prompt optimization with AI
- **sessions.getRecentSessions** - Retrieve user optimization history
- **actions.checkOllamaHealth** - Health check for Ollama service
- **feedback.submitFeedback** - Submit user feedback for learning
- **templates.getTemplates** - Access prompt template library

### Database Schema

Primary tables:
- `users` - User authentication and preferences
- `prompts` - Original and optimized prompt pairs
- `optimization_sessions` - Processing sessions with metrics
- `user_feedback` - Ratings and improvement suggestions
- `prompt_templates` - Reusable prompt templates

---

## 🏛️ ATOMIC VERTICAL SLICE HYBRID ARCHITECTURE (AVSHA)

### **Architecture Philosophy**
AVSHA combines the component hierarchy of Atomic Design with the feature-focused organization of Vertical Slice Architecture, creating a two-dimensional matrix that optimizes both reusability and maintainability.

### **Core Principles**
1. **Atomic Hierarchy**: Components organized by complexity (Atoms → Molecules → Organisms → Templates → Pages)
2. **Feature Cohesion**: Related functionality grouped into cohesive vertical slices
3. **Hybrid Organization**: Two-dimensional structure balancing reusability and feature focus
4. **Scalable Growth**: Architecture that scales with team size and feature complexity

### **AVSHA Matrix Structure**
```
                 Features →
Component Level ↓
┌─────────────┬──────────────┬──────────────┬──────────────┐
│             │ Authentication│ Optimization │ Dashboard    │
├─────────────┼──────────────┼──────────────┼──────────────┤
│ Atoms       │ LoginButton  │ PromptInput  │ MetricCard   │
│             │ InputField   │ LoadSpinner  │ StatusIcon   │
├─────────────┼──────────────┼──────────────┼──────────────┤
│ Molecules   │ LoginForm    │ PromptEditor │ MetricPanel  │
│             │ AuthStatus   │ ResultView   │ ChartWidget  │
├─────────────┼──────────────┼──────────────┼──────────────┤
│ Organisms   │ AuthLayout   │ OptimizeFlow │ DashboardGrid│
│             │ UserMenu     │ HistoryList  │ ReportView   │
├─────────────┼──────────────┼──────────────┼──────────────┤
│ Templates   │ AuthTemplate │ OptimizeTemplate│ DashTemplate│
├─────────────┼──────────────┼──────────────┼──────────────┤
│ Pages       │ LoginPage    │ OptimizePage │ DashboardPage│
│             │ RegisterPage │ HistoryPage  │ AnalyticsPage│
└─────────────┴──────────────┴──────────────┴──────────────┘
```

### **Folder Organization Strategy**

#### **Frontend Structure (React/TypeScript)**
```
src/
├── shared/                         # Cross-feature shared components
│   ├── atoms/                      # Base UI building blocks
│   │   ├── Button/
│   │   ├── Input/
│   │   └── Icon/
│   ├── molecules/                  # Simple composed components
│   │   ├── SearchBox/
│   │   ├── Modal/
│   │   └── Tooltip/
│   └── organisms/                  # Complex reusable components
│       ├── Header/
│       ├── Sidebar/
│       └── Footer/
│
├── features/                       # Feature-specific vertical slices
│   ├── authentication/
│   │   ├── atoms/
│   │   │   ├── LoginButton.tsx
│   │   │   └── AuthIcon.tsx
│   │   ├── molecules/
│   │   │   ├── LoginForm.tsx
│   │   │   └── AuthStatus.tsx
│   │   ├── organisms/
│   │   │   ├── AuthLayout.tsx
│   │   │   └── UserMenu.tsx
│   │   ├── templates/
│   │   │   └── AuthTemplate.tsx
│   │   ├── pages/
│   │   │   ├── LoginPage.tsx
│   │   │   └── RegisterPage.tsx
│   │   ├── api/
│   │   │   └── authApi.ts
│   │   ├── store/
│   │   │   └── authStore.ts
│   │   └── types/
│   │       └── auth.types.ts
│   │
│   ├── optimization/
│   │   ├── atoms/
│   │   │   ├── PromptInput.tsx
│   │   │   └── LoadSpinner.tsx
│   │   ├── molecules/
│   │   │   ├── PromptEditor.tsx
│   │   │   └── ResultView.tsx
│   │   ├── organisms/
│   │   │   ├── OptimizeFlow.tsx
│   │   │   └── HistoryList.tsx
│   │   ├── templates/
│   │   │   └── OptimizeTemplate.tsx
│   │   ├── pages/
│   │   │   ├── OptimizePage.tsx
│   │   │   └── HistoryPage.tsx
│   │   ├── api/
│   │   │   └── optimizeApi.ts
│   │   ├── store/
│   │   │   └── optimizeStore.ts
│   │   └── types/
│   │       └── optimize.types.ts
│   │
│   └── dashboard/
│       ├── atoms/
│       │   ├── MetricCard.tsx
│       │   └── StatusIcon.tsx
│       ├── molecules/
│       │   ├── MetricPanel.tsx
│       │   └── ChartWidget.tsx
│       ├── organisms/
│       │   ├── DashboardGrid.tsx
│       │   └── ReportView.tsx
│       ├── templates/
│       │   └── DashTemplate.tsx
│       ├── pages/
│       │   ├── DashboardPage.tsx
│       │   └── AnalyticsPage.tsx
│       ├── api/
│       │   └── dashboardApi.ts
│       ├── store/
│       │   └── dashboardStore.ts
│       └── types/
│           └── dashboard.types.ts
│
└── app/                           # Application-level configuration
    ├── templates/                 # Page-level templates
    │   └── AppTemplate.tsx
    ├── pages/                     # Top-level pages
    │   └── HomePage.tsx
    └── router/
        └── AppRouter.tsx
```

#### **Backend Structure (Convex/TypeScript)**
```
convex/
├── shared/                        # Cross-feature shared functions
│   ├── atoms/                     # Base utilities and primitives
│   │   ├── validators.ts
│   │   ├── serializers.ts
│   │   └── errors.ts
│   ├── molecules/                 # Composed utilities
│   │   ├── auth.ts
│   │   ├── cache.ts
│   │   └── adapters.ts
│   └── organisms/                 # Complex reusable systems
│       ├── database.ts
│       ├── monitoring.ts
│       └── integrations.ts
│
├── features/                      # Feature-specific vertical slices
│   ├── authentication/
│   │   ├── atoms/
│   │   │   ├── tokenGenerator.ts
│   │   │   └── passwordHasher.ts
│   │   ├── molecules/
│   │   │   ├── authValidator.ts
│   │   │   └── jwtHandler.ts
│   │   ├── organisms/
│   │   │   ├── authService.ts
│   │   │   └── userManager.ts
│   │   ├── queries/               # Convex queries
│   │   │   └── users.ts
│   │   ├── mutations/             # Convex mutations
│   │   │   └── auth.ts
│   │   ├── actions/               # External API actions
│   │   │   └── authActions.ts
│   │   └── schema/
│   │       └── userSchema.ts
│   │
│   ├── optimization/
│   │   ├── atoms/
│   │   │   ├── promptParser.ts
│   │   │   └── qualityScorer.ts
│   │   ├── molecules/
│   │   │   ├── promptwizardAdapter.ts
│   │   │   └── resultFormatter.ts
│   │   ├── organisms/
│   │   │   ├── optimizationService.ts
│   │   │   └── historyManager.ts
│   │   ├── queries/
│   │   │   └── optimizations.ts
│   │   ├── mutations/
│   │   │   └── sessions.ts
│   │   ├── actions/
│   │   │   └── ollamaActions.ts
│   │   └── schema/
│   │       └── promptSchema.ts
│   │
│   └── dashboard/
│       ├── atoms/
│       │   ├── metric_calculator.py
│       │   └── data_aggregator.py
│       ├── molecules/
│       │   ├── report_generator.py
│       │   └── chart_builder.py
│       ├── organisms/
│       │   ├── analytics_service.py
│       │   └── dashboard_service.py
│       ├── templates/
│       │   ├── dashboard_requests.py
│       │   └── dashboard_responses.py
│       ├── pages/
│       │   └── dashboard_router.py
│       ├── models/
│       │   └── metrics.py
│       └── tests/
│           └── test_dashboard.py
│
├── schema.ts                      # Main Convex schema
├── _generated/                    # Auto-generated Convex files
└── convex.config.ts              # Convex configuration
```

### **AVSHA Decision Framework**

#### **Component Placement Decision Tree**
```
1. Is this component used across multiple features?
   YES → Place in /shared/
   NO  → Place in specific /features/{feature}/

2. What is the component's complexity level?
   - Single responsibility, no dependencies → atoms/
   - Combines 2-5 atoms → molecules/
   - Complex business logic, multiple molecules → organisms/
   - Layout and structure patterns → templates/
   - Full application screens → pages/

3. Is this a cross-cutting concern?
   YES → Create as organism in /shared/ with feature-specific adapters
   NO  → Keep within feature boundary

4. Does this need to be tested independently?
   YES → Ensure clear interface boundaries and dependency injection
   NO  → Consider if it should be refactored for better testability
```

#### **Feature Slice Criteria**
- **High Cohesion**: All components serve the same business capability
- **Loose Coupling**: Minimal dependencies on other features
- **Clear Boundaries**: Well-defined APIs between features
- **Independent Deployment**: Feature can be developed and deployed independently

### **Implementation Guidelines**

#### **For Atoms (Basic Building Blocks)**
```typescript
// Example: shared/atoms/Button/Button.tsx
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'danger';
  size: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  onClick?: () => void;
}

export const Button: React.FC<ButtonProps> = ({ 
  variant, size, children, onClick 
}) => {
  const baseClasses = "font-medium rounded-lg transition-colors";
  const variantClasses = {
    primary: "bg-blue-600 text-white hover:bg-blue-700",
    secondary: "bg-gray-200 text-gray-900 hover:bg-gray-300",
    danger: "bg-red-600 text-white hover:bg-red-700"
  };
  
  return (
    <button 
      className={`${baseClasses} ${variantClasses[variant]}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
};
```

#### **For Feature Organisms (Complex Components)**
```typescript
// Example: features/optimization/organisms/OptimizeFlow.tsx
import { PromptEditor } from '../molecules/PromptEditor';
import { ResultView } from '../molecules/ResultView';
import { useOptimizeStore } from '../store/optimizeStore';

export const OptimizeFlow: React.FC = () => {
  const { 
    currentPrompt, 
    optimizedPrompt, 
    isOptimizing, 
    optimizePrompt 
  } = useOptimizeStore();

  return (
    <div className="optimize-flow">
      <PromptEditor 
        value={currentPrompt}
        onChange={setCurrentPrompt}
      />
      <ResultView 
        result={optimizedPrompt}
        isLoading={isOptimizing}
      />
    </div>
  );
};
```

### **Integration with Development Workflow**

#### **Sub-Agent Architecture Alignment**
- **frontend-developer**: Responsible for atoms, molecules, and feature-specific components
- **backend-developer**: Handles API endpoints (pages), services (organisms), and data models
- **ai-integration**: Manages AI-specific atoms and molecules within optimization feature
- **security-specialist**: Reviews authentication feature and cross-cutting security concerns
- **performance-optimizer**: Optimizes shared components and critical path organisms

#### **AVSHA Quality Gates**
1. **Atomic Validation**: Each atom has single responsibility and clear interface
2. **Molecular Composition**: Molecules properly compose atoms without tight coupling
3. **Organism Boundaries**: Complex components maintain clear dependencies
4. **Feature Cohesion**: Feature slices maintain high internal cohesion
5. **Cross-Feature Coupling**: Minimal dependencies between feature slices
6. **Template Consistency**: Layout patterns are consistent across features
7. **Page Integration**: Top-level pages properly integrate all layers

#### **Knowledge Graph Integration**
```python
# AVSHA-specific knowledge graph entities
AVSHA_ENTITIES = {
    "atomic_components": {
        "atoms": ["buttons", "inputs", "icons"],
        "molecules": ["forms", "cards", "modals"],
        "organisms": ["headers", "sidebars", "workflows"],
        "templates": ["layouts", "patterns"],
        "pages": ["screens", "routes"]
    },
    "feature_slices": {
        "boundaries": ["authentication", "optimization", "dashboard"],
        "cohesion_metrics": ["internal_coupling", "external_dependencies"],
        "api_contracts": ["requests", "responses", "events"]
    },
    "architectural_decisions": {
        "component_placement": ["shared_vs_feature", "complexity_level"],
        "feature_boundaries": ["cohesion_criteria", "coupling_metrics"],
        "reusability_patterns": ["abstraction_level", "usage_frequency"]
    }
}
```

### **Migration Strategy for Existing Code**
1. **Audit Current Structure**: Map existing components to AVSHA matrix
2. **Identify Shared Components**: Move cross-feature components to `/shared/`
3. **Create Feature Boundaries**: Group related functionality into feature slices
4. **Establish Component Hierarchy**: Organize components by atomic complexity
5. **Implement Gradually**: Migrate feature by feature to minimize disruption
6. **Update Import Patterns**: Establish clear import rules and dependencies
7. **Validate Architecture**: Ensure each component follows AVSHA principles

### **AVSHA Success Metrics**
- **Reusability Score**: Percentage of components used across multiple contexts
- **Feature Cohesion**: Internal coupling vs. external dependencies ratio
- **Development Velocity**: Time to implement new features using existing components
- **Maintenance Efficiency**: Time to modify functionality without breaking changes
- **Code Discoverability**: Developer time to locate and understand components
- **Test Coverage**: Independent testability of atomic components and feature slices

---

## 🔐 INFISICAL SECRET MANAGEMENT DEVELOPMENT ENVIRONMENT

### **Current Development Setup**

PromptEvolver uses **Infisical** as the development environment for secure secret management while we research and design our simplified PromptVault clone.

### **Why Infisical for Development?**
1. **Learn from Production Tool**: Experience real-world secret management to design PromptVault better
2. **Immediate Security**: Secure our development secrets right now
3. **AVSHA Integration**: Organize secrets according to our architectural framework
4. **Requirements Gathering**: Document what our simplified clone needs to replicate

### **Infisical Services**
- **Web UI**: http://localhost:8080 - Infisical dashboard for secret management
- **Database**: PostgreSQL with persistent storage
- **Cache**: Redis for sessions and performance
- **API**: RESTful API for programmatic access

### **Management Commands**
```bash
# Service Management
./infisical-manage.sh start      # Start all services
./infisical-manage.sh stop       # Stop all services
./infisical-manage.sh status     # Check service status
./infisical-manage.sh logs       # View logs

# Project Setup
./infisical-manage.sh setup-project  # Guide for creating PromptEvolver project
./infisical-manage.sh cli            # Install Infisical CLI

# Maintenance
./infisical-manage.sh backup     # Backup data and config
./infisical-manage.sh reset      # DANGER: Delete all data
```

### **AVSHA-Organized Secret Structure**

#### **Feature-Based Secret Organization**
Following our AVSHA framework, secrets are organized by feature:

**Authentication Feature Secrets:**
```
Environment: development
├── JWT_SECRET_KEY           # JWT token signing key
├── JWT_REFRESH_SECRET       # JWT refresh token key  
├── OAUTH_CLIENT_ID          # OAuth client identifier
├── OAUTH_CLIENT_SECRET      # OAuth client secret
└── SESSION_SECRET_KEY       # Session encryption key
```

**Optimization Feature Secrets:**
```
Environment: development
├── OPENAI_API_KEY          # OpenAI API access key
├── ANTHROPIC_API_KEY       # Anthropic API access key
├── PROMPTWIZARD_CONFIG     # PromptWizard configuration
├── OLLAMA_BASE_URL         # Ollama server URL
└── AI_MODEL_CONFIG         # AI model configuration
```

**Dashboard Feature Secrets:**
```
Environment: development  
├── ANALYTICS_API_KEY       # Analytics service key
├── MONITORING_TOKEN        # Monitoring service token
├── GRAFANA_API_KEY         # Grafana dashboard key
├── PROMETHEUS_CONFIG       # Prometheus configuration
└── SENTRY_DSN             # Error tracking DSN
```

### **Development Workflow**

#### **Initial Setup (One-time)**
```bash
# 1. Start Infisical
./infisical-manage.sh start

# 2. Create admin account at http://localhost:8080
# 3. Download Emergency Kit PDF (CRITICAL!)
# 4. Create "PromptEvolver" project
# 5. Create environments: development, staging, production

# 6. Install CLI
npm install -g @infisical/cli
infisical login --domain=http://localhost:8080
```

#### **Daily Development Workflow**
```bash
# 1. Ensure Infisical is running
./infisical-manage.sh status

# 2. Access secrets via CLI
infisical secrets get JWT_SECRET_KEY --env=development
infisical secrets set OPENAI_API_KEY "sk-..." --env=development

# 3. Export secrets to .env files
infisical export --env=development --format=dotenv > .env.development
infisical export --env=production --format=dotenv > .env.production

# 4. Use in FastAPI application
# Secrets automatically loaded from .env.development
```

### **Integration with Automation Pipeline**

#### **Enhanced security-specialist Sub-Agent**
The security-specialist agent now includes Infisical management:

```bash
# When /agents security-specialist is activated
/agents security-specialist

# Agent automatically:
# 1. Checks Infisical service status
# 2. Validates secret organization follows AVSHA structure  
# 3. Ensures no hardcoded secrets in commits
# 4. Reviews secret access audit logs
# 5. Provides security recommendations
```

#### **Mandatory Secret Management Actions**
Before EVERY commit involving configuration or secrets:

```bash
# 1. Check Infisical services
./infisical-manage.sh status

# 2. Validate secret organization
infisical projects list

# 3. Export latest secrets  
infisical export --env=development --format=dotenv > .env.development

# 4. Scan for hardcoded secrets (manual for now)
grep -r "sk-" --exclude-dir=.git --exclude="*.md" .

# 5. Update knowledge graph
python .claude/scripts/update_knowledge_graph.py
```

### **AVSHA Integration Points**

#### **Shared Components (Future PromptVault)**
Based on Infisical usage, we'll need these AVSHA components:

```
shared/
├── atoms/
│   ├── SecretInput/         # Masked input (like Infisical's secret forms)
│   ├── EnvironmentBadge/    # Environment indicator (dev/staging/prod)
│   └── SecretStrength/      # Secret validation indicator
├── molecules/  
│   ├── SecretForm/          # Add/edit secret forms
│   ├── SecretList/          # List secrets with masking
│   └── EnvironmentSwitcher/ # Switch between environments
└── organisms/
    ├── SecretManager/       # Complete secret dashboard
    ├── ProjectManager/      # Manage secret projects/groups
    └── AuditViewer/         # View access logs and audit trail
```

#### **Feature Integration**
Each feature integrates with Infisical:

**FastAPI Backend Integration:**
```python
# app/shared/organisms/secret_loader.py  
import os
from dotenv import load_dotenv

def load_development_secrets():
    """Load secrets from Infisical-exported .env file"""
    load_dotenv('.env.development')
    return {
        'jwt_secret': os.getenv('JWT_SECRET_KEY'),
        'openai_key': os.getenv('OPENAI_API_KEY'),
        'database_url': os.getenv('DATABASE_URL')
    }

# app/features/authentication/config.py
from shared.organisms.secret_loader import load_development_secrets
secrets = load_development_secrets()
JWT_SECRET_KEY = secrets['jwt_secret']
```

### **Learning Objectives for PromptVault**

Using Infisical teaches us what PromptVault needs:

#### **Essential Features to Replicate**
1. **Web UI**: Simple, clean interface for secret management
2. **Environment Separation**: Clear dev/staging/prod organization  
3. **CLI Integration**: Command-line tool for automation
4. **Export Functionality**: Generate .env files for applications
5. **Audit Logging**: Track who accessed what and when
6. **Project Organization**: Group secrets by application/feature

#### **Simplifications for PromptVault**
1. **Single User**: Remove team/organization features
2. **Local Storage**: File-based instead of database
3. **Basic Auth**: Master password instead of complex auth
4. **Minimal UI**: Focus on essential functionality
5. **Git Integration**: Built-in secret scanning and pre-commit hooks

#### **AVSHA Enhancements**  
1. **Feature-Based Organization**: Automatic grouping by AVSHA features
2. **Framework Integration**: Native integration with our automation pipeline
3. **Component Generation**: Auto-generate secret management UI components
4. **Development Workflow**: Optimized for individual developer productivity

### **Security Best Practices (Current)**

#### **Infisical Security Rules**
1. **Emergency Kit**: Always download and safely store the Emergency Kit PDF
2. **Strong Master Password**: Use a unique, strong password for Infisical admin
3. **Environment Separation**: Never mix dev/staging/prod secrets
4. **Regular Backups**: Use `./infisical-manage.sh backup` weekly
5. **Access Monitoring**: Review audit logs in Infisical dashboard regularly

#### **Development Security Workflow**
```bash
# 1. Daily security check
./infisical-manage.sh status
infisical audit-logs --limit 10

# 2. Before commits
grep -r "sk-\|jwt_secret\|api_key" --exclude-dir=.git .
# Should return no results (except in .env files)

# 3. Rotate secrets monthly
infisical secrets update JWT_SECRET_KEY "$(openssl rand -base64 32)" --env=development

# 4. Backup before major changes
./infisical-manage.sh backup
```

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