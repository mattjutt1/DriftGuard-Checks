import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

// Query to get prompt details by ID
export const getPrompt = query({
  args: { promptId: v.id("prompts") },
  handler: async (ctx, { promptId }) => {
    return await ctx.db.get(promptId);
  },
});

// Query to get session status with prompt details
export const getSessionWithPrompt = query({
  args: { sessionId: v.id("optimizationSessions") },
  handler: async (ctx, { sessionId }) => {
    const session = await ctx.db.get(sessionId);
    if (!session) return null;

    const prompt = await ctx.db.get(session.promptId);
    if (!prompt) return null;

    return {
      ...session,
      prompt,
    };
  },
});

// Query to get user's recent sessions
export const getRecentSessions = query({
  args: { limit: v.optional(v.number()) },
  handler: async (ctx, { limit = 10 }) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Unauthenticated");

    // Find user
    const user = await ctx.db
      .query("users")
      .withIndex("by_token", (q) => q.eq("tokenIdentifier", identity.tokenIdentifier))
      .first();

    if (!user) return [];

    const sessions = await ctx.db
      .query("optimizationSessions")
      .withIndex("by_user", (q) => q.eq("userId", user._id))
      .order("desc")
      .take(limit);

    // Enrich with prompt data
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

// Mutation to submit feedback
export const submitFeedback = mutation({
  args: {
    sessionId: v.id("optimizationSessions"),
    rating: v.number(),
    feedbackText: v.optional(v.string()),
    improvementSuggestions: v.optional(v.array(v.string())),
    isHelpful: v.optional(v.boolean()),
  },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Unauthenticated");

    // Find user
    const user = await ctx.db
      .query("users")
      .withIndex("by_token", (q) => q.eq("tokenIdentifier", identity.tokenIdentifier))
      .first();

    if (!user) throw new Error("User not found");

    // Verify session exists and belongs to user
    const session = await ctx.db.get(args.sessionId);
    if (!session) throw new Error("Session not found");
    if (session.userId !== user._id) throw new Error("Unauthorized");

    // Create feedback record
    const feedbackId = await ctx.db.insert("feedback", {
      sessionId: args.sessionId,
      userId: user._id,
      rating: args.rating,
      feedbackText: args.feedbackText,
      improvementSuggestions: args.improvementSuggestions,
      isHelpful: args.isHelpful,
      createdAt: Date.now(),
    });

    return feedbackId;
  },
});