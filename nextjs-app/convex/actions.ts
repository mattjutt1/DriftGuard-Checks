/**
 * Convex Actions for Real Microsoft PromptWizard Integration
 * Handles the actual prompt optimization process using Microsoft PromptWizard framework
 */

import { action } from "./_generated/server";
import { v } from "convex/values";
import {
  promptWizard,
  PromptWizardConfig,
  OptimizationResult,
} from "./promptwizard";
import { api } from "./_generated/api";

/**
 * Health check action to verify PromptWizard availability
 */
export const checkOllamaHealth = action({
  args: {},
  handler: async (ctx) => {
    try {
      const health = await promptWizard.checkAvailability();
      return {
        available: health.available,
        model: "Microsoft PromptWizard + Qwen3:4b",
        error: health.error,
      };
    } catch (error) {
      return {
        available: false,
        model: "Microsoft PromptWizard + Qwen3:4b",
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  },
});

/**
 * Test PromptWizard optimization with custom configuration
 */
export const testPromptWizardOptimization = action({
  args: {
    prompt: v.string(),
    domain: v.optional(v.string()),
    config: v.optional(
      v.object({
        task_description: v.optional(v.string()),
        base_instruction: v.optional(v.string()),
        answer_format: v.optional(v.string()),
        seen_set_size: v.optional(v.number()),
        few_shot_count: v.optional(v.number()),
        generate_reasoning: v.optional(v.boolean()),
        generate_expert_identity: v.optional(v.boolean()),
        mutate_refine_iterations: v.optional(v.number()),
        mutation_rounds: v.optional(v.number()),
      }),
    ),
  },
  handler: async (ctx, args) => {
    try {
      const result = await promptWizard.optimizePrompt(
        args.prompt,
        args.config || {},
        args.domain || "general",
      );
      return { success: true, result };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  },
});

/**
 * Quick Mode: Single iteration optimization using real Microsoft PromptWizard
 */
export const quickOptimize = action({
  args: {
    sessionId: v.id("optimizationSessions"),
  },
  handler: async (ctx, args) => {
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

      // Update session status to processing
      await ctx.runMutation(api.optimizations.updateSessionStatus, {
        sessionId: args.sessionId,
        status: "processing",
        currentIteration: 1,
        progressSteps: [
          {
            step: "Initializing PromptWizard",
            status: "processing",
            timestamp: Date.now(),
          },
          {
            step: "Running optimization",
            status: "pending",
            timestamp: Date.now(),
          },
          {
            step: "Analyzing results",
            status: "pending",
            timestamp: Date.now(),
          },
        ],
      });

      // Step 1: Complete initialization
      await ctx.runMutation(api.optimizations.updateProgressStep, {
        sessionId: args.sessionId,
        stepIndex: 0,
        status: "completed",
      });

      // Step 2: Run PromptWizard optimization
      await ctx.runMutation(api.optimizations.updateProgressStep, {
        sessionId: args.sessionId,
        stepIndex: 1,
        status: "processing",
      });

      // Create PromptWizard configuration from session settings
      const config: Partial<PromptWizardConfig> = {
        task_description: `Optimize this prompt: ${prompt.originalPrompt}`,
        generate_reasoning: session.optimizationConfig.generateReasoning,
        generate_expert_identity:
          session.optimizationConfig.generateExpertIdentity,
        mutate_refine_iterations: 1, // Quick mode uses single iteration
        mutation_rounds: session.optimizationConfig.rounds || 3,
      };

      // Run the real Microsoft PromptWizard optimization
      const optimizationResult = await promptWizard.optimizePrompt(
        prompt.originalPrompt,
        config,
        "general",
      );

      // Step 3: Analyze results
      await ctx.runMutation(api.optimizations.updateProgressStep, {
        sessionId: args.sessionId,
        stepIndex: 2,
        status: "processing",
      });

      // Calculate processing time
      const processingTimeMs = Date.now() - startTime;

      // Create final results in the expected format
      const finalResults = {
        bestPrompt: optimizationResult.best_prompt,
        improvements: optimizationResult.improvements,
        qualityMetrics: {
          overall: optimizationResult.quality_score,
          clarity: optimizationResult.quality_score,
          specificity: optimizationResult.quality_score,
          engagement: optimizationResult.quality_score,
        },
        reasoning: optimizationResult.expert_profile,
        expertInsights: optimizationResult.improvements,
      };

      // Update session with final results
      await ctx.runMutation(api.optimizations.completeSession, {
        sessionId: args.sessionId,
        processingTimeMs,
        qualityScore: optimizationResult.quality_score,
        iterationsCompleted: optimizationResult.iterations_completed,
        expertIdentity: optimizationResult.expert_profile,
        finalResults,
      });

      // Mark all progress steps as completed
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

/**
 * Advanced Mode: Multiple iterations using real Microsoft PromptWizard
 */
export const advancedOptimize = action({
  args: {
    sessionId: v.id("optimizationSessions"),
    maxIterations: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const maxIterations = args.maxIterations || 3; // Default to 3 iterations for advanced mode
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

      // Update session status to processing
      await ctx.runMutation(api.optimizations.updateSessionStatus, {
        sessionId: args.sessionId,
        status: "processing",
        currentIteration: 1,
        progressSteps: [
          {
            step: "Initializing PromptWizard",
            status: "processing",
            timestamp: Date.now(),
          },
          {
            step: "Running advanced optimization",
            status: "pending",
            timestamp: Date.now(),
          },
          {
            step: "Finalizing results",
            status: "pending",
            timestamp: Date.now(),
          },
        ],
      });

      // Step 1: Complete initialization
      await ctx.runMutation(api.optimizations.updateProgressStep, {
        sessionId: args.sessionId,
        stepIndex: 0,
        status: "completed",
      });

      // Step 2: Run PromptWizard optimization with multiple iterations
      await ctx.runMutation(api.optimizations.updateProgressStep, {
        sessionId: args.sessionId,
        stepIndex: 1,
        status: "processing",
      });

      // Create PromptWizard configuration from session settings
      const config: Partial<PromptWizardConfig> = {
        task_description: `Optimize this prompt for maximum effectiveness: ${prompt.originalPrompt}`,
        generate_reasoning: session.optimizationConfig.generateReasoning,
        generate_expert_identity:
          session.optimizationConfig.generateExpertIdentity,
        mutate_refine_iterations: maxIterations, // Advanced mode uses multiple iterations
        mutation_rounds: session.optimizationConfig.rounds || 3,
      };

      // Run the real Microsoft PromptWizard optimization
      const optimizationResult = await promptWizard.optimizePrompt(
        prompt.originalPrompt,
        config,
        "general",
      );

      // Step 3: Finalize results
      await ctx.runMutation(api.optimizations.updateProgressStep, {
        sessionId: args.sessionId,
        stepIndex: 2,
        status: "processing",
      });

      // Calculate processing time
      const processingTimeMs = Date.now() - startTime;

      // Create final results in the expected format
      const finalResults = {
        bestPrompt: optimizationResult.best_prompt,
        improvements: optimizationResult.improvements,
        qualityMetrics: {
          overall: optimizationResult.quality_score,
          clarity: optimizationResult.quality_score,
          specificity: optimizationResult.quality_score,
          engagement: optimizationResult.quality_score,
        },
        reasoning: optimizationResult.expert_profile,
        expertInsights: optimizationResult.improvements,
      };

      // Complete the session
      await ctx.runMutation(api.optimizations.completeSession, {
        sessionId: args.sessionId,
        processingTimeMs,
        qualityScore: optimizationResult.quality_score,
        iterationsCompleted: optimizationResult.iterations_completed,
        expertIdentity: optimizationResult.expert_profile,
        finalResults,
      });

      // Mark all progress steps as completed
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
        iterationsCompleted: optimizationResult.iterations_completed,
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
