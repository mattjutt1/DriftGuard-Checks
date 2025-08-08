#!/usr/bin/env python3
"""
Repository Orphan File Audit Script

Analyzes repository for orphaned, unused, and oversized files.
Produces audit report and candidate list for cleanup.

Usage: python scripts/repo_orphan_audit.py
Output: repo_audit/report.md, repo_audit/candidates.csv
"""

import csv
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class RepoAuditor:
    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or Path.cwd()
        self.report_dir = self.repo_root / "repo_audit"
        self.report_dir.mkdir(exist_ok=True)

        # File patterns that are likely orphans
        self.orphan_patterns = {
            "legacy_sample": [".ipynb_checkpoints", "__pycache__", ".pytest_cache", ".mypy_cache"],
            "screenshot_duplicate": [".png", ".jpg", ".jpeg", ".gif", "screenshot", "Screen Shot"],
            "model_artifact": [".pth", ".pt", ".ckpt", ".model", ".bin", ".safetensors"],
            "cache": [".cache", "node_modules", ".next", "dist", "build"],
            "system_junk": [".DS_Store", "Thumbs.db", "desktop.ini"],
            "temp_output": ["tmp", "temp", ".tmp", "output", "results"],
            "legacy_dir": ["microsoft-promptwizard", "hf-deployment", "nextjs-app/hf_training"]
        }

    def run_audit(self):
        """Run complete repository audit"""
        print("🔍 Starting repository orphan file audit...")

        # Get all files to analyze
        tracked_files = self.get_tracked_files()
        large_untracked = self.get_large_untracked_files()
        all_files = tracked_files + large_untracked

        print(f"📊 Analyzing {len(all_files)} files...")

        # Analyze each file
        file_data = []
        for i, file_path in enumerate(all_files):
            if i % 100 == 0:
                print(f"   Progress: {i}/{len(all_files)}")

            try:
                data = self.analyze_file(file_path)
                if data:
                    file_data.append(data)
            except Exception as e:
                print(f"   Warning: Error analyzing {file_path}: {e}")

        # Generate reports
        self.generate_report(file_data, tracked_files, large_untracked)
        self.generate_candidates_csv(file_data)

        print("✅ Audit complete!")
        print(f"📄 Report: {self.report_dir / 'report.md'}")
        print(f"📊 Candidates: {self.report_dir / 'candidates.csv'}")

    def get_tracked_files(self) -> List[Path]:
        """Get all git-tracked files"""
        try:
            result = subprocess.run(
                ["git", "ls-files"],
                capture_output=True,
                text=True,
                cwd=self.repo_root
            )
            return [Path(line.strip()) for line in result.stdout.strip().split('\n') if line.strip()]
        except Exception as e:
            print(f"Warning: Could not get tracked files: {e}")
            return []

    def get_large_untracked_files(self, min_size_mb: float = 1.0) -> List[Path]:
        """Get untracked files over min_size_mb"""
        try:
            # Find large files, excluding .git
            result = subprocess.run([
                "find", ".", "-type", "f", "-size", f"+{int(min_size_mb)}M",
                "-not", "-path", "./.git/*"
            ], capture_output=True, text=True, cwd=self.repo_root)

            candidates = [Path(line.strip()[2:]) for line in result.stdout.strip().split('\n') if line.strip()]

            # Filter out tracked files
            tracked_set = set(self.get_tracked_files())
            return [f for f in candidates if f not in tracked_set]

        except Exception as e:
            print(f"Warning: Could not find large untracked files: {e}")
            return []

    def analyze_file(self, file_path: Path) -> Optional[Dict]:
        """Analyze individual file for orphan characteristics"""
        full_path = self.repo_root / file_path

        if not full_path.exists():
            return None

        # Get file size
        try:
            size_bytes = full_path.stat().st_size
        except:
            return None

        # Get last commit date
        last_commit_date = self.get_last_commit_date(file_path)

        # Count references
        ref_count, ref_locations = self.count_references(file_path)

        # Guess reason for being orphan
        reason_guess = self.guess_orphan_reason(file_path, ref_count)

        return {
            "path": str(file_path),
            "size_bytes": size_bytes,
            "last_commit_date": last_commit_date,
            "ref_count": ref_count,
            "ref_locations": "; ".join(ref_locations[:5]),  # Top 5 locations
            "reason_guess": reason_guess
        }

    def get_last_commit_date(self, file_path: Path) -> str:
        """Get last commit date for file"""
        try:
            result = subprocess.run([
                "git", "log", "-1", "--format=%cs", "--", str(file_path)
            ], capture_output=True, text=True, cwd=self.repo_root)

            return result.stdout.strip() or "never"
        except:
            return "unknown"

    def count_references(self, file_path: Path) -> Tuple[int, List[str]]:
        """Count references to file across repository"""
        filename = file_path.name
        basename = file_path.stem

        # Search patterns
        search_terms = [filename]
        if basename != filename:
            search_terms.append(basename)

        all_locations = []

        for term in search_terms:
            try:
                # Use ripgrep to search for references
                result = subprocess.run([
                    "rg", "-n", "--no-ignore", "-S", term,
                    "--type-not", "binary"
                ], capture_output=True, text=True, cwd=self.repo_root)

                if result.returncode == 0:
                    locations = [
                        line.split(':', 2)[0] + ":" + line.split(':', 2)[1]
                        for line in result.stdout.strip().split('\n')
                        if line.strip() and not line.startswith(str(file_path))
                    ]
                    all_locations.extend(locations)

            except Exception:
                pass

        # Remove duplicates and self-references
        unique_locations = list(set(all_locations))
        return len(unique_locations), unique_locations

    def guess_orphan_reason(self, file_path: Path, ref_count: int) -> str:
        """Guess why file might be orphaned"""
        path_str = str(file_path).lower()

        # No references = likely orphan
        if ref_count == 0:
            reasons = []

            # Check patterns
            for category, patterns in self.orphan_patterns.items():
                for pattern in patterns:
                    if pattern.lower() in path_str:
                        reasons.append(category)
                        break

            # Special cases
            if any(x in path_str for x in ["test", "demo", "example"]):
                reasons.append("test_artifact")

            if file_path.suffix in [".png", ".jpg", ".jpeg", ".gif", ".svg"]:
                reasons.append("image_asset")

            if file_path.suffix in [".json", ".yaml", ".yml"] and "config" in path_str:
                reasons.append("config_file")

            return "+".join(reasons) if reasons else "unknown_orphan"

        elif ref_count < 3:
            return "low_usage"

        else:
            return "actively_used"

    def generate_report(self, file_data: List[Dict], tracked_files: List[Path], large_untracked: List[Path]):
        """Generate markdown audit report"""
        report_path = self.report_dir / "report.md"

        # Sort by size for analysis
        by_size = sorted(file_data, key=lambda x: x["size_bytes"], reverse=True)
        orphans = [f for f in file_data if f["ref_count"] == 0]
        large_files = [f for f in file_data if f["size_bytes"] > 50 * 1024 * 1024]  # >50MB

        with open(report_path, 'w') as f:
            f.write(f"""# Repository Orphan File Audit Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Total files analyzed**: {len(file_data):,}
- **Tracked files**: {len(tracked_files):,}
- **Large untracked files**: {len(large_untracked):,}
- **Zero-reference files**: {len(orphans):,}
- **Files >50MB**: {len(large_files):,}
- **Total repository size**: {sum(f['size_bytes'] for f in file_data) / (1024*1024):.1f} MB

## Top 50 Largest Tracked Files

| Size (MB) | Path | Last Commit | Refs | Reason |
|-----------|------|-------------|------|---------|
""")

            # Top 50 largest tracked files
            tracked_data = [f for f in by_size if Path(f['path']) in tracked_files]
            for file_info in tracked_data[:50]:
                size_mb = file_info['size_bytes'] / (1024 * 1024)
                f.write(f"| {size_mb:.1f} | `{file_info['path']}` | {file_info['last_commit_date']} | {file_info['ref_count']} | {file_info['reason_guess']} |\n")

            f.write(f"""
## Top 50 Largest Untracked Files

| Size (MB) | Path | Reason |
|-----------|------|---------|
""")

            # Top 50 largest untracked files
            untracked_data = [f for f in by_size if Path(f['path']) in large_untracked]
            for file_info in untracked_data[:50]:
                size_mb = file_info['size_bytes'] / (1024 * 1024)
                f.write(f"| {size_mb:.1f} | `{file_info['path']}` | {file_info['reason_guess']} |\n")

            f.write(f"""
## Files Over 50MB (LFS Candidates)

| Size (MB) | Path | Type | Last Commit | Refs |
|-----------|------|------|-------------|------|
""")

            for file_info in large_files:
                size_mb = file_info['size_bytes'] / (1024 * 1024)
                file_type = "tracked" if Path(file_info['path']) in tracked_files else "untracked"
                f.write(f"| {size_mb:.1f} | `{file_info['path']}` | {file_type} | {file_info['last_commit_date']} | {file_info['ref_count']} |\n")

            f.write(f"""
## Zero-Reference Files (Orphan Candidates)

| Size (MB) | Path | Last Commit | Reason |
|-----------|------|-------------|---------|
""")

            orphan_by_size = sorted(orphans, key=lambda x: x["size_bytes"], reverse=True)
            for file_info in orphan_by_size[:100]:  # Top 100 orphans
                size_mb = file_info['size_bytes'] / (1024 * 1024)
                f.write(f"| {size_mb:.1f} | `{file_info['path']}` | {file_info['last_commit_date']} | {file_info['reason_guess']} |\n")

            f.write(f"""
## Cleanup Recommendations

### Immediate Candidates for Attic
- **Zero-reference files**: {len(orphans)} files, {sum(f['size_bytes'] for f in orphans) / (1024*1024):.1f} MB total
- **Legacy directories**: Files in microsoft-promptwizard/, hf-deployment/, etc.
- **Cache/temp files**: .DS_Store, __pycache__, .pytest_cache, etc.

### Require Manual Review
- **Large tracked files**: Consider Git LFS for files >50MB
- **Config files**: May be environment-specific, review before removal
- **Image assets**: Check if used in documentation or UI

### Keep Intact
- **.github/workflows/**: All workflow files preserved
- **platform/**, **library/**: Core functionality preserved
- **Active code files**: Files with >3 references
""")

    def generate_candidates_csv(self, file_data: List[Dict]):
        """Generate CSV of deletion candidates"""
        csv_path = self.report_dir / "candidates.csv"

        # Filter for deletion candidates (zero references, certain patterns)
        candidates = [
            f for f in file_data
            if f["ref_count"] == 0 and f["reason_guess"] != "actively_used"
        ]

        with open(csv_path, 'w', newline='') as csvfile:
            fieldnames = ['path', 'size_bytes', 'last_commit_date', 'ref_count', 'ref_locations', 'reason_guess']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for candidate in sorted(candidates, key=lambda x: x["size_bytes"], reverse=True):
                writer.writerow(candidate)

        print(f"📊 Generated {len(candidates)} deletion candidates")


if __name__ == "__main__":
    auditor = RepoAuditor()
    auditor.run_audit()
