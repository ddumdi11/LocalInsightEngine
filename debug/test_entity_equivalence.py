#!/usr/bin/env python3
"""
Test Entity Equivalence Mapping - Standalone test for scientific name resolution
"""

import sys
import logging
import traceback
from dataclasses import dataclass
from typing import Optional
import pytest

from src.local_insight_engine.services.processing_hub.entity_equivalence_mapper import EntityEquivalenceMapper
from src.local_insight_engine.models.text_data import EntityData


@dataclass
class TestEntityData:
    """Wrapper for EntityData with additional test-specific fields."""
    entity: EntityData
    source_sentence: Optional[str] = None


def main() -> None:
    """Run entity equivalence mapping tests."""
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("🧬 ENTITY EQUIVALENCE MAPPING - STANDALONE TEST")
    logger.info("=" * 65)
    logger.info("")

    # Initialize the mapper
    logger.info("🔧 Initializing EntityEquivalenceMapper...")
    try:
        mapper = EntityEquivalenceMapper()
        logger.info("✅ Mapper initialized successfully!")
    except Exception as e:
        error_msg = f"Failed to initialize EntityEquivalenceMapper: {e.__class__.__name__}: {e}"
        logger.error(error_msg)
        pytest.fail(error_msg)
    logger.info("")

    # Test predefined equivalences
    logger.info("📚 PREDEFINED EQUIVALENCES TEST:")
    logger.info("-" * 35)

    test_names = [
        "Niacin",
        "Vitamin B3",
        "Vitamin B-3",
        "B3",
        "Nikotinamid",
        "Thiamin",
        "Vitamin B1",
        "Riboflavin",
        "Vitamin B2",
        "Cobalamin",
        "Vitamin B12",
        "Unknown Entity"
    ]

    for name in test_names:
        resolved = mapper.resolve_entity_name(name)
        status = "✅" if resolved != name.replace(" ", "_") else "➡️"
        logger.info(f"   {status} '{name}' → '{resolved}'")

    # Test dynamic document equivalence discovery
    logger.info("")
    logger.info("🔬 DYNAMIC DOCUMENT EQUIVALENCE DISCOVERY:")
    logger.info("-" * 48)

    # Create mock entities for testing
    mock_entity_1 = EntityData(
        text="Vitamin B3",
        label="NUTRIENT",
        source_paragraph_id=1,
        source_page=1
    )

    mock_entity_2 = EntityData(
        text="Niacin",
        label="NUTRIENT",
        source_paragraph_id=2,
        source_page=1
    )

    test_entities = [
        TestEntityData(mock_entity_1, "Vitamin B3 (Niacin) ist wichtig für den Energiestoffwechsel."),
        TestEntityData(mock_entity_2, "Niacin, auch bekannt als Vitamin B3, unterstützt den Körper.")
    ]

    logger.info("📝 Created test entities with source sentences:")
    for i, test_entity in enumerate(test_entities, 1):
        logger.info(f"   {i}. {test_entity.entity.text}: '{test_entity.source_sentence}'")

    logger.info("")
    logger.info("🧠 Discovering document-specific equivalences...")
    try:
        # Extract entities for discovery process
        entities_for_discovery = [test_entity.entity for test_entity in test_entities]
        mapper.discover_document_equivalences(entities_for_discovery)
        logger.info("✅ Document equivalence discovery completed!")

        # Display discovered equivalences
        dynamic_equiv = mapper.dynamic_equivalences
        logger.info(f"📊 Found {len(dynamic_equiv)} dynamic equivalences:")
        for alt_name, primary_name in dynamic_equiv.items():
            logger.info(f"   🔗 '{alt_name}' → '{primary_name}'")

    except Exception as e:
        logger.error(f"❌ Discovery failed: {e}")
        traceback.print_exc()

    # Test mapping statistics
    logger.info("")
    logger.info("📊 MAPPING STATISTICS:")
    logger.info("-" * 25)

    report = mapper.get_mapping_statistics()
    logger.info(f"   📈 Total predefined mappings: {report['total_predefined_mappings']}")
    logger.info(f"   🔄 Total dynamic mappings: {report['total_dynamic_mappings']}")
    logger.info(f"   🔗 Total name mappings: {report['total_name_mappings']}")

    logger.info("")
    logger.info("   🎯 Primary canonical names:")
    for primary in report['predefined_primary_names'][:10]:  # Show first 10
        logger.info(f"      • {primary}")

    if len(report['predefined_primary_names']) > 10:
        logger.info(f"      ... and {len(report['predefined_primary_names']) - 10} more")

    logger.info("")

    # Test the core use case: Vitamin B3 variants
    logger.info("🧪 VITAMIN B3 VARIANT RESOLUTION TEST:")
    logger.info("-" * 42)

    vitamin_b3_variants = [
        "Vitamin B3",
        "Niacin",
        "Vitamin B-3",
        "B3-Vitamin",
        "B3",
        "Nikotinamid",
        "Nicotinamid",
        "vitamin b3",
        "NIACIN"
    ]

    logger.info("All variants should resolve to 'Vitamin_B3':")
    all_resolved_correctly = True

    for variant in vitamin_b3_variants:
        resolved = mapper.resolve_entity_name(variant)
        is_correct = resolved == "Vitamin_B3"
        status = "✅" if is_correct else "❌"
        logger.info(f"   {status} '{variant}' → '{resolved}'")

        if not is_correct:
            all_resolved_correctly = False

    logger.info("")
    if all_resolved_correctly:
        logger.info("🎉 SUCCESS: All Vitamin B3 variants correctly resolved!")
        logger.info("💡 Ready for integration into FactTripletExtractor!")
    else:
        logger.warning("⚠️  Some variants not resolved correctly - needs adjustment")

    logger.info("")
    logger.info("🔬 Entity Equivalence Mapping test complete!")
    logger.info("   Next: Integrate into FactTripletExtractor for unified triple extraction")


if __name__ == "__main__":
    main()