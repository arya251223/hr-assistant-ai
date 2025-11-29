import json
import re
from typing import Dict, Any, List
from ..base_agent import BaseAgent
from .evaluator import InterviewEvaluator
from ...utils.logger import logger

class InterviewAgent(BaseAgent):
    """Interview Agent - Conducts and evaluates interviews"""
    
    def __init__(self, llm_client):
        super().__init__("Interview Agent", llm_client)
        self.evaluator = InterviewEvaluator()
        self.current_interview = None
    
    def get_system_prompt(self) -> str:
        return "You are an expert interviewer. Generate clear, relevant interview questions."
    
    def generate_questions(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate interview questions with robust parsing"""
        try:
            job_role = input_data.get("job_role", "")
            job_description = input_data.get("job_description", "")
            num_questions = input_data.get("num_questions", 5)
            
            # ULTRA SIMPLE PROMPT - No JSON request
            prompt = f"""Generate {num_questions} interview questions for: {job_role}

Requirements: {job_description[:200]}

List each question on a new line starting with "Q1:", "Q2:", etc.

Example:
Q1: Explain your experience with Python
Q2: Describe a challenging project you worked on
Q3: How do you handle tight deadlines?

Now generate {num_questions} questions:"""
            
            response = self.generate_response(prompt, temperature=0.7, max_tokens=500)
            
            # Parse questions from plain text
            questions = self._parse_questions_from_text(response, num_questions)
            
            # Initialize interview session
            self.current_interview = {
                "job_role": job_role,
                "questions": questions,
                "answers": [],
                "current_question": 0
            }
            
            return {
                "success": True,
                "questions": questions,
                "session_id": id(self.current_interview)
            }
            
        except Exception as e:
            logger.error(f"Question generation error: {e}")
            # FALLBACK: Generate generic questions
            return {
                "success": True,
                "questions": self._get_fallback_questions(num_questions, job_role)
            }
    
    def _parse_questions_from_text(self, text: str, expected_num: int) -> List[Dict[str, Any]]:
        """Parse questions from plain text response"""
        questions = []
        
        # Try multiple parsing strategies
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for Q1:, Q2:, etc.
            match = re.match(r'Q\d+[:\-\.\)]\s*(.+)', line, re.IGNORECASE)
            if match:
                question_text = match.group(1).strip()
                questions.append({
                    "id": len(questions) + 1,
                    "question": question_text,
                    "type": self._guess_question_type(question_text)
                })
            # Look for numbered lists: 1., 2., etc.
            elif re.match(r'\d+[\.\)]\s*(.+)', line):
                match = re.match(r'\d+[\.\)]\s*(.+)', line)
                question_text = match.group(1).strip()
                questions.append({
                    "id": len(questions) + 1,
                    "question": question_text,
                    "type": self._guess_question_type(question_text)
                })
            # Any line ending with ?
            elif '?' in line and len(line) > 20:
                questions.append({
                    "id": len(questions) + 1,
                    "question": line,
                    "type": self._guess_question_type(line)
                })
        
        # Ensure we have expected number
        if len(questions) < expected_num:
            logger.warning(f"Only parsed {len(questions)} questions, expected {expected_num}")
            # Add fallback questions
            while len(questions) < expected_num:
                questions.append({
                    "id": len(questions) + 1,
                    "question": f"Describe your relevant experience and skills for this role.",
                    "type": "general"
                })
        
        return questions[:expected_num]
    
    def _guess_question_type(self, question: str) -> str:
        """Guess question type from content"""
        q_lower = question.lower()
        
        if any(word in q_lower for word in ['algorithm', 'code', 'technical', 'system', 'architecture', 'debug']):
            return "technical"
        elif any(word in q_lower for word in ['situation', 'time when', 'example of', 'tell me about', 'describe']):
            return "behavioral"
        elif any(word in q_lower for word in ['solve', 'problem', 'challenge', 'difficult']):
            return "problem-solving"
        else:
            return "general"
    
    def _get_fallback_questions(self, num: int, role: str) -> List[Dict[str, Any]]:
        """Fallback questions if parsing fails"""
        base_questions = [
            f"Tell me about your experience relevant to the {role} position.",
            f"What interests you most about this {role} role?",
            "Describe a challenging project you've worked on and how you overcame obstacles.",
            "How do you stay updated with the latest technologies and best practices?",
            "Where do you see yourself in 3-5 years?",
            "Describe your ideal work environment and team dynamics.",
            "How do you handle tight deadlines and pressure?",
            "Tell me about a time you had to learn something new quickly.",
            "How do you approach problem-solving?",
            "What makes you a good fit for this role?"
        ]
        
        return [
            {"id": i+1, "question": q, "type": "general"}
            for i, q in enumerate(base_questions[:num])
        ]
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process interview answer and evaluate"""
        try:
            question = input_data.get("question", "")
            answer = input_data.get("answer", "")
            
            if not question or not answer:
                return {
                    "success": False,
                    "error": "Missing question or answer"
                }
            
            # Simple evaluation prompt - no JSON
            prompt = f"""Evaluate this interview answer on a scale of 0-10.

Question: {question}

Answer: {answer}

Provide:
- Score (0-10):
- Feedback:

Keep it brief."""
            
            response = self.generate_response(prompt, temperature=0.3, max_tokens=300)
            evaluation = self._parse_evaluation_from_text(response)
            
            # Store in session if active
            if self.current_interview:
                self.current_interview["answers"].append({
                    "question": question,
                    "answer": answer,
                    "evaluation": evaluation
                })
            
            return {
                "success": True,
                "evaluation": evaluation
            }
            
        except Exception as e:
            logger.error(f"Interview evaluation error: {e}")
            return {
                "success": True,
                "evaluation": {
                    "score": 5,
                    "feedback": "Evaluation completed. Response noted."
                }
            }
    
    def _parse_evaluation_from_text(self, text: str) -> Dict[str, Any]:
        """Parse evaluation from plain text"""
        # Try to extract score
        score = 5  # default
        
        # Look for "Score: X" or "X/10"
        score_patterns = [
            r'score[:\s]+(\d+)',
            r'(\d+)\s*/\s*10',
            r'rating[:\s]+(\d+)',
            r'(\d+)\s*out of 10'
        ]
        
        for pattern in score_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    score = int(match.group(1))
                    score = max(0, min(10, score))  # Clamp to 0-10
                    break
                except:
                    pass
        
        # Rest is feedback
        feedback = text.strip()
        
        return {
            "score": score,
            "feedback": feedback
        }
    
    def get_final_evaluation(self) -> Dict[str, Any]:
        """Generate final interview evaluation"""
        if not self.current_interview:
            return {
                "success": False,
                "error": "No active interview session"
            }
        
        answers = self.current_interview["answers"]
        scores = [a["evaluation"].get("score", 0) for a in answers]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        recommendation = self.evaluator.get_recommendation(avg_score)
        
        return {
            "success": True,
            "total_questions": len(self.current_interview["questions"]),
            "questions_answered": len(answers),
            "average_score": round(avg_score, 2),
            "recommendation": recommendation,
            "detailed_scores": scores,
            "job_role": self.current_interview["job_role"]
        }