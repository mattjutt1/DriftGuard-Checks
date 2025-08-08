# Contributing Guidelines

## Code Quality Standards

### Markdown Formatting

This repository uses markdownlint with relaxed line length rules:

- **Line Length**: Maximum 120 characters (MD013)
- **Code Blocks**: No line length enforcement in code blocks
- **Tables**: No line length enforcement in tables

Configuration is defined in `.markdownlint.jsonc` at the repository root.

### Pre-commit Hooks

All commits are validated with pre-commit hooks that enforce:

- YAML formatting and validation
- Python code quality (Black, isort, flake8)
- Markdown linting with the above relaxed rules
- Trailing whitespace and end-of-file fixes

Run `pre-commit run --all-files` to validate your changes before committing.
