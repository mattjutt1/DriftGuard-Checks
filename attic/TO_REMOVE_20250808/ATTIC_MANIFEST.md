# Attic Manifest - 2025-08-08

**Total files moved**: 2526
**Total size freed**: 185.9 MB

## What's in this attic

This directory contains files that were identified as orphaned or safe-to-remove candidates by the repository cleanup process.

### Categories moved:
- **Cache files**: .next/cache, __pycache__, .pytest_cache, etc.
- **Virtual environment artifacts**: Large binaries, compiled extensions
- **Generated files**: Claude Code embeddings, knowledge graphs (can be regenerated)
- **System junk**: .DS_Store, Thumbs.db
- **Legacy artifacts**: Safe portions of microsoft-promptwizard/, hf-deployment/

## Safe to delete?

**Yes, if**:
- CI passes after this change
- All core functionality still works
- 30+ days have passed with no issues

**Review first**:
- Any config files in legacy directories
- Files you specifically remember creating
- Anything in platform/ or library/ directories

## Restore instructions

To restore a file:
```bash
# Find the file in attic
find attic/TO_REMOVE_20250808/ -name "filename"

# Move back to original location
mv attic/TO_REMOVE_20250808/path/to/file path/to/original/location
```

## Full deletion (after review period)

```bash
# After 30+ days of successful operation
rm -rf attic/TO_REMOVE_20250808/
```
