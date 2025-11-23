# JobHunter AI

AI-powered job application automation platform with ghost job detection, ATS resume optimization, and personalized cold email generation.

## 🌟 Key Features

- **Ghost Job Detection**: ML-powered detection of fake job postings (85-92% accuracy)
- **ATS Resume Optimization**: Automatically tailor resumes for each company's tech stack
- **Universal Company Knowledge Base**: Free, self-learning MCP server with 10,000+ companies
- **Multi-Agent System**: LangGraph-powered workflow with specialized agents
- **Cold Email Generation**: Personalized outreach based on company research
- **Application Tracking**: Monitor application status and auto-follow-up

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph Orchestrator                    │
│                  (Supervisor-Worker Pattern)                 │
├─────────────────────────────────────────────────────────────┤
│  Job Scraper → Ghost Detector → Resume Optimizer →          │
│  ATS Scorer → Email Writer → Application Submitter          │
└─────────────────────┬───────────────────────────────────────┘
                      │ MCP Protocol (OAuth 2.1)
                      ▼
        ┌─────────────────────────────────────┐
        │   MCP Server (FastMCP)              │
        │   Universal Company Knowledge Base  │
        │   - 10,000+ companies               │
        │   - Daily auto-updates              │
        │   - Self-learning                   │
        └─────────────────────────────────────┘
```

## 🚀 Tech Stack

- **Language**: Python 3.11+
- **Agent Framework**: LangGraph
- **MCP**: FastMCP (async operations, OAuth 2.1)
- **LLM**: Anthropic Claude 3.5 Sonnet
- **Vector DB**: Qdrant
- **Graph DB**: Neo4j
- **Document Store**: PostgreSQL 16 + pgvector
- **Job Scraping**: Playwright + JSearch API
- **ML**: XGBoost + SMOTE (ghost job detection)
- **API**: FastAPI + Uvicorn

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/yourusername/jobhunter-ai.git
cd jobhunter-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Set up database
python scripts/setup_db.py

# Seed initial company data (100 companies)
python scripts/seed_companies.py
```

## 🔧 Configuration

Create a `.env` file with:

```env
# LLM API Keys
ANTHROPIC_API_KEY=your_key_here

# Database
POSTGRES_URL=postgresql://user:pass@localhost:5432/jobhunter
QDRANT_URL=http://localhost:6333
NEO4J_URL=bolt://localhost:7687

# Job Scraping APIs
JSEARCH_API_KEY=your_rapidapi_key
ADZUNA_API_KEY=your_key

# Email (Gmail API)
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_secret

# MCP Server
MCP_SERVER_URL=http://localhost:8000
MCP_OAUTH_CLIENT_ID=your_client_id
```

## 🎯 Usage

### Start MCP Server
```bash
python mcp_server/server.py
```

### Start API Server
```bash
uvicorn api.main:app --reload
```

### Run Daily Update Pipeline
```bash
python scripts/run_daily_update.py
```

### Use as Library
```python
from agents.resume_optimizer import ResumeOptimizer
from agents.ats_scorer import ATSScorer

# Optimize resume for a job
optimizer = ResumeOptimizer()
optimized_resume = optimizer.optimize(
    base_resume="path/to/resume.pdf",
    job_url="https://linkedin.com/jobs/123"
)

# Score ATS compatibility
scorer = ATSScorer()
score = scorer.score(optimized_resume, job_description)
print(f"ATS Score: {score}/100")
```

## 📚 Documentation

- [MCP Architecture](docs/mcp_architecture.md)
- [Self-Learning MCP](docs/self_learning_mcp.md)
- [Multi-Company Examples](docs/mcp_multi_company_examples.md)
- [Tech Stack 2025](docs/tech_stack_2025.md)

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/test_agents/

# Run with coverage
pytest --cov=agents --cov-report=html
```

## 🤝 Contributing

We welcome contributions! The MCP server is a **free, public knowledge base** that improves with community input.

Ways to contribute:
- Report ghost jobs
- Submit company data
- Add interview experiences
- Improve ML models

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.



## 🙏 Acknowledgments

- [Anthropic](https://anthropic.com) for MCP protocol
- [LangChain](https://langchain.com) for LangGraph
- Research papers on ghost job detection
- Open-source community

t jobs and help job seekers**
