# Uninstall Guide - Prompt Gate for GitHub

## Complete Removal

Follow these steps to completely remove Prompt Gate from your repository.

### Step 1: Remove Workflow File

Delete the workflow file from your repository:

```bash
rm .github/workflows/prompt-gate.yml
```

If this was your only workflow file, you can also remove the entire workflows directory:

```bash
# Only if no other workflows exist
rmdir .github/workflows
rmdir .github  # Only if .github directory is now empty
```

### Step 2: Remove Configuration File

Delete the PromptOps configuration file:

```bash
rm .promptops.yml
```

### Step 3: Remove Branch Protection Rule

To remove the Prompt Gate requirement from branch protection:

1. Go to your repository on GitHub
2. Click **Settings** → **Branches**
3. Click **Edit** on your branch protection rule
4. Uncheck **"Require status checks to pass before merging"** OR
5. Remove **"Prompt Gate"** from the required status checks list
6. Click **Save changes**

### Step 4: Clean Up Labels (Optional)

If you no longer need the `prompt-check` label:

1. Go to **Issues** → **Labels** in your repository
2. Find the `prompt-check` label
3. Click **Delete** to remove it

### Step 5: Remove Repository Secrets (Optional)

If you added any Prompt Gate-related secrets:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Delete these secrets if they exist:
   - `SLACK_WEBHOOK_URL`
   - `ALLOW_NETWORK`
   - `OPENAI_API_KEY` (only if used solely for Prompt Gate)
   - `ANTHROPIC_API_KEY` (only if used solely for Prompt Gate)

## Commit the Changes

After removing the files, commit the changes:

```bash
git add -A  # Stage all deletions
git commit -m "remove: uninstall Prompt Gate workflow and configuration"
git push
```

## Verification

To verify complete removal:

1. **Check Actions tab**: No new "Prompt Gate" workflows should appear on future PRs
2. **Check branch protection**: PRs should merge without requiring Prompt Gate checks
3. **Check repository files**: No `.promptops.yml` or `prompt-gate.yml` files should remain

## Partial Removal Options

### Keep Files, Disable Temporarily

To temporarily disable without removing files:

1. **Rename the workflow**:

   ```bash
   mv .github/workflows/prompt-gate.yml .github/workflows/prompt-gate.yml.disabled
   ```

2. **Or add a condition to skip**:

   ```yaml
   # Add to the top of your workflow file
   if: false  # This disables the entire workflow
   ```

### Remove Only Branch Protection

To keep the workflow but make it optional:

1. Go to **Settings** → **Branches** → **Edit** rule
2. Uncheck **"Require status checks to pass before merging"**
3. Keep the workflow - it will still run and comment, but won't block merges

### Remove Only Auto-Trigger

To run Prompt Gate only manually:

1. Edit `.github/workflows/prompt-gate.yml`
2. Remove the `pull_request:` trigger section
3. Keep only `workflow_dispatch:` for manual runs

## Alternative: Archive Instead of Delete

If you want to keep the configuration for potential future use:

```bash
# Create an archive directory
mkdir archive

# Move files instead of deleting
mv .github/workflows/prompt-gate.yml archive/
mv .promptops.yml archive/

# Commit the archival
git add archive/
git add -A  # Stage the deletions from original locations
git commit -m "archive: move Prompt Gate configuration to archive/"
git push
```

## Troubleshooting Removal

### Workflow Still Running

If the workflow continues to run after deletion:

1. Check you deleted the correct file: `.github/workflows/prompt-gate.yml`
2. Verify the commit was pushed to the correct branch
3. Wait 5-10 minutes for GitHub to process the change

### Status Check Still Required

If GitHub still requires the "Prompt Gate" check:

1. Go to **Settings** → **Branches**
2. Edit your branch protection rule
3. Look for "Prompt Gate" in the status checks list
4. Click the **X** to remove it
5. Save changes

### Old PR Comments Remain

This is normal - existing PR comments from Prompt Gate will remain in the history, but no new comments will be added to future PRs.

## Re-installation

If you want to reinstall Prompt Gate later:

1. Follow the [installation guide](install.md)
2. If you archived files, you can restore them:

   ```bash
   mv archive/prompt-gate.yml .github/workflows/
   mv archive/.promptops.yml .
   ```

## Support

If you encounter issues during removal:

1. Check that you have **Write** permissions to the repository
2. Verify you're working on the correct branch (usually `main` or `master`)
3. Ensure all changes are committed and pushed
4. For persistent issues, open an issue in the [prompt-wizard repository](https://github.com/mattjutt1/prompt-wizard/issues)

---

**✅ Removal Complete**

Your repository should now be completely free of Prompt Gate components. Future pull requests will not trigger prompt evaluations.
