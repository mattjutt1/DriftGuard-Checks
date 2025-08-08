# Demo Screenshots

This directory contains example screenshots showing Prompt Gate in action.

## Screenshot Collection

### PR Results Examples

- **pr-passed.png** - Shows successful evaluation with green checkmark, metrics table, and links
- **pr-failed.png** - Shows failed evaluation with red X, improvement suggestions
- **pr-skipped.png** - Shows skipped evaluation when prompt-check label is missing
- **workflow-logs.png** - Shows detailed workflow execution logs and timing

### Branch Protection Setup

- **branch-settings.png** - Shows GitHub branch protection configuration
- **status-checks.png** - Shows Prompt Gate selected as required status check
- **merge-block.png** - Shows PR blocked from merging due to failed Prompt Gate

### Workflow Results

- **actions-tab.png** - Shows Prompt Gate workflows in GitHub Actions tab
- **workflow-summary.png** - Shows workflow run summary with status and artifacts
- **artifact-download.png** - Shows downloadable artifacts with evaluation details

## How to Generate Real Screenshots

To replace these placeholders with actual screenshots:

1. **Set up a test repository** with Prompt Gate installed
2. **Create test PRs** with different prompt quality levels
3. **Capture screenshots** at key points in the workflow
4. **Replace placeholder files** with actual PNG images
5. **Update documentation** to reference real screenshots

## Placeholder Status

Currently using placeholder files to complete the demo structure.
Real screenshots will be generated when running Prompt Gate in a live environment.

## Expected Screenshot Content

### PR Comments Should Show

- ✅/❌ Status indicators
- Win rate percentage vs threshold
- Number of prompts tested
- Simulated cost calculations
- Links to detailed results and artifacts
- Professional table formatting

### Workflow Logs Should Show

- Step-by-step execution progress
- Timing information for each step
- PromptOps CLI output and results
- Artifact upload confirmation
- Final pass/fail determination

### Branch Protection Should Show

- "Require status checks to pass before merging" enabled
- "Prompt Gate" selected in required checks list
- Branch protection rule active and enforced
- Merge button blocked when checks fail
