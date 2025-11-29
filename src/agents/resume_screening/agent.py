import json
import re
from typing import Dict, Any
from ..base_agent import BaseAgent
from .scorer import ResumeScorer
from ...utils.logger import logger

class ResumeScreeningAgent(BaseAgent):
    """Resume Screening Agent - Ranks and scores candidates"""
    
    def __init__(self, llm_client):
        super().__init__("Resume Screening Agent", llm_client)
        self.scorer = ResumeScorer()
        self.prompt_template = self._load_prompt_template(
            "src/agents/resume_screening/prompts.md"
        )
    
    def get_system_prompt(self) -> str:
        return self.prompt_template
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Screen resume against job description"""
        try:
            resume_text = input_data.get("resume", "")
            jd_text = input_data.get("job_description", "")
            
            if not resume_text or not jd_text:
                return {
                    "success": False,
                    "error": "Missing resume or job description"
                }
            
            # Build evaluation prompt
            prompt = f"""
Analyze this resume against the job description and provide a detailed scoring.

JOB DESCRIPTION:
{jd_text}

RESUME:
{resume_text}

Evaluate the candidate and provide your assessment in the exact JSON format specified in your instructions.
"""
            
            # Generate assessment
            response = self.generate_response(prompt, temperature=0.2, max_tokens=2048)
            
            # Parse JSON response
            result = self._parse_json_response(response)
            
            # Add calculated metrics
            if result.get("success"):
                result["match_percentage"] = result.get("score", 0)
                result["agent"] = self.name
            
            return result
            
        except Exception as e:
            logger.error(f"Resume screening error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Extract and parse JSON from LLM response"""
        try:
            # Try to find JSON block
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                data["success"] = True
                return data
            else:
                # Fallback parsing
                return {
                    "success": True,
                    "score": 0,
                    "reasoning": response,
                    "recommendation": "Manual Review"
                }
        except Exception as e:
            logger.error(f"JSON parsing error: {e}")
            return {
                "success": False,
                "error": f"Failed to parse response: {str(e)}",
                "raw_response": response
            }