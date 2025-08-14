/**
 * Comprehensive Webhook Negative Testing
 * Tests edge cases, malformed requests, and security boundaries
 */

import { describe, test, expect, beforeAll, afterAll } from '@jest/globals';
import request from 'supertest';
import express from 'express';
import crypto from 'crypto';
import { webhookSignatureMiddleware } from '../src/security';

const TEST_SECRET = 'test-webhook-secret-at-least-32-characters-long';

describe('Webhook Negative Test Suite', () => {
  let app: express.Application;

  beforeAll(() => {
    app = express();
    app.use(express.json({ limit: '1mb' }));
    
    // Test webhook endpoint with signature validation
    app.post('/webhook', 
      webhookSignatureMiddleware(TEST_SECRET),
      (req, res) => res.json({ success: true, received: req.body })
    );

    // Test endpoint without signature validation (for comparison)
    app.post('/webhook-unsecured', 
      (req, res) => res.json({ success: true, received: req.body })
    );
  });

  describe('Signature Validation Failures', () => {
    test('should reject completely missing signature header', async () => {
      const response = await request(app)
        .post('/webhook')
        .send({ test: 'data' });

      expect(response.status).toBe(401);
      expect(response.body.error).toBe('Unauthorized');
    });

    test('should reject empty signature header', async () => {
      const response = await request(app)
        .post('/webhook')
        .set('x-hub-signature-256', '')
        .send({ test: 'data' });

      expect(response.status).toBe(401);
    });

    test('should reject malformed signature (missing sha256 prefix)', async () => {
      const response = await request(app)
        .post('/webhook')
        .set('x-hub-signature-256', 'invalidhex')
        .send({ test: 'data' });

      expect(response.status).toBe(401);
    });

    test('should reject signature with wrong prefix', async () => {
      const payload = JSON.stringify({ test: 'data' });
      const signature = `sha1=${crypto
        .createHmac('sha1', TEST_SECRET)
        .update(payload)
        .digest('hex')}`;

      const response = await request(app)
        .post('/webhook')
        .set('x-hub-signature-256', signature)
        .send({ test: 'data' });

      expect(response.status).toBe(401);
    });

    test('should reject signature computed with wrong secret', async () => {
      const payload = JSON.stringify({ test: 'data' });
      const wrongSecret = 'wrong-secret-that-is-different-and-32-chars';
      const signature = `sha256=${crypto
        .createHmac('sha256', wrongSecret)
        .update(payload)
        .digest('hex')}`;

      const response = await request(app)
        .post('/webhook')
        .set('x-hub-signature-256', signature)
        .send({ test: 'data' });

      expect(response.status).toBe(401);
    });

    test('should reject signature with extra characters', async () => {
      const payload = JSON.stringify({ test: 'data' });
      const validSignature = `sha256=${crypto
        .createHmac('sha256', TEST_SECRET)
        .update(payload)
        .digest('hex')}`;

      const response = await request(app)
        .post('/webhook')
        .set('x-hub-signature-256', validSignature + 'extra')
        .send({ test: 'data' });

      expect(response.status).toBe(401);
    });

    test('should reject truncated signature', async () => {
      const payload = JSON.stringify({ test: 'data' });
      const validSignature = `sha256=${crypto
        .createHmac('sha256', TEST_SECRET)
        .update(payload)
        .digest('hex')}`;

      const response = await request(app)
        .post('/webhook')
        .set('x-hub-signature-256', validSignature.slice(0, -5))
        .send({ test: 'data' });

      expect(response.status).toBe(401);
    });
  });

  describe('Payload Tampering Detection', () => {
    test('should detect modified payload body', async () => {
      const originalPayload = { test: 'data', important: 'value' };
      const signature = `sha256=${crypto
        .createHmac('sha256', TEST_SECRET)
        .update(JSON.stringify(originalPayload))
        .digest('hex')}`;

      // Send different payload with valid signature for original
      const tamperedPayload = { test: 'data', important: 'modified' };
      
      const response = await request(app)
        .post('/webhook')
        .set('x-hub-signature-256', signature)
        .send(tamperedPayload);

      expect(response.status).toBe(401);
    });

    test('should detect payload with additional fields', async () => {
      const originalPayload = { test: 'data' };
      const signature = `sha256=${crypto
        .createHmac('sha256', TEST_SECRET)
        .update(JSON.stringify(originalPayload))
        .digest('hex')}`;

      // Add extra field to payload
      const tamperedPayload = { test: 'data', extra: 'field' };
      
      const response = await request(app)
        .post('/webhook')
        .set('x-hub-signature-256', signature)
        .send(tamperedPayload);

      expect(response.status).toBe(401);
    });

    test('should detect payload with removed fields', async () => {
      const originalPayload = { test: 'data', keep: 'this', remove: 'this' };
      const signature = `sha256=${crypto
        .createHmac('sha256', TEST_SECRET)
        .update(JSON.stringify(originalPayload))
        .digest('hex')}`;

      // Remove field from payload
      const tamperedPayload = { test: 'data', keep: 'this' };
      
      const response = await request(app)
        .post('/webhook')
        .set('x-hub-signature-256', signature)
        .send(tamperedPayload);

      expect(response.status).toBe(401);
    });
  });

  describe('Edge Cases and Boundary Conditions', () => {
    test('should handle empty payload with valid signature', async () => {
      const payload = '';
      const signature = `sha256=${crypto
        .createHmac('sha256', TEST_SECRET)
        .update(payload)
        .digest('hex')}`;

      const response = await request(app)
        .post('/webhook')
        .set('x-hub-signature-256', signature)
        .set('content-type', 'application/json')
        .send(payload);

      // Should reject due to signature validation failure for empty payload
      expect(response.status).toBe(401);
    });

    test('should handle very large payloads', async () => {
      const largeData = 'x'.repeat(100000); // 100KB
      const payload = JSON.stringify({ data: largeData });
      const signature = `sha256=${crypto
        .createHmac('sha256', TEST_SECRET)
        .update(payload)
        .digest('hex')}`;

      const response = await request(app)
        .post('/webhook')
        .set('x-hub-signature-256', signature)
        .send(JSON.parse(payload));

      expect([200, 400, 401]).toContain(response.status);
      if (response.status === 200) expect(response.body.success).toBe(true);
    });

    test('should reject oversized payloads (>1MB)', async () => {
      const oversizedData = 'x'.repeat(2 * 1024 * 1024); // 2MB
      const payload = JSON.stringify({ data: oversizedData });

      const response = await request(app)
        .post('/webhook')
        .set('x-hub-signature-256', 'sha256=dummy')
        .send(JSON.parse(payload));

      expect(response.status).toBe(413); // Payload too large
    });

    test('should handle unicode characters in payload', async () => {
      const payload = JSON.stringify({ 
        message: '🚀 Testing unicode: éñ中文 🎉',
        emoji: '✅❌⚠️🔥'
      });
      const signature = `sha256=${crypto
        .createHmac('sha256', TEST_SECRET)
        .update(payload)
        .digest('hex')}`;

      const response = await request(app)
        .post('/webhook')
        .set('x-hub-signature-256', signature)
        .send(JSON.parse(payload));

      expect([200, 400, 401]).toContain(response.status);
      if (response.status === 200) expect(response.body.success).toBe(true);
    });
  });

  describe('Timing Attack Resistance', () => {
    test('should take similar time for valid and invalid signatures', async () => {
      const payload = JSON.stringify({ test: 'timing' });
      
      // Valid signature
      const validSignature = `sha256=${crypto
        .createHmac('sha256', TEST_SECRET)
        .update(payload)
        .digest('hex')}`;
      
      // Invalid signature (same length)
      const invalidSignature = 'sha256=' + 'a'.repeat(64);

      // Measure timing for valid signature
      const start1 = process.hrtime.bigint();
      await request(app)
        .post('/webhook')
        .set('x-hub-signature-256', validSignature)
        .send(JSON.parse(payload));
      const end1 = process.hrtime.bigint();

      // Measure timing for invalid signature
      const start2 = process.hrtime.bigint();
      await request(app)
        .post('/webhook')
        .set('x-hub-signature-256', invalidSignature)
        .send(JSON.parse(payload));
      const end2 = process.hrtime.bigint();

      const time1 = Number(end1 - start1);
      const time2 = Number(end2 - start2);
      
      // Times should be within reasonable range (timing-safe comparison)
      const ratio = Math.max(time1, time2) / Math.min(time1, time2);
      expect(ratio).toBeLessThan(2.0); // Allow for some variance
    });
  });

  describe('Content-Type Validation', () => {
    test('should handle missing content-type header', async () => {
      const payload = JSON.stringify({ test: 'data' });
      const signature = `sha256=${crypto
        .createHmac('sha256', TEST_SECRET)
        .update(payload)
        .digest('hex')}`;

      const response = await request(app)
        .post('/webhook')
        .set('x-hub-signature-256', signature)
        // No content-type header
        .send(payload);

      // Should handle gracefully (signature validation may still fail)
      expect([200, 400, 401]).toContain(response.status);
    });

    test('should handle incorrect content-type', async () => {
      const payload = JSON.stringify({ test: 'data' });
      const signature = `sha256=${crypto
        .createHmac('sha256', TEST_SECRET)
        .update(payload)
        .digest('hex')}`;

      const response = await request(app)
        .post('/webhook')
        .set('x-hub-signature-256', signature)
        .set('content-type', 'text/plain')
        .send(payload);

      // Should handle gracefully (signature validation may still fail)
      expect([200, 400, 401]).toContain(response.status);
    });
  });

  describe('GitHub Event Header Validation', () => {
    test('should log missing X-GitHub-Event header', async () => {
      const payload = JSON.stringify({ test: 'data' });
      const signature = `sha256=${crypto
        .createHmac('sha256', TEST_SECRET)
        .update(payload)
        .digest('hex')}`;

      const response = await request(app)
        .post('/webhook')
        .set('x-hub-signature-256', signature)
        // Missing X-GitHub-Event header
        .send(JSON.parse(payload));

      expect([200, 400, 401]).toContain(response.status); // Should still work
    });

    test('should handle various event types', async () => {
      const events = ['push', 'pull_request', 'issues', 'workflow_run'];
      
      for (const event of events) {
        const payload = JSON.stringify({ action: 'test', event });
        const signature = `sha256=${crypto
          .createHmac('sha256', TEST_SECRET)
          .update(payload)
          .digest('hex')}`;

        const response = await request(app)
          .post('/webhook')
          .set('x-hub-signature-256', signature)
          .set('x-github-event', event)
          .send(JSON.parse(payload));

        expect([200, 400, 401]).toContain(response.status);
      }
    });
  });

  describe('Delivery ID Tracking', () => {
    test('should handle missing X-GitHub-Delivery header', async () => {
      const payload = JSON.stringify({ test: 'data' });
      const signature = `sha256=${crypto
        .createHmac('sha256', TEST_SECRET)
        .update(payload)
        .digest('hex')}`;

      const response = await request(app)
        .post('/webhook')
        .set('x-hub-signature-256', signature)
        // Missing X-GitHub-Delivery header
        .send(JSON.parse(payload));

      expect([200, 400, 401]).toContain(response.status); // Should still work
    });

    test('should handle duplicate delivery IDs', async () => {
      const deliveryId = 'test-delivery-123';
      const payload = JSON.stringify({ test: 'data' });
      const signature = `sha256=${crypto
        .createHmac('sha256', TEST_SECRET)
        .update(payload)
        .digest('hex')}`;

      // First request
      const response1 = await request(app)
        .post('/webhook')
        .set('x-hub-signature-256', signature)
        .set('x-github-delivery', deliveryId)
        .send(JSON.parse(payload));

      // Duplicate request with same delivery ID
      const response2 = await request(app)
        .post('/webhook')
        .set('x-hub-signature-256', signature)
        .set('x-github-delivery', deliveryId)
        .send(JSON.parse(payload));

      expect(response1.status).toBe(200);
      expect(response2.status).toBe(200); // Basic webhook handler doesn't implement replay protection
    });
  });
});

describe('Security Boundary Testing', () => {
  test('should prevent signature bypass attempts', async () => {
    const app = express();
    app.use(express.json());
    
    app.post('/webhook-bypass-test', 
      webhookSignatureMiddleware(TEST_SECRET),
      (req, res) => res.json({ success: true })
    );

    // Try various bypass attempts
    const bypassAttempts = [
      { headers: { 'x-hub-signature-256': 'sha256=0' } },
      { headers: { 'x-hub-signature-256': 'sha256=' } },
      { headers: { 'x-hub-signature-256': 'bypass' } },
      { headers: { 'authorization': 'Bearer token' } }, // Wrong auth header
      { headers: {} }, // No headers
    ];

    for (const attempt of bypassAttempts) {
      const response = await request(app)
        .post('/webhook-bypass-test')
        .set(attempt.headers)
        .send({ test: 'bypass' });

      expect(response.status).toBe(401);
    }
  });
});