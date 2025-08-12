/**
 * Public HTTP endpoints for CLI access
 * These can be called without authentication via HTTP API
 */

import { httpRouter } from "convex/server";
import { httpAction } from "./_generated/server";
import { api } from "./_generated/api";

const http = httpRouter();

/**
 * Public health check endpoint
 * GET /health
 */
http.route({
  path: "/health",
  method: "GET",
  handler: httpAction(async (ctx, request) => {
    const startTime = Date.now();
    const callId = `health_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    try {
      // Call the internal action
      const result = await ctx.runAction(api.actions.checkOllamaHealth, {});

      const responseTime = Date.now() - startTime;
      const responseBody = JSON.stringify({ status: "success", data: result });

      // Log API call
      await ctx.runMutation(api.testLogs.createApiCall, {
        callId,
        endpoint: "/health",
        method: "GET",
        requestSize: 0,
        responseSize: responseBody.length,
        statusCode: 200,
        responseTime,
        success: result.available,
        responseBody: `Health: ${result.available ? 'available' : 'unavailable'}`,
        metadata: {
          modelUsed: result.model,
        },
      });

      return new Response(responseBody, {
        status: 200,
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
      });
    } catch (error) {
      const responseTime = Date.now() - startTime;
      const errorMessage = error instanceof Error ? error.message : "Unknown error";

      // Log failed API call
      await ctx.runMutation(api.testLogs.createApiCall, {
        callId,
        endpoint: "/health",
        method: "GET",
        requestSize: 0,
        statusCode: 500,
        responseTime,
        success: false,
        errorMessage,
      });

      return new Response(
        JSON.stringify({
          status: "error",
          error: errorMessage,
        }),
        {
          status: 500,
          headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
          },
        },
      );
    }
  }),
});

/**
 * Public prompt optimization endpoint
 * POST /optimize
 */
http.route({
  path: "/optimize",
  method: "POST",
  handler: httpAction(async (ctx, request) => {
    const startTime = Date.now();
    const callId = `optimize_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    try {
      const body = await request.json();
      const { prompt, domain, config } = body;

      if (!prompt) {
        // Log failed API call
        await ctx.runMutation(api.testLogs.createApiCall, {
          callId,
          endpoint: "/optimize",
          method: "POST",
          requestSize: JSON.stringify(body).length,
          statusCode: 400,
          responseTime: Date.now() - startTime,
          success: false,
          errorMessage: "Prompt is required",
          metadata: {
            modelUsed: "Microsoft PromptWizard + Qwen3:4b",
          },
        });

        return new Response(
          JSON.stringify({
            status: "error",
            error: "Prompt is required",
          }),
          {
            status: 400,
            headers: {
              "Content-Type": "application/json",
              "Access-Control-Allow-Origin": "*",
            },
          },
        );
      }

      // Call the internal action
      const result = await ctx.runAction(
        api.actions.testPromptWizardOptimization,
        {
          prompt,
          domain: domain || "general",
          config: config || {},
        },
      );

      const responseTime = Date.now() - startTime;
      const responseBody = JSON.stringify({ status: "success", data: result });

      // Log successful API call
      await ctx.runMutation(api.testLogs.createApiCall, {
        callId,
        endpoint: "/optimize",
        method: "POST",
        requestSize: JSON.stringify(body).length,
        responseSize: responseBody.length,
        statusCode: 200,
        responseTime,
        success: result.success,
        requestBody: JSON.stringify({ prompt: prompt.substring(0, 200) + "...", domain, config }),
        responseBody: result.success ? `Success: ${result.result?.best_prompt?.substring(0, 100)}...` : `Error: ${result.error}`,
        metadata: {
          modelUsed: "Microsoft PromptWizard + Qwen3:4b",
          promptTokens: prompt.length / 4, // Rough token estimate
          completionTokens: result.result?.best_prompt?.length / 4 || 0,
          totalTokens: (prompt.length + (result.result?.best_prompt?.length || 0)) / 4,
        },
      });

      return new Response(responseBody, {
        status: 200,
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
      });
    } catch (error) {
      const responseTime = Date.now() - startTime;
      const errorMessage = error instanceof Error ? error.message : "Unknown error";

      // Log failed API call
      await ctx.runMutation(api.testLogs.createApiCall, {
        callId,
        endpoint: "/optimize",
        method: "POST",
        statusCode: 500,
        responseTime,
        success: false,
        errorMessage,
        metadata: {
          modelUsed: "Microsoft PromptWizard + Qwen3:4b",
        },
      });

      return new Response(
        JSON.stringify({
          status: "error",
          error: errorMessage,
        }),
        {
          status: 500,
          headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
          },
        },
      );
    }
  }),
});

/**
 * Handle CORS preflight requests
 */
http.route({
  path: "/health",
  method: "OPTIONS",
  handler: httpAction(async (ctx, request) => {
    return new Response(null, {
      status: 200,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
      },
    });
  }),
});

http.route({
  path: "/optimize",
  method: "OPTIONS",
  handler: httpAction(async (ctx, request) => {
    return new Response(null, {
      status: 200,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
      },
    });
  }),
});

/**
 * Test logging endpoints for CLI integration
 */

/**
 * Submit test execution data
 * POST /log-test
 */
http.route({
  path: "/log-test",
  method: "POST",
  handler: httpAction(async (ctx, request) => {
    try {
      const body = await request.json();
      const {
        executionId,
        testType,
        testSuite,
        environment,
        testResults,
        apiCalls,
        errors,
        metadata
      } = body;

      if (!executionId || !testType || !testSuite) {
        return new Response(
          JSON.stringify({
            status: "error",
            error: "executionId, testType, and testSuite are required",
          }),
          {
            status: 400,
            headers: {
              "Content-Type": "application/json",
              "Access-Control-Allow-Origin": "*",
            },
          },
        );
      }

      // Call the internal action to store test data
      const result = await ctx.runAction(api.actions.logTestExecution, {
        executionId,
        testType,
        testSuite,
        environment: environment || "development",
        testResults: testResults || [],
        apiCalls: apiCalls || [],
        errors: errors || [],
        metadata: metadata || {},
      });

      return new Response(
        JSON.stringify({
          status: "success",
          data: result,
        }),
        {
          status: 200,
          headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
          },
        },
      );
    } catch (error) {
      return new Response(
        JSON.stringify({
          status: "error",
          error: error instanceof Error ? error.message : "Unknown error",
        }),
        {
          status: 500,
          headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
          },
        },
      );
    }
  }),
});

/**
 * Get test execution results
 * GET /test-results?executionId=xxx&limit=50&testType=unit
 */
http.route({
  path: "/test-results",
  method: "GET",
  handler: httpAction(async (ctx, request) => {
    try {
      const url = new URL(request.url);
      const executionId = url.searchParams.get("executionId");
      const limit = parseInt(url.searchParams.get("limit") || "50");
      const testType = url.searchParams.get("testType");
      const environment = url.searchParams.get("environment");

      const result = await ctx.runAction(api.actions.getTestResults, {
        executionId,
        limit,
        testType,
        environment,
      });

      return new Response(
        JSON.stringify({
          status: "success",
          data: result,
        }),
        {
          status: 200,
          headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
          },
        },
      );
    } catch (error) {
      return new Response(
        JSON.stringify({
          status: "error",
          error: error instanceof Error ? error.message : "Unknown error",
        }),
        {
          status: 500,
          headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
          },
        },
      );
    }
  }),
});

/**
 * Get API performance metrics
 * GET /api-metrics?endpoint=/optimize&limit=100&hours=24
 */
http.route({
  path: "/api-metrics",
  method: "GET",
  handler: httpAction(async (ctx, request) => {
    try {
      const url = new URL(request.url);
      const endpoint = url.searchParams.get("endpoint");
      const limit = parseInt(url.searchParams.get("limit") || "100");
      const hours = parseInt(url.searchParams.get("hours") || "24");

      const result = await ctx.runAction(api.actions.getApiMetrics, {
        endpoint,
        limit,
        hours,
      });

      return new Response(
        JSON.stringify({
          status: "success",
          data: result,
        }),
        {
          status: 200,
          headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
          },
        },
      );
    } catch (error) {
      return new Response(
        JSON.stringify({
          status: "error",
          error: error instanceof Error ? error.message : "Unknown error",
        }),
        {
          status: 500,
          headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
          },
        },
      );
    }
  }),
});

/**
 * Update test execution status
 * PUT /test-status
 */
http.route({
  path: "/test-status",
  method: "PUT",
  handler: httpAction(async (ctx, request) => {
    try {
      const body = await request.json();
      const { executionId, status, endTime, duration, results } = body;

      if (!executionId || !status) {
        return new Response(
          JSON.stringify({
            status: "error",
            error: "executionId and status are required",
          }),
          {
            status: 400,
            headers: {
              "Content-Type": "application/json",
              "Access-Control-Allow-Origin": "*",
            },
          },
        );
      }

      const result = await ctx.runAction(api.actions.updateTestStatus, {
        executionId,
        status,
        endTime,
        duration,
        results,
      });

      return new Response(
        JSON.stringify({
          status: "success",
          data: result,
        }),
        {
          status: 200,
          headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
          },
        },
      );
    } catch (error) {
      return new Response(
        JSON.stringify({
          status: "error",
          error: error instanceof Error ? error.message : "Unknown error",
        }),
        {
          status: 500,
          headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
          },
        },
      );
    }
  }),
});

/**
 * CORS preflight for new endpoints
 */
const corsEndpoints = ["/log-test", "/test-results", "/api-metrics", "/test-status"];

corsEndpoints.forEach((path) => {
  http.route({
    path,
    method: "OPTIONS",
    handler: httpAction(async (ctx, request) => {
      return new Response(null, {
        status: 200,
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, PUT, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type",
        },
      });
    }),
  });
});

export default http;
