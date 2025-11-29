

## 📄 FILE 26: `src/agents/analytics/agent.py`

import json
from typing import Dict, Any, List
from collections import Counter
from ..base_agent import BaseAgent
from .report_gen import ReportGenerator
from ...utils.logger import logger

class AnalyticsAgent(BaseAgent):
    """Analytics Agent - Generates HR insights and reports"""
    
    def __init__(self, llm_client):
        super().__init__("HR Analytics Agent", llm_client)
        self.report_gen = ReportGenerator()
        self.prompt_template = self._load_prompt_template(
            "src/agents/analytics/prompts.md"
        )
        self.data_store = []
    
    def get_system_prompt(self) -> str:
        return self.prompt_template
    
    def add_data(self, data: Dict[str, Any]):
        """Add data point for analysis"""
        self.data_store.append(data)
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analytics report"""
        try:
            report_type = input_data.get("report_type", "summary")
            data_points = input_data.get("data", self.data_store)
            
            if report_type == "summary":
                return self._generate_summary(data_points)
            elif report_type == "pipeline":
                return self._generate_pipeline_report(data_points)
            elif report_type == "skills":
                return self._generate_skill_analysis(data_points)
            else:
                return {
                    "success": False,
                    "error": f"Unknown report type: {report_type}"
                }
                
        except Exception as e:
            logger.error(f"Analytics error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_summary(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate overall summary"""
        # Calculate basic metrics
        total_candidates = len(data)
        resume_scores = [d.get("resume_score", 0) for d in data if "resume_score" in d]
        interview_scores = [d.get("interview_score", 0) for d in data if "interview_score" in d]
        
        avg_resume = sum(resume_scores) / len(resume_scores) if resume_scores else 0
        avg_interview = sum(interview_scores) / len(interview_scores) if interview_scores else 0
        
        # Generate AI insights
        prompt = f"""
Analyze this HR data and provide insights:

Total Candidates: {total_candidates}
Average Resume Score: {avg_resume:.2f}
Average Interview Score: {avg_interview:.2f}

Provide:
1. 3 key insights
2. 3 actionable recommendations
3. Trends observed

Be specific and data-driven.
"""
        
        ai_insights = self.generate_response(prompt, temperature=0.3, max_tokens=512)
        
        return {
            "success": True,
            "summary": {
                "total_candidates": total_candidates,
                "avg_resume_score": round(avg_resume, 2),
                "avg_interview_score": round(avg_interview, 2)
            },
            "ai_insights": ai_insights,
            "generated_at": self.report_gen.get_timestamp()
        }
    
    def _generate_pipeline_report(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate pipeline metrics"""
        stages = {
            "applied": 0,
            "screening_passed": 0,
            "interviewed": 0,
            "offer": 0,
            "hired": 0
        }
        
        for candidate in data:
            stages["applied"] += 1
            if candidate.get("resume_score", 0) >= 70:
                stages["screening_passed"] += 1
            if candidate.get("interview_score", 0) >= 7:
                stages["interviewed"] += 1
            if candidate.get("offer_made"):
                stages["offer"] += 1
            if candidate.get("hired"):
                stages["hired"] += 1
        
        return {
            "success": True,
            "pipeline_status": stages,
            "conversion_rates": {
                "screening": f"{stages['screening_passed']/max(stages['applied'], 1)*100:.1f}%",
                "interview": f"{stages['interviewed']/max(stages['screening_passed'], 1)*100:.1f}%",
                "offer": f"{stages['offer']/max(stages['interviewed'], 1)*100:.1f}%"
            }
        }
    
    def _generate_skill_analysis(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze skill gaps"""
        all_skills = []
        missing_skills = []
        
        for candidate in data:
            all_skills.extend(candidate.get("skills_matched", []))
            missing_skills.extend(candidate.get("skills_missing", []))
        
        skill_counts = Counter(all_skills)
        gap_counts = Counter(missing_skills)
        
        return {
            "success": True,
            "most_common_skills": dict(skill_counts.most_common(10)),
            "skill_gaps": dict(gap_counts.most_common(10)),
            "analysis": f"Analyzed {len(data)} candidates"
        }