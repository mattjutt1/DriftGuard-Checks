#!/usr/bin/env node

// Quick script to retrigger check runs by deleting and recreating them
const { Octokit } = require('@octokit/rest');

async function main() {
  const token = process.env.GITHUB_TOKEN;
  const octokit = new Octokit({ auth: token });

  const shas = [
    'c27758bb707e4d03faeba5d875bf31e999e0cf01', // PR #12
    '0191b6f2c507afa3fb16ca7f34aa0cbdb8e8c7af'  // PR #13
  ];

  for (const sha of shas) {
    console.log(`Processing ${sha}...`);

    // Get the app's check run
    const { data } = await octokit.rest.checks.listForRef({
      owner: 'mattjutt1',
      repo: 'prompt-wizard',
      ref: sha
    });

    const appCheck = data.check_runs.find(r => r.app.slug === 'driftguard-checks-matt');
    if (appCheck) {
      // Trigger update by modifying
      await octokit.rest.checks.update({
        owner: 'mattjutt1',
        repo: 'prompt-wizard',
        check_run_id: appCheck.id,
        status: 'in_progress',
        output: {
          title: 'Re-evaluating...',
          summary: 'Checking for workflow artifacts...'
        }
      });
      console.log(`Updated check ${appCheck.id} to in_progress`);
    }
  }
}

main().catch(console.error);
