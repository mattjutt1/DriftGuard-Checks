/**
 * DriftGuard Checks App - Security-Enhanced Version
 * This version implements comprehensive security measures including:
 * - Webhook signature validation
 * - Rate limiting
 * - Input validation
 * - Error sanitization
 * - Security headers
 */

import express from 'express';
import { createNodeMiddleware, createProbot, Probot } from 'probot';
import { Readable } from 'stream';
import * as unzipper from 'unzipper';
import helmet from 'helmet';
import dotenv from 'dotenv';
import winston from 'winston';
import {
  webhookSignatureMiddleware,
  rateLimiters,
  securityHeaders,
  sanitizeError,
  validateWebhookPayload,
  validateEnvConfig,
  securityAuditLogger,
  securityErrorHandler
} from './security';

// Load environment variables
dotenv.config();

// Validate environment configuration
try {
  validateEnvConfig(process.env);
} catch (error) {
  console.error('Invalid environment configuration:', error);
  process.exit(1);
}

// Configure Winston logger
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'error',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    }),
    new winston.transports.File({ 
      filename: 'error.log', 
      level: 'error' 
    }),
    new winston.transports.File({ 
      filename: 'security.log',
      level: 'warning'
    })
  ]
});

// Helper function for error messages
function errMsg(e: unknown): string {
  return e instanceof Error ? e.message : typeof e === 'string' ? e : JSON.stringify(e);
}

// Bounded Map to prevent memory leaks
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
  securityEvents: number;
  blockedRequests: number;
}

let appState: AppState = {
  startTime: new Date(),
  lastEventAt: null,
  eventCount: 0,
  checkRuns: new BoundedMap(1000),
  errors: new BoundedMap(1000),
  securityEvents: 0,
  blockedRequests: 0
};

// Structured logging helper with security context
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
  security?: boolean;
  [key: string]: any;
}) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    ...data
  };
  
  // Use appropriate log level
  if (data.security) {
    logger.warn('Security event', logEntry);
    appState.securityEvents++;
  } else if (data.error) {
    logger.error('Error event', logEntry);
  } else {
    logger.info('Event', logEntry);
  }
}

// Enhanced health endpoint data
function getHealthData() {
  const uptime = Math.floor((Date.now() - appState.startTime.getTime()) / 1000);
  const memoryUsage = process.memoryUsage();

  return {
    status: 'healthy',
    version: '1.0.0-secure',
    uptime,
    memory: {
      rss: Math.round(memoryUsage.rss / 1024 / 1024),
      heapUsed: Math.round(memoryUsage.heapUsed / 1024 / 1024),
      heapTotal: Math.round(memoryUsage.heapTotal / 1024 / 1024)
    },
    lastEventAt: appState.lastEventAt?.toISOString() || null,
    eventCount: appState.eventCount,
    checkRunCount: appState.checkRuns.size,
    security: {
      securityEvents: appState.securityEvents,
      blockedRequests: appState.blockedRequests,
      webhookValidation: process.env.ENABLE_WEBHOOK_VALIDATION !== 'false',
      rateLimiting: process.env.ENABLE_RATE_LIMITING !== 'false'
    }
  };
}

// Main handler function for SHA processing with enhanced security
async function handleSha(context: any, sha: string, runId?: string): Promise<void> {
  const { owner, repo } = context.repo();

  logEvent({ evt: 'handleSha', sha, runId, stage: 'start' });

  try {
    // Step 1: Create or update check run to in_progress
    let checkRunId = appState.checkRuns.get(sha);

    if (!checkRunId) {
      logEvent({ evt: 'createCheck', sha, stage: 'create' });
      
      const checkRunResponse = await context.octokit.checks.create({
        owner,
        repo,
        name: 'DriftGuard',
        head_sha: sha,
        status: 'in_progress',
        started_at: new Date().toISOString(),
        output: {
          title: 'Processing evaluation results',
          summary: 'Analyzing prompt evaluation artifacts...'
        }
      });

      checkRunId = checkRunResponse.data.id;
      appState.checkRuns.set(sha, checkRunId);
      
      logEvent({ evt: 'checkCreated', sha, checkRunId });
    } else {
      logEvent({ evt: 'updateCheck', sha, checkRunId, stage: 'update' });
      
      await context.octokit.checks.update({
        owner,
        repo,
        check_run_id: checkRunId,
        status: 'in_progress',
        output: {
          title: 'Processing evaluation results',
          summary: 'Analyzing prompt evaluation artifacts...'
        }
      });
    }

    // Step 2: List artifacts for the workflow run
    if (!runId) {
      throw new Error('No workflow run ID provided');
    }

    logEvent({ evt: 'listArtifacts', sha, runId });
    
    const artifactsResponse = await context.octokit.actions.listWorkflowRunArtifacts({
      owner,
      repo,
      run_id: parseInt(runId)
    });

    const evaluationArtifact = artifactsResponse.data.artifacts.find(
      (artifact: any) => artifact.name === 'evaluation-results'
    );

    if (!evaluationArtifact) {
      throw new Error('No evaluation-results artifact found');
    }

    // Step 3: Download and process the artifact
    logEvent({ evt: 'downloadArtifact', sha, artifactId: evaluationArtifact.id });
    
    const artifactData = await context.octokit.actions.downloadArtifact({
      owner,
      repo,
      artifact_id: evaluationArtifact.id,
      archive_format: 'zip'
    });

    // Process the ZIP file
    const buffer = Buffer.from(artifactData.data as any);
    const stream = Readable.from(buffer);
    
    let evaluationData: any = null;
    
    await new Promise((resolve, reject) => {
      stream
        .pipe(unzipper.Parse())
        .on('entry', async (entry: any) => {
          const fileName = entry.path;
          
          if (fileName === 'evaluation-results.json') {
            const content = await entry.buffer();
            try {
              evaluationData = JSON.parse(content.toString());
            } catch (e) {
              logEvent({ 
                evt: 'parseError', 
                sha, 
                error: errMsg(e) 
              });
            }
          } else {
            entry.autodrain();
          }
        })
        .on('finish', resolve)
        .on('error', reject);
    });

    if (!evaluationData) {
      throw new Error('Failed to extract evaluation results from artifact');
    }

    // Step 4: Analyze results and determine check status
    logEvent({ 
      evt: 'analyzeResults', 
      sha, 
      winRate: evaluationData.aggregate?.winRate 
    });

    const winRate = evaluationData.aggregate?.winRate || 0;
    const threshold = evaluationData.config?.threshold || 0.7;
    const passed = winRate >= threshold;

    const conclusion = passed ? 'success' : 'failure';
    const title = passed ? 
      `✅ Evaluation Passed (${(winRate * 100).toFixed(1)}%)` : 
      `❌ Evaluation Failed (${(winRate * 100).toFixed(1)}%)`;
    
    const summary = `
## Prompt Evaluation Results

**Win Rate:** ${(winRate * 100).toFixed(1)}%
**Threshold:** ${(threshold * 100).toFixed(1)}%
**Status:** ${passed ? 'PASSED' : 'FAILED'}

### Details
- Total Evaluations: ${evaluationData.aggregate?.totalEvaluations || 0}
- Wins: ${evaluationData.aggregate?.wins || 0}
- Losses: ${evaluationData.aggregate?.losses || 0}
- Ties: ${evaluationData.aggregate?.ties || 0}

${evaluationData.summary || ''}
`;

    // Step 5: Update check run with final status
    logEvent({ 
      evt: 'finalizeCheck', 
      sha, 
      checkRunId, 
      conclusion,
      winRate,
      threshold
    });

    await context.octokit.checks.update({
      owner,
      repo,
      check_run_id: checkRunId,
      status: 'completed',
      conclusion,
      completed_at: new Date().toISOString(),
      output: {
        title,
        summary
      }
    });

    logEvent({ 
      evt: 'handleSha', 
      sha, 
      runId, 
      stage: 'complete',
      result: conclusion
    });

  } catch (error) {
    const sanitized = sanitizeError(error);
    logEvent({ 
      evt: 'handleShaError', 
      sha, 
      runId, 
      error: sanitized.message,
      stage: 'error'
    });
    
    appState.errors.set(`${sha}-${Date.now()}`, sanitized);

    // Update check run with error status if we have a checkRunId
    const checkRunId = appState.checkRuns.get(sha);
    if (checkRunId && context.octokit) {
      try {
        await context.octokit.checks.update({
          owner,
          repo,
          check_run_id: checkRunId,
          status: 'completed',
          conclusion: 'failure',
          completed_at: new Date().toISOString(),
          output: {
            title: '❌ Evaluation Error',
            summary: `Error processing evaluation: ${sanitized.message}`
          }
        });
      } catch (updateError) {
        logEvent({ 
          evt: 'checkUpdateError', 
          sha, 
          error: errMsg(updateError) 
        });
      }
    }
    
    throw error;
  }
}

// Main app function with security enhancements
export default async function app(app: Probot) {
  logEvent({ evt: 'appStart' });
  
  // Security audit log
  securityAuditLogger.log('Application started', 'info', {
    nodeVersion: process.version,
    environment: process.env.NODE_ENV
  });

  // Register webhook handlers with validation
  app.on('workflow_run.completed', async (context) => {
    appState.lastEventAt = new Date();
    appState.eventCount++;

    const { payload } = context;
    
    // Validate webhook payload
    try {
      validateWebhookPayload(payload);
    } catch (error) {
      logEvent({
        evt: 'invalidPayload',
        security: true,
        error: errMsg(error)
      });
      appState.blockedRequests++;
      return;
    }

    logEvent({
      evt: 'workflowRun',
      action: payload.action,
      runId: payload.workflow_run?.id,
      sha: payload.workflow_run?.head_sha,
      conclusion: payload.workflow_run?.conclusion
    });

    // Only process if the workflow run completed successfully
    if (payload.workflow_run?.conclusion === 'success') {
      const sha = payload.workflow_run.head_sha;
      const runId = payload.workflow_run.id.toString();
      
      try {
        await handleSha(context, sha, runId);
      } catch (error) {
        logEvent({
          evt: 'workflowRunError',
          sha,
          runId,
          error: errMsg(error)
        });
      }
    }
  });

  // Handle check_run events for re-runs
  app.on(['check_run.created', 'check_run.rerequested'], async (context) => {
    appState.lastEventAt = new Date();
    appState.eventCount++;

    const { payload } = context;
    
    // Validate webhook payload
    try {
      validateWebhookPayload(payload);
    } catch (error) {
      logEvent({
        evt: 'invalidPayload',
        security: true,
        error: errMsg(error)
      });
      appState.blockedRequests++;
      return;
    }

    logEvent({
      evt: 'checkRun',
      action: payload.action,
      sha: payload.check_run?.head_sha,
      name: payload.check_run?.name
    });

    if (payload.check_run?.name === 'DriftGuard') {
      const sha = payload.check_run.head_sha;
      
      try {
        await handleSha(context, sha);
      } catch (error) {
        logEvent({
          evt: 'checkRunError',
          sha,
          error: errMsg(error)
        });
      }
    }
  });

  logEvent({ evt: 'appReady' });
}

// Create Express app with security middleware
const expressApp = express();

// Apply security middleware
expressApp.use(helmet());
expressApp.use(securityHeaders());

// Health check endpoint with rate limiting
expressApp.get('/health', rateLimiters.health, (req, res) => {
  const health = getHealthData();
  logEvent({ 
    evt: 'healthCheck',
    memMB: health.memory.heapUsed,
    uptime: health.uptime
  });
  res.json(health);
});

// Metrics endpoint for monitoring
expressApp.get('/metrics', rateLimiters.api, (req, res) => {
  const metrics = {
    ...getHealthData(),
    errors: Array.from(appState.errors.entries()).slice(-10),
    recentChecks: Array.from(appState.checkRuns.entries()).slice(-10)
  };
  res.json(metrics);
});

// Security audit endpoint (protected)
expressApp.get('/security/audit', rateLimiters.api, (req, res) => {
  // Simple authorization check
  const authHeader = req.headers.authorization;
  if (!authHeader || authHeader !== `Bearer ${process.env.ADMIN_TOKEN}`) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  
  res.json({
    events: securityAuditLogger.getEvents(),
    stats: {
      securityEvents: appState.securityEvents,
      blockedRequests: appState.blockedRequests
    }
  });
});

// Create Probot instance
const probot = createProbot();

// Load the app
probot.load(app);

// Create and apply Probot middleware with webhook validation
const probotMiddleware = createNodeMiddleware(app, { 
  probot,
  webhooksPath: '/api/github/webhooks'
});

// Apply webhook signature validation if enabled
if (process.env.ENABLE_WEBHOOK_VALIDATION !== 'false') {
  expressApp.use(
    '/api/github/webhooks',
    rateLimiters.webhook,
    webhookSignatureMiddleware(process.env.WEBHOOK_SECRET || ''),
    probotMiddleware
  );
} else {
  console.warn('⚠️  WARNING: Webhook signature validation is disabled!');
  expressApp.use(
    '/api/github/webhooks',
    rateLimiters.webhook,
    probotMiddleware
  );
}

// Error handling middleware
expressApp.use(securityErrorHandler);

// Start server
const port = process.env.PORT || 3000;
expressApp.listen(port, () => {
  console.log(`🔒 DriftGuard Secure Server running on port ${port}`);
  console.log(`🛡️  Security features enabled:`);
  console.log(`   - Webhook validation: ${process.env.ENABLE_WEBHOOK_VALIDATION !== 'false'}`);
  console.log(`   - Rate limiting: ${process.env.ENABLE_RATE_LIMITING !== 'false'}`);
  console.log(`   - Security headers: enabled`);
  console.log(`   - Error sanitization: enabled`);
  
  securityAuditLogger.log('Server started', 'info', {
    port,
    securityFeatures: {
      webhookValidation: process.env.ENABLE_WEBHOOK_VALIDATION !== 'false',
      rateLimiting: process.env.ENABLE_RATE_LIMITING !== 'false',
      securityHeaders: true,
      errorSanitization: true
    }
  });
});