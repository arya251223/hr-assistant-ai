from typing import Dict, Any, List
from .workflow import WorkflowOrchestrator
from ..utils.logger import logger

class CrewManager:
    """High-level manager for agent crews"""
    
    def __init__(self):
        self.orchestrator = WorkflowOrchestrator()
        logger.info("Crew Manager initialized")
    
    def execute_task(
        self,
        task_type: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute specific task type"""
        
        task_handlers = {
            "resume_pipeline": self.orchestrator.execute_resume_pipeline,
            "onboarding": self.orchestrator.execute_onboarding_workflow,
            "query": lambda data: self.orchestrator.handle_query(
                data.get("query", ""),
                data.get("session_id", "default")
            )
        }
        
        handler = task_handlers.get(task_type)
        if not handler:
            return {
                "success": False,
                "error": f"Unknown task type: {task_type}"
            }
        
        try:
            return handler(input_data)
        except Exception as e:
            logger.error(f"Task execution error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        agents = self.orchestrator.registry.list_agents()
        return {
            "success": True,
            "agents": agents,
            "count": len(agents),
            "status": "operational"
        }