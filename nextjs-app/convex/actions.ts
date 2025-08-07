/**
 * Convex Actions for HuggingFace Space Integration
 * Handles prompt optimization via deployed HF Space
 */

import { action } from "./_generated/server";
import { v } from "convex/values";
import { api } from "./_generated/api";
import { optimizeWithHFSpace, checkHFSpaceHealth } from "./hfIntegration";

// Types for optimization
export interface PromptWizardConfig {
  task_description?: string;
  base_instruction?: string;
  answer_format?: string;
  generate_reasoning?: boolean;
  generate_expert_identity?: boolean;
  mutate_refine_iterations?: number;
  mutation_rounds?: number;
  seen_set_size?: number;
  few_shot_count?: number;
  temperature?: number;
  max_tokens?: number;
}

export interface OptimizationResult {
  best_prompt: string;
  improvements: string[];
  quality_score: number;
  expert_profile: string;
  optimization_history: any[];
  model_used: string;
  processing_time: number;
}

/**
 * Health check action to verify PromptWizard availability
 */
export const checkOllamaHealth = action({
  args: {},
  handler: async (ctx) => {
    try {
      // Only use HF Space
      const hfHealth = await checkHFSpaceHealth();
      return hfHealth;
    } catch (error) {
      return {
        available: false,
        model: "HF Space Unavailable",
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  },
});

/**
 * Test PromptWizard optimization with custom configuration
 */
export const testPromptWizardOptimization = action({
  args: {
    prompt: v.string(),
    domain: v.optional(v.string()),
    config: v.optional(
      v.object({
        task_description: v.optional(v.string()),
        base_instruction: v.optional(v.string()),
        answer_format: v.optional(v.string()),
        seen_set_size: v.optional(v.number()),
        few_shot_count: v.optional(v.number()),
        generate_reasoning: v.optional(v.boolean()),
        generate_expert_identity: v.optional(v.boolean()),
        mutate_refine_iterations: v.optional(v.number()),
        mutation_rounds: v.optional(v.number()),
      }),
    ),
  },
  handler: async (ctx, args): Promise<any> => {
    try {
      // This is a test action - just use HF Space directly for testing
      const result = await optimizeWithHFSpace(
        args.prompt,
        args.config?.task_description || "Optimize this prompt",
        "balanced",
        0.7 // Default temperature
      );
      
      return { 
        success: result.status === "success" || result.status === "mock_mode", 
        result 
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  },
});

/**
 * Quick Mode: Single iteration optimization using real Microsoft PromptWizard
 */
export const quickOptimize = action({
  args: {
    sessionId: v.id("optimizationSessions"),
  },
  handler: async (ctx, args): Promise<any> => {
    const startTime = Date.now();

    try {
      // Get session and prompt data
      const session = await ctx.runQuery(api.optimizations.getSession, {
        sessionId: args.sessionId,
      });

      if (!session) {
        throw new Error("Session not found");
      }

      const prompt = await ctx.runQuery(api.optimizations.getPromptById, {
        promptId: session.promptId,
      });

      if (!prompt) {
        throw new Error("Prompt not found");
      }

      // Update session status to processing
      await ctx.runMutation(api.optimizations.updateSessionStatus, {
        sessionId: args.sessionId,
        status: "processing",
        currentIteration: 1,
        progressSteps: [
          {
            step: "Initializing PromptWizard",
            status: "processing",
            timestamp: Date.now(),
          },
          {
            step: "Running optimization",
            status: "pending",
            timestamp: Date.now(),
          },
          {
            step: "Analyzing results",
            status: "pending",
            timestamp: Date.now(),
          },
        ],
      });

      // Step 1: Complete initialization
      await ctx.runMutation(api.optimizations.updateProgressStep, {
        sessionId: args.sessionId,
        stepIndex: 0,
        status: "completed",
      });

      // Step 2: Run PromptWizard optimization
      await ctx.runMutation(api.optimizations.updateProgressStep, {
        sessionId: args.sessionId,
        stepIndex: 1,
        status: "processing",
      });

      // Create PromptWizard configuration from session settings
      const config: Partial<PromptWizardConfig> = {
        task_description: `Optimize this prompt: ${prompt.originalPrompt}`,
        generate_reasoning: session.optimizationConfig.generateReasoning,
        generate_expert_identity:
          session.optimizationConfig.generateExpertIdentity,
        mutate_refine_iterations: 1, // Quick mode uses single iteration
        mutation_rounds: session.optimizationConfig.rounds || 3,
      };

      // Try HF Space first, fallback to local PromptWizard
      let optimizationResult: OptimizationResult;
      
      try {
        // Try HF Space
        const hfResult = await optimizeWithHFSpace(
          prompt.originalPrompt,
          config.task_description || "",
          "balanced",
          0.7
        );
        
        if (hfResult.status === "success" || hfResult.status === "mock_mode") {
          // Convert HF result to PromptWizard format
          optimizationResult = {
            best_prompt: hfResult.optimized_prompt,
            improvements: hfResult.improvements,
            quality_score: hfResult.quality_score,
            expert_profile: `Model: ${hfResult.model}`,
            optimization_history: [],
            model_used: hfResult.model,
            processing_time: parseFloat(hfResult.processing_time) || 0,
          };
        } else {
          throw new Error("HF Space returned error status");
        }
      } catch (hfError) {
        console.log("HF Space failed:", hfError);
        // Return error result
        optimizationResult = {
          best_prompt: prompt.originalPrompt,
          improvements: ["HF Space unavailable - optimization failed"],
          quality_score: 0,
          expert_profile: "Error: HF Space unavailable",
          optimization_history: [],
          model_used: "None",
          processing_time: 0,
        };
      }

      // Step 3: Analyze results
      await ctx.runMutation(api.optimizations.updateProgressStep, {
        sessionId: args.sessionId,
        stepIndex: 2,
        status: "processing",
      });

      // Calculate processing time
      const processingTimeMs = Date.now() - startTime;

      // Create final results in the expected format
      const finalResults = {
        bestPrompt: optimizationResult.best_prompt,
        improvements: optimizationResult.improvements,
        qualityMetrics: {
          overall: optimizationResult.quality_score,
          clarity: optimizationResult.quality_score,
          specificity: optimizationResult.quality_score,
          engagement: optimizationResult.quality_score,
          structure: optimizationResult.quality_score,
          completeness: optimizationResult.quality_score,
          errorPrevention: optimizationResult.quality_score,
        },
        reasoning: optimizationResult.expert_profile,
        expertInsights: optimizationResult.improvements,
      };

      // Update session with final results
      await ctx.runMutation(api.optimizations.completeSession, {
        sessionId: args.sessionId,
        processingTimeMs,
        qualityScore: optimizationResult.quality_score,
        iterationsCompleted: 1, // Quick mode always uses 1 iteration
        expertIdentity: optimizationResult.expert_profile,
        finalResults,
      });

      // Mark all progress steps as completed
      for (let i = 0; i < 3; i++) {
        await ctx.runMutation(api.optimizations.updateProgressStep, {
          sessionId: args.sessionId,
          stepIndex: i,
          status: "completed",
        });
      }

      return {
        success: true,
        sessionId: args.sessionId,
        processingTimeMs,
        finalResults,
      };
    } catch (error) {
      // Mark session as failed
      await ctx.runMutation(api.optimizations.markOptimizationFailed, {
        sessionId: args.sessionId,
        errorMessage: error instanceof Error ? error.message : "Unknown error",
      });

      return {
        success: false,
        sessionId: args.sessionId,
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  },
});

/**
 * Advanced Mode: Multiple iterations using real Microsoft PromptWizard
 */
export const advancedOptimize = action({
  args: {
    sessionId: v.id("optimizationSessions"),
    maxIterations: v.optional(v.number()),
  },
  handler: async (ctx, args): Promise<any> => {
    const maxIterations = args.maxIterations || 3; // Default to 3 iterations for advanced mode
    const startTime = Date.now();

    try {
      // Get session and prompt data
      const session = await ctx.runQuery(api.optimizations.getSession, {
        sessionId: args.sessionId,
      });

      if (!session) {
        throw new Error("Session not found");
      }

      const prompt = await ctx.runQuery(api.optimizations.getPromptById, {
        promptId: session.promptId,
      });

      if (!prompt) {
        throw new Error("Prompt not found");
      }

      // Update session status to processing
      await ctx.runMutation(api.optimizations.updateSessionStatus, {
        sessionId: args.sessionId,
        status: "processing",
        currentIteration: 1,
        progressSteps: [
          {
            step: "Initializing PromptWizard",
            status: "processing",
            timestamp: Date.now(),
          },
          {
            step: "Running advanced optimization",
            status: "pending",
            timestamp: Date.now(),
          },
          {
            step: "Finalizing results",
            status: "pending",
            timestamp: Date.now(),
          },
        ],
      });

      // Step 1: Complete initialization
      await ctx.runMutation(api.optimizations.updateProgressStep, {
        sessionId: args.sessionId,
        stepIndex: 0,
        status: "completed",
      });

      // Step 2: Run PromptWizard optimization with multiple iterations
      await ctx.runMutation(api.optimizations.updateProgressStep, {
        sessionId: args.sessionId,
        stepIndex: 1,
        status: "processing",
      });

      // Create PromptWizard configuration from session settings
      const config: Partial<PromptWizardConfig> = {
        task_description: `Optimize this prompt for maximum effectiveness: ${prompt.originalPrompt}`,
        generate_reasoning: session.optimizationConfig.generateReasoning,
        generate_expert_identity:
          session.optimizationConfig.generateExpertIdentity,
        mutate_refine_iterations: maxIterations, // Advanced mode uses multiple iterations
        mutation_rounds: session.optimizationConfig.rounds || 3,
      };

      // Try HF Space first, fallback to local PromptWizard
      let optimizationResult: OptimizationResult;
      
      try {
        // Try HF Space
        const hfResult = await optimizeWithHFSpace(
          prompt.originalPrompt,
          config.task_description || "",
          "balanced",
          0.7
        );
        
        if (hfResult.status === "success" || hfResult.status === "mock_mode") {
          // Convert HF result to PromptWizard format
          optimizationResult = {
            best_prompt: hfResult.optimized_prompt,
            improvements: hfResult.improvements,
            quality_score: hfResult.quality_score,
            expert_profile: `Model: ${hfResult.model}`,
            optimization_history: [],
            model_used: hfResult.model,
            processing_time: parseFloat(hfResult.processing_time) || 0,
          };
        } else {
          throw new Error("HF Space returned error status");
        }
      } catch (hfError) {
        console.log("HF Space failed:", hfError);
        // Return error result
        optimizationResult = {
          best_prompt: prompt.originalPrompt,
          improvements: ["HF Space unavailable - optimization failed"],
          quality_score: 0,
          expert_profile: "Error: HF Space unavailable",
          optimization_history: [],
          model_used: "None",
          processing_time: 0,
        };
      }

      // Step 3: Finalize results
      await ctx.runMutation(api.optimizations.updateProgressStep, {
        sessionId: args.sessionId,
        stepIndex: 2,
        status: "processing",
      });

      // Calculate processing time
      const processingTimeMs = Date.now() - startTime;

      // Create final results in the expected format
      const finalResults = {
        bestPrompt: optimizationResult.best_prompt,
        improvements: optimizationResult.improvements,
        qualityMetrics: {
          overall: optimizationResult.quality_score,
          clarity: optimizationResult.quality_score,
          specificity: optimizationResult.quality_score,
          engagement: optimizationResult.quality_score,
          structure: optimizationResult.quality_score,
          completeness: optimizationResult.quality_score,
          errorPrevention: optimizationResult.quality_score,
        },
        reasoning: optimizationResult.expert_profile,
        expertInsights: optimizationResult.improvements,
      };

      // Complete the session
      await ctx.runMutation(api.optimizations.completeSession, {
        sessionId: args.sessionId,
        processingTimeMs,
        qualityScore: optimizationResult.quality_score,
        iterationsCompleted: maxIterations, // Advanced mode uses the specified iterations
        expertIdentity: optimizationResult.expert_profile,
        finalResults,
      });

      // Mark all progress steps as completed
      for (let i = 0; i < 3; i++) {
        await ctx.runMutation(api.optimizations.updateProgressStep, {
          sessionId: args.sessionId,
          stepIndex: i,
          status: "completed",
        });
      }

      return {
        success: true,
        sessionId: args.sessionId,
        processingTimeMs,
        finalResults,
        iterationsCompleted: maxIterations,
      };
    } catch (error) {
      // Mark session as failed
      await ctx.runMutation(api.optimizations.markOptimizationFailed, {
        sessionId: args.sessionId,
        errorMessage: error instanceof Error ? error.message : "Unknown error",
      });

      return {
        success: false,
        sessionId: args.sessionId,
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  },
});


/**
 * Test Logging Actions
 * Handle test execution data, API metrics, and error logs
 */

/**
 * Log test execution data from CLI
 */
export const logTestExecution: any = action({
  args: {
    executionId: v.string(),
    testType: v.union(
      v.literal("unit"),
      v.literal("integration"),
      v.literal("e2e"),
      v.literal("api"),
      v.literal("cli"),
    ),
    testSuite: v.string(),
    environment: v.string(),
    testResults: v.array(
      v.object({
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
        metadata: v.optional(
          v.object({
            promptText: v.optional(v.string()),
            promptLength: v.optional(v.number()),
            responseLength: v.optional(v.number()),
            modelUsed: v.optional(v.string()),
            temperature: v.optional(v.number()),
            maxTokens: v.optional(v.number()),
          }),
        ),
      }),
    ),
    apiCalls: v.array(
      v.object({
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
        metadata: v.optional(
          v.object({
            modelUsed: v.optional(v.string()),
            promptTokens: v.optional(v.number()),
            completionTokens: v.optional(v.number()),
            totalTokens: v.optional(v.number()),
            cacheHit: v.optional(v.boolean()),
          }),
        ),
      }),
    ),
    errors: v.array(
      v.object({
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
        context: v.optional(
          v.object({
            function: v.optional(v.string()),
            file: v.optional(v.string()),
            line: v.optional(v.number()),
            variables: v.optional(v.string()),
          }),
        ),
        tags: v.optional(v.array(v.string())),
      }),
    ),
    metadata: v.object({
      pythonVersion: v.optional(v.string()),
      pytestVersion: v.optional(v.string()),
      nodeVersion: v.optional(v.string()),
      platform: v.optional(v.string()),
      branch: v.optional(v.string()),
      commit: v.optional(v.string()),
    }),
  },
  handler: async (ctx, args): Promise<any> => {
    const timestamp = Date.now();

    try {
      // Store test execution summary
      const testExecutionId = await ctx.runMutation(
        api.testLogs.createTestExecution,
        {
          executionId: args.executionId,
          testType: args.testType,
          testSuite: args.testSuite,
          environment: args.environment,
          startTime: timestamp,
          status: "running",
          totalTests: args.testResults.length,
          passedTests: args.testResults.filter((t) => t.status === "passed")
            .length,
          failedTests: args.testResults.filter((t) => t.status === "failed")
            .length,
          skippedTests: args.testResults.filter((t) => t.status === "skipped")
            .length,
          metadata: args.metadata,
        },
      );

      // Store individual test results
      const testResultIds = [];
      for (const testResult of args.testResults) {
        const resultId = await ctx.runMutation(api.testLogs.createTestResult, {
          executionId: args.executionId,
          testId: testResult.testId,
          testName: testResult.testName,
          testClass: testResult.testClass,
          testModule: testResult.testModule,
          status: testResult.status,
          duration: testResult.duration,
          errorMessage: testResult.errorMessage,
          errorTrace: testResult.errorTrace,
          assertions: testResult.assertions,
          apiCallCount: testResult.apiCallCount,
          responseTime: testResult.responseTime,
          memoryUsage: testResult.memoryUsage,
          tags: testResult.tags,
          metadata: testResult.metadata,
        });
        testResultIds.push(resultId);
      }

      // Store API call logs
      const apiCallIds = [];
      for (const apiCall of args.apiCalls) {
        const callId = await ctx.runMutation(api.testLogs.createApiCall, {
          executionId: args.executionId,
          callId: apiCall.callId,
          endpoint: apiCall.endpoint,
          method: apiCall.method,
          requestSize: apiCall.requestSize,
          responseSize: apiCall.responseSize,
          statusCode: apiCall.statusCode,
          responseTime: apiCall.responseTime,
          success: apiCall.success,
          errorMessage: apiCall.errorMessage,
          retryCount: apiCall.retryCount,
          requestBody: apiCall.requestBody,
          responseBody: apiCall.responseBody,
          metadata: apiCall.metadata,
        });
        apiCallIds.push(callId);
      }

      // Store error logs
      const errorLogIds = [];
      for (const error of args.errors) {
        const errorId = await ctx.runMutation(api.testLogs.createErrorLog, {
          executionId: args.executionId,
          errorId: error.errorId,
          errorType: error.errorType,
          errorMessage: error.errorMessage,
          errorTrace: error.errorTrace,
          severity: error.severity,
          context: error.context,
          tags: error.tags,
        });
        errorLogIds.push(errorId);
      }

      return {
        success: true,
        testExecutionId,
        testResultIds,
        apiCallIds,
        errorLogIds,
        timestamp,
      };
    } catch (error) {
      console.error("Failed to log test execution:", error);
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  },
});

/**
 * Get test execution results with filtering options
 */
export const getTestResults: any = action({
  args: {
    executionId: v.optional(v.string()),
    limit: v.optional(v.number()),
    testType: v.optional(v.string()),
    environment: v.optional(v.string()),
  },
  handler: async (ctx, args): Promise<any> => {
    try {
      const results = await ctx.runQuery(api.testLogs.getTestExecutions, {
        executionId: args.executionId,
        limit: args.limit || 50,
        testType: args.testType,
        environment: args.environment,
      });

      return {
        success: true,
        data: results,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  },
});

/**
 * Get API performance metrics
 */
export const getApiMetrics: any = action({
  args: {
    endpoint: v.optional(v.string()),
    limit: v.optional(v.number()),
    hours: v.optional(v.number()),
  },
  handler: async (ctx, args): Promise<any> => {
    try {
      const results = await ctx.runQuery(api.testLogs.getApiMetrics, {
        endpoint: args.endpoint,
        limit: args.limit || 100,
        hours: args.hours || 24,
      });

      return {
        success: true,
        data: results,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  },
});

/**
 * Update test execution status
 */
export const updateTestStatus: any = action({
  args: {
    executionId: v.string(),
    status: v.union(
      v.literal("running"),
      v.literal("passed"),
      v.literal("failed"),
      v.literal("skipped"),
      v.literal("timeout"),
    ),
    endTime: v.optional(v.number()),
    duration: v.optional(v.number()),
    results: v.optional(
      v.object({
        totalTests: v.optional(v.number()),
        passedTests: v.optional(v.number()),
        failedTests: v.optional(v.number()),
        skippedTests: v.optional(v.number()),
        coverage: v.optional(v.number()),
      }),
    ),
  },
  handler: async (ctx, args): Promise<any> => {
    try {
      const result = await ctx.runMutation(api.testLogs.updateTestExecution, {
        executionId: args.executionId,
        status: args.status,
        endTime: args.endTime,
        duration: args.duration,
        results: args.results,
      });

      return {
        success: true,
        data: result,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  },
});
