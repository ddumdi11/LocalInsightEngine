"""
Semantic Triples Data Models for Aussagenlogische Pipeline.
Transforms sentences into structured fact representations.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from pathlib import Path


@dataclass
class FactTriplet:
    """
    A single semantic fact in Subject-Predicate-Object form.

    Examples:
        ("Vitamin_B3", "supports", "Energy_Metabolism")
        ("Vitamin_B3", "is_type_of", "B_Vitamin")
        ("Energy_Metabolism", "occurs_in", "Human_Body")
    """
    subject: str           # The entity performing the action or having the property
    predicate: str         # The relationship or action
    object: str           # The target entity or property value
    confidence: float     # Extraction confidence (0.0 - 1.0)

    # Source tracking for transparency
    source_sentence: str          # Original sentence this fact was extracted from
    source_paragraph_id: Optional[int] = None
    source_page: Optional[int] = None
    source_char_range: Optional[tuple] = None

    # Enhanced metadata for future extensions
    semantic_context: Optional[Dict[str, Any]] = None  # For hybrid logic expansion
    normalization_applied: bool = False                # Track if entities were normalized
    extraction_method: str = "spacy_dependency"        # Track extraction approach

    def __str__(self) -> str:
        return f"({self.subject}, {self.predicate}, {self.object}) [conf: {self.confidence:.2f}]"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.object,
            "confidence": self.confidence,
            "source_sentence": self.source_sentence,
            "source_paragraph_id": self.source_paragraph_id,
            "source_page": self.source_page,
            "source_char_range": self.source_char_range,
            "semantic_context": self.semantic_context,
            "normalization_applied": self.normalization_applied,
            "extraction_method": self.extraction_method
        }


@dataclass
class SemanticTripleSet:
    """
    Collection of semantic triples extracted from a text chunk.
    Represents the complete factual content in structured form.
    """
    triples: List[FactTriplet]
    source_chunk_id: str
    source_document_id: str

    # Chunk metadata
    source_paragraphs: List[int]
    source_pages: List[int]
    original_char_range: tuple
    word_count: int

    # Extraction statistics
    extraction_time_seconds: float
    total_sentences_processed: int
    successful_extractions: int
    failed_extractions: int

    @property
    def extraction_success_rate(self) -> float:
        """Calculate the percentage of successful triple extractions."""
        total = self.successful_extractions + self.failed_extractions
        return (self.successful_extractions / total * 100) if total > 0 else 0.0

    def get_entities(self) -> List[str]:
        """Get all unique entities mentioned in triples."""
        entities = set()
        for triple in self.triples:
            entities.add(triple.subject)
            entities.add(triple.object)
        return sorted(list(entities))

    def get_predicates(self) -> List[str]:
        """Get all unique predicates (relationships) used."""
        return sorted(list(set(triple.predicate for triple in self.triples)))

    def filter_by_confidence(self, min_confidence: float) -> 'SemanticTripleSet':
        """Return a new set with only high-confidence triples."""
        filtered_triples = [t for t in self.triples if t.confidence >= min_confidence]

        # Create new instance with filtered triples
        return SemanticTripleSet(
            triples=filtered_triples,
            source_chunk_id=self.source_chunk_id,
            source_document_id=self.source_document_id,
            source_paragraphs=self.source_paragraphs,
            source_pages=self.source_pages,
            original_char_range=self.original_char_range,
            word_count=self.word_count,
            extraction_time_seconds=self.extraction_time_seconds,
            total_sentences_processed=self.total_sentences_processed,
            successful_extractions=len(filtered_triples),
            failed_extractions=self.failed_extractions  # Preserve original extraction failures
        )

    def to_fact_text(self) -> str:
        """
        Convert triples to structured text format for LLM consumption.
        This replaces the old neutralized_content approach.
        """
        if not self.triples:
            return "No factual relationships extracted."

        fact_lines = ["FACTUAL RELATIONSHIPS:"]

        # Group by subject for better readability
        subjects = {}
        for triple in self.triples:
            if triple.subject not in subjects:
                subjects[triple.subject] = []
            subjects[triple.subject].append((triple.predicate, triple.object))

        for subject, relationships in subjects.items():
            fact_lines.append(f"\n{subject}:")
            for predicate, obj in relationships:
                fact_lines.append(f"  - {predicate} -> {obj}")

        fact_lines.append(f"\nExtracted from {self.word_count} words with {self.extraction_success_rate:.1f}% success rate.")

        return "\n".join(fact_lines)


@dataclass
class DocumentTripleAnalysis:
    """
    Complete semantic triple analysis for an entire document.
    Contains all extracted facts organized by chunks.
    """
    source_document_id: str
    triple_sets: List[SemanticTripleSet]

    # Global statistics
    total_triples: int
    total_entities: int
    total_relationships: int
    processing_time_seconds: float

    # Analysis metadata
    factual_mode_enabled: bool
    extraction_method: str
    confidence_threshold: float

    @property
    def all_triples(self) -> List[FactTriplet]:
        """Get all triples from all chunks."""
        all_triples = []
        for triple_set in self.triple_sets:
            all_triples.extend(triple_set.triples)
        return all_triples

    @property
    def global_entities(self) -> List[str]:
        """Get all unique entities across the entire document."""
        entities = set()
        for triple_set in self.triple_sets:
            entities.update(triple_set.get_entities())
        return sorted(list(entities))

    @property
    def global_predicates(self) -> List[str]:
        """Get all unique relationships across the entire document."""
        predicates = set()
        for triple_set in self.triple_sets:
            predicates.update(triple_set.get_predicates())
        return sorted(list(predicates))

    def find_triples_about_entity(self, entity: str, case_sensitive: bool = False) -> List[FactTriplet]:
        """
        Find all triples where the entity appears as subject or object.
        This enables precise Q&A like 'What about Vitamin B3?'
        """
        matches = []
        search_entity = entity if case_sensitive else entity.lower()

        for triple in self.all_triples:
            subject = triple.subject if case_sensitive else triple.subject.lower()
            obj = triple.object if case_sensitive else triple.object.lower()

            if search_entity in subject or search_entity in obj:
                matches.append(triple)

        return matches

    def to_llm_context(self, max_triples: Optional[int] = None) -> str:
        """
        Convert entire analysis to structured text for LLM consumption.
        This replaces the old chunk-by-chunk neutralized content approach.
        """
        if not self.triple_sets:
            return "No semantic relationships extracted from document."

        context_lines = [
            f"DOCUMENT SEMANTIC ANALYSIS",
            f"Total Facts: {self.total_triples}",
            f"Entities: {self.total_entities}",
            f"Relationships: {self.total_relationships}",
            f"Factual Mode: {self.factual_mode_enabled}",
            "",
            "EXTRACTED FACTS:"
        ]

        # Get all triples, optionally limited
        all_triples = self.all_triples
        if max_triples and len(all_triples) > max_triples:
            # Sort by confidence and take top N
            all_triples = sorted(all_triples, key=lambda t: t.confidence, reverse=True)[:max_triples]
            context_lines.append(f"(Showing top {max_triples} of {len(self.all_triples)} facts)")

        # Group facts by subject for readability
        subjects = {}
        for triple in all_triples:
            if triple.subject not in subjects:
                subjects[triple.subject] = []
            subjects[triple.subject].append((triple.predicate, triple.object, triple.confidence))

        for subject, relationships in subjects.items():
            context_lines.append(f"\n{subject}:")
            for predicate, obj, confidence in relationships:
                context_lines.append(f"  - {predicate} -> {obj} (conf: {confidence:.2f})")

        return "\n".join(context_lines)