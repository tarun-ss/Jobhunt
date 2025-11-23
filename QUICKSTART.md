# JobHunter AI - Quick Start Guide

## Prerequisites

- Python 3.11+
- PostgreSQL (for company data)
- Qdrant (for vector search) - Optional for MVP
- Neo4j (for graph relationships) - Optional for MVP
- Google Gemini API key

## Minimal Setup (Without Databases)

If you want to test the agents without setting up databases:

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install google-generativeai langchain langchain-google-genai
```

### 2. Get Google Gemini API Key

1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy your key

### 3. Create .env File

```bash
# Create .env file
copy .env.example .env  # Windows
# or
cp .env.example .env    # Mac/Linux
```

Edit `.env` and add your Gemini API key:

```env
GOOGLE_API_KEY=your_actual_api_key_here
```

### 4. Test Base Agent

Create a test file `test_agent.py`:

```python
import asyncio
from agents.base_agent import BaseAgent

async def main():
    # Create a simple agent
    agent = BaseAgent(
        name="TestAgent",
        system_prompt="You are a helpful assistant that analyzes job descriptions."
    )
    
    # Test it
    response = await agent.invoke_llm(
        "Analyze this job description and extract the tech stack: "
        "We're looking for a Senior Software Engineer with Python, React, and AWS experience."
    )
    
    print("Agent Response:")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:

```bash
python test_agent.py
```

## Full Setup (With Databases)

### 1. Install All Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Databases

#### PostgreSQL
```bash
# Install PostgreSQL
# Windows: Download from https://www.postgresql.org/download/windows/
# Mac: brew install postgresql
# Linux: sudo apt-get install postgresql

# Create database
createdb jobhunter
```

#### Qdrant (Vector Database)
```bash
# Using Docker (easiest)
docker run -p 6333:6333 qdrant/qdrant

# Or install locally: https://qdrant.tech/documentation/quick-start/
```

#### Neo4j (Graph Database)
```bash
# Using Docker
docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j

# Or download: https://neo4j.com/download/
```

### 3. Configure .env

```env
GOOGLE_API_KEY=your_gemini_api_key

# Database URLs
POSTGRES_URL=postgresql://user:password@localhost:5432/jobhunter
QDRANT_URL=http://localhost:6333
NEO4J_URL=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
REDIS_URL=redis://localhost:6379/0

# API Configuration
API_SECRET_KEY=your_random_secret_key_here
```

### 4. Initialize Project

```bash
python scripts/setup_db.py
```

### 5. Start MCP Server

```bash
python mcp_server/server.py
```

## What's Next?

Once the basic setup works, you can:

1. **Add Company Data**: Run `python scripts/seed_companies.py` to add initial companies
2. **Build Agents**: Start implementing job scrapers, resume optimizers, etc.
3. **Test Workflows**: Create LangGraph workflows to orchestrate agents
4. **Deploy**: Deploy MCP server to Railway/Render

## Troubleshooting

### "Module not found" errors
```bash
# Make sure you're in the virtual environment
# and have installed dependencies
pip install -r requirements.txt
```

### Database connection errors
```bash
# For minimal testing, you can skip databases
# Just test the base agent with LLM calls
```

### API key errors
```bash
# Make sure .env file exists and has your key
# Check: cat .env (Mac/Linux) or type .env (Windows)
```

## Minimal Working Example

Don't want to set up databases yet? Here's a standalone script:

```python
# minimal_test.py
import os
os.environ["GOOGLE_API_KEY"] = "your_key_here"

from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")

response = llm.invoke("Extract tech stack from: Looking for Python, React, AWS engineer")
print(response.content)
```

Run: `python minimal_test.py`

## Need Help?

- Check logs in `logs/jobhunter.log`
- Review documentation in `docs/`
- Open an issue on GitHub
