# 🔧 DriftGuard Evaluation Engine: Technical Implementation Guide

## Critical Missing Component Analysis

### Current State (What's Built)
```typescript
// Current: Creates empty check runs with no evaluation
app.on(['pull_request.opened', 'pull_request.synchronize'], async (context) => {
  const check = await context.octokit.checks.create({
    name: 'DriftGuard Evaluation',
    head_sha: pull_request.head.sha,
    status: 'completed',
    conclusion: 'success', // Always passes - NO EVALUATION!
    output: {
      title: 'Check Complete',
      summary: 'No actual evaluation performed' // THIS IS THE PROBLEM
    }
  });
});
```

### Required State (What's Needed)
```typescript
// Required: Actual evaluation with meaningful results
app.on(['workflow_run.completed'], async (context) => {
  // 1. Fetch workflow artifacts containing prompts
  const artifacts = await fetchWorkflowArtifacts(context);
  
  // 2. Parse and extract prompt content
  const prompts = await parsePromptArtifacts(artifacts);
  
  // 3. Run evaluation engine
  const evaluation = await evaluatePrompts(prompts);
  
  // 4. Create detailed check run with results
  const check = await createDetailedCheckRun(context, evaluation);
  
  // 5. Store results for analytics
  await storeEvaluationMetrics(evaluation);
});
```

---

## 📋 IMPLEMENTATION PLAN

### Step 1: Create Core Evaluation Module

**File:** `/apps/driftguard-checks-app/src/evaluation/engine.ts`

```typescript
import { z } from 'zod';

// Validation schemas
const PromptSchema = z.object({
  content: z.string().min(1).max(10000),
  metadata: z.object({
    file: z.string(),
    line: z.number().optional(),
    type: z.enum(['system', 'user', 'assistant']).optional()
  }).optional()
});

export interface EvaluationResult {
  overall_pass: boolean;
  score: number; // 0-100
  metrics: {
    clarity: number;
    completeness: number;
    specificity: number;
    safety: number;
    best_practices: number;
  };
  issues: Issue[];
  suggestions: string[];
  drift_analysis?: DriftAnalysis;
}

interface Issue {
  severity: 'error' | 'warning' | 'info';
  category: string;
  message: string;
  line?: number;
  suggestion?: string;
}

interface DriftAnalysis {
  has_baseline: boolean;
  drift_percentage?: number;
  breaking_changes?: boolean;
  changed_elements?: string[];
}

// Main evaluation function
export async function evaluatePrompt(
  content: string,
  baseline?: string
): Promise<EvaluationResult> {
  const issues: Issue[] = [];
  const suggestions: string[] = [];
  
  // 1. CLARITY EVALUATION (0-100)
  const clarity = evaluateClarity(content, issues, suggestions);
  
  // 2. COMPLETENESS CHECK (0-100)
  const completeness = evaluateCompleteness(content, issues, suggestions);
  
  // 3. SPECIFICITY ANALYSIS (0-100)
  const specificity = evaluateSpecificity(content, issues, suggestions);
  
  // 4. SAFETY & SECURITY SCAN (0-100)
  const safety = evaluateSafety(content, issues, suggestions);
  
  // 5. BEST PRACTICES COMPLIANCE (0-100)
  const bestPractices = evaluateBestPractices(content, issues, suggestions);
  
  // 6. DRIFT DETECTION (if baseline provided)
  const driftAnalysis = baseline ? 
    analyzeDrift(content, baseline) : undefined;
  
  // Calculate overall score
  const score = Math.round(
    (clarity * 0.2) +
    (completeness * 0.25) +
    (specificity * 0.2) +
    (safety * 0.2) +
    (bestPractices * 0.15)
  );
  
  // Determine pass/fail (configurable threshold)
  const threshold = process.env.PASS_THRESHOLD || 70;
  const overall_pass = score >= threshold && 
    !issues.some(i => i.severity === 'error');
  
  return {
    overall_pass,
    score,
    metrics: {
      clarity,
      completeness,
      specificity,
      safety,
      best_practices: bestPractices
    },
    issues,
    suggestions,
    drift_analysis: driftAnalysis
  };
}

// CLARITY EVALUATION
function evaluateClarity(
  content: string, 
  issues: Issue[], 
  suggestions: string[]
): number {
  let score = 100;
  
  // Check for ambiguous language
  const ambiguousWords = [
    'maybe', 'perhaps', 'might', 'could', 'possibly',
    'sometimes', 'usually', 'often', 'rarely'
  ];
  
  const foundAmbiguous = ambiguousWords.filter(word => 
    content.toLowerCase().includes(word)
  );
  
  if (foundAmbiguous.length > 0) {
    score -= foundAmbiguous.length * 5;
    issues.push({
      severity: 'warning',
      category: 'clarity',
      message: `Ambiguous language detected: ${foundAmbiguous.join(', ')}`,
      suggestion: 'Use more definitive language for clearer instructions'
    });
  }
  
  // Check sentence complexity (average words per sentence)
  const sentences = content.split(/[.!?]+/).filter(s => s.trim());
  const avgWordsPerSentence = sentences.reduce((acc, s) => 
    acc + s.trim().split(/\s+/).length, 0) / sentences.length;
  
  if (avgWordsPerSentence > 25) {
    score -= 10;
    issues.push({
      severity: 'warning',
      category: 'clarity',
      message: 'Complex sentences detected (avg > 25 words)',
      suggestion: 'Break down complex sentences for better readability'
    });
  }
  
  // Check for clear structure markers
  const hasStructure = /#{1,6}\s|^\d+\.|^[-*]\s/m.test(content);
  if (!hasStructure && content.length > 200) {
    score -= 10;
    suggestions.push('Consider adding headers or bullet points for better structure');
  }
  
  return Math.max(0, score);
}

// COMPLETENESS EVALUATION
function evaluateCompleteness(
  content: string,
  issues: Issue[],
  suggestions: string[]
): number {
  let score = 100;
  const required = [];
  
  // Check for context/background
  if (!/(context|background|scenario|given)/i.test(content)) {
    score -= 20;
    required.push('context or background information');
  }
  
  // Check for clear instructions
  if (!/(instruct|direct|command|task|should|must|will)/i.test(content)) {
    score -= 20;
    required.push('clear instructions or directives');
  }
  
  // Check for output format specification
  if (!/(format|output|return|response|result|provide)/i.test(content)) {
    score -= 15;
    required.push('output format specification');
  }
  
  // Check for examples (recommended for complex prompts)
  if (content.length > 500 && !/(example|e\.g\.|for instance|such as)/i.test(content)) {
    score -= 10;
    suggestions.push('Consider adding examples for complex instructions');
  }
  
  if (required.length > 0) {
    issues.push({
      severity: score < 50 ? 'error' : 'warning',
      category: 'completeness',
      message: `Missing required elements: ${required.join(', ')}`,
      suggestion: 'Add missing elements for a complete prompt'
    });
  }
  
  return Math.max(0, score);
}

// SPECIFICITY EVALUATION
function evaluateSpecificity(
  content: string,
  issues: Issue[],
  suggestions: string[]
): number {
  let score = 100;
  
  // Check for vague terms
  const vagueTerms = [
    'thing', 'stuff', 'something', 'whatever',
    'etc', 'and so on', 'and more'
  ];
  
  const foundVague = vagueTerms.filter(term =>
    new RegExp(`\\b${term}\\b`, 'i').test(content)
  );
  
  if (foundVague.length > 0) {
    score -= foundVague.length * 8;
    issues.push({
      severity: 'warning',
      category: 'specificity',
      message: `Vague terms detected: ${foundVague.join(', ')}`,
      suggestion: 'Replace vague terms with specific descriptions'
    });
  }
  
  // Check for quantifiable metrics
  if (content.length > 200 && !/\d+/.test(content)) {
    score -= 10;
    suggestions.push('Consider adding specific numbers, metrics, or thresholds');
  }
  
  // Check for open-ended instructions
  if (/(anything|everything|all|whatever you think)/i.test(content)) {
    score -= 15;
    issues.push({
      severity: 'warning',
      category: 'specificity',
      message: 'Open-ended instructions detected',
      suggestion: 'Provide specific boundaries and constraints'
    });
  }
  
  return Math.max(0, score);
}

// SAFETY EVALUATION
function evaluateSafety(
  content: string,
  issues: Issue[],
  suggestions: string[]
): number {
  let score = 100;
  
  // Check for potential secrets/credentials
  const secretPatterns = [
    /api[_-]?key/i,
    /password/i,
    /secret/i,
    /token/i,
    /bearer/i,
    /private[_-]?key/i,
    /ssh[_-]?key/i
  ];
  
  const detectedSecrets = secretPatterns.filter(pattern =>
    pattern.test(content)
  );
  
  if (detectedSecrets.length > 0) {
    score -= 30;
    issues.push({
      severity: 'error',
      category: 'safety',
      message: 'Potential secrets or credentials detected',
      suggestion: 'Never include actual credentials in prompts. Use placeholders instead.'
    });
  }
  
  // Check for PII
  const piiPatterns = [
    /\b\d{3}-\d{2}-\d{4}\b/, // SSN
    /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/, // Email
    /\b\d{3}[-.]?\d{3}[-.]?\d{4}\b/, // Phone
    /\b\d{16}\b/ // Credit card
  ];
  
  const detectedPII = piiPatterns.filter(pattern =>
    pattern.test(content)
  );
  
  if (detectedPII.length > 0) {
    score -= 20;
    issues.push({
      severity: 'warning',
      category: 'safety',
      message: 'Potential PII detected',
      suggestion: 'Use example data instead of real personal information'
    });
  }
  
  // Check for harmful instructions
  const harmfulKeywords = [
    'hack', 'exploit', 'bypass security', 'crack',
    'illegal', 'malicious', 'virus', 'malware'
  ];
  
  const detectedHarmful = harmfulKeywords.filter(keyword =>
    new RegExp(`\\b${keyword}\\b`, 'i').test(content)
  );
  
  if (detectedHarmful.length > 0) {
    score -= 25;
    issues.push({
      severity: 'error',
      category: 'safety',
      message: `Potentially harmful content detected: ${detectedHarmful.join(', ')}`,
      suggestion: 'Remove or rephrase potentially harmful instructions'
    });
  }
  
  return Math.max(0, score);
}

// BEST PRACTICES EVALUATION
function evaluateBestPractices(
  content: string,
  issues: Issue[],
  suggestions: string[]
): number {
  let score = 100;
  
  // Check prompt length
  if (content.length < 50) {
    score -= 20;
    issues.push({
      severity: 'warning',
      category: 'best_practices',
      message: 'Prompt too short (< 50 characters)',
      suggestion: 'Provide more context and detail for better results'
    });
  } else if (content.length > 4000) {
    score -= 15;
    issues.push({
      severity: 'warning',
      category: 'best_practices',
      message: 'Prompt too long (> 4000 characters)',
      suggestion: 'Consider breaking into smaller, focused prompts'
    });
  }
  
  // Check for role definition
  if (!/(you are|act as|role|persona|behave|function as)/i.test(content)) {
    score -= 10;
    suggestions.push('Consider defining a role or persona for better context');
  }
  
  // Check for success criteria
  if (!/(success|complete|done|finish|achieve|accomplish)/i.test(content)) {
    score -= 10;
    suggestions.push('Define clear success criteria or completion conditions');
  }
  
  // Check for constraints
  if (!/(must not|should not|avoid|don't|cannot|limit)/i.test(content)) {
    score -= 5;
    suggestions.push('Consider adding constraints or limitations');
  }
  
  return Math.max(0, score);
}

// DRIFT DETECTION
function analyzeDrift(current: string, baseline: string): DriftAnalysis {
  const currentLines = current.split('\n');
  const baselineLines = baseline.split('\n');
  
  // Calculate similarity
  const commonLines = currentLines.filter(line =>
    baselineLines.includes(line)
  ).length;
  
  const similarity = (commonLines * 2) / 
    (currentLines.length + baselineLines.length);
  
  const driftPercentage = Math.round((1 - similarity) * 100);
  
  // Detect breaking changes (significant structural differences)
  const breakingChanges = driftPercentage > 50 ||
    Math.abs(currentLines.length - baselineLines.length) > 
    baselineLines.length * 0.5;
  
  // Find changed elements
  const changedElements = currentLines
    .filter(line => !baselineLines.includes(line))
    .slice(0, 5); // Limit to 5 for readability
  
  return {
    has_baseline: true,
    drift_percentage: driftPercentage,
    breaking_changes: breakingChanges,
    changed_elements: changedElements
  };
}
```

---

## Step 2: Artifact Fetching & Parsing

**File:** `/apps/driftguard-checks-app/src/evaluation/artifacts.ts`

```typescript
import { Context } from 'probot';
import * as unzipper from 'unzipper';
import { Readable } from 'stream';

export interface PromptArtifact {
  name: string;
  content: string;
  metadata: {
    workflow_run_id: number;
    artifact_id: number;
    created_at: string;
  };
}

export async function fetchWorkflowArtifacts(
  context: Context,
  workflowRunId: number
): Promise<PromptArtifact[]> {
  try {
    // List artifacts for the workflow run
    const { data: artifacts } = await context.octokit.actions.listWorkflowRunArtifacts({
      owner: context.repo().owner,
      repo: context.repo().repo,
      run_id: workflowRunId
    });
    
    const promptArtifacts: PromptArtifact[] = [];
    
    // Filter for prompt-related artifacts
    const relevantArtifacts = artifacts.artifacts.filter(a =>
      a.name.includes('prompt') || 
      a.name.includes('evaluation') ||
      a.name.includes('drift')
    );
    
    for (const artifact of relevantArtifacts) {
      try {
        // Download artifact
        const download = await context.octokit.actions.downloadArtifact({
          owner: context.repo().owner,
          repo: context.repo().repo,
          artifact_id: artifact.id,
          archive_format: 'zip'
        });
        
        // Parse zip content
        const contents = await parseZipArtifact(download.data as Buffer);
        
        for (const file of contents) {
          promptArtifacts.push({
            name: file.name,
            content: file.content,
            metadata: {
              workflow_run_id: workflowRunId,
              artifact_id: artifact.id,
              created_at: artifact.created_at
            }
          });
        }
      } catch (error) {
        console.error(`Failed to process artifact ${artifact.id}:`, error);
      }
    }
    
    return promptArtifacts;
  } catch (error) {
    console.error('Failed to fetch workflow artifacts:', error);
    return [];
  }
}

async function parseZipArtifact(
  buffer: Buffer
): Promise<{ name: string; content: string }[]> {
  const files: { name: string; content: string }[] = [];
  
  return new Promise((resolve, reject) => {
    const stream = Readable.from(buffer);
    
    stream
      .pipe(unzipper.Parse())
      .on('entry', async (entry: any) => {
        const fileName = entry.path;
        const type = entry.type;
        
        if (type === 'File' && 
            (fileName.endsWith('.txt') || 
             fileName.endsWith('.md') || 
             fileName.endsWith('.json'))) {
          try {
            const content = await streamToString(entry);
            files.push({ name: fileName, content });
          } catch (error) {
            console.error(`Failed to read ${fileName}:`, error);
          }
        } else {
          entry.autodrain();
        }
      })
      .on('finish', () => resolve(files))
      .on('error', reject);
  });
}

function streamToString(stream: any): Promise<string> {
  const chunks: Buffer[] = [];
  return new Promise((resolve, reject) => {
    stream.on('data', (chunk: Buffer) => chunks.push(chunk));
    stream.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')));
    stream.on('error', reject);
  });
}

export function parsePromptContent(artifacts: PromptArtifact[]): string[] {
  const prompts: string[] = [];
  
  for (const artifact of artifacts) {
    // Try to parse as JSON first
    try {
      const json = JSON.parse(artifact.content);
      if (json.prompt) {
        prompts.push(json.prompt);
      } else if (json.prompts && Array.isArray(json.prompts)) {
        prompts.push(...json.prompts);
      }
    } catch {
      // If not JSON, treat as plain text
      if (artifact.content.trim()) {
        prompts.push(artifact.content.trim());
      }
    }
  }
  
  return prompts;
}
```

---

## Step 3: GitHub Check Run Integration

**File:** `/apps/driftguard-checks-app/src/evaluation/checkrun.ts`

```typescript
import { Context } from 'probot';
import { EvaluationResult } from './engine';

export async function createDetailedCheckRun(
  context: Context,
  evaluation: EvaluationResult,
  sha: string
): Promise<void> {
  const conclusion = evaluation.overall_pass ? 'success' : 'failure';
  const emoji = evaluation.overall_pass ? '✅' : '❌';
  
  // Build summary
  const summary = buildSummary(evaluation);
  
  // Build detailed text
  const text = buildDetailedText(evaluation);
  
  // Build annotations for inline feedback
  const annotations = buildAnnotations(evaluation);
  
  await context.octokit.checks.create({
    owner: context.repo().owner,
    repo: context.repo().repo,
    name: 'DriftGuard Prompt Evaluation',
    head_sha: sha,
    status: 'completed',
    conclusion,
    output: {
      title: `${emoji} Prompt Evaluation: ${evaluation.overall_pass ? 'Passed' : 'Failed'}`,
      summary,
      text,
      annotations
    }
  });
}

function buildSummary(evaluation: EvaluationResult): string {
  const { score, metrics, overall_pass } = evaluation;
  
  return `
## Overall Score: ${score}/100 ${overall_pass ? '✅' : '❌'}

### Metrics Breakdown
| Metric | Score | Status |
|--------|-------|--------|
| Clarity | ${metrics.clarity}/100 | ${getStatusEmoji(metrics.clarity)} |
| Completeness | ${metrics.completeness}/100 | ${getStatusEmoji(metrics.completeness)} |
| Specificity | ${metrics.specificity}/100 | ${getStatusEmoji(metrics.specificity)} |
| Safety | ${metrics.safety}/100 | ${getStatusEmoji(metrics.safety)} |
| Best Practices | ${metrics.best_practices}/100 | ${getStatusEmoji(metrics.best_practices)} |

### Issues Found: ${evaluation.issues.length}
- 🔴 Errors: ${evaluation.issues.filter(i => i.severity === 'error').length}
- 🟡 Warnings: ${evaluation.issues.filter(i => i.severity === 'warning').length}
- 🔵 Info: ${evaluation.issues.filter(i => i.severity === 'info').length}

${evaluation.drift_analysis ? buildDriftSummary(evaluation.drift_analysis) : ''}
  `.trim();
}

function buildDetailedText(evaluation: EvaluationResult): string {
  let text = '## Detailed Analysis\n\n';
  
  // Issues section
  if (evaluation.issues.length > 0) {
    text += '### Issues\n\n';
    for (const issue of evaluation.issues) {
      const icon = issue.severity === 'error' ? '🔴' :
                   issue.severity === 'warning' ? '🟡' : '🔵';
      text += `${icon} **${issue.category}**: ${issue.message}\n`;
      if (issue.suggestion) {
        text += `   💡 *Suggestion: ${issue.suggestion}*\n`;
      }
      text += '\n';
    }
  }
  
  // Suggestions section
  if (evaluation.suggestions.length > 0) {
    text += '### Improvement Suggestions\n\n';
    for (const suggestion of evaluation.suggestions) {
      text += `- ${suggestion}\n`;
    }
    text += '\n';
  }
  
  // Best practices tips
  text += '### Best Practices Tips\n\n';
  text += '1. **Be Specific**: Use concrete examples and clear boundaries\n';
  text += '2. **Provide Context**: Include background information and goals\n';
  text += '3. **Define Format**: Specify the expected output structure\n';
  text += '4. **Set Constraints**: Define what should NOT be done\n';
  text += '5. **Include Examples**: Show desired input/output patterns\n';
  
  return text;
}

function buildAnnotations(evaluation: EvaluationResult): any[] {
  const annotations: any[] = [];
  
  for (const issue of evaluation.issues) {
    if (issue.line) {
      annotations.push({
        path: 'prompt.md', // This would be dynamic based on actual file
        start_line: issue.line,
        end_line: issue.line,
        annotation_level: issue.severity === 'error' ? 'failure' :
                         issue.severity === 'warning' ? 'warning' : 'notice',
        message: issue.message,
        title: issue.category
      });
    }
  }
  
  return annotations;
}

function getStatusEmoji(score: number): string {
  if (score >= 80) return '✅';
  if (score >= 60) return '⚠️';
  return '❌';
}

function buildDriftSummary(drift: any): string {
  if (!drift.has_baseline) return '';
  
  return `
### Drift Analysis
- **Drift Percentage**: ${drift.drift_percentage}%
- **Breaking Changes**: ${drift.breaking_changes ? 'Yes ⚠️' : 'No ✅'}
${drift.changed_elements?.length > 0 ? 
  `- **Changed Elements**: \n${drift.changed_elements.map(e => `  - ${e}`).join('\n')}` : ''}
  `;
}
```

---

## Step 4: Wire Everything Together

**File:** `/apps/driftguard-checks-app/src/index-evaluation.ts`

```typescript
import { Probot } from 'probot';
import { evaluatePrompt } from './evaluation/engine';
import { fetchWorkflowArtifacts, parsePromptContent } from './evaluation/artifacts';
import { createDetailedCheckRun } from './evaluation/checkrun';

export = (app: Probot) => {
  // Listen for workflow completions
  app.on('workflow_run.completed', async (context) => {
    const { workflow_run } = context.payload;
    
    // Only process if workflow contains prompt evaluation
    if (!workflow_run.name?.toLowerCase().includes('prompt') &&
        !workflow_run.name?.toLowerCase().includes('drift')) {
      return;
    }
    
    console.log(`Processing workflow run ${workflow_run.id}`);
    
    try {
      // Fetch artifacts
      const artifacts = await fetchWorkflowArtifacts(context, workflow_run.id);
      
      if (artifacts.length === 0) {
        console.log('No prompt artifacts found');
        return;
      }
      
      // Parse prompts
      const prompts = parsePromptContent(artifacts);
      
      if (prompts.length === 0) {
        console.log('No prompts found in artifacts');
        return;
      }
      
      // Evaluate each prompt
      const evaluations = await Promise.all(
        prompts.map(prompt => evaluatePrompt(prompt))
      );
      
      // Aggregate results
      const overallEvaluation = aggregateEvaluations(evaluations);
      
      // Create check run with results
      await createDetailedCheckRun(
        context,
        overallEvaluation,
        workflow_run.head_sha
      );
      
      console.log(`Created check run for ${workflow_run.id}`);
      
    } catch (error) {
      console.error('Failed to process workflow run:', error);
      
      // Create failure check run
      await context.octokit.checks.create({
        owner: context.repo().owner,
        repo: context.repo().repo,
        name: 'DriftGuard Prompt Evaluation',
        head_sha: workflow_run.head_sha,
        status: 'completed',
        conclusion: 'failure',
        output: {
          title: '❌ Evaluation Failed',
          summary: 'Failed to evaluate prompts',
          text: `Error: ${error.message}`
        }
      });
    }
  });
  
  // Also listen for check suite requests
  app.on('check_suite.requested', async (context) => {
    const { check_suite } = context.payload;
    
    // Create in-progress check
    const check = await context.octokit.checks.create({
      owner: context.repo().owner,
      repo: context.repo().repo,
      name: 'DriftGuard Prompt Evaluation',
      head_sha: check_suite.head_sha,
      status: 'in_progress',
      output: {
        title: 'Evaluating Prompts...',
        summary: 'Waiting for workflow artifacts'
      }
    });
    
    console.log(`Created pending check ${check.data.id}`);
  });
};

function aggregateEvaluations(evaluations: any[]): any {
  if (evaluations.length === 1) {
    return evaluations[0];
  }
  
  // Average scores across multiple prompts
  const avgScore = evaluations.reduce((sum, e) => sum + e.score, 0) / evaluations.length;
  const allIssues = evaluations.flatMap(e => e.issues);
  const allSuggestions = [...new Set(evaluations.flatMap(e => e.suggestions))];
  
  return {
    overall_pass: evaluations.every(e => e.overall_pass),
    score: Math.round(avgScore),
    metrics: {
      clarity: Math.round(evaluations.reduce((sum, e) => 
        sum + e.metrics.clarity, 0) / evaluations.length),
      completeness: Math.round(evaluations.reduce((sum, e) => 
        sum + e.metrics.completeness, 0) / evaluations.length),
      specificity: Math.round(evaluations.reduce((sum, e) => 
        sum + e.metrics.specificity, 0) / evaluations.length),
      safety: Math.round(evaluations.reduce((sum, e) => 
        sum + e.metrics.safety, 0) / evaluations.length),
      best_practices: Math.round(evaluations.reduce((sum, e) => 
        sum + e.metrics.best_practices, 0) / evaluations.length)
    },
    issues: allIssues,
    suggestions: allSuggestions
  };
}
```

---

## 🚀 DEPLOYMENT STEPS

### 1. Install Dependencies
```bash
cd apps/driftguard-checks-app
npm install zod
```

### 2. Build & Test
```bash
npm run build
npm run test
npm run smoke:pr -- 12
```

### 3. Commit Changes
```bash
git add -A
git commit -m "feat: Add comprehensive prompt evaluation engine

- Clarity, completeness, specificity, safety, best practices evaluation
- Drift detection and comparison to baseline
- Detailed GitHub check runs with actionable feedback
- Artifact fetching and parsing from workflow runs
- Scoring system with configurable pass/fail thresholds"
```

### 4. Deploy to Production
```bash
git push origin main

# Deploy to Render.com
# The webhook will trigger automatic deployment
```

---

## 📊 EXPECTED RESULTS

### Example Check Run Output
```markdown
✅ Prompt Evaluation: Passed

## Overall Score: 85/100 ✅

### Metrics Breakdown
| Metric | Score | Status |
|--------|-------|--------|
| Clarity | 90/100 | ✅ |
| Completeness | 85/100 | ✅ |
| Specificity | 80/100 | ✅ |
| Safety | 100/100 | ✅ |
| Best Practices | 70/100 | ⚠️ |

### Issues Found: 3
- 🔴 Errors: 0
- 🟡 Warnings: 2
- 🔵 Info: 1

## Detailed Analysis

### Issues

🟡 **clarity**: Ambiguous language detected: usually, might
   💡 *Suggestion: Use more definitive language for clearer instructions*

🟡 **best_practices**: Prompt too long (> 4000 characters)
   💡 *Suggestion: Consider breaking into smaller, focused prompts*

🔵 **completeness**: Consider adding examples for complex instructions

### Improvement Suggestions
- Consider defining a role or persona for better context
- Add specific numbers, metrics, or thresholds
```

---

## 🎯 VALUE DELIVERED TO USERS

1. **Immediate Feedback**: Know if prompts meet quality standards
2. **Actionable Insights**: Specific suggestions for improvement
3. **Drift Prevention**: Catch breaking changes before merge
4. **Team Consistency**: Standardized evaluation criteria
5. **Time Savings**: Eliminate manual review bottleneck

**This evaluation engine transforms DriftGuard from an empty shell to a valuable tool that solves real problems!**