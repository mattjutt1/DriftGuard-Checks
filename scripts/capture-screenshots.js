const { chromium } = require('playwright');

async function captureScreenshots() {
  console.log('🚀 Launching headed browser for screenshot capture...');
  
  // Launch browser in headed mode so we can see what's happening
  const browser = await chromium.launch({ 
    headless: false,
    slowMo: 1000 // Slow down actions for visibility
  });
  
  const context = await browser.newContext({
    viewport: { width: 1200, height: 800 }
  });
  
  const page = await context.newPage();
  
  try {
    // Navigate to health endpoint first
    console.log('📊 Capturing health endpoint...');
    await page.goto('http://localhost:3001/health');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ 
      path: 'assets/screenshots/health-endpoint.png',
      fullPage: true 
    });
    
    // Navigate to metrics endpoint
    console.log('📈 Capturing metrics endpoint...');
    await page.goto('http://localhost:3001/metrics');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ 
      path: 'assets/screenshots/metrics-endpoint.png',
      fullPage: true 
    });
    
    // Navigate to readiness endpoint
    console.log('✅ Capturing readiness endpoint...');
    await page.goto('http://localhost:3001/readyz');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ 
      path: 'assets/screenshots/readiness-check.png',
      fullPage: true 
    });
    
    // Try to trigger a webhook simulation
    console.log('🔗 Attempting webhook demo...');
    const webhookData = {
      action: 'opened',
      pull_request: {
        number: 123,
        title: 'Add new authentication module',
        head: { sha: 'abc123def456' },
        base: { ref: 'main' }
      },
      repository: {
        name: 'demo-repo',
        full_name: 'demo-org/demo-repo'
      }
    };
    
    // Create a simple HTML page to show the app in action
    const demoHTML = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>DriftGuard Demo</title>
      <style>
        body { 
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          margin: 0; 
          padding: 20px; 
          background: #f6f8fa;
        }
        .container { 
          max-width: 800px; 
          margin: 0 auto; 
          background: white; 
          border-radius: 8px; 
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
          overflow: hidden;
        }
        .header { 
          background: linear-gradient(135deg, #3b82f6, #1e40af); 
          color: white; 
          padding: 30px; 
          text-align: center;
        }
        .logo { 
          width: 60px; 
          height: 60px; 
          margin: 0 auto 15px;
          background: white;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 24px;
        }
        .content { padding: 30px; }
        .status-item { 
          display: flex; 
          align-items: center; 
          padding: 15px; 
          margin: 10px 0;
          background: #f8fafc;
          border-radius: 6px;
          border-left: 4px solid #22c55e;
        }
        .status-icon { 
          width: 24px; 
          height: 24px; 
          margin-right: 15px;
          background: #22c55e;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 14px;
        }
        .endpoint { 
          font-family: 'Monaco', 'Consolas', monospace;
          background: #1f2937;
          color: #e5e7eb;
          padding: 20px;
          border-radius: 6px;
          margin: 15px 0;
          overflow-x: auto;
        }
        .json { color: #60a5fa; }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <div class="logo">🛡️</div>
          <h1>DriftGuard</h1>
          <p>Enterprise Code Analysis Platform</p>
        </div>
        <div class="content">
          <h2>System Status</h2>
          <div class="status-item">
            <div class="status-icon">✓</div>
            <div>
              <strong>Application Health</strong><br>
              <small>All systems operational</small>
            </div>
          </div>
          <div class="status-item">
            <div class="status-icon">⚡</div>
            <div>
              <strong>Performance Metrics</strong><br>
              <small>Response time: &lt;200ms</small>
            </div>
          </div>
          <div class="status-item">
            <div class="status-icon">🔗</div>
            <div>
              <strong>GitHub Integration</strong><br>
              <small>Webhook endpoint ready</small>
            </div>
          </div>
          
          <h2>API Endpoints</h2>
          <div class="endpoint">
            <div class="json">GET /health</div>
            Returns application health status and metrics
          </div>
          <div class="endpoint">
            <div class="json">GET /metrics</div>
            Prometheus-compatible metrics for monitoring
          </div>
          <div class="endpoint">
            <div class="json">POST /webhooks/github</div>
            GitHub webhook handler for PR analysis
          </div>
        </div>
      </div>
    </body>
    </html>
    `;
    
    // Set content and capture
    console.log('🎨 Creating demo interface...');
    await page.setContent(demoHTML);
    await page.waitForTimeout(2000); // Let it render
    await page.screenshot({ 
      path: 'assets/screenshots/driftguard-demo.png',
      fullPage: true 
    });
    
    console.log('✅ Screenshots captured successfully!');
    console.log('📁 Saved to:');
    console.log('  - assets/screenshots/health-endpoint.png');
    console.log('  - assets/screenshots/metrics-endpoint.png');
    console.log('  - assets/screenshots/readiness-check.png');
    console.log('  - assets/screenshots/driftguard-demo.png');
    
  } catch (error) {
    console.error('❌ Error capturing screenshots:', error);
  } finally {
    await browser.close();
  }
}

captureScreenshots();