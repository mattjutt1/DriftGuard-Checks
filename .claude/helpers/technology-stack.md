# TECHNOLOGY-STACK.md - Technology Stack and Dependencies

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

### **Superior Integration Patterns We've Established**
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
