# JobHunter AI - API Keys Guide

## What You Actually Need

### ✅ Required (To Get Started)

**1. Google Gemini API Key** - FREE
- Get it here: https://aistudio.google.com/app/apikey
- Click "Create API Key"
- Free tier: 60 requests/minute
- **You already have this!** ✓

**2. API Secret Key**
- Just make up any random string
- Example: `my_secret_key_12345`
- Used for JWT authentication

### 🔧 Optional (For Specific Features)

#### Job Scraping APIs (Only if you want to auto-scrape jobs)

**JSearch API** (RapidAPI)
- Get it: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
- Free tier: 100 requests/month
- Use case: Scrape jobs from LinkedIn, Indeed, etc.

**Adzuna API**
- Get it: https://developer.adzuna.com/
- Free tier: 500 requests/month
- Use case: Alternative job scraping source

#### Email Automation (Only if you want to send cold emails)

**Gmail API**
- Guide: https://developers.google.com/gmail/api/quickstart/python
- Free: Unlimited (within Gmail limits)
- Use case: Send personalized cold emails to recruiters

#### Observability (Only for debugging)

**LangSmith**
- Get it: https://smith.langchain.com/
- Free tier available
- Use case: Debug LangGraph workflows, trace agent execution

### 💾 Databases (Optional for MVP)

You **don't need** these to start building agents:
- PostgreSQL - Can use SQLite instead
- Qdrant - Can skip vector search initially
- Neo4j - Can skip graph relationships initially
- Redis - Can skip caching initially

## Minimal Setup (Just to Test)

Create a `.env` file with ONLY this:

```env
GOOGLE_API_KEY=AIzaSyAxlr6Br5biUCbE3w8mlCClL9unCkL5VzI
API_SECRET_KEY=my_random_secret_123
POSTGRES_URL=sqlite:///jobhunter.db
```

That's it! You can now:
- ✅ Use Gemini LLM
- ✅ Build and test agents
- ✅ Store data in SQLite (no PostgreSQL needed)

## When Do You Need Other APIs?

| Feature | API Needed | Priority |
|---------|-----------|----------|
| Build agents | ✅ Gemini only | **High** |
| Test resume optimization | ✅ Gemini only | **High** |
| Scrape real jobs | JSearch or Adzuna | Medium |
| Send cold emails | Gmail API | Medium |
| Debug workflows | LangSmith | Low |
| Full MCP server | PostgreSQL, Qdrant, Neo4j | Low (for MVP) |

## How to Get Free API Keys (If Needed Later)

### JSearch (Job Scraping)
1. Go to https://rapidapi.com/
2. Sign up (free)
3. Subscribe to JSearch API (free tier)
4. Copy your API key

### Adzuna (Job Scraping)
1. Go to https://developer.adzuna.com/
2. Sign up
3. Create an app
4. Copy App ID and API Key

### Gmail API (Email Automation)
1. Go to https://console.cloud.google.com/
2. Create a new project
3. Enable Gmail API
4. Create OAuth credentials
5. Download credentials JSON

## Summary

**Right now, you only need:**
- ✅ Gemini API key (you have it!)
- ✅ A random secret key

**Everything else is optional** and can be added later when you need those specific features!
