"""
ATS Scorer Agent
Scores resume compatibility with job descriptions for ATS systems
"""
import logging
from typing import Dict, List, Any
import re

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ATSScorer(BaseAgent):
    """Agent that scores resume ATS compatibility"""
    
    def __init__(self):
        super().__init__(
            name="ATSScorer",
            system_prompt="""You are an ATS (Applicant Tracking System) expert. 
            
Your job is to analyze how well a resume matches a job description and score it from 0-100.

Consider:
1. Keyword matching (40 points) - How many job requirements appear in the resume?
2. Skills alignment (30 points) - Do candidate skills match required skills?
3. Experience relevance (20 points) - Is the experience level and domain appropriate?
4. Format quality (10 points) - Is the resume ATS-friendly (clear sections, no images/tables)?

Provide specific feedback on what's missing and how to improve the score."""
        )
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Score a resume against a job description
        
        Args:
            input_data: {
                "resume_data": parsed resume dict,
                "job_description": job description text,
                "company_tech_stack": optional list of company technologies
            }
            
        Returns:
            {
                "score": 0-100,
                "breakdown": {keyword_score, skills_score, experience_score, format_score},
                "missing_keywords": [],
                "recommendations": []
            }
        """
        resume_data = input_data.get("resume_data")
        job_description = input_data.get("job_description")
        company_tech_stack = input_data.get("company_tech_stack", [])
        
        if not resume_data or not job_description:
            raise ValueError("resume_data and job_description are required")
        
        # Extract keywords from job description
        job_keywords = self._extract_keywords(job_description)
        
        # Extract skills from resume
        resume_skills = self._extract_resume_skills(resume_data)
        
        # Calculate scores
        keyword_score = self._calculate_keyword_score(resume_skills, job_keywords)
        skills_score = self._calculate_skills_score(resume_skills, job_keywords, company_tech_stack)
        
        # Use LLM for experience and format analysis
        llm_analysis = await self._llm_analysis(resume_data, job_description)
        
        # Combine scores
        total_score = (
            keyword_score * 0.4 +
            skills_score * 0.3 +
            llm_analysis.get("experience_score", 70) * 0.2 +
            llm_analysis.get("format_score", 90) * 0.1
        )
        
        # Find missing keywords
        missing_keywords = list(set(job_keywords) - set(resume_skills))
        
        result = {
            "score": round(total_score, 1),
            "breakdown": {
                "keyword_score": round(keyword_score, 1),
                "skills_score": round(skills_score, 1),
                "experience_score": llm_analysis.get("experience_score", 70),
                "format_score": llm_analysis.get("format_score", 90)
            },
            "missing_keywords": missing_keywords[:10],  # Top 10 missing
            "recommendations": llm_analysis.get("recommendations", []),
            "strengths": llm_analysis.get("strengths", [])
        }
        
        self.log(f"ATS Score: {result['score']}/100")
        return result
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Common tech keywords and skills
        keywords = []
        
        # Extract capitalized words (likely technologies/tools)
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        keywords.extend(words)
        
        # Extract common tech terms
        tech_terms = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'React', 'Angular', 'Vue',
            'Node.js', 'Django', 'Flask', 'Spring', 'AWS', 'Azure', 'GCP', 'Docker',
            'Kubernetes', 'SQL', 'NoSQL', 'MongoDB', 'PostgreSQL', 'Redis',
            'Git', 'CI/CD', 'Agile', 'Scrum', 'REST', 'GraphQL', 'API',
            'Machine Learning', 'AI', 'Data Science', 'TensorFlow', 'PyTorch'
        ]
        
        text_lower = text.lower()
        for term in tech_terms:
            if term.lower() in text_lower:
                keywords.append(term)
        
        return list(set(keywords))
    
    def _extract_resume_skills(self, resume_data: Dict[str, Any]) -> List[str]:
        """Extract all skills from resume"""
        skills = []
        
        # 1. Try structured skills
        if "skills" in resume_data:
            skill_data = resume_data["skills"]
            if isinstance(skill_data, dict):
                for category in skill_data.values():
                    if isinstance(category, list):
                        skills.extend(category)
            elif isinstance(skill_data, list):
                skills.extend(skill_data)
        
        # 2. Try experience descriptions
        if "experience" in resume_data:
            for exp in resume_data["experience"]:
                if "responsibilities" in exp:
                    for resp in exp["responsibilities"]:
                        skills.extend(self._extract_keywords(resp))
                        
        # 3. Fallback: Raw text extraction (if skills are empty)
        if not skills and "raw_text" in resume_data:
            self.log("Using raw text fallback for skills extraction")
            skills.extend(self._extract_keywords(resume_data["raw_text"]))
        
        return list(set(skills))
    
    def _calculate_keyword_score(self, resume_skills: List[str], job_keywords: List[str]) -> float:
        """Calculate keyword matching score"""
        if not job_keywords:
            return 100.0
        
        resume_skills_lower = [s.lower() for s in resume_skills]
        job_keywords_lower = [k.lower() for k in job_keywords]
        
        matches = sum(1 for keyword in job_keywords_lower if keyword in resume_skills_lower)
        score = (matches / len(job_keywords)) * 100
        
        return min(score, 100.0)
    
    def _calculate_skills_score(self, resume_skills: List[str], job_keywords: List[str], company_tech_stack: List[str]) -> float:
        """Calculate skills alignment score"""
        all_required = set(job_keywords + company_tech_stack)
        if not all_required:
            return 100.0
        
        resume_skills_lower = [s.lower() for s in resume_skills]
        required_lower = [r.lower() for r in all_required]
        
        matches = sum(1 for req in required_lower if req in resume_skills_lower)
        score = (matches / len(all_required)) * 100
        
        return min(score, 100.0)
    
    async def _llm_analysis(self, resume_data: Dict[str, Any], job_description: str) -> Dict[str, Any]:
        """Use LLM to analyze experience relevance and format"""
        prompt = f"""Analyze this resume against the job description.

Job Description:
{job_description}

Resume Summary:
{resume_data.get('summary', 'N/A')}

Experience:
{resume_data.get('experience', [])}

Provide:
1. experience_score (0-100): How relevant is the candidate's experience?
2. format_score (0-100): How ATS-friendly is the resume format?
3. recommendations: List of 3-5 specific improvements
4. strengths: List of 2-3 key strengths

Return as JSON: {{"experience_score": X, "format_score": Y, "recommendations": [], "strengths": []}}
"""
        
        response = await self.invoke_llm(prompt)
        
        import json
        try:
            # Clean response
            cleaned_response = response.strip()
            if "```json" in cleaned_response:
                cleaned_response = cleaned_response.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned_response:
                cleaned_response = cleaned_response.split("```")[1].split("```")[0].strip()
                
            llm_analysis = json.loads(cleaned_response)
        except json.JSONDecodeError:
            llm_analysis = {
                "experience_score": 70,
                "format_score": 90,
                "recommendations": ["Unable to parse LLM response"],
                "strengths": []
            }
        return llm_analysis
