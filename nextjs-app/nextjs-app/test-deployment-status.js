#!/usr/bin/env node

/**
 * Test deployment status and provide deployment instructions
 * This script attempts to understand the current Convex deployment state
 */

const https = require('https');
const http = require('http');
const { execSync } = require('child_process');

const DEPLOYMENT_URLS = {
  convex_cloud: 'https://resilient-guanaco-29.convex.cloud',
  convex_site: 'https://resilient-guanaco-29.convex.site',
  expected_health: '/health',
  expected_optimize: '/optimize'
};

async function testEndpoint(url, method = 'GET', data = null) {
  return new Promise((resolve) => {
    const options = {
      method,
      timeout: 5000,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'PromptEvolver-CLI-Test/1.0'
      }
    };

    const req = https.request(url, options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        resolve({
          success: true,
          status: res.statusCode,
          headers: res.headers,
          body: body.slice(0, 500) // Limit body size
        });
      });
    });

    req.on('error', (err) => {
      resolve({
        success: false,
        error: err.message
      });
    });

    req.on('timeout', () => {
      req.destroy();
      resolve({
        success: false,
        error: 'Request timeout'
      });
    });

    if (data && method === 'POST') {
      req.write(JSON.stringify(data));
    }
    
    req.end();
  });
}

async function checkConvexInstallation() {
  try {
    const version = execSync('npx convex --version', { encoding: 'utf-8' }).trim();
    return { installed: true, version };
  } catch (error) {
    return { installed: false, error: error.message };
  }
}

async function checkDeploymentConfiguration() {
  const config = {
    env_vars: {},
    config_files: {}
  };

  // Check environment variables
  const envVars = ['CONVEX_DEPLOYMENT', 'NEXT_PUBLIC_CONVEX_URL', 'CONVEX_SITE_URL'];
  envVars.forEach(varName => {
    config.env_vars[varName] = process.env[varName] || 'NOT_SET';
  });

  // Check for configuration files
  const fs = require('fs');
  const configFiles = ['convex.json', '.env.local'];
  configFiles.forEach(file => {
    try {
      config.config_files[file] = fs.existsSync(file) ? 'EXISTS' : 'MISSING';
      if (fs.existsSync(file) && file === 'convex.json') {
        const content = JSON.parse(fs.readFileSync(file, 'utf-8'));
        config.config_files[file] = { exists: true, content };
      }
    } catch (error) {
      config.config_files[file] = `ERROR: ${error.message}`;
    }
  });

  return config;
}

async function main() {
  console.log('🚀 PromptEvolver Convex Deployment Status Check');
  console.log('=' .repeat(60));

  // Test 1: Check Convex CLI installation
  console.log('\n📦 Checking Convex CLI installation...');
  const convexCheck = await checkConvexInstallation();
  if (convexCheck.installed) {
    console.log(`✅ Convex CLI installed: ${convexCheck.version}`);
  } else {
    console.log(`❌ Convex CLI not installed: ${convexCheck.error}`);
  }

  // Test 2: Check deployment configuration
  console.log('\n⚙️  Checking deployment configuration...');
  const config = await checkDeploymentConfiguration();
  console.log('Environment Variables:');
  Object.entries(config.env_vars).forEach(([key, value]) => {
    const status = value === 'NOT_SET' ? '❌' : '✅';
    const displayValue = value.length > 50 ? value.slice(0, 50) + '...' : value;
    console.log(`  ${status} ${key}: ${displayValue}`);
  });

  console.log('\nConfiguration Files:');
  Object.entries(config.config_files).forEach(([key, value]) => {
    if (typeof value === 'object' && value.exists) {
      console.log(`  ✅ ${key}: ${JSON.stringify(value.content, null, 2)}`);
    } else {
      const status = value === 'MISSING' ? '❌' : '✅';
      console.log(`  ${status} ${key}: ${value}`);
    }
  });

  // Test 3: Test endpoint connectivity
  console.log('\n🌐 Testing endpoint connectivity...');
  
  for (const [name, baseUrl] of Object.entries(DEPLOYMENT_URLS)) {
    if (name.includes('health') || name.includes('optimize')) continue;
    
    console.log(`\nTesting ${name}: ${baseUrl}`);
    
    // Test health endpoint
    const healthUrl = `${baseUrl}/health`;
    console.log(`  Testing: ${healthUrl}`);
    const healthResult = await testEndpoint(healthUrl);
    
    if (healthResult.success) {
      console.log(`  ✅ Health endpoint: HTTP ${healthResult.status}`);
      if (healthResult.body) {
        console.log(`  📝 Response: ${healthResult.body.slice(0, 200)}...`);
      }
    } else {
      console.log(`  ❌ Health endpoint failed: ${healthResult.error}`);
    }
    
    // Test optimize endpoint with POST
    const optimizeUrl = `${baseUrl}/optimize`;
    console.log(`  Testing: ${optimizeUrl} (POST)`);
    const optimizeResult = await testEndpoint(optimizeUrl, 'POST', {
      prompt: 'Write a blog post about AI',
      domain: 'test'
    });
    
    if (optimizeResult.success) {
      console.log(`  ✅ Optimize endpoint: HTTP ${optimizeResult.status}`);
      if (optimizeResult.body) {
        console.log(`  📝 Response: ${optimizeResult.body.slice(0, 200)}...`);
      }
    } else {
      console.log(`  ❌ Optimize endpoint failed: ${optimizeResult.error}`);
    }
  }

  // Test 4: Provide deployment instructions
  console.log('\n📋 Deployment Instructions:');
  console.log('=' .repeat(60));
  
  const hasValidEnvVars = config.env_vars.CONVEX_DEPLOYMENT !== 'NOT_SET';
  
  if (!hasValidEnvVars) {
    console.log('❌ Missing deployment configuration. To deploy:');
    console.log('1. Run: npx convex dev');
    console.log('2. Follow authentication prompts');
    console.log('3. Choose or create a deployment');
    console.log('4. Push functions with HTTP actions enabled');
  } else {
    console.log('✅ Deployment configuration found');
    console.log('To deploy with current configuration:');
    console.log('1. Ensure you\'re authenticated: npx convex auth list');
    console.log('2. Deploy functions: npx convex deploy');
    console.log('3. Verify HTTP actions are enabled in Convex dashboard');
    
    // Provide direct deployment URLs for testing
    console.log('\n🔗 Expected endpoint URLs after deployment:');
    console.log(`Health: ${DEPLOYMENT_URLS.convex_site}/health`);
    console.log(`Optimize: ${DEPLOYMENT_URLS.convex_site}/optimize`);
  }

  // Test 5: CLI Integration Test (if endpoints are working)
  console.log('\n🧪 CLI Integration Test:');
  const cliTestUrl = `${DEPLOYMENT_URLS.convex_site}/health`;
  const cliResult = await testEndpoint(cliTestUrl);
  
  if (cliResult.success && cliResult.status === 200) {
    console.log('✅ Backend is ready for CLI integration testing');
    console.log('Run: cd ../cli && python -m pytest test_cli.py -v');
  } else {
    console.log('❌ Backend not ready - deploy first before running CLI tests');
  }

  console.log('\n✅ Deployment status check complete');
}

main().catch(console.error);