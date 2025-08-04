import { action } from "./_generated/server";
import { v } from "convex/values";
import { api } from "./_generated/api";

// Action to optimize prompt using external Ollama API
export const optimizePromptWithOllama = action({
  args: {
    sessionId: v.id("optimizationSessions"),
  },
  handler: async (ctx, { sessionId }) => {
    try {
      // Get session details
      const session = await ctx.runQuery(api.optimizations.getSession, { sessionId });
      if (!session) throw new Error("Session not found");

      // Get prompt details
      const prompt = await ctx.runQuery(api.sessions.getPrompt, { promptId: session.promptId });
      if (!prompt) throw new Error("Prompt not found");

      const startTime = Date.now();

      // Call Ollama API (or Qwen3 8B model)
      const ollamaResponse = await fetch("http://localhost:11434/api/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: "qwen3:8b",
          prompt: `You are an expert prompt optimization assistant. Your task is to improve the following prompt to make it clearer, more specific, and more effective.

Original prompt: "${prompt.originalPrompt}"

Context domain: ${prompt.contextDomain || "general"}

Please provide:
1. An optimized version of the prompt
2. A list of specific improvements made
3. A quality score from 1-10

Respond in this exact JSON format:
{
  "optimized_prompt": "your optimized prompt here",
  "improvements": ["improvement 1", "improvement 2", "improvement 3"],
  "quality_score": 8.5,
  "metrics": {
    "clarity": 9.0,
    "specificity": 8.0,
    "engagement": 8.5
  }
}`,
          stream: false,
        }),
      });

      if (!ollamaResponse.ok) {
        throw new Error(`Ollama API error: ${ollamaResponse.statusText}`);
      }

      const ollamaData = await ollamaResponse.json();
      const processingTime = Date.now() - startTime;

      // Parse the response
      let optimizationResult;
      try {
        // Try to extract JSON from the response
        const jsonMatch = ollamaData.response.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          optimizationResult = JSON.parse(jsonMatch[0]);
        } else {
          throw new Error("No JSON found in response");
        }
      } catch (parseError) {
        // Fallback if JSON parsing fails
        optimizationResult = {
          optimized_prompt: ollamaData.response,
          improvements: ["Restructured for clarity", "Enhanced specificity", "Improved engagement"],
          quality_score: 7.5,
          metrics: {
            clarity: 7.5,
            specificity: 7.5,
            engagement: 7.5,
          },
        };
      }

      // Update the optimization session with results
      await ctx.runMutation(api.optimizations.updateOptimizationResults, {
        sessionId,
        optimizedPrompt: optimizationResult.optimized_prompt,
        qualityScore: optimizationResult.quality_score,
        processingTimeMs: processingTime,
        improvements: optimizationResult.improvements,
        metrics: optimizationResult.metrics,
      });

      return {
        success: true,
        sessionId,
        processingTime,
        qualityScore: optimizationResult.quality_score,
      };
    } catch (error) {
      // Mark optimization as failed
      await ctx.runMutation(api.optimizations.markOptimizationFailed, {
        sessionId,
        errorMessage: error instanceof Error ? error.message : "Unknown error",
      });

      throw error;
    }
  },
});

// Health check action for Ollama service
export const checkOllamaHealth = action({
  args: {},
  handler: async () => {
    try {
      const response = await fetch("http://localhost:11434/api/tags", {
        method: "GET",
      });

      if (!response.ok) {
        return {
          healthy: false,
          error: `Ollama service unavailable: ${response.statusText}`,
        };
      }

      const data = await response.json();
      const qwen3Model = data.models?.find((model: any) => 
        model.name.includes("qwen3") || model.name.includes("qwen3:8b")
      );

      return {
        healthy: true,
        models: data.models?.map((m: any) => m.name) || [],
        qwen3Available: !!qwen3Model,
        message: qwen3Model 
          ? "Qwen3 8B model is available"
          : "Qwen3 8B model not found. Please run: ollama pull qwen3:8b",
      };
    } catch (error) {
      return {
        healthy: false,
        error: error instanceof Error ? error.message : "Unknown error",
        message: "Please ensure Ollama service is running: ollama serve",
      };
    }
  },
});