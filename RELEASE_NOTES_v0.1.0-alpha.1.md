# 🚀 Prompt Gate for GitHub v0.1.0-alpha.1

**One-click quality gates for AI prompts in your GitHub workflow**

## ✨ Key Features

- **📋 Copy-Paste Installation**: Single workflow file, works in 60 seconds
- **🏁 Label-Triggered Gate**: Add `prompt-check` label to activate quality checks
- **📊 Rich PR Summaries**: Visual pass/fail metrics directly in GitHub UI
- **🔒 Branch Protection Ready**: Block merges when quality thresholds aren't met
- **💰 Offline-First**: Zero API costs by default (stub mode)
- **🌙 Nightly Canary**: Automated drift detection to catch regressions early
- **💬 Slack Alerts**: Optional notifications for gate failures (requires webhook)
- **🧹 Repo Hygiene**: Automated cleanup workflows for attic/orphan files

## 🎯 Quick Install

```bash
# 1. Copy the workflow
curl -o .github/workflows/prompt-gate.yml \
  https://raw.githubusercontent.com/mattjutt1/prompt-wizard/main/.github/workflows/prompt-gate.yml

# 2. Set your threshold
echo "threshold: 0.85" > .promptops.yml

# 3. Commit and push
git add . && git commit -m "feat: add prompt gate" && git push

# 4. Enable branch protection (Settings → Branches → Add rule → Require "gate" check)
```

## 📚 Documentation

- [Quickstart Guide](docs/quickstart.md)
- [Branch Protection Setup](docs/branch_protection.md)
- [Pre-commit Policy](docs/precommit-policy.md)

## 💵 Pilot Pricing

- **Starter**: $500/mo (up to 10 devs)
- **Team**: $1,000/mo (up to 50 devs)
- **Enterprise**: $1,500/mo (unlimited)

Contact: <promptgate@example.com>
