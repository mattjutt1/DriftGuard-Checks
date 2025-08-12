/**
 * Convex Test Logging Functions
 * Functions for managing test execution data, API metrics, and error logs
 */

import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

/**
 * Create a test execution record
 */
export const createTestExecution = mutation({
  args: {
    executionId: v.string(),
    testType: v.union(
      v.literal("unit"),
      v.literal("integration"),
      v.literal("e2e"),
      v.literal("api"),
      v.literal("cli")
    ),
    testSuite: v.string(),
    environment: v.string(),
    startTime: v.number(),
    status: v.union(
      v.literal("running"),
      v.literal("passed"),
      v.literal("failed"),
      v.literal("skipped"),
      v.literal("timeout")
    ),
    totalTests: v.number(),
    passedTests: v.number(),
    failedTests: v.number(),
    skippedTests: v.number(),
    metadata: v.optional(v.object({
      pythonVersion: v.optional(v.string()),
      pytestVersion: v.optional(v.string()),
      nodeVersion: v.optional(v.string()),
      platform: v.optional(v.string()),
      branch: v.optional(v.string()),
      commit: v.optional(v.string()),
    })),
  },
  handler: async (ctx, args) => {
    const testExecutionId = await ctx.db.insert("testExecutions", {
      executionId: args.executionId,
      testType: args.testType,
      testSuite: args.testSuite,
      environment: args.environment,
      startTime: args.startTime,
      status: args.status,
      totalTests: args.totalTests,
      passedTests: args.passedTests,
      failedTests: args.failedTests,
      skippedTests: args.skippedTests,
      metadata: args.metadata,
      createdAt: Date.now(),
    });

    return testExecutionId;
  },
});

/**
 * Create a test result record
 */
export const createTestResult = mutation({
  args: {
    executionId: v.string(),
    testId: v.string(),
    testName: v.string(),
    testClass: v.optional(v.string()),
    testModule: v.string(),
    status: v.union(
      v.literal("passed"),
      v.literal("failed"),
      v.literal("skipped"),
      v.literal("timeout")
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
  },
  handler: async (ctx, args) => {
    const testResultId = await ctx.db.insert("testResults", {
      executionId: args.executionId,
      testId: args.testId,
      testName: args.testName,
      testClass: args.testClass,
      testModule: args.testModule,
      status: args.status,
      duration: args.duration,
      errorMessage: args.errorMessage,
      errorTrace: args.errorTrace,
      assertions: args.assertions,
      apiCallCount: args.apiCallCount,
      responseTime: args.responseTime,
      memoryUsage: args.memoryUsage,
      tags: args.tags,
      metadata: args.metadata,
      createdAt: Date.now(),
    });

    return testResultId;
  },
});

/**
 * Create an API call log
 */
export const createApiCall = mutation({
  args: {
    executionId: v.string(),
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
    requestBody: v.optional(v.string()),
    responseBody: v.optional(v.string()),
    metadata: v.optional(v.object({
      modelUsed: v.optional(v.string()),
      promptTokens: v.optional(v.number()),
      completionTokens: v.optional(v.number()),
      totalTokens: v.optional(v.number()),
      cacheHit: v.optional(v.boolean()),
    })),
  },
  handler: async (ctx, args) => {
    const apiCallId = await ctx.db.insert("apiCalls", {
      executionId: args.executionId,
      callId: args.callId,
      endpoint: args.endpoint,
      method: args.method,
      requestSize: args.requestSize,
      responseSize: args.responseSize,
      statusCode: args.statusCode,
      responseTime: args.responseTime,
      success: args.success,
      errorMessage: args.errorMessage,
      retryCount: args.retryCount,
      requestBody: args.requestBody,
      responseBody: args.responseBody,
      metadata: args.metadata,
      timestamp: Date.now(),
    });

    return apiCallId;
  },
});

/**
 * Create an error log
 */
export const createErrorLog = mutation({
  args: {
    executionId: v.string(),
    errorId: v.string(),
    errorType: v.string(),
    errorMessage: v.string(),
    errorTrace: v.optional(v.string()),
    severity: v.union(
      v.literal("low"),
      v.literal("medium"),
      v.literal("high"),
      v.literal("critical")
    ),
    context: v.optional(v.object({
      function: v.optional(v.string()),
      file: v.optional(v.string()),
      line: v.optional(v.number()),
      variables: v.optional(v.string()),
    })),
    tags: v.optional(v.array(v.string())),
  },
  handler: async (ctx, args) => {
    const errorLogId = await ctx.db.insert("errorLogs", {
      executionId: args.executionId,
      errorId: args.errorId,
      errorType: args.errorType,
      errorMessage: args.errorMessage,
      errorTrace: args.errorTrace,
      severity: args.severity,
      context: args.context,
      resolved: false,
      tags: args.tags,
      occurrenceCount: 1,
      firstOccurrence: Date.now(),
      lastOccurrence: Date.now(),
      createdAt: Date.now(),
    });

    return errorLogId;
  },
});

/**
 * Get test executions with filtering
 */
export const getTestExecutions = query({
  args: {
    executionId: v.optional(v.string()),
    limit: v.optional(v.number()),
    testType: v.optional(v.string()),
    environment: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const limit = args.limit || 50;

    let query = ctx.db.query("testExecutions");

    if (args.executionId) {
      query = query.filter((q) => q.eq(q.field("executionId"), args.executionId));
    }

    if (args.testType) {
      query = query.filter((q) => q.eq(q.field("testType"), args.testType as any));
    }

    if (args.environment) {
      query = query.filter((q) => q.eq(q.field("environment"), args.environment));
    }

    const results = await query.order("desc").take(limit);
    return results;
  },
});

/**
 * Get API metrics
 */
export const getApiMetrics = query({
  args: {
    endpoint: v.optional(v.string()),
    limit: v.optional(v.number()),
    hours: v.optional(v.number()),
  },
  handler: async (ctx, args) => {
    const limit = args.limit || 100;
    const hours = args.hours || 24;
    const threshold = Date.now() - (hours * 60 * 60 * 1000);

    let query = ctx.db.query("apiCalls")
      .filter((q) => q.gte(q.field("timestamp"), threshold));

    if (args.endpoint) {
      query = query.filter((q) => q.eq(q.field("endpoint"), args.endpoint));
    }

    const results = await query.order("desc").take(limit);
    return results;
  },
});

/**
 * Update test execution status
 */
export const updateTestExecution = mutation({
  args: {
    executionId: v.string(),
    status: v.union(
      v.literal("running"),
      v.literal("passed"),
      v.literal("failed"),
      v.literal("skipped"),
      v.literal("timeout")
    ),
    endTime: v.optional(v.number()),
    duration: v.optional(v.number()),
    results: v.optional(v.object({
      totalTests: v.optional(v.number()),
      passedTests: v.optional(v.number()),
      failedTests: v.optional(v.number()),
      skippedTests: v.optional(v.number()),
      coverage: v.optional(v.number()),
    })),
  },
  handler: async (ctx, args) => {
    const execution = await ctx.db
      .query("testExecutions")
      .filter((q) => q.eq(q.field("executionId"), args.executionId))
      .first();

    if (!execution) {
      throw new Error("Test execution not found");
    }

    const updateData: any = {
      status: args.status,
    };

    if (args.endTime) {
      updateData.endTime = args.endTime;
    }

    if (args.duration) {
      updateData.duration = args.duration;
    }

    if (args.results) {
      if (args.results.totalTests !== undefined) {
        updateData.totalTests = args.results.totalTests;
      }
      if (args.results.passedTests !== undefined) {
        updateData.passedTests = args.results.passedTests;
      }
      if (args.results.failedTests !== undefined) {
        updateData.failedTests = args.results.failedTests;
      }
      if (args.results.skippedTests !== undefined) {
        updateData.skippedTests = args.results.skippedTests;
      }
      if (args.results.coverage !== undefined) {
        updateData.coverage = args.results.coverage;
      }
    }

    await ctx.db.patch(execution._id, updateData);
    return execution._id;
  },
});
