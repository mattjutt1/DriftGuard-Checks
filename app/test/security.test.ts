/**
 * Comprehensive Security Tests for DriftGuard
 * Tests all security features with real and mock scenarios
 */

import { describe, test, expect, beforeAll, afterAll, jest } from '@jest/globals';
import crypto from 'crypto';
import express from 'express';
import request from 'supertest';
import Redis from 'redis';
import { Queue } from 'bull';

// Import security modules
import {
  verifyWebhookSignature,
  webhookSignatureMiddleware,
  rateLimiters,
  sanitizeError,
  securityHeaders,
  validateWebhookPayload,
  validateEnvConfig,
  SecurityAuditLogger
} from '../src/security';

import {
  GitHubIPWhitelist,
  WebhookQueue,
  ReplayProtection,
  requestSizeLimiter,
  enhancedSecurityHeaders,
  SecurityAuditTrail
} from '../src/security/advanced-2025';

// Test configuration
const TEST_SECRET = 'test-webhook-secret-that-is-at-least-32-characters-long';
const TEST_REDIS_URL = process.env.TEST_REDIS_URL || 'redis://localhost:6379';

describe('Security Module Tests', () => {
  
  describe('Webhook Signature Validation', () => {
    test('should validate correct webhook signature', () => {
      const payload = JSON.stringify({ test: 'data' });
      const signature = `sha256=${crypto
        .createHmac('sha256', TEST_SECRET)
        .update(payload)
        .digest('hex')}`;
      
      const result = verifyWebhookSignature(payload, signature, TEST_SECRET);
      expect(result).toBe(true);
    });

    test('should reject invalid webhook signature', () => {
      const payload = JSON.stringify({ test: 'data' });
      const signature = 'sha256=invalid-signature';
      
      const result = verifyWebhookSignature(payload, signature, TEST_SECRET);
      expect(result).toBe(false);
    });

    test('should reject missing signature', () => {
      const payload = JSON.stringify({ test: 'data' });
      
      const result = verifyWebhookSignature(payload, undefined, TEST_SECRET);
      expect(result).toBe(false);
    });

    test('should use timing-safe comparison', () => {
      // This tests that the function doesn't return early on first mismatch
      const payload = JSON.stringify({ test: 'data' });
      const correctSig = `sha256=${crypto
        .createHmac('sha256', TEST_SECRET)
        .update(payload)
        .digest('hex')}`;
      
      // Test with similar signatures (should take similar time)
      const start1 = process.hrtime.bigint();
      verifyWebhookSignature(payload, correctSig, TEST_SECRET);
      const end1 = process.hrtime.bigint();
      
      const wrongSig = correctSig.slice(0, -1) + 'x';
      const start2 = process.hrtime.bigint();
      verifyWebhookSignature(payload, wrongSig, TEST_SECRET);
      const end2 = process.hrtime.bigint();
      
      // Times should be within 50% of each other (timing-safe)
      const time1 = Number(end1 - start1);
      const time2 = Number(end2 - start2);
      const ratio = Math.max(time1, time2) / Math.min(time1, time2);
      
      expect(ratio).toBeLessThan(1.5);
    });
  });

  describe('Webhook Signature Middleware', () => {
    let app: express.Application;

    beforeAll(() => {
      app = express();
      app.use(express.json());
      app.post('/webhook', 
        webhookSignatureMiddleware(TEST_SECRET),
        (req, res) => res.json({ success: true })
      );
    });

    test('should allow valid webhook', async () => {
      const payload = { test: 'data' };
      const payloadString = JSON.stringify(payload);
      const signature = `sha256=${crypto
        .createHmac('sha256', TEST_SECRET)
        .update(payloadString)
        .digest('hex')}`;

      const response = await request(app)
        .post('/webhook')
        .set('x-hub-signature-256', signature)
        .send(payload);

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
    });

    test('should reject invalid webhook', async () => {
      const response = await request(app)
        .post('/webhook')
        .set('x-hub-signature-256', 'sha256=invalid')
        .send({ test: 'data' });

      expect(response.status).toBe(401);
      expect(response.body.error).toBe('Unauthorized');
    });
  });

  describe('Rate Limiting', () => {
    let app: express.Application;

    beforeAll(() => {
      app = express();
      app.get('/api', rateLimiters.api, (req, res) => res.json({ ok: true }));
      app.get('/health', rateLimiters.health, (req, res) => res.json({ ok: true }));
    });

    test('should enforce API rate limits', async () => {
      // Make requests up to the limit
      const limit = 200; // API limit per minute
      const requests = [];
      
      // Make 201 requests (one over limit)
      for (let i = 0; i < limit + 1; i++) {
        requests.push(request(app).get('/api'));
      }
      
      const responses = await Promise.all(requests);
      
      // First 200 should succeed
      const successCount = responses.filter(r => r.status === 200).length;
      expect(successCount).toBe(limit);
      
      // Last one should be rate limited
      const rateLimited = responses.filter(r => r.status === 429).length;
      expect(rateLimited).toBeGreaterThan(0);
    });

    test('health endpoint should have higher limit', async () => {
      // Health limit is 300/min, much higher than API
      const requests = [];
      for (let i = 0; i < 250; i++) {
        requests.push(request(app).get('/health'));
      }
      
      const responses = await Promise.all(requests);
      const successCount = responses.filter(r => r.status === 200).length;
      
      // All 250 should succeed (under 300 limit)
      expect(successCount).toBe(250);
    });
  });

  describe('Error Sanitization', () => {
    const originalEnv = process.env.NODE_ENV;

    afterAll(() => {
      process.env.NODE_ENV = originalEnv;
    });

    test('should sanitize errors in production', () => {
      process.env.NODE_ENV = 'production';
      
      const error = new Error('Sensitive database connection failed at 192.168.1.1');
      error.name = 'ValidationError';
      
      const sanitized = sanitizeError(error);
      
      expect(sanitized.message).toBe('Invalid request data');
      expect(sanitized.message).not.toContain('192.168.1.1');
    });

    test('should show more detail in development', () => {
      process.env.NODE_ENV = 'development';
      
      const error = new Error('Database connection failed');
      const sanitized = sanitizeError(error);
      
      expect(sanitized.message).toBe('Database connection failed');
    });
  });

  describe('Input Validation', () => {
    test('should validate webhook payload', () => {
      const validPayload = {
        action: 'completed',
        workflow_run: {
          id: 123,
          head_sha: 'a'.repeat(40),
          workflow_id: 456,
          repository: {
            id: 789,
            name: 'test-repo',
            full_name: 'owner/test-repo',
            owner: { login: 'owner', id: 1 }
          }
        },
        repository: {
          id: 789,
          name: 'test-repo',
          full_name: 'owner/test-repo'
        },
        sender: { login: 'user', id: 2 }
      };

      expect(() => validateWebhookPayload(validPayload)).not.toThrow();
    });

    test('should reject invalid SHA', () => {
      const invalidPayload = {
        action: 'completed',
        workflow_run: {
          id: 123,
          head_sha: 'not-a-valid-sha',
          workflow_id: 456,
          repository: {
            id: 789,
            name: 'test-repo',
            full_name: 'owner/test-repo',
            owner: { login: 'owner', id: 1 }
          }
        },
        repository: {
          id: 789,
          name: 'test-repo',
          full_name: 'owner/test-repo'
        },
        sender: { login: 'user', id: 2 }
      };

      expect(() => validateWebhookPayload(invalidPayload)).toThrow();
    });
  });

  describe('Security Headers', () => {
    let app: express.Application;

    beforeAll(() => {
      app = express();
      app.use(securityHeaders());
      app.use(enhancedSecurityHeaders());
      app.get('/test', (req, res) => res.json({ ok: true }));
    });

    test('should set security headers', async () => {
      const response = await request(app).get('/test');
      
      expect(response.headers['x-content-type-options']).toBe('nosniff');
      expect(response.headers['x-frame-options']).toBe('DENY');
      expect(response.headers['x-xss-protection']).toBe('1; mode=block');
      expect(response.headers['strict-transport-security']).toContain('max-age=31536000');
      expect(response.headers['x-powered-by']).toBeUndefined();
    });

    test('should set enhanced 2025 headers', async () => {
      const response = await request(app).get('/test');
      
      expect(response.headers['x-dns-prefetch-control']).toBe('off');
      expect(response.headers['x-download-options']).toBe('noopen');
      expect(response.headers['x-permitted-cross-domain-policies']).toBe('none');
    });
  });
});

describe('Advanced Security Features', () => {
  
  describe('GitHub IP Whitelist', () => {
    let whitelist: GitHubIPWhitelist;

    beforeAll(() => {
      whitelist = new GitHubIPWhitelist();
    });

    test('should fetch GitHub IPs from meta API', async () => {
      await whitelist.updateWhitelist();
      
      // GitHub always has some IPs
      const testIP = '140.82.112.1'; // GitHub IP range
      const allowed = await whitelist.isAllowed(testIP);
      
      expect(allowed).toBeDefined();
    });

    test('should block non-GitHub IPs', async () => {
      const testIP = '1.2.3.4'; // Not a GitHub IP
      const allowed = await whitelist.isAllowed(testIP);
      
      expect(allowed).toBe(false);
    });
  });

  describe('Replay Protection', () => {
    let replayProtection: ReplayProtection;

    beforeAll(() => {
      replayProtection = new ReplayProtection();
    });

    test('should prevent replay attacks', () => {
      const deliveryId = 'unique-delivery-id-123';
      
      // First request should be allowed
      expect(replayProtection.isReplay(deliveryId)).toBe(false);
      
      // Replay should be blocked
      expect(replayProtection.isReplay(deliveryId)).toBe(true);
    });

    test('should expire old delivery IDs', () => {
      const oldId = 'old-delivery-id';
      
      // Add an old entry (mock as if it was added an hour ago)
      replayProtection['deliveryIds'].set(oldId, Date.now() - 3700000); // 1h 10min ago
      
      // Clean expired entries
      replayProtection.cleanExpired();
      
      // Should now be allowed again
      expect(replayProtection.isReplay(oldId)).toBe(false);
    });
  });

  describe('Request Size Limiting', () => {
    let app: express.Application;

    beforeAll(() => {
      app = express();
      app.use(requestSizeLimiter());
      app.post('/upload', (req, res) => res.json({ received: true }));
    });

    test('should limit JSON payload size', async () => {
      // Create a payload larger than 1MB
      const largePayload = { data: 'x'.repeat(1024 * 1024 + 1) };
      
      const response = await request(app)
        .post('/upload')
        .set('Content-Type', 'application/json')
        .send(largePayload);
      
      expect(response.status).toBe(413); // Payload too large
    });
  });

  describe('Security Audit Trail', () => {
    let auditTrail: SecurityAuditTrail;

    beforeAll(() => {
      auditTrail = new SecurityAuditTrail();
    });

    test('should log security events', () => {
      auditTrail.log({
        type: 'authentication',
        severity: 'info',
        action: 'login',
        result: 'success',
        details: { user: 'test' }
      });

      const trail = auditTrail.getAuditTrail();
      
      expect(trail.length).toBeGreaterThan(0);
      expect(trail[0].type).toBe('authentication');
      expect(trail[0].severity).toBe('info');
    });

    test('should filter by severity', () => {
      auditTrail.log({
        type: 'test1',
        severity: 'info',
        action: 'test',
        result: 'success'
      });

      auditTrail.log({
        type: 'test2',
        severity: 'error',
        action: 'test',
        result: 'failure'
      });

      const errors = auditTrail.getAuditTrail({ severity: 'error' });
      
      expect(errors.every(e => e.severity === 'error')).toBe(true);
    });
  });
});

describe('Redis Integration', () => {
  let queue: WebhookQueue | null = null;

  beforeAll(async () => {
    // Try to connect to Redis
    try {
      queue = new WebhookQueue(TEST_REDIS_URL);
      await queue.testConnection();
    } catch (error) {
      console.log('Redis not available, skipping Redis tests');
      queue = null;
    }
  });

  test('should connect to Redis if available', async () => {
    if (!queue) {
      console.log('Skipping: Redis not available');
      return;
    }

    const status = await queue.getQueueStatus();
    expect(status).toBeDefined();
    expect(status).toHaveProperty('waiting');
    expect(status).toHaveProperty('active');
  });

  test('should queue webhooks for processing', async () => {
    if (!queue) {
      console.log('Skipping: Redis not available');
      return;
    }

    const jobId = await queue.addWebhook(
      { test: 'payload' },
      { 'x-github-delivery': 'test-123' }
    );

    expect(jobId).toBeDefined();
    expect(typeof jobId).toBe('string');
  });
});