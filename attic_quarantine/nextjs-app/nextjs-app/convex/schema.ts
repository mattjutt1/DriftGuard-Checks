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

  // Test Logging System
  testExecutions: defineTable({
    executionId: v.string(),
    testType: v.union(
      v.literal("unit"),
      v.literal("integration"),
      v.literal("e2e"),
      v.literal("api"),
      v.literal("cli"),
    ),
    testSuite: v.string(),
    environment: v.string(), // development, staging, production
    startTime: v.number(),
    endTime: v.optional(v.number()),
    duration: v.optional(v.number()),
    status: v.union(
      v.literal("running"),
      v.literal("passed"),
      v.literal("failed"),
      v.literal("skipped"),
      v.literal("timeout"),
    ),
    totalTests: v.number(),
    passedTests: v.number(),
    failedTests: v.number(),
    skippedTests: v.number(),
    coverage: v.optional(v.number()),
    metadata: v.optional(v.object({
      pythonVersion: v.optional(v.string()),
      pytestVersion: v.optional(v.string()),
      nodeVersion: v.optional(v.string()),
      platform: v.optional(v.string()),
      branch: v.optional(v.string()),
      commit: v.optional(v.string()),
    })),
    createdAt: v.number(),
  })
    .index("by_execution_id", ["executionId"])
    .index("by_test_type", ["testType"])
    .index("by_status", ["status"])
    .index("by_created_at", ["createdAt"])
    .index("by_environment", ["environment"]),

  testResults: defineTable({
    executionId: v.string(),
    testId: v.string(),
    testName: v.string(),
    testClass: v.optional(v.string()),
    testModule: v.string(),
    status: v.union(
      v.literal("passed"),
      v.literal("failed"),
      v.literal("skipped"),
      v.literal("timeout"),
    ),
    duration: v.number(),
    errorMessage: v.optional(v.string()),
    errorTrace: v.optional(v.string()),
    assertions: v.optional(v.number()),
    apiCallCount: v.optional(v.number()),
    responseTime: v.optional(v.number()),
    memoryUsage: v.optional(v.number()),
    tags: v.optional(v.array(v.string())),
    metadata: v.optional(v.object({
      promptText: v.optional(v.string()),
      promptLength: v.optional(v.number()),
      responseLength: v.optional(v.number()),
      modelUsed: v.optional(v.string()),
      temperature: v.optional(v.number()),
      maxTokens: v.optional(v.number()),
    })),
    createdAt: v.number(),
  })
    .index("by_execution_id", ["executionId"])
    .index("by_test_id", ["testId"])
    .index("by_status", ["status"])
    .index("by_duration", ["duration"])
    .index("by_test_name", ["testName"]),

  apiCalls: defineTable({
    executionId: v.optional(v.string()),
    testId: v.optional(v.string()),
    callId: v.string(),
    endpoint: v.string(),
    method: v.string(),
    requestSize: v.optional(v.number()),
    responseSize: v.optional(v.number()),
    statusCode: v.number(),
    responseTime: v.number(),
    success: v.boolean(),
    errorMessage: v.optional(v.string()),
    retryCount: v.optional(v.number()),
    requestHeaders: v.optional(v.object({
      contentType: v.optional(v.string()),
      userAgent: v.optional(v.string()),
      authorization: v.optional(v.string()),
    })),
    requestBody: v.optional(v.string()),
    responseBody: v.optional(v.string()),
    metadata: v.optional(v.object({
      modelUsed: v.optional(v.string()),
      promptTokens: v.optional(v.number()),
      completionTokens: v.optional(v.number()),
      totalTokens: v.optional(v.number()),
      cacheHit: v.optional(v.boolean()),
    })),
    timestamp: v.number(),
  })
    .index("by_execution_id", ["executionId"])
    .index("by_endpoint", ["endpoint"])
    .index("by_status_code", ["statusCode"])
    .index("by_response_time", ["responseTime"])
    .index("by_success", ["success"])
    .index("by_timestamp", ["timestamp"]),

  errorLogs: defineTable({
    executionId: v.optional(v.string()),
    testId: v.optional(v.string()),
    errorId: v.string(),
    errorType: v.string(),
    errorMessage: v.string(),
    errorTrace: v.optional(v.string()),
    severity: v.union(
      v.literal("low"),
      v.literal("medium"),
      v.literal("high"),
      v.literal("critical"),
    ),
    context: v.optional(v.object({
      function: v.optional(v.string()),
      file: v.optional(v.string()),
      line: v.optional(v.number()),
      variables: v.optional(v.string()),
    })),
    resolved: v.boolean(),
    resolvedAt: v.optional(v.number()),
    resolvedBy: v.optional(v.string()),
    tags: v.optional(v.array(v.string())),
    occurrenceCount: v.number(),
    firstOccurrence: v.number(),
    lastOccurrence: v.number(),
    createdAt: v.number(),
  })
    .index("by_execution_id", ["executionId"])
    .index("by_error_type", ["errorType"])
    .index("by_severity", ["severity"])
    .index("by_resolved", ["resolved"])
    .index("by_occurrence_count", ["occurrenceCount"])
    .index("by_created_at", ["createdAt"]),
});
