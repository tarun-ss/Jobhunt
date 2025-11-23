# MCP Server: Universal Company Knowledge Base

## Overview

Instead of building a traditional database, we'll create an **MCP (Model Context Protocol) server** that acts as a universal, queryable knowledge base for company information - similar to how [Supermemory](https://github.com/supermemoryai/supermemory) works for personal knowledge.

## Why MCP Server?

### Benefits
1. **Standardized Interface**: Any LLM agent can query company data using MCP protocol
2. **Persistent Memory**: Companies researched once are available to all future users
3. **Semantic Search**: Vector-based retrieval of relevant company info
4. **Incremental Learning**: Knowledge base grows over time as agents research more companies
5. **Multi-Agent Access**: All agents (resume optimizer, email writer, etc.) can access the same company context

### Comparison to Traditional DB
| Traditional DB | MCP Server |
|---|---|
| SQL queries | Natural language queries |
| Fixed schema | Flexible, unstructured data |
| Agent needs DB knowledge | Agent just asks questions |
| Siloed data | Shared knowledge graph |

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    MCP Server                            │
│  (Universal Company Knowledge Base)                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Vector DB  │  │  Graph DB    │  │  Document    │  │
│  │  (Embeddings)│  │ (Relations)  │  │   Store      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
│  Resources:                                              │
│  - company://{company_name}/overview                     │
│  - company://{company_name}/tech_stack                   │
│  - company://{company_name}/culture                      │
│  - company://{company_name}/jobs                         │
│  - company://{company_name}/interview_process            │
│                                                          │
│  Tools:                                                  │
│  - search_companies(query)                               │
│  - get_company_info(name, aspect)                        │
│  - add_company_data(name, data)                          │
│  - find_similar_companies(name)                          │
└─────────────────────────────────────────────────────────┘
                          ▲
                          │ MCP Protocol
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   ┌────▼────┐      ┌────▼────┐      ┌────▼────┐
   │ Resume  │      │  Email  │      │  Ghost  │
   │Optimizer│      │ Writer  │      │  Job    │
   │ Agent   │      │ Agent   │      │Detector │
   └─────────┘      └─────────┘      └─────────┘
```

## Data Model

### Multi-Company Storage

The MCP server is a **centralized knowledge base** that stores information about **thousands of companies**. Think of it like a Wikipedia for company hiring data.

**Scale Example:**
- 10,000+ companies (Google, Microsoft, startups, etc.)
- 100,000+ job postings across all companies
- Shared by all users of the platform

### Company Knowledge Graph

Each company in the MCP server contains:

```json
{
  "company_id": "google",  // Unique identifier
  "basic_info": {
    "name": "Google LLC",
    "industry": "Technology",
    "size": "100,000+",
    "founded": "1998",
    "headquarters": "Mountain View, CA"
  },
  "tech_stack": {
    "languages": ["Python", "Java", "Go", "C++"],
    "frameworks": ["TensorFlow", "Angular", "Kubernetes"],
    "tools": ["Bazel", "Bigtable", "Spanner"],
    "confidence": 0.95
  },
  "culture": {
    "values": ["Innovation", "Collaboration", "Impact"],
    "work_style": "Hybrid",
    "glassdoor_rating": 4.3,
    "employee_sentiment": "Generally positive, some concerns about bureaucracy",
    "interview_difficulty": "Hard"
  },
  "hiring_patterns": {
    "ghost_job_frequency": 0.12,
    "avg_time_to_hire": "45 days",
    "response_rate": 0.68,
    "common_roles": ["Software Engineer", "Product Manager", "Data Scientist"]
  },
  "job_postings": [
    {
      "job_id": "google_swe_2024_001",
      "title": "Senior Software Engineer",
      "posted_date": "2024-11-15",
      "is_ghost_job": false,
      "ghost_score": 0.08
    }
  ],
  "metadata": {
    "last_updated": "2024-11-22",
    "data_sources": ["LinkedIn", "Glassdoor", "Company Website", "Crunchbase"],
    "completeness_score": 0.87
  }
}
```

## MCP Server Implementation

### Resources (Read-Only Data)

Agents can read company data via URIs:

```python
# Get company overview
resource = await mcp_client.read_resource("company://google/overview")

# Get tech stack
tech_stack = await mcp_client.read_resource("company://google/tech_stack")

# Get all jobs from a company
jobs = await mcp_client.read_resource("company://google/jobs")
```

### Tools (Actions)

Agents can perform actions:

```python
# Search for companies by criteria
results = await mcp_client.call_tool(
    "search_companies",
    {
        "query": "AI startups in San Francisco with <100 employees",
        "limit": 10
    }
)

# Add new company data (from research agent)
await mcp_client.call_tool(
    "add_company_data",
    {
        "company": "OpenAI",
        "aspect": "tech_stack",
        "data": {
            "languages": ["Python", "Rust"],
            "frameworks": ["PyTorch", "Triton"]
        },
        "source": "job_description_analysis"
    }
)

# Find similar companies (for job recommendations)
similar = await mcp_client.call_tool(
    "find_similar_companies",
    {
        "company": "Google",
        "criteria": ["tech_stack", "culture"],
        "limit": 5
    }
)
```

## Integration with Agents

### Example: Resume Optimizer Agent

```python
class ResumeOptimizerAgent(BaseAgent):
    def optimize_for_job(self, resume, job_posting):
        # Get company context from MCP server
        company_info = self.mcp_client.read_resource(
            f"company://{job_posting.company}/tech_stack"
        )
        
        # Use company tech stack to prioritize skills
        relevant_skills = self.match_skills(
            resume.skills,
            company_info.tech_stack.languages
        )
        
        # Optimize resume with company-specific context
        optimized = self.llm.generate(
            prompt=f"""
            Optimize this resume for {job_posting.company}.
            Their tech stack: {company_info.tech_stack}
            Job requirements: {job_posting.description}
            Candidate skills: {resume.skills}
            """
        )
        
        return optimized
```

### Example: Email Writer Agent

```python
class EmailWriterAgent(BaseAgent):
    def write_cold_email(self, job_posting, resume):
        # Get company culture from MCP server
        culture = self.mcp_client.read_resource(
            f"company://{job_posting.company}/culture"
        )
        
        # Personalize email based on company values
        email = self.llm.generate(
            prompt=f"""
            Write a cold email for this job.
            Company values: {culture.values}
            Company culture: {culture.work_style}
            Candidate background: {resume.summary}
            Tone: Match their culture ({culture.employee_sentiment})
            """
        )
        
        return email
```

## Data Collection Strategy

### Initial Population
1. **Seed from Job Postings**: Extract company info from scraped jobs
2. **Public APIs**: Crunchbase, Clearbit, LinkedIn Company API
3. **Web Scraping**: Company websites, Glassdoor, BuiltWith

### Continuous Learning
1. **User Feedback**: When users get interviews/offers, mark company data as validated
2. **Agent Research**: Company research agents continuously update the knowledge base
3. **Crowdsourced**: Multiple users' applications contribute to ghost job detection

### Data Quality
- **Confidence Scores**: Each data point has a confidence score
- **Source Tracking**: Know where each piece of information came from
- **Staleness Detection**: Flag outdated information (e.g., tech stack from 2020)
- **Conflict Resolution**: When sources disagree, use voting or recency

## Privacy & Ethics

### What We Store
- ✅ Public company information (tech stack, culture, job postings)
- ✅ Aggregated hiring patterns (response rates, time-to-hire)
- ❌ Individual recruiter names/emails (unless publicly listed)
- ❌ User's personal application data (stored separately, not in MCP server)

### Data Retention
- Company data: Indefinite (public information)
- Job postings: 90 days after closing
- Ghost job scores: Anonymized and aggregated

## Technical Stack

### Recommended Implementation
```
MCP Server Framework: Python with FastMCP or TypeScript with @modelcontextprotocol/sdk
Vector DB: Chroma or Qdrant (for semantic search)
Graph DB: Neo4j (for company relationships)
Document Store: PostgreSQL with JSONB (for structured data)
Caching: Redis (for frequently accessed companies)
```

### Deployment
- **Local Development**: SQLite + in-memory vector store
- **Production**: Hosted MCP server (Railway, Render, or self-hosted)
- **Scaling**: Horizontal scaling with load balancer for multiple users

## Next Steps

1. Define MCP server schema and resources
2. Implement basic company CRUD operations
3. Build company research agent to populate initial data
4. Create MCP client wrapper for other agents
5. Test with 100 companies to validate data model
