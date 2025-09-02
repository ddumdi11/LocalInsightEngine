"""
Entity extractor for Named Entity Recognition.
Simple regex-based approach for initial testing, will be enhanced with spaCy.
"""

import logging
import re
from typing import List, Optional

from ...models.text_data import EntityData

logger = logging.getLogger(__name__)


class EntityExtractor:
    """
    Extracts named entities from text.
    
    Uses simple regex patterns for initial implementation.
    Will be enhanced with spaCy for production use.
    """
    
    def __init__(self):
        # German patterns
        self.german_patterns = {
            'PERSON': [
                r'\b[A-ZÄÖÜ][a-zäöüß]+\s+[A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)?\b',  # Names
                r'\b(?:Herr|Frau|Dr\.|Prof\.|Professor)\s+[A-ZÄÖÜ][a-zäöüß]+\b',  # Titles
            ],
            'ORG': [
                r'\b[A-ZÄÖÜ][a-zäöüß]*(?:\s+[A-ZÄÖÜ][a-zäöüß]*)*\s+(?:GmbH|AG|eV|e\.V\.|KG|OHG|SE)\b',
                r'\b(?:Universität|Hochschule|Institut|Gesellschaft|Verein|Stiftung)\s+[A-ZÄÖÜ][a-zäöüß]+\b',
            ],
            'LOC': [
                r'\b(?:Deutschland|Österreich|Schweiz|Berlin|München|Hamburg|Wien|Zürich)\b',
                r'\b[A-ZÄÖÜ][a-zäöüß]+(?:stadt|berg|burg|heim|hausen|dorf|tal)\b',
            ],
            'MISC': [
                r'\b(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s+\d{4}\b',
                r'\b\d{1,2}\.\s*(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\s+\d{4}\b',
            ]
        }
        
        # English patterns  
        self.english_patterns = {
            'PERSON': [
                r'\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b',  # Names
                r'\b(?:Mr\.|Mrs\.|Dr\.|Prof\.|Professor)\s+[A-Z][a-z]+\b',  # Titles
            ],
            'ORG': [
                r'\b[A-Z][a-z]*(?:\s+[A-Z][a-z]*)*\s+(?:Inc\.|Corp\.|LLC|Ltd\.|Company|Corporation|University|Institute)\b',
                r'\b(?:University|College|Institute|Foundation|Association)\s+of\s+[A-Z][a-z]+\b',
            ],
            'GPE': [  # Geopolitical entities
                r'\b(?:United States|Germany|France|England|China|Japan|Canada|Australia)\b',
                r'\b(?:New York|Los Angeles|London|Paris|Berlin|Tokyo|Sydney)\b',
            ],
            'DATE': [
                r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
                r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            ]
        }
        
        # Common entities to exclude (too generic)
        self.generic_exclusions = {
            'german': {'Das', 'Die', 'Der', 'Eine', 'Ein', 'Dieser', 'Diese', 'Jeder', 'Alle'},
            'english': {'The', 'This', 'That', 'Every', 'All', 'Some', 'Many'}
        }
    
    def extract_entities(self, text: str, source_paragraphs: List[int], source_pages: List[int]) -> List[EntityData]:
        """
        Extract named entities from text.
        
        Args:
            text: Text to process
            source_paragraphs: Paragraph IDs where this text originated
            source_pages: Page numbers where this text originated
            
        Returns:
            List of extracted entities
        """
        # Simple language detection
        language = self._detect_language(text)
        
        # Select appropriate patterns
        patterns = self.german_patterns if language == 'german' else self.english_patterns
        exclusions = self.generic_exclusions.get(language, set())
        
        entities = []
        
        for entity_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.finditer(pattern, text)
                
                for match in matches:
                    entity_text = match.group().strip()
                    
                    # Skip if too generic or too short
                    if entity_text in exclusions or len(entity_text) < 2:
                        continue
                    
                    # Skip if already found (avoid duplicates)
                    if any(e.text.lower() == entity_text.lower() for e in entities):
                        continue
                    
                    entity = EntityData(
                        text=entity_text,
                        label=entity_type,
                        confidence=0.8,  # Simple regex confidence
                        start_char=match.start(),
                        end_char=match.end(),
                        source_paragraph_id=source_paragraphs[0] if source_paragraphs else None,
                        source_page=source_pages[0] if source_pages else None
                    )
                    entities.append(entity)
        
        return entities
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection."""
        text_lower = text.lower()
        
        # Count German indicators
        german_words = {'und', 'der', 'die', 'das', 'ist', 'sind', 'mit', 'von', 'auf', 'für', 'dass'}
        german_count = sum(1 for word in german_words if word in text_lower)
        
        # Count English indicators
        english_words = {'and', 'the', 'is', 'are', 'with', 'from', 'on', 'for', 'that', 'this'}
        english_count = sum(1 for word in english_words if word in text_lower)
        
        return 'german' if german_count > english_count else 'english'