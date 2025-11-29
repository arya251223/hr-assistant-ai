from typing import Dict, List, Any

class OnboardingChecklist:
    """Manage onboarding checklists"""
    
    def __init__(self):
        self.checklists = self._initialize_checklists()
    
    def _initialize_checklists(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize role-based checklists"""
        base_checklist = [
            {
                "phase": "Pre-Joining",
                "tasks": [
                    {"id": 1, "task": "Sign offer letter", "status": "pending"},
                    {"id": 2, "task": "Complete background verification", "status": "pending"},
                    {"id": 3, "task": "Submit required documents", "status": "pending"}
                ]
            },
            {
                "phase": "Day 1",
                "tasks": [
                    {"id": 4, "task": "Attend orientation", "status": "pending"},
                    {"id": 5, "task": "Receive IT equipment", "status": "pending"},
                    {"id": 6, "task": "Setup email and accounts", "status": "pending"},
                    {"id": 7, "task": "Office tour", "status": "pending"}
                ]
            },
            {
                "phase": "Week 1",
                "tasks": [
                    {"id": 8, "task": "Meet your buddy", "status": "pending"},
                    {"id": 9, "task": "Complete HR policy training", "status": "pending"},
                    {"id": 10, "task": "Setup development environment", "status": "pending"}
                ]
            },
            {
                "phase": "First Month",
                "tasks": [
                    {"id": 11, "task": "Complete role training", "status": "pending"},
                    {"id": 12, "task": "First project assignment", "status": "pending"},
                    {"id": 13, "task": "30-day check-in meeting", "status": "pending"}
                ]
            }
        ]
        
        return {
            "default": base_checklist,
            "software engineer": base_checklist,
            "data scientist": base_checklist,
            "product manager": base_checklist
        }
    
    def get_checklist(self, role: str) -> List[Dict[str, Any]]:
        """Get checklist for specific role"""
        role_lower = role.lower()
        return self.checklists.get(role_lower, self.checklists["default"])
    
    def calculate_completion(self, checklist: List[Dict[str, Any]]) -> float:
        """Calculate completion percentage"""
        total_tasks = 0
        completed_tasks = 0
        
        for phase in checklist:
            for task in phase.get("tasks", []):
                total_tasks += 1
                if task.get("status") == "completed":
                    completed_tasks += 1
        
        return (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0