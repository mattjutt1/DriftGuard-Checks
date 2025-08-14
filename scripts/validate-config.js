#!/usr/bin/env node

/**
 * DriftGuard Configuration Validator
 * Comprehensive validation for environment and setup
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Colors for output
const colors = {
  reset: '\x1b[0m',
  bold: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

class ConfigValidator {
  constructor() {
    this.errors = [];
    this.warnings = [];
    this.passed = [];
  }

  log(message, color = 'reset') {
    console.log(`${colors[color]}${message}${colors.reset}`);
  }

  success(message) {
    this.passed.push(message);
    this.log(`✅ ${message}`, 'green');
  }

  warning(message) {
    this.warnings.push(message);
    this.log(`⚠️  ${message}`, 'yellow');
  }

  error(message) {
    this.errors.push(message);
    this.log(`❌ ${message}`, 'red');
  }

  info(message) {
    this.log(`ℹ️  ${message}`, 'blue');
  }

  // Validation Methods
  validateEnvironmentFile() {
    this.log('\n🔍 Validating Environment Configuration', 'bold');
    
    if (!fs.existsSync('.env')) {
      this.error('Missing .env file. Run setup wizard: ./scripts/setup-wizard.sh');
      return;
    }

    const envContent = fs.readFileSync('.env', 'utf8');
    const lines = envContent.split('\n').filter(line => line.trim() && !line.startsWith('#'));
    const env = {};
    
    lines.forEach(line => {
      const [key, ...valueParts] = line.split('=');
      if (key && valueParts.length > 0) {
        env[key.trim()] = valueParts.join('=').trim().replace(/^"|"$/g, '');
      }
    });

    // Required variables
    const required = ['APP_ID', 'PRIVATE_KEY', 'WEBHOOK_SECRET', 'PORT'];
    
    required.forEach(key => {
      if (!env[key] || env[key].length === 0) {
        this.error(`Missing required environment variable: ${key}`);
      } else {
        this.success(`Environment variable ${key} is configured`);
      }
    });

    // Validate specific formats
    if (env.APP_ID && !/^\d+$/.test(env.APP_ID)) {
      this.error('APP_ID must be a numeric value');
    }

    if (env.PORT && (!/^\d+$/.test(env.PORT) || parseInt(env.PORT) < 1 || parseInt(env.PORT) > 65535)) {
      this.error('PORT must be a number between 1 and 65535');
    }

    if (env.PRIVATE_KEY && !env.PRIVATE_KEY.includes('BEGIN PRIVATE KEY')) {
      this.error('PRIVATE_KEY appears to be invalid (missing PEM headers)');
    }

    if (env.WEBHOOK_SECRET && env.WEBHOOK_SECRET.length < 16) {
      this.warning('WEBHOOK_SECRET should be at least 16 characters for security');
    }

    // Optional but recommended
    if (!env.SESSION_SECRET) {
      this.warning('SESSION_SECRET not set - using generated value');
    }

    if (!env.NODE_ENV) {
      this.warning('NODE_ENV not set - defaulting to development');
    }
  }

  validateDependencies() {
    this.log('\n📦 Validating Dependencies', 'bold');
    
    // Check package.json
    if (!fs.existsSync('package.json')) {
      this.error('Missing package.json file');
      return;
    }

    const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
    this.success('package.json found');

    // Check node_modules
    if (!fs.existsSync('node_modules')) {
      this.error('Dependencies not installed. Run: npm install');
      return;
    }

    this.success('Dependencies installed');

    // Check if build exists
    if (!fs.existsSync('dist')) {
      this.warning('Application not built. Run: npm run build');
    } else {
      this.success('Application build exists');
    }

    // Validate critical dependencies
    const critical = ['@octokit/rest', 'probot', 'express'];
    critical.forEach(dep => {
      try {
        require.resolve(dep);
        this.success(`Critical dependency ${dep} available`);
      } catch (error) {
        this.error(`Critical dependency ${dep} not found`);
      }
    });
  }

  validateGitHubApp() {
    this.log('\n🐙 Validating GitHub App Configuration', 'bold');
    
    if (!fs.existsSync('.env')) {
      this.error('Environment file not found');
      return;
    }

    // Load environment
    require('dotenv').config();
    
    const appId = process.env.APP_ID;
    const privateKey = process.env.PRIVATE_KEY;
    
    if (!appId || !privateKey) {
      this.error('GitHub App credentials not configured');
      return;
    }

    try {
      // Test JWT generation (basic validation)
      const jwt = require('jsonwebtoken');
      const now = Math.floor(Date.now() / 1000);
      
      const payload = {
        iat: now,
        exp: now + 60,
        iss: appId
      };
      
      jwt.sign(payload, privateKey, { algorithm: 'RS256' });
      this.success('GitHub App credentials format valid');
      
    } catch (error) {
      this.error(`GitHub App credential validation failed: ${error.message}`);
    }
  }

  validateNetworking() {
    this.log('\n🌐 Validating Network Configuration', 'bold');
    
    const port = process.env.PORT || 3000;
    
    try {
      // Check if port is available
      const { execSync } = require('child_process');
      execSync(`lsof -ti:${port}`, { stdio: 'ignore' });
      this.warning(`Port ${port} is already in use`);
    } catch (error) {
      this.success(`Port ${port} is available`);
    }

    // Test DNS resolution for GitHub
    try {
      require('dns').resolve4('api.github.com', (err) => {
        if (err) {
          this.warning('GitHub API DNS resolution may have issues');
        } else {
          this.success('GitHub API connectivity looks good');
        }
      });
    } catch (error) {
      this.warning('Could not test GitHub connectivity');
    }
  }

  validateSecurity() {
    this.log('\n🛡️ Validating Security Configuration', 'bold');
    
    // Check .env file permissions
    try {
      const stats = fs.statSync('.env');
      const mode = (stats.mode & parseInt('777', 8)).toString(8);
      
      if (mode === '600' || mode === '644') {
        this.success('.env file has appropriate permissions');
      } else {
        this.warning('.env file permissions may be too permissive');
      }
    } catch (error) {
      this.warning('Could not check .env file permissions');
    }

    // Check for secrets in config files
    const configFiles = ['.env.example', 'app/manifest.example.json'];
    configFiles.forEach(file => {
      if (fs.existsSync(file)) {
        const content = fs.readFileSync(file, 'utf8');
        if (content.includes('-----BEGIN') || /[A-Za-z0-9]{32,}/.test(content)) {
          this.warning(`${file} may contain secrets - ensure it's an example only`);
        } else {
          this.success(`${file} appears clean`);
        }
      }
    });

    // Check webhook secret strength
    const webhookSecret = process.env.WEBHOOK_SECRET;
    if (webhookSecret) {
      if (webhookSecret.length >= 32) {
        this.success('Webhook secret has good length');
      } else {
        this.warning('Webhook secret should be at least 32 characters');
      }
    }
  }

  validateWorkflows() {
    this.log('\n⚙️ Validating GitHub Workflows', 'bold');
    
    const workflowDir = '.github/workflows';
    if (!fs.existsSync(workflowDir)) {
      this.warning('No .github/workflows directory found');
      return;
    }

    const workflows = fs.readdirSync(workflowDir).filter(f => f.endsWith('.yml') || f.endsWith('.yaml'));
    
    if (workflows.length === 0) {
      this.warning('No workflow files found');
      return;
    }

    this.success(`Found ${workflows.length} workflow(s)`);

    // Check for DriftGuard gate workflow
    const driftguardWorkflow = workflows.find(w => w.includes('driftguard'));
    if (driftguardWorkflow) {
      this.success('DriftGuard gate workflow found');
      
      // Validate workflow content
      const workflowContent = fs.readFileSync(path.join(workflowDir, driftguardWorkflow), 'utf8');
      
      if (workflowContent.includes('actions/upload-artifact@v4')) {
        this.success('Workflow uses actions/upload-artifact@v4');
      } else {
        this.warning('Workflow should use actions/upload-artifact@v4');
      }
      
      if (workflowContent.includes('driftguard-capsule')) {
        this.success('Workflow produces driftguard-capsule artifact');
      } else {
        this.error('Workflow must produce driftguard-capsule artifact');
      }
    } else {
      this.warning('No DriftGuard gate workflow found');
    }
  }

  validateDocumentation() {
    this.log('\n📚 Validating Documentation', 'bold');
    
    const docs = ['README.md', 'LICENSE'];
    docs.forEach(doc => {
      if (fs.existsSync(doc)) {
        this.success(`${doc} exists`);
      } else {
        this.warning(`${doc} missing`);
      }
    });

    // Check docs directory
    if (fs.existsSync('docs')) {
      const docFiles = fs.readdirSync('docs');
      this.success(`Documentation directory exists with ${docFiles.length} files`);
    } else {
      this.warning('docs/ directory not found');
    }
  }

  generateReport() {
    this.log('\n📊 Validation Report', 'bold');
    this.log('=' .repeat(50), 'cyan');
    
    this.log(`\n✅ Passed: ${this.passed.length}`, 'green');
    this.log(`⚠️  Warnings: ${this.warnings.length}`, 'yellow');
    this.log(`❌ Errors: ${this.errors.length}`, 'red');
    
    if (this.errors.length > 0) {
      this.log('\n🚨 Critical Issues:', 'red');
      this.errors.forEach(error => this.log(`   • ${error}`, 'red'));
    }
    
    if (this.warnings.length > 0) {
      this.log('\n⚠️  Recommendations:', 'yellow');
      this.warnings.forEach(warning => this.log(`   • ${warning}`, 'yellow'));
    }
    
    this.log('\n' + '=' .repeat(50), 'cyan');
    
    if (this.errors.length === 0) {
      this.log('🎉 Configuration validation passed!', 'green');
      this.log('DriftGuard is ready for deployment.', 'green');
      return 0;
    } else {
      this.log('🔧 Please fix the errors above before deploying.', 'red');
      return 1;
    }
  }

  async run() {
    this.log('🛡️ DriftGuard Configuration Validator', 'bold');
    this.log('Validating your DriftGuard setup...\n', 'cyan');
    
    this.validateEnvironmentFile();
    this.validateDependencies();
    this.validateGitHubApp();
    this.validateNetworking();
    this.validateSecurity();
    this.validateWorkflows();
    this.validateDocumentation();
    
    return this.generateReport();
  }
}

// Run validator if executed directly
if (require.main === module) {
  const validator = new ConfigValidator();
  validator.run().then(exitCode => {
    process.exit(exitCode);
  }).catch(error => {
    console.error(`${colors.red}❌ Validation failed: ${error.message}${colors.reset}`);
    process.exit(1);
  });
}

module.exports = ConfigValidator;