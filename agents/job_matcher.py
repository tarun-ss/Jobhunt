"""
Job Matcher Agent
Matches candidates to jobs based on skills, experience, and company fit
"""
import logging
from typing import Dict, List, Any, Tuple
import json

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class JobMatcher(BaseAgent):
    """Agent that matches candidates to jobs"""
    
    def __init__(self):
        super().__init__(
            name="JobMatcher",
            system_prompt="""You are an expert job matching system. You analyze candidate profiles and job requirements to determine fit.

Consider:
1. Skills match (technical and soft skills)
2. Experience level and relevance
3. Career trajectory alignment
4. Company culture fit
5. Location and work style preferences

Provide honest assessments - don't force matches that aren't good fits."""
        )
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Match a candidate to a job
        
        Args:
            input_data: {
                "resume_data": parsed resume,
                "job_posting": job details,
                "company_data": optional company info from MCP
            }
            
        Returns:
            {
                "match_score": 0-100,
                "match_level": "Excellent/Good/Fair/Poor",
                "strengths": list of matching points,
                "gaps": list of missing requirements,
                "recommendation": "Apply/Maybe/Skip",
                "reasoning": explanation
            }
        """
        resume_data = input_data.get("resume_data")
        job_posting = input_data.get("job_posting")
        company_data = input_data.get("company_data", {})
        
        if not resume_data or not job_posting:
            raise ValueError("resume_data and job_posting are required")
        
        # Calculate match score
        match_result = await self._calculate_match(
            resume_data,
            job_posting,
            company_data
        )
        
        self.log(f"Match score: {match_result['match_score']}/100 - {match_result['recommendation']}")
        return match_result
    
    async def _calculate_match(
        self,
        resume_data: Dict[str, Any],
        job_posting: Dict[str, Any],
        company_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate job match score"""
        
        # Extract candidate info
        candidate_skills = self._extract_skills(resume_data)
        candidate_experience = resume_data.get("experience", [])
        
        # Build matching prompt
        prompt = f"""Analyze this job match.

Candidate Profile:
- Skills: {', '.join(candidate_skills[:10])}
- Experience: {len(candidate_experience)} roles
- Latest Role: {candidate_experience[0].get('title', 'N/A') if candidate_experience else 'N/A'}
- Summary: {resume_data.get('summary', 'N/A')}

Job Requirements:
{job_posting.get('description', 'N/A')}

Company: {job_posting.get('company', 'Unknown')}
{f"Company Tech Stack: {company_data.get('tech_stack', {}).get('languages', [])}" if company_data else ""}

Evaluate the match and return JSON:
{{
  "match_score": 75,
  "match_level": "Good",
  "strengths": ["Has required Python skills", "Experience with cloud platforms"],
  "gaps": ["No Kubernetes experience", "Less than required 5 years"],
  "recommendation": "Apply",
  "reasoning": "Strong technical match despite minor experience gap"
}}

Match levels: Excellent (90-100), Good (70-89), Fair (50-69), Poor (<50)
Recommendations: Apply (70+), Maybe (50-69), Skip (<50)
"""
        
        response = await self.invoke_llm(prompt)
        
        try:
            # Clean response
            cleaned_response = response.strip()
            if "```json" in cleaned_response:
                cleaned_response = cleaned_response.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned_response:
                cleaned_response = cleaned_response.split("```")[1].split("```")[0].strip()
                
            result = json.loads(cleaned_response)
            return result
        except json.JSONDecodeError:
            # Fallback scoring
            return {
                "match_score": 60,
                "match_level": "Fair",
                "strengths": ["Unable to parse detailed analysis"],
                "gaps": [],
                "recommendation": "Maybe",
                "reasoning": response[:200]
            }
    
    def _extract_skills(self, resume_data: Dict[str, Any]) -> List[str]:
        """Extract all skills from resume"""
        skills = []
        
        if "skills" in resume_data:
            skill_data = resume_data["skills"]
            if isinstance(skill_data, dict):
                for category in skill_data.values():
                    if isinstance(category, list):
                        skills.extend(category)
            elif isinstance(skill_data, list):
                skills.extend(skill_data)
        
        return list(set(skills))
    
    async def batch_match(
        self,
        resume_data: Dict[str, Any],
        job_postings: List[Dict[str, Any]],
        min_score: int = 50
    ) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
        """Match a candidate against multiple jobs
        
        Args:
            resume_data: Candidate resume
            job_postings: List of job postings
            min_score: Minimum match score to include
            
        Returns:
            List of (job, match_result) tuples, sorted by score
        """
        matches = []
        
        for job in job_postings:
            try:
                match_result = await self.run({
                    "resume_data": resume_data,
                    "job_posting": job
                })
                
                if match_result["match_score"] >= min_score:
                    matches.append((job, match_result))
                    
            except Exception as e:
                self.log(f"Failed to match job {job.get('title', 'Unknown')}: {e}", level="warning")
        
        # Sort by match score (highest first)
        matches.sort(key=lambda x: x[1]["match_score"], reverse=True)
        
        return matches
