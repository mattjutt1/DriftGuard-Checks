/**
 * Hugging Face Spaces Integration for PromptEvolver
 * Connects to Qwen3-30B-A3B model running on HF Spaces with ZeroGPU
 */

export interface HFSpaceConfig {
  spaceUrl: string;
  timeout?: number;
  retryAttempts?: number;
}

export interface OptimizationRequest {
  prompt: string;
  taskDescription?: string;
  mode?: "quick" | "balanced" | "thorough";
  temperature?: number;
}

export interface OptimizationResponse {
  optimized_prompt: string;
  improvements: string[];
  reasoning: string;
  expert_profile: string;
  quality_score: number;
  processing_time: string;
  model: string;
  mode: string;
  temperature: number;
}

class HFSpaceClient {
  private config: HFSpaceConfig;

  constructor(config: HFSpaceConfig) {
    this.config = {
      timeout: 30000, // 30 seconds default
      retryAttempts: 3,
      ...config,
    };
  }

  /**
   * Check if HF Space is available
   */
  async checkAvailability(): Promise<{
    available: boolean;
    error?: string;
  }> {
    try {
      const response = await fetch(this.config.spaceUrl, {
        method: "GET",
        signal: AbortSignal.timeout(5000), // 5 second timeout for health check
      });

      return {
        available: response.ok,
        error: response.ok ? undefined : `Status: ${response.status}`,
      };
    } catch (error) {
      return {
        available: false,
        error: error instanceof Error ? error.message : "Connection failed",
      };
    }
  }

  /**
   * Optimize a single prompt using HF Space
   */
  async optimizePrompt(request: OptimizationRequest): Promise<OptimizationResponse> {
    const apiUrl = `${this.config.spaceUrl}/api/optimize`;

    // Prepare the request in Gradio format
    const gradioRequest = {
      data: [
        request.prompt,
        request.taskDescription || "",
        request.mode || "balanced",
        request.temperature || 0.7,
      ],
    };

    let lastError: Error | null = null;

    // Retry logic with exponential backoff
    for (let attempt = 1; attempt <= this.config.retryAttempts!; attempt++) {
      try {
        const response = await fetch(apiUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(gradioRequest),
          signal: AbortSignal.timeout(this.config.timeout!),
        });

        if (!response.ok) {
          throw new Error(`HF Space returned status ${response.status}`);
        }

        const result = await response.json();

        // Gradio returns data in a wrapper
        if (result.data && Array.isArray(result.data) && result.data.length > 0) {
          return result.data[0] as OptimizationResponse;
        } else {
          throw new Error("Invalid response format from HF Space");
        }
      } catch (error) {
        lastError = error as Error;

        // If not the last attempt, wait before retrying
        if (attempt < this.config.retryAttempts!) {
          const delay = Math.pow(2, attempt) * 1000; // Exponential backoff
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }

    throw lastError || new Error("Failed to optimize prompt");
  }

  /**
   * Process multiple prompts in batch
   */
  async processBatch(
    prompts: string[],
    taskDescription?: string,
    mode?: "quick" | "balanced" | "thorough"
  ): Promise<OptimizationResponse[]> {
    const apiUrl = `${this.config.spaceUrl}/api/batch`;

    // Join prompts with separator for batch processing
    const batchText = prompts.join("\n---\n");

    const gradioRequest = {
      data: [
        batchText,
        taskDescription || "",
        mode || "balanced",
      ],
    };

    const response = await fetch(apiUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(gradioRequest),
      signal: AbortSignal.timeout(this.config.timeout! * prompts.length), // Longer timeout for batch
    });

    if (!response.ok) {
      throw new Error(`Batch processing failed with status ${response.status}`);
    }

    const result = await response.json();

    if (result.data && Array.isArray(result.data) && result.data.length > 0) {
      return result.data[0] as OptimizationResponse[];
    } else {
      throw new Error("Invalid batch response format");
    }
  }
}

// Export singleton instance
export const hfSpaceClient = new HFSpaceClient({
  spaceUrl: process.env.HF_SPACE_URL || "https://mattjutt1-promptevolver.hf.space",
});

// Export for type usage
export type { HFSpaceClient };
