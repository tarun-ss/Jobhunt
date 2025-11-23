# JobHunter AI - Project Structure

```
jobhunter-ai/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── config/
│   ├── __init__.py
│   ├── settings.py          # Environment variables, API keys
│   └── logging_config.py    # Logging configuration
│
├── mcp_server/              # MCP Server (Universal Company Knowledge Base)
│   ├── __init__.py
│   ├── server.py            # FastMCP server implementation
│   ├── resources.py         # MCP resources (company://{name}/*)
│   ├── tools.py             # MCP tools (search_companies, etc.)
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── vector_db.py     # Qdrant integration
│   │   ├── graph_db.py      # Neo4j integration
│   │   └── document_store.py # PostgreSQL integration
│   ├── data_quality.py      # Confidence scoring, conflict resolution
│   └── daily_update.py      # Automated daily refresh pipeline
│
├── agents/                  # Multi-Agent System
│   ├── __init__.py
│   ├── base_agent.py        # Abstract base class
│   ├── protocols/
│   │   ├── __init__.py
│   │   └── a2a.py           # Agent-to-Agent protocol
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base_scraper.py
│   │   ├── linkedin_scraper.py
│   │   ├── indeed_scraper.py
│   │   └── glassdoor_scraper.py
│   ├── ghost_job_detector.py
│   ├── resume_parser.py
│   ├── ats_scorer.py
│   ├── resume_optimizer.py
│   ├── company_researcher.py
│   ├── job_matcher.py
│   ├── email_writer.py
│   ├── application_submitter.py
│   └── application_monitor.py
│
├── orchestration/           # LangGraph Workflows
│   ├── __init__.py
│   ├── workflow.py          # Main workflow definition
│   └── supervisor.py        # Supervisor-worker pattern
│
├── memory/                  # Session & State Management
│   ├── __init__.py
│   └── session_manager.py   # User session state
│
├── tools/                   # Custom Tools
│   ├── __init__.py
│   ├── resume_diff.py       # Resume comparison
│   ├── email_sender.py      # Gmail API integration
│   └── ats_parser.py        # ATS keyword extraction
│
├── ml_models/               # Machine Learning Models
│   ├── __init__.py
│   ├── ghost_job_detector/
│   │   ├── model.pkl
│   │   ├── train.py
│   │   └── predict.py
│   └── embeddings/
│       └── generate_embeddings.py
│
├── observability/           # Logging, Tracing, Metrics
│   ├── __init__.py
│   ├── logger.py
│   ├── tracer.py
│   └── metrics.py
│
├── api/                     # FastAPI User-Facing API
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── resume.py
│   │   ├── jobs.py
│   │   ├── applications.py
│   │   └── metrics.py
│   └── middleware/
│       ├── __init__.py
│       ├── auth.py
│       └── rate_limit.py
│
├── database/                # Database Schemas & Migrations
│   ├── schema.sql
│   ├── migrations/
│   └── seed_data.sql
│
├── tests/                   # Test Suite
│   ├── __init__.py
│   ├── test_agents/
│   ├── test_mcp_server/
│   ├── test_orchestration/
│   └── test_api/
│
├── scripts/                 # Utility Scripts
│   ├── setup_db.py
│   ├── seed_companies.py    # Initial 100 companies
│   └── run_daily_update.py
│
└── docs/                    # Documentation
    ├── mcp_architecture.md
    ├── mcp_multi_company_examples.md
    ├── self_learning_mcp.md
    └── tech_stack_2025.md
```
