"""
Email Writer Agent
Generates personalized cold emails for job applications
"""
import logging
from typing import Dict, List, Any
import json

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class EmailWriter(BaseAgent):
    """Agent that writes personalized cold emails"""
    
    def __init__(self):
        super().__init__(
            name="EmailWriter",
            system_prompt="""You are an expert at writing compelling, personalized cold emails for job applications.

Your emails should:
1. Be concise (150-200 words max)
2. Reference specific company details (recent news, values, tech stack)
3. Highlight 2-3 relevant candidate achievements
4. Show genuine interest in the company
5. Include a clear call-to-action
6. Be professional but personable

Avoid:
- Generic templates
- Desperation or begging
- Listing entire resume
- Being too formal or stiff"""
        )
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a personalized cold email
        
        Args:
            input_data: {
                "job_posting": {title, company, description},
                "resume_data": parsed resume,
                "company_data": optional company info from MCP,
                "tone": optional ("professional", "casual", "enthusiastic")
            }
            
        Returns:
            {
                "subject": email subject line,
                "body": email body,
                "key_points": list of personalization points used
            }
        """
        job_posting = input_data.get("job_posting", {})
        resume_data = input_data.get("resume_data", {})
        company_data = input_data.get("company_data", {})
        tone = input_data.get("tone", "professional")
        
        if not job_posting or not resume_data:
            raise ValueError("job_posting and resume_data are required")
        
        # Build context for email
        prompt = self._build_email_prompt(
            job_posting, 
            resume_data, 
            company_data, 
            tone
        )
        
        # Generate email
        response = await self.invoke_llm(prompt)
        
        # Parse response
        try:
            # Clean response
            cleaned_response = response.strip()
            if "```json" in cleaned_response:
                cleaned_response = cleaned_response.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned_response:
                cleaned_response = cleaned_response.split("```")[1].split("```")[0].strip()
                
            result = json.loads(cleaned_response)
            self.log(f"Generated email for {job_posting.get('company', 'Unknown')} - {job_posting.get('title', 'Unknown')}")
            return result
        except json.JSONDecodeError:
            # Fallback if LLM doesn't return JSON
            return {
                "subject": f"Application for {job_posting.get('title', 'Position')} at {job_posting.get('company', 'Your Company')}",
                "body": response,
                "key_points": ["Unable to parse structured response"]
            }
    
    def _build_email_prompt(
        self, 
        job_posting: Dict[str, Any],
        resume_data: Dict[str, Any],
        company_data: Dict[str, Any],
        tone: str
    ) -> str:
        """Build the email generation prompt"""
        
        # Extract key info
        company_name = job_posting.get("company", "the company")
        job_title = job_posting.get("title", "this position")
        candidate_name = resume_data.get("contact", {}).get("name", "the candidate")
        
        # Build company context
        company_context = ""
        if company_data:
            tech_stack = company_data.get("tech_stack", {})
            culture = company_data.get("culture", {})
            recent_news = company_data.get("recent_news", [])
            
            company_context = f"""
Company Context:
- Tech Stack: {', '.join(tech_stack.get('languages', [])[:3])}
- Values: {', '.join(culture.get('values', [])[:2])}
- Recent News: {recent_news[0] if recent_news else 'N/A'}
"""
        
        # Extract top achievements
        achievements = self._extract_achievements(resume_data)
        
        prompt = f"""Write a personalized cold email for this job application.

Job: {job_title} at {company_name}
Candidate: {candidate_name}

{company_context}

Candidate's Top Achievements:
{chr(10).join(f'- {ach}' for ach in achievements[:3])}

Tone: {tone}

Requirements:
1. Subject line that stands out
2. Opening that references something specific about {company_name}
3. 2-3 sentences connecting candidate's experience to the role
4. Clear call-to-action (request for interview/call)
5. Professional closing
6. Total length: 150-200 words

Return JSON:
{{
  "subject": "...",
  "body": "...",
  "key_points": ["personalization point 1", "personalization point 2"]
}}
"""
        return prompt
    
    def _extract_achievements(self, resume_data: Dict[str, Any]) -> List[str]:
        """Extract key achievements from resume"""
        achievements = []
        
        # From summary
        if "summary" in resume_data:
            achievements.append(resume_data["summary"])
        
        # From experience
        if "experience" in resume_data:
            for exp in resume_data["experience"][:2]:  # Top 2 roles
                if "responsibilities" in exp:
                    # Look for quantifiable achievements
                    for resp in exp["responsibilities"][:2]:
                        if any(char.isdigit() for char in resp):  # Has numbers
                            achievements.append(resp)
                        elif len(achievements) < 3:
                            achievements.append(resp)
        
        return achievements[:5]
    
    async def generate_follow_up(self, original_email: Dict[str, Any], days_since: int) -> Dict[str, Any]:
        """Generate a follow-up email
        
        Args:
            original_email: The original email sent
            days_since: Days since original email
            
        Returns:
            Follow-up email dict
        """
        prompt = f"""Write a polite follow-up email.

Original email was sent {days_since} days ago.
Original subject: {original_email.get('subject', 'N/A')}

Requirements:
1. Brief reminder of original application
2. Reiterate interest
3. Ask about timeline
4. Keep it short (50-75 words)

Return JSON with subject and body.
"""
        
        response = await self.invoke_llm(prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "subject": f"Following up: {original_email.get('subject', 'My Application')}",
                "body": response
            }
