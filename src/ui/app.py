import streamlit as st
import sys
from pathlib import Path
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.orchestrator.crew_manager import CrewManager
from src.utils.logger import logger

# Page config
st.set_page_config(
    page_title="HR Multi-Agent Intelligence Suite",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
    .agent-response {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
if 'interview_questions' not in st.session_state:
    st.session_state.interview_questions = []
if 'interview_answers' not in st.session_state:
    st.session_state.interview_answers = {}

# Initialize crew manager
@st.cache_resource
def get_crew_manager():
    return CrewManager()

crew = get_crew_manager()

# Sidebar
with st.sidebar:
    st.markdown("### 🤖 HR AI Suite")
    st.markdown("---")
    
    # Agent status
    status = crew.get_agent_status()
    if status.get('success'):
        st.success(f"✅ {status['count']} Agents Active")
    else:
        st.error("❌ System Error")
    
    with st.expander("📋 Active Agents"):
        for agent in status.get('agents', []):
            st.write(f"• {agent.replace('_', ' ').title()}")
    
    st.markdown("---")
    
    # Quick tips
    with st.expander("💡 Quick Tips"):
        st.markdown("""
        **Resume Screening:**
        - Paste full resume and JD
        - Minimum 100 words each
        
        **Interview:**
        - Generate questions first
        - Answer each one
        - Click evaluate
        
        **HR Chat:**
        - Ask about policies
        - Keep questions specific
        
        **Performance:**
        - First query may take 1-2 min
        - Subsequent queries are faster
        """)
    
    st.markdown("---")
    st.caption("Powered by Ollama + DeepSeek + Phi-3")

# Main header
st.markdown('<p class="main-header">🎯 HR Multi-Agent Intelligence Suite</p>', unsafe_allow_html=True)
st.markdown("*AI-powered HR automation with 6 specialized agents*")
st.markdown("---")

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📄 Resume Screening",
    "💬 Interview Assistant",
    "🎓 Onboarding",
    "🤖 HR Chatbot",
    "📊 Analytics"
])

# ============================================================================
# TAB 1: RESUME SCREENING
# ============================================================================
with tab1:
    st.header("📄 Resume Screening & Evaluation")
    st.markdown("*Upload resume and job description for AI-powered candidate evaluation*")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Candidate Resume")
        resume_text = st.text_area(
            "Paste resume text (minimum 100 words)",
            height=300,
            placeholder="Paste complete resume here...\n\nInclude: Contact info, Skills, Experience, Education",
            key="resume_input"
        )
        word_count_resume = len(resume_text.split())
        st.caption(f"Words: {word_count_resume}")
    
    with col2:
        st.subheader("📋 Job Description")
        jd_text = st.text_area(
            "Paste job description (minimum 50 words)",
            height=300,
            placeholder="Paste job description here...\n\nInclude: Requirements, Skills, Responsibilities",
            key="jd_input"
        )
        word_count_jd = len(jd_text.split())
        st.caption(f"Words: {word_count_jd}")
    
    job_role = st.text_input("🎯 Job Role/Title", placeholder="e.g., Senior Software Engineer", key="job_role")
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn2:
        analyze_btn = st.button("🔍 Analyze Resume", type="primary", use_container_width=True)
    
    if analyze_btn:
        if not resume_text or word_count_resume < 50:
            st.error("⚠️ Please provide a resume (minimum 50 words)")
        elif not jd_text or word_count_jd < 30:
            st.error("⚠️ Please provide a job description (minimum 30 words)")
        elif not job_role:
            st.error("⚠️ Please enter the job role")
        else:
            with st.spinner("🔄 Running AI evaluation pipeline... (This may take 2-3 minutes)"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("Step 1/3: Screening resume...")
                progress_bar.progress(33)
                
                result = crew.execute_task("resume_pipeline", {
                    "resume": resume_text,
                    "job_description": jd_text,
                    "job_role": job_role
                })
                
                progress_bar.progress(100)
                status_text.empty()
                progress_bar.empty()
                
                if result.get("success"):
                    st.balloons()
                    st.markdown('<div class="success-box"><h3>✅ Analysis Complete!</h3></div>', unsafe_allow_html=True)
                    
                    # Screening Results
                    screening = result.get("screening", {})
                    if screening and screening.get("success"):
                        st.markdown("### 🎯 Screening Results")
                        
                        score = screening.get("score", 0)
                        recommendation = screening.get("recommendation", "N/A")
                        
                        # Score visualization
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric(
                                "📊 Match Score",
                                f"{score}%",
                                delta="High" if score >= 70 else "Low" if score < 50 else "Medium"
                            )
                        
                        with col2:
                            st.metric(
                                "✅ Recommendation",
                                recommendation
                            )
                        
                        with col3:
                            seniority = screening.get("seniority_fit", "N/A")
                            st.metric(
                                "👔 Seniority Fit",
                                seniority.title()
                            )
                        
                        # Skills section
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            skills_matched = screening.get("skills_matched", [])
                            if skills_matched:
                                st.markdown("**✅ Skills Matched:**")
                                for skill in skills_matched:
                                    st.markdown(f"- {skill}")
                            else:
                                st.info("No specific skills extracted")
                        
                        with col2:
                            skills_missing = screening.get("skills_missing", [])
                            if skills_missing:
                                st.markdown("**❌ Skills Missing:**")
                                for skill in skills_missing:
                                    st.markdown(f"- {skill}")
                        
                        # Reasoning
                        if screening.get("reasoning"):
                            with st.expander("📝 Detailed Analysis"):
                                st.write(screening["reasoning"])
                    
                    # Verification Results
                    verification = result.get("verification", {})
                    if verification and verification.get("success"):
                        st.markdown("---")
                        st.markdown("### 🔍 Document Verification")
                        
                        risk_score = verification.get("risk_score", 0)
                        status = verification.get("verification_status", "unknown")
                        
                        # Risk indicator
                        if risk_score < 25:
                            st.success(f"🟢 **Status:** VERIFIED (Risk Score: {risk_score}/100)")
                        elif risk_score < 50:
                            st.warning(f"🟡 **Status:** NEEDS REVIEW (Risk Score: {risk_score}/100)")
                        else:
                            st.error(f"🔴 **Status:** HIGH RISK (Risk Score: {risk_score}/100)")
                        
                        issues = verification.get("issues_found", [])
                        if issues:
                            st.markdown("**⚠️ Issues Detected:**")
                            for issue in issues:
                                with st.expander(f"🔸 {issue.get('type', 'Issue')}"):
                                    st.write(f"**Severity:** {issue.get('severity', 'Unknown')}")
                                    st.write(f"**Description:** {issue.get('description', 'N/A')}")
                                    st.write(f"**Recommendation:** {issue.get('recommendation', 'N/A')}")
                        else:
                            st.success("✅ No issues detected")
                    
                    # Interview Questions
                    if "interview_prep" in result:
                        st.markdown("---")
                        st.markdown("### 📝 Generated Interview Questions")
                        
                        questions = result["interview_prep"].get("questions", [])
                        if questions:
                            for i, q in enumerate(questions, 1):
                                question_text = q.get('question', 'N/A')
                                question_type = q.get('type', 'General')
                                
                                with st.expander(f"**Q{i}:** {question_text[:80]}..."):
                                    st.markdown(f"**Full Question:** {question_text}")
                                    st.markdown(f"**Type:** {question_type.title()}")
                        else:
                            st.info("No questions generated. Score may be below threshold.")
                    
                    # Overall recommendation
                    st.markdown("---")
                                        # Overall recommendation with hiring decision
                    st.markdown("---")
                    st.markdown("### 🎯 Hiring Decision")
                    
                    if "hiring_decision" in result:
                        decision = result["hiring_decision"]
                        
                        # Status banner
                        status = decision.get("status", "Unknown")
                        if "REJECT" in status:
                            st.error(f"## {status}")
                        elif "STRONG CANDIDATE" in status:
                            st.success(f"## {status}")
                        elif "INTERVIEW" in status:
                            st.success(f"## {status}")
                        else:
                            st.warning(f"## {status}")
                        
                        # Recommendation
                        st.markdown(f"**Recommendation:** {decision.get('recommendation', 'N/A')}")
                        st.markdown(f"**Decision Confidence:** {decision.get('confidence', 'N/A')}")
                        
                        # Action items
                        st.markdown("#### 📋 Action Items:")
                        for action in decision.get("action_items", []):
                            st.markdown(f"- {action}")
                        
                        # Score summary
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Resume Score", f"{decision.get('resume_score', 0)}%")
                        with col2:
                            st.metric("Risk Score", f"{decision.get('risk_score', 0)}/100")
                        with col3:
                            proceed = "✅ Yes" if decision.get("proceed_to_interview") else "❌ No"
                            st.metric("Proceed to Interview", proceed)
                    
                    else:
                        # Fallback
                        final_rec = result.get("recommendation", "Review Required")
                        if "Proceed to Interview" in final_rec:
                            st.success(f"✅ **{final_rec}**")
                        else:
                            st.warning(f"⚠️ **{final_rec}**")
# ============================================================================
# TAB 2: INTERVIEW ASSISTANT
# ============================================================================
with tab2:
    st.header("💬 Interview Assistant")
    st.markdown("*Generate AI-powered interview questions and evaluate candidate responses*")
    st.markdown("---")
    
    # Question Generation Section
    st.subheader("📝 Step 1: Generate Interview Questions")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        interview_role = st.text_input(
            "Job Position",
            placeholder="e.g., Senior Data Scientist",
            key="interview_role"
        )
    
    with col2:
        num_questions = st.slider(
            "Number of Questions",
            min_value=3,
            max_value=10,
            value=5,
            key="num_questions"
        )
    
    interview_jd = st.text_area(
        "Job Requirements & Description",
        height=150,
        placeholder="Describe the role, required skills, responsibilities...",
        key="interview_jd"
    )
    
    if st.button("🎯 Generate Interview Questions", use_container_width=True):
        if not interview_role or not interview_jd:
            st.error("⚠️ Please provide both job role and description")
        else:
            with st.spinner("🤖 Generating personalized interview questions..."):
                from src.orchestrator.agent_registry import AgentRegistry
                registry = AgentRegistry()
                interview_agent = registry.get_agent("interview")
                
                result = interview_agent.generate_questions({
                    "job_role": interview_role,
                    "job_description": interview_jd,
                    "num_questions": num_questions
                })
                
                if result.get("success"):
                    st.session_state.interview_questions = result.get("questions", [])
                    st.session_state.interview_answers = {}  # Reset answers
                    st.success(f"✅ Generated {len(st.session_state.interview_questions)} questions!")
                else:
                    st.error(f"Failed to generate questions: {result.get('error', 'Unknown error')}")
    
    # Display and evaluate questions
    if st.session_state.interview_questions:
        st.markdown("---")
        st.subheader("📋 Step 2: Answer & Evaluate")
        
        total_questions = len(st.session_state.interview_questions)
        answered_count = len(st.session_state.interview_answers)
        
        # Progress indicator
        progress = answered_count / total_questions if total_questions > 0 else 0
        st.progress(progress)
        st.caption(f"Progress: {answered_count}/{total_questions} questions evaluated")
        
        for i, q in enumerate(st.session_state.interview_questions, 1):
            question_text = q.get("question", "N/A")
            question_type = q.get("type", "General")
            
            with st.container():
                st.markdown(f"### Question {i} of {total_questions}")
                st.markdown(f'<div class="agent-response"><strong>Q{i}:</strong> {question_text}</div>', unsafe_allow_html=True)
                st.caption(f"Type: {question_type.title()}")
                
                # Show if already evaluated
                if i in st.session_state.interview_answers:
                    saved = st.session_state.interview_answers[i]
                    score = saved['score']
                    
                    # Color-coded score display
                    if score >= 8:
                        st.success(f"✅ **Evaluated | Score: {score}/10**")
                    elif score >= 6:
                        st.info(f"ℹ️ **Evaluated | Score: {score}/10**")
                    else:
                        st.warning(f"⚠️ **Evaluated | Score: {score}/10**")
                    
                    with st.expander("📝 View Answer & Feedback"):
                        st.markdown("**Answer:**")
                        st.write(saved['answer'])
                        st.markdown("**Feedback:**")
                        st.write(saved['feedback'])
                else:
                    # Answer input
                    answer_key = f"answer_{i}"
                    answer = st.text_area(
                        f"Candidate's Answer",
                        height=150,
                        placeholder="Type or paste the candidate's answer here...",
                        key=answer_key
                    )
                    
                    # Evaluate button
                    eval_button_key = f"eval_{i}"
                    if st.button(f"📊 Evaluate Answer {i}", key=eval_button_key):
                        if not answer:
                            st.warning("⚠️ Please provide an answer first")
                        else:
                            with st.spinner(f"🤖 Evaluating answer {i}..."):
                                from src.orchestrator.agent_registry import AgentRegistry
                                registry = AgentRegistry()
                                interview_agent = registry.get_agent("interview")
                                
                                eval_result = interview_agent.process({
                                    "question": question_text,
                                    "answer": answer
                                })
                                
                                if eval_result.get("success"):
                                    evaluation = eval_result.get("evaluation", {})
                                    score = evaluation.get("score", 0)
                                    feedback = evaluation.get("feedback", "No feedback available")
                                    
                                    # Store in session
                                    st.session_state.interview_answers[i] = {
                                        "question": question_text,
                                        "answer": answer,
                                        "score": score,
                                        "feedback": feedback
                                    }
                                    
                                    st.rerun()  # Refresh to show updated UI
                                else:
                                    st.error(f"Evaluation failed: {eval_result.get('error', 'Unknown error')}")
                
                st.markdown("---")
        
        # Final Summary - ONLY SHOW WHEN ALL QUESTIONS ARE ANSWERED
        if len(st.session_state.interview_answers) == total_questions:
            st.markdown("### 🎯 Final Interview Assessment")
            
            # Calculate statistics
            scores = [a['score'] for a in st.session_state.interview_answers.values()]
            avg_score = sum(scores) / len(scores)
            max_score = max(scores)
            min_score = min(scores)
            
            # Determine recommendation
            if avg_score >= 8.5:
                recommendation = "🌟 Strong Hire"
                recommendation_color = "success"
                decision = "Highly recommend hiring. Candidate demonstrated excellent knowledge across all areas."
            elif avg_score >= 7.0:
                recommendation = "✅ Hire"
                recommendation_color = "success"
                decision = "Recommend hiring. Candidate shows strong competency with minor areas for growth."
            elif avg_score >= 5.5:
                recommendation = "🤔 Maybe"
                recommendation_color = "warning"
                decision = "Borderline candidate. Consider team fit and other factors. May need additional interviews."
            else:
                recommendation = "❌ No Hire"
                recommendation_color = "error"
                decision = "Not recommended for hiring. Significant skill gaps identified."
            
            # Display final metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Questions Answered", f"{total_questions}/{total_questions}")
            
            with col2:
                st.metric("Average Score", f"{avg_score:.1f}/10")
            
            with col3:
                st.metric("Best Answer", f"{max_score}/10")
            
            with col4:
                st.metric("Weakest Answer", f"{min_score}/10")
            
            # Recommendation box
            st.markdown("---")
            if recommendation_color == "success":
                st.success(f"## {recommendation}")
            elif recommendation_color == "warning":
                st.warning(f"## {recommendation}")
            else:
                st.error(f"## {recommendation}")
            
            st.markdown(f"**Decision:** {decision}")
            
            # Score breakdown
            with st.expander("📊 Detailed Score Breakdown"):
                for i, (q_num, answer_data) in enumerate(st.session_state.interview_answers.items(), 1):
                    st.markdown(f"**Q{q_num}:** {answer_data['score']}/10")
                    st.caption(answer_data['question'][:100] + "...")
            
            # Export option
            st.markdown("---")
            if st.button("📄 Export Interview Report", use_container_width=True):
                report = f"""
INTERVIEW ASSESSMENT REPORT
===========================

Position: {interview_role}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}

OVERALL ASSESSMENT
------------------
Recommendation: {recommendation}
Average Score: {avg_score:.2f}/10
Questions Answered: {total_questions}

DETAILED SCORES
---------------
"""
                for q_num, answer_data in st.session_state.interview_answers.items():
                    report += f"\nQuestion {q_num}: {answer_data['score']}/10\n"
                    report += f"Q: {answer_data['question']}\n"
                    report += f"A: {answer_data['answer'][:200]}...\n"
                    report += f"Feedback: {answer_data['feedback'][:200]}...\n"
                
                st.download_button(
                    label="Download Report",
                    data=report,
                    file_name=f"interview_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain"
                )
        
        elif len(st.session_state.interview_answers) > 0:
            st.info(f"💡 Answer and evaluate all {total_questions} questions to see the final assessment. ({answered_count}/{total_questions} completed)")
# ============================================================================
# TAB 3: ONBOARDING
# ============================================================================
with tab3:
    st.header("🎓 Employee Onboarding")
    st.markdown("*Create personalized onboarding plans for new hires*")
    st.markdown("---")
    
    st.subheader("📋 New Employee Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        emp_name = st.text_input("Employee Name", placeholder="e.g., John Doe")
        emp_role = st.text_input("Role/Position", placeholder="e.g., Software Engineer")
    
    with col2:
        start_date = st.date_input("Start Date")
        department = st.selectbox(
            "Department",
            ["Engineering", "Product", "Sales", "Marketing", "HR", "Finance", "Other"]
        )
    
    if st.button("🚀 Create Onboarding Plan", type="primary", use_container_width=True):
        if not emp_name or not emp_role:
            st.error("⚠️ Please provide employee name and role")
        else:
            with st.spinner("🤖 Creating personalized onboarding plan..."):
                result = crew.execute_task("onboarding", {
                    "employee_name": emp_name,
                    "role": emp_role,
                    "start_date": str(start_date)
                })
                
                if result.get("success"):
                    st.success("✅ Onboarding plan created!")
                    
                    # Welcome Message
                    # Welcome Message
                    st.markdown("### 👋 Welcome Message")
                    welcome_msg = result.get("welcome_message", "")
                    
                    # Check if it's a string (should always be now)
                    if isinstance(welcome_msg, str):
                        # Clean display
                        st.markdown(f'<div class="agent-response">{welcome_msg}</div>', unsafe_allow_html=True)
                    
                    # Check if welcome_message is a dict or string
                    if isinstance(welcome_msg, dict):
                        st.markdown(f'<div class="agent-response">', unsafe_allow_html=True)
                        st.markdown(f"**Welcome:** {welcome_msg.get('welcome', 'Welcome to the team!')}")
                        
                        if 'key_priorities' in welcome_msg:
                            st.markdown("**🎯 Key Priorities:**")
                            for priority in welcome_msg['key_priorities']:
                                st.markdown(f"- {priority}")
                        
                        if 'important_contacts' in welcome_msg:
                            st.markdown("**📞 Important Contacts:**")
                            for contact, info in welcome_msg['important_contacts'].items():
                                st.markdown(f"- **{contact}:** {info}")
                        
                        if 'tips_for_success' in welcome_msg:
                            st.markdown("**💡 Tips for Success:**")
                            for tip in welcome_msg['tips_for_success']:
                                st.markdown(f"- {tip}")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        # Fallback for dict (shouldn't happen with new code)
                        st.info("Welcome to the team! Your onboarding plan is ready.")
                    
                    # Checklist
                    st.markdown("---")
                    st.markdown("### 📋 Onboarding Checklist")
                    
                    checklist = result.get("checklist", [])
                    
                    for phase in checklist:
                        phase_name = phase.get("phase", "Phase")
                        tasks = phase.get("tasks", [])
                        
                        with st.expander(f"**{phase_name}** ({len(tasks)} tasks)", expanded=True):
                            for task in tasks:
                                task_name = task.get("task", "Task")
                                task_status = task.get("status", "pending")
                                
                                if task_status == "completed":
                                    st.markdown(f"✅ {task_name}")
                                else:
                                    st.markdown(f"⏳ {task_name}")
                    
                    # Progress
                    st.markdown("---")
                    completion = result.get("completion_percentage", 0)
                    st.progress(completion / 100)
                    st.caption(f"Overall Progress: {completion}%")
                    
                    # Next Steps
                    if result.get("next_steps"):
                        st.markdown("### ⏭️ Next Steps")
                        for step in result["next_steps"]:
                            st.markdown(f"- {step}")
                
                else:
                    st.error(f"❌ Error: {result.get('error', 'Unknown error')}")

# ============================================================================
# TAB 4: HR CHATBOT
# ============================================================================
with tab4:
    st.header("🤖 HR Policy Assistant")
    st.markdown("*Ask questions about HR policies, leave, benefits, and more*")
    st.markdown("---")
    
    # Sample questions
    st.markdown("### 💡 Sample Questions")
    sample_questions = [
        "What is the sick leave policy?",
        "How many vacation days do I get?",
        "What are the maternity leave benefits?",
        "How do I apply for leave?",
        "What is the remote work policy?"
    ]
    
    cols = st.columns(len(sample_questions))
    for i, q in enumerate(sample_questions):
        with cols[i]:
            if st.button(q, key=f"sample_{i}", use_container_width=True):
                st.session_state.chat_messages.append({"role": "user", "content": q})
    
    st.markdown("---")
    
    # Chat history
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask your HR question... (e.g., 'What is the leave policy?')"):
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("🤖 Searching policies..."):
                result = crew.execute_task("query", {
                    "query": prompt,
                    "session_id": "chatbot"
                })
                
                if result.get("success"):
                    response = result.get("answer", "I couldn't find relevant information.")
                    
                    # Check for timeout errors
                    if "timeout" in response.lower() or "error:" in response.lower():
                        response = """I apologize, but I'm taking longer than expected to respond. 

**Quick Answer:** Please check the HR policy documents in the data/hr_policies folder for:
- Leave Policy
- Benefits Policy
- Company Handbook

**Or try asking:**
- More specific questions
- One policy at a time

Would you like to try rephrasing your question?"""
                    
                    st.markdown(response)
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})
                    
                    # Show referenced policies
                    if result.get("policies_referenced"):
                        st.caption(f"📚 Referenced: {', '.join(result['policies_referenced'])}")
                else:
                    error_msg = result.get('error', 'Unknown error')
                    if 'timeout' in error_msg.lower():
                        st.warning("⏱️ Response took too long. Please try a simpler question.")
                    else:
                        st.error(f"Error: {error_msg}")

# ============================================================================
# TAB 5: ANALYTICS
# ============================================================================
with tab5:
    st.header("📊 HR Analytics Dashboard")
    st.markdown("*Generate insights from candidate data*")
    st.markdown("---")
    
    st.info("💡 Analytics will aggregate data from all agent interactions")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        report_type = st.selectbox(
            "Report Type",
            ["Summary Report", "Pipeline Analysis", "Skills Gap Analysis"]
        )
    
    with col2:
        st.write("")  # Spacing
        generate_btn = st.button("📊 Generate Report", type="primary", use_container_width=True)
    
    if generate_btn:
        with st.spinner("🤖 Generating analytics report..."):
            from src.orchestrator.agent_registry import AgentRegistry
            registry = AgentRegistry()
            analytics_agent = registry.get_agent("analytics")
            
            # Sample data for demonstration
            sample_data = [
                {
                    "resume_score": 85,
                    "interview_score": 8.5,
                    "skills_matched": ["Python", "AWS", "Docker"],
                    "skills_missing": ["Kubernetes"]
                },
                {
                    "resume_score": 72,
                    "interview_score": 7.2,
                    "skills_matched": ["Java", "Spring", "MySQL"],
                    "skills_missing": ["AWS", "Docker"]
                },
                {
                    "resume_score": 65,
                    "interview_score": 6.5,
                    "skills_matched": ["Python", "Django"],
                    "skills_missing": ["AWS", "Docker", "React"]
                },
            ]
            
            # Determine report type
            if report_type == "Summary Report":
                result = analytics_agent.process({"report_type": "summary", "data": sample_data})
            elif report_type == "Pipeline Analysis":
                result = analytics_agent.process({"report_type": "pipeline", "data": sample_data})
            else:
                result = analytics_agent.process({"report_type": "skills", "data": sample_data})
            
            if result.get("success"):
                # Summary metrics
                if "summary" in result:
                    summary = result["summary"]
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "📊 Total Candidates",
                            summary.get("total_candidates", 0)
                        )
                    
                    with col2:
                        st.metric(
                            "📝 Avg Resume Score",
                            f"{summary.get('avg_resume_score', 0):.1f}%"
                        )
                    
                    with col3:
                        st.metric(
                            "💬 Avg Interview Score",
                            f"{summary.get('avg_interview_score', 0):.1f}/10"
                        )
                
                # AI Insights
                if result.get("ai_insights"):
                    st.markdown("### 🔍 AI-Generated Insights")
                    st.markdown(f'<div class="agent-response">{result["ai_insights"]}</div>', unsafe_allow_html=True)
                
                # Pipeline metrics
                if "pipeline_status" in result:
                    st.markdown("---")
                    st.markdown("### 📈 Hiring Pipeline")
                    
                    pipeline = result["pipeline_status"]
                    
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    with col1:
                        st.metric("Applied", pipeline.get("applied", 0))
                    with col2:
                        st.metric("Screened", pipeline.get("screening_passed", 0))
                    with col3:
                        st.metric("Interviewed", pipeline.get("interviewed", 0))
                    with col4:
                        st.metric("Offers", pipeline.get("offer", 0))
                    with col5:
                        st.metric("Hired", pipeline.get("hired", 0))
                    
                    # Conversion rates
                    if "conversion_rates" in result:
                        st.markdown("**Conversion Rates:**")
                        rates = result["conversion_rates"]
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.info(f"Screening: {rates.get('screening', 'N/A')}")
                        with col2:
                            st.info(f"Interview: {rates.get('interview', 'N/A')}")
                        with col3:
                            st.info(f"Offer: {rates.get('offer', 'N/A')}")
                
                # Skills analysis
                if "most_common_skills" in result:
                    st.markdown("---")
                    st.markdown("### 🎯 Skills Analysis")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Most Common Skills:**")
                        for skill, count in result["most_common_skills"].items():
                            st.markdown(f"- {skill}: {count} candidates")
                    
                    with col2:
                        if "skill_gaps" in result:
                            st.markdown("**Common Skill Gaps:**")
                            for skill, count in result["skill_gaps"].items():
                                st.markdown(f"- {skill}: Missing in {count} candidates")
            
            else:
                st.error(f"Failed to generate report: {result.get('error', 'Unknown error')}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p style='color: #666;'>
            🤖 HR Multi-Agent Intelligence Suite v1.0 | 
            Powered by <strong>Ollama</strong> + <strong>DeepSeek-R1</strong> + <strong>Phi-3</strong>
        </p>
        <p style='color: #999; font-size: 0.8em;'>
            💡 Tip: First query may take 1-2 minutes as models load. Subsequent queries are faster.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)