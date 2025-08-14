/**
 * DriftGuard Checks Health Server - Simple Express Implementation
 * Works alongside Probot for health endpoints
 */

import express from 'express';
import { readFileSync, existsSync } from 'fs';
import dotenv from 'dotenv';
import { rateLimiters } from './security';

// Load environment variables
dotenv.config();

const app = express();
const port = parseInt(process.env.HEALTH_PORT || '3001', 10);

// Security headers middleware
app.use((_req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
  res.setHeader('Content-Security-Policy', "default-src 'self'");
  next();
});

// Apply rate limiting
app.use('/health', rateLimiters.health);
app.use('/metrics', rateLimiters.api);
app.use('/readyz', rateLimiters.api);

// App state tracking
const appState = {
  startTime: new Date(),
  eventCount: 0,
  lastEventAt: null as Date | null,
  version: '1.0.0'
};

// Health data helper
function getHealthData() {
  const uptime = Date.now() - appState.startTime.getTime();
  
  return {
    status: 'healthy',
    message: 'DriftGuard Checks is running',
    timestamp: new Date().toISOString(),
    uptime: uptime,
    uptimeFormatted: `${Math.floor(uptime / 60000)}m ${Math.floor((uptime % 60000) / 1000)}s`,
    eventCount: appState.eventCount,
    lastEventAt: appState.lastEventAt?.toISOString() || null,
    version: appState.version,
    environment: {
      nodeEnv: process.env.NODE_ENV || 'development',
      port: process.env.PORT || '3000',
      githubAppId: process.env.GITHUB_APP_ID || 'not configured',
      webhookSecretConfigured: !!(process.env.WEBHOOK_SECRET && process.env.WEBHOOK_SECRET.length >= 32),
      privateKeyExists: existsSync(process.env.PRIVATE_KEY_PATH || './private-key.pem')
    }
  };
}

// Health endpoints
app.get('/health', (_req, res) => {
  res.status(200).json(getHealthData());
});

app.get('/readyz', (_req, res) => {
  const health = getHealthData();
  const isReady = health.environment.webhookSecretConfigured && health.environment.privateKeyExists;
  
  res.status(isReady ? 200 : 503).json({
    ready: isReady,
    status: isReady ? 'ready' : 'not ready',
    message: isReady ? 'DriftGuard Checks is ready' : 'DriftGuard Checks is not properly configured',
    timestamp: new Date().toISOString(),
    version: appState.version,
    checks: {
      webhookSecret: health.environment.webhookSecretConfigured,
      privateKey: health.environment.privateKeyExists,
      githubApp: !!health.environment.githubAppId
    }
  });
});

app.get('/metrics', (_req, res) => {
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
driftguard_check_runs_total ${appState.eventCount}

# HELP driftguard_uptime_seconds Application uptime in seconds
# TYPE driftguard_uptime_seconds gauge
driftguard_uptime_seconds ${uptime}`;

  res.setHeader('Content-Type', 'text/plain; version=0.0.4; charset=utf-8');
  res.status(200).send(metricsText);
});

app.get('/probot', (_req, res) => {
  res.status(200).json({
    status: 'ok',
    message: 'DriftGuard Checks is running',
    timestamp: new Date().toISOString(),
    framework: 'Probot v14',
    version: appState.version
  });
});

// Start health server
app.listen(port, () => {
  console.log(`🏥 Health server listening on port ${port}`);
  console.log(`📊 Health endpoints:`);
  console.log(`   • http://localhost:${port}/health - General health status`);
  console.log(`   • http://localhost:${port}/readyz - Readiness check`);
  console.log(`   • http://localhost:${port}/probot - Probot status`);
  
  const health = getHealthData();
  console.log(`✅ Configuration status:`);
  console.log(`   • Webhook secret: ${health.environment.webhookSecretConfigured ? 'CONFIGURED' : 'MISSING'}`);
  console.log(`   • Private key: ${health.environment.privateKeyExists ? 'FOUND' : 'MISSING'}`);
  console.log(`   • GitHub App ID: ${health.environment.githubAppId}`);
});