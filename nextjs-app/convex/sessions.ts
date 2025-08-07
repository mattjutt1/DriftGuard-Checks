/**
 * Convex Session Management Functions
 * Functions for managing optimization sessions, history, and user feedback
 */

import { mutation, query } from "./_generated/server";
import { v } from "convex/values";
import { Id } from "./_generated/dataModel";

/**
 * Get recent optimization sessions
 */
export const getRecentSessions = query({
  args: {
    limit: v.optional(v.number()),
    userId: v.optional(v.id("users")),
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
 * Get session details by ID
 */
export const getSessionDetails = query({
  args: {
    sessionId: v.id("optimizationSessions"),
  },
  handler: async (ctx, args) => {
    const session = await ctx.db.get(args.sessionId);
    if (!session) return null;

    // Get associated prompt and user data
    const prompt = await ctx.db.get(session.promptId);
    const user = await ctx.db.get(session.userId);

    // Get feedback for this session
    const feedback = await ctx.db
      .query("feedback")
      .filter((q) => q.eq(q.field("sessionId"), args.sessionId))
      .collect();

    return {
      ...session,
      prompt,
      user,
      feedback,
    };
  },
});

/**
 * Submit feedback for an optimization session
 */
export const submitFeedback = mutation({
  args: {
    sessionId: v.id("optimizationSessions"),
    rating: v.number(), // 1-5 scale
    feedbackText: v.optional(v.string()),
    improvementSuggestions: v.optional(v.array(v.string())),
    isHelpful: v.optional(v.boolean()),
  },
  handler: async (ctx, args) => {
    const session = await ctx.db.get(args.sessionId);
    if (!session) {
      throw new Error("Session not found");
    }

    // Create feedback record
    const feedbackId = await ctx.db.insert("feedback", {
      sessionId: args.sessionId,
      userId: session.userId,
      rating: args.rating,
      feedbackText: args.feedbackText,
      improvementSuggestions: args.improvementSuggestions,
      isHelpful: args.isHelpful,
      createdAt: Date.now(),
    });

    return feedbackId;
  },
});

/**
 * Get feedback statistics
 */
export const getFeedbackStats = query({
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
        totalFeedback: 0,
        averageRating: 0,
        helpfulCount: 0,
        ratingDistribution: { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 },
      };
    }

    const allFeedback = await ctx.db
      .query("feedback")
      .filter((q) => q.eq(q.field("userId"), userId))
      .collect();

    const totalFeedback = allFeedback.length;
    const averageRating = totalFeedback > 0
      ? allFeedback.reduce((sum, f) => sum + f.rating, 0) / totalFeedback
      : 0;

    const helpfulCount = allFeedback.filter(f => f.isHelpful === true).length;

    const ratingDistribution = allFeedback.reduce((dist, f) => {
      dist[f.rating as keyof typeof dist] = (dist[f.rating as keyof typeof dist] || 0) + 1;
      return dist;
    }, { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 });

    return {
      totalFeedback,
      averageRating,
      helpfulCount,
      ratingDistribution,
    };
  },
});

/**
 * Get sessions by status
 */
export const getSessionsByStatus = query({
  args: {
    status: v.union(
      v.literal("pending"),
      v.literal("processing"),
      v.literal("completed"),
      v.literal("failed")
    ),
    limit: v.optional(v.number()),
    userId: v.optional(v.id("users")),
  },
  handler: async (ctx, args) => {
    const limit = args.limit || 50;

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
      .filter((q) =>
        q.and(
          q.eq(q.field("userId"), userId),
          q.eq(q.field("status"), args.status)
        )
      )
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
 * Search sessions by prompt content
 */
export const searchSessions = query({
  args: {
    searchTerm: v.string(),
    limit: v.optional(v.number()),
    userId: v.optional(v.id("users")),
  },
  handler: async (ctx, args) => {
    const limit = args.limit || 20;

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

    // Get all sessions for the user
    const sessions = await ctx.db
      .query("optimizationSessions")
      .filter((q) => q.eq(q.field("userId"), userId))
      .order("desc")
      .take(100); // Get more to search through

    // Get associated prompts and filter by search term
    const sessionsWithPrompts = await Promise.all(
      sessions.map(async (session) => {
        const prompt = await ctx.db.get(session.promptId);
        return {
          ...session,
          prompt,
        };
      })
    );

    // Filter by search term (case insensitive)
    const filteredSessions = sessionsWithPrompts.filter(session => {
      const searchLower = args.searchTerm.toLowerCase();
      const originalPrompt = session.prompt?.originalPrompt?.toLowerCase() || "";
      const optimizedPrompt = session.prompt?.optimizedPrompt?.toLowerCase() || "";
      const contextDomain = session.prompt?.contextDomain?.toLowerCase() || "";

      return originalPrompt.includes(searchLower) ||
             optimizedPrompt.includes(searchLower) ||
             contextDomain.includes(searchLower);
    });

    return filteredSessions.slice(0, limit);
  },
});

/**
 * Delete a session (and associated data)
 */
export const deleteSession = mutation({
  args: {
    sessionId: v.id("optimizationSessions"),
  },
  handler: async (ctx, args) => {
    const session = await ctx.db.get(args.sessionId);
    if (!session) {
      throw new Error("Session not found");
    }

    // Delete associated feedback
    const feedback = await ctx.db
      .query("feedback")
      .filter((q) => q.eq(q.field("sessionId"), args.sessionId))
      .collect();

    for (const f of feedback) {
      await ctx.db.delete(f._id);
    }

    // Delete the session
    await ctx.db.delete(args.sessionId);

    // Optionally delete the prompt if no other sessions reference it
    const otherSessions = await ctx.db
      .query("optimizationSessions")
      .filter((q) => q.eq(q.field("promptId"), session.promptId))
      .collect();

    if (otherSessions.length === 0) {
      await ctx.db.delete(session.promptId);
    }

    return args.sessionId;
  },
});

/**
 * Update session metadata
 */
export const updateSessionMetadata = mutation({
  args: {
    sessionId: v.id("optimizationSessions"),
    metadata: v.object({
      tags: v.optional(v.array(v.string())),
      notes: v.optional(v.string()),
      favorite: v.optional(v.boolean()),
    }),
  },
  handler: async (ctx, args) => {
    const session = await ctx.db.get(args.sessionId);
    if (!session) {
      throw new Error("Session not found");
    }

    // Note: This would require adding metadata fields to the schema
    // For now, we'll just return the sessionId
    // In a real implementation, you'd add these fields to the schema first

    return args.sessionId;
  },
});

/**
 * Get session performance metrics
 */
export const getPerformanceMetrics = query({
  args: {
    timeRange: v.optional(v.union(
      v.literal("24h"),
      v.literal("7d"),
      v.literal("30d"),
      v.literal("90d")
    )),
    userId: v.optional(v.id("users")),
  },
  handler: async (ctx, args) => {
    const timeRange = args.timeRange || "30d";

    // Calculate time threshold
    const now = Date.now();
    const timeThresholds = {
      "24h": 24 * 60 * 60 * 1000,
      "7d": 7 * 24 * 60 * 60 * 1000,
      "30d": 30 * 24 * 60 * 60 * 1000,
      "90d": 90 * 24 * 60 * 60 * 1000,
    };
    const threshold = now - timeThresholds[timeRange];

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
        totalOptimizations: 0,
        successRate: 0,
        averageProcessingTime: 0,
        averageQualityImprovement: 0,
        topContextDomains: [],
      };
    }

    const sessions = await ctx.db
      .query("optimizationSessions")
      .filter((q) =>
        q.and(
          q.eq(q.field("userId"), userId),
          q.gte(q.field("createdAt"), threshold)
        )
      )
      .collect();

    const completedSessions = sessions.filter(s => s.status === "completed");
    const successRate = sessions.length > 0 ? completedSessions.length / sessions.length : 0;

    const averageProcessingTime = completedSessions.length > 0
      ? completedSessions.reduce((sum, s) => sum + (s.processingTimeMs || 0), 0) / completedSessions.length
      : 0;

    const averageQualityScore = completedSessions.length > 0
      ? completedSessions.reduce((sum, s) => sum + (s.qualityScore || 0), 0) / completedSessions.length
      : 0;

    // Get context domains (would need to join with prompts)
    const topContextDomains: string[] = [];

    return {
      totalOptimizations: sessions.length,
      successRate,
      averageProcessingTime,
      averageQualityImprovement: averageQualityScore,
      topContextDomains,
    };
  },
});
