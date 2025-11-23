"""
LangGraph Workflow for JobHunter AI
Orchestrates agents in a complete job application pipeline
"""
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
import operator
import logging

logger = logging.getLogger(__name__)


class JobApplicationState(TypedDict):
    """State for the job application workflow"""
    # Input
    resume_path: str
    job_posting: dict
    
    # Intermediate results
    resume_data: dict
    company_data: dict
    match_result: dict
    ats_score: dict
    optimized_resume: dict
    email: dict
    
    # Control flow
    should_apply: bool
    errors: Annotated[Sequence[str], operator.add]
    status: str


class JobApplicationWorkflow:
    """LangGraph workflow for automated job applications"""
    
    def __init__(self):
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        workflow = StateGraph(JobApplicationState)
        
        # Add nodes (each node is an agent)
        workflow.add_node("parse_resume", self.parse_resume_node)
        workflow.add_node("research_company", self.research_company_node)
        workflow.add_node("match_job", self.match_job_node)
        workflow.add_node("score_ats", self.score_ats_node)
        workflow.add_node("optimize_resume", self.optimize_resume_node)
        workflow.add_node("write_email", self.write_email_node)
        
        # Define edges (workflow flow)
        workflow.set_entry_point("parse_resume")
        
        workflow.add_edge("parse_resume", "research_company")
        workflow.add_edge("research_company", "match_job")
        
        # Conditional: only continue if match is good
        workflow.add_conditional_edges(
            "match_job",
            self.should_continue_after_match,
            {
                "continue": "score_ats",
                "skip": END
            }
        )
        
        workflow.add_edge("score_ats", "optimize_resume")
        workflow.add_edge("optimize_resume", "write_email")
        workflow.add_edge("write_email", END)
        
        return workflow.compile()
    
    async def parse_resume_node(self, state: JobApplicationState) -> JobApplicationState:
        """Node: Parse resume"""
        from agents.resume_parser import ResumeParser
        
        try:
            parser = ResumeParser()
            result = await parser.run({"resume_path": state["resume_path"]})
            state["resume_data"] = result
            state["status"] = "Resume parsed"
            logger.info("✓ Resume parsed")
        except Exception as e:
            state["errors"].append(f"Resume parsing failed: {e}")
            logger.error(f"✗ Resume parsing failed: {e}")
        
        return state
    
    async def research_company_node(self, state: JobApplicationState) -> JobApplicationState:
        """Node: Research company"""
        from agents.company_researcher import CompanyResearcher
        
        try:
            researcher = CompanyResearcher()
            result = await researcher.run({
                "company_name": state["job_posting"]["company"],
                "job_descriptions": [state["job_posting"]["description"]]
            })
            state["company_data"] = result
            state["status"] = "Company researched"
            logger.info(f"✓ Researched {state['job_posting']['company']}")
        except Exception as e:
            state["errors"].append(f"Company research failed: {e}")
            state["company_data"] = {}
            logger.error(f"✗ Company research failed: {e}")
        
        return state
    
    async def match_job_node(self, state: JobApplicationState) -> JobApplicationState:
        """Node: Match job to candidate"""
        from agents.job_matcher import JobMatcher
        
        try:
            matcher = JobMatcher()
            result = await matcher.run({
                "resume_data": state["resume_data"],
                "job_posting": state["job_posting"],
                "company_data": state["company_data"]
            })
            state["match_result"] = result
            state["should_apply"] = result["recommendation"] in ["Apply", "Maybe"]
            state["status"] = f"Match score: {result['match_score']}/100"
            logger.info(f"✓ Match score: {result['match_score']}/100 - {result['recommendation']}")
        except Exception as e:
            state["errors"].append(f"Job matching failed: {e}")
            state["should_apply"] = False
            logger.error(f"✗ Job matching failed: {e}")
        
        return state
    
    def should_continue_after_match(self, state: JobApplicationState) -> str:
        """Conditional: Continue only if match is good"""
        if state.get("should_apply", False):
            return "continue"
        else:
            logger.info("⊘ Skipping application - poor match")
            return "skip"
    
    async def score_ats_node(self, state: JobApplicationState) -> JobApplicationState:
        """Node: Score ATS compatibility"""
        from agents.ats_scorer import ATSScorer
        
        try:
            scorer = ATSScorer()
            result = await scorer.run({
                "resume_data": state["resume_data"],
                "job_description": state["job_posting"]["description"],
                "company_tech_stack": state["company_data"].get("tech_stack", {}).get("languages", [])
            })
            state["ats_score"] = result
            state["status"] = f"ATS score: {result['score']}/100"
            logger.info(f"✓ ATS score: {result['score']}/100")
        except Exception as e:
            state["errors"].append(f"ATS scoring failed: {e}")
            logger.error(f"✗ ATS scoring failed: {e}")
        
        return state
    
    async def optimize_resume_node(self, state: JobApplicationState) -> JobApplicationState:
        """Node: Optimize resume"""
        from agents.resume_optimizer import ResumeOptimizer
        
        try:
            optimizer = ResumeOptimizer()
            result = await optimizer.run({
                "base_resume": state["resume_data"],
                "job_description": state["job_posting"]["description"],
                "ats_score_data": state["ats_score"],
                "company_data": state["company_data"]
            })
            state["optimized_resume"] = result
            state["status"] = f"Resume optimized (+{result['expected_score_improvement']} points)"
            logger.info(f"✓ Resume optimized (+{result['expected_score_improvement']} points)")
        except Exception as e:
            state["errors"].append(f"Resume optimization failed: {e}")
            logger.error(f"✗ Resume optimization failed: {e}")
        
        return state
    
    async def write_email_node(self, state: JobApplicationState) -> JobApplicationState:
        """Node: Write cold email"""
        from agents.email_writer import EmailWriter
        
        try:
            writer = EmailWriter()
            result = await writer.run({
                "job_posting": state["job_posting"],
                "resume_data": state["optimized_resume"].get("optimized_resume", state["resume_data"]),
                "company_data": state["company_data"]
            })
            state["email"] = result
            state["status"] = "Email generated"
            logger.info("✓ Email generated")
        except Exception as e:
            state["errors"].append(f"Email generation failed: {e}")
            logger.error(f"✗ Email generation failed: {e}")
        
        return state
    
    async def run(self, resume_path: str, job_posting: dict) -> JobApplicationState:
        """Run the complete workflow
        
        Args:
            resume_path: Path to resume file
            job_posting: Job posting dict with company, title, description
            
        Returns:
            Final state with all results
        """
        initial_state = JobApplicationState(
            resume_path=resume_path,
            job_posting=job_posting,
            resume_data={},
            company_data={},
            match_result={},
            ats_score={},
            optimized_resume={},
            email={},
            should_apply=False,
            errors=[],
            status="Starting"
        )
        
        logger.info("=" * 60)
        logger.info("Starting JobHunter AI Workflow")
        logger.info("=" * 60)
        
        final_state = await self.graph.ainvoke(initial_state)
        
        logger.info("=" * 60)
        logger.info("Workflow Complete")
        logger.info(f"Status: {final_state['status']}")
        logger.info(f"Errors: {len(final_state['errors'])}")
        logger.info("=" * 60)
        
        return final_state
