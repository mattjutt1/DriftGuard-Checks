#!/usr/bin/env node

/**
 * Smoke test for DriftGuard Checks App
 * 
 * Usage: PR_NUMBER=12 npm run smoke
 * 
 * This script:
 * 1. Resolves PR number from PR_NUMBER env
 * 2. Lists check-runs for the PR head SHA
 * 3. Logs the most recent prompt-check's status/conclusion
 */

const { Octokit } = require('@octokit/rest');
const fs = require('fs');
const path = require('path');

async function main() {
  // Get PR number from environment
  const prNumber = process.env.PR_NUMBER;
  if (!prNumber) {
    console.error('❌ PR_NUMBER environment variable is required');
    console.error('Usage: PR_NUMBER=12 npm run smoke');
    process.exit(1);
  }

  // Get GitHub token from environment or .env file
  let token = process.env.GITHUB_TOKEN;
  
  if (!token) {
    // Try to read from .env file
    const envPath = path.join(__dirname, '..', '.env');
    if (fs.existsSync(envPath)) {
      const envContent = fs.readFileSync(envPath, 'utf8');
      const match = envContent.match(/GITHUB_TOKEN=(.+)/);
      if (match) {
        token = match[1].trim();
      }
    }
  }

  if (!token) {
    console.error('❌ GITHUB_TOKEN not found in environment or .env file');
    console.error('Please set GITHUB_TOKEN or add it to .env file');
    process.exit(1);
  }

  const octokit = new Octokit({ auth: token });

  try {
    console.log(`\n🔍 Checking PR #${prNumber}...\n`);

    // Get PR details
    const { data: pr } = await octokit.rest.pulls.get({
      owner: 'mattjutt1',
      repo: 'prompt-wizard',
      pull_number: parseInt(prNumber)
    });

    const headSha = pr.head.sha;
    console.log(`📍 Head SHA: ${headSha}`);
    console.log(`🌿 Branch: ${pr.head.ref}`);
    console.log(`📝 Title: ${pr.title}\n`);

    // List check runs for the head SHA
    const { data: checkRuns } = await octokit.rest.checks.listForRef({
      owner: 'mattjutt1',
      repo: 'prompt-wizard',
      ref: headSha
    });

    // Find prompt-check runs
    const promptChecks = checkRuns.check_runs.filter(run => run.name === 'prompt-check');

    if (promptChecks.length === 0) {
      console.log('⚠️  No prompt-check runs found for this PR');
      console.log('\nAll check runs:');
      checkRuns.check_runs.forEach(run => {
        console.log(`  - ${run.name}: ${run.status} / ${run.conclusion || 'N/A'}`);
      });
    } else {
      console.log(`✅ Found ${promptChecks.length} prompt-check run(s)\n`);

      // Get the most recent prompt-check
      const latestCheck = promptChecks[0];
      
      console.log('📊 Latest prompt-check:');
      console.log(`  ID: ${latestCheck.id}`);
      console.log(`  Status: ${latestCheck.status}`);
      console.log(`  Conclusion: ${latestCheck.conclusion || 'N/A'}`);
      console.log(`  Created: ${new Date(latestCheck.created_at).toLocaleString()}`);
      
      if (latestCheck.completed_at) {
        console.log(`  Completed: ${new Date(latestCheck.completed_at).toLocaleString()}`);
      }
      
      if (latestCheck.details_url) {
        console.log(`  Details: ${latestCheck.details_url}`);
      }
      
      if (latestCheck.output) {
        console.log(`\n📄 Output:`);
        console.log(`  Title: ${latestCheck.output.title}`);
        if (latestCheck.output.summary) {
          console.log(`  Summary Preview: ${latestCheck.output.summary.substring(0, 200)}...`);
        }
      }

      // Show conclusion emoji
      console.log('\n🎯 Result:');
      switch (latestCheck.conclusion) {
        case 'success':
          console.log('  ✅ PASSED - Check succeeded');
          break;
        case 'failure':
          console.log('  ❌ FAILED - Check failed');
          break;
        case 'neutral':
          console.log('  ⚪ NEUTRAL - Check was neutral');
          break;
        case null:
        case undefined:
          console.log('  ⏳ IN PROGRESS - Check is still running');
          break;
        default:
          console.log(`  ❓ ${latestCheck.conclusion.toUpperCase()}`);
      }

      // Show other check runs for context
      if (checkRuns.check_runs.length > 1) {
        console.log('\n📋 Other check runs:');
        checkRuns.check_runs
          .filter(run => run.name !== 'prompt-check')
          .forEach(run => {
            console.log(`  - ${run.name}: ${run.status} / ${run.conclusion || 'N/A'}`);
          });
      }
    }

    // Show PR URL
    console.log(`\n🔗 PR URL: ${pr.html_url}`);
    console.log(`🔗 Checks: ${pr.html_url}/checks`);

  } catch (error) {
    console.error('❌ Error:', error.message);
    if (error.status === 404) {
      console.error('   PR not found. Check the PR number and repository.');
    } else if (error.status === 401) {
      console.error('   Authentication failed. Check your GITHUB_TOKEN.');
    }
    process.exit(1);
  }
}

// Run the smoke test
main().catch(console.error);