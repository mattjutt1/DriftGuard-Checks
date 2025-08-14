---
allowed-tools: Bash(gh:*), Read(./**)
description: Create a GitHub release with notes
argument-hint: [tag]
---
## Your task
`gh release create "$ARGUMENTS" --notes-file RELEASE_NOTES.md` or prompt for notes if file missing.