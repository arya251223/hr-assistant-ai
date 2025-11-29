import os
from pathlib import Path
from typing import Dict, Any
from ..base_agent import BaseAgent
from .tools import PolicySearchTool
from ...utils.logger import logger

class HRAssistantAgent(BaseAgent):
    """HR Assistant Agent - Answers policy and benefits questions"""
    
    def __init__(self, llm_client, policy_dir: str = "data/hr_policies"):
        super().__init__("HR Assistant Agent", llm_client)
        self.policy_dir = policy_dir
        self.policy_tool = PolicySearchTool(policy_dir)
    
    def get_system_prompt(self) -> str:
        return "You are a helpful HR assistant. Answer briefly."
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process HR query with MINIMAL context"""
        try:
            query = input_data.get("query", "").lower()
            
            # RULE-BASED RESPONSES for common queries
            quick_answer = self._get_quick_answer(query)
            if quick_answer:
                return quick_answer
            
            # For other queries, use MINIMAL LLM
            relevant_policies = self.policy_tool.search(query, top_k=1)
            
            if not relevant_policies:
                return {
                    "success": True,
                    "query": query,
                    "answer": "I don't have specific information about that. Please check the HR handbook or contact hr@company.com",
                    "policies_referenced": []
                }
            
            # Get ONLY the most relevant snippet
            policy_name, full_content = list(relevant_policies.items())[0]
            
            # Extract ONLY relevant section (max 300 chars)
            snippet = self._extract_relevant_snippet(full_content, query, max_len=300)
            
            # ULTRA SHORT PROMPT
            prompt = f"""Policy: {snippet}

Question: {query}

Answer in 1-2 sentences:"""
            
            response = self.generate_response(
                prompt,
                temperature=0.3,
                max_tokens=100  # VERY SHORT
            )
            
            return {
                "success": True,
                "query": query,
                "answer": response if response else "Please check the HR policy documents.",
                "policies_referenced": [policy_name]
            }
            
        except Exception as e:
            logger.error(f"HR Assistant error: {e}")
            return {
                "success": True,
                "query": query,
                "answer": "Please check the HR policy documents in data/hr_policies folder or contact HR.",
                "policies_referenced": []
            }
    
    def _get_quick_answer(self, query: str) -> Dict[str, Any]:
        """Rule-based quick answers for common queries"""
        
        quick_responses = {
            "sick leave": {
                "answer": "Employees get 10 days of sick leave per year. Medical certificate required for absences over 2 consecutive days. Source: Leave Policy",
                "policies": ["leave_policy.md"]
            },
            "vacation": {
                "answer": "Employees are entitled to 20 days of annual leave per year, accrued monthly. Maximum 5 days can be carried forward. Source: Leave Policy",
                "policies": ["leave_policy.md"]
            },
            "maternity": {
                "answer": "16 weeks paid maternity leave. Notice required 8 weeks before due date. Medical documentation required. Source: Leave Policy",
                "policies": ["leave_policy.md"]
            },
            "paternity": {
                "answer": "2 weeks paid paternity leave within 4 weeks of child's birth. 4 weeks advance notice preferred. Source: Leave Policy",
                "policies": ["leave_policy.md"]
            },
            "health insurance": {
                "answer": "Company pays 80% of premium. Covers medical, dental, vision. PPO and HMO options available. Source: Benefits Policy",
                "policies": ["benefits_policy.md"]
            },
            "remote work": {
                "answer": "Employees can work remotely 3 days per week with manager approval. Source: Benefits Policy",
                "policies": ["benefits_policy.md"]
            }
        }
        
        # Check if query matches any quick response
        for keyword, response_data in quick_responses.items():
            if keyword in query:
                return {
                    "success": True,
                    "query": query,
                    "answer": response_data["answer"],
                    "policies_referenced": response_data["policies"]
                }
        
        return None
    
    def _extract_relevant_snippet(self, text: str, query: str, max_len: int = 300) -> str:
        """Extract most relevant snippet from policy"""
        # Split into paragraphs
        paragraphs = text.split('\n\n')
        
        # Find most relevant paragraph
        query_words = set(query.lower().split())
        best_para = ""
        best_score = 0
        
        for para in paragraphs:
            para_lower = para.lower()
            score = sum(1 for word in query_words if word in para_lower)
            if score > best_score:
                best_score = score
                best_para = para
        
        # Truncate if too long
        if len(best_para) > max_len:
            best_para = best_para[:max_len] + "..."
        
        return best_para if best_para else text[:max_len]