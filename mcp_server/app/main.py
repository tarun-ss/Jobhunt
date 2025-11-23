# mcp_server/app/main.py
"""FastAPI entry point for the MCP (Multi‑Company Knowledge) server.

Now connected to cloud databases:
- Supabase (PostgreSQL)
- Qdrant Cloud (Vector DB)
- Neo4j Aura (Graph DB)
- Upstash (Redis)
"""

from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database manager
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from storage.db_manager import db_manager, get_postgres_session, get_redis_client
from services.news_service import get_latest_news

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("\n" + "=" * 60)
    print("Starting JobHunter AI MCP Server")
    print("=" * 60)
    
    # Connect to cloud databases
    success = db_manager.connect_all()
    if not success:
        print("\n[WARNING] Some database connections failed")
        print("Check CLOUD_SETUP.md for setup instructions")
    
    yield
    
    # Shutdown
    print("\nShutting down...")
    db_manager.close_all()

app = FastAPI(
    title="JobHunter AI MCP Server",
    version="0.2.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ResumeUpload(BaseModel):
    resume_id: str
    content: str

class JobPosting(BaseModel):
    title: str
    company: str
    location: str
    description: str
    url: str
    ghost_score: Optional[float] = None

class Company(BaseModel):
    company_id: str
    name: str
    industry: Optional[str] = None
    size: Optional[str] = None

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "databases": {
            "postgres": db_manager.postgres_engine is not None,
            "qdrant": db_manager.qdrant_client is not None,
            "neo4j": db_manager.neo4j_driver is not None,
            "redis": db_manager.redis_client is not None
        }
    }

@app.get("/news/latest")
async def news_latest():
    """Return latest tech news"""
    try:
        news = get_latest_news()
        return {"news": news}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Resume endpoints
@app.post("/resumes")
async def upload_resume(resume: ResumeUpload):
    """Upload a resume"""
    try:
        from sqlalchemy import text
        session = get_postgres_session()
        
        # Check if resume exists
        result = session.execute(
            text("SELECT resume_id FROM resumes WHERE resume_id = :id"),
            {"id": resume.resume_id}
        )
        if result.fetchone():
            raise HTTPException(status_code=400, detail="Resume ID already exists")
        
        # Insert resume
        session.execute(
            text("""
            INSERT INTO resumes (resume_id, content, created_at)
            VALUES (:id, :content, NOW())
            """),
            {"id": resume.resume_id, "content": resume.content}
        )
        session.commit()
        session.close()
        
        # Cache in Redis (optional)
        try:
            if db_manager.redis_client:
                redis_client = get_redis_client()
                redis_client.setex(
                    f"resume:{resume.resume_id}",
                    3600,  # 1 hour TTL
                    resume.content
                )
        except:
            pass  # Redis is optional
        
        return {"message": "Resume stored", "resume_id": resume.resume_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/resumes/upload")
async def upload_resume_file(file: UploadFile = File(...)):
    """Upload a resume file (PDF, DOCX, or TXT)"""
    try:
        # Import document parser
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from utils.document_parser import extract_text_from_file
        from sqlalchemy import text
        
        # Read file content
        file_content = await file.read()
        
        # Extract text from file
        try:
            text_content = extract_text_from_file(file.filename, file_content)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Generate resume ID using timestamp and file size
        import time
        resume_id = f"resume-{int(time.time())}-{len(file_content)}"
        
        # Store in database
        session = get_postgres_session()
        
        # Check if resume exists
        result = session.execute(
            text("SELECT resume_id FROM resumes WHERE resume_id = :id"),
            {"id": resume_id}
        )
        if result.fetchone():
            resume_id = f"{resume_id}-{hash(text_content) % 10000}"
        
        # Insert resume
        session.execute(
            text("""
            INSERT INTO resumes (resume_id, content, created_at)
            VALUES (:id, :content, NOW())
            """),
            {"id": resume_id, "content": text_content}
        )
        session.commit()
        session.close()
        
        # Cache in Redis (optional)
        try:
            if db_manager.redis_client:
                redis_client = get_redis_client()
                redis_client.setex(
                    f"resume:{resume_id}",
                    3600,  # 1 hour TTL
                    text_content
                )
        except:
            pass  # Redis is optional
        
        return {
            "message": "Resume uploaded successfully",
            "resume_id": resume_id,
            "filename": file.filename
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@app.get("/resumes/{resume_id}")
async def get_resume(resume_id: str):
    """Get a resume by ID"""
    try:
        # Try Redis cache first (if available)
        session = get_postgres_session()
        result = session.execute(
            text("SELECT content FROM resumes WHERE resume_id = :id"),
            {" id": resume_id}
        )
        row = result.fetchone()
        session.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        return {"resume_id": resume_id, "content": row[0]}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ATS & Resume Analysis endpoints
@app.post("/resumes/analyze")
async def analyze_resume(resume_id: str):
    """Analyze resume to extract skills, experience, education"""
    try:
        from sqlalchemy import text
        from services.resume_parser import parse_resume
        
        # Get resume content
        session = get_postgres_session()
        result = session.execute(
            text("SELECT content FROM resumes WHERE resume_id = :id"),
            {"id": resume_id}
        )
        row = result.fetchone()
        session.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Parse resume using Groq AI
        resume_text = row[0]
        parsed_data = parse_resume(resume_text)
        
        return {
            "resume_id": resume_id,
            "parsed_data": parsed_data,
            "message": "Resume analyzed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/jobs/{job_id}/ats-score")
async def calculate_ats_score_endpoint(job_id: str, resume_id: str):
    """Calculate ATS match score for a specific job"""
    try:
        from sqlalchemy import text
        from services.resume_parser import parse_resume
        from services.job_analyzer import analyze_job_description
        from services.ats_scorer import calculate_score
        
        session = get_postgres_session()
        
        # Get resume
        result = session.execute(
            text("SELECT content FROM resumes WHERE resume_id = :id"),
            {"id": resume_id}
        )
        resume_row = result.fetchone()
        if not resume_row:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Get job
        result = session.execute(
            text("SELECT title, description FROM job_postings WHERE job_id = :id"),
            {"id": job_id}
        )
        job_row = result.fetchone()
        if not job_row:
            raise HTTPException(status_code=404, detail="Job not found")
        
        session.close()
        
        # Parse resume and analyze job
        resume_data = parse_resume(resume_row[0])
        job_requirements = analyze_job_description(job_row[1], job_row[0])
        
        # Calculate ATS score
        score_result = calculate_score(resume_data, job_requirements)
        
        return score_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ATS scoring failed: {str(e)}")

@app.post("/jobs/{job_id}/tailor-resume")
async def tailor_resume_endpoint(job_id: str, resume_id: str):
    """Generate a tailored resume for a specific job"""
    try:
        from sqlalchemy import text
        from services.resume_tailor import generate_tailored_resume
        from services.ats_scorer import calculate_score
        from services.resume_parser import parse_resume
        from services.job_analyzer import analyze_job_description
        import time
        
        session = get_postgres_session()
        
        # Get resume
        result = session.execute(
            text("SELECT content FROM resumes WHERE resume_id = :id"),
            {"id": resume_id}
        )
        resume_row = result.fetchone()
        if not resume_row:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Get job
        result = session.execute(
            text("SELECT title, description, company_id FROM job_postings WHERE job_id = :id"),
            {"id": job_id}
        )
        job_row = result.fetchone()
        if not job_row:
            raise HTTPException(status_code=404, detail="Job not found")
            
        # Get company name
        company_result = session.execute(
            text("SELECT name FROM companies WHERE company_id = :id"),
            {"id": job_row[2]}
        )
        company_row = company_result.fetchone()
        company_name = company_row[0] if company_row else "Unknown Company"
        
        session.close()
        
        base_resume = resume_row[0]
        job_title = job_row[0]
        job_desc = job_row[1]
        
        # Generate tailored resume
        tailored_result = generate_tailored_resume(
            base_resume,
            job_desc,
            job_title,
            company_name
        )
        
        # Calculate new ATS score
        new_resume_data = parse_resume(tailored_result["tailored_content"])
        job_requirements = analyze_job_description(job_desc, job_title)
        new_score = calculate_score(new_resume_data, job_requirements)
        
        # Store tailored resume in database
        tailored_id = f"tailored-{job_id}-{int(time.time())}"
        
        session = get_postgres_session()
        session.execute(
            text("""
            INSERT INTO resumes (resume_id, content, created_at)
            VALUES (:id, :content, NOW())
            ON CONFLICT (resume_id) DO UPDATE SET content = :content
            """),
            {
                "id": tailored_id,
                "content": tailored_result["tailored_content"]
            }
        )
        session.commit()
        session.close()
        
        return {
            "tailored_resume_id": tailored_id,
            "tailored_content": tailored_result["tailored_content"],
            "changes_made": tailored_result["changes_made"],
            "new_ats_score": new_score["ats_score"],
            "message": "Resume tailored successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume tailoring failed: {str(e)}")

@app.get("/resumes/{resume_id}/download")
async def download_resume(resume_id: str):
    """Download resume as DOCX"""
    try:
        from sqlalchemy import text
        from fastapi.responses import StreamingResponse
        from utils.markdown_to_docx import markdown_to_docx
        
        session = get_postgres_session()
        result = session.execute(
            text("SELECT content FROM resumes WHERE resume_id = :id"),
            {"id": resume_id}
        )
        row = result.fetchone()
        session.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Resume not found")
            
        resume_content = row[0]
        
        # Convert to DOCX
        docx_stream = markdown_to_docx(resume_content)
        
        return StreamingResponse(
            docx_stream,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename=Resume_{resume_id}.docx"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")
@app.post("/jobs")
async def add_job(job: JobPosting):
    """Add a job posting"""
    try:
        from sqlalchemy import text
        session = get_postgres_session()
        
        # Generate job ID
        job_id = f"job_{job.company.lower().replace(' ', '_')}_{hash(job.title) % 10000}"
        
        # Insert job
        session.execute(
            text("""
            INSERT INTO job_postings 
            (job_id, company_id, title, description, location, url, ghost_score, posted_date)
            VALUES (:id, :company, :title, :desc, :location, :url, :ghost_score, CURRENT_DATE)
            ON CONFLICT (job_id) DO NOTHING
            """),
            {
                "id": job_id,
                "company": job.company.lower().replace(' ', '_'),
                "title": job.title,
                "desc": job.description,
                "location": job.location,
                "url": job.url,
                "ghost_score": job.ghost_score or 0.0
            }
        )
        session.commit()
        session.close()
        
        return {"message": "Job added", "job_id": job_id, "title": job.title}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/jobs/scrape")
async def scrape_jobs_endpoint(
    search_term: str,
    location: str = "United States",
    results_wanted: int = 20
):
    """
    Scrape real jobs from LinkedIn, Indeed, Glassdoor using JobSpy
    """
    try:
        from sqlalchemy import text
        from services.job_scraper import scrape_real_jobs, enrich_jobs_with_ghost_scores
        import time
        
        # Scrape jobs
        jobs = scrape_real_jobs(search_term, location, results_wanted)
        
        if not jobs:
            return {"message": "No jobs found", "count": 0}
        
        # Add ghost job scores
        jobs = enrich_jobs_with_ghost_scores(jobs)
        
        # Store in database
        session = get_postgres_session()
        stored_count = 0
        
        for job in jobs:
            # Generate unique job ID
            job_id = f"job-{job['company'].lower().replace(' ', '-')}-{int(time.time())}-{hash(job['title']) % 10000}"
            
            # Convert date_posted to proper format
            posted_date = job.get('date_posted')
            if posted_date:
                try:
                    from datetime import datetime
                    if isinstance(posted_date, str):
                        posted_date = datetime.fromisoformat(posted_date.replace('Z', '+00:00')).date()
                except:
                    posted_date = None
            
            # Generate company_id from company name
            company_id = job['company'].lower().replace(' ', '_').replace('.', '')[:50]
            
            try:
                # First, ensure the company exists (insert if not exists)
                session.execute(
                    text("""
                    INSERT INTO companies (company_id, name)
                    VALUES (:company_id, :name)
                    ON CONFLICT (company_id) DO NOTHING
                    """),
                    {
                        "company_id": company_id,
                        "name": job['company'][:100]
                    }
                )
                
                # Now insert the job posting
                session.execute(
                    text("""
                    INSERT INTO job_postings 
                    (job_id, company_id, title, description, location, url, ghost_score, 
                     is_ghost_job, posted_date, remote_type, salary_min, salary_max)
                    VALUES (:id, :company, :title, :desc, :location, :url, :ghost_score,
                            :is_ghost, :posted_date, :remote_type, :salary_min, :salary_max)
                    ON CONFLICT (job_id) DO NOTHING
                    """),
                    {
                        "id": job_id,
                        "company": company_id,
                        "title": job['title'],
                        "desc": job['description'],
                        "location": job['location'],
                        "url": job['url'],
                        "ghost_score": job['ghost_score'] / 100.0,  # Convert to 0-1 scale
                        "is_ghost": job['is_ghost_job'],
                        "posted_date": posted_date,
                        "remote_type": "Remote" if job.get('is_remote') else "On-site",
                        "salary_min": job.get('salary_min'),
                        "salary_max": job.get('salary_max')
                    }
                )
                stored_count += 1
                
                # Add ID to job object so it's returned to frontend
                job['id'] = job_id
                
            except Exception as e:
                print(f"Error storing job: {e}")
                session.rollback()  # Rollback failed transaction
                continue
        
        session.commit()
        session.close()
        
        return {
            "message": f"Scraped and stored {stored_count} jobs",
            "search_term": search_term,
            "location": location,
            "total_found": len(jobs),
            "stored": stored_count,
            "jobs": jobs
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.get("/jobs")
async def list_jobs(skip: int = 0, limit: int = 20):
    """List all jobs"""
    try:
        from sqlalchemy import text
        session = get_postgres_session()
        
        result = session.execute(
            text("""
            SELECT job_id, title, company_id, location, description, url, ghost_score
            FROM job_postings
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :skip
            """),
            {"limit": limit, "skip": skip}
        )
        
        jobs = []
        for row in result:
            jobs.append({
                "id": row[0],
                "title": row[1],
                "company": row[2],
                "location": row[3],
                "description": row[4],
                "url": row[5],
                "ghost_score": float(row[6]) if row[6] else 0.0
            })
        
        session.close()
        return jobs
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Company endpoints
@app.get("/companies")
async def list_companies(limit: int = 10):
    """List companies"""
    try:
        from sqlalchemy import text
        session = get_postgres_session()
        
        result = session.execute(
            text("""
            SELECT company_id, name, industry, size, headquarters
            FROM companies
            LIMIT :limit
            """),
            {"limit": limit}
        )
        
        companies = []
        for row in result:
            companies.append({
                "company_id": row[0],
                "name": row[1],
                "industry": row[2],
                "size": row[3],
                "headquarters": row[4]
            })
        
        session.close()
        return companies
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/companies/{company_id}/tech-stack")
async def get_company_tech_stack(company_id: str):
    """Get company tech stack"""
    try:
        from sqlalchemy import text
        session = get_postgres_session()
        
        result = session.execute(
            text("""
            SELECT languages, frameworks, tools, confidence
            FROM tech_stacks
            WHERE company_id = :id
            ORDER BY updated_at DESC
            LIMIT 1
            """),
            {"id": company_id}
        )
        
        row = result.fetchone()
        session.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Tech stack not found")
        
        return {
            "company_id": company_id,
            "languages": row[0],
            "frameworks": row[1],
            "tools": row[2],
            "confidence": float(row[3]) if row[3] else 0.0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Stats endpoint
@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    try:
        from sqlalchemy import text
        session = get_postgres_session()
        
        # Count jobs
        result = session.execute(text("SELECT COUNT(*) FROM job_postings"))
        job_count = result.fetchone()[0]
        
        # Count companies
        result = session.execute(text("SELECT COUNT(*) FROM companies"))
        company_count = result.fetchone()[0]
        
        # Count resumes
        result = session.execute(text("SELECT COUNT(*) FROM resumes"))
        resume_count = result.fetchone()[0]
        
        session.close()
        
        return {
            "jobs": job_count,
            "companies": company_count,
            "resumes": resume_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

