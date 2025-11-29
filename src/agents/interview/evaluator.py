from typing import Dict, List

class InterviewEvaluator:
    """Utilities for interview evaluation"""
    
    def get_recommendation(self, average_score: float) -> str:
        """Get hiring recommendation based on score"""
        if average_score >= 8.5:
            return "Strong Hire"
        elif average_score >= 7.0:
            return "Hire"
        elif average_score >= 5.5:
            return "Maybe"
        else:
            return "No Hire"
    
    def calculate_weighted_score(
        self,
        scores: List[Dict[str, float]],
        weights: Dict[str, float]
    ) -> float:
        """Calculate weighted average of scores"""
        total = 0.0
        total_weight = 0.0
        
        for score_data in scores:
            category = score_data.get("category", "general")
            score = score_data.get("score", 0)
            weight = weights.get(category, 1.0)
            
            total += score * weight
            total_weight += weight
        
        return total / total_weight if total_weight > 0 else 0.0
    
    def identify_strengths_weaknesses(
        self,
        evaluations: List[Dict[str, any]]
    ) -> Dict[str, List[str]]:
        """Identify candidate strengths and weaknesses"""
        strengths = []
        weaknesses = []
        
        for eval_data in evaluations:
            score = eval_data.get("score", 0)
            question_type = eval_data.get("type", "general")
            
            if score >= 8:
                strengths.append(question_type)
            elif score < 5:
                weaknesses.append(question_type)
        
        return {
            "strengths": list(set(strengths)),
            "weaknesses": list(set(weaknesses))
        }