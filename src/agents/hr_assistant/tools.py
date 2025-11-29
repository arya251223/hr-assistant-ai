from pathlib import Path
from typing import Dict, List
from ...utils.file_loader import FileLoader
from ...utils.logger import logger

class PolicySearchTool:
    """Search and retrieve HR policy documents"""
    
    def __init__(self, policy_dir: str):
        self.policy_dir = Path(policy_dir)
        self.policies = self._load_policies()
    
    def _load_policies(self) -> Dict[str, str]:
        """Load all policy documents"""
        policies = {}
        
        if not self.policy_dir.exists():
            logger.warning(f"Policy directory not found: {self.policy_dir}")
            return policies
        
        for file in self.policy_dir.iterdir():
            if file.suffix in ['.md', '.txt']:
                content = FileLoader.load_file(str(file))
                policies[file.name] = content
        
        logger.info(f"Loaded {len(policies)} policy documents")
        return policies
    
    def search(self, query: str, top_k: int = 3) -> Dict[str, str]:
        """Simple keyword-based search"""
        query_lower = query.lower()
        scores = {}
        
        for name, content in self.policies.items():
            # Simple scoring: count keyword matches
            score = sum(1 for word in query_lower.split() if word in content.lower())
            if score > 0:
                scores[name] = score
        
        # Return top k documents
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        
        return {name: self.policies[name] for name, _ in sorted_docs}
    
    def get_all_policies(self) -> Dict[str, str]:
        """Return all policies"""
        return self.policies