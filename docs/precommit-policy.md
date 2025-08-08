# Pre-commit Policy

## Default Policy: Never Skip

**Do NOT use `--no-verify`** for git commits unless explicitly allowed by this policy.

Pre-commit hooks ensure code quality, security, and consistency. They run automatically before each commit to catch
issues early.

## When Skipping is Allowed

### 1. Pure Documentation/Sales Copy PRs

- Only documentation changes in `docs/` or markdown files
- Sales/marketing copy that doesn't affect code functionality
- Must still follow up with a lint cleanup PR if hooks would have failed

### 2. CI Hotfix Emergency

- Critical production issues requiring immediate fixes
- Must include `SKIP_REASON:` in commit body explaining the emergency
- **Mandatory**: Open a lint cleanup PR within 24 hours

## Skipping Process

If you must skip pre-commit hooks:

1. **Include justification** in commit message:

   ```bash
   fix: critical security patch for API

   SKIP_REASON: Production security vulnerability requires immediate deployment.
   Follow-up lint PR: #123
   ```

2. **Open follow-up PR** within 24 hours to fix any lint issues

3. **Use the skip flag**:

   ```bash
   git commit --no-verify -m "your message with SKIP_REASON"
   ```

## Repair Commands

If pre-commit hooks are failing locally:

```bash
# Quick repair (recommended)
./scripts/fix_precommit_env.sh

# Manual repair
python3.12 -m pip install -U pre-commit
pre-commit clean
pre-commit install --install-hooks
```

## Troubleshooting

### Python Version Issues

- Hooks are pinned to Python 3.12
- Ensure `python3.12 --version` works on your system
- Use the repair script which handles version detection

### Hook Failures

- Run `pre-commit run --all-files --show-diff-on-failure` to see specific issues
- Most issues can be auto-fixed by running hooks again
- For complex issues, see individual tool documentation (black, flake8, mypy, etc.)

### Emergency Override

In true emergencies where hooks are completely broken:

1. Document the reason in commit message with `SKIP_REASON:`
2. Use `--no-verify`
3. Open immediate follow-up PR to fix the hook infrastructure
4. Never leave hooks permanently broken

## CI Integration

Pre-commit hooks also run in CI on every PR. If local hooks are skipped, CI will still catch issues.

- **PR checks**: All hooks must pass before merge
- **Automatic fixes**: Some hooks auto-fix issues (trailing whitespace, formatting)
- **Manual review**: Complex issues may require manual fixes

## Questions?

For pre-commit issues or policy questions:

1. Check this document first
2. Try the repair script: `./scripts/fix_precommit_env.sh`
3. Review hook configuration in `.pre-commit-config.yaml`
4. Open an issue if problems persist
