import express from 'express';
import { createNodeMiddleware, createProbot, Probot } from 'probot';
import { throttling } from '@octokit/plugin-throttling';
import { Readable } from 'stream';
import * as unzipper from 'unzipper';
import { addEvaluationToApp } from './simple-evaluation';
import { webhookSignatureMiddleware, rateLimiters } from './security';
import { monitorRateLimit, safeThrottledApiCall } from './octokit-throttled';

// Billing system imports
import { 
  stripeWebhookHandler, 
  githubBillingIntegration,
  stripeProductManager 
} from './billing';

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

// App state tracking with billing metrics
interface AppState {
  startTime: Date;
  lastEventAt: Date | null;
  eventCount: number;
  checkRuns: BoundedMap<string, any>;
  errors: BoundedMap<string, any>;
  billingEvents: BoundedMap<string, any>;
  blockedAnalyses: number;
}

let appState: AppState = {
  startTime: new Date(),
  lastEventAt: null,
  eventCount: 0,
  checkRuns: new BoundedMap(1000),
  errors: new BoundedMap(1000),
  billingEvents: new BoundedMap(1000),
  blockedAnalyses: 0
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
  organizationId?: number;
  billingPlan?: string;
  billingStatus?: string;
  overageCharge?: number;
}) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    ...data
  };
  console.log(JSON.stringify(logEntry));
}

// Health endpoint data with billing metrics
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
    checkRunCount: appState.checkRuns.size,
    billing: {
      eventsProcessed: appState.billingEvents.size,
      blockedAnalyses: appState.blockedAnalyses
    }
  };
}

// Error boundary for API operations
async function safeApiCall<T>(
  operation: () => Promise<T>,
  context: { sha: string; operationName: string; runId?: string }
): Promise<T | null> {
  const { sha, operationName, runId } = context;
  
  try {
    const result = await operation();
    
    logEvent({
      evt: 'api_success',
      sha: sha.substring(0, 7),
      runId,
      action: operationName
    });
    
    return result;
  } catch (error) {
    const errorMsg = errMsg(error);
    
    appState.errors.set(`${sha}-${operationName}`, {
      error: errorMsg,
      timestamp: new Date(),
      operationName,
      runId
    });

    logEvent({
      evt: 'api_error',
      sha: sha.substring(0, 7),
      runId,
      action: operationName,
      error: errorMsg
    });

    return null;
  }
}

// Enhanced evaluation handler with billing enforcement
export const driftGuardApp = (app: Probot) => {
  
  // Apply billing enforcement middleware
  app.on(['pull_request.opened', 'pull_request.synchronize'], 
    githubBillingIntegration.getBillingEnforcementMiddleware()
  );

  // Apply the evaluation logic after billing checks
  addEvaluationToApp(app);

  // Add workflow run handler with billing tracking
  app.on('workflow_run.completed', async (context) => {
    appState.lastEventAt = new Date();
    appState.eventCount++;

    const { payload } = context;
    const organizationId = payload.organization?.id || payload.repository?.owner?.id;
    
    // Track for billing if organization ID is available
    if (organizationId) {
      const repositoryFullName = payload.repository?.full_name;
      if (repositoryFullName) {
        try {
          await githubBillingIntegration.recordPRAnalysis(organizationId, repositoryFullName);
        } catch (error) {
          logEvent({
            evt: 'billing_tracking_error',
            organizationId,
            error: errMsg(error)
          });
        }
      }
    }

    // Continue with original workflow handling
    logEvent({
      evt: 'workflow_completed',
      sha: payload.workflow_run.head_sha?.substring(0, 7),
      action: payload.workflow_run.name,
      result: payload.workflow_run.conclusion || 'unknown',
      organizationId
    });
  });

  // Health endpoint
  app.webhooks.onError((error) => {
    console.error('Webhook error:', error);
  });
};

// Create Express app with billing routes
const app = express();

// Trust proxy for proper IP handling behind load balancers
app.set('trust proxy', true);

// Raw body parser for Stripe webhooks
app.use('/webhooks/stripe', express.raw({ type: 'application/json' }));

// JSON parser for other routes
app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
  res.json(getHealthData());
});

// Metrics endpoint  
app.get('/metrics', (req, res) => {
  const health = getHealthData();
  res.json({
    ...health,
    errors: Array.from(appState.errors.entries()).slice(-10),
    recentCheckRuns: Array.from(appState.checkRuns.entries()).slice(-5)
  });
});

// Stripe webhook endpoint
app.post('/webhooks/stripe', async (req, res) => {
  try {
    await stripeWebhookHandler.handleWebhook(req, res);
    
    appState.billingEvents.set(
      `stripe-${Date.now()}`, 
      { 
        type: 'stripe_webhook', 
        timestamp: new Date(),
        processed: true 
      }
    );
    
    logEvent({
      evt: 'stripe_webhook_processed',
      result: 'success'
    });
  } catch (error) {
    logEvent({
      evt: 'stripe_webhook_error',
      error: errMsg(error)
    });
    
    if (!res.headersSent) {
      res.status(500).json({ error: 'Webhook processing failed' });
    }
  }
});

// Billing API endpoints
app.get('/api/billing/plans', (req, res) => {
  res.json({
    plans: Object.values(require('./billing/types').PLAN_CONFIGS)
  });
});

// Usage dashboard endpoint
app.get('/api/billing/usage/:organizationId', async (req, res) => {
  const organizationId = parseInt(req.params.organizationId);
  
  if (!organizationId) {
    return res.status(400).json({ error: 'Invalid organization ID' });
  }

  try {
    // This would typically require authentication/authorization
    // For now, we'll return a placeholder response
    res.json({
      message: 'Usage dashboard endpoint - authentication required',
      organizationId
    });
  } catch (error) {
    res.status(500).json({ error: errMsg(error) });
  }
});

// Initialize Probot
const probot = createProbot({
  defaults: {
    webhookPath: '/api/github/webhooks',
  }
});

// Add our app to Probot
probot.load(driftGuardApp);

// Create the GitHub webhooks middleware
const webhooks = createNodeMiddleware(driftGuardApp, {
  path: '/api/github/webhooks',
  probot
});

// Mount GitHub webhooks
app.use(webhookSignatureMiddleware);
app.use(webhooks);

// Error handling middleware
app.use((error: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Express error:', error);
  
  logEvent({
    evt: 'express_error',
    error: errMsg(error)
  });

  if (!res.headersSent) {
    res.status(500).json({ 
      error: 'Internal server error',
      timestamp: new Date().toISOString()
    });
  }
});

// Initialize Stripe products on startup
async function initializeBilling() {
  try {
    console.log('Initializing Stripe products...');
    await stripeProductManager.syncProducts();
    console.log('Stripe products synchronized successfully');
    
    logEvent({
      evt: 'billing_initialized',
      result: 'success'
    });
  } catch (error) {
    console.error('Failed to initialize billing:', error);
    
    logEvent({
      evt: 'billing_init_error',
      error: errMsg(error)
    });
    
    // Don't fail startup, but log the error
  }
}

// Start server
const port = process.env.PORT || 3000;

app.listen(port, async () => {
  console.log(`DriftGuard app with billing listening on port ${port}`);
  
  // Initialize billing on startup
  await initializeBilling();
  
  logEvent({
    evt: 'server_started',
    memMB: Math.round(process.memoryUsage().heapUsed / 1024 / 1024),
    uptime: 0
  });
});

export default app;