"""
Neo4j Graph Database
Company relationships and similarity
"""
import logging
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase

from config.settings import settings

logger = logging.getLogger(__name__)


class GraphDB:
    """Neo4j graph database for company relationships"""
    
    def __init__(self):
        self.driver = None
    
    async def initialize(self):
        """Initialize Neo4j connection"""
        try:
            self.driver = GraphDatabase.driver(
                settings.neo4j_url,
                auth=(settings.neo4j_user, settings.neo4j_password)
            )
            
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            
            logger.info("Neo4j graph DB initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize graph DB: {e}")
            raise
    
    async def find_similar(
        self,
        company_name: str,
        criteria: List[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Find similar companies based on criteria"""
        try:
            company_id = company_name.lower().replace(" ", "_")
            
            # For now, return placeholder data
            # In production, this would use graph traversal
            # to find companies with similar tech stacks, size, etc.
            
            with self.driver.session() as session:
                # Example Cypher query (simplified)
                query = """
                MATCH (c1:Company {id: $company_id})
                MATCH (c2:Company)
                WHERE c1 <> c2
                RETURN c2.id AS company_id, c2.name AS name
                LIMIT $limit
                """
                
                result = session.run(
                    query,
                    company_id=company_id,
                    limit=limit
                )
                
                similar = []
                for record in result:
                    similar.append({
                        "company_id": record["company_id"],
                        "name": record["name"],
                        "similarity_score": 0.85  # Placeholder
                    })
                
                return similar
                
        except Exception as e:
            logger.error(f"Failed to find similar companies: {e}")
            return []
    
    async def add_company_node(self, company_id: str, company_data: Dict[str, Any]):
        """Add company as a node in the graph"""
        try:
            with self.driver.session() as session:
                query = """
                MERGE (c:Company {id: $company_id})
                SET c.name = $name,
                    c.industry = $industry,
                    c.size = $size
                """
                
                session.run(
                    query,
                    company_id=company_id,
                    name=company_data.get("name", ""),
                    industry=company_data.get("overview", {}).get("industry", ""),
                    size=company_data.get("overview", {}).get("size", "")
                )
                
                logger.info(f"Added company node: {company_id}")
                
        except Exception as e:
            logger.error(f"Failed to add company node: {e}")
    
    async def create_tech_stack_relationships(self, company_id: str, technologies: List[str]):
        """Create relationships between company and technologies"""
        try:
            with self.driver.session() as session:
                for tech in technologies:
                    query = """
                    MATCH (c:Company {id: $company_id})
                    MERGE (t:Technology {name: $tech})
                    MERGE (c)-[:USES]->(t)
                    """
                    
                    session.run(
                        query,
                        company_id=company_id,
                        tech=tech
                    )
                
                logger.info(f"Created tech stack relationships for {company_id}")
                
        except Exception as e:
            logger.error(f"Failed to create tech relationships: {e}")
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
