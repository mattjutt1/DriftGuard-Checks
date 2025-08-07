# DEPLOYMENT.md - Deployment Strategies

## Deployment Configuration

### **Technology Stack Deployment**
- **Frontend**: Vercel (Next.js 15.4.5 + React 19 optimized)
- **Backend**: Convex (serverless, auto-scaling)
- **AI Processing**: Ollama (local development), HuggingFace Spaces (production)
- **Database**: Convex (managed, real-time)

### **Deployment Targets**
- **Development**: Local Ollama + Convex dev environment
- **Staging**: Vercel preview + Convex staging
- **Production**: Vercel + Convex production + HuggingFace Spaces

### **Environment Configuration**
```bash
# Development
CONVEX_URL=https://your-dev-convex.convex.cloud
OLLAMA_BASE_URL=http://localhost:11434
NEXT_PUBLIC_CONVEX_URL=https://your-dev-convex.convex.cloud

# Production
CONVEX_URL=https://your-prod-convex.convex.cloud
HUGGINGFACE_API_URL=https://your-space.hf.space
NEXT_PUBLIC_CONVEX_URL=https://your-prod-convex.convex.cloud
```

### **Deployment Pipeline**
```bash
# 1. Frontend (Vercel)
npm run build
vercel --prod

# 2. Backend (Convex)
npx convex deploy --prod

# 3. Database Schema
npx convex schema push --prod

# 4. Environment Verification
npm run verify:production
```

### **Performance Considerations**
- **Build Optimization**: Turbopack for fast builds
- **Edge Deployment**: Vercel Edge Functions for global performance
- **Caching Strategy**: Convex automatic caching + CDN
- **Image Optimization**: Next.js Image component + Vercel optimization

### **Monitoring and Health Checks**
```typescript
// Health check endpoints
export const healthCheck = {
  convex: () => convex.query(api.health.check),
  ollama: () => fetch(`${OLLAMA_BASE_URL}/api/tags`),
  frontend: () => fetch('/api/health')
};

// Performance monitoring
export const performanceMetrics = {
  buildTime: "< 30s with Turbopack",
  deployTime: "< 2 minutes end-to-end",
  firstLoad: "< 3s on 3G networks",
  apiResponse: "< 200ms average"
};
```

### **Rollback Strategy**
```bash
# Convex rollback
npx convex rollback --to-version <version>

# Vercel rollback
vercel rollback <deployment-url>

# Database schema rollback
npx convex schema rollback --to-version <version>
```