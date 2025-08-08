# Contributing to PromptEvolver

## Development Setup

1. **Clone and setup**:

   ```bash
   git clone https://github.com/mattjutt1/prompt-wizard.git
   cd prompt-wizard
   python3.12 -m pip install -U pre-commit
   pre-commit install
   ```

2. **Install dependencies** (see README.md for specific instructions)

## Code Quality

### Pre-commit Hooks

This project uses pre-commit hooks to maintain code quality. **Do not skip pre-commit hooks** unless explicitly allowed.

- **Default**: Always let pre-commit hooks run
- **Repair**: Use `./scripts/fix_precommit_env.sh` if hooks fail
- **Policy**: See [docs/precommit-policy.md](docs/precommit-policy.md) for when skipping is allowed

### Code Style

- **Python**: Black formatting, isort imports, flake8 linting
- **Line length**: 120 characters
- **Type hints**: Required for new Python code
- **Security**: Bandit security scanning

## Testing

Run tests before submitting PRs:

```bash
# Run all tests
pytest

# Run specific test suite
pytest cli/tests/
```

## Pull Requests

1. **Create feature branch**: `git checkout -b feature/your-feature`
2. **Make changes**: Follow code style and add tests
3. **Run pre-commit**: Ensure all hooks pass
4. **Submit PR**: Include clear description of changes

## Questions?

- **Pre-commit issues**: See [docs/precommit-policy.md](docs/precommit-policy.md)
- **General questions**: Open an issue
- **Security concerns**: See security policy
