from typing import Dict, Any, List
from datetime import datetime

class ContextManager:
    """Manage conversation context across agents"""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_session(self, session_id: str) -> str:
        """Create new conversation session"""
        self.sessions[session_id] = {
            "created_at": datetime.now(),
            "history": [],
            "context": {},
            "current_agent": None
        }
        return session_id
    
    def add_interaction(
        self,
        session_id: str,
        agent: str,
        user_input: str,
        agent_output: Any
    ):
        """Add interaction to session history"""
        if session_id not in self.sessions:
            self.create_session(session_id)
        
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "input": user_input,
            "output": agent_output
        }
        
        self.sessions[session_id]["history"].append(interaction)
        self.sessions[session_id]["current_agent"] = agent
        
        # Maintain max history length
        if len(self.sessions[session_id]["history"]) > self.max_history:
            self.sessions[session_id]["history"].pop(0)
    
    def get_context(self, session_id: str) -> Dict[str, Any]:
        """Get session context"""
        return self.sessions.get(session_id, {}).get("context", {})
    
    def update_context(self, session_id: str, key: str, value: Any):
        """Update session context"""
        if session_id not in self.sessions:
            self.create_session(session_id)
        
        self.sessions[session_id]["context"][key] = value
    
    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.sessions.get(session_id, {}).get("history", [])
    
    def clear_session(self, session_id: str):
        """Clear session data"""
        if session_id in self.sessions:
            del self.sessions[session_id]