# Cloud Database Setup Guide

## Step-by-Step Setup (15 minutes)

### 1. Supabase (PostgreSQL) - FREE

**Sign Up:**
1. Go to https://supabase.com/
2. Click "Start your project"
3. Sign in with GitHub
4. Create new project:
   - Name: **Any name you want** (e.g., "tarun-ss's Project", "jobhunter", etc.)
   - Database Password: (create a strong password - SAVE THIS!)
   - Region: Choose closest to you
   - Click "Create new project"

**Get Connection String:**
1. Wait for project to finish setting up (~2 minutes)
2. Go to Settings → Database
3. Scroll to "Connection string" section
4. Copy the **"URI"** connection string (looks like: `postgresql://postgres.[PROJECT-REF]:[PASSWORD]@...`)
5. Replace `[YOUR-PASSWORD]` with the database password you created

**Example:**
```
postgresql://postgres.xxxxx:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:5432/postgres
```

**Run Schema:**
1. Go to **SQL Editor** in Supabase dashboard (left sidebar)
2. Click "New Query"
3. Copy ALL contents of `database/schema.sql` from your project
4. Paste into the SQL editor
5. Click "Run" (or press Ctrl+Enter)
6. You should see "Success. No rows returned" - this is correct!

---

### 2. Qdrant Cloud (Vector DB) - FREE

**Sign Up:**
1. Go to https://cloud.qdrant.io/
2. Click "Get Started"
3. Sign up with email or GitHub
4. Create new cluster:
   - Name: `jobhunter-vectors`
   - Cloud: Any (AWS recommended)
   - Region: Choose closest
   - Plan: Free tier (1GB)
   - Click "Create"

**Get API Key:**
1. Wait for cluster to be ready (~1 minute)
2. Click on your cluster
3. Go to "API Keys" tab
4. Click "Create API Key"
5. Copy the API key (save it securely!)
6. Copy the cluster URL (looks like: `https://xxxxx.us-east.aws.cloud.qdrant.io`)

---

### 3. Neo4j Aura (Graph DB) - FREE

**Sign Up:**
1. Go to https://neo4j.com/cloud/aura/
2. Click "Start Free"
3. Sign up with email or Google
4. Create new instance:
   - Name: `jobhunter-graph`
   - Type: AuraDB Free
   - Region: Choose closest
   - Click "Create"

**Get Credentials:**
1. **IMPORTANT**: Download credentials file immediately (you can't see password again!)
2. Save the file securely
3. Note down:
   - Connection URI: `neo4j+s://xxxxx.databases.neo4j.io`
   - Username: `neo4j`
   - Password: (from downloaded file)

---

### 4. Upstash (Redis) - FREE

**Sign Up:**
1. Go to https://upstash.com/
2. Click "Get Started"
3. Sign up with email or GitHub
4. Create new database:
   - Name: `jobhunter-cache`
   - Type: Regional
   - Region: Choose closest
   - Click "Create"

**Get Connection String:**
1. Click on your database
2. Copy the "REST URL" or "Redis URL"
3. Example: `redis://default:xxxxx@us1-xxxxx.upstash.io:6379`

---

## Update Your .env File

Once you have all the credentials, update your `.env` file:

```env
# LLM Configuration (already set)
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
LLM_MODEL=llama-3.3-70b-versatile
GOOGLE_API_KEY=your_google_api_key_here

# Cloud Databases (UPDATE THESE)
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres
QDRANT_URL=https://xxxxx.us-east.aws.cloud.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key_here
NEO4J_URL=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password_here
REDIS_URL=redis://default:xxxxx@us1-xxxxx.upstash.io:6379

# API Configuration
API_SECRET_KEY=my_random_secret_key_12345
LOG_LEVEL=INFO
LOG_FILE=logs/jobhunter.log
```

---

## Test Connections

After updating .env, test each connection:

```bash
# Test script will be created
python test_cloud_connections.py
```

---

## Free Tier Limits

### Supabase
- ✓ 500MB database
- ✓ 1GB file storage
- ✓ 50,000 monthly active users
- ✓ Unlimited API requests

### Qdrant Cloud
- ✓ 1GB vector storage
- ✓ ~1M vectors (depending on size)
- ✓ Unlimited requests

### Neo4j Aura
- ✓ 200k nodes
- ✓ 400k relationships
- ✓ Plenty for development

### Upstash Redis
- ✓ 10,000 commands/day
- ✓ 256MB storage
- ✓ Perfect for caching

---

## Next Steps

1. Sign up for all 4 services (takes ~15 minutes)
2. Update .env with your credentials
3. Run `python test_cloud_connections.py`
4. Start the backend: `cd mcp_server && uvicorn app.main:app --reload`
5. Start the frontend: `cd frontend && npm run dev`

---

## Troubleshooting

### Supabase Connection Failed
- Check password is correct
- Make sure you replaced `[YOUR-PASSWORD]` in connection string
- Check if IP is whitelisted (Supabase allows all by default)

### Qdrant Connection Failed
- Make sure you copied the API key correctly
- Check cluster is "Running" status
- Verify URL includes `https://`

### Neo4j Connection Failed
- Use the password from downloaded credentials file
- Make sure URL starts with `neo4j+s://`
- Check instance is "Running"

### Upstash Connection Failed
- Copy the full Redis URL including password
- Make sure database is "Active"

---

## Cost

**All services are FREE for development!**

You only pay if you exceed free tier limits, which is unlikely during development.

---

## Security Note

**Never commit .env file to Git!**

The `.env` file is already in `.gitignore`, but double-check before pushing code.
