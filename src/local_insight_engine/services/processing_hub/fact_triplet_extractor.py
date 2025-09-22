"""
FactTripletExtractor - Core component for Semantic Triples Pipeline.
Extracts structured fact relationships from natural language text.
"""

import logging
import time
from typing import List, Dict, Set, Optional, Tuple
import spacy
from spacy.tokens import Doc, Token, Span

from ...models.semantic_triples import FactTriplet, SemanticTripleSet
from ...models.text_data import EntityData
from .entity_equivalence_mapper import EntityEquivalenceMapper

logger = logging.getLogger(__name__)


class FactTripletExtractor:
    """
    Extracts semantic triples (Subject-Predicate-Object) from text using spaCy dependency parsing.

    This replaces content neutralization for scientific texts with structured fact extraction.
    Perfect for answering specific questions like "What does Vitamin B3 do?"
    """

    def __init__(self) -> None:
        self.nlp = None
        self._load_spacy_model()

        # Entity Equivalence Mapper for scientific name resolution
        self.entity_mapper = EntityEquivalenceMapper()

        # Multi-language dependency label mapping
        self.dependency_labels = {
            'german': {
                'subject': ['sb', 'mo'],             # Subjekt + Modaladverbial (oft Subject in DE)
                'object': ['oa', 'og', 'od', 'sb'], # Objekt + manchmal auch sb bei verwirrten Parses
                'prep_object': ['op'],               # Präpositionalobjekt
                'copula': ['pd'],                    # Prädikativ
                'compound': ['cj', 'cm'],            # Konjunkt, Komparativ Modifier
                'modifier': ['nk', 'ag', 'pnc']      # Noun Kernel, Attribut Genitiv, Punctuation/Names
            },
            'english': {
                'subject': ['nsubj', 'nsubjpass', 'csubj'],
                'object': ['dobj', 'pobj', 'attr', 'oprd'],
                'prep_object': ['pobj'],
                'copula': ['attr'],
                'compound': ['compound'],
                'modifier': ['amod', 'det']
            }
        }

        # Current language (auto-detected)
        self.current_language = 'german'  # Default to German

        # Predicate normalization mapping
        self.predicate_mapping = {
            # Scientific relationships
            'unterstützen': 'supports',
            'unterstützt': 'supports',
            'fördern': 'promotes',
            'fördert': 'promotes',
            'hilft': 'helps',
            'helfen': 'helps',
            'verbessert': 'improves',
            'steigert': 'increases',
            'senkt': 'decreases',
            'reduziert': 'reduces',
            'verhindert': 'prevents',
            'verursacht': 'causes',
            'bewirkt': 'causes',

            # Properties
            'ist': 'is_type_of',
            'enthält': 'contains',
            'besteht aus': 'consists_of',
            'hat': 'has_property',
            'besitzt': 'has_property',

            # Location/occurrence
            'kommt vor in': 'occurs_in',
            'findet sich in': 'found_in',
            'befindet sich in': 'located_in',

            # Quantitative
            'benötigt': 'requires',
            'braucht': 'requires',
            'verwendet': 'uses',
            'nutzt': 'uses',

            # Temporal
            'passiert': 'happens',
            'geschieht': 'occurs',
            'dauert': 'lasts'
        }

        # Subject/Object normalization for scientific terms
        self.entity_normalization = {
            # Vitamins
            'Vitamin B3': 'Vitamin_B3',
            'Vitamin B-3': 'Vitamin_B3',
            'Niacin': 'Vitamin_B3',
            'Nikotinamid': 'Vitamin_B3',
            'Nicotinamid': 'Vitamin_B3',

            # Body systems
            'Energiestoffwechsel': 'Energy_Metabolism',
            'Nervensystem': 'Nervous_System',
            'Immunsystem': 'Immune_System',
            'Verdauungssystem': 'Digestive_System',

            # General concepts
            'Körper': 'Human_Body',
            'Organismus': 'Human_Body',
            'Stoffwechsel': 'Metabolism'
        }

        # Confidence thresholds
        self.min_confidence = 0.4
        self.high_confidence_threshold = 0.8

    def _load_spacy_model(self) -> None:
        """Load spaCy model for dependency parsing."""
        try:
            self.nlp = spacy.load('de_core_news_lg')
            logger.info("German spaCy model loaded for fact extraction")
        except Exception as e:
            logger.error(f"Could not load German spaCy model: {e}")
            logger.warning("Fact triplet extraction will not be available")

    def extract_triples_from_chunk(
        self,
        text: str,
        chunk_id: str,
        document_id: str,
        source_paragraphs: List[int],
        source_pages: List[int],
        original_char_range: tuple,
        word_count: int
    ) -> SemanticTripleSet:
        """
        Extract semantic triples from a text chunk.

        Args:
            text: Original text content
            chunk_id: Unique identifier for this chunk
            document_id: Source document identifier
            source_paragraphs: Paragraph IDs this chunk spans
            source_pages: Page numbers this chunk spans
            original_char_range: Character range in original document
            word_count: Number of words in chunk

        Returns:
            SemanticTripleSet with extracted facts
        """
        start_time = time.time()

        if not self.nlp:
            logger.warning("No spaCy model available for fact extraction")
            return self._create_empty_triple_set(
                chunk_id, document_id, source_paragraphs, source_pages,
                original_char_range, word_count, time.time() - start_time
            )

        try:
            # Process text with spaCy
            doc = self.nlp(text)
            triples = []
            successful = 0
            failed = 0

            # Process each sentence
            for sent in doc.sents:
                sentence_triples = self._extract_triples_from_sentence(sent)
                if sentence_triples:
                    triples.extend(sentence_triples)
                    successful += 1
                else:
                    failed += 1

            # Remove duplicates and low-confidence triples
            triples = self._deduplicate_and_filter_triples(triples)

            processing_time = time.time() - start_time

            logger.debug(f"Extracted {len(triples)} triples from chunk {chunk_id} "
                        f"in {processing_time:.3f}s")

            return SemanticTripleSet(
                triples=triples,
                source_chunk_id=chunk_id,
                source_document_id=document_id,
                source_paragraphs=source_paragraphs,
                source_pages=source_pages,
                original_char_range=original_char_range,
                word_count=word_count,
                extraction_time_seconds=processing_time,
                total_sentences_processed=len(list(doc.sents)),
                successful_extractions=successful,
                failed_extractions=failed
            )

        except Exception as e:
            logger.error(f"Error extracting triples from chunk {chunk_id}: {e}")
            return self._create_empty_triple_set(
                chunk_id, document_id, source_paragraphs, source_pages,
                original_char_range, word_count, time.time() - start_time
            )

    def _extract_triples_from_sentence(self, sentence: Span) -> List[FactTriplet]:
        """
        Extract semantic triples from a single sentence using dependency parsing.

        Strategy:
        1. Find the main verb (predicate)
        2. Find the subject (nsubj, nsubjpass)
        3. Find the object (dobj, pobj, attr)
        4. Handle compound subjects/objects
        5. Extract additional relationships (prep, amod, etc.)
        """
        triples = []
        sentence_text = sentence.text.strip()

        # Find the root verb (main predicate)
        root_verb = None
        for token in sentence:
            if token.dep_ == "ROOT" and token.pos_ in ["VERB", "AUX"]:
                root_verb = token
                break

        if not root_verb:
            # Try to find any verb if no clear root
            for token in sentence:
                if token.pos_ == "VERB":
                    root_verb = token
                    break

        if not root_verb:
            logger.debug(f"No main verb found in sentence: {sentence_text}")
            return triples

        # Extract subject-verb-object relationships
        subject = self._find_subject(root_verb)
        objects = self._find_objects(root_verb)

        # Pre-filter: Remove self-referential objects BEFORE copula check
        if subject:
            normalized_subject = self._normalize_entity(subject)
            objects = [obj for obj in objects
                      if self._normalize_entity(obj) != normalized_subject]

        # Handle German copula constructions with linguistic nuances
        if not objects and self._is_copula_verb(root_verb):
            copula_predicatives = self._find_copula_predicatives(root_verb)
            if copula_predicatives:
                objects = copula_predicatives

        # Handle German modal verb constructions
        if not objects and self._is_modal_verb(root_verb):
            modal_chain = self._extract_modal_chain(root_verb, subject, sentence_text)
            if modal_chain:
                triples.extend(modal_chain)
                # Early return for modal constructions to avoid duplicate processing
                return triples

        if subject and objects:
            # Use specialized copula predicate normalization for linking verbs
            if self._is_copula_verb(root_verb):
                predicate = self._normalize_copula_predicate(root_verb)
            else:
                predicate = self._normalize_predicate(root_verb.lemma_)
            confidence = self._calculate_triple_confidence(subject, root_verb, objects[0])

            for obj in objects:
                normalized_subject = self._normalize_entity(subject)
                normalized_object = self._normalize_entity(obj)

                # FILTER: Skip self-referential triples (Subject == Object)
                if normalized_subject != normalized_object:
                    triple = FactTriplet(
                        subject=normalized_subject,
                        predicate=predicate,
                        object=normalized_object,
                        confidence=confidence,
                        source_sentence=sentence_text,
                        extraction_method="spacy_dependency"
                    )
                    triples.append(triple)
                else:
                    logger.debug(f"Skipped self-referential triple: {normalized_subject} {predicate} {normalized_object}")

        # Extract coordinated verb relationships (conjunctions)
        coordinated_triples = self._extract_coordinated_verbs(root_verb, subject, sentence_text)
        triples.extend(coordinated_triples)

        # Extract additional relationships (prepositional, adjectival)
        additional_triples = self._extract_additional_relationships(sentence, sentence_text)
        triples.extend(additional_triples)

        return triples

    def _extract_coordinated_verbs(self, root_verb: Token, main_subject: Optional[str], sentence_text: str) -> List[FactTriplet]:
        """
        Extract triples from coordinated verbs using conjunctions.

        Handles patterns like:
        - "Vitamin B3 hilft bei der Regeneration und ist wichtig für den Körper"
        - "Niacin unterstützt den Stoffwechsel und fördert die Gesundheit"

        Based on debug analysis showing:
        - Conjunctions: ['und'] are detected by spaCy
        - Conjunctive verbs have dep_='cj' (conjunct)
        """
        triples = []

        if not main_subject:
            return triples

        # Look for conjunctions in the root verb's children
        for child in root_verb.children:
            if child.dep_ == "cd" and child.pos_ == "CCONJ":  # Coordinating conjunction
                # Find conjunctive verbs attached to this conjunction
                for conj_child in child.children:
                    if conj_child.dep_ == "cj" and conj_child.pos_ in ["VERB", "AUX"]:
                        # Extract subject-verb-object for the conjunctive verb
                        conj_subject = main_subject  # Share the same subject
                        conj_objects = self._find_objects(conj_child)

                        # Pre-filter self-referential objects for conjunctive verb too
                        if conj_subject:
                            normalized_subject = self._normalize_entity(conj_subject)
                            conj_objects = [obj for obj in conj_objects
                                          if self._normalize_entity(obj) != normalized_subject]

                        # Handle copula constructions for conjunctive verb
                        if not conj_objects and self._is_copula_verb(conj_child):
                            copula_predicatives = self._find_copula_predicatives(conj_child)
                            if copula_predicatives:
                                conj_objects = copula_predicatives

                        if conj_objects:
                            # Use specialized predicate normalization for conjunctive verb
                            if self._is_copula_verb(conj_child):
                                predicate = self._normalize_copula_predicate(conj_child)
                            else:
                                predicate = self._normalize_predicate(conj_child.lemma_)

                            confidence = self._calculate_triple_confidence(conj_subject, conj_child, conj_objects[0])

                            for obj in conj_objects:
                                normalized_subject = self._normalize_entity(conj_subject)
                                normalized_object = self._normalize_entity(obj)

                                # Skip self-referential triples
                                if normalized_subject != normalized_object:
                                    triple = FactTriplet(
                                        subject=normalized_subject,
                                        predicate=predicate,
                                        object=normalized_object,
                                        confidence=confidence,
                                        source_sentence=sentence_text,
                                        extraction_method="coordinated_verb"
                                    )
                                    triples.append(triple)
                                    logger.debug(f"Extracted coordinated triple: {triple}")

        return triples

    def _is_modal_verb(self, verb: Token) -> bool:
        """
        Check if a verb is a modal verb in German.

        Modal verbs: können, sollen, müssen, dürfen, wollen, mögen
        """
        if verb.pos_ != "AUX":
            return False

        modal_verbs = {
            "können", "kann", "sollen", "sollte", "müssen", "muss",
            "dürfen", "darf", "wollen", "will", "mögen", "mag"
        }

        return verb.lemma_ in modal_verbs or verb.text.lower() in modal_verbs

    def _extract_modal_chain(self, modal_verb: Token, subject: Optional[str], sentence_text: str) -> List[FactTriplet]:
        """
        Extract semantic triples from modal verb constructions.

        Handles patterns like:
        - "Ein Mangel an Vitamin B3 kann zu Müdigkeit führen"
        - "Vitamin B3 sollte täglich eingenommen werden"

        Based on debug analysis:
        - Modal verb is ROOT: "kann"
        - Main verb is child with dep_="oc": "führen"
        - Objects are found via prepositional phrases: "zu Müdigkeit"
        """
        triples = []

        if not subject:
            # Try to find subject in wider context for modal constructions
            subject = self._find_extended_subject(modal_verb)

        if not subject:
            return triples

        # Find the main semantic verb linked to the modal
        main_verb = None
        for child in modal_verb.children:
            if child.dep_ == "oc" and child.pos_ == "VERB":  # Object clause
                main_verb = child
                break

        if not main_verb:
            return triples

        # Extract objects from the main verb and its prepositional phrases
        modal_objects = self._find_modal_objects(main_verb)

        if modal_objects:
            # Create modal predicate that captures the semantic meaning
            modal_predicate = self._normalize_modal_predicate(modal_verb, main_verb)
            confidence = self._calculate_triple_confidence(subject, main_verb, modal_objects[0])

            for obj in modal_objects:
                normalized_subject = self._normalize_entity(subject)
                normalized_object = self._normalize_entity(obj)

                # Skip self-referential triples
                if normalized_subject != normalized_object:
                    triple = FactTriplet(
                        subject=normalized_subject,
                        predicate=modal_predicate,
                        object=normalized_object,
                        confidence=confidence,
                        source_sentence=sentence_text,
                        extraction_method="modal_chain"
                    )
                    triples.append(triple)
                    logger.debug(f"Extracted modal triple: {triple}")

        return triples

    def _find_extended_subject(self, verb: Token) -> Optional[str]:
        """
        Find extended subject for modal constructions that might span multiple tokens.

        For "Ein Mangel an Vitamin B3 kann..." tries to capture the full subject phrase.
        """
        # First try normal subject finding
        subject = self._find_subject(verb)
        if subject:
            return subject

        # For modals, look for subjects in the sentence context
        # that might be parsed as other dependencies due to complex structure
        sent_tokens = list(verb.sent)
        verb_idx = verb.i - sent_tokens[0].i

        # Look for noun phrases before the modal verb
        for i in range(verb_idx - 1, -1, -1):
            token = sent_tokens[i]
            if token.pos_ in ["NOUN", "PROPN"] and token.dep_ not in ["punct"]:
                # Found a potential subject, get its full phrase
                return self._get_full_phrase(token)

        return None

    def _find_modal_objects(self, main_verb: Token) -> List[str]:
        """
        Find objects in modal constructions, especially prepositional objects.

        For "führen zu Müdigkeit" extracts "Müdigkeit" from prepositional phrase.
        """
        objects = []

        # Look for prepositional phrases attached to the main verb
        for child in main_verb.children:
            if child.dep_ == "mo" and child.pos_ == "ADP":  # Modal object (preposition)
                # Find the noun in the prepositional phrase
                for grandchild in child.children:
                    if grandchild.pos_ in ["NOUN", "PROPN"]:
                        objects.append(self._get_full_phrase(grandchild))

        # Also check direct objects
        for child in main_verb.children:
            if child.dep_ in ["oa", "og", "od"]:  # German direct objects
                objects.append(self._get_full_phrase(child))

        return objects

    def _normalize_modal_predicate(self, modal_verb: Token, main_verb: Token) -> str:
        """
        Create meaningful predicates for modal constructions.

        Combines modal + main verb into semantic relationship.
        """
        modal_mappings = {
            "können": "can",
            "sollen": "should",
            "müssen": "must",
            "dürfen": "may",
            "wollen": "wants_to",
            "mögen": "likes_to"
        }

        modal_meaning = modal_mappings.get(modal_verb.lemma_, "can")
        main_meaning = self._normalize_predicate(main_verb.lemma_)

        # Combine modal + main verb for semantic clarity
        return f"{modal_meaning}_{main_meaning}"

    def _find_subject(self, verb: Token) -> Optional[str]:
        """Find the subject of a verb using language-specific dependency parsing."""
        # Get language-specific subject labels
        subject_labels = self.dependency_labels[self.current_language]['subject']

        # Look for nominal subject
        for child in verb.children:
            if child.dep_ in subject_labels:
                return self._get_full_phrase(child)

        # German Copula-Subject-Detection Heuristic
        # Pattern: "Magnesium ist ein Mineral"
        # If capitalized word + copula + article + capitalized word
        # → First capitalized word is definitely the subject!
        if self.current_language == 'de' and self._is_copula_verb(verb):
            subject = self._detect_german_copula_subject(verb)
            if subject:
                return subject

        # Fallback: look for any noun before the verb
        for token in verb.sent:
            if token.i < verb.i and token.pos_ in ["NOUN", "PROPN"] and token.dep_ != "punct":
                return self._get_full_phrase(token)

        return None

    def _find_objects(self, verb: Token) -> List[str]:
        """Find objects of a verb using language-specific dependency parsing."""
        objects = []

        # Get language-specific object labels
        object_labels = self.dependency_labels[self.current_language]['object']
        prep_object_labels = self.dependency_labels[self.current_language]['prep_object']

        for child in verb.children:
            if child.dep_ in object_labels:
                objects.append(self._get_full_phrase(child))

            # Handle prepositional phrases (language-specific)
            elif child.dep_ == "prep" or child.pos_ == "ADP":  # Preposition
                for grandchild in child.children:
                    if grandchild.dep_ in prep_object_labels:
                        objects.append(self._get_full_phrase(grandchild))

        return objects

    def _get_full_phrase(self, token: Token) -> str:
        """
        Get the full phrase including compounds, adjectives, and determiners.
        Uses language-specific dependency labels.

        Example: "wichtige Rolle" -> gets both words, not just "Rolle"
        """
        # Start with the token itself
        phrase_tokens = [token]

        # Get language-specific modifier labels
        modifier_labels = self.dependency_labels[self.current_language]['modifier']
        compound_labels = self.dependency_labels[self.current_language]['compound']

        # Add modifiers and compounds before
        for child in token.children:
            if child.dep_ in modifier_labels + compound_labels and child.i < token.i:
                phrase_tokens.insert(0, child)

        # Add compounds after
        for child in token.children:
            if child.dep_ in compound_labels and child.i > token.i:
                phrase_tokens.append(child)

        # Sort by position and join
        phrase_tokens.sort(key=lambda t: t.i)
        phrase = " ".join(t.text for t in phrase_tokens)

        return phrase.strip()

    def _extract_additional_relationships(self, sentence: Span, sentence_text: str) -> List[FactTriplet]:
        """Extract additional semantic relationships beyond simple SVO patterns."""
        triples = []

        # Look for "ist" relationships (type definitions)
        for token in sentence:
            if token.lemma_ in ["sein", "ist"] and token.dep_ == "cop":
                subject = self._find_subject_for_copula(token)
                predicate_obj = self._find_predicate_object_for_copula(token)

                if subject and predicate_obj:
                    triple = FactTriplet(
                        subject=self._normalize_entity(subject),
                        predicate="is_type_of",
                        object=self._normalize_entity(predicate_obj),
                        confidence=0.7,
                        source_sentence=sentence_text,
                        extraction_method="copula_extraction"
                    )
                    triples.append(triple)

        return triples

    def _find_subject_for_copula(self, copula: Token) -> Optional[str]:
        """Find subject for copula constructions like 'X ist Y'."""
        # Look in the parent of the copula
        if copula.head:
            for child in copula.head.children:
                if child.dep_ in ["nsubj", "nsubjpass"]:
                    return self._get_full_phrase(child)
        return None

    def _find_predicate_object_for_copula(self, copula: Token) -> Optional[str]:
        """Find predicate object for copula constructions."""
        if copula.head and copula.head.pos_ in ["NOUN", "ADJ"]:
            return self._get_full_phrase(copula.head)
        return None

    def _normalize_predicate(self, predicate: str) -> str:
        """Normalize German predicates to standardized English forms."""
        predicate_lower = predicate.lower().strip()
        return self.predicate_mapping.get(predicate_lower, predicate_lower)

    def _normalize_entity(self, entity: str) -> str:
        """
        Normalize entity names using Entity Equivalence Mapper.
        This resolves scientific equivalences like Niacin → Vitamin_B3.
        """
        entity_clean = entity.strip()

        # Use Entity Equivalence Mapper for scientific resolution
        resolved_entity = self.entity_mapper.resolve_entity_name(entity_clean)

        # If no equivalence found, fall back to legacy normalization
        if resolved_entity == entity_clean.replace(" ", "_"):
            # Check legacy mappings for backward compatibility
            if entity_clean in self.entity_normalization:
                return self.entity_normalization[entity_clean]

            # Check for partial matches (case-insensitive)
            entity_lower = entity_clean.lower()
            for key, value in self.entity_normalization.items():
                if key.lower() in entity_lower or entity_lower in key.lower():
                    return value

        return resolved_entity

    def _calculate_triple_confidence(self, subject: str, verb: Token, obj: str) -> float:
        """Calculate confidence score for a semantic triple."""
        confidence = 0.5  # Base confidence

        # Boost for known scientific terms
        if any(term in subject.lower() for term in ['vitamin', 'mineral', 'nährstoff']):
            confidence += 0.2

        if any(term in obj.lower() for term in ['stoffwechsel', 'system', 'funktion']):
            confidence += 0.2

        # Boost for clear dependency relationships
        if verb.dep_ == "ROOT":
            confidence += 0.1

        # Penalty for very short phrases
        if len(subject) < 3 or len(obj) < 3:
            confidence -= 0.2

        return max(0.0, min(1.0, confidence))

    def _deduplicate_and_filter_triples(self, triples: List[FactTriplet]) -> List[FactTriplet]:
        """Remove duplicates and filter low-confidence triples."""
        # Remove duplicates based on (subject, predicate, object)
        seen = set()
        unique_triples = []

        for triple in triples:
            key = (triple.subject.lower(), triple.predicate.lower(), triple.object.lower())
            if key not in seen and triple.confidence >= self.min_confidence:
                seen.add(key)
                unique_triples.append(triple)

        # Sort by confidence (highest first)
        unique_triples.sort(key=lambda t: t.confidence, reverse=True)

        return unique_triples

    def _create_empty_triple_set(
        self,
        chunk_id: str,
        document_id: str,
        source_paragraphs: List[int],
        source_pages: List[int],
        original_char_range: tuple,
        word_count: int,
        processing_time: float
    ) -> SemanticTripleSet:
        """Create empty triple set when extraction fails."""
        return SemanticTripleSet(
            triples=[],
            source_chunk_id=chunk_id,
            source_document_id=document_id,
            source_paragraphs=source_paragraphs,
            source_pages=source_pages,
            original_char_range=original_char_range,
            word_count=word_count,
            extraction_time_seconds=processing_time,
            total_sentences_processed=0,
            successful_extractions=0,
            failed_extractions=1
        )

    def _is_copula_verb(self, verb: Token) -> bool:
        """
        Check if a verb is a copula (linking verb) in German.

        Handles linguistic nuances of different copula types.
        """
        if verb.pos_ != "AUX":
            return False

        # German copula verbs with their semantic types
        copula_verbs = {
            "sein": "state",      # is/are - describes properties
            "werden": "change",   # become - describes transformation
            "bleiben": "continuity", # remain - describes persistence
            "scheinen": "appearance", # seem - describes perception
            "wirken": "appearance",   # appear - describes impression
        }

        return verb.lemma_ in copula_verbs

    def _detect_german_copula_subject(self, verb: Token) -> Optional[str]:
        """
        German Copula-Subject-Detection Heuristic for patterns like:
        'Magnesium ist ein Mineral' where spaCy misclassifies 'Magnesium' as predicative.

        Heuristic: Capitalized + Copula + Article + Capitalized
        → First capitalized word is definitely the subject!
        """
        sent_tokens = list(verb.sent)
        verb_idx = verb.i - sent_tokens[0].i  # Position in sentence

        # Need at least 4 tokens: [Subject] [Copula] [Article] [Object]
        if len(sent_tokens) < 4 or verb_idx < 1 or verb_idx >= len(sent_tokens) - 2:
            return None

        # Check pattern: [Capitalized] [ist/war/...] [ein/eine/der/die/das] [Capitalized]
        prev_token = sent_tokens[verb_idx - 1]  # Potential subject
        next_token = sent_tokens[verb_idx + 1]  # Potential article

        # Check if we have enough tokens for article + object
        if verb_idx + 2 >= len(sent_tokens):
            return None

        article_token = next_token
        object_token = sent_tokens[verb_idx + 2]  # Potential object

        # Check the pattern
        is_prev_capitalized = (prev_token.text[0].isupper() and
                              prev_token.pos_ in ["NOUN", "PROPN"])
        is_copula = verb.lemma_ in ["sein", "werden", "bleiben"]
        is_article = article_token.text.lower() in ["ein", "eine", "der", "die", "das"]
        is_obj_capitalized = (object_token.text[0].isupper() and
                             object_token.pos_ in ["NOUN", "PROPN"])

        if is_prev_capitalized and is_copula and is_article and is_obj_capitalized:
            # Found the pattern! The first capitalized word is the subject
            return self._get_full_phrase(prev_token)

        return None

    def _find_copula_predicatives(self, copula_verb: Token) -> List[str]:
        """
        Find predicative complements for copula constructions.

        In German: Subject + Copula + Predicative
        E.g., "Vitamin B3 ist wasserlöslich"
        → Subject: "Vitamin B3", Copula: "ist", Predicative: "wasserlöslich"
        """
        predicatives = []

        # Get language-specific copula labels
        copula_labels = self.dependency_labels[self.current_language]['copula']

        # Find predicative complements
        for child in copula_verb.children:
            if child.dep_ in copula_labels:
                predicatives.append(self._get_full_phrase(child))

        return predicatives

    def _normalize_copula_predicate(self, copula_verb: Token) -> str:
        """
        Normalize copula verbs to semantic predicates that capture linguistic nuances.

        Maps German copula verbs to meaningful semantic relations.
        """
        copula_mappings = {
            "sein": "has_property",      # Static property: "X ist Y" → "X has_property Y"
            "werden": "becomes",         # Change: "X wird Y" → "X becomes Y"
            "bleiben": "remains",        # Continuity: "X bleibt Y" → "X remains Y"
            "scheinen": "appears_to_be", # Perception: "X scheint Y" → "X appears_to_be Y"
            "wirken": "appears_as",      # Impression: "X wirkt Y" → "X appears_as Y"
        }

        lemma = copula_verb.lemma_
        return copula_mappings.get(lemma, "is_related_to")