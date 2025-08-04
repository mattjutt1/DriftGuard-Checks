#!/usr/bin/env python3
"""
Knowledge Graph Update Script for PromptEvolver
Automatically updates the contextual knowledge graph after code changes
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
import subprocess

class KnowledgeGraphUpdater:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.graph_file = self.project_root / ".claude" / "knowledge_graph.json"
        self.embeddings_file = self.project_root / ".claude" / "embeddings.json"
        
    def load_graph(self):
        """Load existing knowledge graph or create new one"""
        if self.graph_file.exists():
            with open(self.graph_file, 'r') as f:
                return json.load(f)
        return self.create_empty_graph()
    
    def create_empty_graph(self):
        """Create empty knowledge graph structure"""
        return {
            "metadata": {
                "created": datetime.now().isoformat(),
                "version": "1.0",
                "last_updated": datetime.now().isoformat()
            },
            "entities": {
                "files": {},
                "functions": {},
                "classes": {},
                "agents": {},
                "decisions": {}
            },
            "relationships": {},
            "context_vectors": {
                "current_session": [],
                "recent_changes": [],
                "architectural_patterns": [],
                "quality_metrics": []
            }
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
                "size": py_file.stat().st_size
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
                    "last_modified": datetime.fromtimestamp(agent_file.stat().st_mtime).isoformat()
                }
        
        return entities
    
    def get_file_hash(self, file_path):
        """Generate hash for file content"""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def detect_changes(self, current_entities, previous_entities):
        """Detect changes between current and previous state"""
        changes = {
            "added": [],
            "modified": [],
            "deleted": []
        }
        
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
                        with open(file_path, 'r') as f:
                            content = f.read()
                            # Extract imports
                            imports = self.extract_imports(content)
                            graph["relationships"][change["id"]] = {
                                "imports": imports,
                                "timestamp": datetime.now().isoformat()
                            }
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")
        
        return graph
    
    def extract_imports(self, content):
        """Extract import statements from Python code"""
        imports = []
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                imports.append(line)
        return imports
    
    def save_graph(self, graph):
        """Save knowledge graph to file"""
        graph["metadata"]["last_updated"] = datetime.now().isoformat()
        
        # Ensure directory exists
        self.graph_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.graph_file, 'w') as f:
            json.dump(graph, f, indent=2)
    
    def update(self):
        """Main update method"""
        print("🧠 Updating knowledge graph...")
        
        # Load existing graph
        graph = self.load_graph()
        
        # Scan current project state
        current_entities = self.scan_project_files()
        
        # Detect changes
        changes = self.detect_changes(current_entities, graph["entities"])
        
        # Update entities
        graph["entities"] = current_entities
        
        # Update relationships
        graph = self.update_relationships(graph, changes)
        
        # Update context vectors
        graph["context_vectors"]["recent_changes"] = changes
        graph["context_vectors"]["last_scan"] = datetime.now().isoformat()
        
        # Save graph
        self.save_graph(graph)
        
        print(f"✅ Knowledge graph updated - {len(changes['added'])} added, {len(changes['modified'])} modified, {len(changes['deleted'])} deleted")
        
        return changes

if __name__ == "__main__":
    updater = KnowledgeGraphUpdater()
    changes = updater.update()