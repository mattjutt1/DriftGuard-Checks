/**
 * Test script for PromptWizard integration
 * Run this in the Convex dashboard to test components
 */

import { action } from "./_generated/server";
import { v } from "convex/values";
import { promptWizard } from "./promptwizard";
import { api } from "./_generated/api";

/**
 * Test basic Ollama connectivity
 */
export const testOllamaConnection = action({
  args: {},
  handler: async (ctx) => {
    console.log("Testing Ollama connection...");

    try {
      const health = await promptWizard.checkHealth();
      console.log("Health check result:", health);
      return {
        success: true,
        health,
        message: health.available
          ? "Ollama is running and accessible"
          : "Ollama connection failed",
      };
    } catch (error) {
      console.error("Health check failed:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
        message: "Make sure Ollama is running: ollama serve",
      };
    }
  },
});

/**
 * Test expert identity generation
 */
export const testExpertIdentity = action({
  args: {
    prompt: v.string(),
  },
  handler: async (ctx, { prompt }) => {
    console.log("Testing expert identity generation for:", prompt);

    try {
      const identity = await promptWizard.generateExpertIdentity(prompt);
      console.log("Generated expert identity:", identity);

      return {
        success: true,
        expertIdentity: identity,
        message: "Expert identity generated successfully",
      };
    } catch (error) {
      console.error("Expert identity generation failed:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  },
});

/**
 * Test prompt mutation
 */
export const testPromptMutation = action({
  args: {
    prompt: v.string(),
    mutationType: v.union(
      v.literal("specific"),
      v.literal("engaging"),
      v.literal("structured"),
    ),
    expertIdentity: v.optional(v.string()),
  },
  handler: async (ctx, { prompt, mutationType, expertIdentity }) => {
    console.log(`Testing ${mutationType} mutation for:`, prompt);

    try {
      const mutatedPrompt = await promptWizard.mutatePrompt(
        prompt,
        mutationType,
        expertIdentity,
      );
      console.log("Mutated prompt:", mutatedPrompt);

      return {
        success: true,
        originalPrompt: prompt,
        mutatedPrompt,
        mutationType,
        message: `${mutationType} mutation completed successfully`,
      };
    } catch (error) {
      console.error("Prompt mutation failed:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  },
});

/**
 * Test quality scoring
 */
export const testQualityScoring = action({
  args: {
    prompt: v.string(),
  },
  handler: async (ctx, { prompt }) => {
    console.log("Testing quality scoring for:", prompt);

    try {
      const scores = await promptWizard.scorePrompt(prompt);
      console.log("Quality scores:", scores);

      return {
        success: true,
        prompt,
        qualityScores: scores,
        message: "Quality scoring completed successfully",
      };
    } catch (error) {
      console.error("Quality scoring failed:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  },
});

/**
 * Test complete optimization flow (simplified)
 */
export const testFullOptimization = action({
  args: {
    prompt: v.string(),
  },
  handler: async (ctx, { prompt }) => {
    console.log("Testing full optimization flow for:", prompt);

    try {
      // Step 1: Generate expert identity
      console.log("Step 1: Generating expert identity...");
      const expertIdentity = await promptWizard.generateExpertIdentity(prompt);
      console.log("Expert identity:", expertIdentity);

      // Step 2: Create mutations
      console.log("Step 2: Creating prompt mutations...");
      const mutations = [];
      const mutationTypes = ["specific", "engaging", "structured"] as const;

      for (const mutationType of mutationTypes) {
        const result = await promptWizard.performMutationRound(
          prompt,
          mutationType,
          expertIdentity,
        );
        mutations.push({
          type: mutationType,
          prompt: result.mutatedPrompt,
          scores: result.qualityScores,
        });
        console.log(`${mutationType} mutation:`, result.mutatedPrompt);
        console.log(`${mutationType} scores:`, result.qualityScores);
      }

      // Step 3: Select best mutation
      console.log("Step 3: Selecting best mutation...");
      const bestMutation = promptWizard.selectBestPrompt(
        mutations.map((m) => ({ prompt: m.prompt, scores: m.scores })),
      );
      console.log("Best mutation:", bestMutation);

      // Step 4: Analyze improvements
      console.log("Step 4: Analyzing improvements...");
      const improvements = await promptWizard.analyzeImprovements(
        prompt,
        bestMutation.prompt,
      );
      console.log("Improvements:", improvements);

      // Step 5: Generate expert insights
      console.log("Step 5: Generating expert insights...");
      const insights = await promptWizard.generateExpertInsights(
        bestMutation.prompt,
        expertIdentity,
      );
      console.log("Expert insights:", insights);

      return {
        success: true,
        originalPrompt: prompt,
        expertIdentity,
        mutations,
        bestMutation,
        improvements,
        expertInsights: insights,
        message: "Full optimization completed successfully",
      };
    } catch (error) {
      console.error("Full optimization failed:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  },
});

/**
 * Test creating and running an optimization session
 */
export const testOptimizationSession = action({
  args: {
    prompt: v.string(),
    contextDomain: v.optional(v.string()),
  },
  handler: async (ctx, { prompt, contextDomain }) => {
    console.log("Testing optimization session creation and execution...");

    try {
      // Step 1: Create optimization request
      console.log("Step 1: Creating optimization request...");
      const sessionId = await ctx.runMutation(
        api.optimizations.createOptimizationRequest,
        {
          originalPrompt: prompt,
          contextDomain,
        },
      );
      console.log("Created session:", sessionId);

      // Step 2: Run quick optimization
      console.log("Step 2: Running quick optimization...");
      const result = await ctx.runAction(api.actions.quickOptimize, {
        sessionId,
      });
      console.log("Optimization result:", result);

      return {
        success: true,
        sessionId,
        optimizationResult: result,
        message: "Optimization session completed successfully",
      };
    } catch (error) {
      console.error("Optimization session failed:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  },
});
