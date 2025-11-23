"""
Ghost Job Detector Agent
Detects fake/ghost job postings using ML and heuristics
"""
import logging
from typing import Dict, List, Any
import json
import re

from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class GhostJobDetector(BaseAgent):
    """Agent that detects ghost/fake job postings"""
    
    def __init__(self):
        super().__init__(
            "GhostJobDetector",
            system_prompt="""You are an expert at detecting fake or "ghost" job postings.

Ghost job indicators:
1. Vague job descriptions
2. No salary information
3. Excessive urgency ("Apply now!", "Immediate hire!")
4. Too many requirements for entry-level
5. Generic company descriptions
6. Typos and poor grammar
7. Unrealistic promises
8. Very old postings (>90 days)

Analyze job postings and provide a ghost job probability score."""
        )
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect if a job is a ghost job
        
        Args:
            input_data: {
                "job_posting": job dict,
                "company_history": optional company ghost job rate
            }
            
        Returns:
            {
                "is_ghost_job": bool,
                "confidence": 0.0-1.0,
                "ghost_score": 0-100 (higher = more likely ghost),
                "red_flags": list of issues found,
                "recommendation": "Apply" | "Caution" | "Skip"
            }
        """
        job_posting = input_data.get("job_posting")
        company_history = input_data.get("company_history", {})
        
        if not job_posting:
            raise ValueError("job_posting is required")
        
        # Calculate heuristic score
        heuristic_score = self._calculate_heuristic_score(job_posting)
        
        # Use LLM for deeper analysis
        llm_analysis = await self._llm_analysis(job_posting, company_history)
        
        # Combine scores
        final_score = (heuristic_score * 0.4) + (llm_analysis.get("score", 50) * 0.6)
        
        is_ghost = final_score > 60
        confidence = abs(final_score - 50) / 50  # 0-1 based on distance from 50
        
        result = {
            "is_ghost_job": is_ghost,
            "confidence": round(confidence, 2),
            "ghost_score": round(final_score, 1),
            "red_flags": llm_analysis.get("red_flags", []),
            "recommendation": self._get_recommendation(final_score)
        }
        
        self.log(f"Ghost score: {result['ghost_score']}/100 - {result['recommendation']}")
        return result
    
    def _calculate_heuristic_score(self, job: Dict[str, Any]) -> float:
        """Calculate ghost job score using heuristics"""
        score = 0
        description = job.get("description", "").lower()
        title = job.get("title", "").lower()
        
        # Red flag 1: No salary (20 points)
        if not job.get("salary"):
            score += 20
        
        # Red flag 2: Very short description (<100 chars) (15 points)
        if len(description) < 100:
            score += 15
        
        # Red flag 3: Urgency keywords (15 points)
        urgency_words = ["urgent", "immediate", "asap", "apply now", "hiring immediately"]
        if any(word in description for word in urgency_words):
            score += 15
        
        # Red flag 4: Excessive requirements for entry-level (10 points)
        if "entry" in title or "junior" in title:
            if "5+ years" in description or "10+ years" in description:
                score += 10
        
        # Red flag 5: Typos (count) (up to 15 points)
        typo_indicators = ["teh", "recieve", "seperate", "occured"]
        typo_count = sum(1 for typo in typo_indicators if typo in description)
        score += min(typo_count * 5, 15)
        
        # Red flag 6: Generic company name (10 points)
        generic_names = ["company", "corporation", "inc", "llc", "firm"]
        company = job.get("company", "").lower()
        if any(name in company for name in generic_names) and len(company) < 15:
            score += 10
        
        # Red flag 7: No specific requirements (15 points)
        if "requirements" not in description and "qualifications" not in description:
            score += 15
        
        return min(score, 100)
    
    async def _llm_analysis(self, job: Dict[str, Any], company_history: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM for deeper ghost job analysis"""
        
        prompt = f"""Analyze this job posting for ghost job indicators.

Job Title: {job.get('title', 'N/A')}
Company: {job.get('company', 'N/A')}
Description:
{job.get('description', 'N/A')[:500]}

{f"Company Ghost Job Rate: {company_history.get('ghost_job_rate', 'Unknown')}" if company_history else ""}

Evaluate:
1. Is the description vague or overly generic?
2. Are there unrealistic requirements?
3. Is there excessive urgency?
4. Are there grammar/spelling issues?
5. Does it seem like a real hiring need?

Return JSON:
{{
  "score": 0-100 (higher = more likely ghost),
  "red_flags": ["flag 1", "flag 2", ...],
  "analysis": "brief explanation"
}}
"""
        
        response = await self.invoke_llm(prompt)
        
        try:
            # Clean response
            cleaned_response = response.strip()
            if "```json" in cleaned_response:
                cleaned_response = cleaned_response.split("```json")[1].split("```")[0].strip()
            elif "```" in cleaned_response:
                cleaned_response = cleaned_response.split("```")[1].split("```")[0].strip()
                
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            return {
                "score": 50,
                "red_flags": ["Unable to parse LLM response"],
                "analysis": response[:200]
            }
    
    def _get_recommendation(self, ghost_score: float) -> str:
        """Get recommendation based on ghost score"""
        if ghost_score < 40:
            return "Apply"
        elif ghost_score < 65:
            return "Caution"
        else:
            return "Skip"
    
    async def batch_detect(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect ghost jobs in batch
        
        Returns list of jobs with ghost_detection added
        """
        results = []
        
        for job in jobs:
            try:
                detection = await self.run({"job_posting": job})
                job["ghost_detection"] = detection
                results.append(job)
            except Exception as e:
                self.log(f"Failed to detect ghost job for {job.get('title', 'Unknown')}: {e}", level="warning")
                job["ghost_detection"] = {"error": str(e)}
                results.append(job)
        
        return results
