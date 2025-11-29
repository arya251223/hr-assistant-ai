from typing import Dict, List, Set
import re

class ResumeScorer:
    """Deterministic scoring utilities for resume screening"""
    
    def extract_skills(self, text: str) -> Set[str]:
        """Extract technical skills from text"""
        # Common tech skills patterns
        skill_keywords = [
            'python', 'java', 'javascript', 'typescript', 'c\\+\\+', 'c#',
            'react', 'angular', 'vue', 'node.js', 'django', 'flask',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes',
            'sql', 'postgresql', 'mongodb', 'redis',
            'machine learning', 'deep learning', 'nlp', 'computer vision',
            'git', 'ci/cd', 'agile', 'scrum'
        ]
        
        text_lower = text.lower()
        found_skills = set()
        
        for skill in skill_keywords:
            if re.search(r'\b' + skill + r'\b', text_lower):
                found_skills.add(skill.replace('\\', ''))
        
        return found_skills
    
    def extract_years_experience(self, text: str) -> int:
        """Extract years of experience"""
        # Look for patterns like "5 years", "5+ years"
        patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'experience.*?(\d+)\+?\s*years?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        return 0
    
    def calculate_skill_match_score(
        self,
        resume_skills: Set[str],
        required_skills: Set[str]
    ) -> float:
        """Calculate skill match percentage"""
        if not required_skills:
            return 100.0
        
        matched = resume_skills.intersection(required_skills)
        return (len(matched) / len(required_skills)) * 100
    
    def determine_seniority(self, years: int) -> str:
        """Determine seniority level"""
        if years >= 7:
            return "senior"
        elif years >= 3:
            return "mid"
        elif years >= 1:
            return "junior"
        else:
            return "entry"