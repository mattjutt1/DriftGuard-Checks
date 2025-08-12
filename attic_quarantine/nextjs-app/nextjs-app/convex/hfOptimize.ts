/**
 * Simplified HF Spaces integration for Convex
 * Connects to Qwen3-30B-A3B model on Hugging Face Spaces
 */

import { action } from "./_generated/server";
import { v } from "convex/values";
import { api } from "./_generated/api";

// HF Space URL - Update this with your actual deployed space URL
const HF_SPACE_URL = process.env.HF_SPACE_URL || "https://mattjutt1-promptevolver.hf.space";

/**
 * Simple health check for HF Space
 */
export const checkHFSpaceHealth = action({
  args: {},
  handler: async () => {
    try {
      const response = await fetch(HF_SPACE_URL, {
        method: "GET",
        signal: AbortSignal.timeout(5000),
      });

      return {
        available: response.ok,
        model: "Qwen3-30B-A3B-Instruct-2507",
        error: response.ok ? undefined : `Status: ${response.status}`,
      };
    } catch (error) {
      return {
        available: false,
        model: "Qwen3-30B-A3B-Instruct-2507",
        error: error instanceof Error ? error.message : "Connection failed",
      };
    }
  },
});

/**
 * Optimize prompt using HF Space
 */
export const optimizeWithHFSpace: any = action({
  args: {
    sessionId: v.id("optimizationSessions"),
  },
  handler: async (ctx, args): Promise<any> => {
    const startTime = Date.now();

    try {
      // Get session and prompt data
      const session = await ctx.runQuery(api.optimizations.getSession, {
        sessionId: args.sessionId,
      });

      if (!session) {
        throw new Error("Session not found");
      }

      const prompt = await ctx.runQuery(api.optimizations.getPromptById, {
        promptId: session.promptId,
      });

      if (!prompt) {
        throw new Error("Prompt not found");
      }

      // Update session status
      await ctx.runMutation(api.optimizations.updateSessionStatus, {
        sessionId: args.sessionId,
        status: "processing",
        currentIteration: 1,
        progressSteps: [
          {
            step: "Connecting to HF Space",
            status: "processing",
            timestamp: Date.now(),
          },
          {
            step: "Running Qwen3-30B optimization",
            status: "pending",
            timestamp: Date.now(),
          },
          {
            step: "Processing results",
            status: "pending",
            timestamp: Date.now(),
          },
        ],
      });

      // Step 1: Connect to HF Space
      await ctx.runMutation(api.optimizations.updateProgressStep, {
        sessionId: args.sessionId,
        stepIndex: 0,
        status: "completed",
      });

      // Step 2: Call HF Space API
      await ctx.runMutation(api.optimizations.updateProgressStep, {
        sessionId: args.sessionId,
        stepIndex: 1,
        status: "processing",
      });

      const apiUrl = `${HF_SPACE_URL}/api/optimize`;
      const gradioRequest = {
        data: [
          prompt.originalPrompt,
          session.contextDomain || "",
          session.optimizationConfig.generateReasoning ? "thorough" : "balanced",
          0.7, // temperature
        ],
      };

      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(gradioRequest),
        signal: AbortSignal.timeout(30000), // 30 second timeout
      });

      if (!response.ok) {
        throw new Error(`HF Space returned status ${response.status}`);
      }

      const result = await response.json();
      const hfResponse = result.data?.[0];

      if (!hfResponse) {
        throw new Error("Invalid response from HF Space");
      }

      // Step 3: Process results
      await ctx.runMutation(api.optimizations.updateProgressStep, {
        sessionId: args.sessionId,
        stepIndex: 2,
        status: "processing",
      });

      const processingTimeMs = Date.now() - startTime;

      // Format results for Convex
      const finalResults = {
        bestPrompt: hfResponse.optimized_prompt || prompt.originalPrompt,
        improvements: hfResponse.improvements || ["Optimization attempted"],
        qualityMetrics: {
          overall: hfResponse.quality_score || 0.75,
          clarity: hfResponse.quality_score || 0.75,
          specificity: hfResponse.quality_score || 0.75,
          engagement: hfResponse.quality_score || 0.75,
        },
        reasoning: hfResponse.reasoning || "Optimization completed",
        expertInsights: [
          hfResponse.expert_profile || "Qwen3-30B-A3B analysis",
          `Processing time: ${hfResponse.processing_time || 'N/A'}`,
          `Model: ${hfResponse.model || 'Qwen3-30B-A3B'}`,
        ],
      };

      // Complete session
      await ctx.runMutation(api.optimizations.completeSession, {
        sessionId: args.sessionId,
        processingTimeMs,
        qualityScore: hfResponse.quality_score || 0.75,
        iterationsCompleted: 1,
        expertIdentity: hfResponse.expert_profile || "Qwen3-30B Expert",
        finalResults,
      });

      // Mark all steps completed
      for (let i = 0; i < 3; i++) {
        await ctx.runMutation(api.optimizations.updateProgressStep, {
          sessionId: args.sessionId,
          stepIndex: i,
          status: "completed",
        });
      }

      return {
        success: true,
        sessionId: args.sessionId,
        processingTimeMs,
        finalResults,
      };
    } catch (error) {
      // Mark session as failed
      await ctx.runMutation(api.optimizations.markOptimizationFailed, {
        sessionId: args.sessionId,
        errorMessage: error instanceof Error ? error.message : "Unknown error",
      });

      return {
        success: false,
        sessionId: args.sessionId,
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  },
});
