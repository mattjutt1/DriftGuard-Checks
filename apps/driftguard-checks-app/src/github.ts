// Using 'any' for octokit type to avoid Probot/Octokit type conflicts
type OctokitInstance = any;
import * as unzipper from 'unzipper';
import { Readable } from 'stream';

// Helper to safely extract error messages
export function getErrorMessage(e: unknown): string {
  if (e instanceof Error) return e.message;
  if (typeof e === 'string') return e;
  if (e && typeof e === 'object' && 'message' in e) return String(e.message);
  return 'Unknown error';
}

// Artifact result type
export interface EvaluationResult {
  win_rate: number;
  threshold: number;
  metrics?: {
    win_rate: number;
  };
}

// Check run data
export interface CheckRunData {
  id?: number;
  name: string;
  head_sha: string;
  status: 'queued' | 'in_progress' | 'completed';
  conclusion?: 'success' | 'failure' | 'neutral' | 'cancelled' | 'skipped' | 'timed_out' | 'action_required';
  details_url?: string;
  output?: {
    title: string;
    summary: string;
  };
}

// Helper to add timeout to promises
async function withTimeout<T>(promise: Promise<T>, timeoutMs: number): Promise<T> {
  const timeout = new Promise<never>((_, reject) =>
    setTimeout(() => reject(new Error(`Operation timed out after ${timeoutMs}ms`)), timeoutMs)
  );
  return Promise.race([promise, timeout]);
}

// Helper for retry with exponential backoff
async function retryOnce<T>(fn: () => Promise<T>, delayMs: number = 2000): Promise<T> {
  try {
    return await fn();
  } catch (error: unknown) {
    const errorMsg = getErrorMessage(error);
    
    // Only retry on rate limit or 5xx errors
    if (errorMsg.includes('rate limit') || errorMsg.includes('500') || errorMsg.includes('502') || errorMsg.includes('503')) {
      console.log(`Retrying after ${delayMs}ms due to: ${errorMsg}`);
      await new Promise(resolve => setTimeout(resolve, delayMs));
      return fn();
    }
    throw error;
  }
}

/**
 * List workflow runs for a specific head SHA
 * REST API: GET /repos/{owner}/{repo}/actions/runs
 */
export async function listWorkflowRunsByHeadSha(
  octokit: OctokitInstance,
  owner: string,
  repo: string,
  head_sha: string
): Promise<any[]> {
  const fn = async () => {
    const response: any = await withTimeout(
      octokit.rest.actions.listWorkflowRunsForRepo({
        owner,
        repo,
        head_sha,
        per_page: 10,
        status: 'completed'
      }),
      10000
    );
    return response.data.workflow_runs;
  };
  
  return retryOnce(fn);
}

/**
 * List artifacts for a workflow run
 * REST API: GET /repos/{owner}/{repo}/actions/runs/{run_id}/artifacts
 */
export async function listArtifactsForRun(
  octokit: OctokitInstance,
  owner: string,
  repo: string,
  run_id: number
): Promise<any[]> {
  const fn = async () => {
    const response: any = await withTimeout(
      octokit.rest.actions.listWorkflowRunArtifacts({
        owner,
        repo,
        run_id,
        per_page: 100
      }),
      10000
    );
    return response.data.artifacts;
  };
  
  return retryOnce(fn);
}

/**
 * Download an artifact and extract results.json from memory
 * REST API: GET /repos/{owner}/{repo}/actions/artifacts/{artifact_id}/{archive_format}
 */
export async function downloadArtifactAndExtractResults(
  octokit: OctokitInstance,
  owner: string,
  repo: string,
  artifact_id: number
): Promise<EvaluationResult | null> {
  const fn = async () => {
    // Download artifact as zip
    const response: any = await withTimeout(
      octokit.rest.actions.downloadArtifact({
        owner,
        repo,
        artifact_id,
        archive_format: 'zip'
      }),
      10000
    );
    
    // Convert ArrayBuffer to Buffer for Node.js
    const buffer = Buffer.from(response.data as ArrayBuffer);
    
    // Create a readable stream from the buffer
    const stream = Readable.from(buffer);
    
    // Extract results.json from zip in memory
    return new Promise<EvaluationResult | null>((resolve, reject) => {
      let foundResults = false;
      
      stream
        .pipe(unzipper.Parse())
        .on('entry', async (entry: any) => {
          if (entry.path === 'results.json' && entry.type === 'File') {
            try {
              const content = await entry.buffer();
              const results = JSON.parse(content.toString());
              foundResults = true;
              
              // Handle both direct and nested win_rate
              const evaluation: EvaluationResult = {
                win_rate: results.win_rate ?? results.metrics?.win_rate ?? 0,
                threshold: results.threshold ?? 0.85,
                metrics: results.metrics
              };
              
              resolve(evaluation);
            } catch (err) {
              reject(new Error(`Failed to parse results.json: ${getErrorMessage(err)}`));
            }
          } else {
            entry.autodrain();
          }
        })
        .on('error', (err: any) => {
          reject(new Error(`Failed to extract artifact: ${getErrorMessage(err)}`));
        })
        .on('finish', () => {
          if (!foundResults) {
            resolve(null);
          }
        });
    });
  };
  
  return retryOnce(fn);
}

/**
 * Create a check run
 * REST API: POST /repos/{owner}/{repo}/check-runs
 */
export async function createCheckRun(
  octokit: OctokitInstance,
  owner: string,
  repo: string,
  data: CheckRunData
): Promise<number> {
  const fn = async () => {
    const response: any = await withTimeout(
      octokit.rest.checks.create({
        owner,
        repo,
        ...data
      }),
      10000
    );
    return response.data.id;
  };
  
  return retryOnce(fn);
}

/**
 * Update a check run
 * REST API: PATCH /repos/{owner}/{repo}/check-runs/{check_run_id}
 */
export async function updateCheckRun(
  octokit: OctokitInstance,
  owner: string,
  repo: string,
  check_run_id: number,
  data: Partial<CheckRunData>
): Promise<void> {
  const fn = async () => {
    await withTimeout(
      octokit.rest.checks.update({
        owner,
        repo,
        check_run_id,
        ...data
      }),
      10000
    );
  };
  
  return retryOnce(fn);
}

/**
 * List check runs for a specific ref
 * REST API: GET /repos/{owner}/{repo}/commits/{ref}/check-runs
 */
export async function listCheckRunsForRef(
  octokit: OctokitInstance,
  owner: string,
  repo: string,
  ref: string
): Promise<any[]> {
  const fn = async () => {
    const response: any = await withTimeout(
      octokit.rest.checks.listForRef({
        owner,
        repo,
        ref,
        check_name: 'prompt-check',
        per_page: 10
      }),
      10000
    );
    return response.data.check_runs;
  };
  
  return retryOnce(fn);
}

/**
 * Get the latest evaluation from Actions artifacts
 */
export async function getLatestEvaluation(
  octokit: OctokitInstance,
  owner: string,
  repo: string,
  head_sha: string
): Promise<{ evaluation: EvaluationResult | null; runId: number | null; runUrl: string | null }> {
  try {
    // Get workflow runs for this SHA
    const runs = await listWorkflowRunsByHeadSha(octokit, owner, repo, head_sha);
    
    if (runs.length === 0) {
      return { evaluation: null, runId: null, runUrl: null };
    }
    
    // Try runs in order (most recent first)
    for (const run of runs) {
      if (run.status !== 'completed') continue;
      
      try {
        // Get artifacts for this run
        const artifacts = await listArtifactsForRun(octokit, owner, repo, run.id);
        
        // Find the evaluation artifact
        const evalArtifact = artifacts.find(a => a.name === 'prompt-evaluation-results');
        
        if (evalArtifact) {
          // Download and extract results
          const evaluation = await downloadArtifactAndExtractResults(
            octokit,
            owner,
            repo,
            evalArtifact.id
          );
          
          if (evaluation) {
            return {
              evaluation,
              runId: run.id,
              runUrl: run.html_url
            };
          }
        }
      } catch (err) {
        console.error(`Failed to process run ${run.id}: ${getErrorMessage(err)}`);
        // Continue to next run
      }
    }
    
    return { evaluation: null, runId: null, runUrl: null };
  } catch (error) {
    console.error(`Failed to get latest evaluation: ${getErrorMessage(error)}`);
    throw error;
  }
}