"""
SpaCy-based statement extractor for better sentence analysis and neutralization.
"""

import logging
from typing import List, Set
import re
import spacy
from spacy.lang.de import German
from spacy.lang.en import English

logger = logging.getLogger(__name__)


class SpacyStatementExtractor:
    """
    Advanced statement extractor using spaCy for better sentence parsing.
    
    Provides much more accurate sentence detection and linguistic analysis
    compared to simple regex-based approach.
    """
    
    def __init__(self):
        self.german_nlp = None
        self.english_nlp = None
        self._load_models()
        
        # German factual indicators
        self.german_factual_indicators = {
            'forschung', 'studie', 'studien', 'daten', 'beweis', 'beweise', 'befund', 'befunde',
            'ergebnis', 'ergebnisse', 'analyse', 'statistik', 'bericht', 'untersuchung', 'umfrage',
            'experiment', 'beobachtung', 'messung', 'berechnung', 'wissenschaft', 'forscher',
            'experte', 'experten', 'fachmann', 'spezialist', 'gelehrte', 'theorie', 'hypothese',
            'methode', 'verfahren', 'prozess', 'system', 'modell', 'konzept', 'prinzip'
        }
        
        # English factual indicators
        self.english_factual_indicators = {
            'research', 'study', 'studies', 'data', 'evidence', 'findings', 'results',
            'analysis', 'statistics', 'report', 'investigation', 'survey', 'experiment',
            'observation', 'measurement', 'calculation', 'science', 'researcher', 'expert',
            'theory', 'hypothesis', 'method', 'process', 'system', 'model', 'concept', 'principle'
        }
        
        # German subjective indicators to filter out
        self.german_subjective_indicators = {
            'ich denke', 'ich glaube', 'meiner meinung', 'meiner ansicht', 'ich fühle',
            'persönlich', 'scheint', 'wirkt', 'könnte sein', 'möglicherweise', 'vielleicht',
            'wahrscheinlich', 'vermutlich', 'anscheinend', 'offenbar'
        }
        
        # English subjective indicators
        self.english_subjective_indicators = {
            'i think', 'i believe', 'in my opinion', 'i feel', 'personally',
            'seems like', 'appears to be', 'might be', 'could be', 'perhaps',
            'probably', 'likely', 'apparently', 'presumably'
        }
    
    def _load_models(self):
        """Load spaCy language models."""
        try:
            self.german_nlp = spacy.load('de_core_news_sm')
            logger.info("German spaCy model loaded successfully")
        except Exception as e:
            logger.warning(f"German spaCy model not available, using basic tokenizer: {e}")
            self.german_nlp = German()
            # Add sentencizer for sentence boundary detection
            self.german_nlp.add_pipe('sentencizer')
        
        # For now, don't try to load English model - focus on German
        logger.info("Using German-only processing")
        self.english_nlp = German()
        self.english_nlp.add_pipe('sentencizer')
    
    def extract_statements(self, text: str) -> List[str]:
        """
        Extract and neutralize key factual statements from text using spaCy.
        
        Args:
            text: Original text content
            
        Returns:
            List of neutralized factual statements
        """
        if not text or not text.strip():
            return []
        
        # Detect language
        language = self._detect_language(text)
        nlp = self.german_nlp if language == 'german' else self.english_nlp
        
        if nlp is None:
            return []
        
        try:
            # Process text with spaCy for better sentence segmentation
            doc = nlp(text)
            statements = []
            
            for sent in doc.sents:
                sentence_text = sent.text.strip()
                
                # Skip very short sentences
                if len(sentence_text.split()) < 5:
                    continue
                
                # Check if sentence contains factual content
                if self._is_factual_sentence(sent, language):
                    neutralized = self._neutralize_statement(sentence_text, language)
                    if neutralized and neutralized not in statements:
                        statements.append(neutralized)
            
            return statements[:20]  # Limit to most relevant statements
            
        except Exception as e:
            logger.error(f"Error in spaCy statement extraction: {e}")
            return []
    
    def _detect_language(self, text: str) -> str:
        """Detect language of the text."""
        text_lower = text.lower()
        
        german_words = {'und', 'der', 'die', 'das', 'ist', 'sind', 'mit', 'von', 'auf', 'für', 'dass'}
        german_count = sum(1 for word in german_words if f' {word} ' in f' {text_lower} ')
        
        english_words = {'and', 'the', 'is', 'are', 'with', 'from', 'on', 'for', 'that'}
        english_count = sum(1 for word in english_words if f' {text_lower} ')
        
        return 'german' if german_count > english_count else 'english'
    
    def _is_factual_sentence(self, sent, language: str) -> bool:
        """
        Determine if a sentence likely contains factual content using spaCy analysis.
        """
        sentence_text = sent.text.lower()
        
        # Select language-specific indicators
        if language == 'german':
            factual_indicators = self.german_factual_indicators
            subjective_indicators = self.german_subjective_indicators
        else:
            factual_indicators = self.english_factual_indicators
            subjective_indicators = self.english_subjective_indicators
        
        # Check for factual indicators
        has_factual_words = any(
            indicator in sentence_text 
            for indicator in factual_indicators
        )
        
        # Check for entities (often indicate factual content)
        has_entities = len(sent.ents) > 0
        
        # Check for numbers/dates (often factual)
        has_numbers = any(token.like_num or token.ent_type_ in ['DATE', 'MONEY', 'PERCENT'] for token in sent)
        
        # Check for verbs that indicate facts
        factual_verbs = {'zeigt', 'belegt', 'beweist', 'demonstrates', 'shows', 'proves', 'indicates'}
        has_factual_verbs = any(token.lemma_ in factual_verbs for token in sent)
        
        # Avoid purely subjective content
        is_subjective = any(
            indicator in sentence_text 
            for indicator in subjective_indicators
        )
        
        # Score the sentence
        factual_score = sum([
            has_factual_words * 2,
            has_entities * 1,
            has_numbers * 1,
            has_factual_verbs * 2
        ])
        
        return factual_score >= 2 and not is_subjective
    
    def _neutralize_statement(self, statement: str, language: str) -> str:
        """
        Neutralize a statement to remove original creative expression.
        """
        # Basic neutralization (could be enhanced)
        neutralized = statement
        
        if language == 'german':
            # Replace first-person references
            neutralized = neutralized.replace('ich', 'der Autor')
            neutralized = neutralized.replace('mein', 'des Autors')
            neutralized = neutralized.replace('wir', 'die Forscher')
            
            # Remove subjective modifiers
            subjective_words = ['sehr', 'wirklich', 'ziemlich', 'einfach', 'nur', 'besonders']
            for word in subjective_words:
                neutralized = neutralized.replace(f' {word} ', ' ')
        else:
            # English neutralization
            neutralized = neutralized.replace(' I ', ' the author ')
            neutralized = neutralized.replace(' my ', ' the author\'s ')
            neutralized = neutralized.replace(' we ', ' the researchers ')
            
            subjective_words = ['very', 'really', 'quite', 'simply', 'just', 'particularly']
            for word in subjective_words:
                neutralized = neutralized.replace(f' {word} ', ' ')
        
        # Clean up extra spaces
        neutralized = ' '.join(neutralized.split())
        
        # Ensure proper capitalization and punctuation
        if neutralized:
            neutralized = neutralized[0].upper() + neutralized[1:]
            if not neutralized.endswith('.'):
                neutralized += '.'
        
        # Check if neutralization is sufficient - if not, create abstract version
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