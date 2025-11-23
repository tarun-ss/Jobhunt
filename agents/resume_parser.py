"""
Resume Parser Agent
Extracts structured data from PDF/DOCX resumes
"""
import logging
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
import PyPDF2
import docx

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ResumeParser(BaseAgent):
    """Agent that parses resumes and extracts structured information"""
    
    def __init__(self):
        super().__init__(
            name="ResumeParser",
            system_prompt="""You are a strict JSON-only resume parsing API. 
            
Instructions:
1. Extract information from the resume text provided.
2. Output ONLY valid JSON matching the specified structure.
3. DO NOT include any conversational text, markdown formatting, or code blocks.
4. If a field is missing, use null or empty list [].
5. Your entire response must be parseable by json.loads()."""
        )
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse a resume file
        
        Args:
            input_data: {
                "resume_path": "path/to/resume.pdf" or "path/to/resume.docx"
            }
            
        Returns:
            Structured resume data
        """
        resume_path = input_data.get("resume_path")
        if not resume_path:
            raise ValueError("resume_path is required")
        
        # Extract text from file
        resume_text = self._extract_text(resume_path)
        
        # Use LLM to parse the resume
        prompt = f"""Parse this resume and extract structured information.

Resume Text:
{resume_text}

Return a JSON object with these fields:
- contact: {{name, email, phone, location, linkedin}}
- summary: brief professional summary
- skills: {{technical: [], soft: [], tools: [], languages: []}}
- experience: [{{company, title, start_date, end_date, responsibilities: []}}]
- education: [{{degree, institution, graduation_date, gpa}}]
- certifications: []
- projects: [{{name, description, technologies: []}}]
"""
        
        response = await self.invoke_llm(prompt)
        
        # Log raw response for debugging
        with open("resume_parser_debug.log", "w", encoding="utf-8") as f:
            f.write(response)
        
        # Parse JSON response
        import json
        import re
        
        try:
            # Clean response (remove markdown code blocks)
            cleaned_response = response.strip()
            if "```json" in cleaned_response:
                cleaned_response = cleaned_response.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned_response:
                cleaned_response = cleaned_response.split("```")[1].split("```")[0].strip()
            
            # Find JSON object if still not clean
            if not cleaned_response.startswith("{"):
                match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                if match:
                    cleaned_response = match.group(0)
                
            parsed_data = json.loads(cleaned_response)
            # Add raw text to the output for fallback usage
            parsed_data["raw_text"] = resume_text
            
            self.log(f"Successfully parsed resume: {parsed_data.get('contact', {}).get('name', 'Unknown')}")
            return parsed_data
        except json.JSONDecodeError as e:
            # If LLM didn't return valid JSON, wrap it
            self.log(f"LLM response wasn't valid JSON: {e}", level="warning")
            return {
                "raw_text": resume_text,
                "llm_analysis": response
            }
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF or DOCX file"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Resume file not found: {file_path}")
        
        if path.suffix.lower() == '.pdf':
            return self._extract_from_pdf(file_path)
        elif path.suffix.lower() in ['.docx', '.doc']:
            return self._extract_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            raise
    
    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX using docx2txt"""
        try:
            import docx2txt
            text = docx2txt.process(file_path)
            return text.strip()
        except Exception as e:
            logger.error(f"Failed to extract text from DOCX: {e}")
            raise
    
    def extract_skills(self, resume_data: Dict[str, Any]) -> List[str]:
        """Extract all skills from parsed resume data"""
        skills = []
        
        if "skills" in resume_data:
            skill_data = resume_data["skills"]
            if isinstance(skill_data, dict):
                for category in ["technical", "soft", "tools", "languages"]:
                    if category in skill_data:
                        skills.extend(skill_data[category])
            elif isinstance(skill_data, list):
                skills.extend(skill_data)
        
        return list(set(skills))  # Remove duplicates
