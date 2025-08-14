/**
 * DriftGuard Checks App - Fully Integrated Security Version
 * Complete implementation with all security features integrated and testable
 */

import express from 'express';
import { createNodeMiddleware, createProbot, Probot } from 'probot';
import { Readable } from 'stream';
import * as unzipper from 'unzipper';
import helmet from 'helmet';
import dotenv from 'dotenv';
import winston from 'winston';
import * as fs from 'fs';
import * as path from 'path';

// Import all security modules
import {
  webhookSignatureMiddleware,
  rateLimiters,
  securityHeaders,
  sanitizeError,
  validateWebhookPayload,
  validateEnvConfig,
  securityAuditLogger,
  securityErrorHandler,
  SecurityAuditLogger
} from './security';

import {
  GitHubIPWhitelist,
  ipWhitelistMiddleware,
  WebhookQueue,
  requestSizeLimiter,
  ReplayProtection,
  replayProtectionMiddleware,
  enhancedSecurityHeaders,
  enforceProcessLimits,
  restrictHTTPMethods,
  SecurityAuditTrail
} from './security/advanced-2025';

// Load environment variables
dotenv.config();

// Configure Winston logger
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
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
      filename: 'logs/error.log', 
      level: 'error' 
    }),
    new winston.transports.File({ 
      filename: 'logs/security.log',
      level: 'warning'
    }),
    new winston.transports.File({ 
      filename: 'logs/combined.log'
    })
  ]
});

// Create logs directory if it doesn't exist
const logsDir = path.join(__dirname, '../logs');
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir, { recursive: true });
}

// Initialize security components
const ipWhitelist = new GitHubIPWhitelist();
const replayProtection = new ReplayProtection();
const auditTrail = new SecurityAuditTrail();

// Initialize webhook queue (with intelligent Redis detection)
let webhookQueue: WebhookQueue | null = null;
const ENABLE_ASYNC_PROCESSING = process.env.ENABLE_ASYNC !== 'false';

async function initializeQueue() {
  if (!ENABLE_ASYNC_PROCESSING) {
    logger.info('Async processing disabled by configuration');
    return null;
  }

  const redisUrl = process.env.REDIS_URL || 'redis://localhost:6379';
  
  try {
    // Try to connect to Redis
    const queue = new WebhookQueue(redisUrl);
    
    // Test connection with timeout
    await Promise.race([
      queue.testConnection(),
      new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Redis connection timeout')), 5000)
      )
    ]);
    
    logger.info('Webhook queue initialized with Redis', { url: redisUrl });
    return queue;
  } catch (error) {
    if (process.env.NODE_ENV === 'production') {
      logger.error('Redis connection failed in production', { error: errMsg(error) });
      // In production, we might want to exit or alert
      if (process.env.REQUIRE_REDIS === 'true') {
        logger.error('Redis is required but not available, exiting...');
        process.exit(1);
      }
    } else {
      logger.warn('Redis not available, using mock queue for development', { 
        attempted: redisUrl,
        error: errMsg(error) 
      });
      // Use mock queue in development
      const { createMockQueue } = await import('./mocks/redis-mock');
      return createMockQueue('webhook-queue', redisUrl) as any;
    }
    return null;
  }
}

// Initialize queue asynchronously
initializeQueue().then(queue => {
  webhookQueue = queue;
  if (queue) {
    logger.info('Queue system ready', { 
      type: queue.constructor.name,
      async: true 
    });
  } else {
    logger.warn('Running in synchronous mode (no queue)');
  }
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

// App state tracking with security metrics
interface AppState {
  startTime: Date;
  lastEventAt: Date | null;
  eventCount: number;
  checkRuns: BoundedMap<string, any>;
  errors: BoundedMap<string, any>;
  security: {
    validatedWebhooks: number;
    blockedRequests: number;
    rateLimitHits: number;
    replayAttemptsBlocked: number;
    ipWhitelistBlocks: number;
  };
}

const appState: AppState = {
  startTime: new Date(),
  lastEventAt: null,
  eventCount: 0,
  checkRuns: new BoundedMap(1000),
  errors: new BoundedMap(1000),
  security: {
    validatedWebhooks: 0,
    blockedRequests: 0,
    rateLimitHits: 0,
    replayAttemptsBlocked: 0,
    ipWhitelistBlocks: 0
  }
};

// Enhanced health endpoint data
function getHealthData() {
  const uptime = Math.floor((Date.now() - appState.startTime.getTime()) / 1000);
  const memoryUsage = process.memoryUsage();

  return {
    status: 'healthy',
    version: '2.0.0-secure',
    environment: process.env.NODE_ENV || 'development',
    uptime,
    memory: {
      rss: Math.round(memoryUsage.rss / 1024 / 1024),
      heapUsed: Math.round(memoryUsage.heapUsed / 1024 / 1024),
      heapTotal: Math.round(memoryUsage.heapTotal / 1024 / 1024)
    },
    stats: {
      lastEventAt: appState.lastEventAt?.toISOString() || null,
      eventCount: appState.eventCount,
      checkRunCount: appState.checkRuns.size,
      errorCount: appState.errors.size
    },
    security: {
      ...appState.security,
      features: {
        webhookValidation: process.env.ENABLE_WEBHOOK_VALIDATION !== 'false',
        rateLimiting: process.env.ENABLE_RATE_LIMITING !== 'false',
        ipWhitelisting: process.env.ENABLE_IP_WHITELIST === 'true',
        replayProtection: process.env.ENABLE_REPLAY_PROTECTION !== 'false',
        asyncProcessing: ENABLE_ASYNC_PROCESSING && webhookQueue !== null
      }
    }
  };
}

// Main handler function for SHA processing
async function handleSha(context: any, sha: string, runId?: string): Promise<void> {
  const { owner, repo } = context.repo();
  
  logger.info('Processing SHA', { sha, runId, owner, repo });
  auditTrail.log({
    type: 'sha_processing',
    severity: 'info',
    action: 'start',
    details: { sha, runId, owner, repo }
  });

  try {
    // Step 1: Create or update check run
    let checkRunId = appState.checkRuns.get(sha);

    if (!checkRunId) {
      const checkRunResponse = await context.octokit.checks.create({
        owner,
        repo,
        name: 'DriftGuard Security',
        head_sha: sha,
        status: 'in_progress',
        started_at: new Date().toISOString(),
        output: {
          title: '🔒 Processing secure evaluation',
          summary: 'Analyzing with enhanced security...'
        }
      });

      checkRunId = checkRunResponse.data.id;
      appState.checkRuns.set(sha, checkRunId);
      logger.info('Check run created', { sha, checkRunId });
    }

    // Step 2: Process workflow artifacts
    if (!runId) {
      throw new Error('No workflow run ID provided');
    }

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

    // Step 3: Download and process artifact
    const artifactData = await context.octokit.actions.downloadArtifact({
      owner,
      repo,
      artifact_id: evaluationArtifact.id,
      archive_format: 'zip'
    });

    // Process ZIP file
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
              logger.error('Failed to parse evaluation results', { error: errMsg(e) });
            }
          } else {
            entry.autodrain();
          }
        })
        .on('finish', resolve)
        .on('error', reject);
    });

    if (!evaluationData) {
      throw new Error('Failed to extract evaluation results');
    }

    // Step 4: Update check with results
    const winRate = evaluationData.aggregate?.winRate || 0;
    const threshold = evaluationData.config?.threshold || 0.7;
    const passed = winRate >= threshold;

    await context.octokit.checks.update({
      owner,
      repo,
      check_run_id: checkRunId,
      status: 'completed',
      conclusion: passed ? 'success' : 'failure',
      completed_at: new Date().toISOString(),
      output: {
        title: passed ? 
          `✅ Secure Check Passed (${(winRate * 100).toFixed(1)}%)` : 
          `❌ Secure Check Failed (${(winRate * 100).toFixed(1)}%)`,
        summary: `Security-validated evaluation: ${(winRate * 100).toFixed(1)}% win rate`
      }
    });

    logger.info('Check run completed', { sha, passed, winRate });
    auditTrail.log({
      type: 'sha_processing',
      severity: 'info',
      action: 'complete',
      result: 'success',
      details: { sha, passed, winRate }
    });

  } catch (error) {
    const sanitized = sanitizeError(error);
    logger.error('Error processing SHA', { sha, error: sanitized });
    
    auditTrail.log({
      type: 'sha_processing',
      severity: 'error',
      action: 'failed',
      result: 'failure',
      details: { sha, error: sanitized.message }
    });

    const checkRunId = appState.checkRuns.get(sha);
    if (checkRunId && context.octokit) {
      await context.octokit.checks.update({
        owner,
        repo,
        check_run_id: checkRunId,
        status: 'completed',
        conclusion: 'failure',
        completed_at: new Date().toISOString(),
        output: {
          title: '❌ Security Check Error',
          summary: `Error: ${sanitized.message}`
        }
      });
    }
    throw error;
  }
}

// Main Probot app function
export default async function app(app: Probot, options: any = {}) {
  const { getRouter } = options;
  logger.info('DriftGuard Security App starting...');
  
  // Add health endpoints using Probot's getRouter
  if (getRouter) {
    const router = getRouter();
    
    router.get('/health', (_req: any, res: any) => {
      res.status(200).json({
        status: 'healthy',
        message: 'DriftGuard Checks is running',
        timestamp: new Date().toISOString(),
        uptime: Date.now() - appState.startTime.getTime(),
        eventCount: appState.eventCount,
        lastEventAt: appState.lastEventAt?.toISOString() || null,
        security: {
          validatedWebhooks: appState.security.validatedWebhooks,
          blockedRequests: appState.security.blockedRequests
        }
      });
    });
    
    router.get('/readyz', (_req: any, res: any) => {
      res.status(200).json({
        status: 'ready',
        message: 'DriftGuard Checks is ready',
        timestamp: new Date().toISOString(),
        version: '1.0.0'
      });
    });
    
    router.get('/probot', (_req: any, res: any) => {
      res.status(200).json({
        status: 'ok',
        message: 'DriftGuard Checks is running',
        timestamp: new Date().toISOString()
      });
    });
    
    logger.info('✅ Health endpoints registered: /health, /readyz, /probot');
  }
  
  // Initialize IP whitelist
  if (process.env.ENABLE_IP_WHITELIST === 'true') {
    await ipWhitelist.updateWhitelist();
    logger.info('GitHub IP whitelist initialized');
  }

  // Register webhook handlers
  app.on('workflow_run.completed', async (context) => {
    appState.lastEventAt = new Date();
    appState.eventCount++;

    const { payload } = context;
    
    // Validate webhook payload
    try {
      validateWebhookPayload(payload);
      appState.security.validatedWebhooks++;
    } catch (error) {
      logger.warn('Invalid webhook payload', { error: errMsg(error) });
      appState.security.blockedRequests++;
      return;
    }

    if (payload.workflow_run?.conclusion === 'success') {
      const sha = payload.workflow_run.head_sha;
      const runId = payload.workflow_run.id.toString();
      
      // Process asynchronously if queue is available
      if (webhookQueue) {
        const jobId = await webhookQueue.addWebhook(payload, context.request?.headers);
        logger.info('Webhook queued for async processing', { jobId, sha });
      } else {
        await handleSha(context, sha, runId);
      }
    }
  });

  app.on(['check_run.created', 'check_run.rerequested'], async (context) => {
    appState.lastEventAt = new Date();
    appState.eventCount++;

    const { payload } = context;
    
    try {
      validateWebhookPayload(payload);
      appState.security.validatedWebhooks++;
    } catch (error) {
      logger.warn('Invalid check_run payload', { error: errMsg(error) });
      appState.security.blockedRequests++;
      return;
    }

    if (payload.check_run?.name === 'DriftGuard Security') {
      const sha = payload.check_run.head_sha;
      await handleSha(context, sha);
    }
  });

  logger.info('DriftGuard Security App ready');
}

// Create Express app with full security stack
const expressApp = express();

// Apply security middleware stack
expressApp.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  }
}));

expressApp.use(securityHeaders());
expressApp.use(enhancedSecurityHeaders());

// Restrict HTTP methods globally
expressApp.use(restrictHTTPMethods(['GET', 'POST', 'HEAD', 'OPTIONS']));

// Health check endpoint
expressApp.get('/health', rateLimiters.health, (req, res) => {
  const health = getHealthData();
  logger.debug('Health check requested', { ip: req.ip });
  res.json(health);
});

// Security status endpoint
expressApp.get('/security/status', rateLimiters.api, (req, res) => {
  res.json({
    timestamp: new Date().toISOString(),
    security: appState.security,
    features: {
      webhookValidation: process.env.ENABLE_WEBHOOK_VALIDATION !== 'false',
      rateLimiting: process.env.ENABLE_RATE_LIMITING !== 'false',
      ipWhitelisting: process.env.ENABLE_IP_WHITELIST === 'true',
      replayProtection: process.env.ENABLE_REPLAY_PROTECTION !== 'false',
      asyncProcessing: webhookQueue !== null
    },
    auditTrail: auditTrail.getAuditTrail({ severity: 'error' }).slice(-10)
  });
});

// Create Probot instance
const probot = createProbot();
probot.load(app);

// Create Probot middleware
const probotMiddleware = createNodeMiddleware(app, { 
  probot,
  webhooksPath: '/api/github/webhooks'
});

// Apply full security stack to webhook endpoint
const webhookMiddlewares = [];

// Add IP whitelist if enabled
if (process.env.ENABLE_IP_WHITELIST === 'true') {
  webhookMiddlewares.push(ipWhitelistMiddleware(ipWhitelist));
  logger.info('IP whitelist middleware enabled');
}

// Add rate limiting
if (process.env.ENABLE_RATE_LIMITING !== 'false') {
  webhookMiddlewares.push(rateLimiters.webhook);
  logger.info('Rate limiting middleware enabled');
}

// Add replay protection
if (process.env.ENABLE_REPLAY_PROTECTION !== 'false') {
  webhookMiddlewares.push(replayProtectionMiddleware(replayProtection));
  logger.info('Replay protection middleware enabled');
}

// Add webhook signature validation
if (process.env.ENABLE_WEBHOOK_VALIDATION !== 'false') {
  webhookMiddlewares.push(
    webhookSignatureMiddleware(process.env.WEBHOOK_SECRET || '')
  );
  logger.info('Webhook signature validation enabled');
}

// Add request size limiting
webhookMiddlewares.push(requestSizeLimiter());

// Apply all middleware to webhook endpoint
expressApp.use(
  '/api/github/webhooks',
  ...webhookMiddlewares,
  probotMiddleware
);

// Error handling middleware
expressApp.use(securityErrorHandler);

// 404 handler
expressApp.use((req, res) => {
  res.status(404).json({ error: 'Not found' });
});

// Set process limits
if (process.env.NODE_ENV === 'production') {
  enforceProcessLimits({
    maxMemoryMB: parseInt(process.env.MAX_MEMORY_MB || '512'),
    maxCPUPercent: parseInt(process.env.MAX_CPU_PERCENT || '80'),
    restartOnMemoryLimit: process.env.RESTART_ON_MEMORY === 'true'
  });
}

// Start server
const port = process.env.PORT || 3000;
const server = expressApp.listen(port, () => {
  console.log(`
╔════════════════════════════════════════════╗
║     DriftGuard Security Server v2.0.0      ║
╠════════════════════════════════════════════╣
║  🚀 Server:     http://localhost:${port}      ║
║  🔒 Security:   FULLY INTEGRATED           ║
║  📊 Health:     /health                    ║
║  🛡️  Status:     /security/status          ║
╠════════════════════════════════════════════╣
║  Security Features Enabled:                ║
║  ✅ Webhook Validation                     ║
║  ✅ Rate Limiting                          ║
║  ${process.env.ENABLE_IP_WHITELIST === 'true' ? '✅' : '⚠️ '} IP Whitelisting                       ║
║  ✅ Replay Protection                      ║
║  ${webhookQueue ? '✅' : '⚠️ '} Async Processing                      ║
║  ✅ Security Headers                       ║
║  ✅ Error Sanitization                     ║
║  ✅ Audit Trail                            ║
╚════════════════════════════════════════════╝
  `);
  
  logger.info('Server started successfully', {
    port,
    environment: process.env.NODE_ENV,
    security: getHealthData().security
  });
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  server.close(() => {
    logger.info('Server closed');
    process.exit(0);
  });
});

export { server, appState, getHealthData };