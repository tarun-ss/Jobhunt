"""
Company Researcher Agent
Gathers company intelligence and populates MCP server
"""
import logging
from typing import Dict, List, Any, Optional
import json

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class CompanyResearcher(BaseAgent):
    """Agent that researches companies and extracts intelligence"""
    
    def __init__(self):
        super().__init__(
            name="CompanyResearcher",
            system_prompt="""You are an expert company researcher. You analyze job descriptions and public information to extract company intelligence.

Extract:
1. Tech Stack (languages, frameworks, tools, cloud platforms)
2. Company Culture (values, work style, team structure)
3. Industry and Domain
4. Company Size and Stage
5. Key Products/Services

Be accurate and only include information you're confident about."""
        )
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Research a company
        
        Args:
            input_data: {
                "company_name": str,
                "job_descriptions": list of job description texts,
                "additional_context": optional extra info
            }
            
        Returns:
            {
                "company_id": str,
                "name": str,
                "tech_stack": {...},
                "culture": {...},
                "overview": {...},
                "confidence_score": 0.0-1.0
            }
        """
        company_name = input_data.get("company_name")
        job_descriptions = input_data.get("job_descriptions", [])
        additional_context = input_data.get("additional_context", "")
        
        if not company_name:
            raise ValueError("company_name is required")
        
        # Analyze job descriptions to extract company info
        company_data = await self._analyze_company(
            company_name,
            job_descriptions,
            additional_context
        )
        
        self.log(f"Researched {company_name} - Confidence: {company_data.get('confidence_score', 0)}")
        return company_data
    
    async def _analyze_company(
        self,
        company_name: str,
        job_descriptions: List[str],
        additional_context: str
    ) -> Dict[str, Any]:
        """Analyze company from job descriptions"""
        
        # Combine all job descriptions
        combined_jobs = "\n\n---\n\n".join(job_descriptions[:5])  # Max 5 jobs
        
        prompt = f"""Analyze these job descriptions from {company_name} and extract company intelligence.

Job Descriptions:
{combined_jobs}

{f"Additional Context: {additional_context}" if additional_context else ""}

Extract and return JSON:
{{
  "company_id": "{company_name.lower().replace(' ', '_')}",
  "name": "{company_name}",
  "tech_stack": {{
    "languages": ["Python", "Java", ...],
    "frameworks": ["React", "Django", ...],
    "tools": ["Docker", "Git", ...],
    "cloud": ["AWS", "GCP", ...],
    "databases": ["PostgreSQL", "MongoDB", ...]
  }},
  "culture": {{
    "values": ["Innovation", "Collaboration", ...],
    "work_style": "Remote/Hybrid/Office",
    "team_size": "Small/Medium/Large",
    "interview_difficulty": "Easy/Medium/Hard"
  }},
  "overview": {{
    "industry": "Technology/Finance/Healthcare/etc",
    "domain": "SaaS/E-commerce/AI/etc",
    "size": "<50/50-200/200-1000/1000+",
    "stage": "Startup/Growth/Enterprise"
  }},
  "confidence_score": 0.85
}}

Only include technologies/values you see mentioned multiple times. Set confidence_score based on how much information you have.
"""
        
        response = await self.invoke_llm(prompt)
        
        try:
            # Clean response
            cleaned_response = response.strip()
            if "```json" in cleaned_response:
                cleaned_response = cleaned_response.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned_response:
                cleaned_response = cleaned_response.split("```")[1].split("```")[0].strip()
                
            company_data = json.loads(cleaned_response)
            return company_data
        except json.JSONDecodeError:
            # Fallback structure
            self.log("Failed to parse LLM response, using fallback", level="warning")
            return {
                "company_id": company_name.lower().replace(" ", "_"),
                "name": company_name,
                "tech_stack": {"languages": [], "frameworks": [], "tools": []},
                "culture": {"values": [], "work_style": "Unknown"},
                "overview": {"industry": "Unknown", "size": "Unknown"},
                "confidence_score": 0.3,
                "raw_analysis": response
            }
    
    async def extract_tech_stack_from_job(self, job_description: str) -> List[str]:
        """Quick extraction of tech stack from a single job description"""
        
        prompt = f"""Extract all technologies mentioned in this job description.

Job Description:
{job_description}

Return a JSON list of technologies:
["Python", "React", "AWS", "Docker", ...]

Only include specific technologies, not general terms like "programming" or "software".
"""
        
        response = await self.invoke_llm(prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract from text
            import re
            # Common tech terms
            tech_terms = [
                'Python', 'Java', 'JavaScript', 'TypeScript', 'Go', 'Rust', 'C++',
                'React', 'Angular', 'Vue', 'Django', 'Flask', 'Spring', 'Node.js',
                'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'PostgreSQL', 'MongoDB'
            ]
            found = [tech for tech in tech_terms if tech.lower() in job_description.lower()]
            return found
    
    async def update_mcp_server(self, company_data: Dict[str, Any], mcp_client) -> bool:
        """Update MCP server with company data
        
        Args:
            company_data: Company information dict
            mcp_client: MCP client instance
            
        Returns:
            Success boolean
        """
        try:
            # Update tech stack
            await mcp_client.call_tool("add_company_data", {
                "company_name": company_data["name"],
                "field": "tech_stack",
                "data": company_data["tech_stack"],
                "source": "job_description_analysis"
            })
            
            # Update culture
            await mcp_client.call_tool("add_company_data", {
                "company_name": company_data["name"],
                "field": "culture",
                "data": company_data["culture"],
                "source": "job_description_analysis"
            })
            
            # Update overview
            await mcp_client.call_tool("add_company_data", {
                "company_name": company_data["name"],
                "field": "overview",
                "data": company_data["overview"],
                "source": "job_description_analysis"
            })
            
            self.log(f"Updated MCP server with {company_data['name']} data")
            return True
            
        except Exception as e:
            self.log(f"Failed to update MCP server: {e}", level="error")
            return False
