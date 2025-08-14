/**
 * Enhanced API Call Wrapper for DriftGuard Checks
 * Provides additional logging and monitoring for rate limit handling
 * Works with Probot's built-in throttling via @octokit/plugin-throttling
 */

// Event logging helper (matches pattern from index.ts)
function logEvent(data: any) {
  const timestamp = new Date().toISOString();
  console.log(JSON.stringify({ ...data, timestamp, service: 'driftguard-checks' }));
}

/**
 * Monitor rate limit status from API responses
 * Call this after any GitHub API operation to track rate limit usage
 */
export function monitorRateLimit(response: any, context: string) {
  if (response?.headers) {
    const remaining = response.headers['x-ratelimit-remaining'];
    const limit = response.headers['x-ratelimit-limit'];
    const resetTime = response.headers['x-ratelimit-reset'];
    
    if (remaining !== undefined) {
      logEvent({
        evt: 'rate_limit_status',
        context,
        remaining: parseInt(remaining),
        limit: parseInt(limit),
        resetTime: parseInt(resetTime),
        usagePercent: Math.round(((limit - remaining) / limit) * 100)
      });

      // Warn if rate limit is getting low
      if (parseInt(remaining) < 100) {
        logEvent({
          evt: 'rate_limit_warning',
          context,
          remaining: parseInt(remaining),
          resetTime: parseInt(resetTime)
        });
      }
    }
  }
}

/**
 * Enhanced safe API call wrapper with throttling context
 */
export async function safeThrottledApiCall<T>(
  operation: () => Promise<T>,
  context: { sha: string; operationName: string; runId?: string }
): Promise<T | null> {
  const { sha, operationName, runId } = context;
  
  try {
    const startTime = Date.now();
    const result = await operation();
    const duration = Date.now() - startTime;

    logEvent({
      evt: 'api_success',
      sha,
      operationName,
      runId,
      duration
    });

    return result;
  } catch (error: any) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    
    logEvent({
      evt: 'api_error',
      sha,
      operationName,
      runId,
      error: errorMessage,
      statusCode: error.status,
      rateLimit: error.response?.headers?.['x-ratelimit-remaining']
    });

    return null;
  }
}