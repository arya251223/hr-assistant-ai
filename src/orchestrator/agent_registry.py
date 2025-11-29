from typing import Dict, Any
from ..agents.hr_assistant.agent import HRAssistantAgent
from ..agents.resume_screening.agent import ResumeScreeningAgent
from ..agents.interview.agent import InterviewAgent
from ..agents.onboarding.agent import OnboardingAgent
from ..agents.doc_verification.agent import DocumentVerificationAgent
from ..agents.analytics.agent import AnalyticsAgent
from ..llm.model_router import ModelRouter
from ..utils.logger import logger

class AgentRegistry:
    """Central registry for all agents"""
    
    def __init__(self):
        self.model_router = ModelRouter()
        self.agents: Dict[str, Any] = {}
        self._register_agents()
    
    def _register_agents(self):
        """Initialize and register all agents"""
        logger.info("Registering agents...")
        
        # HR Assistant - uses chat model
        hr_client = self.model_router.get_client("hr_assistant")
        self.agents["hr_assistant"] = HRAssistantAgent(hr_client)
        
        # Resume Screening - uses reasoning model
        resume_client = self.model_router.get_client("resume_screening")
        self.agents["resume_screening"] = ResumeScreeningAgent(resume_client)
        
        # Interview Agent - uses chat model
        interview_client = self.model_router.get_client("interview")
        self.agents["interview"] = InterviewAgent(interview_client)
        
        # Onboarding Agent - uses chat model
        onboarding_client = self.model_router.get_client("onboarding")
        self.agents["onboarding"] = OnboardingAgent(onboarding_client)
        
        # Document Verification - uses reasoning model
        doc_client = self.model_router.get_client("doc_verification")
        self.agents["doc_verification"] = DocumentVerificationAgent(doc_client)
        
        # Analytics Agent - uses reasoning model
        analytics_client = self.model_router.get_client("analytics")
        self.agents["analytics"] = AnalyticsAgent(analytics_client)
        
        logger.info(f"Registered {len(self.agents)} agents")
    
    def get_agent(self, agent_name: str):
        """Get agent by name"""
        agent = self.agents.get(agent_name)
        if not agent:
            logger.warning(f"Agent not found: {agent_name}")
        return agent
    
    def list_agents(self) -> list:
        """List all registered agents"""
        return list(self.agents.keys())
    
    def get_all_agents(self) -> Dict[str, Any]:
        """Get all agents"""
        return self.agents