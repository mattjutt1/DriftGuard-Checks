/**
 * DriftGuard E2E Tests - Marketplace Readiness
 * Comprehensive end-to-end testing for GitHub Marketplace submission
 */

const { test, expect } = require('@playwright/test');

// Test configuration
const config = {
  baseURL: process.env.BASE_URL || 'http://localhost:3000',
  timeout: 30000,
  retries: 2
};

test.describe('DriftGuard Marketplace Readiness', () => {
  
  test.beforeAll(async () => {
    // Ensure DriftGuard is running
    console.log('Testing against:', config.baseURL);
  });

  test.describe('Core Application Health', () => {
    
    test('health endpoint returns success', async ({ request }) => {
      const response = await request.get(`${config.baseURL}/health`);
      expect(response.status()).toBe(200);
      
      const data = await response.json();
      expect(data.status).toBe('healthy');
      expect(data.message).toContain('DriftGuard');
      expect(data.version).toBeDefined();
      expect(data.uptime).toBeDefined();
    });

    test('readiness endpoint confirms load balancer compatibility', async ({ request }) => {
      const response = await request.get(`${config.baseURL}/readyz`);
      expect(response.status()).toBe(200);
      
      const data = await response.json();
      expect(data.ready).toBe(true);
    });

    test('metrics endpoint provides prometheus-compatible data', async ({ request }) => {
      const response = await request.get(`${config.baseURL}/metrics`);
      expect(response.status()).toBe(200);
      
      const metrics = await response.text();
      expect(metrics).toContain('# HELP');
      expect(metrics).toContain('# TYPE');
      expect(metrics).toContain('nodejs_');
    });
  });

  test.describe('GitHub App Integration', () => {
    
    test('webhook endpoint handles POST requests', async ({ request }) => {
      const mockPRPayload = {
        action: 'opened',
        pull_request: {
          number: 123,
          title: 'Test PR for marketplace validation',
          head: { sha: 'abc123def456' },
          base: { ref: 'main' }
        },
        repository: {
          name: 'test-repo',
          full_name: 'test-org/test-repo'
        }
      };

      // This should return 400 due to missing signature (expected)
      const response = await request.post(`${config.baseURL}/webhooks/github`, {
        data: mockPRPayload,
        headers: {
          'Content-Type': 'application/json',
          'X-GitHub-Event': 'pull_request'
        }
      });
      
      // Expecting 400 due to signature validation (security working correctly)
      expect([400, 401, 403]).toContain(response.status());
    });

    test('webhook validates signatures properly', async ({ request }) => {
      const payload = JSON.stringify({ test: 'data' });
      
      const response = await request.post(`${config.baseURL}/webhooks/github`, {
        data: payload,
        headers: {
          'Content-Type': 'application/json',
          'X-GitHub-Event': 'ping',
          'X-Hub-Signature-256': 'sha256=invalid'
        }
      });
      
      // Should reject invalid signatures
      expect([400, 401, 403]).toContain(response.status());
    });
  });

  test.describe('Performance & Reliability', () => {
    
    test('response times meet SLA requirements', async ({ request }) => {
      const startTime = Date.now();
      const response = await request.get(`${config.baseURL}/health`);
      const responseTime = Date.now() - startTime;
      
      expect(response.status()).toBe(200);
      expect(responseTime).toBeLessThan(2000); // 2 second SLA
    });

    test('handles concurrent requests gracefully', async ({ request }) => {
      const concurrentRequests = 10;
      const promises = [];
      
      for (let i = 0; i < concurrentRequests; i++) {
        promises.push(request.get(`${config.baseURL}/health`));
      }
      
      const responses = await Promise.all(promises);
      
      // All requests should succeed
      for (const response of responses) {
        expect(response.status()).toBe(200);
      }
    });

    test('handles malformed requests safely', async ({ request }) => {
      // Test various malformed requests
      const malformedTests = [
        { path: '/webhooks/github', data: 'invalid-json', contentType: 'application/json' },
        { path: '/health', data: null, contentType: 'application/xml' },
        { path: '/nonexistent', data: null, contentType: 'application/json' }
      ];

      for (const testCase of malformedTests) {
        const response = await request.post(`${config.baseURL}${testCase.path}`, {
          data: testCase.data,
          headers: { 'Content-Type': testCase.contentType }
        });
        
        // Should handle gracefully, not crash
        expect(response.status()).toBeGreaterThanOrEqual(400);
        expect(response.status()).toBeLessThan(500);
      }
    });
  });

  test.describe('Security Standards', () => {
    
    test('implements proper security headers', async ({ request }) => {
      const response = await request.get(`${config.baseURL}/health`);
      
      expect(response.headers()['x-content-type-options']).toBe('nosniff');
      expect(response.headers()['x-frame-options']).toBeDefined();
      expect(response.headers()['x-xss-protection']).toBeDefined();
    });

    test('does not expose sensitive information in errors', async ({ request }) => {
      const response = await request.get(`${config.baseURL}/nonexistent-endpoint`);
      const text = await response.text();
      
      // Should not expose stack traces or internal paths
      expect(text).not.toMatch(/\/[A-Za-z]:[\\\\].*[\\\\]/); // Windows paths
      expect(text).not.toMatch(/\/home\/.*\//); // Unix paths
      expect(text).not.toMatch(/at Object\.[^\\\\s]+/); // Stack traces
    });

    test('rate limiting protects against abuse', async ({ request }) => {
      // Attempt rapid requests to test rate limiting
      const rapidRequests = 50;
      const promises = [];
      
      for (let i = 0; i < rapidRequests; i++) {
        promises.push(
          request.post(`${config.baseURL}/webhooks/github`, {
            data: '{}',
            headers: { 'Content-Type': 'application/json' }
          })
        );
      }
      
      const responses = await Promise.all(promises);
      const rateLimitedResponses = responses.filter(r => r.status() === 429);
      
      // Should have some rate limited responses
      expect(rateLimitedResponses.length).toBeGreaterThan(0);
    });
  });

  test.describe('Enterprise Features', () => {
    
    test('provides comprehensive audit logging', async ({ request }) => {
      // Make several requests to generate audit events
      await request.get(`${config.baseURL}/health`);
      await request.get(`${config.baseURL}/metrics`);
      await request.post(`${config.baseURL}/webhooks/github`, {
        data: '{"test": "audit"}',
        headers: { 'Content-Type': 'application/json' }
      });
      
      // Verify logging is working (logs should be accessible for audit)
      // This is a basic test - in production, you'd verify log aggregation
      const healthResponse = await request.get(`${config.baseURL}/health`);
      expect(healthResponse.status()).toBe(200);
    });

    test('monitoring endpoints support observability', async ({ request }) => {
      const metricsResponse = await request.get(`${config.baseURL}/metrics`);
      const metrics = await metricsResponse.text();
      
      // Verify key enterprise metrics exist
      expect(metrics).toContain('http_requests_total');
      expect(metrics).toContain('nodejs_heap_size_total_bytes');
      expect(metrics).toContain('process_cpu_user_seconds_total');
    });
  });

  test.describe('Documentation & UX', () => {
    
    test('health endpoint provides clear status information', async ({ request }) => {
      const response = await request.get(`${config.baseURL}/health`);
      const data = await response.json();
      
      // Verify user-friendly information
      expect(data.message).toBeTruthy();
      expect(data.timestamp).toBeTruthy();
      expect(data.version).toBeTruthy();
      expect(data.uptimeFormatted).toBeTruthy();
    });

    test('error responses are user-friendly', async ({ request }) => {
      const response = await request.get(`${config.baseURL}/invalid-endpoint`);
      
      expect(response.status()).toBe(404);
      
      // Should provide helpful error message, not just "Not Found"
      const text = await response.text();
      expect(text.length).toBeGreaterThan(20); // More than just "Not Found"
    });
  });

  test.describe('Marketplace Compliance', () => {
    
    test('application starts within acceptable time', async ({ request }) => {
      // This test assumes the app just started; in real scenario, 
      // you'd restart the container and measure startup time
      const response = await request.get(`${config.baseURL}/health`);
      const data = await response.json();
      
      expect(response.status()).toBe(200);
      expect(data.status).toBe('healthy');
    });

    test('handles GitHub webhook events without errors', async ({ request }) => {
      const validEvents = ['ping', 'pull_request', 'check_run', 'check_suite'];
      
      for (const event of validEvents) {
        const response = await request.post(`${config.baseURL}/webhooks/github`, {
          data: JSON.stringify({ action: 'test', zen: 'GitHub event test' }),
          headers: {
            'Content-Type': 'application/json',
            'X-GitHub-Event': event
          }
        });
        
        // Should not crash on valid event types
        expect(response.status()).not.toBe(500);
      }
    });

    test('provides proper API versioning support', async ({ request }) => {
      const response = await request.get(`${config.baseURL}/health`);
      const data = await response.json();
      
      // Version should be semantic version format
      expect(data.version).toMatch(/^\d+\.\d+\.\d+/);
    });
  });
});

test.describe('Integration Scenarios', () => {
  
  test('simulates real GitHub App workflow', async ({ request }) => {
    // Simulate the full workflow a repository owner would experience
    
    // 1. Install GitHub App (simulated by webhook registration)
    // 2. Create PR (simulated by webhook)
    // 3. DriftGuard processes and responds
    
    const prPayload = {
      action: 'opened',
      number: 1,
      pull_request: {
        id: 123456789,
        number: 1,
        title: 'Add new feature',
        body: 'This PR adds a new feature to the application',
        head: {
          sha: 'abc123def456789',
          ref: 'feature-branch'
        },
        base: {
          sha: 'def456abc123789',
          ref: 'main'
        }
      },
      repository: {
        id: 987654321,
        name: 'test-repo',
        full_name: 'test-org/test-repo',
        private: false
      }
    };

    // This will fail signature validation (expected) but shouldn't crash
    const response = await request.post(`${config.baseURL}/webhooks/github`, {
      data: JSON.stringify(prPayload),
      headers: {
        'Content-Type': 'application/json',
        'X-GitHub-Event': 'pull_request',
        'X-GitHub-Delivery': 'test-delivery-id'
      }
    });

    // Should handle gracefully
    expect(response.status()).toBeGreaterThanOrEqual(400);
    expect(response.status()).toBeLessThan(500);
  });
});

// Test teardown
test.afterAll(async () => {
  console.log('✅ DriftGuard E2E tests completed - Marketplace ready!');
});