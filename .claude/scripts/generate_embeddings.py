#!/usr/bin/env python3
"""
Embedding Generation Script for PromptEvolver
Generates contextual embeddings for the knowledge graph
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
import numpy as np

class EmbeddingGenerator:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.embeddings_file = self.project_root / ".claude" / "embeddings.json"
        self.graph_file = self.project_root / ".claude" / "knowledge_graph.json"
        
    def load_knowledge_graph(self):
        """Load the knowledge graph"""
        if self.graph_file.exists():
            with open(self.graph_file, 'r') as f:
                return json.load(f)
        return {}
    
    def simple_text_embedding(self, text, dimension=384):
        """Generate a simple text embedding (placeholder for real embedding model)"""
        # This is a simplified embedding - in production, use actual models
        # like sentence-transformers, OpenAI embeddings, etc.
        
        # Create a hash-based embedding for consistency
        text_hash = hashlib.md5(text.encode()).digest()
        
        # Convert to pseudo-embedding vector
        embedding = []
        for i in range(0, min(len(text_hash), dimension // 8)):
            byte_val = text_hash[i]
            # Convert byte to multiple float values
            for j in range(8):
                bit = (byte_val >> j) & 1
                embedding.append(float(bit) * 2.0 - 1.0)  # Convert to -1 or 1
        
        # Pad or truncate to desired dimension
        while len(embedding) < dimension:
            embedding.append(0.0)
        
        return embedding[:dimension]
    
    def generate_code_embedding(self, code_content):
        """Generate embedding for code content"""
        # Extract key code features for embedding
        features = []
        
        # Function/class definitions
        lines = code_content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('def ') or line.startswith('class '):
                features.append(line)
            elif line.startswith('import ') or line.startswith('from '):
                features.append(line)
        
        # Combine features for embedding
        feature_text = ' '.join(features) + ' ' + code_content[:500]  # First 500 chars
        return self.simple_text_embedding(feature_text)
    
    def generate_agent_embedding(self, agent_content):
        """Generate embedding for agent description"""
        # Extract agent metadata and description
        lines = agent_content.split('\n')
        
        # Find description and core responsibilities
        description_text = ""
        capture_content = False
        
        for line in lines:
            line = line.strip()
            if line.startswith('description:'):
                description_text += line + ' '
            elif line.startswith('## Your Core Responsibilities:'):
                capture_content = True
            elif capture_content and line.startswith('##'):
                break
            elif capture_content and line.startswith('-'):
                description_text += line + ' '
        
        return self.simple_text_embedding(description_text)
    
    def generate_architectural_embedding(self, decisions):
        """Generate embedding for architectural decisions"""
        decision_text = json.dumps(decisions, separators=(',', ':'))
        return self.simple_text_embedding(decision_text)
    
    def generate_embeddings_for_graph(self, graph):
        """Generate embeddings for all entities in the knowledge graph"""
        embeddings = {
            "metadata": {
                "generated": datetime.now().isoformat(),
                "model": "simple_hash_embedding",
                "dimension": 384
            },
            "embeddings": {}
        }
        
        # Generate embeddings for files
        for file_path, file_data in graph.get("entities", {}).get("files", {}).items():
            try:
                file_path_obj = Path(file_path)
                if file_path_obj.exists():
                    with open(file_path_obj, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if file_path.endswith('.py'):
                        embedding = self.generate_code_embedding(content)
                    else:
                        embedding = self.simple_text_embedding(content[:1000])
                    
                    embeddings["embeddings"][file_path] = {
                        "type": "file",
                        "embedding": embedding,
                        "hash": file_data.get("hash", "")
                    }
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
        
        # Generate embeddings for agents
        for agent_name, agent_data in graph.get("entities", {}).get("agents", {}).items():
            try:
                agent_file = Path(agent_data.get("file", ""))
                if agent_file.exists():
                    with open(agent_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    embedding = self.generate_agent_embedding(content)
                    embeddings["embeddings"][f"agent:{agent_name}"] = {
                        "type": "agent",
                        "embedding": embedding,
                        "hash": agent_data.get("hash", "")
                    }
            except Exception as e:
                print(f"Error processing agent {agent_name}: {e}")
        
        # Generate embeddings for architectural decisions
        decisions = graph.get("entities", {}).get("decisions", {})
        if decisions:
            embedding = self.generate_architectural_embedding(decisions)
            embeddings["embeddings"]["architecture:decisions"] = {
                "type": "architecture",
                "embedding": embedding,
                "hash": hashlib.md5(json.dumps(decisions).encode()).hexdigest()
            }
        
        return embeddings
    
    def calculate_similarity(self, embedding1, embedding2):
        """Calculate cosine similarity between two embeddings"""
        try:
            # Convert to numpy arrays
            e1 = np.array(embedding1)
            e2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(e1, e2)
            norm1 = np.linalg.norm(e1)
            norm2 = np.linalg.norm(e2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception:
            return 0.0
    
    def find_similar_entities(self, embeddings, target_embedding, threshold=0.7):
        """Find entities similar to target embedding"""
        similar = []
        
        for entity_id, entity_data in embeddings["embeddings"].items():
            similarity = self.calculate_similarity(
                target_embedding, 
                entity_data["embedding"]
            )
            
            if similarity >= threshold:
                similar.append({
                    "entity": entity_id,
                    "similarity": similarity,
                    "type": entity_data["type"]
                })
        
        return sorted(similar, key=lambda x: x["similarity"], reverse=True)
    
    def save_embeddings(self, embeddings):
        """Save embeddings to file"""
        # Ensure directory exists
        self.embeddings_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.embeddings_file, 'w') as f:
            json.dump(embeddings, f, indent=2)
    
    def generate(self):
        """Main embedding generation method"""
        print("🧠 Generating contextual embeddings...")
        
        # Load knowledge graph
        graph = self.load_knowledge_graph()
        
        if not graph:
            print("No knowledge graph found - run update_knowledge_graph.py first")
            return
        
        # Generate embeddings
        embeddings = self.generate_embeddings_for_graph(graph)
        
        # Save embeddings
        self.save_embeddings(embeddings)
        
        total_embeddings = len(embeddings["embeddings"])
        print(f"✅ Generated {total_embeddings} contextual embeddings")
        
        return embeddings

if __name__ == "__main__":
    generator = EmbeddingGenerator()
    generator.generate()