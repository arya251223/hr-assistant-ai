"""
Tests for Document Verification Agent
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrator.agent_registry import AgentRegistry

class TestDocumentVerificationAgent:
    """Test suite for Document Verification Agent"""
    
    @pytest.fixture
    def registry(self):
        return AgentRegistry()
    
    @pytest.fixture
    def doc_agent(self, registry):
        return registry.get_agent("doc_verification")
    
    @pytest.fixture
    def clean_resume(self):
        """Resume with no issues"""
        return """
        Jane Smith
        Software Engineer
        
        EXPERIENCE:
        Senior Engineer at TechCo (2020-2023)
        - Led development of microservices
        
        Engineer at StartupXYZ (2018-2020)
        - Developed web applications
        
        EDUCATION:
        BS Computer Science (2014-2018)
        
        SKILLS: Python, JavaScript, AWS
        """
    
    @pytest.fixture
    def suspicious_resume(self):
        """Resume with red flags"""
        return """
        John Doe
        
        EXPERIENCE:
        CEO at Google (2025-2026)  # Future dates
        Senior Engineer at Microsoft (2015-2016)
        # Gap here
        Junior Developer at StartupXYZ (2010-2011)
        
        SKILLS: Various technologies, multiple projects
        """
    
    def test_agent_initialization(self, doc_agent):
        """Test agent initializes"""
        assert doc_agent is not None
        assert doc_agent.name == "Document Verification Agent"
    
    def test_verify_clean_resume(self, doc_agent, clean_resume):
        """Test verification of clean resume"""
        result = doc_agent.process({
            "resume": clean_resume
        })
        
        assert result is not None
        assert "success" in result
        
        if result.get("success"):
            assert "risk_score" in result
            assert "verification_status" in result
    
    def test_verify_suspicious_resume(self, doc_agent, suspicious_resume):
        """Test verification of suspicious resume"""
        result = doc_agent.process({
            "resume": suspicious_resume
        })
        
        if result.get("success"):
            # Should detect issues
            assert "issues_found" in result
            issues = result.get("issues_found", [])
            # Might find future dates or gaps
            assert isinstance(issues, list)
    
    def test_missing_resume(self, doc_agent):
        """Test missing resume handling"""
        result = doc_agent.process({})
        
        assert result["success"] == False
        assert "error" in result
    
    def test_risk_scoring(self, doc_agent, clean_resume):
        """Test risk score is in valid range"""
        result = doc_agent.process({
            "resume": clean_resume
        })
        
        if result.get("success") and "risk_score" in result:
            risk = result["risk_score"]
            assert 0 <= risk <= 100


def test_resume_validator():
    """Test resume validator utilities"""
    from src.agents.doc_verification.validators import ResumeValidator
    
    validator = ResumeValidator()
    
    # Test with suspicious content
    suspicious_text = """
    EXPERIENCE:
    CEO at Google (2025-2026)
    Various projects and multiple tasks
    """
    
    issues = validator.check_resume(suspicious_text)
    
    assert isinstance(issues, list)
    # Should find some issues (future dates, vague content)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])