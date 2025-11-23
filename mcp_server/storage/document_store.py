"""
PostgreSQL Document Store
Stores structured company data with JSONB
"""
import logging
import json
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, Column, String, JSON, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from config.settings import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


class Company(Base):
    """Company data model"""
    __tablename__ = "companies"
    
    company_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    overview = Column(JSON)
    tech_stack = Column(JSON)
    culture = Column(JSON)
    hiring_patterns = Column(JSON)
    jobs = Column(JSON)
    metadata = Column(JSON)
    last_updated = Column(DateTime, default=datetime.utcnow)
    completeness_score = Column(Float, default=0.0)


class DocumentStore:
    """PostgreSQL document store for company data"""
    
    def __init__(self):
        self.engine = None
        self.Session = None
    
    async def initialize(self):
        """Initialize database connection"""
        try:
            self.engine = create_engine(settings.postgres_url)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            logger.info("PostgreSQL document store initialized")
        except Exception as e:
            logger.error(f"Failed to initialize document store: {e}")
            raise
    
    async def get_company(self, company_name: str, fields: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Get company data"""
        session = self.Session()
        try:
            company_id = company_name.lower().replace(" ", "_")
            company = session.query(Company).filter_by(company_id=company_id).first()
            
            if not company:
                return None
            
            # Build response
            data = {
                "company_id": company.company_id,
                "name": company.name,
                "last_updated": company.last_updated.isoformat() if company.last_updated else None,
                "completeness_score": company.completeness_score
            }
            
            # Add requested fields or all fields
            if fields:
                for field in fields:
                    if hasattr(company, field):
                        data[field] = getattr(company, field)
            else:
                data.update({
                    "overview": company.overview,
                    "tech_stack": company.tech_stack,
                    "culture": company.culture,
                    "hiring_patterns": company.hiring_patterns,
                    "jobs": company.jobs,
                    "metadata": company.metadata
                })
            
            return data
            
        finally:
            session.close()
    
    async def get_company_resource(self, company_name: str, resource_type: str) -> Optional[str]:
        """Get a specific company resource as JSON string"""
        session = self.Session()
        try:
            company_id = company_name.lower().replace(" ", "_")
            company = session.query(Company).filter_by(company_id=company_id).first()
            
            if not company:
                return None
            
            # Get the requested resource
            if hasattr(company, resource_type):
                data = getattr(company, resource_type)
                return json.dumps(data, indent=2) if data else None
            
            return None
            
        finally:
            session.close()
    
    async def update_company(self, company_name: str, field: str, data: Dict[str, Any], source: str = "unknown") -> bool:
        """Update company data"""
        session = self.Session()
        try:
            company_id = company_name.lower().replace(" ", "_")
            company = session.query(Company).filter_by(company_id=company_id).first()
            
            if not company:
                # Create new company
                company = Company(
                    company_id=company_id,
                    name=company_name,
                    metadata={"sources": [source]}
                )
                session.add(company)
            
            # Update field
            if hasattr(company, field):
                setattr(company, field, data)
                company.last_updated = datetime.utcnow()
                
                # Update metadata
                if not company.metadata:
                    company.metadata = {}
                if "sources" not in company.metadata:
                    company.metadata["sources"] = []
                if source not in company.metadata["sources"]:
                    company.metadata["sources"].append(source)
                
                session.commit()
                logger.info(f"Updated {company_name}.{field}")
                return True
            
            return False
            
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update company {company_name}: {e}")
            return False
        finally:
            session.close()
    
    async def list_companies(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List all companies"""
        session = self.Session()
        try:
            companies = session.query(Company).limit(limit).all()
            return [
                {
                    "company_id": c.company_id,
                    "name": c.name,
                    "last_updated": c.last_updated.isoformat() if c.last_updated else None,
                    "completeness_score": c.completeness_score
                }
                for c in companies
            ]
        finally:
            session.close()
