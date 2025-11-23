"""
ATS Scorer Service - Calculate match score between resume and job

Calculates ATS (Applicant Tracking System) score based on:
- Skills match (50% weight)
- Experience match (30% weight)  
- Education match (10% weight)
- Keyword density (10% weight)

Score range: 0-100
"""

from typing import Dict, List, Set


class ATSScorer:
    
    def calculate_ats_score(
        self,
        resume_data: Dict,
        job_requirements: Dict
    ) -> Dict:
        """
        Calculate comprehensive ATS match score
        
        Args:
            resume_data: Parsed resume data from resume_parser
            job_requirements: Analyzed job requirements from job_analyzer
            
        Returns:
            Dictionary with score breakdown and details
        """
        
        # Extract data
        resume_skills = set(skill.lower() for skill in resume_data.get("skills", []))
        resume_tech_skills = set(skill.lower() for skill in resume_data.get("technical_skills", []))
        resume_exp_years = resume_data.get("experience_years", 0)
        resume_education = set(edu.lower() for edu in resume_data.get("education", []))
        
        required_skills = set(skill.lower() for skill in job_requirements.get("required_skills", []))
        preferred_skills = set(skill.lower() for skill in job_requirements.get("preferred_skills", []))
        required_exp_years = job_requirements.get("experience_required_years", 0)
        required_education = set(edu.lower() for edu in job_requirements.get("education_required", []))
        keywords = set(kw.lower() for kw in job_requirements.get("keywords", []))
        
        # 1. Skills Match (50% weight)
        skills_score = self._calculate_skills_score(
            resume_skills,
            resume_tech_skills,
            required_skills,
            preferred_skills
        )
        
        # 2. Experience Match (30% weight)
        experience_score = self._calculate_experience_score(
            resume_exp_years,
            required_exp_years
        )
        
        # 3. Education Match (10% weight)
        education_score = self._calculate_education_score(
            resume_education,
            required_education
        )
        
        # 4. Keyword Density (10% weight)
        keyword_score = self._calculate_keyword_score(
            resume_skills,
            keywords
        )
        
        # Total score
        total_score = skills_score + experience_score + education_score + keyword_score
        
        # Find missing and matching skills
        matching_required = resume_skills.intersection(required_skills)
        missing_required = required_skills - resume_skills
        matching_preferred = resume_skills.intersection(preferred_skills)
        
        return {
            "ats_score": round(total_score, 1),
            "breakdown": {
                "skills_match": round(skills_score, 1),
                "experience_match": round(experience_score, 1),
                "education_match": round(education_score, 1),
                "keyword_density": round(keyword_score, 1)
            },
            "matching_skills": {
                "required": list(matching_required),
                "preferred": list(matching_preferred)
            },
            "missing_skills": {
                "required": list(missing_required),
                "preferred": list(preferred_skills - resume_skills)
            },
            "experience_gap": max(0, required_exp_years - resume_exp_years),
            "recommendations": self._generate_recommendations(
                missing_required,
                required_exp_years,
                resume_exp_years
            )
        }
    
    def _calculate_skills_score(
        self,
        resume_skills: Set[str],
        resume_tech_skills: Set[str],
        required_skills: Set[str],
        preferred_skills: Set[str]
    ) -> float:
        """Calculate skills match score (max 50 points)"""
        
        if not required_skills and not preferred_skills:
            return 0.0  # No requirements found (e.g. empty description) = 0 score
        
        # Required skills match (70% of skills score)
        if required_skills:
            required_match = len(resume_skills.intersection(required_skills)) / len(required_skills)
        else:
            required_match = 1.0
        
        # Preferred skills match (30% of skills score)
        if preferred_skills:
            preferred_match = len(resume_skills.intersection(preferred_skills)) / len(preferred_skills)
        else:
            preferred_match = 1.0
        
        # Combined score
        skills_score = (required_match * 0.7 + preferred_match * 0.3) * 50
        
        return skills_score
    
    def _calculate_experience_score(
        self,
        resume_years: int,
        required_years: int
    ) -> float:
        """Calculate experience match score (max 30 points)"""
        
        if required_years == 0:
            return 30.0  # No requirement = perfect score
        
        # Score decreases if under-experienced, caps at 100% if over-experienced
        experience_ratio = min(resume_years / required_years, 1.0)
        
        # Apply gentle penalty for being significantly under-experienced
        if experience_ratio < 0.5:
            experience_ratio *= 0.8  # 20% penalty
        
        return experience_ratio * 30
    
    def _calculate_education_score(
        self,
        resume_education: Set[str],
        required_education: Set[str]
    ) -> float:
        """Calculate education match score (max 10 points)"""
        
        if not required_education:
            return 10.0  # No requirement = perfect score
        
        # Check for any degree matches (bachelor's, master's, phd)
        degree_keywords = {
            "bachelor": ["bachelor", "bs", "ba", "bsc", "btech", "b.tech"],
            "master": ["master", "ms", "ma", "msc", "mtech", "m.tech", "mba"],
            "phd": ["phd", "ph.d", "doctorate"]
        }
        
        resume_level = None
        for level, keywords in degree_keywords.items():
            if any(kw in " ".join(resume_education) for kw in keywords):
                resume_level = level
                break
        
        required_level = None
        for level, keywords in degree_keywords.items():
            if any(kw in " ".join(required_education) for kw in keywords):
                required_level = level
                break
        
        if resume_level == required_level:
            return 10.0
        elif resume_level == "master" and required_level == "bachelor":
            return 10.0  # Higher degree satisfies lower requirement
        elif resume_level == "phd":
            return 10.0  # PhD satisfies any requirement
        elif resume_level:
            return 6.0  # Has some degree
        else:
            return 0.0  # No degree
    
    def _calculate_keyword_score(
        self,
        resume_skills: Set[str],
        keywords: Set[str]
    ) -> float:
        """Calculate keyword density score (max 10 points)"""
        
        if not keywords:
            return 10.0  # No keywords = perfect score
        
        keyword_match = len(resume_skills.intersection(keywords)) / len(keywords)
        return keyword_match * 10
    
    def _generate_recommendations(
        self,
        missing_skills: Set[str],
        required_years: int,
        resume_years: int
    ) -> List[str]:
        """Generate recommendations to improve ATS score"""
        
        recommendations = []
        
        if missing_skills:
            top_missing = list(missing_skills)[:3]
            recommendations.append(
                f"Add these key skills to your resume: {', '.join(top_missing)}"
            )
        
        if resume_years < required_years:
            gap = required_years - resume_years
            recommendations.append(
                f"Emphasize relevant experience (need {gap} more years)"
            )
        
        if not recommendations:
            recommendations.append("Great match! Consider tailoring resume to this specific role.")
        
        return recommendations


# Singleton instance
ats_scorer = ATSScorer()


def calculate_score(resume_data: Dict, job_requirements: Dict) -> Dict:
    """Convenience function to calculate ATS score"""
    return ats_scorer.calculate_ats_score(resume_data, job_requirements)
