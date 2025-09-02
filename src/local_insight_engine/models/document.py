"""
Document data models for LocalInsightEngine.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Metadata for a loaded document."""
    
    file_path: Path
    file_size: int
    file_format: str
    created_at: datetime = Field(default_factory=datetime.now)
    title: Optional[str] = None
    author: Optional[str] = None
    language: Optional[str] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            Path: str,
            datetime: lambda v: v.isoformat()
        }


class Document(BaseModel):
    """
    Represents a loaded document with its content and metadata.
    
    This is the output of Layer 1 (data_layer) and contains the original
    document content with location mapping for copyright compliance.
    """
    
    id: UUID = Field(default_factory=uuid4)
    metadata: DocumentMetadata
    text_content: str
    page_mapping: Dict[int, tuple[int, int]]  # page -> (start_char, end_char)
    paragraph_mapping: Dict[int, tuple[int, int]]  # paragraph -> (start_char, end_char)
    section_mapping: Dict[str, tuple[int, int]]  # section_title -> (start_char, end_char)
    
    created_at: datetime = Field(default_factory=datetime.now)
    
    def get_text_by_page(self, page_number: int) -> Optional[str]:
        """Get text content for a specific page."""
        if page_number not in self.page_mapping:
            return None
        
        start, end = self.page_mapping[page_number]
        return self.text_content[start:end]
    
    def get_text_by_paragraph(self, paragraph_id: int) -> Optional[str]:
        """Get text content for a specific paragraph."""
        if paragraph_id not in self.paragraph_mapping:
            return None
        
        start, end = self.paragraph_mapping[paragraph_id]
        return self.text_content[start:end]
    
    def find_text_location(self, text_snippet: str) -> Optional[tuple[int, int, str]]:
        """
        Find the location of a text snippet in the document.
        
        Returns:
            Tuple of (page_number, paragraph_id, location_type) if found, None otherwise
        """
        snippet_start = self.text_content.find(text_snippet)
        if snippet_start == -1:
            return None
        
        # Find page
        page_num = None
        for page, (start, end) in self.page_mapping.items():
            if start <= snippet_start < end:
                page_num = page
                break
        
        # Find paragraph
        paragraph_id = None
        for para_id, (start, end) in self.paragraph_mapping.items():
            if start <= snippet_start < end:
                paragraph_id = para_id
                break
        
        return page_num, paragraph_id, "exact_match"
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
            Path: str
        }