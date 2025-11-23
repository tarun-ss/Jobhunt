"""
Resume Optimizer Agent
Tailors resumes for specific job descriptions while keeping core intact
"""
import logging
from typing import Dict, List, Any
import json

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ResumeOptimizer(BaseAgent):
    """Agent that optimizes resumes for specific jobs"""
    
    def __init__(self):
        super().__init__(
            name="ResumeOptimizer",
            system_prompt="""You are an expert resume optimizer. Your job is to tailor resumes for specific job descriptions while maintaining authenticity.

Rules:
1. NEVER fabricate experience or skills
2. Reorder and emphasize relevant experience
3. Add missing keywords naturally where they fit
4. Adjust language to match job description tone
5. Keep the core resume structure intact
6. Highlight transferable skills

Your goal is to maximize ATS score while keeping the resume truthful."""
        )
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize a resume for a specific job
        
        Args:
            input_data: {
                "base_resume": parsed resume dict,
                "job_description": job description text,
                "ats_score_data": ATS score breakdown,
                "company_data": optional company info from MCP
            }
            
        Returns:
            {
                "optimized_resume": optimized resume dict,
                "changes": list of changes made,
                "expected_score_improvement": estimated points
            }
        """
        base_resume = input_data.get("base_resume")
        job_description = input_data.get("job_description")
        ats_score_data = input_data.get("ats_score_data", {})
        company_data = input_data.get("company_data", {})
        
        if not base_resume or not job_description:
            raise ValueError("base_resume and job_description are required")
        
        # Get missing keywords and recommendations
        missing_keywords = ats_score_data.get("missing_keywords", [])
        recommendations = ats_score_data.get("recommendations", [])
        current_score = ats_score_data.get("score", 0)
        
        # Build optimization prompt
        prompt = self._build_optimization_prompt(
            base_resume, 
            job_description, 
            missing_keywords, 
            recommendations,
            company_data
        )
        
        # Get optimized resume from LLM
        response = await self.invoke_llm(prompt)
        
        # Parse response
        import json
        try:
            # Clean response
            cleaned_response = response.strip()
            if "```json" in cleaned_response:
                cleaned_response = cleaned_response.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned_response:
                cleaned_response = cleaned_response.split("```")[1].split("```")[0].strip()
                
            result = json.loads(cleaned_response)
            optimized_resume = result.get("optimized_resume", base_resume)
            changes = result.get("changes", [])
            
            # Estimate score improvement
            keywords_added = len([c for c in changes if "keyword" in c.lower()])
            estimated_improvement = min(keywords_added * 2, 20)  # Max 20 points improvement
            
            self.log(f"Optimized resume. Expected improvement: +{estimated_improvement} points")
            
            return {
                "optimized_resume": optimized_resume,
                "changes": changes,
                "expected_score_improvement": estimated_improvement,
                "new_estimated_score": min(current_score + estimated_improvement, 100)
            }
            
        except json.JSONDecodeError:
            self.log("Failed to parse LLM response", level="error")
            return {
                "optimized_resume": base_resume,
                "changes": ["Optimization failed - using original resume"],
                "expected_score_improvement": 0,
                "new_estimated_score": current_score
            }
    
    def _build_optimization_prompt(
        self, 
        base_resume: Dict[str, Any], 
        job_description: str,
        missing_keywords: List[str],
        recommendations: List[str],
        company_data: Dict[str, Any]
    ) -> str:
        """Build the optimization prompt"""
        
        company_context = ""
        if company_data:
            tech_stack = company_data.get("tech_stack", {})
            culture = company_data.get("culture", {})
            company_context = f"""
Company Context:
- Tech Stack: {tech_stack.get('languages', [])}
- Company Values: {culture.get('values', [])}
- Work Style: {culture.get('work_style', 'Unknown')}
"""
        
        prompt = f"""Optimize this resume for the job description below.

Job Description:
{job_description}

{company_context}

Current Resume:
{json.dumps(base_resume, indent=2)}

Missing Keywords: {', '.join(missing_keywords[:10])}

ATS Recommendations:
{chr(10).join(f'- {rec}' for rec in recommendations)}

Instructions:
1. Add missing keywords naturally where they fit (in skills, experience descriptions)
2. Reorder experience to highlight most relevant roles first
3. Adjust language to match job description tone
4. Emphasize skills that match company tech stack
5. Keep all information truthful - DO NOT fabricate

Return JSON:
{{
  "optimized_resume": {{same structure as input resume}},
  "changes": ["List of specific changes made"]
}}
"""
        return prompt
    
    async def create_resume_diff(self, base_resume: Dict[str, Any], optimized_resume: Dict[str, Any]) -> List[Dict[str, str]]:
        """Create a diff showing changes between base and optimized resume"""
        diffs = []
        
        # Compare skills
        base_skills = set(self._flatten_skills(base_resume.get("skills", {})))
        opt_skills = set(self._flatten_skills(optimized_resume.get("skills", {})))
        
        added_skills = opt_skills - base_skills
        if added_skills:
            diffs.append({
                "section": "skills",
                "type": "addition",
                "content": f"Added skills: {', '.join(added_skills)}"
            })
        
        # Compare experience descriptions
        base_exp = base_resume.get("experience", [])
        opt_exp = optimized_resume.get("experience", [])
        
        for i, (base_job, opt_job) in enumerate(zip(base_exp, opt_exp)):
            if base_job.get("responsibilities") != opt_job.get("responsibilities"):
                diffs.append({
                    "section": "experience",
                    "type": "modification",
                    "content": f"Updated responsibilities for {opt_job.get('title', 'position ' + str(i))}"
                })
        
        return diffs
    
    def _flatten_skills(self, skills_dict: Dict[str, List[str]]) -> List[str]:
        """Flatten skills dictionary to list"""
        all_skills = []
        if isinstance(skills_dict, dict):
            for category in skills_dict.values():
                if isinstance(category, list):
                    all_skills.extend(category)
        elif isinstance(skills_dict, list):
            all_skills = skills_dict
        return all_skills
