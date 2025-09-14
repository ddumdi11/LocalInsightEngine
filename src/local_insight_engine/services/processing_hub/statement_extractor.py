"""
Statement extractor for neutralizing content while preserving factual meaning.
Supports German and English text processing.
"""

import logging
import re
from typing import List, Dict

logger = logging.getLogger(__name__)


class StatementExtractor:
    """
    Extracts factual statements and neutralizes them for copyright compliance.
    
    The key function is to preserve factual content while removing the original
    creative expression and wording that would be protected by copyright.
    
    Supports both German and English text.
    """
    
    def __init__(self):
        # German patterns for different types of statements
        self.german_fact_patterns = [
            r'(?:ist|sind|war|waren|hat|haben|hatte|hatten)\s+',  # Sein/haben statements
            r'(?:zeigt|demonstriert|deutet|weist|belegt|beweist)\s+',  # Evidence statements
            r'(?:laut|gemäß|nach|basierend auf|Studien zeigen|Forschung zeigt)\s+',  # Attribution
            r'(?:Studien|Daten|Ergebnisse|Befunde|Untersuchungen)\s+(?:zeigen|deuten|belegen)',  # Research
            r'(?:Forscher|Wissenschaftler|Experten)\s+(?:fanden|entdeckten|stellten fest)',  # Researcher findings
        ]
        
        # English patterns
        self.english_fact_patterns = [
            r'(?:is|are|was|were|has|have|had)\s+',  # State-of-being statements
            r'(?:shows|demonstrates|indicates|suggests|reveals|proves)\s+',  # Evidence statements  
            r'(?:according to|based on|research shows|studies show)\s+',  # Attribution statements
            r'(?:studies|data|results|findings|research)\s+(?:show|indicate|suggest|reveal)',  # Research statements
        ]
        
        # German factual indicators
        self.german_factual_indicators = {
            'forschung', 'studie', 'studien', 'daten', 'beweis', 'beweise', 'befund', 'befunde',
            'ergebnis', 'ergebnisse', 'analyse', 'statistik', 'bericht', 'untersuchung', 'umfrage',
            'experiment', 'beobachtung', 'messung', 'berechnung', 'wissenschaft', 'forscher',
            'experte', 'experten', 'fachmann', 'spezialist', 'gelehrte'
        }
        
        # English factual indicators
        self.english_factual_indicators = {
            'research', 'study', 'studies', 'data', 'evidence', 'findings', 'results',
            'analysis', 'statistics', 'report', 'investigation', 'survey', 'experiment',
            'observation', 'measurement', 'calculation', 'science', 'researcher', 'expert'
        }
        
        # German transition words
        self.german_key_transitions = {
            'jedoch', 'allerdings', 'dennoch', 'trotzdem', 'daher', 'deshalb', 'folglich',
            'außerdem', 'zusätzlich', 'darüber hinaus', 'ferner', 'weiterhin', 'insbesondere',
            'besonders', 'wichtig', 'bedeutsam', 'wesentlich', 'grundlegend', 'letztendlich'
        }
        
        # English transition words
        self.english_key_transitions = {
            'however', 'therefore', 'consequently', 'furthermore', 'moreover',
            'additionally', 'specifically', 'particularly', 'importantly',
            'significantly', 'notably', 'essentially', 'ultimately'
        }
        
        # German subjective indicators to avoid
        self.german_subjective_indicators = {
            'ich denke', 'ich glaube', 'meiner meinung', 'meiner ansicht', 'ich fühle',
            'persönlich', 'scheint', 'wirkt', 'könnte sein', 'möglicherweise', 'vielleicht',
            'wahrscheinlich', 'vermutlich'
        }
        
        # English subjective indicators to avoid  
        self.english_subjective_indicators = {
            'i think', 'i believe', 'in my opinion', 'i feel', 'personally',
            'seems like', 'appears to be', 'might be', 'could be', 'perhaps',
            'probably', 'likely'
        }
    
    def extract_statements(self, text: str) -> List[str]:
        """
        Extract and neutralize key factual statements from text.
        
        Args:
            text: Original text content (German or English)
            
        Returns:
            List of neutralized factual statements
        """
        # Detect language
        language = self._detect_language(text)
        
        sentences = self._split_into_sentences(text)
        statements = []
        
        for sentence in sentences:
            # Clean and normalize sentence
            cleaned = self._clean_sentence(sentence)
            if not cleaned or len(cleaned.split()) < 5:  # Skip very short sentences
                continue
            
            # Check if sentence contains factual content
            if self._is_factual_sentence(cleaned, language):
                neutralized = self._neutralize_statement(cleaned, language)
                if neutralized and neutralized not in statements:
                    statements.append(neutralized)
        
        return statements
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection based on common words."""
        text_lower = text.lower()
        
        # Count German indicators
        german_words = {'und', 'der', 'die', 'das', 'ist', 'sind', 'mit', 'von', 'auf', 'für', 'sich', 'dass'}
        german_count = sum(1 for word in german_words if word in text_lower)
        
        # Count English indicators
        english_words = {'and', 'the', 'is', 'are', 'with', 'from', 'on', 'for', 'that', 'this'}
        english_count = sum(1 for word in english_words if word in text_lower)
        
        return 'german' if german_count > english_count else 'english'
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting - could be enhanced with nltk or spaCy
        sentences = re.split(r'[.!?]+', text)
        
        # Clean up sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:  # Minimum length filter
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def _clean_sentence(self, sentence: str) -> str:
        """Clean and normalize a sentence."""
        # Remove extra whitespace
        sentence = re.sub(r'\s+', ' ', sentence).strip()
        
        # Remove common formatting artifacts
        sentence = re.sub(r'\s*-\s*', ' ', sentence)  # Remove dashes
        sentence = re.sub(r'\([^)]*\)', '', sentence)  # Remove parenthetical content
        
        return sentence
    
    def _is_factual_sentence(self, sentence: str, language: str) -> bool:
        """Determine if a sentence likely contains factual content."""
        sentence_lower = sentence.lower()
        
        # Select language-specific patterns
        if language == 'german':
            factual_indicators = self.german_factual_indicators
            fact_patterns = self.german_fact_patterns
            key_transitions = self.german_key_transitions
            subjective_indicators = self.german_subjective_indicators
        else:
            factual_indicators = self.english_factual_indicators
            fact_patterns = self.english_fact_patterns
            key_transitions = self.english_key_transitions
            subjective_indicators = self.english_subjective_indicators
        
        # Check for factual indicators
        has_factual_words = any(
            indicator in sentence_lower 
            for indicator in factual_indicators
        )
        
        # Check for factual patterns
        has_factual_pattern = any(
            re.search(pattern, sentence_lower) 
            for pattern in fact_patterns
        )
        
        # Check for key transition words
        has_key_transition = any(
            transition in sentence_lower 
            for transition in key_transitions
        )
        
        # Check for numbers/percentages (often factual)
        has_numbers = bool(re.search(r'\d+(?:[.,]\d+)?%?', sentence))
        
        # Avoid purely subjective content
        is_subjective = any(
            indicator in sentence_lower 
            for indicator in subjective_indicators
        )
        
        return (has_factual_words or has_factual_pattern or has_key_transition or has_numbers) and not is_subjective
    
    def _neutralize_statement(self, statement: str, language: str) -> str:
        """
        Neutralize a statement to remove original creative expression.
        """
        neutralized = statement
        
        # Language-specific neutralization
        if language == 'german':
            # Replace first-person references in German
            neutralized = re.sub(r'\b(ich|mein|mir|mich)\b', 'der Autor', neutralized, flags=re.IGNORECASE)
            neutralized = re.sub(r'\bwir\b', 'die Forscher', neutralized, flags=re.IGNORECASE)
            
            # German subjective language to objective
            german_replacements = {
                r'\bschön\b': 'bemerkenswert',
                r'\bunglaublich\b': 'bedeutsam',
                r'\berstaunlich\b': 'beachtlich',
                r'\boffensichtlich\b': 'erkennbar',
                r'\bklar\b': 'ersichtlich',
                r'\beinfach\b': '',
                r'\bnur\b': '',
                r'\bwirklich\b': '',
                r'\bsehr\b': 'besonders',
            }
            
            for pattern, replacement in german_replacements.items():
                neutralized = re.sub(pattern, replacement, neutralized, flags=re.IGNORECASE)
        
        else:  # English
            # Replace first-person references in English
            neutralized = re.sub(r'\b(I|my|me|mine)\b', 'the author', neutralized, flags=re.IGNORECASE)
            neutralized = re.sub(r'\bwe\b', 'the researchers', neutralized, flags=re.IGNORECASE)
            
            # English subjective language to objective
            english_replacements = {
                r'\bbeautiful\b': 'aesthetically notable',
                r'\bincredible\b': 'significant',
                r'\bamazing\b': 'remarkable',
                r'\bobviously\b': 'evidently',
                r'\bclearly\b': 'apparently',
                r'\bsimply\b': '',
                r'\bjust\b': '',
                r'\breally\b': '',
                r'\bvery\b': 'particularly',
            }
            
            for pattern, replacement in english_replacements.items():
                neutralized = re.sub(pattern, replacement, neutralized, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        neutralized = re.sub(r'\s+', ' ', neutralized).strip()
        
        # Ensure proper capitalization and punctuation
        if neutralized:
            neutralized = neutralized[0].upper() + neutralized[1:]
            if not neutralized.endswith('.'):
                neutralized += '.'
        
        # Final check: make sure it's different enough from original
        if self._is_sufficiently_neutralized(statement, neutralized):
            return neutralized
        else:
            return self._create_abstract_version(statement, language)
    
    def _is_sufficiently_neutralized(self, original: str, neutralized: str) -> bool:
        """Check if neutralized version is sufficiently different from original."""
        original_words = set(original.lower().split())
        neutralized_words = set(neutralized.lower().split())
        
        if len(original_words) == 0:
            return False
        
        common_words = original_words.intersection(neutralized_words)
        similarity = len(common_words) / len(original_words)
        
        return similarity < 0.7  # At least 30% different
    
    def _create_abstract_version(self, statement: str, language: str) -> str:
        """Create a highly abstract version of the statement with NO original content."""
        # CRITICAL: This method must NEVER include any original words or phrases
        # to ensure copyright compliance and prevent canary phrases from leaking through

        # Analyze statement characteristics without using original words
        has_numbers = bool(re.search(r'\d+(?:[.,]\d+)?%?', statement))
        has_research_indicators = False
        has_technical_content = False

        statement_lower = statement.lower()

        # Language-specific abstract fallbacks - NO ORIGINAL CONTENT
        if language == 'german':
            research_keywords = {'studie', 'forschung', 'daten', 'analyse', 'untersuchung', 'befund'}
            technical_keywords = {'system', 'methode', 'verfahren', 'prozess', 'technologie', 'algorithmus'}

            has_research_indicators = any(keyword in statement_lower for keyword in research_keywords)
            has_technical_content = any(keyword in statement_lower for keyword in technical_keywords)

            # Abstract templates with NO original content
            if has_numbers and has_research_indicators:
                return "Der Inhalt enthält quantitative Forschungsergebnisse."
            elif has_research_indicators:
                return "Der Inhalt beschreibt wissenschaftliche Erkenntnisse."
            elif has_technical_content:
                return "Der Inhalt behandelt technische Aspekte."
            elif has_numbers:
                return "Der Inhalt enthält numerische Informationen."
            else:
                return "Der Inhalt vermittelt sachliche Informationen."
        else:
            research_keywords = {'study', 'research', 'data', 'analysis', 'investigation', 'findings'}
            technical_keywords = {'system', 'method', 'process', 'technology', 'algorithm', 'technique'}

            has_research_indicators = any(keyword in statement_lower for keyword in research_keywords)
            has_technical_content = any(keyword in statement_lower for keyword in technical_keywords)

            # Abstract templates with NO original content
            if has_numbers and has_research_indicators:
                return "Content contains quantitative research findings."
            elif has_research_indicators:
                return "Content describes scientific insights."
            elif has_technical_content:
                return "Content addresses technical aspects."
            elif has_numbers:
                return "Content contains numerical information."
            else:
                return "Content conveys factual information."