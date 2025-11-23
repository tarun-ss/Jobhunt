"""
Qdrant Vector Database
Semantic search for companies
"""
import logging
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

from config.settings import settings

logger = logging.getLogger(__name__)


class VectorDB:
    """Qdrant vector database for semantic company search"""
    
    COLLECTION_NAME = "companies"
    VECTOR_SIZE = 384  # all-MiniLM-L6-v2 embedding size
    
    def __init__(self):
        self.client = None
        self.encoder = None
    
    async def initialize(self):
        """Initialize Qdrant client and embedding model"""
        try:
            self.client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key
            )
            
            # Create collection if it doesn't exist
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.COLLECTION_NAME not in collection_names:
                self.client.create_collection(
                    collection_name=self.COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=self.VECTOR_SIZE,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection: {self.COLLECTION_NAME}")
            
            # Load embedding model
            self.encoder = SentenceTransformer(settings.embedding_model)
            logger.info("Qdrant vector DB initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector DB: {e}")
            raise
    
    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Semantic search for companies"""
        try:
            # Generate query embedding
            query_vector = self.encoder.encode(query).tolist()
            
            # Search in Qdrant
            results = self.client.search(
                collection_name=self.COLLECTION_NAME,
                query_vector=query_vector,
                limit=limit
            )
            
            # Format results
            companies = []
            for result in results:
                companies.append({
                    "company_id": result.id,
                    "score": result.score,
                    "payload": result.payload
                })
            
            return companies
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    async def add_company(self, company_id: str, company_data: Dict[str, Any]):
        """Add company to vector index"""
        try:
            # Create text representation for embedding
            text = self._create_company_text(company_data)
            
            # Generate embedding
            vector = self.encoder.encode(text).tolist()
            
            # Upsert to Qdrant
            self.client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=[
                    PointStruct(
                        id=company_id,
                        vector=vector,
                        payload=company_data
                    )
                ]
            )
            
            logger.info(f"Added company to vector index: {company_id}")
            
        except Exception as e:
            logger.error(f"Failed to add company to vector index: {e}")
    
    def _create_company_text(self, company_data: Dict[str, Any]) -> str:
        """Create text representation of company for embedding"""
        parts = []
        
        if "name" in company_data:
            parts.append(f"Company: {company_data['name']}")
        
        if "overview" in company_data and company_data["overview"]:
            overview = company_data["overview"]
            if "industry" in overview:
                parts.append(f"Industry: {overview['industry']}")
            if "description" in overview:
                parts.append(overview["description"])
        
        if "tech_stack" in company_data and company_data["tech_stack"]:
            tech = company_data["tech_stack"]
            if "languages" in tech:
                parts.append(f"Languages: {', '.join(tech['languages'])}")
            if "frameworks" in tech:
                parts.append(f"Frameworks: {', '.join(tech['frameworks'])}")
        
        return " ".join(parts)
