/**
 * Convex Data Seeding Functions
 * Functions to populate demo data for testing the advanced UI
 */

import { mutation } from "./_generated/server";
import { v } from "convex/values";

/**
 * Seed demo data for testing
 */
export const seedDemoData = mutation({
  args: {},
  handler: async (ctx) => {
    // Check if demo user already exists
    const existingUser = await ctx.db
      .query("users")
      .filter((q) => q.eq(q.field("email"), "demo@promptevolver.com"))
      .first();

    let userId;
    if (existingUser) {
      userId = existingUser._id;
    } else {
      // Create demo user
      userId = await ctx.db.insert("users", {
        tokenIdentifier: "demo-user",
        email: "demo@promptevolver.com",
        username: "Demo User",
        preferences: {
          theme: "light",
          defaultContext: "general",
          notifications: true,
        },
        createdAt: Date.now(),
        updatedAt: Date.now(),
      });
    }

    // Create some demo prompts and sessions
    const demoPrompts = [
      {
        original: "Write a product description for a smartwatch",
        optimized: "Create a compelling, feature-rich product description for a premium smartwatch that highlights its health monitoring capabilities, sleek design, and seamless connectivity. Focus on benefits that resonate with health-conscious professionals aged 25-45.",
        context: "marketing",
        quality: 8.5,
      },
      {
        original: "Explain machine learning",
        optimized: "Provide a comprehensive yet accessible explanation of machine learning, including its core concepts, practical applications, and real-world examples. Structure the response for a business audience with minimal technical background, emphasizing practical benefits and use cases.",
        context: "education",
        quality: 9.2,
      },
      {
        original: "Help me write an email",
        optimized: "Assist me in crafting a professional, persuasive email for [specific purpose]. Include guidance on subject line optimization, appropriate tone, clear call-to-action, and follow-up strategy. Provide a template structure that can be customized for different scenarios.",
        context: "business communication",
        quality: 7.8,
      },
    ];

    const sessionIds = [];

    for (const demo of demoPrompts) {
      // Create prompt
      const promptId = await ctx.db.insert("prompts", {
        userId,
        originalPrompt: demo.original,
        optimizedPrompt: demo.optimized,
        contextDomain: demo.context,
        optimizationStatus: "completed",
        createdAt: Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000, // Random time in last week
        updatedAt: Date.now(),
      });

      // Create optimization session
      const sessionId = await ctx.db.insert("optimizationSessions", {
        promptId,
        userId,
        optimizationConfig: {
          iterations: Math.floor(Math.random() * 3) + 2, // 2-4 iterations
          rounds: 3,
          temperature: 0.7,
          maxTokens: 2000,
          generateReasoning: true,
          generateExpertIdentity: true,
          seenSetSize: 10,
          fewShotCount: 3,
        },
        status: "completed",
        processingTimeMs: Math.floor(Math.random() * 60000) + 30000, // 30-90 seconds
        qualityScore: demo.quality,
        iterationsCompleted: Math.floor(Math.random() * 3) + 2,
        expertIdentity: "Marketing Communications Specialist",
        finalResults: {
          bestPrompt: demo.optimized,
          improvements: [
            "Added specific target audience definition",
            "Included clear structure and formatting guidelines",
            "Enhanced with actionable outcome specifications",
            "Improved clarity and specificity of requirements",
          ],
          qualityMetrics: {
            clarity: demo.quality + Math.random() * 0.5 - 0.25,
            specificity: demo.quality + Math.random() * 0.5 - 0.25,
            engagement: demo.quality + Math.random() * 0.5 - 0.25,
            structure: demo.quality + Math.random() * 0.5 - 0.25,
            completeness: demo.quality + Math.random() * 0.5 - 0.25,
            errorPrevention: demo.quality + Math.random() * 0.5 - 0.25,
            overall: demo.quality,
          },
          reasoning: "The optimized prompt provides clear context, specific requirements, and actionable guidance that will lead to more consistent and valuable responses.",
          expertInsights: [
            "Consider adding specific examples to further improve clarity",
            "The target audience specification significantly enhances relevance",
            "Structure guidelines help ensure consistent output format",
          ],
        },
        createdAt: Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000,
        updatedAt: Date.now(),
      });

      sessionIds.push(sessionId);

      // Add some feedback
      if (Math.random() > 0.3) { // 70% chance of feedback
        await ctx.db.insert("feedback", {
          sessionId,
          userId,
          rating: Math.floor(Math.random() * 2) + 4, // 4-5 stars
          feedbackText: "Great optimization! The improved prompt is much more specific and actionable.",
          isHelpful: true,
          createdAt: Date.now() - Math.random() * 5 * 24 * 60 * 60 * 1000,
        });
      }
    }

    return {
      message: "Demo data seeded successfully",
      userId,
      sessionIds,
      promptCount: demoPrompts.length,
    };
  },
});

/**
 * Clear all demo data
 */
export const clearDemoData = mutation({
  args: {},
  handler: async (ctx) => {
    // Find demo user
    const demoUser = await ctx.db
      .query("users")
      .filter((q) => q.eq(q.field("email"), "demo@promptevolver.com"))
      .first();

    if (!demoUser) {
      return { message: "No demo data found" };
    }

    // Delete all sessions for demo user
    const sessions = await ctx.db
      .query("optimizationSessions")
      .filter((q) => q.eq(q.field("userId"), demoUser._id))
      .collect();

    for (const session of sessions) {
      await ctx.db.delete(session._id);
    }

    // Delete all prompts for demo user
    const prompts = await ctx.db
      .query("prompts")
      .filter((q) => q.eq(q.field("userId"), demoUser._id))
      .collect();

    for (const prompt of prompts) {
      await ctx.db.delete(prompt._id);
    }

    // Delete all feedback for demo user
    const feedback = await ctx.db
      .query("feedback")
      .filter((q) => q.eq(q.field("userId"), demoUser._id))
      .collect();

    for (const f of feedback) {
      await ctx.db.delete(f._id);
    }

    // Delete demo user
    await ctx.db.delete(demoUser._id);

    return {
      message: "Demo data cleared successfully",
      deletedSessions: sessions.length,
      deletedPrompts: prompts.length,
      deletedFeedback: feedback.length,
    };
  },
});
