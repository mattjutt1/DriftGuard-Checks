# Prompt Gate Quickstart - Install in 5 Minutes

Get prompt quality gates running in your GitHub repository in under 5 minutes. No API keys required - runs offline by default.

## Step 1: Copy the Workflow File

Copy the one-file installer to your repository's workflow directory:

```bash
# Create the workflows directory if it doesn't exist
mkdir -p .github/workflows

# Copy our installer
curl -o .github/workflows/prompt-gate.yml https://raw.githubusercontent.com/mattjutt1/prompt-wizard/main/examples/prompt-gate.min.yml
```

**Or manually:** Copy the contents of [`examples/prompt-gate.min.yml`](../examples/prompt-gate.min.yml) to `.github/workflows/prompt-gate.yml` in your repository.

## Step 2: Create Configuration File

Create a `.promptops.yml` file in your repository root:

```yaml
version: '1.0'
threshold: 0.80
model: 'mock'
test_prompts:
  - 'Write a function to calculate fibonacci numbers'
  - 'Explain quantum computing in simple terms'
  - 'Create a REST API for user authentication'
  - 'Generate unit tests for a shopping cart class'
```

**What this does:**

- `threshold: 0.80` - Requires 80% of prompts to pass quality checks
- `model: 'mock'` - Uses offline evaluation (no API costs)
- `test_prompts` - Your actual prompts to be evaluated

## Step 3: Commit and Push

```bash
git add .github/workflows/prompt-gate.yml .promptops.yml
git commit -m "feat: add Prompt Gate quality checks"
git push origin main
```

## Step 4: Enable Branch Protection

**Important:** The workflow job name is `prompt-gate` - you'll need this for step 5.

1. Go to your repository **Settings** → **Branches**
2. Click **Add rule** or edit existing rule for your main branch
3. Check **Restrict pushes that create files**
4. Check **Require status checks to pass before merging**
5. Search for and select: **`prompt-gate`**
6. Click **Create** or **Save changes**

![Branch Protection Setup](img/branch-protection-complete.png)

*Screenshot placeholder - Branch protection with prompt-gate status check enabled*

## Step 5: Test Your Setup

Create a test pull request:

```bash
# Create test branch
git checkout -b test/prompt-gate-setup

# Add the prompt-check label trigger
echo "Testing Prompt Gate setup" > test-gate.txt
git add test-gate.txt
git commit -m "test: verify Prompt Gate integration"
git push origin test/prompt-gate-setup

# Create PR and add label
gh pr create --title "Test: Prompt Gate Setup" --body "Testing prompt quality gates" --label "prompt-check"
```

**Expected Results:**

- ✅ Workflow runs automatically when `prompt-check` label is added
- ✅ Job Summary shows: Status, Win rate, Threshold
- ✅ PR merging blocked if prompts fail quality checks
- ✅ No API costs incurred (runs offline)

## 🎉 You're Done

Your repository now has automated prompt quality gates that:

- **Run offline** - No API keys or external costs
- **Block bad prompts** - Prevents merging low-quality changes
- **Show clear results** - Win rate and threshold in PR summaries
- **Scale automatically** - Works with any team size

## Next Steps

### Customize Your Setup

- **Adjust threshold:** Change `threshold` in `.promptops.yml` (0.70 = 70%, 0.90 = 90%)
- **Add more prompts:** Expand `test_prompts` list with your actual prompt patterns
- **Enable API providers:** Add real LLM evaluation (see [Provider Setup](install.md#llm-provider-configuration))

### Monitor Quality Trends

- **Download artifacts** - Each run saves detailed `results.json`
- **Track improvements** - Monitor win rates over time
- **Set up alerts** - Add Slack notifications (see workflow comments)

### Enterprise Features

- **Nightly drift detection** - Catch quality degradation early
- **Custom scoring** - Domain-specific evaluation criteria
- **Team dashboards** - Centralized quality metrics

---

**Need help?** Check the [full installation guide](install.md) or [open an issue](https://github.com/mattjutt1/prompt-wizard/issues).
