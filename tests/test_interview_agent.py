"""
Tests for Interview Agent
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator.agent_registry import AgentRegistry

class TestInterviewAgent:
    """Test suite for Interview Agent"""
    
    @pytest.fixture
    def registry(self):
        return AgentRegistry()
    
    @pytest.fixture
    def interview_agent(self, registry):
        return registry.get_agent("interview")
    
    def test_agent_initialization(self, interview_agent):
        """Test agent initializes"""
        assert interview_agent is not None
        assert interview_agent.name == "Interview Agent"
    
    def test_generate_questions(self, interview_agent):
        """Test question generation"""
        result = interview_agent.generate_questions({
            "job_role": "Software Engineer",
            "job_description": "Python developer with cloud experience",
            "num_questions": 3
        })
        
        assert result is not None
        assert "success" in result
        
        if result.get("success"):
            assert "questions" in result
            questions = result["questions"]
            assert isinstance(questions, list)
            assert len(questions) > 0
    
    def test_evaluate_answer(self, interview_agent):
        """Test answer evaluation"""
        result = interview_agent.process({
            "question": "What is polymorphism in OOP?",
            "answer": "Polymorphism allows objects of different classes to be treated as objects of a common base class."
        })
        
        assert result is not None
        assert "success" in result
        
        if result.get("success"):
            assert "evaluation" in result
            eval_data = result["evaluation"]
            assert "score" in eval_data or "feedback" in eval_data
    
    def test_missing_question(self, interview_agent):
        """Test missing question handling"""
        result = interview_agent.process({
            "answer": "Some answer"
        })
        
        assert result["success"] == False
    
    def test_missing_answer(self, interview_agent):
        """Test missing answer handling"""
        result = interview_agent.process({
            "question": "What is Python?"
        })
        
        assert result["success"] == False


def test_interview_evaluator():
    """Test interview evaluator utilities"""
    from src.agents.interview.evaluator import InterviewEvaluator
    
    evaluator = InterviewEvaluator()
    
    # Test recommendation logic
    assert evaluator.get_recommendation(9.0) == "Strong Hire"
    assert evaluator.get_recommendation(7.5) == "Hire"
    assert evaluator.get_recommendation(6.0) == "Maybe"
    assert evaluator.get_recommendation(4.0) == "No Hire"
    
    # Test weighted scoring
    scores = [
        {"category": "technical", "score": 8},
        {"category": "behavioral", "score": 7}
    ]
    weights = {"technical": 0.7, "behavioral": 0.3}
    
    weighted = evaluator.calculate_weighted_score(scores, weights)
    assert 0 <= weighted <= 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])