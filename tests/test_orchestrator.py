"""
Tests for Orchestration Layer
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator.crew_manager import CrewManager
from src.orchestrator.router import TaskRouter
from src.orchestrator.context_manager import ContextManager

class TestCrewManager:
    """Test suite for CrewManager"""
    
    @pytest.fixture
    def crew(self):
        return CrewManager()
    
    def test_initialization(self, crew):
        """Test crew manager initializes"""
        assert crew is not None
        assert crew.orchestrator is not None
    
    def test_get_agent_status(self, crew):
        """Test agent status retrieval"""
        status = crew.get_agent_status()
        
        assert status is not None
        assert "success" in status
        assert status["success"] == True
        assert "agents" in status
        assert "count" in status
        assert status["count"] == 6  # Should have 6 agents
    
    def test_execute_invalid_task(self, crew):
        """Test handling of invalid task type"""
        result = crew.execute_task("invalid_task", {})
        
        assert result["success"] == False
        assert "error" in result


class TestTaskRouter:
    """Test suite for TaskRouter"""
    
    @pytest.fixture
    def router(self):
        return TaskRouter()
    
    def test_route_hr_query(self, router):
        """Test routing HR policy questions"""
        agent = router.route("What is the leave policy?")
        assert agent == "hr_assistant"
    
    def test_route_resume_screening(self, router):
        """Test routing resume screening tasks"""
        agent = router.route("Screen this resume for the job")
        assert agent == "resume_screening"
    
    def test_route_interview(self, router):
        """Test routing interview tasks"""
        agent = router.route("Generate interview questions")
        assert agent == "interview"
    
    def test_route_onboarding(self, router):
        """Test routing onboarding tasks"""
        agent = router.route("Create onboarding plan for new hire")
        assert agent == "onboarding"
    
    def test_route_verification(self, router):
        """Test routing verification tasks"""
        agent = router.route("Verify this resume for red flags")
        assert agent == "doc_verification"
    
    def test_route_analytics(self, router):
        """Test routing analytics tasks"""
        agent = router.route("Generate analytics report")
        assert agent == "analytics"
    
    def test_route_unknown_query(self, router):
        """Test routing of unknown queries"""
        agent = router.route("Random unrelated query")
        # Should default to HR assistant
        assert agent == "hr_assistant"


class TestContextManager:
    """Test suite for ContextManager"""
    
    @pytest.fixture
    def context_mgr(self):
        return ContextManager()
    
    def test_create_session(self, context_mgr):
        """Test session creation"""
        session_id = context_mgr.create_session("test_session")
        assert session_id == "test_session"
        assert "test_session" in context_mgr.sessions
    
    def test_add_interaction(self, context_mgr):
        """Test adding interaction to session"""
        session_id = "test_session"
        context_mgr.create_session(session_id)
        
        context_mgr.add_interaction(
            session_id,
            "hr_assistant",
            "What is the policy?",
            {"answer": "Policy details..."}
        )
        
        history = context_mgr.get_history(session_id)
        assert len(history) == 1
        assert history[0]["agent"] == "hr_assistant"
    
    def test_update_context(self, context_mgr):
        """Test context update"""
        session_id = "test_session"
        context_mgr.create_session(session_id)
        
        context_mgr.update_context(session_id, "user_name", "John Doe")
        
        context = context_mgr.get_context(session_id)
        assert context["user_name"] == "John Doe"
    
    def test_clear_session(self, context_mgr):
        """Test session clearing"""
        session_id = "test_session"
        context_mgr.create_session(session_id)
        context_mgr.update_context(session_id, "test", "value")
        
        context_mgr.clear_session(session_id)
        
        assert session_id not in context_mgr.sessions


if __name__ == "__main__":
    pytest.main([__file__, "-v"])