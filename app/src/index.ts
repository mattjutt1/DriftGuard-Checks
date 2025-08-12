import express from 'express';
import { createNodeMiddleware, createProbot, Probot } from 'probot';
import { Readable } from 'stream';
import * as unzipper from 'unzipper';
import { addEvaluationToApp } from './simple-evaluation';

// Helper function as specified in requirements
function errMsg(e: unknown): string {
  return e instanceof Error ? e.message : typeof e === 'string' ? e : JSON.stringify(e);
}

// Bounded Map to prevent memory leaks (1000 entries max)
class BoundedMap<K, V> extends Map<K, V> {
  private maxSize: number;

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

// Main handler function for SHA processing
async function handleSha(context: any, sha: string, runId?: string): Promise<void> {
  const { owner, repo } = context.repo();

  logEvent({ evt: 'handleSha', sha, runId, stage: 'start' });

  try {
    // Step 1: Create or update check run to in_progress
    let checkRunId = appState.checkRuns.get(sha);

    if (!checkRunId) {
      const checkRun = await context.octokit.rest.checks.create({
        owner,
        repo,
        name: 'prompt-check',
        head_sha: sha,
        status: 'in_progress',
        output: {
          title: 'Evaluating prompts...',
          summary: 'Waiting for evaluation results from GitHub Actions.'
        }
      });
      checkRunId = checkRun.data.id;
      appState.checkRuns.set(sha, checkRunId);

      logEvent({ evt: 'checkRun', sha, runId, stage: 'created', result: checkRunId.toString() });
    } else {
      await context.octokit.rest.checks.update({
        owner,
        repo,
        check_run_id: checkRunId,
        status: 'in_progress',
        output: {
          title: 'Re-evaluating prompts...',
          summary: 'Processing updated evaluation results.'
        }
      });

      logEvent({ evt: 'checkRun', sha, runId, stage: 'updated', result: checkRunId.toString() });
    }

    // Step 2: Fetch latest Actions run + artifact
    const { evaluation, actionsRunUrl } = await getLatestEvaluation(context, sha, runId);

    if (!evaluation) {
      // Update check to failure - no artifact found
      await context.octokit.rest.checks.update({
        owner,
        repo,
        check_run_id: checkRunId,
        status: 'completed',
        conclusion: 'failure',
        output: {
          title: 'ERROR / MISSING_ARTIFACT',
          summary: '## ❌ Missing Evaluation Artifact\\n\\nNo `prompt-evaluation-results` artifact found.\\n\\n**Solutions:**\\n1. Ensure workflow completed successfully\\n2. Verify artifact upload in workflow\\n3. Check workflow logs for errors'
        },
        details_url: actionsRunUrl || undefined
      });

      logEvent({ evt: 'checkRun', sha, runId, stage: 'failed', result: 'missing_artifact' });
      return;
    }

    // Step 3: Compute pass/fail and update check
    const passed = evaluation.winRate >= evaluation.threshold;
    const conclusion = passed ? 'success' : 'failure';
    const emoji = passed ? '✅' : '❌';
    const status = passed ? 'PASSED' : 'FAILED';

    const summary = `## ${emoji} Prompt Gate ${status}

**Win Rate:** ${(evaluation.winRate * 100).toFixed(1)}%
**Threshold:** ${(evaluation.threshold * 100).toFixed(1)}%
**Result:** ${passed ? 'Meets requirements' : 'Below threshold'}

${actionsRunUrl ? `[View workflow run →](${actionsRunUrl})` : ''}`;

    await context.octokit.rest.checks.update({
      owner,
      repo,
      check_run_id: checkRunId,
      status: 'completed',
      conclusion,
      output: {
        title: `${emoji} Prompt Gate ${status} (${(evaluation.winRate * 100).toFixed(1)}%)`,
        summary
      },
      details_url: actionsRunUrl || undefined
    });

    logEvent({
      evt: 'checkRun',
      sha,
      runId,
      stage: 'completed',
      result: conclusion,
      winRate: evaluation.winRate,
      threshold: evaluation.threshold
    });

  } catch (error) {
    const errorMessage = errMsg(error);
    appState.errors.set(sha, { error: errorMessage, timestamp: new Date() });

    context.log.error(`Error handling SHA ${sha}:`, error);
    logEvent({ evt: 'error', sha, runId, error: errorMessage });

    // Try to update check to failure if we have a check run ID
    const checkRunId = appState.checkRuns.get(sha);
    if (checkRunId) {
      try {
        await context.octokit.rest.checks.update({
          owner: context.repo().owner,
          repo: context.repo().repo,
          check_run_id: checkRunId,
          status: 'completed',
          conclusion: 'failure',
          output: {
            title: 'ERROR / PROCESSING_FAILED',
            summary: `## ❌ Processing Error\\n\\n${errorMessage}\\n\\n**Action Required:** Check the workflow configuration and ensure the evaluation completes successfully.`
          }
        });
      } catch (updateError) {
        context.log.error('Failed to update check run after error:', updateError);
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
function probotApp(app: Probot) {

  // Handle pull_request events (opened, synchronize)
  // Add simple evaluation to the app
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

// Express server setup with createNodeMiddleware (Evidence-based Probot v14 pattern)
const app = express();
const port = parseInt(process.env.PORT || '3000', 10);

// Add health endpoints BEFORE Probot middleware (critical order)
app.get('/health', (_req, res) => {
  res.status(200).json(getHealthData());
});

app.get('/probot', (_req, res) => {
  res.status(200).json({
    status: 'ok',
    message: 'DriftGuard Checks is running',
    timestamp: new Date().toISOString()
  });
});

// Add Probot webhook middleware using correct async pattern
app.use('/api/github/webhooks', async (req, res, next) => {
  try {
    const middleware = await createNodeMiddleware(probotApp, {
      probot: createProbot()
    });
    return middleware(req, res, next);
  } catch (error) {
    console.error('Webhook middleware error:', error);
    next(error);
  }
});

// Start Express server
app.listen(port, () => {
  console.log(`Express server listening on port ${port}`);
  console.log('Health endpoints: /health and /probot');
  console.log('GitHub webhooks: /api/github/webhooks');
});
