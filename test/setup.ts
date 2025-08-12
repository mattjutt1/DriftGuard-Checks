/**
 * Jest Test Setup
 * Configure test environment and global mocks
 */

// Set test environment variables
process.env.NODE_ENV = 'test';
process.env.LOG_LEVEL = 'error'; // Reduce noise in tests
process.env.WEBHOOK_SECRET = 'test-webhook-secret-at-least-32-chars-long';
process.env.GITHUB_APP_ID = '12345';
process.env.GITHUB_CLIENT_ID = 'test-client-id';
process.env.GITHUB_CLIENT_SECRET = 'test-client-secret-at-least-20-chars';
process.env.USE_MOCK_REDIS = 'true'; // Use mock Redis in tests

// Mock console methods to reduce test output noise
const originalConsole = {
  log: console.log,
  error: console.error,
  warn: console.warn,
  info: console.info
};

beforeAll(() => {
  // Suppress console output in tests unless DEBUG is set
  if (!process.env.DEBUG) {
    console.log = jest.fn();
    console.error = jest.fn();
    console.warn = jest.fn();
    console.info = jest.fn();
  }
});

afterAll(() => {
  // Restore console
  console.log = originalConsole.log;
  console.error = originalConsole.error;
  console.warn = originalConsole.warn;
  console.info = originalConsole.info;
});

// Global test utilities
global.testUtils = {
  generateWebhookSignature: (payload: string, secret: string): string => {
    const crypto = require('crypto');
    return `sha256=${crypto
      .createHmac('sha256', secret)
      .update(payload)
      .digest('hex')}`;
  },
  
  createMockWebhookPayload: () => ({
    action: 'completed',
    workflow_run: {
      id: 123456,
      head_sha: 'a'.repeat(40),
      workflow_id: 789,
      conclusion: 'success',
      repository: {
        id: 111,
        name: 'test-repo',
        full_name: 'owner/test-repo',
        owner: {
          login: 'owner',
          id: 222
        }
      }
    },
    repository: {
      id: 111,
      name: 'test-repo',
      full_name: 'owner/test-repo'
    },
    sender: {
      login: 'test-user',
      id: 333
    }
  }),
  
  wait: (ms: number) => new Promise(resolve => setTimeout(resolve, ms))
};

// Extend global namespace for TypeScript
declare global {
  var testUtils: {
    generateWebhookSignature: (payload: string, secret: string) => string;
    createMockWebhookPayload: () => any;
    wait: (ms: number) => Promise<void>;
  };
}

export {};