#!/usr/bin/env node

const { exec } = require('child_process');
const { promisify } = require('util');
const execAsync = promisify(exec);

async function smokeTestPR(prNumber) {
  if (!prNumber) {
    console.error('Usage: npm run smoke:pr -- <PR_NUMBER>');
    process.exit(1);
  }

  try {
    // Get PR head SHA
    const { stdout: sha } = await execAsync(`gh pr view ${prNumber} --json headRefOid -q .headRefOid`);
    const headSha = sha.trim();

    // Get repository info
    const { stdout: owner } = await execAsync('gh repo view --json owner -q .owner.login');
    const { stdout: repo } = await execAsync('gh repo view --json name -q .name');
    const ownerName = owner.trim();
    const repoName = repo.trim();

    // Get check runs for the SHA
    const { stdout: checkRunsJson } = await execAsync(
      `gh api repos/${ownerName}/${repoName}/commits/${headSha}/check-runs --jq '.check_runs[] | select(.name=="prompt-check") | {name, app: .app.slug, status, conclusion, details_url, title: .output.title}'`
    );

    if (!checkRunsJson.trim()) {
      console.log(`❌ No "prompt-check" run found for PR #${prNumber} (SHA: ${headSha.substring(0, 8)})`);
      process.exit(1);
    }

    const checkRun = JSON.parse(checkRunsJson.trim());

    console.log(`🔍 PR #${prNumber} (SHA: ${headSha.substring(0, 8)})`);
    console.log(`   Check: ${checkRun.name}`);
    console.log(`   App: ${checkRun.app}`);
    console.log(`   Status: ${checkRun.status}`);
    console.log(`   Conclusion: ${checkRun.conclusion === 'success' ? '✅ SUCCESS' : '❌ FAILURE'}`);
    console.log(`   Title: ${checkRun.title || 'N/A'}`);
    console.log(`   Details: ${checkRun.details_url || 'N/A'}`);

  } catch (error) {
    console.error(`❌ Error testing PR #${prNumber}:`, error.message);
    process.exit(1);
  }
}

// Get PR number from command line args
const prNumber = process.argv[2];
smokeTestPR(prNumber);
