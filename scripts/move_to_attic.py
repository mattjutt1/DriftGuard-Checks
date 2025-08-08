#!/usr/bin/env python3
"""
Move Orphaned Files to Attic Script

Safely moves obvious orphan candidates to attic/TO_REMOVE_<date>/ for review.
NON-DESTRUCTIVE: preserves original file structure in attic.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime


class AtticMover:
    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or Path.cwd()
        self.attic_dir = self.repo_root / f"attic/TO_REMOVE_{datetime.now().strftime('%Y%m%d')}"
        self.attic_dir.mkdir(parents=True, exist_ok=True)
        self.moved_count = 0
        self.moved_size = 0

    def should_move_to_attic(self, file_path: Path) -> tuple[bool, str]:
        """Determine if file should be moved to attic with reason"""
        path_str = str(file_path)

        # Absolute safe-to-move patterns
        safe_patterns = [
            # Next.js cache (biggest space saver)
            ".next/cache/",
            ".next/server/",

            # Python cache and compiled files
            "__pycache__/",
            ".pytest_cache/",
            ".mypy_cache/",
            ".ruff_cache/",
            ".ipynb_checkpoints/",

            # Node modules (untracked, huge)
            "node_modules/",

            # Virtual environment binaries (duplicated)
            "/venv/lib/python",
            "/bin/ruff",
            "/bin/wandb-core",
            "/bin/server",

            # System junk
            ".DS_Store",
            "Thumbs.db",

            # Temp and output directories
            "/tmp/",
            "/temp/",
            "/output/",
            "/results/",
        ]

        # Check safe patterns
        for pattern in safe_patterns:
            if pattern in path_str:
                return True, f"cache_or_temp:{pattern}"

        # Large binary artifacts in venv (safe to remove)
        if "/venv/" in path_str and any(ext in path_str for ext in [".so", ".so.", ".node", ".dylib"]):
            return True, "venv_binary"

        # Claude Code generated files (can be regenerated)
        if path_str.endswith((".claude/embeddings.json", ".claude/knowledge_graph.json")):
            return True, "claude_generated"

        # Legacy directories (specified as safe to evaluate)
        legacy_dirs = ["microsoft-promptwizard/", "hf-deployment/"]
        if any(legacy in path_str for legacy in legacy_dirs):
            # Be more careful with legacy - only move obvious artifacts
            if any(artifact in path_str for artifact in ["venv/", "__pycache__/", ".git/", "node_modules/"]):
                return True, "legacy_artifact"

        return False, "keep"

    def move_file_to_attic(self, file_path: Path, reason: str):
        """Move file to attic preserving directory structure"""
        try:
            # Preserve directory structure in attic
            rel_path = file_path.relative_to(self.repo_root)
            attic_path = self.attic_dir / rel_path

            # Create parent directories
            attic_path.parent.mkdir(parents=True, exist_ok=True)

            # Get file size before moving
            if file_path.exists():
                size = file_path.stat().st_size

                # Move file (shutil.move handles both files and directories)
                shutil.move(str(file_path), str(attic_path))

                self.moved_count += 1
                self.moved_size += size

                print(f"✓ Moved {rel_path} ({size/1024/1024:.1f} MB) - {reason}")

        except Exception as e:
            print(f"⚠️  Failed to move {file_path}: {e}")

    def scan_and_move(self):
        """Scan repository and move obvious candidates to attic"""
        print(f"🏠 Moving orphaned files to: {self.attic_dir}")

        # Walk through all files
        for root, dirs, files in os.walk(self.repo_root):
            root_path = Path(root)

            # Skip attic and .git directories
            if any(skip in str(root_path) for skip in ["/attic/", "/.git/"]):
                continue

            # Check directories first (can move entire dirs)
            dirs_to_remove = []
            for dir_name in dirs:
                dir_path = root_path / dir_name
                should_move, reason = self.should_move_to_attic(dir_path)

                if should_move:
                    self.move_file_to_attic(dir_path, reason)
                    dirs_to_remove.append(dir_name)  # Don't descend into moved dirs

            # Remove moved directories from further traversal
            for dir_name in dirs_to_remove:
                dirs.remove(dir_name)

            # Check individual files
            for file_name in files:
                file_path = root_path / file_name
                should_move, reason = self.should_move_to_attic(file_path)

                if should_move:
                    self.move_file_to_attic(file_path, reason)

    def generate_attic_manifest(self):
        """Generate manifest of what was moved to attic"""
        manifest_path = self.attic_dir / "ATTIC_MANIFEST.md"

        with open(manifest_path, 'w') as f:
            f.write(f"""# Attic Manifest - {datetime.now().strftime('%Y-%m-%d')}

**Total files moved**: {self.moved_count}
**Total size freed**: {self.moved_size / (1024*1024):.1f} MB

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
find attic/TO_REMOVE_{datetime.now().strftime('%Y%m%d')}/ -name "filename"

# Move back to original location
mv attic/TO_REMOVE_{datetime.now().strftime('%Y%m%d')}/path/to/file path/to/original/location
```

## Full deletion (after review period)

```bash
# After 30+ days of successful operation
rm -rf attic/TO_REMOVE_{datetime.now().strftime('%Y%m%d')}/
```
""")

        print(f"📋 Generated manifest: {manifest_path}")


if __name__ == "__main__":
    mover = AtticMover()
    mover.scan_and_move()
    mover.generate_attic_manifest()

    print(f"\n🎯 Summary:")
    print(f"   Files moved: {mover.moved_count}")
    print(f"   Space freed: {mover.moved_size / (1024*1024):.1f} MB")
    print(f"   Attic location: {mover.attic_dir}")
