"""
Job Scraper Service using JobSpy
Fetches real job postings from LinkedIn, Indeed, Glassdoor, ZipRecruiter
"""
from jobspy import scrape_jobs
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional

def scrape_real_jobs(
    search_term: str,
    location: str = "United States",
    results_wanted: int = 20,
    site_name: List[str] = None
) -> List[Dict]:
    """
    Scrape jobs from multiple job boards using JobSpy
    
    Args:
        search_term: Job title or keyword to search
        location: Location to search jobs in
        results_wanted: Number of jobs to fetch (default 20)
        site_name: List of job boards to scrape from ['indeed', 'linkedin', 'glassdoor', 'zip_recruiter']
    
    Returns:
        List of job dictionaries
    """
    
    if site_name is None:
        site_name = ['indeed', 'linkedin', 'glassdoor']
    
    
    try:
        print(f"[JobSpy] Scraping jobs for: {search_term} in {location}")
        print(f"[JobSpy] Sites: {site_name}, Results wanted: {results_wanted}")
        
        # Scrape jobs using JobSpy
        jobs_df = scrape_jobs(
            site_name=site_name,
            search_term=search_term,
            location=location,
            results_wanted=results_wanted,
            hours_old=720,  # Jobs from last 30 days
            country_indeed='USA',
            distance=50,  # 50 miles radius
            linkedin_fetch_description=True,  # Enable to get full descriptions
        )
        
        print(f"[JobSpy] Scraping complete. DataFrame shape: {jobs_df.shape if jobs_df is not None else 'None'}")
        
        if jobs_df is None or jobs_df.empty:
            print("[JobSpy] No jobs found - DataFrame is empty")
            return []
        
        # Convert DataFrame to list of dicts
        jobs_list = []
        failed_count = 0
        
        for idx, row in jobs_df.iterrows():
            try:
                # Calculate days ago from date_posted
                days_ago = 0
                if pd.notna(row.get('date_posted')):
                    try:
                        posted_date = pd.to_datetime(row['date_posted'])
                        days_ago = (datetime.now() - posted_date).days
                    except:
                        pass
                
                # Safely convert all fields to strings if they're NaN/float
                def safe_get(field, default=''):
                    val = row.get(field)
                    if pd.isna(val):
                        return default
                    return str(val) if not isinstance(val, (str, int, float, bool, type(None))) else val
                
                job = {
                    'title': safe_get('title', 'N/A'),
                    'company': safe_get('company', 'N/A'),
                    'location': safe_get('location', location),
                    'description': safe_get('description', 'No description available'),
                    'url': safe_get('job_url', '#'),
                    'date_posted': row.get('date_posted') if pd.notna(row.get('date_posted')) else None,
                    'days_ago': days_ago,
                    'job_type': safe_get('job_type', 'fulltime'),
                    'salary_min': row.get('min_amount') if pd.notna(row.get('min_amount')) else None,
                    'salary_max': row.get('max_amount') if pd.notna(row.get('max_amount')) else None,
                    'salary_interval': safe_get('interval', 'yearly'),
                    'site': safe_get('site', 'unknown'),
                    'is_remote': bool(row.get('is_remote', False)),
                    'company_url': safe_get('company_url', ''),
                }
                jobs_list.append(job)
                
            except Exception as e:
                failed_count += 1
                print(f"[JobSpy] Failed to process job {idx}: {type(e).__name__}: {e}")
                continue
        
        print(f"[JobSpy] Processed {len(jobs_list)} jobs successfully, {failed_count} failed")
        return jobs_list
        
    except Exception as e:
        print(f"[JobSpy] Error scraping jobs: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return []

def calculate_ghost_score(job: Dict) -> float:
    """
    Calculate ghost job probability score (0-100%)
    
    Factors:
    - Age of posting (older = more suspicious)
    - Description quality
    - Salary information
    """
    score = 0.0
    
    # Age factor (40% weight)
    days_ago = job.get('days_ago', 0)
    if days_ago > 60:
        score += 40
    elif days_ago > 30:
        score += 25
    elif days_ago > 14:
        score += 10
    
    # Description quality (30% weight)
    description = job.get('description') or ''
    # Ensure description is a string (handle NaN floats)
    if not isinstance(description, str):
        description = str(description)
    if len(description) < 100:
        score += 20  # Too short/vague
    if 'competitive salary' in description.lower() or 'commensurate with experience' in description.lower():
        score += 10  # Vague salary language
    
    # Salary transparency (20% weight)
    if not job.get('salary_min') and not job.get('salary_max'):
        score += 15  # No salary posted
    
    # Remote job factor (10% weight)
    if job.get('is_remote'):
        score += 5  # Remote jobs have slightly higher ghost rate
    
    return min(score, 100.0)  # Cap at 100%


def enrich_jobs_with_ghost_scores(jobs: List[Dict]) -> List[Dict]:
    """Add ghost job scores to each job"""
    for job in jobs:
        job['ghost_score'] = calculate_ghost_score(job)
        job['is_ghost_job'] = job['ghost_score'] > 50
    return jobs
