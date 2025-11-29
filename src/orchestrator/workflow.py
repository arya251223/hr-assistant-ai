"""
Workflow Orchestrator - Manages multi-agent workflows
"""
from typing import Dict, Any, List
from .agent_registry import AgentRegistry
from .router import TaskRouter
from .context_manager import ContextManager
from ..utils.logger import logger


class WorkflowOrchestrator:
    """Orchestrate multi-agent workflows"""
    
    def __init__(self):
        """Initialize orchestrator with all components"""
        try:
            self.registry = AgentRegistry()
            self.router = TaskRouter()
            self.context = ContextManager()
            logger.info("Workflow Orchestrator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize WorkflowOrchestrator: {e}")
            raise
    
    def execute_resume_pipeline(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Complete resume evaluation pipeline with hiring decision
        
        Steps:
        1. Resume Screening
        2. Document Verification
        3. Generate Interview Questions (if qualified)
        4. Make Hiring Decision
        """
        session_id = input_data.get("session_id", "default")
        results = {}
        
        try:
            # Step 1: Resume Screening
            logger.info("Step 1: Resume Screening")
            screening_agent = self.registry.get_agent("resume_screening")
            
            if not screening_agent:
                return {"success": False, "error": "Resume screening agent not available"}
            
            screening_result = screening_agent.process({
                "resume": input_data.get("resume"),
                "job_description": input_data.get("job_description")
            })
            results["screening"] = screening_result
            
            # Step 2: Document Verification
            logger.info("Step 2: Document Verification")
            doc_agent = self.registry.get_agent("doc_verification")
            
            if not doc_agent:
                return {"success": False, "error": "Document verification agent not available"}
            
            verification_result = doc_agent.process({
                "resume": input_data.get("resume")
            })
            results["verification"] = verification_result
            
            # Get scores for decision
            resume_score = screening_result.get("score", 0)
            risk_score = verification_result.get("risk_score", 0)
            
            # HIRING DECISION LOGIC
            hiring_decision = self._make_hiring_decision(resume_score, risk_score)
            results["hiring_decision"] = hiring_decision
            
            # Step 3: Conditional Interview Question Generation
            if hiring_decision["proceed_to_interview"]:
                logger.info("Step 3: Generating Interview Questions")
                interview_agent = self.registry.get_agent("interview")
                
                if interview_agent:
                    interview_result = interview_agent.generate_questions({
                        "job_role": input_data.get("job_role", ""),
                        "job_description": input_data.get("job_description", ""),
                        "num_questions": 5
                    })
                    results["interview_prep"] = interview_result
                    results["recommendation"] = "Proceed to Interview"
                else:
                    logger.warning("Interview agent not available")
            else:
                results["recommendation"] = hiring_decision["recommendation"]
            
            # Store in context
            self.context.add_interaction(
                session_id,
                "workflow",
                "resume_pipeline",
                results
            )
            
            results["success"] = True
            return results
            
        except Exception as e:
            logger.error(f"Pipeline execution error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _make_hiring_decision(self, resume_score: int, risk_score: int) -> Dict[str, Any]:
        """
        Make hiring decision based on scores
        
        Args:
            resume_score: Resume match score (0-100)
            risk_score: Document verification risk score (0-100)
            
        Returns:
            Decision dictionary with status, recommendation, and action items
        """
        proceed_to_interview = False
        decision_status = ""
        recommendation = ""
        action_items = []
        
        # High risk = reject regardless of resume score
        if risk_score >= 50:
            decision_status = "❌ REJECT"
            recommendation = "Candidate rejected due to high risk score"
            action_items = [
                "Do not proceed with this candidate",
                "Document verification failed",
                "Consider other applicants"
            ]
        
        # Low resume score = reject
        elif resume_score < 50:
            decision_status = "❌ REJECT"
            recommendation = "Candidate does not meet minimum requirements"
            action_items = [
                "Skills gap too large",
                "Send rejection email",
                "Keep resume on file for future roles"
            ]
        
        # Medium score = maybe/phone screen
        elif 50 <= resume_score < 70:
            decision_status = "🤔 PHONE SCREEN"
            recommendation = "Schedule phone screening"
            action_items = [
                "Conduct 15-min phone screen",
                "Assess cultural fit",
                "Verify salary expectations",
                "Decide on full interview after call"
            ]
            proceed_to_interview = False
        
        # Good score, low risk = Interview
        elif 70 <= resume_score < 85:
            decision_status = "✅ SCHEDULE INTERVIEW"
            recommendation = "Proceed to technical interview"
            action_items = [
                "Schedule 1-hour interview",
                "Prepare technical questions",
                "Include team member in interview",
                "Assess both technical and cultural fit"
            ]
            proceed_to_interview = True
        
        # Excellent score, low risk = Fast track
        else:  # >= 85
            decision_status = "🌟 STRONG CANDIDATE"
            recommendation = "Fast-track to final round"
            action_items = [
                "Priority scheduling",
                "Schedule with hiring manager",
                "Prepare competitive offer",
                "Check references proactively"
            ]
            proceed_to_interview = True
        
        return {
            "status": decision_status,
            "recommendation": recommendation,
            "proceed_to_interview": proceed_to_interview,
            "action_items": action_items,
            "resume_score": resume_score,
            "risk_score": risk_score,
            "confidence": self._calculate_confidence(resume_score, risk_score)
        }
    
    def _calculate_confidence(self, resume_score: int, risk_score: int) -> str:
        """Calculate confidence in hiring decision"""
        if risk_score > 30:
            return "Medium (due to risk flags)"
        elif resume_score >= 80 or resume_score <= 40:
            return "High (clear decision)"
        else:
            return "Medium (borderline case)"
    
    def execute_onboarding_workflow(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute onboarding workflow
        
        Args:
            input_data: Employee information
            
        Returns:
            Onboarding plan
        """
        try:
            onboarding_agent = self.registry.get_agent("onboarding")
            
            if not onboarding_agent:
                return {"success": False, "error": "Onboarding agent not available"}
            
            result = onboarding_agent.process({
                "action": "create_plan",
                "employee_name": input_data.get("employee_name"),
                "role": input_data.get("role"),
                "start_date": input_data.get("start_date")
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Onboarding workflow error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def handle_query(self, query: str, session_id: str = "default") -> Dict[str, Any]:
        """
        Handle general query by routing to appropriate agent
        
        Args:
            query: User's question
            session_id: Session identifier
            
        Returns:
            Agent response
        """
        try:
            # Validate input
            if not query:
                return {
                    "success": False,
                    "error": "Empty query provided"
                }
            
            # Route to agent
            logger.info(f"Handling query: {query[:50]}...")
            agent_name = self.router.route(query)
            
            if not agent_name:
                return {
                    "success": False,
                    "error": "Could not determine appropriate agent"
                }
            
            agent = self.registry.get_agent(agent_name)
            
            if not agent:
                return {
                    "success": False,
                    "error": f"Agent {agent_name} not available"
                }
            
            # Process query
            logger.info(f"Processing query with agent: {agent_name}")
            result = agent.process({"query": query})
            
            # Store in context
            self.context.add_interaction(
                session_id,
                agent_name,
                query,
                result
            )
            
            result["agent_used"] = agent_name
            return result
            
        except AttributeError as e:
            logger.error(f"Attribute error in query handling: {e}")
            return {
                "success": False,
                "error": f"Internal error: {str(e)}. Please check agent configuration."
            }
        except Exception as e:
            logger.error(f"Query handling error: {e}")
            return {
                "success": False,
                "error": str(e)
            }