import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  users: defineTable({
    tokenIdentifier: v.string(), // From Convex Auth
    username: v.optional(v.string()),
    email: v.string(),
    preferences: v.object({
      theme: v.optional(v.string()),
      defaultContext: v.optional(v.string()),
      notifications: v.optional(v.boolean()),
    }),
    createdAt: v.number(),
    updatedAt: v.number(),
  })
    .index("by_token", ["tokenIdentifier"])
    .index("by_email", ["email"]),

  prompts: defineTable({
    userId: v.id("users"),
    originalPrompt: v.string(),
    optimizedPrompt: v.optional(v.string()),
    contextDomain: v.optional(v.string()),
    optimizationStatus: v.union(
      v.literal("pending"),
      v.literal("processing"),
      v.literal("completed"),
      v.literal("failed"),
    ),
    createdAt: v.number(),
    updatedAt: v.number(),
  })
    .index("by_user", ["userId"])
    .index("by_status", ["optimizationStatus"])
    .index("by_user_status", ["userId", "optimizationStatus"])
    .index("by_created_at", ["createdAt"]),

  optimizationSessions: defineTable({
    promptId: v.id("prompts"),
    userId: v.id("users"),
    optimizationConfig: v.object({
      iterations: v.number(),
      rounds: v.number(),
      temperature: v.number(),
      maxTokens: v.number(),
      generateReasoning: v.boolean(),
      generateExpertIdentity: v.boolean(),
      seenSetSize: v.number(),
      fewShotCount: v.number(),
    }),
    status: v.union(
      v.literal("pending"),
      v.literal("processing"),
      v.literal("completed"),
      v.literal("failed"),
    ),
    processingTimeMs: v.optional(v.number()),
    qualityScore: v.optional(v.number()),
    iterationsCompleted: v.optional(v.number()),
    currentIteration: v.optional(v.number()),
    errorMessage: v.optional(v.string()),
    expertIdentity: v.optional(v.string()),
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
    mutationHistory: v.optional(
      v.array(
        v.object({
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
      ),
    ),
    finalResults: v.optional(
      v.object({
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
    ),
    createdAt: v.number(),
    updatedAt: v.optional(v.number()),
  })
    .index("by_prompt", ["promptId"])
    .index("by_user", ["userId"])
    .index("by_quality", ["qualityScore"])
    .index("by_created_at", ["createdAt"]),

  feedback: defineTable({
    sessionId: v.id("optimizationSessions"),
    userId: v.id("users"),
    rating: v.number(), // 1-5 scale
    feedbackText: v.optional(v.string()),
    improvementSuggestions: v.optional(v.array(v.string())),
    isHelpful: v.optional(v.boolean()),
    createdAt: v.number(),
  })
    .index("by_session", ["sessionId"])
    .index("by_user", ["userId"])
    .index("by_rating", ["rating"])
    .index("by_created_at", ["createdAt"]),

  templates: defineTable({
    name: v.string(),
    category: v.string(),
    templateText: v.string(),
    description: v.optional(v.string()),
    usageCount: v.number(),
    averageRating: v.optional(v.number()),
    isPublic: v.boolean(),
    createdBy: v.id("users"),
    tags: v.optional(v.array(v.string())),
    createdAt: v.number(),
    updatedAt: v.number(),
  })
    .index("by_category", ["category"])
    .index("by_creator", ["createdBy"])
    .index("by_public", ["isPublic"])
    .index("by_usage", ["usageCount"])
    .index("by_rating", ["averageRating"]),
});
