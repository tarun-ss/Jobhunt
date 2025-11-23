"""
Database connection utilities for cloud services
Handles PostgreSQL (Supabase), Qdrant Cloud, Neo4j Aura, and Upstash Redis
"""
import os
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from qdrant_client import QdrantClient
from neo4j import GraphDatabase
import redis

class DatabaseManager:
    """Manages all database connections"""
    
    def __init__(self):
        self.postgres_engine = None
        self.postgres_session = None
        self.qdrant_client = None
        self.neo4j_driver = None
        self.redis_client = None
        
    def connect_postgres(self):
        """Connect to PostgreSQL (Supabase)"""
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL not set in environment")
        
        self.postgres_engine = create_engine(db_url, pool_pre_ping=True)
        SessionLocal = sessionmaker(bind=self.postgres_engine)
        self.postgres_session = SessionLocal
        
        print("[OK] Connected to PostgreSQL (Supabase)")
        return self.postgres_engine
    
    def connect_qdrant(self):
        """Connect to Qdrant Cloud"""
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_key = os.getenv("QDRANT_API_KEY")
        
        if not qdrant_url:
            raise ValueError("QDRANT_URL not set in environment")
        
        self.qdrant_client = QdrantClient(
            url=qdrant_url,
            api_key=qdrant_key
        )
        
        print("[OK] Connected to Qdrant Cloud")
        return self.qdrant_client
    
    def connect_neo4j(self):
        """Connect to Neo4j Aura"""
        neo4j_url = os.getenv("NEO4J_URL")
        neo4j_user = os.getenv("NEO4J_USER", "neo4j")
        neo4j_password = os.getenv("NEO4J_PASSWORD")
        
        if not neo4j_url or not neo4j_password:
            raise ValueError("NEO4J_URL and NEO4J_PASSWORD must be set")
        
        self.neo4j_driver = GraphDatabase.driver(
            neo4j_url,
            auth=(neo4j_user, neo4j_password)
        )
        
        print("[OK] Connected to Neo4j Aura")
        return self.neo4j_driver
    
    def connect_redis(self):
        """Connect to Upstash Redis"""
        redis_url = os.getenv("REDIS_URL")
        
        if not redis_url:
            raise ValueError("REDIS_URL not set in environment")
        
        self.redis_client = redis.from_url(redis_url)
        
        # Test connection
        self.redis_client.ping()
        
        print("[OK] Connected to Upstash Redis")
        return self.redis_client
    
    def connect_all(self):
        """Connect to all databases"""
        success_count = 0
        total_count = 4
        
        # PostgreSQL is required
        try:
            self.connect_postgres()
            success_count += 1
        except Exception as e:
            print(f"\n[ERROR] PostgreSQL connection failed: {e}")
            print("PostgreSQL is REQUIRED. Check your DATABASE_URL in .env")
            return False
        
        # Other databases are optional
        try:
            self.connect_qdrant()
            success_count += 1
        except Exception as e:
            print(f"\n[WARNING] Qdrant connection failed: {e}")
            print("Qdrant is optional - vector search will be disabled")
        
        try:
            self.connect_neo4j()
            success_count += 1
        except Exception as e:
            print(f"\n[WARNING] Neo4j connection failed: {e}")
            print("Neo4j is optional - graph features will be disabled")
        
        try:
            self.connect_redis()
            success_count += 1
        except Exception as e:
            print(f"\n[WARNING] Redis connection failed: {e}")
            print("Redis is optional - caching will be disabled")
        
        print(f"\n[SUCCESS] Connected to {success_count}/{total_count} databases")
        print("System is ready to use!")
        return True
    
    def close_all(self):
        """Close all database connections"""
        if self.postgres_engine:
            self.postgres_engine.dispose()
        if self.neo4j_driver:
            self.neo4j_driver.close()
        if self.redis_client:
            self.redis_client.close()
        
        print("All database connections closed")

# Global database manager instance
db_manager = DatabaseManager()

# Convenience functions
def get_postgres_session():
    """Get PostgreSQL session"""
    if not db_manager.postgres_session:
        db_manager.connect_postgres()
    return db_manager.postgres_session()

def get_qdrant_client():
    """Get Qdrant client"""
    if not db_manager.qdrant_client:
        db_manager.connect_qdrant()
    return db_manager.qdrant_client

def get_neo4j_session():
    """Get Neo4j session"""
    if not db_manager.neo4j_driver:
        db_manager.connect_neo4j()
    return db_manager.neo4j_driver.session()

def get_redis_client():
    """Get Redis client"""
    if not db_manager.redis_client:
        db_manager.connect_redis()
    return db_manager.redis_client
