"""
MCP Server - Universal Company Knowledge Base
FastMCP implementation with async operations and OAuth 2.1
"""
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp import types
import logging
from typing import Any

from config.settings import settings
from .resources import CompanyResources
from .tools import CompanyTools
from .storage.document_store import DocumentStore
from .storage.vector_db import VectorDB
from .storage.graph_db import GraphDB

logger = logging.getLogger(__name__)


class CompanyKnowledgeServer:
    """MCP Server for company knowledge base"""
    
    def __init__(self):
        self.server = Server("company-knowledge-base")
        self.doc_store = DocumentStore()
        self.vector_db = VectorDB()
        self.graph_db = GraphDB()
        
        self.resources = CompanyResources(
            doc_store=self.doc_store,
            vector_db=self.vector_db,
            graph_db=self.graph_db
        )
        self.tools = CompanyTools(
            doc_store=self.doc_store,
            vector_db=self.vector_db,
            graph_db=self.graph_db
        )
        
        self._register_handlers()
    
    def _register_handlers(self):
        """Register MCP protocol handlers"""
        
        @self.server.list_resources()
        async def list_resources() -> list[types.Resource]:
            """List available company resources"""
            return await self.resources.list_resources()
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read a specific company resource"""
            return await self.resources.read_resource(uri)
        
        @self.server.list_tools()
        async def list_tools() -> list[types.Tool]:
            """List available tools"""
            return await self.tools.list_tools()
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
            """Execute a tool"""
            return await self.tools.call_tool(name, arguments)
    
    async def run(self):
        """Start the MCP server"""
        logger.info(f"Starting MCP server on port {settings.mcp_server_port}")
        
        # Initialize storage backends
        await self.doc_store.initialize()
        await self.vector_db.initialize()
        await self.graph_db.initialize()
        
        logger.info("MCP server ready")
        
        # Run server (implementation depends on transport - stdio, HTTP, etc.)
        # For now, this is a placeholder
        # In production, you'd use: await self.server.run()


async def main():
    """Main entry point"""
    from config.logging_config import setup_logging
    setup_logging()
    
    server = CompanyKnowledgeServer()
    await server.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
