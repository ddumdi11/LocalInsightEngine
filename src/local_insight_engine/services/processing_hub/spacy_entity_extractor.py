"""
SpaCy-based entity extractor for Named Entity Recognition.
Much more accurate than regex-based approach.
"""

import logging
from typing import List, Optional
import re
import spacy
from spacy.lang.de import German
from spacy.lang.en import English

from ...models.text_data import EntityData

logger = logging.getLogger(__name__)


class SpacyEntityExtractor:
    """
    Advanced entity extractor using spaCy for German and English text.
    
    Provides much more accurate NER than simple regex patterns.
    """
    
    def __init__(self):
        self.german_nlp = None
        self.english_nlp = None
        self._load_models()
        
        # spaCy to our label mapping
        self.label_mapping = {
            'PER': 'PERSON',
            'PERSON': 'PERSON',  
            'ORG': 'ORG',
            'LOC': 'LOC',
            'GPE': 'LOC',  # Geopolitical entity -> Location
            'MISC': 'MISC',
            'DATE': 'DATE',
            'TIME': 'TIME',
            'MONEY': 'MONEY',
            'PERCENT': 'PERCENT',
            'QUANTITY': 'QUANTITY'
        }
        
        # Minimum confidence threshold (lower for testing)
        self.min_confidence = 0.3
        
        # Entities to exclude (too generic or likely errors)
        self.exclusion_patterns = {
            'german': {
                'der', 'die', 'das', 'eine', 'ein', 'und', 'oder', 'mit', 'von', 'zu', 'auf',
                'in', 'an', 'bei', 'nach', 'vor', 'über', 'unter', 'zwischen', 'durch',
                'für', 'gegen', 'ohne', 'um', 'während', 'wegen', 'trotz', 'statt'
            },
            'english': {
                'the', 'and', 'or', 'with', 'from', 'to', 'at', 'in', 'on', 'by', 'for',
                'about', 'during', 'before', 'after', 'above', 'below', 'between', 'through'
            }
        }
    
    def _load_models(self):
        """Load spaCy language models."""
        try:
            self.german_nlp = spacy.load('de_core_news_sm')
            logger.info("German model loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load German model: {e}")
            logger.info("Falling back to German language class without NER")
            self.german_nlp = German()
        
        # For now, focus on German only
        logger.info("Using German-only processing for entities")
        self.english_nlp = None
    
    def extract_entities(self, text: str, source_paragraphs: List[int], source_pages: List[int], bypass_anonymization: bool = False) -> List[EntityData]:
        """
        Extract named entities using spaCy.

        Args:
            text: Text to process
            source_paragraphs: Paragraph IDs where this text originated
            source_pages: Page numbers where this text originated
            bypass_anonymization: If True, skips anonymization for factual content
            
        Returns:
            List of extracted entities with high confidence
        """
        # Use German model for now (we can expand later)
        nlp = self.german_nlp
        
        if nlp is None:
            logger.warning("No NLP model available, returning empty entity list")
            return []
        
        try:
            # Process text with spaCy
            doc = nlp(text)
            entities = []
            
            for ent in doc.ents:
                # Skip if too short or generic
                if len(ent.text.strip()) < 2:
                    continue
                
                # Skip common words (using German exclusions for now)
                exclusions = self.exclusion_patterns.get('german', set())
                if ent.text.lower().strip() in exclusions:
                    continue
                
                # Map spaCy label to our labels
                our_label = self.label_mapping.get(ent.label_, ent.label_)
                
                # Calculate confidence (spaCy doesn't provide confidence scores directly)
                # We use a heuristic based on entity length and type
                confidence = self._calculate_confidence(ent)
                
                if confidence >= self.min_confidence:
                    # CRITICAL: Neutralize suspicious identifiers for copyright compliance
                    # BUT: Skip neutralization in factual content mode
                    entity_text = ent.text.strip()
                    if bypass_anonymization:
                        neutralized_text = entity_text  # Keep original in factual mode
                    else:
                        neutralized_text = self._neutralize_suspicious_identifiers(entity_text)

                    entity = EntityData(
                        text=neutralized_text,
                        label=our_label,
                        confidence=confidence,
                        start_char=ent.start_char,
                        end_char=ent.end_char,
                        source_paragraph_id=source_paragraphs[0] if source_paragraphs else None,
                        source_page=source_pages[0] if source_pages else None
                    )
                    entities.append(entity)
            
            # Remove duplicates
            entities = self._deduplicate_entities(entities)
            
            logger.debug(f"Extracted {len(entities)} entities from {len(text)} characters of text")
            return entities
            
        except Exception as e:
            logger.error(f"Error during spaCy entity extraction: {e}")
            return []
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection based on common words."""
        text_lower = text.lower()
        
        # Count German indicators
        german_words = {
            'und', 'der', 'die', 'das', 'ist', 'sind', 'mit', 'von', 'auf', 'für', 
            'sich', 'dass', 'nicht', 'auch', 'werden', 'haben', 'sein', 'können'
        }
        german_count = sum(1 for word in german_words if f' {word} ' in f' {text_lower} ')
        
        # Count English indicators
        english_words = {
            'and', 'the', 'is', 'are', 'with', 'from', 'on', 'for', 'that', 'this',
            'not', 'will', 'have', 'be', 'can', 'would', 'could', 'should'
        }
        english_count = sum(1 for word in english_words if f' {word} ' in f' {text_lower} ')
        
        return 'german' if german_count > english_count else 'english'
    
    def _calculate_confidence(self, ent) -> float:
        """
        Calculate confidence score for an entity.
        
        spaCy doesn't provide confidence scores directly, so we use heuristics:
        - Longer entities are generally more reliable
        - Certain entity types are more reliable
        - Entities with mixed case are more likely to be real names
        """
        base_confidence = 0.7
        
        # Length bonus
        length_bonus = min(0.2, len(ent.text) * 0.02)
        
        # Type bonus
        type_bonus = {
            'PERSON': 0.1,
            'ORG': 0.1, 
            'PER': 0.1,
            'LOC': 0.05,
            'GPE': 0.05,
            'DATE': 0.15,
            'MONEY': 0.15
        }.get(ent.label_, 0.0)
        
        # Capitalization bonus (proper nouns)
        cap_bonus = 0.1 if ent.text[0].isupper() and len(ent.text) > 1 else 0.0
        
        # Contains numbers penalty (often extraction errors)
        number_penalty = -0.1 if any(c.isdigit() for c in ent.text) else 0.0
        
        confidence = base_confidence + length_bonus + type_bonus + cap_bonus + number_penalty
        return min(1.0, max(0.0, confidence))
    
    def _deduplicate_entities(self, entities: List[EntityData]) -> List[EntityData]:
        """Remove duplicate entities based on text and label."""
        seen = set()
        unique_entities = []
        
        for entity in entities:
            key = (entity.text.lower(), entity.label)
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities

    def _neutralize_suspicious_identifiers(self, entity_text: str) -> str:
        """
        Neutralize suspicious test/canary identifiers while preserving legitimate terms.

        This targets obvious test patterns like CANARY_*, TEST_*, etc. while preserving
        scientific terms (Phosphatidylserin), product names (Playstation 4), vitamins, etc.

        Args:
            entity_text: Original entity text

        Returns:
            Neutralized text or original if it appears to be legitimate
        """
        # Whitelist for legitimate scientific and health terms
        legitimate_patterns = [
            # Vitamins and nutrients
            r'^(Vitamin\s+)?[ABCDEK]\d{1,2}$',  # B3, B12, D3, etc.
            r'^(Vitamin\s+)?(Niacin|Thiamin|Riboflavin|Biotin|Folat|Cobalamin)$',
            r'^(Magnesium|Calcium|Kalium|Eisen|Zink|Selen)$',
            # Common health/nutrition terms
            r'^(Phosphatidyl\w+|Omega-?\d+|Aminosäure\w*)$',
            # Product names and brands (common patterns)
            r'^[A-Z][a-z]+\s+\d+$',  # "Playstation 4", "iPhone 12"
        ]

        # Check if entity matches legitimate patterns first
        for pattern in legitimate_patterns:
            if re.match(pattern, entity_text, re.IGNORECASE):
                return entity_text  # Preserve legitimate terms
        # Patterns that indicate test/canary/debug identifiers
        # pattern, flags
        suspicious_patterns = [
            (r'^.*_(CANARY|TEST|MARKER|DEBUG)_.*$', re.IGNORECASE),
            (r'^(CANARY|TEST|MARKER|DEBUG)_.*$', re.IGNORECASE),
            (r'^.*_(CANARY|TEST|MARKER|DEBUG)$', re.IGNORECASE),
            # Strict ALL-CAPS/underscore run; case-sensitive on purpose
            (r'^[A-Z_]{15,}$', 0),
            (r'^[A-Z]+_[A-Z]+_[A-Z]+_[0-9]+$', re.IGNORECASE),
            (r'^[A-Z]+_[A-Z]+_[0-9]{6,}$', re.IGNORECASE),
            # Optional: long opaque alphanumeric runs (reduce false positives with higher threshold)
            (r'^[A-Za-z0-9]{24,}$', re.IGNORECASE),
        ]

        # Check if entity matches suspicious patterns
        for pattern, flags in suspicious_patterns:
            if re.match(pattern, entity_text, flags):
                # Generate neutral replacement based on entity characteristics
                if 'CANARY' in entity_text.upper():
                    return "Test-Identifikator"
                elif 'TEST' in entity_text.upper():
                    return "Test-Element"
                elif 'MARKER' in entity_text.upper():
                    return "Markierung"
                elif 'DEBUG' in entity_text.upper():
                    return "Debug-Element"
                elif len(entity_text) > 20:
                    return "Langer Identifikator"
                elif '_' in entity_text and entity_text.isupper():
                    return "System-Identifikator"
                else:
                    return "Unbekannter Identifikator"

        # If no suspicious pattern matches, return original (preserve legitimate terms)
        return entity_text