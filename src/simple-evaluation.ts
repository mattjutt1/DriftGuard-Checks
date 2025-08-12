// SIMPLE EVALUATION - NO OVER-ENGINEERING
// Just 3 checks that actually matter to users

export function evaluatePrompt(content: string) {
  // Check 1: Not empty or too short
  const notEmpty = content && content.trim().length > 10;
  
  // Check 2: Not ridiculously long
  const notTooLong = content.length < 5000;
  
  // Check 3: No obvious secrets
  const noSecrets = !(/api[_-]?key|password|secret|token|bearer/i.test(content));
  
  // That's it. Pass or fail.
  const pass = notEmpty && notTooLong && noSecrets;
  
  // Simple message
  let message = 'Prompt evaluation complete';
  if (!notEmpty) message = '❌ Prompt too short (min 10 characters)';
  else if (!notTooLong) message = '❌ Prompt too long (max 5000 characters)';
  else if (!noSecrets) message = '❌ Potential secrets detected';
  else message = '✅ Prompt looks good';
  
  return {
    pass,
    message,
    details: {
      length: content.length,
      checks: {
        not_empty: notEmpty,
        not_too_long: notTooLong,
        no_secrets: noSecrets
      }
    }
  };
}

// Hook into existing app - ADD THIS TO index.ts
export function addEvaluationToApp(app: any) {
  app.on('pull_request.opened', async (context: any) => {
    const { pull_request } = context.payload;
    
    // Get PR description as "prompt" to evaluate
    const prompt = pull_request.body || '';
    
    // Run simple evaluation
    const result = evaluatePrompt(prompt);
    
    // Create check run with actual result
    await context.octokit.checks.create({
      owner: context.repo().owner,
      repo: context.repo().repo,
      name: 'DriftGuard Check',
      head_sha: pull_request.head.sha,
      status: 'completed',
      conclusion: result.pass ? 'success' : 'failure',
      output: {
        title: result.pass ? '✅ Prompt Check Passed' : '❌ Prompt Check Failed',
        summary: result.message,
        text: `
**Prompt Length:** ${result.details.length} characters

**Checks:**
- Not empty: ${result.details.checks.not_empty ? '✅' : '❌'}
- Not too long: ${result.details.checks.not_too_long ? '✅' : '❌'}  
- No secrets: ${result.details.checks.no_secrets ? '✅' : '❌'}

---
*DriftGuard - Simple, reliable prompt checks for GitHub*
        `.trim()
      }
    });
    
    console.log(`Check created: ${result.pass ? 'PASS' : 'FAIL'}`);
  });
}