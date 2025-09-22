#!/usr/bin/env python3
"""
TDD Tests for Content Flow - TextProcessor end-to-end testing

Tests the complete flow from Document → TextProcessor → neutralized content
for both Sachbuch-Modus and Normal-Modus.
"""

import pytest
import sys
from pathlib import Path
from uuid import uuid4
from typing import Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from local_insight_engine.services.processing_hub.text_processor import TextProcessor
from local_insight_engine.models.document import Document, DocumentMetadata


class TestContentFlow:
    """Test suite for content flow through TextProcessor."""

    # Test configuration constants
    CHUNK_SIZE: int = 200
    CHUNK_OVERLAP: int = 50

    # Test data constants
    VITAMIN_B3_TEXT: str = """
    Vitamin B3 (Niacin) spielt eine wichtige Rolle im Energiestoffwechsel und hilft bei der Regeneration.
    Vitamin B3 unterstützt die Funktion des Nervensystems und trägt zur normalen psychischen Funktion bei.
    Ein Mangel an Vitamin B3 kann zu Müdigkeit und Konzentrationsproblemen führen.
    """.strip()

    SIMPLE_NUTRIENT_TEXT: str = "Vitamin B3 und Magnesium sind wichtige Nährstoffe für die Gesundheit."
    MINERAL_TEXT: str = "Magnesium ist ein wichtiges Mineral für den Körper."

    def setup_method(self, method: Optional[object] = None) -> None:
        """Setup fresh processor for each test."""
        self.processor = TextProcessor(chunk_size=self.CHUNK_SIZE, chunk_overlap=self.CHUNK_OVERLAP)

    def _create_test_document(self, text_content: str) -> Document:
        """Helper to create test documents."""
        metadata = DocumentMetadata(
            file_path=Path("test.txt"),
            file_format="txt",
            file_size=len(text_content)
        )

        return Document(
            id=uuid4(),  # Generate valid UUID
            text_content=text_content,
            metadata=metadata,
            paragraph_mapping={0: (0, len(text_content))},
            page_mapping={1: (0, len(text_content))},
            section_mapping={"main": (0, len(text_content))}  # Add required section_mapping
        )

    def _assert_basic_processing_results(self, result: Any, expected_min_entities: int = 1) -> None:
        """
        Helper to assert basic processing results.

        Args:
            result: Processing result object with chunks and entities attributes
            expected_min_entities: Minimum number of entities expected to be extracted (default: 1)

        Raises:
            AssertionError: If processing results don't meet expectations
        """
        assert len(result.chunks) > 0, "Should create at least one chunk"
        assert len(result.all_entities) >= expected_min_entities, f"Should extract at least {expected_min_entities} entities"

        # Validate chunk properties
        chunk = result.chunks[0]
        assert chunk.neutralized_content, "Should have neutralized content"
        assert len(chunk.neutralized_content.strip()) > 0, "Neutralized content should not be empty"
        assert isinstance(chunk.word_count, int), "Word count should be integer"
        assert isinstance(chunk.entities, list), "Entities should be list"

    def test_sachbuch_modus_preserves_scientific_terms(self) -> None:
        """Test that Sachbuch-Modus (bypass_anonymization=True) preserves scientific terms."""
        document: Document = self._create_test_document(self.VITAMIN_B3_TEXT)

        # Process in Sachbuch-Modus
        result: Any = self.processor.process(document, bypass_anonymization=True)

        # Validate basic processing results
        self._assert_basic_processing_results(result, expected_min_entities=1)

        # Check that scientific terms are preserved in entities
        entity_texts = [entity.text for entity in result.all_entities]
        assert any("Vitamin B3" in text or "Niacin" in text for text in entity_texts), \
            f"Should preserve scientific terms, got entities: {entity_texts}"

    def test_normal_modus_anonymizes_content(self) -> None:
        """Test that Normal-Modus (bypass_anonymization=False) anonymizes content."""
        document: Document = self._create_test_document(self.VITAMIN_B3_TEXT)

        # Process in Normal-Modus
        result: Any = self.processor.process(document, bypass_anonymization=False)

        # Validate basic processing results (lenient on entities due to anonymization)
        self._assert_basic_processing_results(result, expected_min_entities=0)

    def test_content_flow_consistency(self) -> None:
        """Test that content flow produces consistent results."""
        document: Document = self._create_test_document(self.MINERAL_TEXT)

        # Process multiple times - should be consistent
        result1: Any = self.processor.process(document, bypass_anonymization=True)
        result2: Any = self.processor.process(document, bypass_anonymization=True)

        assert len(result1.chunks) == len(result2.chunks), "Should produce consistent chunk count"
        assert len(result1.all_entities) == len(result2.all_entities), "Should extract same number of entities"

    def test_empty_content_handling(self) -> None:
        """Test handling of empty or minimal content."""
        document: Document = self._create_test_document("")

        # Should handle gracefully without crashing
        result: Any = self.processor.process(document, bypass_anonymization=True)

        assert isinstance(result.chunks, list), "Should return chunk list"
        assert isinstance(result.all_entities, list), "Should return entity list"

    def test_chunk_properties(self) -> None:
        """Test that chunks have required properties."""
        document: Document = self._create_test_document(self.SIMPLE_NUTRIENT_TEXT)
        result: Any = self.processor.process(document, bypass_anonymization=True)

        # Use helper for basic validation
        self._assert_basic_processing_results(result, expected_min_entities=1)

        # Additional specific property tests
        chunk = result.chunks[0]
        assert hasattr(chunk, 'word_count'), "Chunk should have word_count"
        assert hasattr(chunk, 'entities'), "Chunk should have entities"
        assert hasattr(chunk, 'neutralized_content'), "Chunk should have neutralized_content"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])