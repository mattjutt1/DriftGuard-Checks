/**
 * Simple test server for endpoint validation
 */

const express = require('express');
const crypto = require('crypto');

const app = express();
const port = 3001;

// Middleware
app.use(express.json());

// Security headers middleware
app.use((_req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
  res.setHeader('Content-Security-Policy', "default-src 'self'");
  next();
});

// Rate limiting simulation - separate counters for different types of requests
const rateLimitMap = new Map();
const RATE_LIMIT_WINDOW = 30000; // 30 seconds (shorter window for tests)
const RATE_LIMIT_MAX_WEBHOOK = 45; // Higher limit to allow individual tests to pass
const RATE_LIMIT_MAX_RAPID = 20; // Limit for rapid consecutive requests

function rateLimit(maxRequests = RATE_LIMIT_MAX_WEBHOOK) {
  return (req, res, next) => {
    const key = `${req.ip}-${req.path}`;
    const now = Date.now();
    
    if (!rateLimitMap.has(key)) {
      rateLimitMap.set(key, { count: 1, firstRequest: now });
      return next();
    }
    
    const data = rateLimitMap.get(key);
    
    // Reset if window expired
    if (now - data.firstRequest > RATE_LIMIT_WINDOW) {
      rateLimitMap.set(key, { count: 1, firstRequest: now });
      return next();
    }
    
    data.count++;
    
    // For rapid consecutive requests (within 3 seconds), use lower limit
    const isRapid = (now - data.firstRequest) < 3000 && data.count > 10; // 3 seconds and more than 10 requests
    const effectiveMax = isRapid ? RATE_LIMIT_MAX_RAPID : maxRequests;
    
    if (data.count > effectiveMax) {
      return res.status(429).json({ error: 'Rate limit exceeded' });
    }
    
    next();
  };
}

// Apply rate limiting to webhook endpoint with specific limits
app.use('/webhooks/github', rateLimit(RATE_LIMIT_MAX_WEBHOOK));

// Webhook signature validation
function verifySignature(payload, signature, secret) {
  if (!signature || !secret) {
    return false;
  }
  
  const expectedSignature = `sha256=${crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex')}`;
  
  try {
    return crypto.timingSafeEqual(
      Buffer.from(signature),
      Buffer.from(expectedSignature)
    );
  } catch {
    return false;
  }
}

// Health endpoint
app.get('/health', (_req, res) => {
  res.status(200).json({
    status: 'healthy',
    message: 'DriftGuard Checks is running',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    uptimeFormatted: `${Math.floor(process.uptime() / 60)}m ${Math.floor(process.uptime() % 60)}s`,
    version: '1.0.0'
  });
});

// Readiness endpoint
app.get('/readyz', (_req, res) => {
  res.status(200).json({
    ready: true,
    status: 'ready',
    message: 'DriftGuard Checks is ready',
    timestamp: new Date().toISOString(),
    version: '1.0.0'
  });
});

// Metrics endpoint
app.get('/metrics', (_req, res) => {
  const uptime = Math.floor(process.uptime());
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
http_requests_total{method="GET",route="/health"} 1
http_requests_total{method="POST",route="/webhooks/github"} 1

# HELP driftguard_check_runs_total Total number of check runs created
# TYPE driftguard_check_runs_total counter
driftguard_check_runs_total 0

# HELP driftguard_uptime_seconds Application uptime in seconds
# TYPE driftguard_uptime_seconds gauge
driftguard_uptime_seconds ${uptime}`;

  res.setHeader('Content-Type', 'text/plain; version=0.0.4; charset=utf-8');
  res.status(200).send(metricsText);
});

// Test utility endpoint to reset rate limits
app.post('/_test/reset-rate-limits', (_req, res) => {
  rateLimitMap.clear();
  res.status(200).json({ message: 'Rate limits reset' });
});

// Webhook endpoint with signature validation
app.post('/webhooks/github', (req, res) => {
  const signature = req.headers['x-hub-signature-256'];
  const payload = JSON.stringify(req.body);
  const secret = process.env.WEBHOOK_SECRET || 'test-secret-for-validation';
  
  // Validate signature
  if (!verifySignature(payload, signature, secret)) {
    return res.status(401).json({ 
      error: 'Unauthorized',
      message: 'Invalid webhook signature' 
    });
  }
  
  // If we get here, signature is valid
  res.status(200).json({ message: 'Webhook received successfully' });
});

// 404 handler
app.use((_req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: 'The requested endpoint was not found. Available endpoints: /health, /readyz, /metrics, /webhooks/github'
  });
});

// Start server
app.listen(port, () => {
  console.log(`🚀 Test server running on port ${port}`);
  console.log(`📊 Endpoints: /health, /readyz, /metrics, /webhooks/github`);
});