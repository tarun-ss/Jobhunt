"""
Resume Parser Service - Extract structured data from resume text using Groq AI

This service uses Groq LLM to intelligently parse resumes and extract:
- Technical and soft skills
- Work experience (years, roles, companies)
- Education (degrees, institutions)
- Certifications and licenses
"""

import os
import re
from typing import Dict, List, Optional
from groq import Groq

class ResumeParser:
    def __init__(self):
        """Initialize Groq client"""
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
    
    def parse_resume_full(self, resume_text: str) -> Dict:
        """
        Parse complete resume using Groq AI
        
        Args:
            resume_text: Full text content of resume
            
        Returns:
            Dictionary with structured resume data
        """
        
        system_prompt = """You are an expert resume parser and HR analyst.
Extract structured information from the resume text provided.

Return a JSON object with these fields:
{
  "name": "John Doe", // Full name of the candidate
  "email": "john@example.com", // Email address
  "skills": ["skill1", "skill2", ...],  // All technical and soft skills
  "technical_skills": ["Python", "React", ...],  // Only technical skills
  "soft_skills": ["Leadership", "Communication", ...],  // Only soft skills
  "experience_years": 5,  // Total years of professional experience (number)
  "job_titles": ["Senior Engineer", "Tech Lead"],  // All job titles held
  "companies": ["Google", "Microsoft"],  // All companies worked at
  "education": ["BS Computer Science", "MS Data Science"],  // Degrees
  "institutions": ["MIT", "Stanford"],  // Schools attended
  "certifications": ["AWS Certified", "PMP"],  // Certifications
  "summary": "Brief professional summary..."  // 2-3 sentence summary
}

Be comprehensive but accurate. Only include information explicitly stated in the resume.
For experience_years, calculate based on dates mentioned or estimate from career progression.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Parse this resume:\n\n{resume_text}"}
                ],
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            # Ensure all required fields exist
            result.setdefault("name", "Candidate")
            result.setdefault("email", "")
            result.setdefault("skills", [])
            result.setdefault("technical_skills", [])
            result.setdefault("soft_skills", [])
            result.setdefault("experience_years", 0)
            result.setdefault("job_titles", [])
            result.setdefault("companies", [])
            result.setdefault("education", [])
            result.setdefault("institutions", [])
            result.setdefault("certifications", [])
            result.setdefault("summary", "")
            
            return result
            
        except Exception as e:
            print(f"Error parsing resume with Groq: {e}")
            # Fallback to basic parsing
            return self._fallback_parse(resume_text)
    
    def extract_skills(self, resume_text: str) -> List[str]:
        """Extract skills from resume"""
        full_parse = self.parse_resume_full(resume_text)
        return full_parse.get("skills", [])
    
    def extract_experience(self, resume_text: str) -> Dict:
        """Extract experience details"""
        full_parse = self.parse_resume_full(resume_text)
        return {
            "years": full_parse.get("experience_years", 0),
            "job_titles": full_parse.get("job_titles", []),
            "companies": full_parse.get("companies", [])
        }
    
    def extract_education(self, resume_text: str) -> Dict:
        """Extract education details"""
        full_parse = self.parse_resume_full(resume_text)
        return {
            "degrees": full_parse.get("education", []),
            "institutions": full_parse.get("institutions", [])
        }
    
    def extract_certifications(self, resume_text: str) -> List[str]:
        """Extract certifications"""
        full_parse = self.parse_resume_full(resume_text)
        return full_parse.get("certifications", [])
    
    def _fallback_parse(self, resume_text: str) -> Dict:
        """Fallback parsing using simple regex if Groq fails"""
        
        # Common technical skills
        tech_keywords = [
            "python", "java", "javascript", "react", "node.js", "aws", "docker",
            "kubernetes", "sql", "mongodb", "git", "agile", "scrum", "ci/cd",
            "typescript", "angular", "vue", "django", "flask", "fastapi",
            "machine learning", "ai", "data science", "tensorflow", "pytorch"
        ]
        
        # Find skills
        text_lower = resume_text.lower()
        found_skills = [skill for skill in tech_keywords if skill in text_lower]
        
        # Estimate experience years (look for patterns like "5 years", "2023-2024")
        years_pattern = r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)'
        years_matches = re.findall(years_pattern, text_lower)
        experience_years = max([int(y) for y in years_matches], default=0)
        
        return {
            "name": "Candidate",
            "email": "",
            "skills": found_skills,
            "technical_skills": found_skills,
            "soft_skills": [],
            "experience_years": experience_years,
            "job_titles": [],
            "companies": [],
            "education": [],
            "institutions": [],
            "certifications": [],
            "summary": ""
        }


# Singleton instance
resume_parser = ResumeParser()


def parse_resume(resume_text: str) -> Dict:
    """Convenience function to parse resume"""
    return resume_parser.parse_resume_full(resume_text)
