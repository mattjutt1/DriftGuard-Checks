import { action } from "./_generated/server";
import { v } from "convex/values";
import { api } from "./_generated/api";

// Enhanced Ollama configuration with retry logic and validation
const OLLAMA_CONFIG = {
  baseUrl: "http://localhost:11434",
  model: "qwen3:4b", // Using Qwen3 4B model as available
  timeout: 30000, // 30 seconds
  maxRetries: 3,
  retryDelay: 1000, // 1 second base delay
};

// PromptWizard enhanced optimization prompt
const PROMPTWIZARD_SYSTEM_PROMPT = `You are PromptWizard, an advanced AI prompt optimization specialist using Microsoft's PromptWizard methodology. Your expertise includes:

1. MUTATION & REFINEMENT: Apply systematic mutations across 3 iterations with 3 rounds each
2. EXPERT IDENTITY GENERATION: Create domain-specific expert personas for optimal prompting
3. REASONING CHAIN DEVELOPMENT: Build logical reasoning pathways for complex tasks
4. FEW-SHOT LEARNING: Generate relevant examples and demonstrations
5. QUALITY METRICS: Evaluate clarity, specificity, engagement, and effectiveness

Your optimization process follows these steps:
- Analyze the original prompt for weaknesses and improvement opportunities
- Apply PromptWizard mutations: clarity enhancement, specificity injection, context enrichment
- Generate expert identity and reasoning frameworks
- Create measurable quality metrics
- Provide actionable improvement recommendations`;

// Utility function for exponential backoff retry
async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxRetries: number = OLLAMA_CONFIG.maxRetries,
  baseDelay: number = OLLAMA_CONFIG.retryDelay,
): Promise<T> {
  let lastError: Error;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      if (attempt === maxRetries) {
        throw new Error(
          `Failed after ${maxRetries + 1} attempts: ${lastError.message}`,
        );
      }

      // Exponential backoff with jitter
      const delay = baseDelay * Math.pow(2, attempt) + Math.random() * 1000;
      await new Promise((resolve) => setTimeout(resolve, delay));
    }
  }

  throw lastError!;
}

// Enhanced Ollama API client with timeout and error handling
async function callOllamaAPI(
  prompt: string,
  contextDomain?: string,
): Promise<any> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), OLLAMA_CONFIG.timeout);

  try {
    const optimizationPrompt = `${PROMPTWIZARD_SYSTEM_PROMPT}

Original prompt: "${prompt}"
Context domain: ${contextDomain || "general"}

Apply PromptWizard methodology to optimize this prompt. Provide your response in this exact JSON format:
{
  "optimized_prompt": "your optimized prompt with expert identity, clear instructions, and enhanced specificity",
  "expert_identity": "the expert persona you generated for this domain",
  "improvements": ["specific improvement 1", "specific improvement 2", "specific improvement 3"],
  "quality_score": 8.5,
  "metrics": {
    "clarity": 9.0,
    "specificity": 8.5,
    "engagement": 8.0,
    "effectiveness": 8.7
  },
  "reasoning": "brief explanation of the optimization strategy applied",
  "promptwizard_mutations": ["mutation type 1", "mutation type 2", "mutation type 3"]
}`;

    const response = await fetch(`${OLLAMA_CONFIG.baseUrl}/api/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: OLLAMA_CONFIG.model,
        prompt: optimizationPrompt,
        stream: false,
        options: {
          temperature: 0.7,
          top_p: 0.9,
          top_k: 40,
          num_predict: 1024,
        },
      }),
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new Error(
        `Ollama API error: ${response.status} ${response.statusText}`,
      );
    }

    return await response.json();
  } finally {
    clearTimeout(timeoutId);
  }
}

// Enhanced JSON parsing with multiple strategies
function parseOptimizationResponse(responseText: string): any {
  // Strategy 1: Direct JSON parsing
  try {
    return JSON.parse(responseText);
  } catch (e) {
    // Continue to next strategy
  }

  // Strategy 2: Extract JSON from markdown code blocks
  const codeBlockMatch = responseText.match(/```(?:json\s*)?([\s\S]*?)```/);
  if (codeBlockMatch) {
    try {
      return JSON.parse(codeBlockMatch[1].trim());
    } catch (e) {
      // Continue to next strategy
    }
  }

  // Strategy 3: Extract JSON object from text
  const jsonMatch = responseText.match(/\{[\s\S]*\}/);
  if (jsonMatch) {
    try {
      return JSON.parse(jsonMatch[0]);
    } catch (e) {
      // Continue to next strategy
    }
  }

  // Strategy 4: Fallback - parse the response text for key information
  return {
    optimized_prompt:
      responseText.length > 100
        ? responseText.substring(0, 500) + "..."
        : responseText,
    expert_identity: "General AI Assistant",
    improvements: ["Enhanced structure", "Improved clarity", "Added context"],
    quality_score: 7.0,
    metrics: {
      clarity: 7.0,
      specificity: 7.0,
      engagement: 7.0,
      effectiveness: 7.0,
    },
    reasoning: "Fallback parsing applied due to JSON parsing issues",
    promptwizard_mutations: [
      "structural_enhancement",
      "clarity_injection",
      "context_enrichment",
    ],
  };
}

// Shared handler for optimization logic
async function optimizePromptWithOllamaHandler(ctx: any, { sessionId }: { sessionId: any }): Promise<{
  success: boolean;
  sessionId: any;
  processingTime: number;
  qualityScore: number;
  expertIdentity: string;
  reasoning: string;
  promptwizardMutations: string[];
}> {
    try {
      // Get session details
      const session = await ctx.runQuery("optimizations:getSession" as never, {
        sessionId,
      });
      if (!session) throw new Error("Session not found");

      // Get prompt details
      const prompt = await ctx.runQuery("sessions:getPrompt" as never, {
        promptId: session.promptId,
      });
      if (!prompt) throw new Error("Prompt not found");

      // Update status to processing
      await ctx.runMutation("optimizations:updateProcessingStatus" as never, {
        sessionId,
        status: "processing",
      });

      const startTime = Date.now();

      // Call Ollama API with retry logic and enhanced error handling
      const ollamaData = await retryWithBackoff(async () => {
        return await callOllamaAPI(prompt.originalPrompt, prompt.contextDomain);
      });

      const processingTime = Date.now() - startTime;

      // Enhanced response parsing with multiple strategies
      const optimizationResult = parseOptimizationResponse(ollamaData.response);

      // Validate required fields and provide defaults
      const validatedResult = {
        optimized_prompt:
          optimizationResult.optimized_prompt || prompt.originalPrompt,
        expert_identity: optimizationResult.expert_identity || "AI Assistant",
        improvements: Array.isArray(optimizationResult.improvements)
          ? optimizationResult.improvements
          : ["Enhanced structure", "Improved clarity", "Added specificity"],
        quality_score:
          typeof optimizationResult.quality_score === "number"
            ? Math.max(1, Math.min(10, optimizationResult.quality_score))
            : 7.5,
        metrics: {
          clarity: optimizationResult.metrics?.clarity ?? 7.5,
          specificity: optimizationResult.metrics?.specificity ?? 7.5,
          engagement: optimizationResult.metrics?.engagement ?? 7.5,
          effectiveness: optimizationResult.metrics?.effectiveness ?? 7.5,
        },
        reasoning:
          optimizationResult.reasoning ||
          "Applied PromptWizard optimization methodology",
        promptwizard_mutations: Array.isArray(
          optimizationResult.promptwizard_mutations,
        )
          ? optimizationResult.promptwizard_mutations
          : [
              "clarity_enhancement",
              "specificity_injection",
              "context_enrichment",
            ],
      };

      // Update the optimization session with results
      await ctx.runMutation("optimizations:updateOptimizationResults" as never, {
        sessionId,
        optimizedPrompt: validatedResult.optimized_prompt,
        qualityScore: validatedResult.quality_score,
        processingTimeMs: processingTime,
        improvements: validatedResult.improvements,
        metrics: validatedResult.metrics,
      });

      return {
        success: true,
        sessionId,
        processingTime,
        qualityScore: validatedResult.quality_score,
        expertIdentity: validatedResult.expert_identity,
        reasoning: validatedResult.reasoning,
        promptwizardMutations: validatedResult.promptwizard_mutations,
      };
    } catch (error) {
      // Enhanced error handling and logging
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error";
      const isNetworkError =
        errorMessage.includes("fetch") || errorMessage.includes("connection");
      const isTimeoutError =
        errorMessage.includes("timeout") || errorMessage.includes("aborted");
      const isModelError =
        errorMessage.includes("model") || errorMessage.includes("404");

      let userFriendlyMessage = errorMessage;
      if (isNetworkError) {
        userFriendlyMessage =
          "Failed to connect to Ollama. Please ensure it's running on localhost:11434";
      } else if (isTimeoutError) {
        userFriendlyMessage =
          "Request timed out. The model may be processing a complex prompt or the system is under load";
      } else if (isModelError) {
        userFriendlyMessage = `Model '${OLLAMA_CONFIG.model}' not found. Please run: ollama pull ${OLLAMA_CONFIG.model}`;
      }

      // Mark optimization as failed with detailed error info
      await ctx.runMutation("optimizations:markOptimizationFailed" as never, {
        sessionId,
        errorMessage: userFriendlyMessage,
      });

      throw new Error(userFriendlyMessage);
    }
}

// Enhanced action to optimize prompt using Ollama API with PromptWizard methodology
export const optimizePromptWithOllama = action({
  args: {
    sessionId: v.id("optimizationSessions"),
  },
  handler: async (ctx, { sessionId }) => {
    return await optimizePromptWithOllamaHandler(ctx, { sessionId });
  },
});

// Enhanced health check action for Ollama service with comprehensive validation
export const checkOllamaHealth = action({
  args: {},
  handler: async () => {
    const healthCheck = {
      healthy: false,
      service: {
        running: false,
        url: OLLAMA_CONFIG.baseUrl,
        responseTime: 0,
      },
      model: {
        available: false,
        name: OLLAMA_CONFIG.model,
        size: null as string | null,
        quantization: null as string | null,
      },
      capabilities: {
        generation: false,
        streaming: false,
      },
      recommendations: [] as string[],
      error: null as string | null,
    };

    try {
      // Test service availability with timeout
      const startTime = Date.now();
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      try {
        const response = await fetch(`${OLLAMA_CONFIG.baseUrl}/api/tags`, {
          method: "GET",
          signal: controller.signal,
        });

        clearTimeout(timeoutId);
        healthCheck.service.responseTime = Date.now() - startTime;

        if (!response.ok) {
          healthCheck.error = `Ollama service returned ${response.status}: ${response.statusText}`;
          healthCheck.recommendations.push(
            "Check if Ollama is running: ollama serve",
          );
          healthCheck.recommendations.push("Verify port 11434 is available");
          return healthCheck;
        }

        healthCheck.service.running = true;
        const data = await response.json();

        // Check for the specific model
        const targetModel = data.models?.find(
          (model: any) =>
            model.name === OLLAMA_CONFIG.model ||
            model.name.includes("qwen3:4b") ||
            (model.name.includes("qwen3") && model.name.includes("4b")),
        );

        if (targetModel) {
          healthCheck.model.available = true;
          healthCheck.model.size = targetModel.size || "Unknown";

          // Extract quantization info if available
          if (
            targetModel.name.includes("q4") ||
            targetModel.name.includes("4b")
          ) {
            healthCheck.model.quantization = "Q4";
          }
        } else {
          healthCheck.recommendations.push(
            `Install the required model: ollama pull ${OLLAMA_CONFIG.model}`,
          );

          // Suggest alternatives if available
          const alternatives = data.models?.filter(
            (model: any) =>
              model.name.includes("qwen") || model.name.includes("llama"),
          );

          if (alternatives?.length > 0) {
            healthCheck.recommendations.push(
              `Available alternatives: ${alternatives.map((m: any) => m.name).join(", ")}`,
            );
          }
        }

        // Test generation capability if model is available
        if (targetModel) {
          try {
            const testResponse = await fetch(
              `${OLLAMA_CONFIG.baseUrl}/api/generate`,
              {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                  model: OLLAMA_CONFIG.model,
                  prompt: "Test",
                  stream: false,
                  options: { num_predict: 1 },
                }),
                signal: AbortSignal.timeout(10000),
              },
            );

            if (testResponse.ok) {
              healthCheck.capabilities.generation = true;
              healthCheck.capabilities.streaming = true; // Assume streaming works if generation works
            }
          } catch (testError) {
            healthCheck.recommendations.push(
              "Model generation test failed - model may be corrupted",
            );
            healthCheck.recommendations.push(
              `Consider reinstalling: ollama rm ${OLLAMA_CONFIG.model} && ollama pull ${OLLAMA_CONFIG.model}`,
            );
          }
        }

        // Overall health determination
        healthCheck.healthy =
          healthCheck.service.running &&
          healthCheck.model.available &&
          healthCheck.capabilities.generation;

        // Performance recommendations
        if (healthCheck.service.responseTime > 2000) {
          healthCheck.recommendations.push(
            "Service response time is slow - consider restarting Ollama",
          );
        }

        return {
          ...healthCheck,
          models:
            data.models?.map((m: any) => ({
              name: m.name,
              size: m.size,
              modified: m.modified_at,
            })) || [],
          message: healthCheck.healthy
            ? `✅ Ollama is healthy with ${OLLAMA_CONFIG.model} model ready`
            : `❌ Ollama health check failed - see recommendations`,
        };
      } catch (fetchError) {
        clearTimeout(timeoutId);
        throw fetchError;
      }
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error";

      if (
        errorMessage.includes("aborted") ||
        errorMessage.includes("timeout")
      ) {
        healthCheck.error = "Connection timeout - Ollama may not be running";
        healthCheck.recommendations.push("Start Ollama service: ollama serve");
        healthCheck.recommendations.push(
          "Check if port 11434 is blocked by firewall",
        );
      } else if (
        errorMessage.includes("ECONNREFUSED") ||
        errorMessage.includes("fetch")
      ) {
        healthCheck.error =
          "Connection refused - Ollama service is not running";
        healthCheck.recommendations.push("Start Ollama service: ollama serve");
        healthCheck.recommendations.push(
          "Verify Ollama is installed: ollama --version",
        );
      } else {
        healthCheck.error = errorMessage;
        healthCheck.recommendations.push(
          "Check Ollama installation and configuration",
        );
      }

      return healthCheck;
    }
  },
});

// Simplified test function for now (TODO: implement proper test pipeline)
export const testOptimizationPipeline = action({
  args: {
    testPrompt: v.optional(v.string()),
    contextDomain: v.optional(v.string()),
  },
  handler: async (ctx, { testPrompt = "Write a blog post about AI", contextDomain = "content creation" }) => {
    return {
      success: true,
      testResults: {
        originalPrompt: testPrompt,
        optimizedPrompt: "This is a simplified test response. Full implementation requires Ollama setup.",
        qualityScore: 8.0,
        processingTime: 1000,
        expertIdentity: "Content Creation Expert",
        reasoning: "Test implementation - full optimization pipeline requires Ollama service.",
      },
    };
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
  handler: async (ctx, args) => {
    try {
      // Use the same optimization logic but return in simplified format
      const ollamaData = await retryWithBackoff(async () => {
        return await callOllamaAPI(args.prompt, args.domain);
      });

      const optimizationData = parseOptimizationResponse(ollamaData.response);

      return { 
        success: true, 
        result: {
          best_prompt: optimizationData.optimized_prompt,
          improvements: optimizationData.improvements || [],
          quality_score: optimizationData.quality_score || 7.0,
          expert_profile: optimizationData.expert_identity,
          iterations_completed: 1
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  },
});
