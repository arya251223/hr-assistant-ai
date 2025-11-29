"""
Tests for HR Assistant Agent
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator.agent_registry import AgentRegistry

class TestHRAssistantAgent:
    """Test suite for HR Assistant Agent"""
    
    @pytest.fixture
    def registry(self):
        return AgentRegistry()
    
    @pytest.fixture
    def hr_agent(self, registry):
        return registry.get_agent("hr_assistant")
    
    def test_agent_initialization(self, hr_agent):
        """Test agent initializes"""
        assert hr_agent is not None
        assert hr_agent.name == "HR Assistant Agent"
    
    def test_policy_question(self, hr_agent):
        """Test answering policy question"""
        result = hr_agent.process({
            "query": "What is the sick leave policy?"
        })
        
        assert result is not None
        assert "success" in result
        
        if result.get("success"):
            assert "answer" in result
            assert isinstance(result["answer"], str)
            assert len(result["answer"]) > 0
    
    def test_missing_query(self, hr_agent):
        """Test handling missing query"""
        result = hr_agent.process({})
        
        # Should handle gracefully
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])