# Claude Code Tools & Commands Reference

This document tracks all external tools, their usage patterns, and command syntax discovered during the hardening process.

## Tool Discovery & Verification

**Philosophy:** Always run `--help` before first use; document successful patterns for reuse.

---

## Available Tools

### Git Operations
```bash
# Tool verification
git --version
git --help

# Common patterns
git status --porcelain=v1    # Machine-readable status
git log -1 --pretty=oneline  # Latest commit summary
```

### GitHub CLI (gh)
```bash
# Tool verification  
gh --version
gh --help

# API patterns
gh api [endpoint] --jq '[filter]'     # REST API calls
gh run list --limit [N]               # Action runs
```

### Node.js Ecosystem
```bash
# Tool verification
node -v
npm -v

# Common patterns
npm install [package]
npm run [script]
```

### Text Processing
```bash
# Tool verification
jq --version        # JSON processor
rg --version        # ripgrep search
sed --version       # Stream editor

# Usage patterns
jq '.[filter]' file.json              # JSON processing
rg -n "pattern" path                  # Search with line numbers
```

---

## Command Patterns Discovered

*Will be populated as tools are used and validated...*

## Custom Tool Documentation

*Any project-specific scripts or tools will be documented here...*