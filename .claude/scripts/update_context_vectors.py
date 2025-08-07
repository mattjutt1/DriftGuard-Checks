#!/usr/bin/env python3
"""
Context Vector Update Script for PromptEvolver
Updates context vectors for Claude Code CLI optimization
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path


class ContextVectorUpdater:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.context_file = self.project_root / ".claude" / "context_vectors.json"
        self.graph_file = self.project_root / ".claude" / "knowledge_graph.json"
        self.embeddings_file = self.project_root / ".claude" / "embeddings.json"

    def load_files(self):
        """Load knowledge graph and embeddings"""
        files = {}

        if self.graph_file.exists():
            with open(self.graph_file, "r") as f:
                files["graph"] = json.load(f)
        else:
            files["graph"] = {}

        if self.embeddings_file.exists():
            with open(self.embeddings_file, "r") as f:
                files["embeddings"] = json.load(f)
        else:
            files["embeddings"] = {}

        return files

    def extract_current_session_context(self, graph):
        """Extract context for current session"""
        session_context = {
            "active_agents": [],
            "recent_files": [],
            "current_patterns": [],
            "session_start": datetime.now().isoformat(),
        }

        # Extract active agents
        agents = graph.get("entities", {}).get("agents", {})
        for agent_name, agent_data in agents.items():
            session_context["active_agents"].append(
                {
                    "name": agent_name,
                    "type": agent_data.get("type", "subagent"),
                    "last_modified": agent_data.get("last_modified", ""),
                }
            )

        # Extract recently modified files (last 24 hours)
        files = graph.get("entities", {}).get("files", {})
        cutoff_time = datetime.now() - timedelta(hours=24)

        for file_path, file_data in files.items():
            try:
                file_time = datetime.fromisoformat(file_data.get("last_modified", ""))
                if file_time > cutoff_time:
                    session_context["recent_files"].append(
                        {
                            "path": file_path,
                            "type": file_data.get("type", "unknown"),
                            "modified": file_data.get("last_modified", ""),
                        }
                    )
            except Exception:
                continue

        return session_context

    def extract_architectural_patterns(self, graph):
        """Extract architectural patterns from the codebase"""
        patterns = {"frameworks": [], "design_patterns": [], "dependencies": [], "structure": {}}

        # Analyze file structure
        files = graph.get("entities", {}).get("files", {})

        # Detect frameworks
        framework_indicators = {
            "fastapi": ["fastapi", "uvicorn"],
            "react": ["react", "jsx", "tsx"],
            "docker": ["dockerfile", "docker-compose"],
            "pytest": ["pytest", "test_"],
        }

        for file_path in files.keys():
            file_lower = file_path.lower()
            for framework, indicators in framework_indicators.items():
                if any(indicator in file_lower for indicator in indicators):
                    if framework not in patterns["frameworks"]:
                        patterns["frameworks"].append(framework)

        # Analyze relationships for dependencies
        relationships = graph.get("relationships", {})
        for file_path, rel_data in relationships.items():
            imports = rel_data.get("imports", [])
            patterns["dependencies"].extend(imports[:5])  # Limit to avoid bloat

        return patterns

    def calculate_quality_metrics(self, graph, embeddings):
        """Calculate quality metrics for context"""
        metrics = {"completeness": 0.0, "consistency": 0.0, "relevance": 0.0, "freshness": 0.0}

        # Completeness: percentage of files with embeddings
        total_files = len(graph.get("entities", {}).get("files", {}))
        embedded_files = len(
            [e for e in embeddings.get("embeddings", {}) if embeddings["embeddings"][e]["type"] == "file"]
        )

        if total_files > 0:
            metrics["completeness"] = embedded_files / total_files

        # Freshness: based on recent updates
        recent_updates = len(graph.get("context_vectors", {}).get("recent_changes", []))
        metrics["freshness"] = min(recent_updates / 10.0, 1.0)  # Normalize to 1.0

        # Consistency: all agents have embeddings
        total_agents = len(graph.get("entities", {}).get("agents", {}))
        embedded_agents = len(
            [e for e in embeddings.get("embeddings", {}) if embeddings["embeddings"][e]["type"] == "agent"]
        )

        if total_agents > 0:
            metrics["consistency"] = embedded_agents / total_agents

        # Relevance: placeholder (would need actual usage data)
        metrics["relevance"] = 0.8  # Assume reasonable relevance

        return metrics

    def generate_context_summary(self, session_context, patterns, metrics, avsha_data=None):
        """Generate a context summary for Claude Code"""
        summary = {
            "project": "PromptEvolver",
            "framework": "Optimized Claude Code Agentic Development with AVSHA",
            "architecture": "Atomic Vertical Slice Hybrid Architecture",
            "active_agents": len(session_context["active_agents"]),
            "recent_activity": len(session_context["recent_files"]),
            "frameworks_detected": patterns["frameworks"],
            "quality_score": sum(metrics.values()) / len(metrics),
            "last_updated": datetime.now().isoformat(),
            "recommendations": [],
            "avsha_status": {},
        }

        # Add AVSHA-specific context if available
        if avsha_data:
            summary["avsha_status"] = {
                "atomic_components": len(avsha_data.get("atomic_components", {})),
                "feature_slices": len(avsha_data.get("feature_slices", {})),
                "violations": len(avsha_data.get("architectural_violations", {})),
                "compliance_score": avsha_data.get("avsha_metrics", {}).get("architectural_compliance", 0.0),
                "reusability_score": avsha_data.get("avsha_metrics", {}).get("reusability_score", 0.0),
            }

        # Add recommendations based on context
        if metrics["completeness"] < 0.8:
            summary["recommendations"].append("Consider generating embeddings for all files")

        if metrics["freshness"] < 0.5:
            summary["recommendations"].append("Update knowledge graph with recent changes")

        if len(session_context["active_agents"]) < 3:
            summary["recommendations"].append("Consider activating more specialized agents")

        # Add AVSHA-specific recommendations
        if avsha_data:
            avsha_metrics = avsha_data.get("avsha_metrics", {})
            violations = avsha_data.get("architectural_violations", {})

            if avsha_metrics.get("architectural_compliance", 0.0) < 0.8:
                summary["recommendations"].append(
                    "AVSHA: Improve architectural compliance - structure files according to atomic levels and feature slices"
                )

            if avsha_metrics.get("reusability_score", 0.0) < 0.3:
                summary["recommendations"].append(
                    "AVSHA: Increase component reusability - move common components to /shared/"
                )

            if violations:
                summary["recommendations"].append(f"AVSHA: Fix {len(violations)} architectural violations")

            component_dist = avsha_metrics.get("component_distribution", {})
            if component_dist.get("atoms", 0) < 3:
                summary["recommendations"].append(
                    "AVSHA: Consider creating more atomic components for better reusability"
                )

            if len(avsha_data.get("feature_slices", {})) < 3:
                summary["recommendations"].append(
                    "AVSHA: Organize code into feature slices (authentication, optimization, dashboard)"
                )

        return summary

    def extract_avsha_guidance(self, graph):
        """Extract AVSHA-specific guidance and patterns"""
        guidance = {
            "current_structure": {},
            "recommendations": [],
            "patterns": [],
            "violations": [],
        }

        # Extract AVSHA data from graph
        atomic_components = graph.get("entities", {}).get("atomic_components", {})
        feature_slices = graph.get("entities", {}).get("feature_slices", {})
        violations = graph.get("entities", {}).get("architectural_violations", {})
        avsha_metrics = graph.get("avsha_metrics", {})

        # Current structure analysis
        guidance["current_structure"] = {
            "atomic_levels": {},
            "features": list(feature_slices.keys()),
            "shared_components": len([c for c in atomic_components.values() if c.get("is_shared", False)]),
        }

        # Group components by level
        for component in atomic_components.values():
            level = component.get("level", "unknown")
            if level not in guidance["current_structure"]["atomic_levels"]:
                guidance["current_structure"]["atomic_levels"][level] = 0
            guidance["current_structure"]["atomic_levels"][level] += 1

        # Generate patterns and recommendations
        if atomic_components:
            guidance["patterns"].append("AVSHA structure detected - continue using atomic hierarchy")

        if feature_slices:
            guidance["patterns"].append(f"Feature slices organized: {', '.join(feature_slices.keys())}")

        # Specific recommendations based on structure
        if avsha_metrics.get("reusability_score", 0) < 0.5:
            guidance["recommendations"].append("Move reusable components to /shared/ directory")

        if len(feature_slices) > 0:
            for feature, data in feature_slices.items():
                if len(data.get("components", [])) < 5:
                    guidance["recommendations"].append(f"Consider expanding {feature} feature with more components")

        # Extract violations
        guidance["violations"] = list(violations.keys()) if violations else []

        return guidance

    def update_context_vectors(self):
        """Main context vector update method"""
        print("🔄 Updating context vectors with AVSHA analysis...")

        # Load data files
        files = self.load_files()
        graph = files["graph"]
        embeddings = files["embeddings"]

        if not graph:
            print("No knowledge graph found - run update_knowledge_graph.py first")
            return

        # Extract context components
        session_context = self.extract_current_session_context(graph)
        patterns = self.extract_architectural_patterns(graph)
        metrics = self.calculate_quality_metrics(graph, embeddings)

        # Extract AVSHA-specific guidance
        avsha_guidance = self.extract_avsha_guidance(graph)
        avsha_data = {
            "atomic_components": graph.get("entities", {}).get("atomic_components", {}),
            "feature_slices": graph.get("entities", {}).get("feature_slices", {}),
            "architectural_violations": graph.get("entities", {}).get("architectural_violations", {}),
            "avsha_metrics": graph.get("avsha_metrics", {}),
        }

        # Generate context summary with AVSHA data
        summary = self.generate_context_summary(session_context, patterns, metrics, avsha_data)

        # Build context vectors
        context_vectors = {
            "metadata": {
                "updated": datetime.now().isoformat(),
                "version": "2.0",
                "architecture": "AVSHA",
            },
            "current_session": session_context,
            "architectural_patterns": patterns,
            "quality_metrics": metrics,
            "context_summary": summary,
            "avsha_guidance": avsha_guidance,
            "claude_optimization": {
                "high_priority_context": [
                    f"Architecture: AVSHA (Atomic Vertical Slice Hybrid)",
                    (
                        f"Active agents: {', '.join([a['name'] for a in session_context['active_agents']])}"
                        if session_context["active_agents"]
                        else "No active agents"
                    ),
                    f"Recent files: {len(session_context['recent_files'])} modified",
                    (
                        f"Frameworks: {', '.join(patterns['frameworks'])}"
                        if patterns["frameworks"]
                        else "No frameworks detected"
                    ),
                    f"Quality score: {summary['quality_score']:.2f}",
                    f"AVSHA Compliance: {summary.get('avsha_status', {}).get('compliance_score', 0.0):.2f}",
                ],
                "context_hints": [
                    "Use /agents command to access specialized sub-agents",
                    "Framework enforces KISS principles and anti-over-engineering",
                    "Follow AVSHA: Atomic Design + Vertical Slice Architecture",
                    "Structure: shared/ for reusable, features/ for domain-specific",
                    "Atomic levels: atoms → molecules → organisms → templates → pages",
                    "All changes must update knowledge graph and embeddings",
                    "Conventional commits required for version control",
                ],
                "avsha_quick_guide": [
                    "Atoms: Basic UI building blocks (buttons, inputs)",
                    "Molecules: Simple composed components (forms, cards)",
                    "Organisms: Complex components with business logic",
                    "Templates: Layout and structure patterns",
                    "Pages: Full application screens",
                    "Features: authentication, optimization, dashboard",
                    "Decision: shared/ vs features/{name}/ based on reusability",
                ],
            },
        }

        # Save context vectors
        self.context_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.context_file, "w") as f:
            json.dump(context_vectors, f, indent=2)

        # Print comprehensive results
        print(f"✅ Context vectors updated with AVSHA analysis:")
        print(f"   📊 Quality score: {summary['quality_score']:.2f}")
        if "avsha_status" in summary:
            avsha_status = summary["avsha_status"]
            print(f"   🏛️ AVSHA Compliance: {avsha_status.get('compliance_score', 0.0):.2f}")
            print(f"   🧩 Atomic Components: {avsha_status.get('atomic_components', 0)}")
            print(f"   🎯 Feature Slices: {avsha_status.get('feature_slices', 0)}")
            print(f"   🔄 Reusability Score: {avsha_status.get('reusability_score', 0.0):.2f}")
            if avsha_status.get("violations", 0) > 0:
                print(f"   ⚠️  Violations: {avsha_status['violations']}")

        # Print recommendations
        if summary["recommendations"]:
            print("💡 Recommendations:")
            for rec in summary["recommendations"]:
                print(f"  - {rec}")

        # Print AVSHA guidance
        if avsha_guidance["patterns"]:
            print("🏛️ AVSHA Patterns:")
            for pattern in avsha_guidance["patterns"]:
                print(f"  - {pattern}")

        return context_vectors


if __name__ == "__main__":
    updater = ContextVectorUpdater()
    updater.update_context_vectors()
