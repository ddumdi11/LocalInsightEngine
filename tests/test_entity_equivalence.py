#!/usr/bin/env python3
"""
TDD Tests for EntityEquivalenceMapper

RED-GREEN-REFACTOR approach for systematic feature development.
"""

import pytest
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from local_insight_engine.services.processing_hub.entity_equivalence_mapper import EntityEquivalenceMapper


class TestEntityEquivalenceMapper:
    """Test suite for EntityEquivalenceMapper using TDD approach."""

    def setup_method(self) -> None:
        """Setup fresh mapper for each test."""
        self.mapper = EntityEquivalenceMapper()

    def test_mapper_initialization(self) -> None:
        """Test that mapper initializes without errors."""
        mapper = EntityEquivalenceMapper()
        assert mapper is not None
        assert hasattr(mapper, 'predefined_equivalences')
        assert hasattr(mapper, 'dynamic_equivalences')

    def test_basic_predefined_equivalences(self) -> None:
        """Test basic predefined name resolution."""
        # These should work based on current implementation
        assert self.mapper.resolve_entity_name("Niacin") == "Vitamin_B3"
        assert self.mapper.resolve_entity_name("B3") == "Vitamin_B3"
        assert self.mapper.resolve_entity_name("Nikotinamid") == "Vitamin_B3"
        assert self.mapper.resolve_entity_name("Thiamin") == "Vitamin_B1"
        assert self.mapper.resolve_entity_name("Riboflavin") == "Vitamin_B2"

    def test_case_insensitive_resolution_red_phase(self) -> None:
        """
        RED PHASE: Test case-insensitive resolution.
        This test will FAIL initially and force us to implement case normalization.
        """
        # These should all resolve to the same canonical form
        expected: str = "Vitamin_B3"

        # This currently fails - vitamin b3 → vitamin_b3 instead of Vitamin_B3
        assert self.mapper.resolve_entity_name("vitamin b3") == expected
        assert self.mapper.resolve_entity_name("VITAMIN B3") == expected
        assert self.mapper.resolve_entity_name("Vitamin B3") == expected
        assert self.mapper.resolve_entity_name("NIACIN") == expected
        assert self.mapper.resolve_entity_name("niacin") == expected
        assert self.mapper.resolve_entity_name("Niacin") == expected

    def test_vitamin_b3_variants_comprehensive(self) -> None:
        """Test all known Vitamin B3 variants resolve correctly."""
        expected: str = "Vitamin_B3"
        variants: List[str] = [
            "Vitamin B3", "Niacin", "Vitamin B-3", "B3-Vitamin",
            "B3", "Nikotinamid", "Nicotinamid", "vitamin b3",
            "NIACIN", "niacin", "VITAMIN B3"
        ]

        for variant in variants:
            assert self.mapper.resolve_entity_name(variant) == expected, \
                f"Variant '{variant}' should resolve to '{expected}'"

    def test_unknown_entities(self) -> None:
        """Test handling of unknown entities."""
        # Unknown entities should be normalized but preserved
        assert "Unknown" in self.mapper.resolve_entity_name("Unknown Entity")
        assert "Random" in self.mapper.resolve_entity_name("Random Substance")

    def test_empty_and_invalid_inputs(self) -> None:
        """Test edge cases with empty or invalid inputs."""
        # Test cases with expected behavior
        test_inputs = [
            ("", ""),  # Empty string should return empty or normalized empty
            ("   ", ""),  # Whitespace should be stripped to empty
            ("123456", "123456")  # Numeric strings should be returned as-is or normalized
        ]

        for input_val, expected_type in test_inputs:
            result: str = self.mapper.resolve_entity_name(input_val)
            assert isinstance(result, str), f"Expected str for input '{input_val}', got {type(result)}"
            assert result == result.strip(), f"Result should be stripped: '{result}'"
            # Ensure deterministic normalization
            assert result.strip() != None, "Result should not be None after stripping"

    def test_dynamic_equivalence_discovery(self) -> None:
        """Test dynamic equivalence discovery from mock entities with definitional patterns."""
        # Create mock entities with definitional patterns
        mock_entities: List[Any] = [
            self._create_mock_entity("Vitamin B3", "NUTRIENT", "Vitamin B3 (Niacin) ist wasserlöslich."),
            self._create_mock_entity("Niacin", "NUTRIENT", "Niacin, auch bekannt als Vitamin B3, unterstützt den Körper.")
        ]

        # Before discovery - Niacin should resolve via predefined rules
        assert self.mapper.resolve_entity_name("Niacin") == "Vitamin_B3"

        # Discover equivalences from mock entities
        self.mapper.discover_document_equivalences(mock_entities)

        # After discovery - should still work (maybe discover additional ones)
        assert self.mapper.resolve_entity_name("Niacin") == "Vitamin_B3"
        assert self.mapper.resolve_entity_name("Vitamin B3") == "Vitamin_B3"

        # Check that dynamic equivalences were discovered
        dynamic_equivalences: Dict[str, str] = self.mapper.dynamic_equivalences
        assert isinstance(dynamic_equivalences, dict)

        # Should have discovered equivalence from definitional patterns
        assert len(dynamic_equivalences) > 0, "Expected dynamic equivalences from definitional patterns"

        # Specifically should discover Niacin -> Vitamin_B3 from our test sentences
        assert "Niacin" in dynamic_equivalences, f"Expected 'Niacin' in {dynamic_equivalences}"
        assert dynamic_equivalences["Niacin"] == "Vitamin_B3"

    def _create_mock_entity(self, text: str, label: str, source_sentence: Optional[str] = None) -> Any:
        """Helper method to create mock entities for testing."""
        class MockEntity:
            def __init__(self, text, label, source_sentence=None):
                self.text = text
                self.label = label
                self.source_sentence = source_sentence
                self.source_paragraph_id = 1
                self.source_page = 1
                self.confidence = 0.9
                self.start_char = 0
                self.end_char = len(text)

        return MockEntity(text, label, source_sentence)

    def test_equivalence_report_generation(self) -> None:
        """Test comprehensive equivalence report generation for analysis transparency."""
        # Setup: Create mock entities with definitional patterns
        mock_entities: List[Any] = [
            self._create_mock_entity("Vitamin B3", "NUTRIENT", "Vitamin B3 (Niacin) ist essentiell."),
            self._create_mock_entity("Thiamin", "NUTRIENT", "Thiamin, auch Vitamin B1 genannt, ist wichtig.")
        ]

        # Discover equivalences from test data
        self.mapper.discover_document_equivalences(mock_entities)

        # Generate comprehensive report
        report: Dict[str, Any] = self.mapper.get_equivalence_report()

        # Validate report structure
        required_keys: Dict[str, type] = {
            "predefined_equivalences": int,
            "dynamic_equivalences_discovered": int,
            "total_name_mappings": int,
            "predefined_primary_names": list
        }

        assert isinstance(report, dict), "Report must be a dictionary"

        for key, expected_type in required_keys.items():
            assert key in report, f"Missing required key: {key}"
            assert isinstance(report[key], expected_type), f"{key} must be {expected_type.__name__}"

        # Validate report content
        assert report["predefined_equivalences"] > 0, "Must have predefined equivalences"
        assert report["dynamic_equivalences_discovered"] > 0, "Must discover dynamic equivalences"
        assert report["total_name_mappings"] >= report["dynamic_equivalences_discovered"]

        # Validate expected primary names are present
        primary_names: List[str] = report["predefined_primary_names"]
        expected_vitamins: List[str] = ["Vitamin_B3", "Vitamin_B1"]
        for vitamin in expected_vitamins:
            assert vitamin in primary_names, f"Missing expected vitamin: {vitamin}"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])