# Branch Protection Setup for Prompt Gate

Complete step-by-step guide to enable required status checks for prompt quality gates.

## Prerequisites

- Prompt Gate workflow installed (see [Quickstart](quickstart.md))
- Admin access to your GitHub repository
- At least one workflow run completed (creates the status check)

## Step-by-Step Setup

### 1. Navigate to Repository Settings

1. Go to your GitHub repository
2. Click the **Settings** tab (requires admin access)
3. In the left sidebar, click **Branches**

![Navigation to Branch Settings](img/branch-protection-nav.png)

### 2. Create or Edit Branch Protection Rule

**For new protection:**

1. Click **Add rule** button
2. Enter your branch name pattern (usually `main` or `master`)

**For existing protection:**

1. Find your main branch rule
2. Click **Edit** button

### 3. Configure Status Check Requirements

1. Check ✅ **Require status checks to pass before merging**
2. Check ✅ **Require branches to be up to date before merging** (recommended)

### 4. Select Prompt Gate Status Check

**⚠️ Critical:** The status check name must match your workflow job name exactly.

1. In the search box under "Status checks found in the last week", type: **`prompt-gate`**
2. Select **✅ prompt-gate** from the dropdown
3. If not found, trigger a workflow run first, then return to this step

![Status Check Selection](img/status-check-selection.png)

### 5. Save Configuration

1. Scroll to bottom of page
2. Click **Create** (new rule) or **Save changes** (existing rule)

![Complete Branch Protection](img/branch-protection-complete.png)

## Job Name Requirements

**🎯 Keep job names unique across all workflows**

The status check system identifies jobs by their `name` field. If multiple workflows use the same job name, GitHub cannot distinguish between them.

### ✅ Good Practice

```yaml
jobs:
  prompt-gate:          # Unique job name
    name: Prompt Gate   # Display name
```

### ❌ Avoid Conflicts

```yaml
jobs:
  test:                 # Generic name - could conflict
    name: Test Suite

  # Another workflow
  test:                 # Same name - creates ambiguity
    name: E2E Tests
```

### Common Job Names Used

If you have existing workflows, avoid these common names:

- `test`, `tests`, `testing`
- `build`, `ci`, `deploy`
- `lint`, `check`, `validate`

**Recommendation:** Use descriptive, specific job names like:

- `prompt-gate` ✅
- `prompt-quality-check` ✅
- `ai-prompt-validation` ✅

## Verification

After setup, test the protection:

### Create Test PR

```bash
# Create branch with failing prompts
git checkout -b test/branch-protection
echo "Write code" > test-prompts.txt  # Low quality prompt
git add . && git commit -m "test: verify branch protection blocks bad prompts"
git push origin test/branch-protection

# Create PR with prompt-check label
gh pr create --title "Test: Branch Protection" --body "Should be blocked by prompt gate" --label "prompt-check"
```

### Expected Behavior

1. **✅ Workflow runs** - Prompt evaluation executes
2. **❌ Status check fails** - Low-quality prompts don't meet threshold
3. **🚫 Merge blocked** - GitHub prevents merging until checks pass
4. **📊 Results visible** - Job Summary shows win rate and threshold

### Troubleshooting

**Status check not appearing?**

- Ensure at least one workflow run completed
- Check job name spelling: must be exactly `prompt-gate`
- Verify workflow file is in `.github/workflows/` directory

**Multiple status checks with same name?**

- Review all workflow files for duplicate job names
- Rename conflicting jobs to be unique
- Wait for new runs to register updated names

**Protection not enforcing?**

- Verify "Require status checks" is checked ✅
- Confirm `prompt-gate` is selected in status checks list
- Test with a PR that has the `prompt-check` label

## Advanced Configuration

### Additional Protection Options

**Recommended settings:**

- ✅ **Require status checks to pass before merging**
- ✅ **Require branches to be up to date before merging**
- ✅ **Include administrators** (applies rules to admins too)

**Optional settings:**

- **Restrict pushes that create files** (prevents direct pushes)
- **Allow force pushes** (generally not recommended)
- **Allow deletions** (based on your team workflow)

### Multiple Status Checks

You can require multiple checks:

```yaml
# In addition to prompt-gate
- tests          # Unit tests
- build          # Build verification
- security-scan  # Security scanning
```

This creates a comprehensive quality gate combining prompt quality with code quality checks.

---

**Need help?** See the [Installation Guide](install.md) or [open an issue](https://github.com/mattjutt1/prompt-wizard/issues).
