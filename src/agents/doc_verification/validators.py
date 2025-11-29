import re
from typing import List, Dict, Any
from datetime import datetime

class ResumeValidator:
    """Rule-based resume validation"""
    
    def check_resume(self, resume_text: str) -> List[Dict[str, Any]]:
        """Run all validation checks"""
        issues = []
        
        # Check for employment gaps
        gap_issues = self._check_employment_gaps(resume_text)
        issues.extend(gap_issues)
        
        # Check date consistency
        date_issues = self._check_date_consistency(resume_text)
        issues.extend(date_issues)
        
        # Check for vague descriptions
        vague_issues = self._check_vague_content(resume_text)
        issues.extend(vague_issues)
        
        return issues
    
    def _check_employment_gaps(self, text: str) -> List[Dict[str, Any]]:
        """Check for employment gaps"""
        # Simple pattern matching for dates
        date_pattern = r'(20\d{2}|19\d{2})'
        years = re.findall(date_pattern, text)
        
        if years:
            years = sorted([int(y) for y in set(years)])
            gaps = []
            
            for i in range(len(years) - 1):
                if years[i+1] - years[i] > 2:
                    gaps.append({
                        "type": "employment_gap",
                        "severity": "medium",
                        "description": f"Potential gap between {years[i]} and {years[i+1]}",
                        "recommendation": "Verify employment continuity"
                    })
            
            return gaps
        
        return []
    
    def _check_date_consistency(self, text: str) -> List[Dict[str, Any]]:
        """Check for date inconsistencies"""
        issues = []
        
        # Check for future dates
        current_year = datetime.now().year
        future_pattern = r'(20[3-9]\d|2[1-9]\d{2})'
        future_dates = re.findall(future_pattern, text)
        
        if future_dates:
            issues.append({
                "type": "future_date",
                "severity": "high",
                "description": "Resume contains future dates",
                "recommendation": "Verify date accuracy"
            })
        
        return issues
    
    def _check_vague_content(self, text: str) -> List[Dict[str, Any]]:
        """Check for overly vague descriptions"""
        vague_phrases = [
            "various projects",
            "multiple tasks",
            "responsible for",
            "worked on",
            "involved in"
        ]
        
        issues = []
        text_lower = text.lower()
        vague_count = sum(1 for phrase in vague_phrases if phrase in text_lower)
        
        if vague_count > 5:
            issues.append({
                "type": "vague_content",
                "severity": "low",
                "description": "Resume contains many vague descriptions",
                "recommendation": "Request specific achievements and metrics"
            })
        
        return issues