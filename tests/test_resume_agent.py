"""
Tests for Resume Screening Agent
"""
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator.agent_registry import AgentRegistry

class TestResumeScreeningAgent:
    """Test suite for Resume Screening Agent"""
    
    @pytest.fixture
    def registry(self):
        """Initialize agent registry"""
        return AgentRegistry()
    
    @pytest.fixture
    def resume_agent(self, registry):
        """Get resume screening agent"""
        return registry.get_agent("resume_screening")
    
    @pytest.fixture
    def sample_resume(self):
        """Sample resume text"""
        return """
        John Doe
        Software Engineer
        
        SKILLS: Python, JavaScript, React, AWS, Docker
        
        EXPERIENCE:
        Senior Software Engineer at Tech Corp (2020-2023)
        - Developed microservices using Python and Docker
        - Led team of 5 engineers
        
        Software Engineer at StartupXYZ (2018-2020)
        - Built RESTful APIs
        - Worked with AWS cloud services
        
        EDUCATION:
        BS Computer Science, University of Tech (2014-2018)
        """
    
    @pytest.fixture
    def sample_jd(self):
        """Sample job description"""
        return """
        Senior Software Engineer
        
        Requirements:
        - 5+ years of Python development
        - Experience with AWS
        - Docker and containerization
        - React or Vue.js
        - Microservices architecture
        
        Skills: Python, AWS, Docker, React, Kubernetes
        """
    
    def test_agent_initialization(self, resume_agent):
        """Test agent initializes correctly"""
        assert resume_agent is not None
        assert resume_agent.name == "Resume Screening Agent"
    
    def test_resume_screening_basic(self, resume_agent, sample_resume, sample_jd):
        """Test basic resume screening"""
        result = resume_agent.process({
            "resume": sample_resume,
            "job_description": sample_jd
        })
        
        assert result is not None
        assert "success" in result
        
        if result.get("success"):
            assert "score" in result
            assert isinstance(result["score"], (int, float))
            assert 0 <= result["score"] <= 100
    
    def test_missing_resume(self, resume_agent):
        """Test handling of missing resume"""
        result = resume_agent.process({
            "job_description": "Some JD"
        })
        
        assert result["success"] == False
        assert "error" in result
    
    def test_missing_jd(self, resume_agent, sample_resume):
        """Test handling of missing job description"""
        result = resume_agent.process({
            "resume": sample_resume
        })
        
        assert result["success"] == False
        assert "error" in result
    
    def test_skills_extraction(self, resume_agent, sample_resume, sample_jd):
        """Test skills are properly extracted"""
        result = resume_agent.process({
            "resume": sample_resume,
            "job_description": sample_jd
        })
        
        if result.get("success"):
            # Should have skills_matched or skills_missing
            has_skills = ("skills_matched" in result or 
                         "skills_missing" in result or
                         "reasoning" in result)
            assert has_skills
    
    def test_score_range(self, resume_agent, sample_resume, sample_jd):
        """Test score is within valid range"""
        result = resume_agent.process({
            "resume": sample_resume,
            "job_description": sample_jd
        })
        
        if result.get("success") and "score" in result:
            score = result["score"]
            assert 0 <= score <= 100, f"Score {score} out of range"


def test_resume_scorer():
    """Test resume scoring utilities"""
    from src.agents.resume_screening.scorer import ResumeScorer
    
    scorer = ResumeScorer()
    
    # Test skill extraction
    text = "I have experience with Python, JavaScript, and AWS"
    skills = scorer.extract_skills(text)
    
    assert isinstance(skills, set)
    assert "python" in skills or "javascript" in skills
    
    # Test years extraction
    text = "5 years of experience in software development"
    years = scorer.extract_years_experience(text)
    
    assert years == 5
    
    # Test skill match calculation
    resume_skills = {"python", "javascript", "aws"}
    required_skills = {"python", "aws", "docker"}
    
    match_score = scorer.calculate_skill_match_score(resume_skills, required_skills)
    
    assert 0 <= match_score <= 100
    assert match_score > 0  # Should have some match


if __name__ == "__main__":
    pytest.main([__file__, "-v"])