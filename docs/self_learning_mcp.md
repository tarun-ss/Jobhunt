# Self-Learning MCP Server Architecture

## Vision: Free, Public, Continuously Updating Company Knowledge Base

Instead of a static database, our MCP server will be a **living, breathing knowledge system** that:
- 🌍 **Free & Public**: Anyone can query company data
- 🔄 **Self-Learning**: Automatically updates daily with fresh data
- 🧠 **Adaptive**: Architecture evolves based on usage patterns
- 🤝 **Community-Driven**: Users contribute feedback to improve data quality

---

## Core Principles

### 1. Free & Open Access
```
Public MCP Server: mcp://jobhunter.ai/companies
- Anyone can read company data (no auth required)
- Rate-limited to prevent abuse (1000 requests/day per IP)
- Premium tier for unlimited access (optional revenue model)
```

### 2. Daily Auto-Update System

#### Automated Data Refresh Pipeline
```python
# Runs every day at 2 AM
class DailyUpdatePipeline:
    def run(self):
        # 1. Scrape new job postings
        new_jobs = self.scrape_job_boards()
        
        # 2. Extract company info from job descriptions
        for job in new_jobs:
            company_data = self.extract_company_info(job)
            self.update_mcp_server(company_data)
        
        # 3. Refresh stale data (>30 days old)
        stale_companies = self.find_stale_companies()
        for company in stale_companies:
            fresh_data = self.research_company(company)
            self.update_mcp_server(fresh_data)
        
        # 4. Update ghost job scores
        self.recalculate_ghost_scores()
        
        # 5. Retrain ML models with new data
        self.retrain_ghost_detector()
```

#### What Gets Updated Daily
- ✅ **Job Postings**: New jobs added, old jobs archived
- ✅ **Tech Stack**: Extracted from new job descriptions
- ✅ **Ghost Job Scores**: Recalculated based on user feedback
- ✅ **Company News**: Latest funding, acquisitions, layoffs
- ✅ **Glassdoor Ratings**: Refreshed weekly

### 3. Adaptive Architecture

#### Schema Evolution
```python
# MCP server automatically adapts schema based on data
class AdaptiveSchema:
    def add_field_if_needed(self, company_id, field_name, value):
        # If we discover a new useful field, add it
        if field_name not in self.schema:
            self.schema[field_name] = {
                "type": type(value),
                "added_date": today,
                "source": "auto_discovery"
            }
            self.migrate_existing_companies(field_name)
```

**Example**: If we notice many companies now list "Remote Policy", we automatically add that field to all companies.

#### Dynamic Resource Types
```python
# MCP server exposes new resources as we discover patterns
# Initially:
company://google/overview
company://google/tech_stack

# After learning:
company://google/remote_policy  # NEW - discovered from job postings
company://google/interview_process  # NEW - crowdsourced from users
company://google/salary_ranges  # NEW - aggregated from job postings
```

---

## Self-Learning Mechanisms

### 1. Crowdsourced Feedback Loop

#### User Contributions
```python
# Users can submit corrections/additions
mcp_client.call_tool(
    "contribute_company_data",
    {
        "company": "Google",
        "field": "interview_process",
        "data": "3 rounds: Phone screen, Technical, Behavioral",
        "source": "user_experience",
        "confidence": 0.9
    }
)

# System validates and merges contributions
if validate_contribution(data):
    merge_with_existing_data(data)
    increment_contributor_reputation(user)
```

#### Feedback Signals
- **Ghost Job Reports**: "Mark as ghost job" → update company ghost_job_frequency
- **Interview Outcomes**: "Got interview" → validate job was real, update company response_rate
- **Salary Data**: "Offered $X" → update company salary_ranges

### 2. Automated Learning from Job Postings

#### Tech Stack Extraction
```python
# Analyze 1000s of job descriptions daily
def learn_tech_stack(company):
    jobs = get_all_jobs_for_company(company)
    
    # Extract technologies mentioned
    tech_mentions = {}
    for job in jobs:
        techs = extract_technologies(job.description)
        for tech in techs:
            tech_mentions[tech] = tech_mentions.get(tech, 0) + 1
    
    # Only include tech mentioned in >20% of jobs
    threshold = len(jobs) * 0.2
    confirmed_tech_stack = [
        tech for tech, count in tech_mentions.items()
        if count > threshold
    ]
    
    return confirmed_tech_stack
```

### 3. Pattern Recognition & Anomaly Detection

#### Detect Emerging Trends
```python
# Detect when a company changes tech stack
def detect_tech_stack_shift(company):
    old_stack = get_historical_tech_stack(company, days_ago=90)
    new_stack = get_current_tech_stack(company)
    
    added_tech = set(new_stack) - set(old_stack)
    removed_tech = set(old_stack) - set(new_stack)
    
    if added_tech:
        log_event(f"{company} is adopting {added_tech}")
        notify_users_interested_in(added_tech)
```

#### Ghost Job Pattern Learning
```python
# ML model learns new ghost job patterns
def continuous_learning():
    # Get feedback from last 30 days
    labeled_jobs = get_user_labeled_jobs(days=30)
    
    # Retrain model monthly
    if len(labeled_jobs) > 100:
        X, y = prepare_training_data(labeled_jobs)
        model.partial_fit(X, y)  # Incremental learning
        
        # Evaluate improvement
        new_accuracy = evaluate_model(model)
        if new_accuracy > old_accuracy:
            deploy_new_model(model)
```

---

## Adaptive Architecture Examples

### Example 1: Auto-Discovering "DEI Initiatives"

```python
# System notices many job descriptions mention "diversity"
# Automatically creates new resource

# Week 1: Pattern detected
diversity_mentions = count_keyword_in_jobs("diversity", "inclusion")
if diversity_mentions > 1000:
    create_new_resource_type("dei_initiatives")

# Week 2: Resource available
company://google/dei_initiatives
# Returns: {"programs": ["Women in Tech", "LGBTQ+ ERG"], "confidence": 0.85}
```

### Example 2: Adapting to Market Changes

```python
# During mass layoffs (e.g., 2024 tech layoffs)
# System automatically adds "layoff_risk" field

if detect_market_trend("layoffs"):
    for company in all_companies:
        layoff_risk = calculate_layoff_risk(
            recent_news=company.news,
            hiring_velocity=company.hiring_velocity,
            funding_status=company.funding
        )
        company.layoff_risk = layoff_risk  # NEW FIELD
```

---

## Data Quality & Trust

### Confidence Scoring
```json
{
  "company": "Google",
  "tech_stack": {
    "languages": ["Python", "Java", "Go"],
    "confidence": 0.95,
    "sources": [
      {"type": "job_descriptions", "count": 1247, "weight": 0.6},
      {"type": "company_website", "weight": 0.3},
      {"type": "user_contributions", "count": 23, "weight": 0.1}
    ],
    "last_verified": "2025-11-22"
  }
}
```

### Conflict Resolution
```python
# When sources disagree
def resolve_conflict(field, sources):
    if field == "tech_stack":
        # For tech stack, use majority voting
        return majority_vote(sources)
    elif field == "glassdoor_rating":
        # For ratings, use most recent
        return most_recent(sources)
    elif field == "ghost_job_frequency":
        # For ghost jobs, trust user reports over algorithms
        return weighted_average(sources, weights={"user": 0.7, "algorithm": 0.3})
```

---

## Monetization (While Keeping Core Free)

### Free Tier
- ✅ Read access to all company data
- ✅ 1000 API calls/day
- ✅ Basic search

### Premium Tier ($20/month)
- ✅ Unlimited API calls
- ✅ Real-time updates (webhooks)
- ✅ Advanced analytics (company comparisons, trend analysis)
- ✅ Priority support

### Enterprise Tier ($500/month)
- ✅ Private MCP server instance
- ✅ Custom data sources
- ✅ SLA guarantees
- ✅ Dedicated support

---

## Technical Implementation

### Daily Update Cron Job
```python
# Deployed on Railway with cron scheduler
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

# Daily at 2 AM UTC
scheduler.add_job(
    func=update_all_companies,
    trigger="cron",
    hour=2,
    minute=0
)

# Hourly: Update trending companies
scheduler.add_job(
    func=update_trending_companies,
    trigger="interval",
    hours=1
)

# Weekly: Retrain ML models
scheduler.add_job(
    func=retrain_models,
    trigger="cron",
    day_of_week="sun",
    hour=3
)

scheduler.start()
```

### Schema Migration System
```python
# Automatically migrate schema when new fields are added
class SchemaManager:
    def add_field(self, field_name, default_value=None):
        # Add to schema
        self.schema[field_name] = {
            "type": type(default_value),
            "added": datetime.now()
        }
        
        # Backfill existing companies
        for company in self.get_all_companies():
            if field_name not in company:
                company[field_name] = default_value
                company[f"{field_name}_confidence"] = 0.0  # Low confidence until verified
```

---

## Community Contribution Platform

### Web Interface for Contributions
```
https://jobhunter.ai/contribute

Users can:
- Submit company reviews
- Report ghost jobs
- Add interview experiences
- Verify tech stacks
- Upload salary data (anonymized)

Gamification:
- Earn reputation points
- Unlock badges ("Top Contributor", "Ghost Hunter")
- Leaderboard
```

### API for Contributions
```python
# Anyone can contribute via API
import requests

requests.post("https://api.jobhunter.ai/contribute", json={
    "company": "Stripe",
    "field": "interview_process",
    "data": {
        "rounds": 4,
        "difficulty": "Hard",
        "topics": ["System Design", "API Design", "Coding"]
    },
    "source": "personal_experience",
    "date": "2025-11-15"
})
```

---

## Benefits of This Approach

### For Users
- ✅ **Always Fresh Data**: Company info updated daily
- ✅ **Crowdsourced Accuracy**: Real experiences from job seekers
- ✅ **Free Access**: No paywalls for basic features
- ✅ **Transparent**: See confidence scores and data sources

### For the Platform
- ✅ **Network Effects**: More users → more data → better accuracy
- ✅ **Scalable**: Automated updates reduce manual work
- ✅ **Defensible Moat**: Unique, constantly improving dataset
- ✅ **Revenue Potential**: Premium tiers for power users

### For the Ecosystem
- ✅ **Open Standard**: Other tools can build on our MCP server
- ✅ **Reduces Information Asymmetry**: Levels playing field for job seekers
- ✅ **Fights Ghost Jobs**: Collective intelligence to identify fake postings

---

## Next Steps

1. **Build MVP MCP Server**: Start with 100 companies, manual updates
2. **Add Daily Scraper**: Automate job posting ingestion
3. **Implement Feedback Loop**: "Report Ghost Job" button
4. **Launch Public Beta**: Free access, gather user feedback
5. **Add Auto-Learning**: Schema evolution, pattern detection
6. **Scale to 10,000+ Companies**: Full automation

**This is a living, breathing system that gets smarter every day!** 🚀
