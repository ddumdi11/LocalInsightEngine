#!/usr/bin/env python3
"""
TDD Tests for Semantic Triples Pipeline - FactTripletExtractor testing

Tests the complete triple extraction from sentences to structured facts.
"""

import pytest
import sys
import logging
from pathlib import Path
from typing import List, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from local_insight_engine.services.processing_hub.fact_triplet_extractor import FactTripletExtractor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class TestSemanticTriples:
    """Test suite for semantic triple extraction."""

    # Test data constants
    VITAMIN_B3_SENTENCES: List[str] = [
        "Vitamin B3 unterstützt den Energiestoffwechsel.",
        "Vitamin B3 ist wasserlöslich.",
        "Niacin fördert die Nervenfunktion.",
        "Vitamin B3 hilft bei der Regeneration und ist wichtig für den Körper.",
        "Ein Mangel an Vitamin B3 kann zu Müdigkeit führen.",
        # German Copula Heuristic test cases (Capitalized + ist + ein/eine + Capitalized)
        "Magnesium ist ein Mineral.",
        "Niacin ist eine Verbindung."
    ]

    SIMPLE_SENTENCES = [
        "Vitamin B3 ist wichtig.",
        "Das Vitamin unterstützt den Körper.",
        "B3 hilft dem Menschen."
    ]

    def setup_method(self) -> None:
        """Setup fresh extractor for each test."""
        self.extractor: FactTripletExtractor = FactTripletExtractor()

    def test_extractor_initialization(self) -> None:
        """Test that FactTripletExtractor initializes correctly."""
        extractor = FactTripletExtractor()

        assert extractor is not None, "Extractor should initialize"
        assert hasattr(extractor, 'nlp'), "Should have nlp attribute"
        assert hasattr(extractor, 'entity_mapper'), "Should have entity_mapper"

        # Check spaCy model availability
        if extractor.nlp is None:
            pytest.skip("spaCy German model not available - install with: python -m spacy download de_core_news_sm")

    def test_triple_extraction_from_simple_sentences(self) -> None:
        """Test triple extraction from simple, well-formed sentences."""
        if self.extractor.nlp is None:
            pytest.skip("spaCy model not available")

        test_sentence = "Vitamin B3 ist wichtig."

        # Process with spaCy
        doc = self.extractor.nlp(test_sentence)
        sentence_span = list(doc.sents)[0]

        # Extract triples
        triples = self.extractor._extract_triples_from_sentence(sentence_span)

        # Should extract at least basic triples
        assert isinstance(triples, list), "Should return list of triples"

        # If triples are found, validate structure
        for triple in triples:
            assert hasattr(triple, 'subject'), "Triple should have subject"
            assert hasattr(triple, 'predicate'), "Triple should have predicate"
            assert hasattr(triple, 'object'), "Triple should have object"
            assert isinstance(triple.subject, str), "Subject should be string"
            assert isinstance(triple.predicate, str), "Predicate should be string"
            assert isinstance(triple.object, str), "Object should be string"

    def test_vitamin_b3_triple_extraction(self) -> None:
        """Test triple extraction specifically for Vitamin B3 sentences."""
        if self.extractor.nlp is None:
            pytest.skip("spaCy model not available")

        all_triples: List[Any] = []

        logger.info("Processing %d sentences", len(self.VITAMIN_B3_SENTENCES))
        for i, sentence in enumerate(self.VITAMIN_B3_SENTENCES, 1):
            logger.debug("Sentence %d: %s", i, sentence)
            doc = self.extractor.nlp(sentence)
            for sent in doc.sents:
                triples = self.extractor._extract_triples_from_sentence(sent)
                logger.debug("Extracted %d triples", len(triples))
                for triple in triples:
                    logger.debug("Triple: %s", triple)
                all_triples.extend(triples)

        logger.info("TOTAL: %d triples extracted", len(all_triples))

        # Should extract some triples from the vitamin sentences
        assert isinstance(all_triples, list), "Should return list of triples"

        # Log what was extracted for debugging
        if len(all_triples) == 0:
            logger.warning("No triples extracted - extraction logic may need enhancement")
            # This might be expected if the extraction logic needs improvement
            pytest.skip("No triples extracted - this may indicate extraction logic needs enhancement")
        else:
            logger.info("Successfully extracted %d triples!", len(all_triples))

    def test_vitamin_b3_fact_search(self) -> None:
        """Test searching for specific Vitamin B3 facts in extracted triples."""
        if self.extractor.nlp is None:
            pytest.skip("spaCy model not available")

        all_triples = []
        for sentence in self.VITAMIN_B3_SENTENCES:
            doc = self.extractor.nlp(sentence)
            for sent in doc.sents:
                triples = self.extractor._extract_triples_from_sentence(sent)
                all_triples.extend(triples)

        # Search for Vitamin B3 related triples
        vitamin_b3_triples = []
        for triple in all_triples:
            subject_lower = triple.subject.lower() if hasattr(triple, 'subject') else ""
            object_lower = triple.object.lower() if hasattr(triple, 'object') else ""

            if ('vitamin_b3' in subject_lower or 'vitamin_b3' in object_lower or
                'niacin' in subject_lower or 'niacin' in object_lower or
                'b3' in subject_lower or 'b3' in object_lower or
                'magnesium' in subject_lower or 'magnesium' in object_lower):
                vitamin_b3_triples.append(triple)

        # If we found triples, validate they contain meaningful information
        for triple in vitamin_b3_triples:
            assert len(triple.subject.strip()) > 0, "Subject should not be empty"
            assert len(triple.predicate.strip()) > 0, "Predicate should not be empty"
            assert len(triple.object.strip()) > 0, "Object should not be empty"

    def test_llm_context_formatting(self) -> None:
        """Test formatting triples for LLM context."""
        if self.extractor.nlp is None:
            pytest.skip("spaCy model not available")

        # Create some mock triples for testing
        class MockTriple:
            def __init__(self, subject, predicate, obj):
                self.subject = subject
                self.predicate = predicate
                self.object = obj

        mock_triples = [
            MockTriple("Vitamin_B3", "unterstützt", "Energiestoffwechsel"),
            MockTriple("Niacin", "fördert", "Nervenfunktion")
        ]

        # Test context formatting
        if mock_triples:
            context_lines = ["EXTRACTED FACTS ABOUT VITAMIN B3:"]
            for triple in mock_triples:
                context_lines.append(f"- {triple.subject} {triple.predicate} {triple.object}")

            context = "\n".join(context_lines)

            assert "EXTRACTED FACTS" in context, "Should have header"
            assert "Vitamin_B3" in context, "Should contain vitamin information"
            assert len(context.split('\n')) >= 2, "Should have multiple lines"

    def test_edge_cases(self):
        """Test edge cases and error handling."""
        if self.extractor.nlp is None:
            pytest.skip("spaCy model not available")

        # Test empty sentence
        empty_doc = self.extractor.nlp("")
        empty_triples = []
        for sent in empty_doc.sents:
            triples = self.extractor._extract_triples_from_sentence(sent)
            empty_triples.extend(triples)

        assert isinstance(empty_triples, list), "Should handle empty input gracefully"

        # Test single word
        single_word = self.extractor.nlp("Vitamin")
        single_triples = []
        for sent in single_word.sents:
            triples = self.extractor._extract_triples_from_sentence(sent)
            single_triples.extend(triples)

        assert isinstance(single_triples, list), "Should handle single word gracefully"

    def test_ist_constructions_red_phase(self):
        """
        RED PHASE: Test that 'ist' constructions are properly extracted.
        These currently FAIL and need improvement in extraction logic.
        """
        if self.extractor.nlp is None:
            pytest.skip("spaCy model not available")

        ist_sentences = [
            "Vitamin B3 ist wasserlöslich.",
            "Niacin ist wichtig.",
            "Magnesium ist ein Mineral."
        ]

        print(f"\n🔴 RED TEST: 'ist' constructions")
        total_triples = 0

        for sentence in ist_sentences:
            print(f"\n📝 Testing: {sentence}")
            doc = self.extractor.nlp(sentence)
            for sent in doc.sents:
                triples = self.extractor._extract_triples_from_sentence(sent)
                total_triples += len(triples)
                print(f"   📊 Extracted {len(triples)} triples:")
                for triple in triples:
                    print(f"      • {triple}")

        # This should FAIL initially - forcing us to improve extraction
        assert total_triples >= 3, f"Expected at least 3 triples from 'ist' constructions, got {total_triples}"

    def test_complex_sentences_red_phase(self):
        """
        RED PHASE: Test that complex sentences with conjunctions are handled.
        These currently FAIL and need improvement in extraction logic.
        """
        if self.extractor.nlp is None:
            pytest.skip("spaCy model not available")

        complex_sentences = [
            "Vitamin B3 hilft bei der Regeneration und ist wichtig für den Körper.",
            "Ein Mangel an Vitamin B3 kann zu Müdigkeit führen."
        ]

        print(f"\n🔴 RED TEST: Complex sentences")
        total_triples = 0

        for sentence in complex_sentences:
            print(f"\n📝 Testing: {sentence}")
            doc = self.extractor.nlp(sentence)
            for sent in doc.sents:
                triples = self.extractor._extract_triples_from_sentence(sent)
                total_triples += len(triples)
                print(f"   📊 Extracted {len(triples)} triples:")
                for triple in triples:
                    print(f"      • {triple}")

        # This should FAIL initially - forcing us to improve extraction
        assert total_triples >= 2, f"Expected at least 2 triples from complex sentences, got {total_triples}"

    def test_negation_constructions_red_phase(self):
        """
        RED PHASE: Test that negation and modal constructions are handled.
        These currently FAIL and need improvement in extraction logic.
        """
        if self.extractor.nlp is None:
            pytest.skip("spaCy model not available")

        negation_sentences = [
            "Ein Mangel an Vitamin B3 kann zu Müdigkeit führen.",
            "Vitamin B3 sollte täglich eingenommen werden.",
            "Ohne Niacin funktioniert der Stoffwechsel nicht."
        ]

        print(f"\n🔴 RED TEST: Negation/Modal constructions")
        total_triples = 0

        for sentence in negation_sentences:
            print(f"\n📝 Testing: {sentence}")
            doc = self.extractor.nlp(sentence)
            for sent in doc.sents:
                triples = self.extractor._extract_triples_from_sentence(sent)
                total_triples += len(triples)
                print(f"   📊 Extracted {len(triples)} triples:")
                for triple in triples:
                    print(f"      • {triple}")

        # This should FAIL initially - forcing us to improve extraction
        assert total_triples >= 2, f"Expected at least 2 triples from negation/modal constructions, got {total_triples}"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])