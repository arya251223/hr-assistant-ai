import json
import re
from typing import Dict, Any, List
from ..base_agent import BaseAgent
from .validators import ResumeValidator
from ...utils.logger import logger

class DocumentVerificationAgent(BaseAgent):
    """Document Verification Agent - Verifies resume credibility"""
    
    def __init__(self, llm_client):
        super().__init__("Document Verification Agent", llm_client)
        self.validator = ResumeValidator()
        self.prompt_template = self._load_prompt_template(
            "src/agents/doc_verification/prompts.md"
        )
    
    def get_system_prompt(self) -> str:
        return self.prompt_template
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify resume document"""
        try:
            resume_text = input_data.get("resume", "")
            
            if not resume_text:
                return {
                    "success": False,
                    "error": "No resume provided"
                }
            
            # Run rule-based checks
            rule_based_issues = self.validator.check_resume(resume_text)
            
            # LLM-based analysis
            prompt = f"""
Analyze this resume for credibility and consistency:

RESUME:
{resume_text}

Identify:
1. Any inconsistencies or red flags
2. Suspicious claims
3. Timeline issues
4. Skill-experience mismatches

Provide detailed verification report in JSON format as specified.
"""
            
            response = self.generate_response(prompt, temperature=0.1, max_tokens=2048)
            
            # Parse verification result
            verification = self._parse_verification(response)
            
            # Merge rule-based and LLM findings
            all_issues = rule_based_issues + verification.get("issues_found", [])
            
            # Calculate final risk score
            risk_score = self._calculate_risk_score(all_issues)
            
            return {
                "success": True,
                "verification_status": self._get_status(risk_score),
                "risk_score": risk_score,
                "issues_found": all_issues,
                "recommendations": verification.get("recommendations", []),
                "agent": self.name
            }
            
        except Exception as e:
            logger.error(f"Document verification error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_verification(self, response: str) -> Dict[str, Any]:
        """Parse verification response"""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            
            return {
                "issues_found": [],
                "recommendations": [],
                "raw_analysis": response
            }
        except Exception as e:
            logger.warning(f"Verification parsing failed: {e}")
            return {
                "issues_found": [],
                "recommendations": []
            }
    
    def _calculate_risk_score(self, issues: List[Dict[str, Any]]) -> int:
        """Calculate overall risk score"""
        severity_weights = {
            "critical": 30,
            "high": 20,
            "medium": 10,
            "low": 5
        }
        
        total_score = 0
        for issue in issues:
            severity = issue.get("severity", "low")
            total_score += severity_weights.get(severity, 5)
        
        return min(total_score, 100)
    
    def _get_status(self, risk_score: int) -> str:
        """Get verification status"""
        if risk_score <= 25:
            return "verified"
        elif risk_score <= 50:
            return "suspicious"
        else:
            return "high_risk"