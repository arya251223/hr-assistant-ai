from typing import Dict, Any
from ..base_agent import BaseAgent
from .checklist import OnboardingChecklist
from ...utils.logger import logger

class OnboardingAgent(BaseAgent):
    """Onboarding Agent - Guides new employee onboarding"""
    
    def __init__(self, llm_client):
        super().__init__("Onboarding Agent", llm_client)
        self.checklist_manager = OnboardingChecklist()
    
    def get_system_prompt(self) -> str:
        return "You are a friendly HR onboarding specialist."
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process onboarding request"""
        try:
            action = input_data.get("action", "create_plan")
            
            if action == "create_plan":
                return self._create_onboarding_plan(input_data)
            elif action == "update_progress":
                return self._update_progress(input_data)
            elif action == "answer_question":
                return self._answer_question(input_data)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}"
                }
                
        except Exception as e:
            logger.error(f"Onboarding error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_onboarding_plan(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create personalized onboarding plan"""
        employee_name = input_data.get("employee_name", "New Employee")
        role = input_data.get("role", "Employee")
        start_date = input_data.get("start_date", "")
        
        # Get base checklist
        checklist = self.checklist_manager.get_checklist(role)
        
        # Generate SIMPLE welcome message (plain text, not JSON)
        prompt = f"""Write a brief welcome message for {employee_name} starting as {role} on {start_date}.

Include:
1. Welcome greeting
2. One sentence about what to expect first week
3. Who to contact (HR Manager)

Keep it under 100 words and friendly."""
        
        welcome_message = self.generate_response(prompt, temperature=0.6, max_tokens=200)
        
        # Structured response (NOT asking LLM for JSON)
        return {
            "success": True,
            "employee_name": employee_name,
            "role": role,
            "start_date": start_date,
            "welcome_message": welcome_message,  # Plain text string
            "checklist": checklist,
            "completion_percentage": 0,
            "next_steps": [
                "Complete all pre-joining tasks",
                "Prepare required documents",
                "Note your start date and time"
            ]
        }
    
    def _update_progress(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update onboarding progress"""
        task_id = input_data.get("task_id")
        status = input_data.get("status", "completed")
        
        return {
            "success": True,
            "task_id": task_id,
            "status": status,
            "message": f"Task {task_id} marked as {status}"
        }
    
    def _answer_question(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Answer onboarding question"""
        question = input_data.get("question", "")
        
        prompt = f"""Answer this onboarding question briefly:

{question}

Answer in 2-3 sentences:"""
        
        answer = self.generate_response(prompt, temperature=0.3, max_tokens=150)
        
        return {
            "success": True,
            "question": question,
            "answer": answer
        }