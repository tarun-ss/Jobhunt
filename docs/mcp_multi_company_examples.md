# MCP Server: Multi-Company Query Examples

## How the MCP Server Handles Thousands of Companies

The MCP server stores data for **ALL companies** in a centralized knowledge base. Here are real-world usage examples:

---

## Example 1: User Applies to 50 Jobs Across Different Companies

**Scenario**: User wants to apply to 50 software engineering jobs at various companies (Google, Meta, startups, etc.)

### Step 1: Job Scraper Finds Jobs
```python
# Job scrapers find 50 jobs from different companies
jobs = [
    {"company": "Google", "title": "Senior SWE", "id": "job_001"},
    {"company": "Meta", "title": "Backend Engineer", "id": "job_002"},
    {"company": "Stripe", "title": "Full Stack Engineer", "id": "job_003"},
    # ... 47 more jobs
]
```

### Step 2: Resume Optimizer Queries MCP for Each Company
```python
for job in jobs:
    # Query MCP server for THIS specific company
    company_data = mcp_client.read_resource(
        f"company://{job.company}/tech_stack"
    )
    
    # Optimize resume specifically for this company
    optimized_resume = resume_optimizer.optimize(
        base_resume=user.resume,
        job_description=job.description,
        company_tech_stack=company_data.tech_stack  # Google uses Python/Go, Meta uses Python/Hack
    )
    
    # Save optimized version
    save_resume(f"resume_for_{job.company}_{job.id}.pdf", optimized_resume)
```

**Result**: 50 different resume versions, each tailored to the specific company's tech stack and culture.

---

## Example 2: Batch Search Across All Companies

**Scenario**: User wants to find "AI startups in San Francisco with good work-life balance"

```python
# Search across ALL companies in the MCP server
results = mcp_client.call_tool(
    "search_companies",
    {
        "query": "AI startups in San Francisco",
        "filters": {
            "industry": "Artificial Intelligence",
            "location": "San Francisco",
            "size": "<500",
            "culture.work_life_balance": ">4.0"
        },
        "limit": 20
    }
)

# Returns 20 companies that match criteria
# [
#   {"company_id": "openai", "name": "OpenAI", "glassdoor_rating": 4.5, ...},
#   {"company_id": "anthropic", "name": "Anthropic", "glassdoor_rating": 4.7, ...},
#   {"company_id": "scale_ai", "name": "Scale AI", "glassdoor_rating": 4.2, ...},
#   ...
# ]
```

---

## Example 3: Ghost Job Detection Across Multiple Companies

**Scenario**: Job scraper finds 500 new jobs today from 200 different companies

```python
# Ghost job detector processes ALL jobs
for job in newly_scraped_jobs:  # 500 jobs
    # Get company's historical hiring patterns from MCP
    company_patterns = mcp_client.read_resource(
        f"company://{job.company}/hiring_patterns"
    )
    
    # Calculate ghost job score
    ghost_score = calculate_ghost_score(
        job_age=job.days_since_posted,
        repost_frequency=company_patterns.repost_frequency,
        company_ghost_rate=company_patterns.ghost_job_frequency,  # e.g., "Acme Corp posts 30% ghost jobs"
        response_rate=company_patterns.response_rate
    )
    
    # Flag suspicious jobs
    if ghost_score > 0.7:
        mark_as_ghost_job(job)
```

**Result**: Filters out ghost jobs from companies known for posting fake listings.

---

## Example 4: Email Personalization for 100 Applications

**Scenario**: User applies to 100 jobs at 100 different companies

```python
for application in user.applications:  # 100 applications
    # Get company-specific context from MCP
    company_culture = mcp_client.read_resource(
        f"company://{application.company}/culture"
    )
    company_news = mcp_client.read_resource(
        f"company://{application.company}/recent_news"
    )
    
    # Generate personalized email
    email = email_writer.generate(
        template="cold_email",
        company_name=application.company,
        company_values=company_culture.values,  # Different for each company
        recent_news=company_news.top_3,  # "Congrats on your Series B!"
        job_title=application.job_title,
        candidate_background=user.resume.summary
    )
    
    send_email(email)
```

**Result**: 100 unique, personalized emails referencing each company's specific culture and recent news.

---

## Example 5: Finding Similar Companies

**Scenario**: User got an interview at Google and wants to find similar companies

```python
# Find companies similar to Google
similar_companies = mcp_client.call_tool(
    "find_similar_companies",
    {
        "company": "Google",
        "criteria": ["tech_stack", "culture", "size"],
        "limit": 10
    }
)

# Returns:
# [
#   {"company": "Meta", "similarity_score": 0.92},
#   {"company": "Microsoft", "similarity_score": 0.89},
#   {"company": "Amazon", "similarity_score": 0.85},
#   {"company": "Databricks", "similarity_score": 0.78},
#   ...
# ]

# Now apply to these similar companies with high match probability
for company in similar_companies:
    jobs = find_jobs_at_company(company.company)
    apply_to_jobs(jobs)
```

---

## How Data is Organized in MCP Server

### Database Structure

```
MCP Server Database
├── companies/
│   ├── google/
│   │   ├── overview.json
│   │   ├── tech_stack.json
│   │   ├── culture.json
│   │   ├── hiring_patterns.json
│   │   └── jobs/
│   │       ├── job_001.json
│   │       ├── job_002.json
│   │       └── ...
│   ├── meta/
│   │   ├── overview.json
│   │   ├── tech_stack.json
│   │   └── ...
│   ├── stripe/
│   ├── openai/
│   ├── ... (10,000+ companies)
│
├── indexes/
│   ├── vector_index/  (for semantic search)
│   ├── tech_stack_index/  (for filtering by technologies)
│   └── location_index/  (for geographic search)
```

### Resource URIs

Every company has standardized URIs:

```
company://google/overview
company://google/tech_stack
company://google/culture
company://google/jobs
company://google/hiring_patterns

company://meta/overview
company://meta/tech_stack
...

company://stripe/overview
company://stripe/tech_stack
...
```

---

## Performance at Scale

### Caching Strategy
```python
# Frequently accessed companies (FAANG) are cached in Redis
cache_hit = redis.get("company:google:tech_stack")
if cache_hit:
    return cache_hit
else:
    data = database.query("SELECT * FROM companies WHERE id='google'")
    redis.set("company:google:tech_stack", data, ttl=3600)  # Cache for 1 hour
    return data
```

### Batch Operations
```python
# Instead of 50 individual queries, batch them
company_names = [job.company for job in jobs]  # ["Google", "Meta", "Stripe", ...]

# Single batch query
company_data = mcp_client.call_tool(
    "batch_get_companies",
    {
        "companies": company_names,
        "fields": ["tech_stack", "culture"]
    }
)

# Returns data for all 50 companies in one call
```

---

## Key Takeaway

**The MCP server is like a shared library**:
- One central database with 10,000+ companies
- All agents query it for different companies as needed
- Each user's job applications touch dozens/hundreds of companies
- Knowledge is shared across all users (if Company X is researched once, all users benefit)

It's **not** one MCP server per company. It's **one MCP server for ALL companies**.
