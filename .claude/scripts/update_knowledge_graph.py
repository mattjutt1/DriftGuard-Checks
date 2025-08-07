#!/usr/bin/env python3
"""
Knowledge Graph Update Script for PromptEvolver
Automatically updates the contextual knowledge graph after code changes
"""

import hashlib
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path


class KnowledgeGraphUpdater:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.graph_file = self.project_root / ".claude" / "knowledge_graph.json"
        self.embeddings_file = self.project_root / ".claude" / "embeddings.json"

    def load_graph(self):
        """Load existing knowledge graph or create new one"""
        if self.graph_file.exists():
            with open(self.graph_file, "r") as f:
                return json.load(f)
        return self.create_empty_graph()

    def create_empty_graph(self):
        """Create empty knowledge graph structure"""
        return {
            "metadata": {
                "created": datetime.now().isoformat(),
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "architecture": "AVSHA",  # Atomic Vertical Slice Hybrid Architecture
            },
            "entities": {
                "files": {},
                "functions": {},
                "classes": {},
                "agents": {},
                "decisions": {},
                "atomic_components": {},
                "feature_slices": {},
                "architectural_violations": {},
            },
            "relationships": {},
            "context_vectors": {
                "current_session": [],
                "recent_changes": [],
                "architectural_patterns": [],
                "quality_metrics": [],
            },
            "avsha_metrics": {
                "reusability_score": 0.0,
                "feature_cohesion": 0.0,
                "component_distribution": {},
                "architectural_compliance": 0.0,
                "last_assessment": datetime.now().isoformat(),
            },
        }

    def scan_project_files(self):
        """Scan project for code files and extract entities"""
        entities = {"files": {}, "functions": {}, "classes": {}, "agents": {}}

        # Scan Python files
        for py_file in self.project_root.rglob("*.py"):
            if ".venv" in str(py_file) or "__pycache__" in str(py_file):
                continue

            file_hash = self.get_file_hash(py_file)
            entities["files"][str(py_file)] = {
                "type": "python",
                "hash": file_hash,
                "last_modified": datetime.fromtimestamp(py_file.stat().st_mtime).isoformat(),
                "size": py_file.stat().st_size,
            }

        # Scan agent files
        agent_dir = self.project_root / ".claude" / "agents"
        if agent_dir.exists():
            for agent_file in agent_dir.glob("*.md"):
                file_hash = self.get_file_hash(agent_file)
                entities["agents"][agent_file.stem] = {
                    "type": "subagent",
                    "file": str(agent_file),
                    "hash": file_hash,
                    "last_modified": datetime.fromtimestamp(agent_file.stat().st_mtime).isoformat(),
                }

        return entities

    def analyze_avsha_structure(self, entities):
        """Analyze AVSHA architectural structure"""
        atomic_components = {}
        feature_slices = {}
        violations = {}

        # Define AVSHA patterns
        atomic_levels = ["atoms", "molecules", "organisms", "templates", "pages"]
        expected_features = ["authentication", "optimization", "dashboard"]

        # Analyze file structure for AVSHA compliance
        for file_path, file_data in entities["files"].items():
            path_parts = Path(file_path).parts

            # Check if file follows AVSHA structure
            if "src" in path_parts or "app" in path_parts:
                # Frontend (React) or Backend (FastAPI) structure
                avsha_analysis = self.analyze_file_avsha_compliance(file_path, path_parts)

                if avsha_analysis["is_atomic_component"]:
                    component_id = f"{avsha_analysis['level']}:{avsha_analysis['component_name']}"
                    atomic_components[component_id] = {
                        "level": avsha_analysis["level"],
                        "feature": avsha_analysis["feature"],
                        "component_name": avsha_analysis["component_name"],
                        "file_path": file_path,
                        "is_shared": avsha_analysis["is_shared"],
                        "last_modified": file_data["last_modified"],
                    }

                if avsha_analysis["feature"] and avsha_analysis["feature"] != "shared":
                    if avsha_analysis["feature"] not in feature_slices:
                        feature_slices[avsha_analysis["feature"]] = {
                            "components": [],
                            "cohesion_score": 0.0,
                            "last_updated": file_data["last_modified"],
                        }
                    feature_slices[avsha_analysis["feature"]]["components"].append(file_path)

                # Check for violations
                if avsha_analysis["violations"]:
                    violations[file_path] = avsha_analysis["violations"]

        return atomic_components, feature_slices, violations

    def analyze_file_avsha_compliance(self, file_path, path_parts):
        """Analyze individual file for AVSHA compliance"""
        analysis = {
            "is_atomic_component": False,
            "level": None,
            "feature": None,
            "component_name": None,
            "is_shared": False,
            "violations": [],
        }

        atomic_levels = ["atoms", "molecules", "organisms", "templates", "pages"]

        # Check for atomic level in path
        for level in atomic_levels:
            if level in path_parts:
                analysis["is_atomic_component"] = True
                analysis["level"] = level
                break

        # Determine feature
        if "shared" in path_parts:
            analysis["is_shared"] = True
            analysis["feature"] = "shared"
        elif "features" in path_parts:
            # Find feature name after 'features'
            try:
                features_index = path_parts.index("features")
                if features_index + 1 < len(path_parts):
                    analysis["feature"] = path_parts[features_index + 1]
            except ValueError:
                pass

        # Extract component name
        if analysis["is_atomic_component"]:
            file_stem = Path(file_path).stem
            analysis["component_name"] = file_stem

        # Check for violations
        if analysis["is_atomic_component"]:
            # Violation: Atomic component not in proper level directory
            if not analysis["level"]:
                analysis["violations"].append("atomic_component_no_level")

            # Violation: Feature component in wrong location
            if analysis["feature"] and not (analysis["is_shared"] or "features" in path_parts):
                analysis["violations"].append("feature_component_wrong_location")

        return analysis

    def calculate_avsha_metrics(self, atomic_components, feature_slices, entities):
        """Calculate AVSHA architecture metrics"""
        metrics = {
            "reusability_score": 0.0,
            "feature_cohesion": 0.0,
            "component_distribution": {},
            "architectural_compliance": 0.0,
        }

        total_files = len(entities["files"])
        if total_files == 0:
            return metrics

        # Calculate component distribution
        for level in ["atoms", "molecules", "organisms", "templates", "pages"]:
            count = len([c for c in atomic_components.values() if c["level"] == level])
            metrics["component_distribution"][level] = count

        # Calculate reusability score (shared components / total components)
        shared_components = len([c for c in atomic_components.values() if c["is_shared"]])
        total_components = len(atomic_components)
        if total_components > 0:
            metrics["reusability_score"] = shared_components / total_components

        # Calculate feature cohesion (average cohesion across features)
        if feature_slices:
            cohesion_scores = []
            for feature, data in feature_slices.items():
                # Simple cohesion metric: components per feature
                component_count = len(data["components"])
                # Higher component count in feature indicates better cohesion
                cohesion_score = min(component_count / 10.0, 1.0)  # Normalize to 1.0
                cohesion_scores.append(cohesion_score)
            metrics["feature_cohesion"] = sum(cohesion_scores) / len(cohesion_scores)

        # Calculate architectural compliance
        compliant_files = len([f for f in entities["files"] if self.is_file_avsha_compliant(f)])
        metrics["architectural_compliance"] = compliant_files / total_files

        return metrics

    def is_file_avsha_compliant(self, file_path):
        """Check if file follows AVSHA naming and structure conventions"""
        path_parts = Path(file_path).parts

        # Basic compliance checks
        if "src" in path_parts or "app" in path_parts:
            # Check for proper structure (shared/ or features/)
            if "shared" in path_parts or "features" in path_parts:
                return True

        # Configuration and root files are considered compliant
        if Path(file_path).name in ["main.py", "app.py", "__init__.py"]:
            return True

        return False

    def get_file_hash(self, file_path):
        """Generate hash for file content"""
        with open(file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def detect_changes(self, current_entities, previous_entities):
        """Detect changes between current and previous state"""
        changes = {"added": [], "modified": [], "deleted": []}

        for entity_type, entities in current_entities.items():
            prev_entities = previous_entities.get(entity_type, {})

            for entity_id, entity_data in entities.items():
                if entity_id not in prev_entities:
                    changes["added"].append({"type": entity_type, "id": entity_id})
                elif prev_entities[entity_id].get("hash") != entity_data.get("hash"):
                    changes["modified"].append({"type": entity_type, "id": entity_id})

            for entity_id in prev_entities:
                if entity_id not in entities:
                    changes["deleted"].append({"type": entity_type, "id": entity_id})

        return changes

    def update_relationships(self, graph, changes):
        """Update relationships based on detected changes"""
        # Simple relationship detection - can be enhanced
        for change in changes["modified"] + changes["added"]:
            if change["type"] == "files":
                # Detect imports and dependencies
                file_path = Path(change["id"])
                if file_path.suffix == ".py":
                    try:
                        with open(file_path, "r") as f:
                            content = f.read()
                            # Extract imports
                            imports = self.extract_imports(content)
                            graph["relationships"][change["id"]] = {
                                "imports": imports,
                                "timestamp": datetime.now().isoformat(),
                            }
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")

        return graph

    def extract_imports(self, content):
        """Extract import statements from Python code"""
        imports = []
        lines = content.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("import ") or line.startswith("from "):
                imports.append(line)
        return imports

    def save_graph(self, graph):
        """Save knowledge graph to file"""
        graph["metadata"]["last_updated"] = datetime.now().isoformat()

        # Ensure directory exists
        self.graph_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.graph_file, "w") as f:
            json.dump(graph, f, indent=2)

    def update(self):
        """Main update method"""
        print("🧠 Updating knowledge graph with AVSHA analysis...")

        # Load existing graph
        graph = self.load_graph()

        # Scan current project state
        current_entities = self.scan_project_files()

        # Detect changes
        changes = self.detect_changes(current_entities, graph["entities"])

        # Update entities
        graph["entities"].update(current_entities)

        # Perform AVSHA architectural analysis
        print("🏛️ Analyzing AVSHA architecture...")
        atomic_components, feature_slices, violations = self.analyze_avsha_structure(
            current_entities
        )

        # Update AVSHA entities
        graph["entities"]["atomic_components"] = atomic_components
        graph["entities"]["feature_slices"] = feature_slices
        graph["entities"]["architectural_violations"] = violations

        # Calculate AVSHA metrics
        avsha_metrics = self.calculate_avsha_metrics(
            atomic_components, feature_slices, current_entities
        )
        avsha_metrics["last_assessment"] = datetime.now().isoformat()
        graph["avsha_metrics"] = avsha_metrics

        # Update relationships
        graph = self.update_relationships(graph, changes)

        # Update context vectors with architectural patterns
        graph["context_vectors"]["recent_changes"] = changes
        graph["context_vectors"]["last_scan"] = datetime.now().isoformat()
        graph["context_vectors"]["architectural_patterns"] = list(atomic_components.keys())

        # Save graph
        self.save_graph(graph)

        # Print results
        print(f"✅ Knowledge graph updated:")
        print(
            f"   📁 Files: {len(changes['added'])} added, {len(changes['modified'])} modified, {len(changes['deleted'])} deleted"
        )
        print(f"   🧩 Atomic Components: {len(atomic_components)}")
        print(f"   🎯 Feature Slices: {len(feature_slices)}")
        print(f"   ⚠️  Violations: {len(violations)}")
        print(f"   📊 Compliance Score: {avsha_metrics['architectural_compliance']:.2f}")
        print(f"   🔄 Reusability Score: {avsha_metrics['reusability_score']:.2f}")

        if violations:
            print("⚠️  AVSHA Violations detected:")
            for file_path, violation_list in violations.items():
                print(f"   - {file_path}: {', '.join(violation_list)}")

        return changes


if __name__ == "__main__":
    updater = KnowledgeGraphUpdater()
    changes = updater.update()
