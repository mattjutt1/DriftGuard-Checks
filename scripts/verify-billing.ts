import { stripeProductManager, PLAN_CONFIGS } from '../src/billing';

/**
 * Verification script for billing infrastructure
 */
async function verifyBillingInfrastructure() {
  console.log('🔍 Verifying DriftGuard billing infrastructure...\n');

  let errors = 0;
  let warnings = 0;

  // Check environment variables
  console.log('📋 Checking environment variables:');
  const requiredEnvVars = [
    'STRIPE_SECRET_KEY',
    'APP_URL',
  ];

  const optionalEnvVars = [
    'STRIPE_WEBHOOK_SECRET',
    'DATABASE_URL',
    'REDIS_URL',
  ];

  for (const envVar of requiredEnvVars) {
    if (!process.env[envVar]) {
      console.log(`❌ Missing required environment variable: ${envVar}`);
      errors++;
    } else {
      console.log(`✅ ${envVar} is set`);
    }
  }

  for (const envVar of optionalEnvVars) {
    if (!process.env[envVar]) {
      console.log(`⚠️  Optional environment variable not set: ${envVar}`);
      warnings++;
    } else {
      console.log(`✅ ${envVar} is set`);
    }
  }

  console.log();

  // Check Stripe configuration
  console.log('🔒 Checking Stripe configuration:');
  try {
    if (process.env.STRIPE_SECRET_KEY) {
      const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
      
      // Test API connection
      const account = await stripe.accounts.retrieve();
      console.log(`✅ Stripe API connection successful (Account: ${account.display_name || account.id})`);
      
      // Check webhook endpoints
      const webhookEndpoints = await stripe.webhookEndpoints.list({ limit: 10 });
      console.log(`✅ Found ${webhookEndpoints.data.length} webhook endpoints`);
      
      if (webhookEndpoints.data.length === 0) {
        console.log(`⚠️  No webhook endpoints configured - you'll need to set one up for production`);
        warnings++;
      }
    }
  } catch (error) {
    console.log(`❌ Stripe API error: ${error instanceof Error ? error.message : error}`);
    errors++;
  }

  console.log();

  // Check plan configurations
  console.log('📊 Validating plan configurations:');
  try {
    for (const [planId, config] of Object.entries(PLAN_CONFIGS)) {
      console.log(`  🔍 Checking ${config.name} plan:`);
      
      // Validate price
      if (config.price < 0) {
        console.log(`    ❌ Invalid price: ${config.price}`);
        errors++;
      } else {
        console.log(`    ✅ Price: $${(config.price / 100).toFixed(2)}/month`);
      }
      
      // Validate limits
      if (config.limits.repositories < 0 || config.limits.monthlyPRs < 0) {
        console.log(`    ❌ Invalid limits`);
        errors++;
      } else {
        console.log(`    ✅ Limits: ${config.limits.repositories} repos, ${config.limits.monthlyPRs} PRs`);
      }
      
      // Validate features
      if (!Array.isArray(config.features) || config.features.length === 0) {
        console.log(`    ❌ No features defined`);
        errors++;
      } else {
        console.log(`    ✅ ${config.features.length} features defined`);
      }
    }
  } catch (error) {
    console.log(`❌ Plan configuration error: ${error instanceof Error ? error.message : error}`);
    errors++;
  }

  console.log();

  // Test Stripe product sync (if API is available)
  if (process.env.STRIPE_SECRET_KEY && errors === 0) {
    console.log('🔄 Testing Stripe product sync:');
    try {
      await stripeProductManager.syncProducts();
      console.log('✅ Stripe products synchronized successfully');
      
      // Verify products were created
      const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
      const products = await stripe.products.list({ active: true, limit: 10 });
      const driftguardProducts = products.data.filter((p: any) => 
        p.name.includes('DriftGuard') || p.metadata.plan_id
      );
      
      console.log(`✅ Found ${driftguardProducts.length} DriftGuard products in Stripe`);
      
      if (driftguardProducts.length === 0) {
        console.log(`⚠️  No DriftGuard products found - this might be expected for a fresh setup`);
        warnings++;
      }
      
    } catch (error) {
      console.log(`❌ Product sync error: ${error instanceof Error ? error.message : error}`);
      errors++;
    }
  }

  console.log();

  // Summary
  console.log('📋 Validation Summary:');
  console.log(`   Errors: ${errors}`);
  console.log(`   Warnings: ${warnings}`);

  if (errors === 0 && warnings === 0) {
    console.log('\n🎉 Billing infrastructure is fully configured and ready!');
  } else if (errors === 0) {
    console.log('\n✅ Billing infrastructure is functional with minor warnings.');
  } else {
    console.log('\n❌ Billing infrastructure has critical errors that need to be resolved.');
    process.exit(1);
  }

  // Next steps
  console.log('\n📋 Next Steps:');
  console.log('   1. Set up webhook endpoint in Stripe dashboard');
  console.log('   2. Configure production environment variables');
  console.log('   3. Test payment flow with test cards');
  console.log('   4. Set up database for persistent billing data');
  console.log('   5. Configure monitoring and alerting');
}

// Run verification
if (require.main === module) {
  verifyBillingInfrastructure().catch(console.error);
}

export default verifyBillingInfrastructure;