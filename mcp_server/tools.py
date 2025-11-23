"""
MCP Tools - Company search and manipulation
Implements: search_companies(), add_company_data(), etc.
"""
from mcp import types
import logging
import json

logger = logging.getLogger(__name__)


class CompanyTools:
    """Manages company tools (search, add, update)"""
    
    def __init__(self, doc_store, vector_db, graph_db):
        self.doc_store = doc_store
        self.vector_db = vector_db
        self.graph_db = graph_db
    
    async def list_tools(self) -> list[types.Tool]:
        """List available tools"""
        return [
            types.Tool(
                name="search_companies",
                description="Search for companies by query (semantic search)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (e.g., 'AI startups in San Francisco')"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            ),
            types.Tool(
                name="get_company_info",
                description="Get detailed information about a specific company",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "company_name": {
                            "type": "string",
                            "description": "Company name (e.g., 'Google')"
                        },
                        "fields": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Fields to retrieve (e.g., ['tech_stack', 'culture'])"
                        }
                    },
                    "required": ["company_name"]
                }
            ),
            types.Tool(
                name="add_company_data",
                description="Add or update company information",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "company_name": {
                            "type": "string",
                            "description": "Company name"
                        },
                        "field": {
                            "type": "string",
                            "description": "Field to update (e.g., 'tech_stack')"
                        },
                        "data": {
                            "type": "object",
                            "description": "Data to add/update"
                        },
                        "source": {
                            "type": "string",
                            "description": "Data source (e.g., 'job_description', 'user_contribution')"
                        }
                    },
                    "required": ["company_name", "field", "data"]
                }
            ),
            types.Tool(
                name="find_similar_companies",
                description="Find companies similar to a given company",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "company_name": {
                            "type": "string",
                            "description": "Reference company name"
                        },
                        "criteria": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Similarity criteria (e.g., ['tech_stack', 'size', 'culture'])"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 5
                        }
                    },
                    "required": ["company_name"]
                }
            )
        ]
    
    async def call_tool(self, name: str, arguments: dict) -> list[types.TextContent]:
        """Execute a tool"""
        try:
            if name == "search_companies":
                result = await self._search_companies(**arguments)
            elif name == "get_company_info":
                result = await self._get_company_info(**arguments)
            elif name == "add_company_data":
                result = await self._add_company_data(**arguments)
            elif name == "find_similar_companies":
                result = await self._find_similar_companies(**arguments)
            else:
                result = {"error": f"Unknown tool: {name}"}
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            return [types.TextContent(
                type="text",
                text=json.dumps({"error": str(e)})
            )]
    
    async def _search_companies(self, query: str, limit: int = 10) -> dict:
        """Search companies using vector similarity"""
        results = await self.vector_db.search(query, limit=limit)
        return {
            "query": query,
            "results": results,
            "count": len(results)
        }
    
    async def _get_company_info(self, company_name: str, fields: list[str] = None) -> dict:
        """Get company information"""
        data = await self.doc_store.get_company(company_name, fields=fields)
        return data or {"error": f"Company not found: {company_name}"}
    
    async def _add_company_data(self, company_name: str, field: str, data: dict, source: str = "unknown") -> dict:
        """Add/update company data"""
        success = await self.doc_store.update_company(
            company_name=company_name,
            field=field,
            data=data,
            source=source
        )
        return {
            "success": success,
            "company": company_name,
            "field": field
        }
    
    async def _find_similar_companies(self, company_name: str, criteria: list[str] = None, limit: int = 5) -> dict:
        """Find similar companies using graph relationships"""
        similar = await self.graph_db.find_similar(
            company_name=company_name,
            criteria=criteria or ["tech_stack"],
            limit=limit
        )
        return {
            "reference_company": company_name,
            "similar_companies": similar,
            "count": len(similar)
        }
