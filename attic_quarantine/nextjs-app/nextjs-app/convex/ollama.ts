/**
 * Ollama HTTP Client for Convex
 * Handles communication with local Ollama server running on localhost:11434
 */

interface OllamaResponse {
  model: string;
  created_at: string;
  response: string;
  done: boolean;
  context?: number[];
  total_duration?: number;
  load_duration?: number;
  prompt_eval_count?: number;
  prompt_eval_duration?: number;
  eval_count?: number;
  eval_duration?: number;
}

interface OllamaRequest {
  model: string;
  prompt: string;
  system?: string;
  temperature?: number;
  max_tokens?: number;
  stream?: boolean;
}

interface OllamaError {
  error: string;
}

export class OllamaClient {
  private baseUrl: string;
  private defaultModel: string;
  private timeout: number;

  constructor(
    baseUrl: string = "http://localhost:11434",
    defaultModel: string = "qwen3:4b",
    timeout: number = 30000, // 30 seconds default timeout
  ) {
    this.baseUrl = baseUrl;
    this.defaultModel = defaultModel;
    this.timeout = timeout;
  }

  /**
   * Generate text completion using Ollama
   */
  async generate(
    prompt: string,
    options: {
      model?: string;
      system?: string;
      temperature?: number;
      max_tokens?: number;
    } = {},
  ): Promise<OllamaResponse> {
    const requestBody: OllamaRequest = {
      model: options.model || this.defaultModel,
      prompt,
      stream: false, // We want the complete response
      ...(options.system && { system: options.system }),
      ...(options.temperature !== undefined && {
        temperature: options.temperature,
      }),
      ...(options.max_tokens && { max_tokens: options.max_tokens }),
    };

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);

      const response = await fetch(`${this.baseUrl}/api/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        let errorMessage: string;

        try {
          const errorJson: OllamaError = JSON.parse(errorText);
          errorMessage =
            errorJson.error ||
            `HTTP ${response.status}: ${response.statusText}`;
        } catch {
          errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        }

        throw new Error(`Ollama API error: ${errorMessage}`);
      }

      const result: OllamaResponse = await response.json();

      if (!result.response) {
        throw new Error("Empty response from Ollama");
      }

      return result;
    } catch (error) {
      if (error instanceof Error) {
        if (error.name === "AbortError") {
          throw new Error(`Ollama request timed out after ${this.timeout}ms`);
        }
        throw error;
      }
      throw new Error("Unknown error occurred while calling Ollama");
    }
  }

  /**
   * Check if Ollama server is available and the model is loaded
   */
  async healthCheck(): Promise<{
    available: boolean;
    model: string;
    error?: string;
  }> {
    try {
      const response = await this.generate("Hello", {
        temperature: 0.1,
        max_tokens: 10,
      });

      return {
        available: true,
        model: response.model,
      };
    } catch (error) {
      return {
        available: false,
        model: this.defaultModel,
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  }

  /**
   * Get available models from Ollama
   */
  async listModels(): Promise<{
    models: Array<{ name: string; model: string; size: number }>;
  }> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout for listing

      const response = await fetch(`${this.baseUrl}/api/tags`, {
        method: "GET",
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      throw new Error(
        `Failed to list models: ${error instanceof Error ? error.message : "Unknown error"}`,
      );
    }
  }

  /**
   * Pull a model if it doesn't exist
   */
  async pullModel(modelName: string): Promise<void> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 minute timeout for pulling

      const response = await fetch(`${this.baseUrl}/api/pull`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ name: modelName }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      // The response is a stream, but we'll just wait for completion
      await response.text();
    } catch (error) {
      throw new Error(
        `Failed to pull model ${modelName}: ${error instanceof Error ? error.message : "Unknown error"}`,
      );
    }
  }
}

// Export a default instance
export const ollamaClient = new OllamaClient();

// Export types for use in other files
export type { OllamaResponse, OllamaRequest, OllamaError };
