#!/usr/bin/env python3
"""
Changelog Update Script for PromptEvolver
Automatically updates CHANGELOG.md based on git commits and changes
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path


class ChangelogUpdater:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.changelog_file = self.project_root / "CHANGELOG.md"
        self.version_file = self.project_root / ".claude" / "version.json"

    def get_current_version(self):
        """Get current version from version file"""
        if self.version_file.exists():
            with open(self.version_file, "r") as f:
                version_data = json.load(f)
                return version_data.get("version", "0.1.0")
        return "0.1.0"

    def increment_version(self, version_type="patch"):
        """Increment version number"""
        current = self.get_current_version()
        major, minor, patch = map(int, current.split("."))

        if version_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif version_type == "minor":
            minor += 1
            patch = 0
        else:  # patch
            patch += 1

        new_version = f"{major}.{minor}.{patch}"

        # Save new version
        self.version_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.version_file, "w") as f:
            json.dump({"version": new_version, "updated": datetime.now().isoformat()}, f, indent=2)

        return new_version

    def get_git_changes(self):
        """Get recent git changes"""
        try:
            # Get commits since last tag or from beginning
            result = subprocess.run(
                ["git", "log", "--oneline", "--since=1 hour ago"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode == 0:
                commits = result.stdout.strip().split("\n") if result.stdout.strip() else []
                return [commit for commit in commits if commit]
            return []
        except Exception as e:
            print(f"Error getting git changes: {e}")
            return []

    def categorize_changes(self, commits):
        """Categorize commits into changelog sections"""
        categories = {
            "Added": [],
            "Changed": [],
            "Fixed": [],
            "Technical": [],
            "Knowledge Graph": [],
        }

        for commit in commits:
            if not commit.strip():
                continue

            commit_lower = commit.lower()

            if any(word in commit_lower for word in ["feat:", "add:", "new:"]):
                categories["Added"].append(commit)
            elif any(word in commit_lower for word in ["fix:", "bug:", "patch:"]):
                categories["Fixed"].append(commit)
            elif any(word in commit_lower for word in ["refactor:", "chore:", "deps:"]):
                categories["Technical"].append(commit)
            elif any(word in commit_lower for word in ["graph:", "embed:", "knowledge"]):
                categories["Knowledge Graph"].append(commit)
            else:
                categories["Changed"].append(commit)

        return categories

    def detect_changes_from_files(self):
        """Detect changes from file system (when no git commits)"""
        changes = {"Added": [], "Changed": [], "Technical": [], "Knowledge Graph": []}

        # Check for new agent files
        agent_dir = self.project_root / ".claude" / "agents"
        if agent_dir.exists():
            for agent_file in agent_dir.glob("*.md"):
                if agent_file.name != "test-agent.md":  # Skip test agent
                    changes["Added"].append(f"Created {agent_file.stem} sub-agent")

        # Check for framework updates
        if (self.project_root / "CLAUDE.md").exists():
            changes["Technical"].append("Updated development framework")

        # Check for knowledge graph files
        kg_file = self.project_root / ".claude" / "knowledge_graph.json"
        if kg_file.exists():
            changes["Knowledge Graph"].append("Updated contextual knowledge graph")

        return changes

    def format_changelog_entry(self, version, categories):
        """Format a new changelog entry"""
        date = datetime.now().strftime("%Y-%m-%d")
        entry = f"\n## [{version}] - {date}\n\n"

        for category, changes in categories.items():
            if changes:
                entry += f"### {category}\n"
                for change in changes:
                    # Clean up commit message (remove hash)
                    clean_change = change.split(" ", 1)[-1] if " " in change else change
                    entry += f"- {clean_change}\n"
                entry += "\n"

        return entry

    def update_changelog(self, changes=None):
        """Update the changelog file"""
        print("📝 Updating CHANGELOG.md...")

        # Get changes from git or file system
        if changes is None:
            git_commits = self.get_git_changes()
            if git_commits:
                categories = self.categorize_changes(git_commits)
            else:
                categories = self.detect_changes_from_files()
        else:
            categories = changes

        # Check if there are any changes to document
        has_changes = any(category_changes for category_changes in categories.values())

        if not has_changes:
            print("No changes to document")
            return

        # Increment version
        new_version = self.increment_version()

        # Format new entry
        new_entry = self.format_changelog_entry(new_version, categories)

        # Read existing changelog
        if self.changelog_file.exists():
            with open(self.changelog_file, "r") as f:
                content = f.read()
        else:
            content = "# Changelog\n\nAll notable changes to PromptEvolver will be documented in this file.\n"

        # Find insertion point (after header)
        lines = content.split("\n")
        header_end = 0
        for i, line in enumerate(lines):
            if line.startswith("## [") or (i > 5 and line.strip() == ""):
                header_end = i
                break

        # Insert new entry
        if header_end > 0:
            lines.insert(header_end, new_entry.rstrip())
        else:
            lines.append(new_entry.rstrip())

        # Write updated changelog
        with open(self.changelog_file, "w") as f:
            f.write("\n".join(lines))

        print(f"✅ CHANGELOG.md updated with version {new_version}")
        return new_version

    def add_manual_entry(self, category, description):
        """Add a manual entry to changelog"""
        categories = {category: [description]}
        return self.update_changelog(categories)


if __name__ == "__main__":
    updater = ChangelogUpdater()
    updater.update_changelog()
