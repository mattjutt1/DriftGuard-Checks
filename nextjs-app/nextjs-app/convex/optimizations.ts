import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

// Query to get optimization history for a user
export const getHistory = query({
  args: { 
    userId: v.optional(v.id("users")),
    limit: v.optional(v.number()) 
  },
  handler: async (ctx, { userId, limit = 20 }) => {
    if (!userId) {
      // If no userId provided, get from authenticated user
      const identity = await ctx.auth.getUserIdentity();
      if (!identity) throw new Error("Unauthenticated");
      
      // Find user by token identifier
      const user = await ctx.db
        .query("users")
        .withIndex("by_token", (q) => q.eq("tokenIdentifier", identity.tokenIdentifier))
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
      .withIndex("by_token", (q) => q.eq("tokenIdentifier", identity.tokenIdentifier))
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
      },
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
    const { sessionId, optimizedPrompt, qualityScore, processingTimeMs, improvements, metrics } = args;
    
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