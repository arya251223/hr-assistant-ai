"""
Task Router - Routes user queries to appropriate agents
"""
from typing import Dict, Any, Optional, List
from ..utils.logger import logger


class TaskRouter:
    """Route user requests to appropriate agents"""
    
    def __init__(self):
        """Initialize router with routing rules"""
        self.routing_rules = self._initialize_rules()
        logger.info("TaskRouter initialized successfully")
    
    def _initialize_rules(self) -> Dict[str, List[str]]:
        """Define routing keywords for each agent"""
        return {
            "hr_assistant": [
                "policy", "leave", "benefits", "reimbursement", 
                "attendance", "vacation", "sick leave", "hr question",
                "holiday", "time off", "pto", "insurance", "health"
            ],
            "resume_screening": [
                "resume", "cv", "screen", "candidate", "evaluate resume",
                "match resume", "score candidate", "application", "applicant"
            ],
            "interview": [
                "interview", "questions", "evaluate answer", "assessment",
                "interview feedback", "candidate evaluation", "interview score"
            ],
            "onboarding": [
                "onboarding", "new hire", "joining", "orientation",
                "first day", "onboard", "new employee", "welcome"
            ],
            "doc_verification": [
                "verify", "verification", "check resume", "validate",
                "credibility", "red flag", "fraud", "suspicious"
            ],
            "analytics": [
                "analytics", "report", "metrics", "dashboard",
                "insights", "statistics", "summary", "data", "analysis"
            ]
        }
    
    def route(self, user_input: str) -> str:
        """
        Determine which agent should handle the request
        
        Args:
            user_input: User's query string
            
        Returns:
            Agent name (str)
        """
        if not user_input:
            logger.warning("Empty user input, defaulting to hr_assistant")
            return "hr_assistant"
        
        user_input_lower = user_input.lower()

        if "verify" in user_input_lower or "validation" in user_input_lower or "credibility" in user_input_lower:
        # Check if it's about documents/resume verification (not just resume screening)
            if "resume" in user_input_lower or "document" in user_input_lower or "credential" in user_input_lower:
                logger.info("Routing to: doc_verification (verify keyword detected)")
                return "doc_verification"
        
        # Score each agent based on keyword matches
        scores = {}
        for agent, keywords in self.routing_rules.items():
            score = sum(1 for kw in keywords if kw in user_input_lower)
            if score > 0:
                scores[agent] = score
        
        if not scores:
            # Default to HR assistant for general queries
            logger.info("No specific agent matched, routing to hr_assistant")
            return "hr_assistant"
        
        # Return agent with highest score
        best_agent = max(scores.items(), key=lambda x: x[1])[0]
        logger.info(f"Routing to: {best_agent} (score: {scores[best_agent]})")
        return best_agent
    
    def route_explicit(self, task_type: str) -> Optional[str]:
        """
        Explicit routing by task type
        
        Args:
            task_type: Specific agent name
            
        Returns:
            Agent name if valid, None otherwise
        """
        valid_agents = list(self.routing_rules.keys())
        if task_type in valid_agents:
            logger.info(f"Explicit routing to: {task_type}")
            return task_type
        
        logger.warning(f"Invalid task type: {task_type}")
        return None
    
    def get_available_agents(self) -> List[str]:
        """Get list of all available agents"""
        return list(self.routing_rules.keys())