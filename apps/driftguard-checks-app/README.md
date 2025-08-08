# DriftGuard Checks App

A GitHub App that creates check runs for prompt evaluation on pull requests.

## Overview

This Probot-based GitHub App automatically creates "prompt-check" check runs on pull requests, providing rich feedback about prompt quality directly in the GitHub UI. It integrates with existing prompt evaluation workflows and can run in offline mode.

## Features

- ✅ Creates check runs named "prompt-check" on PRs
- 📊 Reads results from workflow artifacts when available
- 🔄 Falls back to stub mode evaluation when no artifacts found
- 📝 Rich markdown summaries with win rates and thresholds
- 🛡️ Offline-first design with no external API calls

## Setup

### 1. Create GitHub App

1. Go to your GitHub organization settings
2. Navigate to "Developer settings" > "GitHub Apps"
3. Click "New GitHub App"
4. Configure the app with these settings:

**Basic Information:**

- **Name:** DriftGuard Checks (or your preferred name)
- **Description:** Automated prompt quality evaluation
- **Homepage URL:** `https://your-organization.com` (optional)
- **Webhook URL:** `https://your-server.com/webhooks` (your deployment URL)

**Permissions:**

- **Checks:** Read & write
- **Contents:** Read
- **Metadata:** Read
- **Pull requests:** Read

**Subscribe to events:**

- [x] Pull request
- [x] Check suite

### 2. Install Dependencies

```bash
cd apps/driftguard-checks-app
npm install
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your GitHub App credentials:

```env
APP_ID=123456
PRIVATE_KEY="-----BEGIN PRIVATE KEY-----
...your private key content here...
-----END PRIVATE KEY-----"
WEBHOOK_SECRET=your_webhook_secret
```

### 4. Development

Run the app in development mode:

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### 5. Build for Production

```bash
npm run build
npm start
```

## How It Works

### Event Flow

1. **Pull Request Event:** When a PR is opened or updated, the app receives a webhook
2. **Artifact Check:** App looks for `prompt-evaluation-results` artifacts from recent workflow runs
3. **Evaluation:** If artifacts found, uses those results; otherwise runs stub evaluation
4. **Check Run:** Creates/updates a "prompt-check" check run with results

### Integration with Workflows

The app integrates with existing GitHub Actions workflows that:

- Run prompt evaluation (using promptops library)
- Upload `results.json` as artifacts named `prompt-evaluation-results`
- Use the same evaluation logic and thresholds

### Stub Mode

When no workflow artifacts are available, the app runs in stub mode:

- Uses default threshold of 0.85
- Simulates win rate of 66.67%
- Provides consistent behavior for testing

## Deployment

### Using Docker

```bash
# Build image
docker build -t driftguard-checks-app .

# Run container
docker run -d \
  --name driftguard-checks \
  -p 3000:3000 \
  --env-file .env \
  driftguard-checks-app
```

### Using Cloud Platforms

The app can be deployed to:

- **Heroku:** Add the GitHub buildpack and configure environment variables
- **Vercel:** Deploy as a serverless function
- **Railway:** Connect your GitHub repo and configure environment variables
- **DigitalOcean App Platform:** Deploy directly from GitHub

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `APP_ID` | GitHub App ID | Yes |
| `PRIVATE_KEY` | GitHub App private key (PEM format) | Yes |
| `WEBHOOK_SECRET` | Webhook secret from GitHub App | Yes |
| `GITHUB_URL` | GitHub Enterprise URL (leave empty for GitHub.com) | No |
| `LOG_LEVEL` | Logging level (trace, debug, info, warn, error) | No |
| `PORT` | Webhook server port (default: 3000) | No |

## Development

### Project Structure

```
src/
  index.ts          # Main app logic and event handlers
package.json        # Dependencies and scripts
tsconfig.json       # TypeScript configuration
.env.example        # Environment template
```

### Key Components

- **Event Handlers:** Process `pull_request` and `check_suite` events
- **Artifact Fetcher:** Downloads results from workflow run artifacts
- **Stub Evaluator:** Provides fallback evaluation when no artifacts available
- **Check Run Manager:** Creates and updates GitHub check runs

### Testing

```bash
# Run tests
npm test

# Run with coverage
npm run test:coverage
```

## Troubleshooting

### Common Issues

**Check runs not appearing:**

- Verify GitHub App has `checks:write` permission
- Check webhook URL is accessible from GitHub
- Review app logs for webhook delivery failures

**Artifact not found:**

- Ensure workflow uploads artifacts named `prompt-evaluation-results`
- Check artifact retention policy (GitHub deletes after 90 days by default)
- Verify workflow runs completed successfully

**Authentication errors:**

- Validate APP_ID matches your GitHub App
- Ensure PRIVATE_KEY is in correct PEM format with proper line breaks
- Check WEBHOOK_SECRET matches GitHub App configuration

### Debugging

Enable debug logging:

```bash
LOG_LEVEL=debug npm run dev
```

View detailed logs including:

- Webhook payloads
- API requests/responses
- Artifact fetching attempts
- Evaluation results

## License

MIT
