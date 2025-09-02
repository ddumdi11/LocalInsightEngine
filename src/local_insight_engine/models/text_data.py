"""
Text processing data models for LocalInsightEngine.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EntityData(BaseModel):
    """Named entity extracted from text."""
    
    text: str
    label: str  # PERSON, ORG, GPE, etc.
    confidence: float = Field(ge=0.0, le=1.0)
    start_char: int
    end_char: int
    
    # Source tracking for copyright compliance
    source_paragraph_id: Optional[int] = None
    source_page: Optional[int] = None


class TextChunk(BaseModel):
    """A chunk of processed text with neutralized content."""
    
    id: UUID = Field(default_factory=uuid4)
    
    # Neutralized content (safe to send to external APIs)
    neutralized_content: str
    key_statements: List[str] = Field(default_factory=list)
    entities: List[EntityData] = Field(default_factory=list)
    
    # Source tracking (stays local)
    source_document_id: UUID
    source_paragraphs: List[int] = Field(default_factory=list)
    source_pages: List[int] = Field(default_factory=list)
    original_char_range: tuple[int, int]
    
    # Processing metadata
    processing_timestamp: datetime = Field(default_factory=datetime.now)
    word_count: int = 0
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }


class ProcessedText(BaseModel):
    """
    Complete processed text output from Layer 2 (processing_hub).
    
    Contains all neutralized data that can be safely sent to external APIs,
    along with mapping back to original sources.
    """
    
    id: UUID = Field(default_factory=uuid4)
    source_document_id: UUID
    
    # Processed chunks
    chunks: List[TextChunk] = Field(default_factory=list)
    
    # Global entities and statements
    all_entities: List[EntityData] = Field(default_factory=list)
    key_themes: List[str] = Field(default_factory=list)
    summary_statements: List[str] = Field(default_factory=list)
    
    # Processing statistics
    total_chunks: int = 0
    total_entities: int = 0
    processing_time_seconds: float = 0.0
    
    created_at: datetime = Field(default_factory=datetime.now)
    
    def get_entities_by_type(self, entity_type: str) -> List[EntityData]:
        """Get all entities of a specific type."""
        return [entity for entity in self.all_entities if entity.label == entity_type]
    
    def get_chunks_for_page(self, page_number: int) -> List[TextChunk]:
        """Get all chunks that contain content from a specific page."""
        return [
            chunk for chunk in self.chunks 
            if page_number in chunk.source_pages
        ]
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }