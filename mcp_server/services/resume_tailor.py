"""
Resume Tailor Service - Generate company-specific tailored resumes using Groq AI

This service uses Groq LLM to:
1. Analyze the gap between base resume and job description
2. Rewrite the professional summary to target the specific role
3. Reorder and emphasize relevant work experience
4. Inject ATS-friendly keywords naturally
5. Generate a complete markdown resume optimized for the job
"""

import os
from typing import Dict
from groq import Groq

class ResumeTailor:
    def __init__(self):
        """Initialize Groq client"""
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
    
    def tailor_resume(
        self,
        base_resume_text: str,
        job_description: str,
        job_title: str,
        company_name: str
    ) -> Dict:
        """
        Generate a tailored resume for a specific job
        
        Args:
            base_resume_text: Original resume content
            job_description: Target job description
            job_title: Target job title
            company_name: Target company name
            
        Returns:
            Dictionary with tailored resume content and changes made
        """
        
        system_prompt = """You are an expert Executive Resume Writer and ATS Optimization Specialist.
Your goal is to rewrite a candidate's resume to perfectly match a specific job opportunity at a specific company.

RULES:
1. TRUTHFULNESS: Do NOT invent experiences, skills, or degrees. Only use facts present in the base resume.
2. RELEVANCE: Reorder bullet points to prioritize experience relevant to the job description.
3. KEYWORDS: Naturally incorporate keywords from the job description into the summary and bullet points.
4. FORMAT: Output the result in clean, professional Markdown format.
5. TONE: Professional, action-oriented, and confident.

OUTPUT FORMAT:
Return a JSON object with two fields:
1. "tailored_content": The complete markdown text of the new resume.
2. "changes_made": A list of 3-5 specific changes you made to optimize it (e.g., "Emphasized Python experience", "Added 'Agile' keyword to summary").
"""

        user_prompt = f"""
TARGET JOB:
Title: {job_title}
Company: {company_name}
Description:
{job_description[:2000]}... (truncated)

BASE RESUME:
{base_resume_text}

INSTRUCTIONS:
Tailor the base resume for this specific job. 
- Write a new Professional Summary that mentions the target role and company.
- Highlight skills that match the job requirements.
- Use the same contact info as the base resume.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4,
                max_tokens=2500,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            return {
                "tailored_content": result.get("tailored_content", ""),
                "changes_made": result.get("changes_made", [])
            }
            
        except Exception as e:
            print(f"Error tailoring resume: {e}")
            return {
                "tailored_content": base_resume_text,
                "changes_made": ["Error generating tailored resume. Returned original."]
            }


# Singleton instance
resume_tailor = ResumeTailor()


def generate_tailored_resume(
    base_resume: str,
    job_desc: str,
    title: str,
    company: str
) -> Dict:
    """Convenience function to tailor resume"""
    return resume_tailor.tailor_resume(base_resume, job_desc, title, company)
