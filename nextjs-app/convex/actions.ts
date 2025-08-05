/**
 * Convex Actions for PromptWizard Integration
 * Handles the actual prompt optimization process using Ollama
 */

import { action } from "./_generated/server";
import { v } from "convex/values";
import { promptWizard, MutationType, QualityScores, PROMPTWIZARD_CONFIG } from "./promptwizard";
import { api } from "./_generated/api";

/**
 * Health check action to verify Ollama connectivity
 */
export const checkOllamaHealth = action({
  args: {},
  handler: async (ctx) => {
    try {
      const health = await promptWizard.checkHealth();
      return health;
    } catch (error) {
      return {
        available: false,
        model: "qwen3:4b",
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  },
});

/**
 * Test individual PromptWizard components
 */
export const testPromptWizardComponent = action({
  args: {
    component: v.union(
      v.literal("expert_identity"),
      v.literal("mutation_specific"),
      v.literal("mutation_engaging"),
      v.literal("mutation_structured"),
      v.literal("quality_scoring"),
      v.literal("improvements"),
      v.literal("expert_insights")
    ),
    prompt: v.string(),
    expertIdentity: v.optional(v.string()),
    originalPrompt: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    try {
      switch (args.component) {
        case "expert_identity":
          const identity = await promptWizard.generateExpertIdentity(args.prompt);
          return { success: true, result: identity };

        case "mutation_specific":
          const specificMutation = await promptWizard.mutatePrompt(args.prompt, "specific", args.expertIdentity);
          return { success: true, result: specificMutation };

        case "mutation_engaging":
          const engagingMutation = await promptWizard.mutatePrompt(args.prompt, "engaging", args.expertIdentity);
          return { success: true, result: engagingMutation };

        case "mutation_structured":
          const structuredMutation = await promptWizard.mutatePrompt(args.prompt, "structured", args.expertIdentity);
          return { success: true, result: structuredMutation };

        case "quality_scoring":
          const scores = await promptWizard.scorePrompt(args.prompt);
          return { success: true, result: scores };

        case "improvements":
          if (!args.originalPrompt) {
            throw new Error("Original prompt required for improvements analysis");
          }
          const improvements = await promptWizard.analyzeImprovements(args.originalPrompt, args.prompt);
          return { success: true, result: improvements };

        case "expert_insights":
          if (!args.expertIdentity) {
            throw new Error("Expert identity required for insights generation");
          }
          const insights = await promptWizard.generateExpertInsights(args.prompt, args.expertIdentity);
          return { success: true, result: insights };

        default:
          throw new Error("Invalid component specified");
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  },
});

/**
 * Quick Mode: Single iteration optimization
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
          { step: "Generating expert identity", status: "processing", timestamp: Date.now() },
          { step: "Creating prompt variations", status: "pending", timestamp: Date.now() },
          { step: "Scoring and selecting best version", status: "pending", timestamp: Date.now() },
          { step: "Analyzing improvements", status: "pending", timestamp: Date.now() },
        ],
      });

      // Step 1: Generate expert identity (if enabled)
      let expertIdentity: string | undefined;
      if (session.optimizationConfig.generateExpertIdentity) {
        expertIdentity = await promptWizard.generateExpertIdentity(prompt.originalPrompt);
        
        await ctx.runMutation(api.optimizations.updateProgressStep, {
          sessionId: args.sessionId,
          stepIndex: 0,
          status: "completed",
          details: expertIdentity,
        });
      }

      // Step 2: Update progress
      await ctx.runMutation(api.optimizations.updateProgressStep, {
        sessionId: args.sessionId,
        stepIndex: 1,
        status: "processing",
      });

      // Step 2: Create three mutation types
      const mutations: Array<{ type: MutationType; prompt: string; scores: QualityScores }> = [];
      const mutationTypes: MutationType[] = ["specific", "engaging", "structured"];

      for (const mutationType of mutationTypes) {
        const result = await promptWizard.performMutationRound(
          prompt.originalPrompt,
          mutationType,
          expertIdentity
        );

        mutations.push({
          type: mutationType,
          prompt: result.mutatedPrompt,
          scores: result.qualityScores,
        });

        // Store mutation in history
        await ctx.runMutation(api.optimizations.addMutationToHistory, {
          sessionId: args.sessionId,
          mutation: {
            iteration: 1,
            round: 1,
            mutationType,
            originalPrompt: prompt.originalPrompt,
            mutatedPrompt: result.mutatedPrompt,
            qualityScores: result.qualityScores,
            timestamp: Date.now(),
          },
        });
      }

      // Step 3: Select best mutation
      await ctx.runMutation(api.optimizations.updateProgressStep, {
        sessionId: args.sessionId,
        stepIndex: 2,
        status: "processing",
      });

      const bestMutation = promptWizard.selectBestPrompt(
        mutations.map(m => ({ prompt: m.prompt, scores: m.scores }))
      );

      // Step 4: Analyze improvements
      await ctx.runMutation(api.optimizations.updateProgressStep, {
        sessionId: args.sessionId,
        stepIndex: 3,
        status: "processing",
      });

      const improvements = await promptWizard.analyzeImprovements(
        prompt.originalPrompt,
        bestMutation.prompt
      );

      // Generate expert insights if enabled
      let expertInsights: string[] | undefined;
      if (session.optimizationConfig.generateReasoning && expertIdentity) {
        expertInsights = await promptWizard.generateExpertInsights(
          bestMutation.prompt,
          expertIdentity
        );
      }

      // Calculate processing time
      const processingTimeMs = Date.now() - startTime;

      // Step 5: Finalize results
      const finalResults = {
        bestPrompt: bestMutation.prompt,
        improvements,
        qualityMetrics: bestMutation.scores,
        reasoning: expertIdentity,
        expertInsights,
      };

      // Update session with final results
      await ctx.runMutation(api.optimizations.completeSession, {
        sessionId: args.sessionId,
        processingTimeMs,
        qualityScore: bestMutation.scores.overall,
        iterationsCompleted: 1,
        expertIdentity,
        finalResults,
      });

      // Update all progress steps to completed
      await ctx.runMutation(api.optimizations.updateProgressStep, {
        sessionId: args.sessionId,
        stepIndex: 3,
        status: "completed",
      });

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
 * Advanced Mode: Multiple iterations with refinement
 */
export const advancedOptimize = action({
  args: {
    sessionId: v.id("optimizationSessions"),
    maxIterations: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const maxIterations = args.maxIterations || PROMPTWIZARD_CONFIG.mutateRefineIterations;
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
          { step: "Generating expert identity", status: "processing", timestamp: Date.now() },
          { step: "Iterative prompt optimization", status: "pending", timestamp: Date.now() },
          { step: "Finalizing best version", status: "pending", timestamp: Date.now() },
        ],
      });

      // Step 1: Generate expert identity
      let expertIdentity: string | undefined;
      if (session.optimizationConfig.generateExpertIdentity) {
        expertIdentity = await promptWizard.generateExpertIdentity(prompt.originalPrompt);
        
        await ctx.runMutation(api.optimizations.updateProgressStep, {
          sessionId: args.sessionId,
          stepIndex: 0,
          status: "completed",
          details: expertIdentity,
        });
      }

      // Step 2: Iterative optimization
      await ctx.runMutation(api.optimizations.updateProgressStep, {
        sessionId: args.sessionId,
        stepIndex: 1,
        status: "processing",
      });

      let currentBestPrompt = prompt.originalPrompt;
      let currentBestScore = 0;
      let allCandidates: Array<{ prompt: string; scores: QualityScores; iteration: number }> = [];

      // Perform iterative optimization
      for (let iteration = 1; iteration <= maxIterations; iteration++) {
        await ctx.runMutation(api.optimizations.updateSessionIteration, {
          sessionId: args.sessionId,
          currentIteration: iteration,
        });

        const iterationCandidates: Array<{ type: MutationType; prompt: string; scores: QualityScores }> = [];
        const mutationTypes: MutationType[] = ["specific", "engaging", "structured"];

        // Create mutations for this iteration
        for (let round = 1; round <= session.optimizationConfig.rounds; round++) {
          for (const mutationType of mutationTypes) {
            const result = await promptWizard.performMutationRound(
              currentBestPrompt,
              mutationType,
              expertIdentity
            );

            iterationCandidates.push({
              type: mutationType,
              prompt: result.mutatedPrompt,
              scores: result.qualityScores,
            });

            // Store mutation in history
            await ctx.runMutation(api.optimizations.addMutationToHistory, {
              sessionId: args.sessionId,
              mutation: {
                iteration,
                round,
                mutationType,
                originalPrompt: currentBestPrompt,
                mutatedPrompt: result.mutatedPrompt,
                qualityScores: result.qualityScores,
                timestamp: Date.now(),
              },
            });
          }
        }

        // Find best from this iteration
        const iterationBest = promptWizard.selectBestPrompt(
          iterationCandidates.map(c => ({ prompt: c.prompt, scores: c.scores }))
        );

        // Add to all candidates
        allCandidates.push({
          prompt: iterationBest.prompt,
          scores: iterationBest.scores,
          iteration,
        });

        // Update current best if this iteration improved
        if (iterationBest.scores.overall > currentBestScore) {
          currentBestPrompt = iterationBest.prompt;
          currentBestScore = iterationBest.scores.overall;
        }

        // Early stopping if we reach high quality
        if (currentBestScore >= 95) {
          break;
        }
      }

      // Step 3: Finalize best version
      await ctx.runMutation(api.optimizations.updateProgressStep, {
        sessionId: args.sessionId,
        stepIndex: 2,
        status: "processing",
      });

      // Select overall best from all candidates
      const overallBest = promptWizard.selectBestPrompt(
        allCandidates.map(c => ({ prompt: c.prompt, scores: c.scores }))
      );

      // Analyze improvements
      const improvements = await promptWizard.analyzeImprovements(
        prompt.originalPrompt,
        overallBest.prompt
      );

      // Generate expert insights if enabled
      let expertInsights: string[] | undefined;
      if (session.optimizationConfig.generateReasoning && expertIdentity) {
        expertInsights = await promptWizard.generateExpertInsights(
          overallBest.prompt,
          expertIdentity
        );
      }

      // Calculate processing time
      const processingTimeMs = Date.now() - startTime;

      // Finalize results
      const finalResults = {
        bestPrompt: overallBest.prompt,
        improvements,
        qualityMetrics: overallBest.scores,
        reasoning: expertIdentity,
        expertInsights,
      };

      // Complete the session
      await ctx.runMutation(api.optimizations.completeSession, {
        sessionId: args.sessionId,
        processingTimeMs,
        qualityScore: overallBest.scores.overall,
        iterationsCompleted: maxIterations,
        expertIdentity,
        finalResults,
      });

      // Mark all progress steps completed
      await ctx.runMutation(api.optimizations.updateProgressStep, {
        sessionId: args.sessionId,
        stepIndex: 2,
        status: "completed",
      });

      return {
        success: true,
        sessionId: args.sessionId,
        processingTimeMs,
        finalResults,
        iterationsCompleted: maxIterations,
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