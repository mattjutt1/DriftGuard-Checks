/**
 * Convex Optimization Functions
 * Core functions for managing optimization requests, sessions, and progress tracking
 */

import { mutation, query } from "./_generated/server";
import { v } from "convex/values";
import { Id } from "./_generated/dataModel";

/**
 * Create a new optimization request
 */
export const createOptimizationRequest = mutation({
  args: {
    originalPrompt: v.string(),
    contextDomain: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    // For demo purposes, create a mock user if none exists
    // In production, you'd get this from authentication
    let userId: Id<"users">;
    
    const existingUser = await ctx.db
      .query("users")
      .filter((q) => q.eq(q.field("email"), "demo@promptevolver.com"))
      .first();

    if (existingUser) {
      userId = existingUser._id;
    } else {
      userId = await ctx.db.insert("users", {
        tokenIdentifier: "demo-user",
        email: "demo@promptevolver.com",
        username: "Demo User",
        preferences: {
          theme: "light",
          defaultContext: args.contextDomain || "general",
          notifications: true,
        },
        createdAt: Date.now(),
        updatedAt: Date.now(),
      });
    }

    // Create the prompt record
    const promptId = await ctx.db.insert("prompts", {
      userId,
      originalPrompt: args.originalPrompt,
      contextDomain: args.contextDomain,
      optimizationStatus: "pending",
      createdAt: Date.now(),
      updatedAt: Date.now(),
    });

    // Create the optimization session
    const sessionId = await ctx.db.insert("optimizationSessions", {
      promptId,
      userId,
      optimizationConfig: {
        iterations: 2,
        rounds: 3,
        temperature: 0.7,
        maxTokens: 2000,
        generateReasoning: true,
        generateExpertIdentity: true,
        seenSetSize: 10,
        fewShotCount: 3,
      },
      status: "pending",
      createdAt: Date.now(),
    });

    // Update prompt status
    await ctx.db.patch(promptId, {
      optimizationStatus: "processing",
      updatedAt: Date.now(),
    });

    return sessionId;
  },
});

/**
 * Get optimization session by ID
 */
export const getSession = query({
  args: {
    sessionId: v.id("optimizationSessions"),
  },
  handler: async (ctx, args) => {
    const session = await ctx.db.get(args.sessionId);
    if (!session) return null;

    // Also get the associated prompt data
    const prompt = await ctx.db.get(session.promptId);
    
    return {
      ...session,
      prompt,
    };
  },
});

/**
 * Get prompt by ID
 */
export const getPromptById = query({
  args: {
    promptId: v.id("prompts"),
  },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.promptId);
  },
});

/**
 * Update session status and progress
 */
export const updateSessionStatus = mutation({
  args: {
    sessionId: v.id("optimizationSessions"),
    status: v.union(
      v.literal("pending"),
      v.literal("processing"),
      v.literal("completed"),
      v.literal("failed")
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
            v.literal("failed")
          ),
          timestamp: v.number(),
          details: v.optional(v.string()),
        })
      )
    ),
  },
  handler: async (ctx, args) => {
    const updateData: any = {
      status: args.status,
      updatedAt: Date.now(),
    };

    if (args.currentIteration !== undefined) {
      updateData.currentIteration = args.currentIteration;
    }

    if (args.progressSteps) {
      updateData.progressSteps = args.progressSteps;
    }

    await ctx.db.patch(args.sessionId, updateData);
    return args.sessionId;
  },
});

/**
 * Update a specific progress step
 */
export const updateProgressStep = mutation({
  args: {
    sessionId: v.id("optimizationSessions"),
    stepIndex: v.number(),
    status: v.union(
      v.literal("pending"),
      v.literal("processing"),
      v.literal("completed"),
      v.literal("failed")
    ),
    details: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const session = await ctx.db.get(args.sessionId);
    if (!session || !session.progressSteps) return;

    const updatedSteps = [...session.progressSteps];
    if (updatedSteps[args.stepIndex]) {
      updatedSteps[args.stepIndex] = {
        ...updatedSteps[args.stepIndex],
        status: args.status,
        timestamp: Date.now(),
        details: args.details,
      };

      await ctx.db.patch(args.sessionId, {
        progressSteps: updatedSteps,
        updatedAt: Date.now(),
      });
    }

    return args.sessionId;
  },
});

/**
 * Complete optimization session with final results
 */
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
    const session = await ctx.db.get(args.sessionId);
    if (!session) throw new Error("Session not found");

    // Update session with completion data
    await ctx.db.patch(args.sessionId, {
      status: "completed",
      processingTimeMs: args.processingTimeMs,
      qualityScore: args.qualityScore,
      iterationsCompleted: args.iterationsCompleted,
      expertIdentity: args.expertIdentity,
      finalResults: args.finalResults,
      updatedAt: Date.now(),
    });

    // Update the associated prompt
    await ctx.db.patch(session.promptId, {
      optimizationStatus: "completed",
      optimizedPrompt: args.finalResults.bestPrompt,
      updatedAt: Date.now(),
    });

    return args.sessionId;
  },
});

/**
 * Mark optimization as failed
 */
export const markOptimizationFailed = mutation({
  args: {
    sessionId: v.id("optimizationSessions"),
    errorMessage: v.string(),
  },
  handler: async (ctx, args) => {
    const session = await ctx.db.get(args.sessionId);
    if (!session) throw new Error("Session not found");

    // Update session with failure data
    await ctx.db.patch(args.sessionId, {
      status: "failed",
      errorMessage: args.errorMessage,
      updatedAt: Date.now(),
    });

    // Update the associated prompt
    await ctx.db.patch(session.promptId, {
      optimizationStatus: "failed",
      updatedAt: Date.now(),
    });

    return args.sessionId;
  },
});

/**
 * Get optimization history for a user
 */
export const getOptimizationHistory = query({
  args: {
    userId: v.optional(v.id("users")),
    limit: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const limit = args.limit || 10;
    
    // For demo purposes, get demo user if no userId provided
    let userId = args.userId;
    if (!userId) {
      const demoUser = await ctx.db
        .query("users")
        .filter((q) => q.eq(q.field("email"), "demo@promptevolver.com"))
        .first();
      userId = demoUser?._id;
    }

    if (!userId) return [];

    const sessions = await ctx.db
      .query("optimizationSessions")
      .filter((q) => q.eq(q.field("userId"), userId))
      .order("desc")
      .take(limit);

    // Get associated prompts for each session
    const sessionsWithPrompts = await Promise.all(
      sessions.map(async (session) => {
        const prompt = await ctx.db.get(session.promptId);
        return {
          ...session,
          prompt,
        };
      })
    );

    return sessionsWithPrompts;
  },
});

/**
 * Get session statistics
 */
export const getSessionStats = query({
  args: {
    userId: v.optional(v.id("users")),
  },
  handler: async (ctx, args) => {
    // For demo purposes, get demo user if no userId provided
    let userId = args.userId;
    if (!userId) {
      const demoUser = await ctx.db
        .query("users")
        .filter((q) => q.eq(q.field("email"), "demo@promptevolver.com"))
        .first();
      userId = demoUser?._id;
    }

    if (!userId) {
      return {
        totalSessions: 0,
        completedSessions: 0,
        failedSessions: 0,
        averageQualityScore: 0,
        averageProcessingTime: 0,
      };
    }

    const allSessions = await ctx.db
      .query("optimizationSessions")
      .filter((q) => q.eq(q.field("userId"), userId))
      .collect();

    const completedSessions = allSessions.filter(s => s.status === "completed");
    const failedSessions = allSessions.filter(s => s.status === "failed");

    const averageQualityScore = completedSessions.length > 0
      ? completedSessions.reduce((sum, s) => sum + (s.qualityScore || 0), 0) / completedSessions.length
      : 0;

    const averageProcessingTime = completedSessions.length > 0
      ? completedSessions.reduce((sum, s) => sum + (s.processingTimeMs || 0), 0) / completedSessions.length
      : 0;

    return {
      totalSessions: allSessions.length,
      completedSessions: completedSessions.length,
      failedSessions: failedSessions.length,
      averageQualityScore,
      averageProcessingTime,
    };
  },
});