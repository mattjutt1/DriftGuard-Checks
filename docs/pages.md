# Enabling GitHub Pages

## Quick Setup

1. Go to your repository Settings
2. Scroll down to **Pages** section
3. Under **Source**, select:
   - Branch: `main`
   - Folder: `/site`
4. Click **Save**

Your site will be available at:

```text
https://[username].github.io/[repository]/
```

## Using GitHub CLI (if available)

```bash
gh api \
  -X PUT \
  repos/:owner/:repo/pages \
  -f source.branch=main \
  -f source.path=/site
```

## Verification

After enabling, check deployment status:

```bash
gh api repos/:owner/:repo/pages
```

The site typically takes 2-5 minutes to deploy after first enable.
