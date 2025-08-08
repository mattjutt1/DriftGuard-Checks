# Installation Guide - Prompt Gate for GitHub

## Overview

Prompt Gate is a GitHub Actions workflow that evaluates prompt quality in pull requests. It runs **offline by default** with no API costs, making it safe to use in any repository.

## Quick Install (Copy & Paste)

### Step 1: Copy the Workflow File

1. Create the workflow directory in your repository:

   ```bash
   mkdir -p .github/workflows
   ```

2. Copy the workflow file from [examples/prompt-gate.min.yml](../examples/prompt-gate.min.yml) to `.github/workflows/prompt-gate.yml` in your repository.

### Step 2: Create Configuration File

Create a `.promptops.yml` file in your repository root:

```yaml
version: '1.0'
threshold: 0.80
model: 'mock'
test_prompts:
  - 'Write a function to calculate fibonacci numbers'
  - 'Explain quantum computing in simple terms'
  - 'Create a REST API for user authentication'
  - 'Design a responsive navigation component'
```

### Step 3: Set Up Branch Protection (Required)

To make Prompt Gate **required** for merging PRs, you need to enable branch protection rules:

#### 3.1 Navigate to Branch Protection Settings

1. Go to your repository on GitHub
2. Click **Settings** (repository settings, not your profile)
3. Click **Branches** in the left sidebar
4. Click **Add rule** (or edit existing rule for your default branch)

![Branch protection navigation](img/branch-protection-nav.png)

#### 3.2 Configure Protection Rule

1. **Branch name pattern**: Enter your default branch (usually `main` or `master`)
2. **Protect matching branches**: Check this box
3. **Require status checks to pass before merging**: ✅ **Check this box**
4. **Require branches to be up to date before merging**: ✅ Recommended

![Branch protection basic settings](img/branch-protection-basic.png)

#### 3.3 Add Prompt Gate Status Check

1. In the **Status checks** section, you'll see a search box
2. Type **"Prompt Gate"** (this is the exact name of our workflow job)
3. Click on **"Prompt Gate"** when it appears in the dropdown
4. The check should now appear as **"Required"**

![Status check selection](img/status-check-selection.png)

**Important**: The status check name **"Prompt Gate"** will only appear in the dropdown after the workflow has run at least once on a PR.

#### 3.4 Save Protection Rule

1. Scroll to the bottom and click **Create** (or **Save changes** if editing)
2. Your branch is now protected and requires Prompt Gate to pass before merging

![Branch protection complete](img/branch-protection-complete.png)

### Step 4: Test the Setup

1. Create a test branch and make a change:

   ```bash
   git checkout -b test-prompt-gate
   echo "# Test file" > test.md
   git add test.md
   git commit -m "test: add test file for prompt gate"
   git push -u origin test-prompt-gate
   ```

2. Open a pull request and add the `prompt-check` label
3. The Prompt Gate workflow should run and post results as a comment
4. Try merging - GitHub should require the Prompt Gate check to pass

## Configuration Options

### Environment Variables

The workflow supports these environment variables (set in repository secrets):

```yaml
env:
  # Core offline mode (default)
  PROMPTOPS_MODE: stub              # Use stub implementations
  DISABLE_NETWORK: 1                # Block external network access

  # Optional: Enable real providers (not recommended for CI)
  # ALLOW_NETWORK: 1
  # OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  # ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

### Workflow Triggers

The workflow runs on:

- **Pull requests**: When opened, synchronized, or labeled
- **Manual dispatch**: You can trigger it manually from the Actions tab

### Label-Based Control

- Add the `prompt-check` label to a PR to run the evaluation
- Remove the label to skip evaluation on subsequent pushes
- The workflow comments on PRs with evaluation results

## Advanced Configuration

### Custom Threshold

Edit your `.promptops.yml` to change the pass/fail threshold:

```yaml
version: '1.0'
threshold: 0.85  # 85% win rate required to pass
model: 'mock'
test_prompts:
  - 'Your custom test prompts here'
```

### Custom Test Prompts

Add your own test prompts relevant to your project:

```yaml
version: '1.0'
threshold: 0.80
model: 'mock'
test_prompts:
  - 'Generate unit tests for a React component'
  - 'Write API documentation for a REST endpoint'
  - 'Create error handling for async operations'
```

### Slack Notifications (Optional)

To enable Slack notifications when Prompt Gate fails:

1. Create a Slack webhook URL in your workspace
2. Add it to repository secrets as `SLACK_WEBHOOK_URL`
3. Add `ALLOW_NETWORK: 1` to repository secrets
4. The workflow will automatically post notifications on failures

## Troubleshooting

### Status Check Not Appearing

If "Prompt Gate" doesn't appear in the status checks dropdown:

1. Make sure the workflow has run at least once on any PR
2. Check the workflow name in your `.github/workflows/prompt-gate.yml` matches exactly
3. The job name should be `prompt-gate` (with hyphen, not underscore)

### Workflow Not Running

Common issues:

1. **Missing label**: Add the `prompt-check` label to your PR
2. **Wrong file location**: Workflow must be in `.github/workflows/`
3. **YAML syntax errors**: Check your YAML formatting
4. **Missing config**: Ensure `.promptops.yml` exists in repository root

### Permission Errors

If you see permission errors:

1. Go to **Settings → Actions → General**
2. Under **Workflow permissions**, select **Read and write permissions**
3. Check **Allow GitHub Actions to create and approve pull requests**

## Cost and Security

### Zero API Costs

- Runs completely offline by default
- Uses mock/stub implementations
- No external API calls = no costs incurred
- Safe to run in any repository

### Security Features

- No secrets required for basic operation
- Offline-first architecture prevents accidental API usage
- Repository secrets only used when explicitly enabled
- Network access disabled by default

## Support

For issues or questions:

1. Check the [troubleshooting section](#troubleshooting) above
2. Review workflow logs in the Actions tab
3. Open an issue in the [prompt-wizard repository](https://github.com/mattjutt1/prompt-wizard/issues)

## Next Steps

After successful installation:

1. **Customize prompts**: Edit `.promptops.yml` with prompts relevant to your project
2. **Set team threshold**: Adjust the pass/fail threshold based on your quality standards
3. **Monitor results**: Review PR comments to understand prompt quality trends
4. **Branch protection**: Ensure Prompt Gate is required for all merges

Your repository now has automated prompt quality gates! 🎉
