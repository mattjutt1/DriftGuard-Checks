/**
 * HuggingFace Space Integration for PromptEvolver
 * Connects Convex to the deployed HF Space
 */

const HF_SPACE_URL = "https://unfiltrdfreedom-prompt-evolver.hf.space";

export interface HFOptimizationResult {
  status: string;
  optimized_prompt: string;
  improvements: string[];
  quality_score: number;
  processing_time: string;
  model: string;
  error?: string;
}

/**
 * Call HuggingFace Space to optimize a prompt
 */
export async function optimizeWithHFSpace(
  prompt: string,
  taskDescription: string = "",
  mode: "quick" | "balanced" | "thorough" = "balanced",
  temperature: number = 0.7
): Promise<HFOptimizationResult> {
  try {
    // Gradio 5.0 uses /gradio_api/call endpoint
    const predictUrl = `${HF_SPACE_URL}/gradio_api/call/optimize_prompt`;

    // Step 1: Submit the request
    const submitResponse = await fetch(predictUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        data: [prompt, taskDescription, mode, temperature]
      }),
    });

    if (!submitResponse.ok) {
      throw new Error(`HF Space returned ${submitResponse.status}`);
    }

    const submitData = await submitResponse.json();
    const eventId = submitData.event_id;

    // Step 2: Get the result (Gradio 5.0 uses event streaming)
    const resultUrl = `${HF_SPACE_URL}/gradio_api/call/optimize_prompt/${eventId}`;

    // Poll for result (with timeout)
    let attempts = 0;
    const maxAttempts = 30; // 30 seconds timeout

    while (attempts < maxAttempts) {
      const resultResponse = await fetch(resultUrl);

      if (resultResponse.ok) {
        const text = await resultResponse.text();
        // Parse SSE format
        const lines = text.split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data && typeof data === 'object') {
                return data as HFOptimizationResult;
              }
            } catch (e) {
              // Continue to next line
            }
          }
        }
      }

      // Wait before next attempt
      await new Promise(resolve => setTimeout(resolve, 1000));
      attempts++;
    }

    throw new Error("Timeout waiting for HF Space response");

  } catch (error) {
    console.error("HF Space error:", error);

    // Return fallback response
    return {
      status: "error",
      optimized_prompt: prompt, // Return original prompt
      improvements: ["HF Space unavailable - using fallback"],
      quality_score: 0.5,
      processing_time: "0s",
      model: "Fallback",
      error: error instanceof Error ? error.message : "Unknown error"
    };
  }
}

/**
 * Check if HF Space is available
 */
export async function checkHFSpaceHealth(): Promise<{
  available: boolean;
  model: string;
  error?: string;
}> {
  try {
    const response = await fetch(HF_SPACE_URL, {
      method: "GET",
      signal: AbortSignal.timeout(5000), // 5 second timeout
    });

    const available = response.ok && response.status === 200;

    return {
      available,
      model: available ? "Qwen2.5-7B via HF Space" : "Unavailable",
      error: available ? undefined : `Status: ${response.status}`
    };
  } catch (error) {
    return {
      available: false,
      model: "HF Space Unavailable",
      error: error instanceof Error ? error.message : "Unknown error"
    };
  }
}
