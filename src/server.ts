/**
 * DriftGuard Checks Server - Probot v14 Server Implementation
 * Provides health endpoints via proper server setup with getRouter support
 */

import { Server, Probot } from 'probot';
import app from './index';

async function startServer() {
  // Create Probot server instance
  const server = new Server({
    Probot: Probot.defaults({
      appId: process.env.GITHUB_APP_ID!,
      privateKey: process.env.PRIVATE_KEY_PATH ? 
        require('fs').readFileSync(process.env.PRIVATE_KEY_PATH, 'utf8') : 
        process.env.PRIVATE_KEY!,
      secret: process.env.WEBHOOK_SECRET!,
      webhookPath: process.env.WEBHOOK_PATH || '/api/github/webhooks',
    })
  });

  // Load the app with getRouter support
  await server.load(app);

  // Start the server
  const port = parseInt(process.env.PORT || '3000', 10);
  server.start();
  
  console.log(`🚀 DriftGuard Checks server started on port ${port}`);
  console.log(`📊 Health endpoints available: /health, /readyz, /probot`);
  console.log(`🔗 Webhook endpoint: ${process.env.WEBHOOK_PATH || '/api/github/webhooks'}`);
  console.log(`✅ Webhook signature validation: ${process.env.WEBHOOK_SECRET ? 'ENABLED' : 'DISABLED'}`);
}

// Handle server errors
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

process.on('uncaughtException', (error) => {
  console.error('Uncaught Exception:', error);
  process.exit(1);
});

// Start the server
startServer().catch((error) => {
  console.error('Failed to start server:', error);
  process.exit(1);
});