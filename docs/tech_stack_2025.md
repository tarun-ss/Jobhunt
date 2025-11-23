# Latest Tech Stack Updates (2024-2025)

Based on the latest research, here are cutting-edge technologies and approaches we should incorporate into JobHunter AI:

---

## 🚀 MCP (Model Context Protocol) - Latest Features

### What's New in 2025

**MCP was just released by Anthropic in November 2024** and is rapidly evolving. Major updates:

#### June 2025 Release (Production-Ready)
- ✅ **OAuth 2.1 Authentication**: Secure remote MCP servers with industry-standard auth
- ✅ **Structured Tool Outputs**: Better handling of complex data from tools
- ✅ **Elicitation (User-in-the-Loop)**: Servers can pause and ask users for input mid-operation
- ✅ **Resource Indicators (RFC 8707)**: Prevent token misuse across servers

#### November 2025 Release (Upcoming - Nov 25, 2025)
- 🔄 **Asynchronous Operations**: Long-running tasks (hours/days) without blocking
- 🔄 **Server Identity via `.well-known` URLs**: Auto-discovery of MCP servers
- 🔄 **MCP Registry (General Availability)**: Centralized discovery service for MCP servers
- 🔄 **Multi-Agent Systems Support**: Standardized agent graphs, namespace isolation, handoff patterns

### Why This Matters for JobHunter AI

1. **Async Operations**: Perfect for long-running job scraping (scrape 1000 jobs overnight)
2. **OAuth Security**: Enterprise-ready authentication for company data
3. **MCP Registry**: We can publish our company knowledge base for others to use
4. **Multi-Agent Standardization**: Built-in support for our agent orchestration

### Recommended MCP Stack
```python
# Use the latest MCP SDK
from mcp import Server, Resource, Tool
from mcp.server.fastmcp import FastMCP  # Fastest Python implementation

# Our MCP server will support:
# - Resources: company://{name}/overview, company://{name}/tech_stack
# - Tools: search_companies(), add_company_data()
# - Async: Long-running company research tasks
# - OAuth: Secure multi-user access
```

---

## 🕸️ LangGraph - Multi-Agent Best Practices (2024)

### Key Patterns for Our System

#### 1. **Supervisor-Worker Pattern** (Recommended)
```python
from langgraph.graph import StateGraph

# Planner agent delegates to specialized agents
graph = StateGraph()
graph.add_node("supervisor", supervisor_agent)  # Coordinates workflow
graph.add_node("job_scraper", job_scraper_agent)
graph.add_node("resume_optimizer", resume_optimizer_agent)
graph.add_node("email_writer", email_writer_agent)

# Supervisor decides which agent to call next
graph.add_conditional_edges("supervisor", route_to_agent)
```

#### 2. **Reflection Loops** (For Quality Control)
```python
# Resume optimizer critiques its own output
graph.add_node("optimize_resume", resume_optimizer)
graph.add_node("critique_resume", resume_critic)
graph.add_edge("optimize_resume", "critique_resume")
graph.add_conditional_edges(
    "critique_resume",
    lambda x: "optimize_resume" if x.score < 80 else "done"
)
```

#### 3. **Memory-Driven Context**
- **Short-term**: Conversation history within a job search session (LangGraph checkpointing)
- **Long-term**: Cross-session data stored in MCP server (company knowledge)

#### 4. **Streaming & Observability**
```python
# Stream events to user in real-time
for event in graph.stream(inputs, stream_mode="updates"):
    print(f"Agent: {event['node']}, Action: {event['action']}")
```

### LangGraph Features We'll Use
- ✅ **Stateful Graphs**: Maintain job search context across multiple steps
- ✅ **Cyclical Flows**: Resume optimization loop (optimize → score → re-optimize)
- ✅ **Conditional Routing**: LLM decides next agent based on context
- ✅ **Checkpointing**: Save/resume job search sessions

---

## 📄 ATS Resume Optimization - 2024 State-of-the-Art

### Top Tools & Techniques

#### Leading ATS Optimization Tools (2024)
1. **Jobscan** - Keyword matching + ATS simulation
2. **Teal** - AI resume builder with instant job matching
3. **Rezi** - AI Keyword Targeting + "Rezi Score" (23 metrics)
4. **SkillSyncer** - Free ATS scanner with auto-optimization

### What We'll Build (Better Than Existing Tools)

#### Our Competitive Advantages
1. **Multi-Company Optimization**: Existing tools optimize for ONE job at a time. We optimize for 50+ jobs simultaneously.
2. **MCP-Powered Context**: Use company tech stack from MCP server (not just job description)
3. **Version Control**: Track all resume versions with diffs
4. **Success Feedback Loop**: Learn which resume tweaks lead to interviews

#### ATS Scoring Algorithm
```python
def calculate_ats_score(resume, job_description, company_data):
    score = 0
    
    # 1. Keyword Matching (40 points)
    job_keywords = extract_keywords(job_description)
    resume_keywords = extract_keywords(resume)
    keyword_match_rate = len(set(job_keywords) & set(resume_keywords)) / len(job_keywords)
    score += keyword_match_rate * 40
    
    # 2. Tech Stack Alignment (30 points) - UNIQUE TO US
    company_tech_stack = mcp_client.read_resource(f"company://{company}/tech_stack")
    tech_match_rate = match_skills(resume.skills, company_tech_stack.languages)
    score += tech_match_rate * 30
    
    # 3. Format Quality (20 points)
    score += check_ats_friendly_format(resume) * 20
    
    # 4. Experience Relevance (10 points)
    score += calculate_experience_relevance(resume, job_description) * 10
    
    return score  # 0-100
```

---

## 👻 Ghost Job Detection - ML Techniques (2024)

### State-of-the-Art Approaches

#### Best-Performing Algorithms
1. **Random Forest** - Highest accuracy (85-92%) in research papers
2. **XGBoost** - Fast, handles imbalanced datasets well
3. **Multi-Layer Perceptron (MLP)** - Captures complex patterns

### Our Ghost Job Detection Model

#### Features to Extract
```python
features = {
    # Text-based (NLP)
    "description_length": len(job.description),
    "has_salary": bool(job.salary),
    "typo_count": count_typos(job.description),
    "urgency_keywords": count_keywords(job.description, ["urgent", "immediate", "ASAP"]),
    "vague_language": detect_vague_phrases(job.description),
    
    # Behavioral (from MCP server)
    "company_ghost_rate": mcp_client.read_resource(f"company://{job.company}/hiring_patterns").ghost_job_frequency,
    "repost_frequency": check_if_reposted(job.title, job.company),
    "job_age_days": (today - job.posted_date).days,
    
    # Metadata
    "has_company_logo": bool(job.company_logo),
    "application_method": job.application_method,  # "Easy Apply" vs external site
}
```

#### Model Training
```python
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE  # Handle imbalanced data

# SMOTE to balance dataset (ghost jobs are rare)
X_resampled, y_resampled = SMOTE().fit_resample(X_train, y_train)

# Train Random Forest
model = RandomForestClassifier(n_estimators=100, max_depth=10)
model.fit(X_resampled, y_resampled)

# Predict ghost job probability
ghost_score = model.predict_proba(features)[0][1]  # 0.0 - 1.0
```

#### Continuous Learning
- **User Feedback**: "Mark as ghost job" button → retrain model
- **Outcome Tracking**: If user applies and gets no response after 30 days → increase ghost score
- **Company Patterns**: If 5+ jobs from Company X are marked as ghost → flag all future jobs

---

## 🛠️ Recommended Tech Stack (Updated)

### Core Framework
```
Language: Python 3.11+
Agent Framework: LangGraph (latest)
MCP SDK: FastMCP (Python) or @modelcontextprotocol/sdk (TypeScript)
LLM: Anthropic Claude 3.5 Sonnet (best for agentic workflows)
```

### Data Layer
```
MCP Server Storage:
├── Vector DB: Qdrant (faster than Chroma, better scaling)
├── Graph DB: Neo4j (company relationships)
├── Document Store: PostgreSQL 16 with pgvector
└── Cache: Redis 7.x

User Data (separate from MCP):
└── PostgreSQL (resumes, applications, user preferences)
```

### Job Scraping
```
Scraping: Playwright (handles JavaScript-heavy sites)
APIs: 
├── JSearch API (RapidAPI) - 10,000+ job boards aggregated
├── Adzuna API - Official job board API
└── LinkedIn Voyager API (unofficial, use cautiously)
```

### ML/NLP
```
Resume Parsing: spaCy + custom NER model
ATS Scoring: scikit-learn + custom keyword extraction
Ghost Job Detection: XGBoost + SMOTE for imbalanced data
Embeddings: OpenAI text-embedding-3-large or Cohere Embed v3
```

### Deployment
```
MCP Server: Railway / Render (supports long-running processes)
API: FastAPI + Uvicorn
Background Jobs: Celery + Redis
Monitoring: LangSmith (LangGraph observability)
```

---

## 🎯 Updated Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph Orchestrator                    │
│                  (Supervisor-Worker Pattern)                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Job    │  │  Resume  │  │  Email   │  │  Ghost   │   │
│  │ Scraper  │  │Optimizer │  │  Writer  │  │Detector  │   │
│  │ (Async)  │  │ (Loop)   │  │          │  │ (XGBoost)│   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │             │             │          │
│       └─────────────┴─────────────┴─────────────┘          │
│                         │                                   │
│                         ▼                                   │
│              ┌──────────────────────┐                       │
│              │   MCP Client         │                       │
│              └──────────┬───────────┘                       │
└─────────────────────────┼───────────────────────────────────┘
                          │ OAuth 2.1
                          ▼
        ┌─────────────────────────────────────┐
        │   MCP Server (FastMCP)              │
        │   Universal Company Knowledge Base  │
        ├─────────────────────────────────────┤
        │  Resources:                         │
        │  - company://{name}/overview        │
        │  - company://{name}/tech_stack      │
        │  - company://{name}/hiring_patterns │
        │                                     │
        │  Tools:                             │
        │  - search_companies() [Async]       │
        │  - add_company_data()               │
        │                                     │
        │  Storage:                           │
        │  - Qdrant (vectors)                 │
        │  - Neo4j (graph)                    │
        │  - PostgreSQL (documents)           │
        └─────────────────────────────────────┘
```

---

## 📋 Next Steps

1. **Set up MCP server** with FastMCP (Python) - supports latest async features
2. **Build LangGraph workflow** with supervisor-worker pattern
3. **Train ghost job detector** using XGBoost on EMSCAD dataset
4. **Implement ATS scorer** with company tech stack integration
5. **Deploy to Railway** for MCP server hosting

**Ready to start building?** We now have a cutting-edge, production-ready architecture!
