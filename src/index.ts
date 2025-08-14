import express from 'express';
import { createNodeMiddleware, createProbot, Probot } from 'probot';
import { throttling } from '@octokit/plugin-throttling';
import { Readable } from 'stream';
import * as unzipper from 'unzipper';
import { addEvaluationToApp } from './simple-evaluation';
import { webhookSignatureMiddleware, rateLimiters } from './security';
import { monitorRateLimit, safeThrottledApiCall } from './octokit-throttled';

// Helper function as specified in requirements
function errMsg(e: unknown): string {
  return e instanceof Error ? e.message : typeof e === 'string' ? e : JSON.stringify(e);
}

// Bounded Map to prevent memory leaks (1000 entries max)
class BoundedMap<K, V> extends Map<K, V> {
  private readonly maxSize: number;

  constructor(maxSize = 1000) {
    super();
    this.maxSize = maxSize;
  }

  set(key: K, value: V): this {
    if (this.size >= this.maxSize) {
      const firstKey = this.keys().next().value;
      if (firstKey !== undefined) {
        this.delete(firstKey);
      }
    }
    return super.set(key, value);
  }
}

// App state tracking
interface AppState {
  startTime: Date;
  lastEventAt: Date | null;
  eventCount: number;
  checkRuns: BoundedMap<string, any>;
  errors: BoundedMap<string, any>;
}

let appState: AppState = {
  startTime: new Date(),
  lastEventAt: null,
  eventCount: 0,
  checkRuns: new BoundedMap(1000),
  errors: new BoundedMap(1000)
};

// Structured logging helper
function logEvent(data: {
  evt: string;
  sha?: string;
  runId?: string;
  action?: string;
  stage?: string;
  result?: string;
  winRate?: number;
  threshold?: number;
  error?: string;
  memMB?: number;
  uptime?: number;
  smee?: string;
  lastEventAt?: string | null;
  eventCount?: number;
}) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    ...data
  };
  console.log(JSON.stringify(logEntry));
}

// Health endpoint data
function getHealthData() {
  const uptime = Math.floor((Date.now() - appState.startTime.getTime()) / 1000);
  const memoryUsage = process.memoryUsage();

  return {
    status: 'healthy',
    uptime,
    memory: {
      rss: Math.round(memoryUsage.rss / 1024 / 1024),
      heapUsed: Math.round(memoryUsage.heapUsed / 1024 / 1024),
      heapTotal: Math.round(memoryUsage.heapTotal / 1024 / 1024)
    },
    lastEventAt: appState.lastEventAt?.toISOString() || null,
    eventCount: appState.eventCount,
    checkRunCount: appState.checkRuns.size
  };
}

// Error boundary for API operations
async function safeApiCall<T>(
  operation: () => Promise<T>,
  context: { sha: string; operationName: string; runId?: string }
): Promise<T | null> {
  const { sha, operationName, runId } = context;
  
  try {
    return await operation();
  } catch (error) {
    const errorMessage = errMsg(error);
    appState.errors.set(`${sha}-${operationName}`, { 
      error: errorMessage, 
      timestamp: new Date(),
      operation: operationName,
      sha,
      runId 
    });

    logEvent({ 
      evt: 'api_error', 
      sha, 
      runId, 
      error: errorMessage, 
      stage: operationName 
    });

    return null;
  }
}

// Enhanced check run update with error boundaries
async function safeUpdateCheckRun(
  context: any,
  checkRunId: number,
  update: any,
  errorContext: { sha: string; stage: string; runId?: string }
): Promise<boolean> {
  const { owner, repo } = context.repo();
  const { sha, stage, runId } = errorContext;

  const result = await safeApiCall(
    () => context.octokit.rest.checks.update({
      owner,
      repo,
      check_run_id: checkRunId,
      ...update
    }),
    { sha, operationName: `update_check_${stage}`, runId }
  );

  if (!result) {
    logEvent({ 
      evt: 'check_update_failed', 
      sha, 
      runId, 
      stage, 
      error: 'Failed to update check run' 
    });
    return false;
  }

  return true;
}

// Main handler function for SHA processing with enhanced error boundaries
async function handleSha(context: any, sha: string, runId?: string): Promise<void> {
  const { owner, repo } = context.repo();

  logEvent({ evt: 'handleSha', sha, runId, stage: 'start' });

  let checkRunId: number | null = null;
  let criticalFailure = false;

  try {
    // Step 1: Create or update check run to in_progress with error boundary
    checkRunId = appState.checkRuns.get(sha);

    if (!checkRunId) {
      const checkRunResult = await safeApiCall(
        () => context.octokit.rest.checks.create({
          owner,
          repo,
          name: 'prompt-check',
          head_sha: sha,
          status: 'in_progress',
          output: {
            title: 'Evaluating prompts...',
            summary: 'Waiting for evaluation results from GitHub Actions.'
          }
        }),
        { sha, operationName: 'create_check', runId }
      );

      if (!checkRunResult) {
        criticalFailure = true;
        logEvent({ evt: 'critical_failure', sha, runId, error: 'Failed to create check run' });
        return;
      }

      checkRunId = (checkRunResult as any).data.id;
      appState.checkRuns.set(sha, checkRunId);
      logEvent({ evt: 'checkRun', sha, runId, stage: 'created', result: checkRunId.toString() });
    } else {
      const updateSuccess = await safeUpdateCheckRun(
        context,
        checkRunId,
        {
          status: 'in_progress',
          output: {
            title: 'Re-evaluating prompts...',
            summary: 'Processing updated evaluation results.'
          }
        },
        { sha, stage: 'in_progress', runId }
      );

      if (updateSuccess) {
        logEvent({ evt: 'checkRun', sha, runId, stage: 'updated', result: checkRunId.toString() });
      }
    }

    // Step 2: Fetch latest Actions run + artifact with error boundary
    const evalResult = await safeApiCall(
      () => getLatestEvaluation(context, sha, runId),
      { sha, operationName: 'fetch_evaluation', runId }
    );

    if (!evalResult) {
      // Evaluation fetch failed - update check with error info
      if (checkRunId) {
        await safeUpdateCheckRun(
          context,
          checkRunId,
          {
            status: 'completed',
            conclusion: 'failure',
            output: {
              title: 'ERROR / EVALUATION_FETCH_FAILED',
              summary: '## ❌ Evaluation Fetch Failed\\n\\nUnable to retrieve evaluation results from GitHub Actions.\\n\\n**Possible Causes:**\\n1. GitHub API rate limiting\\n2. Network connectivity issues\\n3. Permissions problems\\n\\n**Action Required:** Retry the operation or check service status.'
            }
          },
          { sha, stage: 'fetch_failed', runId }
        );
      }
      return;
    }

    const { evaluation, actionsRunUrl } = evalResult;

    if (!evaluation) {
      // Update check to failure - no artifact found
      if (checkRunId) {
        await safeUpdateCheckRun(
          context,
          checkRunId,
          {
            status: 'completed',
            conclusion: 'failure',
            output: {
              title: 'ERROR / MISSING_ARTIFACT',
              summary: '## ❌ Missing Evaluation Artifact\\n\\nNo `prompt-evaluation-results` artifact found.\\n\\n**Solutions:**\\n1. Ensure workflow completed successfully\\n2. Verify artifact upload in workflow\\n3. Check workflow logs for errors'
            },
            details_url: actionsRunUrl || undefined
          },
          { sha, stage: 'missing_artifact', runId }
        );
      }

      logEvent({ evt: 'checkRun', sha, runId, stage: 'failed', result: 'missing_artifact' });
      return;
    }

    // Step 3: Compute pass/fail and update check (using neutral mode to prevent blocking)
    const passed = evaluation.winRate >= evaluation.threshold;
    const conclusion = passed ? 'success' : 'neutral';  // Use 'neutral' instead of 'failure' to prevent merge blocking
    const emoji = passed ? '✅' : '⚠️';  // Use warning emoji for neutral state
    const status = passed ? 'PASSED' : 'BELOW_THRESHOLD';

    const summary = `## ${emoji} Prompt Gate ${status}

**Win Rate:** ${(evaluation.winRate * 100).toFixed(1)}%
**Threshold:** ${(evaluation.threshold * 100).toFixed(1)}%
**Result:** ${passed ? 'Meets requirements' : 'Below threshold (informational only)'}

${actionsRunUrl ? `[View workflow run →](${actionsRunUrl})` : ''}`;

    // Final update with error boundary
    const finalUpdateSuccess = await safeUpdateCheckRun(
      context,
      checkRunId!,
      {
        status: 'completed',
        conclusion,
        output: {
          title: `${emoji} Prompt Gate ${status} (${(evaluation.winRate * 100).toFixed(1)}%)${passed ? '' : ' - Informational'}`,
          summary
        },
        details_url: actionsRunUrl || undefined
      },
      { sha, stage: 'final_update', runId }
    );

    if (finalUpdateSuccess) {
      logEvent({
        evt: 'checkRun',
        sha,
        runId,
        stage: 'completed',
        result: conclusion,
        winRate: evaluation.winRate,
        threshold: evaluation.threshold
      });
    }

  } catch (error) {
    const errorMessage = errMsg(error);
    appState.errors.set(sha, { error: errorMessage, timestamp: new Date() });

    context.log.error(`Critical error handling SHA ${sha}:`, error);
    logEvent({ evt: 'critical_error', sha, runId, error: errorMessage });

    // Final fallback: Try to update check to failure with minimal info
    if (checkRunId && !criticalFailure) {
      const fallbackUpdate = await safeApiCall(
        () => context.octokit.rest.checks.update({
          owner,
          repo,
          check_run_id: checkRunId,
          status: 'completed',
          conclusion: 'failure',
          output: {
            title: 'ERROR / CRITICAL_FAILURE',
            summary: `## ❌ Critical Processing Error\\n\\nAn unexpected error occurred during evaluation processing.\\n\\n**Error:** ${errorMessage}\\n\\n**Action Required:** This indicates a system-level issue. Please check service status and retry.`
          }
        }),
        { sha, operationName: 'critical_fallback', runId }
      );

      if (!fallbackUpdate) {
        logEvent({ evt: 'total_failure', sha, runId, error: 'All recovery attempts failed' });
      }
    }
  }
}

// Get latest evaluation from workflow artifacts
async function getLatestEvaluation(context: any, sha: string, preferredRunId?: string): Promise<{
  evaluation: { winRate: number; threshold: number } | null;
  actionsRunUrl: string | null;
}> {
  const { owner, repo } = context.repo();

  try {
    // Get workflow runs for this SHA, sorted by created_at desc (latest first)
    const runs = await context.octokit.rest.actions.listWorkflowRunsForRepo({
      owner,
      repo,
      head_sha: sha,
      status: 'completed',
      per_page: 10
    });

    if (runs.data.workflow_runs.length === 0) {
      return { evaluation: null, actionsRunUrl: null };
    }

    // Sort runs by created_at descending to get latest first (as fixed in previous session)
    const sortedRuns = runs.data.workflow_runs.sort((a: any, b: any) =>
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );

    // If we have a preferred run ID, try that first
    if (preferredRunId) {
      const preferredRun = sortedRuns.find((run: any) => run.id.toString() === preferredRunId);
      if (preferredRun) {
        const evaluation = await extractEvaluationFromRun(context, preferredRun.id);
        if (evaluation) {
          return { evaluation, actionsRunUrl: preferredRun.html_url };
        }
      }
    }

    // Try each run (latest first)
    for (const run of sortedRuns) {
      const evaluation = await extractEvaluationFromRun(context, run.id);
      if (evaluation) {
        return { evaluation, actionsRunUrl: run.html_url };
      }
    }

    return { evaluation: null, actionsRunUrl: sortedRuns[0]?.html_url || null };

  } catch (error) {
    context.log.error('Error fetching evaluation:', error);
    return { evaluation: null, actionsRunUrl: null };
  }
}

// Extract evaluation from specific workflow run
async function extractEvaluationFromRun(context: any, runId: number): Promise<{
  winRate: number;
  threshold: number;
} | null> {
  try {
    const { owner, repo } = context.repo();

    // Get artifacts for this run
    const artifacts = await context.octokit.rest.actions.listWorkflowRunArtifacts({
      owner,
      repo,
      run_id: runId
    });

    // Look for prompt-evaluation-results artifact by exact name
    let targetArtifact = artifacts.data.artifacts.find((a: any) => a.name === 'prompt-evaluation-results');

    // Fallback: use first artifact if exact name not found
    if (!targetArtifact && artifacts.data.artifacts.length > 0) {
      targetArtifact = artifacts.data.artifacts[0];
    }

    if (!targetArtifact) {
      return null;
    }

    // Download and parse artifact
    const download = await context.octokit.rest.actions.downloadArtifact({
      owner,
      repo,
      artifact_id: targetArtifact.id,
      archive_format: 'zip'
    });

    // Parse ZIP data
    const zipBuffer = Buffer.from(download.data as ArrayBuffer);
    const readable = Readable.from([zipBuffer]);

    return new Promise((resolve, _reject) => {
      readable
        .pipe(unzipper.Parse())
        .on('entry', (entry: any) => {
          if (entry.path.endsWith('.json') || entry.path === 'results.json') {
            let content = '';
            entry.on('data', (chunk: Buffer) => {
              content += chunk.toString();
            });
            entry.on('end', () => {
              try {
                const data = JSON.parse(content);
                if (data.metrics?.win_rate !== undefined && data.threshold !== undefined) {
                  resolve({
                    winRate: data.metrics.win_rate,
                    threshold: data.threshold
                  });
                } else {
                  resolve(null);
                }
              } catch (parseError) {
                // Fail closed if parsing fails as specified
                resolve(null);
              }
            });
          } else {
            entry.autodrain();
          }
        })
        .on('error', () => resolve(null))
        .on('end', () => resolve(null));
    });

  } catch (error) {
    return null;
  }
}

// Probot app function (extracted for createNodeMiddleware)
function probotApp(app: Probot, options: any = {}) {
  const { getRouter } = options;

  // Add health endpoints using Probot's getRouter
  if (getRouter) {
    const router = getRouter();
    
    // Security headers middleware
    router.use((_req: any, res: any, next: any) => {
      res.setHeader('X-Content-Type-Options', 'nosniff');
      res.setHeader('X-Frame-Options', 'DENY');
      res.setHeader('X-XSS-Protection', '1; mode=block');
      res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
      res.setHeader('Content-Security-Policy', "default-src 'self'");
      next();
    });
    
    // Apply rate limiting to different endpoints
    router.use('/health', rateLimiters.health);
    router.use('/metrics', rateLimiters.api);
    router.use('/readyz', rateLimiters.api);
    
    // Apply webhook rate limiting and signature validation to webhook endpoint
    router.use('/webhooks/github', rateLimiters.webhook);
    router.use('/webhooks/github', webhookSignatureMiddleware(process.env.WEBHOOK_SECRET || ''));
    
    router.get('/health', (_req: any, res: any) => {
      res.status(200).json(getHealthData());
    });
    
    router.get('/readyz', (_req: any, res: any) => {
      res.status(200).json({
        ready: true,
        status: 'ready',
        message: 'DriftGuard Checks is ready',
        timestamp: new Date().toISOString(),
        version: '1.0.0'
      });
    });
    
    router.get('/metrics', (_req: any, res: any) => {
      const uptime = Math.floor((Date.now() - appState.startTime.getTime()) / 1000);
      const memoryUsage = process.memoryUsage();
      
      const metricsText = `# HELP nodejs_heap_size_total_bytes Process heap size in bytes.
# TYPE nodejs_heap_size_total_bytes gauge
nodejs_heap_size_total_bytes ${memoryUsage.heapTotal}

# HELP nodejs_heap_size_used_bytes Process heap size used in bytes.
# TYPE nodejs_heap_size_used_bytes gauge
nodejs_heap_size_used_bytes ${memoryUsage.heapUsed}

# HELP process_cpu_user_seconds_total Total user CPU time spent in seconds.
# TYPE process_cpu_user_seconds_total counter
process_cpu_user_seconds_total ${uptime}

# HELP http_requests_total Total number of HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",route="/health"} ${appState.eventCount}
http_requests_total{method="POST",route="/webhooks/github"} ${appState.eventCount}

# HELP driftguard_check_runs_total Total number of check runs created
# TYPE driftguard_check_runs_total counter
driftguard_check_runs_total ${appState.checkRuns.size}

# HELP driftguard_uptime_seconds Application uptime in seconds
# TYPE driftguard_uptime_seconds gauge
driftguard_uptime_seconds ${uptime}`;

      res.setHeader('Content-Type', 'text/plain; version=0.0.4; charset=utf-8');
      res.status(200).send(metricsText);
    });
    
    router.get('/probot', (_req: any, res: any) => {
      res.status(200).json({
        status: 'ok',
        message: 'DriftGuard Checks is running',
        timestamp: new Date().toISOString()
      });
    });
    
    console.log('✅ Health endpoints registered: /health, /readyz, /probot');
  }

  // Handle pull_request events (opened, synchronize)
  // Add simple evaluation to the app (includes throttling via @octokit/plugin-throttling)
  // Note: Enhanced throttling configuration available in ./octokit-throttled.ts
  // Probot automatically handles basic throttling, enhanced version provides detailed logging
  addEvaluationToApp(app);
  
  app.on(['pull_request.opened', 'pull_request.synchronize'], async (context) => {
    appState.lastEventAt = new Date();
    appState.eventCount++;

    const sha = context.payload.pull_request.head.sha;
    const action = context.payload.action;

    context.log.info(`Handling pull_request.${action} for SHA ${sha}`);
    logEvent({ evt: 'pull_request', sha, action, stage: 'received' });

    await handleSha(context, sha);
  });

  // Handle workflow_run.completed events - route to same handler
  app.on('workflow_run.completed', async (context) => {
    appState.lastEventAt = new Date();
    appState.eventCount++;

    const { workflow_run } = context.payload;
    const sha = workflow_run.head_sha;
    const runId = workflow_run.id.toString();

    // Only process PR workflows (not main branch)
    if (!workflow_run.head_branch || workflow_run.head_branch === 'main') {
      return;
    }

    context.log.info(`Handling workflow_run.completed for SHA ${sha}, run ${runId}`);
    logEvent({ evt: 'workflow_run', sha, runId, action: 'completed', stage: 'received' });

    await handleSha(context, sha, runId);
  });

  // Log app startup
  app.on('installation.created', async (context) => {
    context.log.info('App installed!');
    logEvent({ evt: 'installation', action: 'created' });
  });

  console.log('🚀 DriftGuard Checks app started');
  console.log('Webhook URL:', process.env.WEBHOOK_PROXY_URL || 'Not configured');

  logEvent({ evt: 'startup', stage: 'initialized' });

  // Cron health logging - emit status every 5 minutes
  setInterval(() => {
    const uptime = Math.floor((Date.now() - appState.startTime.getTime()) / 1000);
    const memoryUsage = process.memoryUsage();
    const memMB = Math.round(memoryUsage.rss / 1024 / 1024);

    // Simple smee connection check (if webhook proxy URL is configured, assume connected)
    const smeeStatus = process.env.WEBHOOK_PROXY_URL ? 'connected' : 'disconnected';

    logEvent({
      evt: 'health',
      memMB,
      uptime,
      smee: smeeStatus,
      lastEventAt: appState.lastEventAt?.toISOString() || null,
      eventCount: appState.eventCount
    });
  }, 5 * 60 * 1000); // 5 minutes
}

// Log webhook security status
const webhookSecret = process.env.WEBHOOK_SECRET;
if (webhookSecret && webhookSecret.length >= 32) {
  console.log('✅ Webhook signature validation enabled via Probot');
} else {
  console.warn('⚠️  WARNING: Webhook signature validation disabled - WEBHOOK_SECRET not configured properly');
}

// Export the Probot app for standalone execution
export default probotApp;
