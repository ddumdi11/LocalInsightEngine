"""
Text processor for Layer 2 - neutralizes content and extracts key information.
LocalInsightEngine v0.1.0 - Layer 2: Processing Hub
"""

import logging
import re
from typing import List, Dict, Optional
from datetime import datetime

from ...models.document import Document
from ...models.text_data import ProcessedText, TextChunk, EntityData
from .spacy_statement_extractor import SpacyStatementExtractor
from .spacy_entity_extractor import SpacyEntityExtractor

logger = logging.getLogger(__name__)


class TextProcessor:
    """
    Layer 2: Text processing and neutralization.
    
    Takes original document content and creates neutralized, structured data
    that can be safely sent to external APIs while maintaining copyright compliance.
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.statement_extractor = SpacyStatementExtractor()
        self.entity_extractor = SpacyEntityExtractor()
        
    def process(self, document: Document) -> ProcessedText:
        """
        Process document content into neutralized chunks.
        
        Args:
            document: Original document from Layer 1
            
        Returns:
            ProcessedText with neutralized content safe for external APIs
        """
        start_time = datetime.now()
        logger.info(f"Processing document: {document.metadata.file_path}")
        
        # Split text into overlapping chunks
        chunks = self._create_chunks(document)
        
        # Process each chunk
        processed_chunks = []
        all_entities = []
        all_statements = []
        
        for chunk_data in chunks:
            processed_chunk = self._process_chunk(chunk_data, document.id)
            processed_chunks.append(processed_chunk)
            all_entities.extend(processed_chunk.entities)
            all_statements.extend(processed_chunk.key_statements)
        
        # Extract global themes and summary
        key_themes = self._extract_themes(all_statements)
        summary_statements = self._create_summary_statements(all_statements)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ProcessedText(
            source_document_id=document.id,
            chunks=processed_chunks,
            all_entities=all_entities,
            key_themes=key_themes,
            summary_statements=summary_statements,
            total_chunks=len(processed_chunks),
            total_entities=len(all_entities),
            processing_time_seconds=processing_time
        )
    
    def _create_chunks(self, document: Document) -> List[Dict]:
        """Create overlapping text chunks with source tracking."""
        chunks = []
        text = document.text_content
        
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 100 characters
                sentence_break = text.rfind('.', start, end)
                if sentence_break > start + self.chunk_size - 100:
                    end = sentence_break + 1
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                # Find which paragraphs and pages this chunk spans
                source_paragraphs = self._find_source_paragraphs(
                    start, end, document.paragraph_mapping
                )
                source_pages = self._find_source_pages(
                    start, end, document.page_mapping
                )
                
                chunks.append({
                    'id': chunk_id,
                    'text': chunk_text,
                    'char_range': (start, end),
                    'source_paragraphs': source_paragraphs,
                    'source_pages': source_pages
                })
                
                chunk_id += 1
            
            # Move forward with overlap
            start = max(start + self.chunk_size - self.chunk_overlap, start + 1)
        
        return chunks
    
    def _process_chunk(self, chunk_data: Dict, document_id) -> TextChunk:
        """Process a single chunk into neutralized content."""
        original_text = chunk_data['text']
        
        # Extract key statements (neutralized)
        key_statements = self.statement_extractor.extract_statements(original_text)
        
        # Extract entities with positions
        entities = self.entity_extractor.extract_entities(
            original_text, 
            chunk_data['source_paragraphs'],
            chunk_data['source_pages']
        )
        
        # Create neutralized content by combining key statements
        neutralized_content = self._neutralize_content(key_statements, entities)
        
        return TextChunk(
            neutralized_content=neutralized_content,
            key_statements=key_statements,
            entities=entities,
            source_document_id=document_id,
            source_paragraphs=chunk_data['source_paragraphs'],
            source_pages=chunk_data['source_pages'],
            original_char_range=chunk_data['char_range'],
            word_count=len(original_text.split())
        )
    
    def _neutralize_content(self, statements: List[str], entities: List[EntityData]) -> str:
        """
        Create neutralized content that preserves meaning without original wording.
        
        This is the core copyright compliance function - it ensures that no
        original creative expression is preserved in the output.
        """
        # Combine statements into neutral, factual representations
        neutralized_parts = []
        
        # Add factual statements
        if statements:
            neutralized_parts.append("Key factual content:")
            for i, statement in enumerate(statements[:5]):  # Limit to avoid too much detail
                neutralized_parts.append(f"- {statement}")
        
        # Add entity information
        entity_types = {}
        for entity in entities:
            if entity.label not in entity_types:
                entity_types[entity.label] = []
            if entity.text not in entity_types[entity.label]:
                entity_types[entity.label].append(entity.text)
        
        if entity_types:
            neutralized_parts.append("\nEntities mentioned:")
            for entity_type, entity_list in entity_types.items():
                neutralized_parts.append(f"- {entity_type}: {', '.join(entity_list[:3])}")  # Limit entities
        
        return "\n".join(neutralized_parts)
    
    def _find_source_paragraphs(self, start: int, end: int, paragraph_mapping: Dict) -> List[int]:
        """Find which paragraphs a text range spans."""
        source_paragraphs = []
        for para_id, (para_start, para_end) in paragraph_mapping.items():
            if not (end <= para_start or start >= para_end):  # Overlapping ranges
                source_paragraphs.append(para_id)
        return source_paragraphs
    
    def _find_source_pages(self, start: int, end: int, page_mapping: Dict) -> List[int]:
        """Find which pages a text range spans."""
        source_pages = []
        for page_num, (page_start, page_end) in page_mapping.items():
            if not (end <= page_start or start >= page_end):  # Overlapping ranges
                source_pages.append(page_num)
        return source_pages
    
    def _extract_themes(self, statements: List[str]) -> List[str]:
        """Extract high-level themes from all statements."""
        # Simple keyword-based theme extraction
        # In a more sophisticated version, this could use topic modeling
        
        themes = set()
        common_words = set()
        
        for statement in statements:
            words = re.findall(r'\b[a-zA-ZäöüÄÖÜß]{4,}\b', statement.lower())
            common_words.update(words)
        
        # Find most frequent meaningful words as themes
        word_counts = {}
        for statement in statements:
            words = re.findall(r'\b[a-zA-ZäöüÄÖÜß]{4,}\b', statement.lower())
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Get top themes (words appearing in multiple statements)
        frequent_themes = [
            word for word, count in word_counts.items() 
            if count > 1 and len(word) > 5
        ][:10]
        
        return frequent_themes
    
    def _create_summary_statements(self, all_statements: List[str]) -> List[str]:
        """Create high-level summary statements."""
        if not all_statements:
            return []
        
        # Simple approach: take the longest statements as likely summary content
        # In production, this could use more sophisticated summarization
        
        sorted_statements = sorted(all_statements, key=len, reverse=True)
        return sorted_statements[:5]  # Top 5 most substantial statements