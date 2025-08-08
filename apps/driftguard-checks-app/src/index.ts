import { Probot } from 'probot';
import {
  getErrorMessage,
  createCheckRun,
  updateCheckRun,
  listCheckRunsForRef,
  getLatestEvaluation,
  EvaluationResult
} from './github';

/**
 * DriftGuard Checks App
 *
 * This GitHub App creates and updates "prompt-check" check runs based on
 * evaluation results from GitHub Actions artifacts.
 *
 * Required permissions:
 * - Checks: read & write
 * - Actions: read
 * - Pull requests: read
 * - Contents: read
 * - Metadata: read
 *
 * Subscribed events:
 * - pull_request
 * - workflow_run
 */

function formatSummary(
  evaluation: EvaluationResult | null,
  runUrl: string | null,
  error?: string
): string {
  if (error) {
    return `## ❌ Evaluation Error\n\n${error}\n\n**Action Required:** Check the [workflow configuration](${runUrl || '#'}) and ensure the evaluation completes successfully.`;
  }

  if (!evaluation) {
    return `## ⚠️ Missing Evaluation Artifact\n\n**Issue:** No \`prompt-evaluation-results\` artifact found.\n\n**Solutions:**\n1. Ensure workflow completed successfully\n2. Verify artifact upload in workflow\n3. Check [workflow logs](${runUrl || '#'}) for errors\n\n**Artifact name expected:** \`prompt-evaluation-results\`\n**File expected:** \`results.json\``;
  }

  const passed = evaluation.win_rate >= evaluation.threshold;
  const emoji = passed ? '✅' : '❌';
  const status = passed ? 'PASSED' : 'FAILED';

  return `## ${emoji} Prompt Gate ${status}

**Win Rate:** ${(evaluation.win_rate * 100).toFixed(1)}%
**Threshold:** ${(evaluation.threshold * 100).toFixed(1)}%
**Result:** ${passed ? 'Meets requirements' : 'Below threshold'}

${runUrl ? `[View workflow run →](${runUrl})` : ''}`;
}

export = (app: Probot) => {
  // Track active check runs to avoid duplicates
  const activeCheckRuns = new Map<string, number>();

  /**
   * Handle pull_request.opened and pull_request.synchronize events
   * Creates an in-progress check run, then updates it with evaluation results
   */
  app.on(['pull_request.opened', 'pull_request.synchronize'], async (context) => {
    const { pull_request } = context.payload;
    const { owner, repo } = context.repo();
    const head_sha = pull_request.head.sha;

    let checkRunId: number | undefined;
    const checkKey = `${owner}/${repo}/${head_sha}`;

    try {
      // Create initial in-progress check run
      console.log(`Creating check run for PR #${pull_request.number} (${head_sha})`);

      checkRunId = await createCheckRun(context.octokit, owner, repo, {
        name: 'prompt-check',
        head_sha,
        status: 'in_progress',
        output: {
          title: 'Evaluating prompts...',
          summary: 'Waiting for evaluation results from GitHub Actions.'
        }
      });

      activeCheckRuns.set(checkKey, checkRunId);
      console.log(`Created check run ${checkRunId}`);

      // Wait a bit for Actions to start
      await new Promise(resolve => setTimeout(resolve, 3000));

      // Get latest evaluation
      const { evaluation, runUrl } = await getLatestEvaluation(
        context.octokit,
        owner,
        repo,
        head_sha
      );

      // Determine conclusion
      let conclusion: 'success' | 'failure';
      let title: string;
      let summary: string;

      if (!evaluation) {
        conclusion = 'failure';
        title = 'ERROR / MISSING_ARTIFACT';
        summary = formatSummary(null, runUrl);
      } else {
        const passed = evaluation.win_rate >= evaluation.threshold;
        conclusion = passed ? 'success' : 'failure';
        title = passed
          ? `✅ Prompt Gate Passed (${(evaluation.win_rate * 100).toFixed(1)}%)`
          : `❌ Prompt Gate Failed (${(evaluation.win_rate * 100).toFixed(1)}%)`;
        summary = formatSummary(evaluation, runUrl);
      }

      // Update check run with results
      await updateCheckRun(context.octokit, owner, repo, checkRunId, {
        status: 'completed',
        conclusion,
        details_url: runUrl || undefined,
        output: {
          title,
          summary
        }
      });

      console.log(`Updated check run ${checkRunId} with conclusion: ${conclusion}`);

    } catch (error) {
      const errorMsg = getErrorMessage(error);
      console.error(`Error processing PR event: ${errorMsg}`);

      // If we have a check run ID, update it to failure
      if (checkRunId) {
        try {
          await updateCheckRun(context.octokit, owner, repo, checkRunId, {
            status: 'completed',
            conclusion: 'failure',
            output: {
              title: 'ERROR / PROCESSING_FAILED',
              summary: formatSummary(null, null, `Failed to process evaluation: ${errorMsg}`)
            }
          });
        } catch (updateError) {
          console.error(`Failed to update check run: ${getErrorMessage(updateError)}`);
        }
      }
    } finally {
      if (checkRunId) {
        activeCheckRuns.delete(checkKey);
      }
    }
  });

  /**
   * Handle workflow_run.completed events
   * Updates existing check runs when new evaluation results are available
   */
  app.on('workflow_run.completed', async (context) => {
    const { workflow_run } = context.payload;
    const { owner, repo } = context.repo();

    // Only process runs from the same repo
    if (workflow_run.repository.full_name !== `${owner}/${repo}`) {
      return;
    }

    // Only process if this looks like a PR workflow
    if (!workflow_run.head_branch || workflow_run.head_branch === 'main') {
      return;
    }

    const head_sha = workflow_run.head_sha;
    const checkKey = `${owner}/${repo}/${head_sha}`;

    // Skip if we're already processing this SHA
    if (activeCheckRuns.has(checkKey)) {
      console.log(`Skipping workflow_run for ${head_sha} - already processing`);
      return;
    }

    try {
      console.log(`Processing workflow_run.completed for ${head_sha}`);

      // Check if there's an existing check run for this SHA
      const existingRuns = await listCheckRunsForRef(context.octokit, owner, repo, head_sha);

      if (existingRuns.length === 0) {
        console.log(`No existing check runs for ${head_sha}, skipping`);
        return;
      }

      const checkRun = existingRuns[0];

      // Get latest evaluation
      const { evaluation, runUrl } = await getLatestEvaluation(
        context.octokit,
        owner,
        repo,
        head_sha
      );

      // Determine conclusion
      let conclusion: 'success' | 'failure';
      let title: string;
      let summary: string;

      if (!evaluation) {
        conclusion = 'failure';
        title = 'ERROR / MISSING_ARTIFACT';
        summary = formatSummary(null, runUrl);
      } else {
        const passed = evaluation.win_rate >= evaluation.threshold;
        conclusion = passed ? 'success' : 'failure';
        title = passed
          ? `✅ Prompt Gate Passed (${(evaluation.win_rate * 100).toFixed(1)}%)`
          : `❌ Prompt Gate Failed (${(evaluation.win_rate * 100).toFixed(1)}%)`;
        summary = formatSummary(evaluation, runUrl);
      }

      // Update check run with results
      await updateCheckRun(context.octokit, owner, repo, checkRun.id, {
        status: 'completed',
        conclusion,
        details_url: runUrl || undefined,
        output: {
          title,
          summary
        }
      });

      console.log(`Updated check run ${checkRun.id} from workflow_run with conclusion: ${conclusion}`);

    } catch (error) {
      console.error(`Error processing workflow_run event: ${getErrorMessage(error)}`);
    }
  });

  // Log app startup
  app.on('installation.created', async (context) => {
    console.log('App installed!', context.payload.installation);
  });

  console.log('🚀 DriftGuard Checks app started');
  console.log('Port:', process.env.PORT || 3001);
  console.log('Webhook URL:', process.env.WEBHOOK_PROXY_URL || 'Not configured');
};
