# ARCHITECTURE.md - Project Architecture and Structure

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

### **AVSHA Architecture Pattern**

#### **Frontend Structure (Next.js/React)**
```
features/                       # Feature-specific vertical slices
├── authentication/
│   ├── atoms/
│   │   ├── LoginButton.tsx
│   │   └── AuthIcon.tsx
│   ├── molecules/
│   │   ├── LoginForm.tsx
│   │   └── AuthStatus.tsx
│   ├── organisms/
│   │   ├── AuthLayout.tsx
│   │   └── UserMenu.tsx
│   ├── templates/
│   │   └── AuthTemplate.tsx
│   ├── pages/
│   │   ├── LoginPage.tsx
│   │   └── RegisterPage.tsx
│   ├── api/
│   │   └── authApi.ts
│   ├── store/
│   │   └── authStore.ts
│   └── types/
│       └── auth.types.ts
│
├── optimization/
│   ├── atoms/
│   │   ├── PromptInput.tsx
│   │   └── LoadSpinner.tsx
│   ├── molecules/
│   │   ├── PromptEditor.tsx
│   │   └── ResultView.tsx
│   ├── organisms/
│   │   ├── OptimizeFlow.tsx
│   │   └── HistoryList.tsx
│   ├── templates/
│   │   └── OptimizeTemplate.tsx
│   ├── pages/
│   │   ├── OptimizePage.tsx
│   │   └── HistoryPage.tsx
│   ├── api/
│   │   └── optimizeApi.ts
│   ├── store/
│   │   └── optimizeStore.ts
│   └── types/
│       └── optimize.types.ts
│
└── dashboard/
    ├── atoms/
    │   ├── MetricCard.tsx
    │   └── StatusIcon.tsx
    ├── molecules/
    │   ├── MetricPanel.tsx
    │   └── ChartWidget.tsx
    ├── organisms/
    │   ├── DashboardGrid.tsx
    │   └── ReportView.tsx
    ├── templates/
    │   └── DashTemplate.tsx
    ├── pages/
    │   ├── DashboardPage.tsx
    │   └── AnalyticsPage.tsx
    ├── api/
    │   └── dashboardApi.ts
    ├── store/
    │   └── dashboardStore.ts
    └── types/
        └── dashboard.types.ts
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