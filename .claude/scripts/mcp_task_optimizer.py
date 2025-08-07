#!/usr/bin/env python3
"""
MCP Task Optimizer - Analyzes tasks and recommends optimal MCP server usage
Automatically checks available MCP servers and suggests best tools for the task at hand
"""

import json
import re
import sys
from typing import Dict, List, Optional, Tuple


class MCPTaskOptimizer:
    def __init__(self):
        self.available_servers = {
            "context7": {
                "description": "Documentation and research for libraries",
                "keywords": [
                    "library",
                    "documentation",
                    "framework",
                    "api",
                    "docs",
                    "reference",
                    "research",
                ],
                "capabilities": ["resolve-library-id", "get-library-docs"],
                "domains": ["development", "research", "integration"],
            },
            "sequential-thinking": {
                "description": "Complex multi-step analysis and thinking",
                "keywords": [
                    "analyze",
                    "complex",
                    "multi-step",
                    "reasoning",
                    "logic",
                    "problem-solving",
                    "debug",
                ],
                "capabilities": ["sequentialthinking"],
                "domains": ["analysis", "debugging", "architecture", "planning"],
            },
        }

        # Task analysis patterns
        self.task_patterns = {
            "frontend": [
                "frontend",
                "ui",
                "component",
                "react",
                "next.js",
                "tailwind",
                "responsive",
            ],
            "backend": ["backend", "api", "server", "database", "convex", "fastapi"],
            "ai_integration": ["ai", "ollama", "model", "qwen", "optimization", "prompt"],
            "documentation": ["document", "readme", "wiki", "guide", "explain"],
            "analysis": ["analyze", "investigate", "debug", "troubleshoot", "review"],
            "development": ["develop", "create", "build", "implement", "code"],
            "research": ["research", "find", "lookup", "documentation", "library"],
        }

    def analyze_task_from_stdin(self) -> Optional[Dict]:
        """Read task data from stdin (hook input)"""
        try:
            input_data = sys.stdin.read().strip()
            if not input_data:
                return None

            # Parse JSON input from Claude Code hook
            task_data = json.loads(input_data)
            return task_data
        except (json.JSONDecodeError, Exception):
            # Fallback: treat as plain text task description
            return {"prompt": input_data}

    def extract_task_info(self, task_data: Dict) -> Tuple[str, str, str]:
        """Extract task description, subagent type, and context"""
        prompt = task_data.get("prompt", "")
        subagent_type = task_data.get("subagent_type", "")
        description = task_data.get("description", "")

        # Combine all text for analysis
        full_context = f"{description} {prompt}".lower()

        return full_context, subagent_type, description

    def identify_task_domains(self, task_text: str) -> List[str]:
        """Identify which domains the task relates to"""
        domains = []

        for domain, keywords in self.task_patterns.items():
            if any(keyword in task_text for keyword in keywords):
                domains.append(domain)

        return domains

    def recommend_mcp_servers(self, task_text: str, domains: List[str]) -> List[Dict]:
        """Recommend MCP servers based on task analysis"""
        recommendations = []

        for server_name, server_info in self.available_servers.items():
            score = 0
            reasons = []

            # Check keyword matches
            keyword_matches = sum(1 for keyword in server_info["keywords"] if keyword in task_text)
            if keyword_matches > 0:
                score += keyword_matches * 10
                reasons.append(f"Keywords matched: {keyword_matches}")

            # Check domain alignment
            domain_matches = sum(1 for domain in server_info["domains"] if domain in domains)
            if domain_matches > 0:
                score += domain_matches * 15
                reasons.append(f"Domain alignment: {domain_matches}")

            # Special patterns
            if "documentation" in task_text and server_name == "context7":
                score += 25
                reasons.append("Documentation task detected")

            if (
                any(word in task_text for word in ["complex", "analyze", "multi-step", "debug"])
                and server_name == "sequential-thinking"
            ):
                score += 20
                reasons.append("Complex analysis task detected")

            if score > 0:
                recommendations.append(
                    {
                        "server": server_name,
                        "score": score,
                        "reasons": reasons,
                        "capabilities": server_info["capabilities"],
                        "description": server_info["description"],
                    }
                )

        # Sort by score descending
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations

    def generate_optimization_report(
        self, task_text: str, subagent_type: str, description: str
    ) -> Dict:
        """Generate comprehensive task optimization report"""
        domains = self.identify_task_domains(task_text)
        recommendations = self.recommend_mcp_servers(task_text, domains)

        # Generate optimization suggestions
        suggestions = []

        if recommendations:
            top_server = recommendations[0]
            suggestions.append(
                f"🎯 Recommended MCP Server: {top_server['server']} (score: {top_server['score']})"
            )
            suggestions.append(f"📋 Capabilities: {', '.join(top_server['capabilities'])}")

            for reason in top_server["reasons"]:
                suggestions.append(f"  • {reason}")

        if not recommendations:
            suggestions.append("💡 No specific MCP servers recommended for this task")
            suggestions.append("📝 Consider using native Claude Code tools")

        # Domain-specific suggestions
        if "frontend" in domains and "documentation" in task_text:
            suggestions.append("🔧 Suggestion: Use Context7 for framework documentation")

        if "analysis" in domains or "complex" in task_text:
            suggestions.append("🧠 Suggestion: Use Sequential Thinking for multi-step analysis")

        return {
            "task_domains": domains,
            "recommendations": recommendations[:3],  # Top 3
            "suggestions": suggestions,
            "optimization_score": len(recommendations) * 10 + len(domains) * 5,
        }

    def run(self):
        """Main execution function"""
        # Read task data
        task_data = self.analyze_task_from_stdin()
        if not task_data:
            print("🔍 MCP Task Optimizer: No task data to analyze")
            return

        # Extract and analyze task
        task_text, subagent_type, description = self.extract_task_info(task_data)
        report = self.generate_optimization_report(task_text, subagent_type, description)

        # Output optimization report
        print("🚀 MCP Task Optimizer Report:")
        print(
            f"📊 Task Domains: {', '.join(report['task_domains']) if report['task_domains'] else 'General'}"
        )
        print(f"🎯 Optimization Score: {report['optimization_score']}")

        if report["recommendations"]:
            print("\n🔧 Recommended MCP Servers:")
            for i, rec in enumerate(report["recommendations"], 1):
                print(f"  {i}. {rec['server']} (score: {rec['score']})")
                print(f"     {rec['description']}")

        print("\n💡 Optimization Suggestions:")
        for suggestion in report["suggestions"]:
            print(f"  {suggestion}")

        print("✅ MCP analysis complete - proceeding with task execution\n")


if __name__ == "__main__":
    optimizer = MCPTaskOptimizer()
    optimizer.run()
