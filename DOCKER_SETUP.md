# JobHunter AI - Docker Setup Guide

## Prerequisites

- Docker Desktop for Windows installed
- At least 8GB RAM available for Docker
- 10GB free disk space

## Quick Start

### 1. Install Docker Desktop

Download and install from: https://www.docker.com/products/docker-desktop/

### 2. Start All Services

```bash
# Start all services (databases + backend + frontend)
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 3. Access Services

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Qdrant**: http://localhost:6333/dashboard
- **Neo4j Browser**: http://localhost:7474
- **Redis**: localhost:6379

### 4. Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

## Service Details

### PostgreSQL (Port 5432)
- Database: `jobhunter`
- User: `jobhunter`
- Password: `jobhunter_dev_password`
- Auto-initializes with schema from `database/schema.sql`

### Qdrant (Port 6333)
- Vector database for semantic search
- Dashboard: http://localhost:6333/dashboard
- Collections: `companies`, `job_postings`

### Neo4j (Ports 7474, 7687)
- Graph database for company relationships
- Browser: http://localhost:7474
- User: `neo4j`
- Password: `jobhunter_dev_password`

### Redis (Port 6379)
- Caching layer
- No password (development only)

### MCP Server (Port 8000)
- FastAPI backend
- Auto-reloads on code changes
- API docs at /docs

### Frontend (Port 5173)
- React + Vite + TailwindCSS
- Hot module replacement enabled

## Development Workflow

### Make Code Changes

All code changes are automatically reflected:
- **Backend**: Uvicorn auto-reloads
- **Frontend**: Vite HMR updates instantly

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f mcp_server
docker-compose logs -f frontend
```

### Access Database

```bash
# PostgreSQL
docker-compose exec postgres psql -U jobhunter -d jobhunter

# Example queries
SELECT * FROM companies;
SELECT * FROM job_postings;
```

### Access Neo4j

1. Open http://localhost:7474
2. Connect with:
   - URL: `bolt://localhost:7687`
   - User: `neo4j`
   - Password: `jobhunter_dev_password`

### Reset Everything

```bash
# Stop and remove all data
docker-compose down -v

# Start fresh
docker-compose up -d
```

## Troubleshooting

### Port Already in Use

If you get "port already in use" errors:

```bash
# Check what's using the port
netstat -ano | findstr :5432
netstat -ano | findstr :8000

# Kill the process or change ports in docker-compose.yml
```

### Database Connection Errors

```bash
# Check if PostgreSQL is healthy
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Frontend Not Loading

```bash
# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend

# Check logs
docker-compose logs -f frontend
```

### Out of Memory

Increase Docker Desktop memory:
1. Docker Desktop → Settings → Resources
2. Set Memory to at least 8GB
3. Click "Apply & Restart"

## Next Steps

Once Docker is running:

1. **Test the API**: http://localhost:8000/docs
2. **Open Frontend**: http://localhost:5173
3. **Upload a resume** and test the system
4. **Check databases** to see data being stored

## Production Deployment

For production, use:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

(Production compose file to be created separately)
