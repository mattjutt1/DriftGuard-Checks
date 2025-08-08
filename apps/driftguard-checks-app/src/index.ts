import { Probot } from "probot";
import * as fs from "fs";
import * as path from "path";

interface EvaluationResult {
  threshold: number;
  metrics: {
    win_rate: number;
  };
}

interface CheckRunOptions {
  name: string;
  head_sha: string;
  status: "queued" | "in_progress" | "completed";
  conclusion?: "success" | "failure" | "neutral" | "cancelled" | "skipped" | "timed_out" | "action_required";
  output?: {
    title: string;
    summary: string;
  };
}

export default (app: Probot) => {
  app.on("pull_request.opened", async (context) => {
    await handlePullRequest(context);
  });

  app.on("pull_request.synchronize", async (context) => {
    await handlePullRequest(context);
  });

  app.on("check_suite.requested", async (context) => {
    await handleCheckSuite(context);
  });

  async function handlePullRequest(context: any) {
    const { pull_request } = context.payload;
    const headSha = pull_request.head.sha;

    context.log.info(`Processing PR #${pull_request.number} with head SHA: ${headSha}`);

    await createOrUpdateCheckRun(context, headSha);
  }

  async function handleCheckSuite(context: any) {
    const { check_suite } = context.payload;
    const headSha = check_suite.head_sha;

    context.log.info(`Processing check suite for SHA: ${headSha}`);

    await createOrUpdateCheckRun(context, headSha);
  }

  async function createOrUpdateCheckRun(context: any, headSha: string) {
    // Create initial "in_progress" check run
    const checkRun = await context.octokit.checks.create({
      owner: context.payload.repository.owner.login,
      repo: context.payload.repository.name,
      name: "prompt-check",
      head_sha: headSha,
      status: "in_progress",
      output: {
        title: "Prompt Gate Evaluation",
        summary: "🔄 Evaluating prompt quality..."
      }
    });

    try {
      // Try to get evaluation result
      const result = await getEvaluationResult(context, headSha);

      // Determine conclusion
      const passed = result.metrics.win_rate >= result.threshold;
      const conclusion = passed ? "success" : "failure";

      // Create summary
      const summary = createSummary(result, passed);

      // Update check run with results
      await context.octokit.checks.update({
        owner: context.payload.repository.owner.login,
        repo: context.payload.repository.name,
        check_run_id: checkRun.data.id,
        status: "completed",
        conclusion: conclusion,
        output: {
          title: passed ? "✅ Prompt Gate Passed" : "❌ Prompt Gate Failed",
          summary: summary
        }
      });

      context.log.info(`Check run completed with conclusion: ${conclusion}`);

    } catch (error) {
      context.log.error("Error processing check run:", error);

      // Update check run with error
      await context.octokit.checks.update({
        owner: context.payload.repository.owner.login,
        repo: context.payload.repository.name,
        check_run_id: checkRun.data.id,
        status: "completed",
        conclusion: "failure",
        output: {
          title: "❌ Prompt Gate Error",
          summary: `Error processing prompt evaluation: ${error.message}`
        }
      });
    }
  }

  async function getEvaluationResult(context: any, headSha: string): Promise<EvaluationResult> {
    // First, try to get results from artifacts
    try {
      const artifactResult = await getResultsFromArtifact(context, headSha);
      if (artifactResult) {
        context.log.info("Found results from workflow artifact");
        return artifactResult;
      }
    } catch (error) {
      context.log.info("No artifact found, falling back to stub mode");
    }

    // Fallback to stub mode evaluation
    return runStubEvaluation();
  }

  async function getResultsFromArtifact(context: any, headSha: string): Promise<EvaluationResult | null> {
    // Get workflow runs for this SHA
    const workflowRuns = await context.octokit.actions.listWorkflowRunsForRepo({
      owner: context.payload.repository.owner.login,
      repo: context.payload.repository.name,
      head_sha: headSha,
      per_page: 10
    });

    for (const run of workflowRuns.data.workflow_runs) {
      try {
        // Get artifacts for this run
        const artifacts = await context.octokit.actions.listWorkflowRunArtifacts({
          owner: context.payload.repository.owner.login,
          repo: context.payload.repository.name,
          run_id: run.id
        });

        // Look for prompt-evaluation-results artifact
        const resultArtifact = artifacts.data.artifacts.find(
          (artifact: any) => artifact.name === "prompt-evaluation-results"
        );

        if (resultArtifact) {
          // Download and parse artifact
          const download = await context.octokit.actions.downloadArtifact({
            owner: context.payload.repository.owner.login,
            repo: context.payload.repository.name,
            artifact_id: resultArtifact.id,
            archive_format: "zip"
          });

          // Note: In a real implementation, you'd need to extract the ZIP and parse results.json
          // For now, we'll return a mock result indicating artifact was found
          context.log.info("Found artifact but ZIP extraction not implemented");
          return null;
        }
      } catch (error) {
        context.log.debug(`Error checking artifacts for run ${run.id}:`, error.message);
      }
    }

    return null;
  }

  function runStubEvaluation(): EvaluationResult {
    // Simulate evaluation in stub mode (matches the workflow stub behavior)
    return {
      threshold: 0.85,
      metrics: {
        win_rate: 0.6667 // 66.67% - matches the stub win rate from workflows
      }
    };
  }

  function createSummary(result: EvaluationResult, passed: boolean): string {
    const statusEmoji = passed ? "✅" : "❌";
    const status = passed ? "PASS" : "FAIL";

    return `### Prompt Gate Results

- **Status:** ${statusEmoji} ${status}
- **Win rate:** ${(result.metrics.win_rate * 100).toFixed(2)}%
- **Threshold:** ${result.threshold.toFixed(2)}

${passed
  ? "🎉 Prompt quality meets the required threshold. Ready to merge!"
  : "⚠️ Prompt quality below threshold. Please improve prompts before merging."
}`;
  }
};
