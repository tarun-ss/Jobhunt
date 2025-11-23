"""
MCP Resources - Company data endpoints
Implements: company://{name}/overview, company://{name}/tech_stack, etc.
"""
from mcp import types
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class CompanyResources:
    """Manages company resource endpoints"""
    
    def __init__(self, doc_store, vector_db, graph_db):
        self.doc_store = doc_store
        self.vector_db = vector_db
        self.graph_db = graph_db
    
    async def list_resources(self) -> list[types.Resource]:
        """List all available company resources"""
        # For now, return template resources
        # In production, this would list all companies in the database
        return [
            types.Resource(
                uri="company://google/overview",
                name="Google - Company Overview",
                description="Basic information about Google",
                mimeType="application/json"
            ),
            types.Resource(
                uri="company://google/tech_stack",
                name="Google - Tech Stack",
                description="Technologies used at Google",
                mimeType="application/json"
            ),
            types.Resource(
                uri="company://google/culture",
                name="Google - Company Culture",
                description="Culture and work environment at Google",
                mimeType="application/json"
            ),
            types.Resource(
                uri="company://google/hiring_patterns",
                name="Google - Hiring Patterns",
                description="Historical hiring data and patterns",
                mimeType="application/json"
            ),
        ]
    
    async def read_resource(self, uri: str) -> str:
        """Read a specific company resource
        
        URI format: company://{company_name}/{resource_type}
        """
        try:
            # Parse URI
            if not uri.startswith("company://"):
                raise ValueError(f"Invalid URI scheme: {uri}")
            
            path = uri.replace("company://", "")
            parts = path.split("/")
            
            if len(parts) != 2:
                raise ValueError(f"Invalid URI format: {uri}")
            
            company_name, resource_type = parts
            
            # Fetch from document store
            data = await self.doc_store.get_company_resource(
                company_name=company_name,
                resource_type=resource_type
            )
            
            if data is None:
                return f'{{"error": "Resource not found: {uri}"}}'
            
            return data
            
        except Exception as e:
            logger.error(f"Error reading resource {uri}: {e}")
            return f'{{"error": "{str(e)}"}}'
