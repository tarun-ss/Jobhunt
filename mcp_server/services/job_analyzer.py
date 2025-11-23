"""
Job Analyzer Service - Extract requirements from job descriptions using Groq AI

Analyzes job postings to extract:
- Required skills (must-have)
- Preferred skills (nice-to-have)
- Experience requirements
- Education requirements
- Important keywords for ATS
"""

import os
import re
from typing import Dict, List
from groq import Groq

class JobAnalyzer:
    def __init__(self):
        """Initialize Groq client"""
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
    
    def analyze_job(self, job_description: str, job_title: str = "") -> Dict:
        """
        Analyze job description to extract requirements
        
        Args:
            job_description: Full job description text
            job_title: Job title (optional, helps with context)
            
        Returns:
            Dictionary with structured job requirements
        """
        
        system_prompt = """You are an expert HR analyst and job description parser.
Extract structured requirements from the job posting provided.

Return a JSON object with these fields:
{
  "required_skills": ["Python", "React", ...],  // Must-have skills
  "preferred_skills": ["Docker", "AWS", ...],  // Nice-to-have skills
  "experience_required_years": 5,  // Minimum years required (number, 0 if not specified)
  "experience_level": "Senior",  // Entry/Junior/Mid/Senior/Lead/Executive
  "education_required": ["Bachelor's Degree"],  // Required education
  "certifications_preferred": ["AWS Certified"],  // Preferred certifications
  "keywords": ["agile", "microservices", "cloud"],  // Important ATS keywords
  "responsibilities": ["Design systems", "Lead team"],  // Key responsibilities
  "company_culture": "Innovation-focused, collaborative"  // Culture indicators
}

Be precise about which skills are REQUIRED vs PREFERRED. Look for words like:
- Required: "must have", "required", "essential", "mandatory"
- Preferred: "nice to have", "preferred", "bonus", "plus"
"""

        try:
            prompt = f"Job Title: {job_title}\n\nJob Description:\n{job_description}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            # Ensure all fields exist
            result.setdefault("required_skills", [])
            result.setdefault("preferred_skills", [])
            result.setdefault("experience_required_years", 0)
            result.setdefault("experience_level", "Mid")
            result.setdefault("education_required", [])
            result.setdefault("certifications_preferred", [])
            result.setdefault("keywords", [])
            result.setdefault("responsibilities", [])
            result.setdefault("company_culture", "")
            
            return result
            
        except Exception as e:
            print(f"Error analyzing job with Groq: {e}")
            return self._fallback_analyze(job_description)
    
    def extract_required_skills(self, job_description: str) -> List[str]:
        """Extract only required skills"""
        analysis = self.analyze_job(job_description)
        return analysis.get("required_skills", [])
    
    def extract_preferred_skills(self, job_description: str) -> List[str]:
        """Extract only preferred skills"""
        analysis = self.analyze_job(job_description)
        return analysis.get("preferred_skills", [])
    
    def calculate_keyword_density(self, job_description: str) -> Dict[str, int]:
        """Calculate frequency of important keywords"""
        analysis = self.analyze_job(job_description)
        keywords = analysis.get("keywords", [])
        
        text_lower = job_description.lower()
        keyword_counts = {}
        
        for keyword in keywords:
            count = text_lower.count(keyword.lower())
            if count > 0:
                keyword_counts[keyword] = count
        
        return keyword_counts
    
    def _fallback_analyze(self, job_description: str) -> Dict:
        """Fallback analysis using regex if Groq fails"""
        
        # Common tech skills
        tech_skills = [
            "python", "java", "javascript", "react", "node.js", "aws", "docker",
            "kubernetes", "sql", "mongodb", "git", "agile", "scrum"
        ]
        
        text_lower = job_description.lower()
        found_skills = [skill for skill in tech_skills if skill in text_lower]
        
        # Detect experience years
        years_pattern = r'(\d+)\s*\+?\s*years?'
        years_matches = re.findall(years_pattern, text_lower)
        experience_years = max([int(y) for y in years_matches], default=0) if years_matches else 0
        
        # Detect level
        level = "Mid"
        if "senior" in text_lower or "lead" in text_lower:
            level = "Senior"
        elif "junior" in text_lower or "entry" in text_lower:
            level = "Junior"
        
        return {
            "required_skills": found_skills[:len(found_skills)//2] if found_skills else [],
            "preferred_skills": found_skills[len(found_skills)//2:] if found_skills else [],
            "experience_required_years": experience_years,
            "experience_level": level,
            "education_required": [],
            "certifications_preferred": [],
            "keywords": found_skills,
            "responsibilities": [],
            "company_culture": ""
        }


# Singleton instance
job_analyzer = JobAnalyzer()


def analyze_job_description(job_description: str, job_title: str = "") -> Dict:
    """Convenience function to analyze job"""
    return job_analyzer.analyze_job(job_description, job_title)
