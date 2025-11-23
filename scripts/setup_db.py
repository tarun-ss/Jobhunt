"""
Setup script to initialize the JobHunter AI project
"""
import asyncio
import logging
from pathlib import Path

# Create necessary directories
DIRECTORIES = [
    "logs",
    "data",
    "ml_models/ghost_job_detector",
    "ml_models/embeddings",
    "agents",
    "agents/scrapers",
    "agents/protocols",
    "orchestration",
    "memory",
    "tools",
    "observability",
    "api/routes",
    "api/middleware",
    "database/migrations",
    "tests/test_agents",
    "tests/test_mcp_server",
    "tests/test_orchestration",
    "tests/test_api",
    "scripts"
]

def create_directories():
    """Create all necessary directories"""
    print("Creating project directories...")
    for dir_path in DIRECTORIES:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        # Create __init__.py for Python packages
        if not dir_path.startswith(("logs", "data", "ml_models", "database", "tests", "scripts")):
            init_file = Path(dir_path) / "__init__.py"
            if not init_file.exists():
                init_file.write_text('"""Package"""\\n')
    print("✓ Directories created")

def create_placeholder_files():
    """Create placeholder files"""
    print("Creating placeholder files...")
    
    # .gitkeep files for empty directories
    for dir_path in ["logs", "data", "ml_models/ghost_job_detector", "ml_models/embeddings"]:
        gitkeep = Path(dir_path) / ".gitkeep"
        gitkeep.touch()
    
    print("✓ Placeholder files created")

async def setup_databases():
    """Initialize databases"""
    print("Setting up databases...")
    
    try:
        from mcp_server.storage.document_store import DocumentStore
        from mcp_server.storage.vector_db import VectorDB
        from mcp_server.storage.graph_db import GraphDB
        
        # Initialize document store
        print("  - Initializing PostgreSQL...")
        doc_store = DocumentStore()
        await doc_store.initialize()
        print("  ✓ PostgreSQL ready")
        
        # Initialize vector DB
        print("  - Initializing Qdrant...")
        vector_db = VectorDB()
        await vector_db.initialize()
        print("  ✓ Qdrant ready")
        
        # Initialize graph DB
        print("  - Initializing Neo4j...")
        graph_db = GraphDB()
        await graph_db.initialize()
        print("  ✓ Neo4j ready")
        
        print("✓ All databases initialized")
        return True
        
    except Exception as e:
        print(f"✗ Database setup failed: {e}")
        print("  Make sure you have:")
        print("  1. PostgreSQL running")
        print("  2. Qdrant running (docker run -p 6333:6333 qdrant/qdrant)")
        print("  3. Neo4j running")
        print("  4. .env file configured with connection strings")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("JobHunter AI - Project Setup")
    print("=" * 60)
    print()
    
    # Step 1: Create directories
    create_directories()
    print()
    
    # Step 2: Create placeholder files
    create_placeholder_files()
    print()
    
    # Step 3: Check for .env file
    if not Path(".env").exists():
        print("⚠ Warning: .env file not found")
        print("  Copy .env.example to .env and configure your API keys")
        print()
        return
    
    # Step 4: Setup databases
    print("Attempting to connect to databases...")
    print("(This requires PostgreSQL, Qdrant, and Neo4j to be running)")
    print()
    
    try:
        success = asyncio.run(setup_databases())
        if success:
            print()
            print("=" * 60)
            print("✓ Setup complete!")
            print("=" * 60)
            print()
            print("Next steps:")
            print("1. Run: python scripts/seed_companies.py (to add initial company data)")
            print("2. Run: python mcp_server/server.py (to start MCP server)")
            print("3. Run: uvicorn api.main:app --reload (to start API server)")
        else:
            print()
            print("Setup incomplete. Please fix database connections and try again.")
    except Exception as e:
        print(f"Setup failed: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
