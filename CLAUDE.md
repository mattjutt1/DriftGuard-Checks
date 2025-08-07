# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# PromptEvolver Development Framework
## Optimized Claude Code Agentic Development Protocol

### 🎯 FRAMEWORK OVERVIEW

This framework guides Claude Code through intelligent, hierarchical development of PromptEvolver using specialized subagents, MCP servers, and anti-over-engineering principles. Follow this protocol exactly to ensure efficient, quality-driven development.

## Project Overview

PromptEvolver is an AI-powered prompt optimization application that leverages Microsoft's PromptWizard framework with Qwen3:4b to create a self-evolving prompt generation system. The project focuses on proven technology choices and intelligent simplification over complexity for complexity's sake.

## Technology Stack (Optimized)

- **Backend**: Convex (serverless database with real-time updates)
- **Frontend**: Next.js 15.4.5 with React 19.1.0, TypeScript, Tailwind CSS
- **Build System**: Turbopack for ultra-fast development builds
- **AI Model**: Qwen3:4b (proven working model, 2.6GB efficient)
- **Framework**: Microsoft PromptWizard (MIT license)
- **Database**: Convex (serverless, real-time)
- **Deployment**: Vercel (frontend), Convex (backend)
- **Testing**: Jest, Playwright
- **Local AI**: Ollama for zero-cost AI processing
- **Performance**: React 19 concurrent features, optimized rendering

---

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

**IMPORTANT**: This project uses ONLY the following streamlined specialized sub-agents located in `.claude/agents/`:

- **backend-developer** - Enhanced with architectural decision-making, Convex development, serverless functions, PromptWizard integration
- **frontend-developer** - Next.js 15/React 19 specialist with UI/UX focus, responsive design, modern performance patterns
- **ai-integration** - Ollama + PromptWizard specialist, advanced error handling, retry logic, health checking
- **security-specialist** - Security + compliance expert, input validation, authentication, data protection
- **performance-optimizer** - Performance + monitoring specialist, build optimization, resource efficiency

---

## 🚫 ANTI-OVER-ENGINEERING PROTOCOL

### **KISS Principle Enforcement**
Keep It Simple, Stupid - Every decision must pass the simplicity test.

#### **Intelligent Simplification Rules**
1. **Value-Based Complexity**: Keep advanced features when they provide clear user benefits
2. **KISS with Intelligence**: Apply simplicity where it improves, not where it limits
3. **Evidence-Based Decisions**: Use data and user feedback to guide complexity decisions
4. **Technology Stack Optimization**: Choose superior current tech over forced downgrades
5. **Quality Over Compliance**: Focus on working quality measures over rigid tool requirements

### **Enhanced Solution Validation Process**
Before implementing any solution, validate:
1. Does this solve the CURRENT problem with clear user value?
2. Does this use proven technology patterns and best practices?
3. Will this solution scale appropriately for the expected usage?
4. Does this maintain or improve system reliability and performance?
5. Is this the most effective solution considering development time and quality?

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

---

## Architecture Overview

### System Components

```
Frontend (Next.js 15.4.5 + React 19)
├── Server and Client Components with React 19 optimizations
├── Real-time updates via Convex
├── TypeScript with Tailwind CSS
├── Turbopack for ultra-fast development builds
├── React 19 concurrent features
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

## 🏗️ INTELLIGENT CODE STRUCTURE APPROACH

### **Architecture Philosophy**
Use standard Next.js App Router structure enhanced with intelligent organization principles. Apply advanced patterns only when they provide clear user value, following KISS principles selectively rather than blindly.

### **Core Principles**
1. **Standard Patterns First**: Use proven Next.js App Router conventions
2. **Value-Based Complexity**: Preserve advanced features when they provide clear user benefits
3. **Intelligent Simplification**: Apply KISS principles where they improve, not where they limit
4. **Quality Over Compliance**: Focus on working quality measures over rigid tool compliance

### **Enhanced Next.js Structure**
```
app/                           # Next.js 15 App Router
├── (auth)/                    # Route groups for organization
│   ├── login/
│   └── register/
├── optimize/                  # Main optimization feature
│   ├── page.tsx
│   ├── components/            # Feature-specific components
│   └── actions.ts             # Server actions
├── dashboard/                 # Analytics and history
│   ├── page.tsx
│   └── components/
├── api/                       # API routes when needed
├── globals.css
└── layout.tsx

components/                    # Shared components
├── ui/                        # Reusable UI components
├── forms/                     # Form components
└── layout/                    # Layout components

lib/                          # Utilities and configurations
├── convex.ts                 # Convex client setup
├── utils.ts                  # Utility functions
└── types.ts                  # TypeScript types
```

### **Proven Implementation Patterns**

#### **Keep High-Value Features**
- **Dual-mode optimization**: Both single and batch processing (clear user value)
- **Quality metrics tracking**: Success rates, improvement scores (measurable benefits)
- **Advanced error handling**: Retry logic, graceful degradation (reliability improvement)
- **Real-time progress tracking**: WebSocket updates, status indicators (user experience)

#### **Intelligent Technology Choices**
- **Next.js 15 + React 19**: Latest stable versions with performance benefits
- **Turbopack**: Faster development builds (measurable improvement)
- **Standard App Router**: Proven patterns over forced complexity
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

## 🔐 SECURITY AND SECRET MANAGEMENT

### **Pragmatic Security Approach**

Implement security best practices without over-engineering. Focus on protecting actual sensitive data rather than theoretical threats.

### **Security Best Practices**
1. **Environment-Based Secrets**: Proper separation of dev/staging/production secrets
2. **Input Validation**: Comprehensive validation of all user inputs
3. **Authentication Security**: JWT with proper refresh token handling
4. **Rate Limiting**: Prevent abuse with intelligent rate limiting
5. **Audit Logging**: Track security events and access patterns

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

## Enhanced Quality Standards

- **Code Coverage**: Minimum 85% test coverage with focus on critical paths
- **Performance**: API responses <200ms, AI processing <5 seconds, React 19 optimizations
- **Security**: All inputs validated, JWT authentication, intelligent rate limiting
- **User Experience**: Dual-mode optimization, real-time progress, error recovery
- **Code Quality**: ESLint + TypeScript compliance, working quality over rigid formatting
- **Integration Quality**: Advanced error handling, retry logic, health checking
- **Technology Standards**: Next.js 15 + React 19 patterns, Turbopack optimization

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

## Enhanced Performance Targets

- **API Response Time**: <200ms (excluding AI processing)
- **AI Processing Time**: <5 seconds for prompt optimization
- **Memory Usage**: <4GB VRAM for Qwen3:4b model, <2GB RAM for application
- **Build Performance**: <5s development builds with Turbopack
- **Concurrent Users**: Support 100+ simultaneous optimizations
- **Database Queries**: <10ms for simple, <100ms for complex
- **React 19 Benefits**: Improved concurrent rendering, better hydration
- **Real-time Updates**: <100ms WebSocket response times

---

## 🎯 LEARNED BEST PRACTICES FRAMEWORK

### **Technology Stack Decision Criteria**

#### **When to Upgrade Technology**
- **Clear Performance Benefits**: Measurable improvements (Turbopack builds, React 19 rendering)
- **Stability and Support**: Mature release cycles with active maintenance
- **Developer Experience**: Improved development workflow and debugging
- **Ecosystem Compatibility**: Works well with existing tool chains
- **Future Proofing**: Aligns with technology direction trends

#### **When to Preserve Advanced Features**
- **User Value Test**: Features that directly improve user experience or outcomes
- **Measurable Benefits**: Can demonstrate clear improvements through metrics
- **Maintenance Cost**: Advanced features that don't significantly increase complexity
- **Competitive Advantage**: Features that differentiate from simpler alternatives

### **Integration Quality Standards**

#### **Superior Integration Patterns We've Established**
```typescript
// Advanced Error Handling with Retry Logic
export const optimizeWithRetry = async (prompt: string, maxRetries = 3) => {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await optimizePrompt(prompt);
    } catch (error) {
      if (attempt === maxRetries) throw error;
      await delay(Math.pow(2, attempt) * 1000); // Exponential backoff
    }
  }
};

// Health Checking Systems
export const checkOllamaHealth = async (): Promise<HealthStatus> => {
  try {
    const response = await fetch(`${OLLAMA_BASE_URL}/api/tags`);
    return { status: 'healthy', models: await response.json() };
  } catch (error) {
    return { status: 'unhealthy', error: error.message };
  }
};

// Multiple Parsing Strategies for AI Responses
export const parseAIResponse = (response: string): ParsedResponse => {
  // Try JSON parsing first
  try {
    return JSON.parse(response);
  } catch {
    // Fallback to regex extraction
    return extractWithRegex(response);
  }
};
```

#### **Real-time Progress Tracking Implementation**
```typescript
// WebSocket-based progress updates
export const trackOptimizationProgress = (sessionId: string) => {
  const progress = useConvexSubscription(api.sessions.watchProgress, { sessionId });

  return {
    stage: progress?.stage || 'queued',
    percentage: progress?.percentage || 0,
    estimatedTimeRemaining: progress?.estimatedTime || null,
    currentStep: progress?.currentStep || 'Initializing...'
  };
};
```

### **Intelligent Simplification Guidelines**

#### **Apply KISS Principles Intelligently (Not Blindly)**

**Keep Advanced When:**
- Dual-mode optimization provides clear user choice and value
- Quality metrics tracking enables data-driven improvements
- Error recovery systems improve reliability without adding complexity
- Real-time progress reduces user anxiety and improves perception

**Simplify When:**
- Complex abstractions don't provide proportional benefits
- Multiple similar components can be consolidated
- Configuration options overwhelm users without clear use cases
- Development tools create more friction than they solve

#### **Framework Compliance vs. Practical Benefits**

**Prioritize:**
1. **Working Quality**: Code that works reliably over code that passes arbitrary style checks
2. **User Experience**: Features that improve actual user outcomes
3. **Developer Productivity**: Tools and patterns that enable faster, better development
4. **Maintainability**: Code organization that facilitates future changes
5. **Performance**: Measurable improvements in speed, reliability, or resource usage

**De-prioritize:**
1. **Rigid Tool Compliance**: Perfect Prettier formatting over working features
2. **Architectural Purity**: Complex patterns that don't solve real problems
3. **Premature Optimization**: Performance work without measured bottlenecks
4. **Over-Abstraction**: Generic solutions for specific, simple problems

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

### **Technology Selection Philosophy**

#### **Superior Current Technology Over Forced Downgrades**

**Evidence-Based Choices:**
- **Next.js 15.4.5**: Latest stable with proven benefits (Turbopack, React 19 support)
- **React 19.1.0**: Concurrent features, improved hydration, better performance
- **Qwen3:4b**: Proven working model with optimal size/performance balance
- **Convex**: Serverless database with real-time features, excellent DX

**Avoid Forced Downgrades:**
- Don't downgrade to older Next.js versions without technical justification
- Don't use outdated React patterns when modern equivalents are superior
- Don't choose inferior AI models for theoretical simplicity
- Don't sacrifice developer experience for arbitrary constraints

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
1. **Never bypass streamlined agent hierarchy** - consult appropriate specialist agents
2. **Never apply rigid simplification blindly** - preserve valuable advanced features
3. **Never skip quality gates** - maintain enhanced quality standards
4. **Never downgrade technology without justification** - use superior current versions
5. **Never sacrifice user experience for theoretical purity** - prioritize working quality
6. **Never accumulate technical debt** - address issues with intelligent solutions
7. **Never skip version control** - every change must be committed with context
8. **Never ignore integration quality** - maintain error handling and health checking
9. **Never skip performance considerations** - leverage React 19 and Turbopack benefits
10. **Never compromise security** - implement pragmatic security without over-engineering

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

**Remember: This enhanced framework reflects our learned best practices. Follow these principles to build superior software that balances simplicity with advanced features where they provide clear value. We're building the future of prompt optimization through intelligent, streamlined, pragmatic development.**

**Let the specialized agents provide domain expertise. Use superior current technology. Focus on user value. Maintain working quality.**

🚀 **Ready to build PromptEvolver with proven best practices? Let's create something exceptional.**
