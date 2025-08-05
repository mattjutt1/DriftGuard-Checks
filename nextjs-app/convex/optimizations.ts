import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

// Query to get optimization history for a user
export const getHistory = query({
  args: {
    userId: v.optional(v.id("users")),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, { userId, limit = 20 }) => {
    if (!userId) {
      // If no userId provided, get from authenticated user
      const identity = await ctx.auth.getUserIdentity();
      if (!identity) throw new Error("Unauthenticated");

      // Find user by token identifier
      const user = await ctx.db
        .query("users")
        .withIndex("by_token", (q) =>
          q.eq("tokenIdentifier", identity.tokenIdentifier),
        )
        .first();

      if (!user) throw new Error("User not found");
      userId = user._id;
    }

    return await ctx.db
      .query("optimizationSessions")
      .withIndex("by_user", (q) => q.eq("userId", userId))
      .order("desc")
      .take(limit);
  },
});

// Query to get a specific optimization session
export const getSession = query({
  args: { sessionId: v.id("optimizationSessions") },
  handler: async (ctx, { sessionId }) => {
    return await ctx.db.get(sessionId);
  },
});

// Mutation to create a new optimization request
export const createOptimizationRequest = mutation({
  args: {
    originalPrompt: v.string(),
    contextDomain: v.optional(v.string()),
  },
  handler: async (ctx, { originalPrompt, contextDomain }) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Unauthenticated");

    // Find or create user
    let user = await ctx.db
      .query("users")
      .withIndex("by_token", (q) =>
        q.eq("tokenIdentifier", identity.tokenIdentifier),
      )
      .first();

    if (!user) {
      // Create new user
      const userId = await ctx.db.insert("users", {
        tokenIdentifier: identity.tokenIdentifier,
        email: identity.email || "",
        preferences: {},
        createdAt: Date.now(),
        updatedAt: Date.now(),
      });
      user = await ctx.db.get(userId);
    }

    if (!user) throw new Error("Failed to create user");

    // Create prompt record
    const promptId = await ctx.db.insert("prompts", {
      userId: user._id,
      originalPrompt,
      contextDomain,
      optimizationStatus: "pending",
      createdAt: Date.now(),
      updatedAt: Date.now(),
    });

    // Create optimization session
    const sessionId = await ctx.db.insert("optimizationSessions", {
      promptId,
      userId: user._id,
      optimizationConfig: {
        iterations: 3,
        rounds: 3,
        temperature: 0.7,
        maxTokens: 1024,
        generateReasoning: true,
        generateExpertIdentity: true,
        seenSetSize: 25,
        fewShotCount: 3,
      },
      status: "pending",
      createdAt: Date.now(),
    });

    return sessionId;
  },
});

// Mutation to update optimization results
export const updateOptimizationResults = mutation({
  args: {
    sessionId: v.id("optimizationSessions"),
    optimizedPrompt: v.string(),
    qualityScore: v.number(),
    processingTimeMs: v.number(),
    improvements: v.array(v.string()),
    metrics: v.object({
      clarity: v.number(),
      specificity: v.number(),
      engagement: v.number(),
    }),
  },
  handler: async (ctx, args) => {
    const {
      sessionId,
      optimizedPrompt,
      qualityScore,
      processingTimeMs,
      improvements,
      metrics,
    } = args;

    // Update session with results
    await ctx.db.patch(sessionId, {
      qualityScore,
      processingTimeMs,
      results: {
        improvements,
        metrics,
      },
    });

    // Update related prompt
    const session = await ctx.db.get(sessionId);
    if (session) {
      await ctx.db.patch(session.promptId, {
        optimizedPrompt,
        optimizationStatus: "completed",
        updatedAt: Date.now(),
      });
    }

    return sessionId;
  },
});

// Mutation to mark optimization as failed
export const markOptimizationFailed = mutation({
  args: {
    sessionId: v.id("optimizationSessions"),
    errorMessage: v.string(),
  },
  handler: async (ctx, { sessionId, errorMessage }) => {
    // Update session with error
    await ctx.db.patch(sessionId, {
      errorMessage,
      status: "failed",
      updatedAt: Date.now(),
    });

    // Update related prompt status
    const session = await ctx.db.get(sessionId);
    if (session) {
      await ctx.db.patch(session.promptId, {
        optimizationStatus: "failed",
        updatedAt: Date.now(),
      });
    }

    return sessionId;
  },
});

// Get prompt by ID
export const getPromptById = query({
  args: { promptId: v.id("prompts") },
  handler: async (ctx, { promptId }) => {
    return await ctx.db.get(promptId);
  },
});

// Update session status and progress
export const updateSessionStatus = mutation({
  args: {
    sessionId: v.id("optimizationSessions"),
    status: v.union(
      v.literal("pending"),
      v.literal("processing"),
      v.literal("completed"),
      v.literal("failed"),
    ),
    currentIteration: v.optional(v.number()),
    progressSteps: v.optional(
      v.array(
        v.object({
          step: v.string(),
          status: v.union(
            v.literal("pending"),
            v.literal("processing"),
            v.literal("completed"),
            v.literal("failed"),
          ),
          timestamp: v.number(),
          details: v.optional(v.string()),
        }),
      ),
    ),
  },
  handler: async (
    ctx,
    { sessionId, status, currentIteration, progressSteps },
  ) => {
    const updateData: any = {
      status,
      updatedAt: Date.now(),
    };

    if (currentIteration !== undefined) {
      updateData.currentIteration = currentIteration;
    }

    if (progressSteps !== undefined) {
      updateData.progressSteps = progressSteps;
    }

    await ctx.db.patch(sessionId, updateData);
    return sessionId;
  },
});

// Update individual progress step
export const updateProgressStep = mutation({
  args: {
    sessionId: v.id("optimizationSessions"),
    stepIndex: v.number(),
    status: v.union(
      v.literal("pending"),
      v.literal("processing"),
      v.literal("completed"),
      v.literal("failed"),
    ),
    details: v.optional(v.string()),
  },
  handler: async (ctx, { sessionId, stepIndex, status, details }) => {
    const session = await ctx.db.get(sessionId);
    if (!session || !session.progressSteps) return;

    const updatedSteps = [...session.progressSteps];
    if (updatedSteps[stepIndex]) {
      updatedSteps[stepIndex] = {
        ...updatedSteps[stepIndex],
        status,
        timestamp: Date.now(),
        ...(details && { details }),
      };

      await ctx.db.patch(sessionId, {
        progressSteps: updatedSteps,
        updatedAt: Date.now(),
      });
    }

    return sessionId;
  },
});

// Add mutation to history
export const addMutationToHistory = mutation({
  args: {
    sessionId: v.id("optimizationSessions"),
    mutation: v.object({
      iteration: v.number(),
      round: v.number(),
      mutationType: v.union(
        v.literal("specific"),
        v.literal("engaging"),
        v.literal("structured"),
      ),
      originalPrompt: v.string(),
      mutatedPrompt: v.string(),
      qualityScores: v.object({
        clarity: v.number(),
        specificity: v.number(),
        engagement: v.number(),
        structure: v.number(),
        completeness: v.number(),
        errorPrevention: v.number(),
        overall: v.number(),
      }),
      timestamp: v.number(),
    }),
  },
  handler: async (ctx, { sessionId, mutation }) => {
    const session = await ctx.db.get(sessionId);
    if (!session) return;

    const currentHistory = session.mutationHistory || [];
    const updatedHistory = [...currentHistory, mutation];

    await ctx.db.patch(sessionId, {
      mutationHistory: updatedHistory,
      updatedAt: Date.now(),
    });

    return sessionId;
  },
});

// Update session iteration
export const updateSessionIteration = mutation({
  args: {
    sessionId: v.id("optimizationSessions"),
    currentIteration: v.number(),
  },
  handler: async (ctx, { sessionId, currentIteration }) => {
    await ctx.db.patch(sessionId, {
      currentIteration,
      updatedAt: Date.now(),
    });
    return sessionId;
  },
});

// Complete session with final results
export const completeSession = mutation({
  args: {
    sessionId: v.id("optimizationSessions"),
    processingTimeMs: v.number(),
    qualityScore: v.number(),
    iterationsCompleted: v.number(),
    expertIdentity: v.optional(v.string()),
    finalResults: v.object({
      bestPrompt: v.string(),
      improvements: v.array(v.string()),
      qualityMetrics: v.object({
        clarity: v.number(),
        specificity: v.number(),
        engagement: v.number(),
        structure: v.number(),
        completeness: v.number(),
        errorPrevention: v.number(),
        overall: v.number(),
      }),
      reasoning: v.optional(v.string()),
      expertInsights: v.optional(v.array(v.string())),
    }),
  },
  handler: async (ctx, args) => {
    const {
      sessionId,
      processingTimeMs,
      qualityScore,
      iterationsCompleted,
      expertIdentity,
      finalResults,
    } = args;

    // Update session with final results
    await ctx.db.patch(sessionId, {
      status: "completed",
      processingTimeMs,
      qualityScore,
      iterationsCompleted,
      expertIdentity,
      finalResults,
      updatedAt: Date.now(),
    });

    // Update related prompt
    const session = await ctx.db.get(sessionId);
    if (session) {
      await ctx.db.patch(session.promptId, {
        optimizedPrompt: finalResults.bestPrompt,
        optimizationStatus: "completed",
        updatedAt: Date.now(),
      });
    }

    return sessionId;
  },
});
