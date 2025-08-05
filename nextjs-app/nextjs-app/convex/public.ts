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
    try {
      // Call the internal action
      const result = await ctx.runAction(api.actions.checkOllamaHealth, {});
      
      return new Response(JSON.stringify({
        status: "success",
        data: result
      }), {
        status: 200,
        headers: { "Content-Type": "application/json" }
      });
    } catch (error) {
      return new Response(JSON.stringify({
        status: "error",
        error: error instanceof Error ? error.message : "Unknown error"
      }), {
        status: 500,
        headers: { "Content-Type": "application/json" }
      });
    }
  })
});

/**
 * Public prompt optimization endpoint
 * POST /optimize
 */
http.route({
  path: "/optimize",
  method: "POST",
  handler: httpAction(async (ctx, request) => {
    try {
      const body = await request.json();
      const { prompt, domain, config } = body;
      
      if (!prompt) {
        return new Response(JSON.stringify({
          status: "error",
          error: "Prompt is required"
        }), {
          status: 400,
          headers: { "Content-Type": "application/json" }
        });
      }
      
      // Call the internal action
      const result = await ctx.runAction(api.actions.testPromptWizardOptimization, {
        prompt,
        domain: domain || "general",
        config: config || {}
      });
      
      return new Response(JSON.stringify({
        status: "success",
        data: result
      }), {
        status: 200,
        headers: { "Content-Type": "application/json" }
      });
    } catch (error) {
      return new Response(JSON.stringify({
        status: "error",
        error: error instanceof Error ? error.message : "Unknown error"
      }), {
        status: 500,
        headers: { "Content-Type": "application/json" }
      });
    }
  })
});

export default http;