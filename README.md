# PromptEvolver - Development Demo

⚠️ **DEVELOPMENT DEMO - NOT PRODUCTION READY** ⚠️

This is a development demonstration of prompt optimization using Microsoft's PromptWizard methodology. This application is designed for local development only and has significant limitations.

## Current Status

### ⏱️ Performance Warning
- **Processing Time**: 60-120 seconds per optimization
- **Architecture**: Local development only (localhost:11434)
- **AI Model**: Qwen3:4b (2.6GB local model)

### 🔧 Technical Limitations
- **Local Only**: Requires Ollama running on localhost:11434
- **No Production Deploy**: Architecture will fail in production environments
- **Basic Implementation**: Uses system prompts, not actual PromptWizard framework
- **Development Grade**: Not optimized for real-world usage

## What Actually Works

✅ **Local Development Demo**
- Basic prompt input/output interface
- Ollama + Qwen3:4b integration
- Simple health checking
- Basic session history

❌ **What's NOT Implemented**
- Production-ready architecture
- Actual PromptWizard framework integration
- Performance optimization
- Advanced error handling
- Production deployment compatibility

## Technology Stack

- **Frontend**: Next.js 15.4.5 + React 19.1.0
- **Backend**: Convex (serverless database)
- **AI**: Local Ollama + Qwen3:4b model
- **Build**: Turbopack for development
- **Styling**: Tailwind CSS

## Quick Start (Local Development Only)

### Prerequisites
1. Node.js 18+
2. Ollama installed locally
3. Qwen3:4b model downloaded

### Setup
```bash
# Clone repository
git clone https://github.com/mattjutt1/prompt-wizard.git
cd prompt-wizard

# Install Ollama model
ollama pull qwen3:4b

# Start Ollama service
ollama serve

# Install dependencies
cd nextjs-app
npm install

# Start development servers
npm run dev          # Next.js frontend
npx convex dev       # Convex backend
```

### Usage
1. Navigate to http://localhost:3000
2. Enter a prompt for optimization
3. Wait 60-120 seconds for processing
4. Review the "optimized" result

## Performance Expectations

| Operation | Time | Notes |
|-----------|------|-------|
| Health Check | <5s | Basic connectivity test |
| Prompt Optimization | 60-120s | Varies by prompt length |
| Model Loading | 10-30s | First-time startup |

## Architecture Notes

### Current Architecture (Development Only)
```
Next.js Frontend (localhost:3000)
    ↓
Convex Actions (serverless)
    ↓
Ollama API (localhost:11434)
    ↓
Qwen3:4b Model (local)
```

### Why This Won't Work in Production
- **Localhost Dependency**: Hardcoded localhost:11434 URLs
- **Local Model**: Requires 2.6GB Qwen3:4b model on server
- **No Load Balancing**: Single-threaded processing
- **No Error Recovery**: Basic error handling only

## Version History (Honest)

- **v0.1.0**: Initial development demo
  - Basic Ollama integration
  - Simple UI implementation
  - Local development setup
  - NOT production ready

## Contributing

This is a development demonstration. For production use cases:

1. Replace localhost architecture with cloud-based AI APIs
2. Implement actual PromptWizard framework (not just system prompts)
3. Add proper error handling and retry logic
4. Optimize for production performance
5. Add comprehensive testing

## License

MIT License - See LICENSE file for details

## Disclaimer

This application is intended for development and demonstration purposes only. Do not deploy to production without significant architectural changes.