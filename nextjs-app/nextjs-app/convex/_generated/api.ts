// Temporary mock API file until Convex is properly configured
// This will be replaced by actual generated API when running `npx convex dev`

export const api = {
  optimizations: {
    createOptimizationRequest: () => {
      throw new Error("Convex not configured. Please run 'npx convex dev' to set up the backend.");
    }
  },
  actions: {
    optimizePromptWithOllama: () => {
      throw new Error("Convex not configured. Please run 'npx convex dev' to set up the backend.");
    },
    checkOllamaHealth: () => {
      throw new Error("Convex not configured. Please run 'npx convex dev' to set up the backend.");
    }
  },
  sessions: {
    getRecentSessions: () => {
      throw new Error("Convex not configured. Please run 'npx convex dev' to set up the backend.");
    }
  }
};