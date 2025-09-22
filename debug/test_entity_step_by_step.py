#!/usr/bin/env python3
"""
Step-by-Step Entity Equivalence Testing Module

This module provides comprehensive step-by-step testing of the Entity Equivalence system,
progressively adding features to isolate and identify integration issues.

Purpose:
    - Test Entity Equivalence Mapper functionality incrementally
    - Validate EntityData object creation and attribute handling
    - Test equivalence discovery with increasing complexity
    - Isolate bugs by testing components individually
    - Verify predefined and discovered equivalences work correctly

How to Run:
    1. Ensure the package is installed in editable mode:
       pip install -e .
    2. Run directly: python debug/test_entity_step_by_step.py
    3. Or via pytest: pytest debug/test_entity_step_by_step.py -v -s

Prerequisites:
    - LocalInsightEngine package installed (pip install -e .)
    - Python 3.8+
    - Required dependencies from requirements.txt

Test Structure:
    Step 1: Basic name resolution (Niacin → Vitamin B3)
    Step 2: EntityData object creation with standard attributes
    Step 3: Dynamic attribute addition (source_sentence)
    Step 4: Equivalence report generation
    Step 5: Discovery testing with empty entity list
    Step 6: Discovery testing with single entity

Environment Variables:
    - PYTHONPATH: Alternative to editable install (not recommended)
    - LOG_LEVEL: Override default INFO logging level

Author: LocalInsightEngine Team
License: Same as project license
Reference: Part of Entity Equivalence debug toolkit
"""

import sys
import logging
from typing import Dict, Any, List, Optional

# Import LocalInsightEngine components
# If this fails, install the package in editable mode: pip install -e .
try:
    from local_insight_engine.services.processing_hub.entity_equivalence_mapper import EntityEquivalenceMapper
    from local_insight_engine.models.text_data import EntityData
except ImportError as e:
    print("❌ Failed to import LocalInsightEngine components.")
    print("   Please install the package in editable mode:")
    print("   pip install -e .")
    print("   Or set PYTHONPATH environment variable to include the src directory.")
    print(f"   Original error: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

logger.info("🧬 STEP-BY-STEP ENTITY EQUIVALENCE TEST")
logger.info("=" * 50)

try:
    # Step 1: Basic functionality (we know this works)
    logger.info("📍 STEP 1: Basic name resolution")
    mapper: EntityEquivalenceMapper = EntityEquivalenceMapper()
    result: str = mapper.resolve_entity_name("Niacin")
    logger.info("   ✅ Niacin → %s", result)

    # Step 2: Try creating EntityData objects
    logger.info("")
    logger.info("📍 STEP 2: Create EntityData objects")
    nutrient_entity: EntityData = EntityData(
        text="Vitamin B3",
        label="NUTRIENT",
        confidence=0.9,
        start_char=0,
        end_char=10,
        source_paragraph_id=1,
        source_page=1
    )
    logger.info("   ✅ EntityData created: %s", nutrient_entity.text)

    # Step 3: Try adding source_sentence attribute
    logger.info("")
    logger.info("📍 STEP 3: Add source_sentence attribute")
    setattr(nutrient_entity, 'source_sentence', "Vitamin B3 (Niacin) ist wichtig.")
    source_sentence: Optional[str] = getattr(nutrient_entity, 'source_sentence', None)
    logger.info("   ✅ source_sentence set: %s", source_sentence)

    # Step 4: Try the equivalence report (no discovery yet)
    logger.info("")
    logger.info("📍 STEP 4: Generate equivalence report")
    report: Dict[str, Any] = mapper.get_equivalence_report()
    logger.info("   ✅ Report generated: %d predefined", report['predefined_equivalences'])

    # Step 5: Try discovery with minimal entities list
    logger.info("")
    logger.info("📍 STEP 5: Test discovery with empty list")
    empty_entities: List[EntityData] = []
    mapper.discover_document_equivalences(empty_entities)
    logger.info("   ✅ Discovery with empty list succeeded")

    # Step 6: Try discovery with one entity
    logger.info("")
    logger.info("📍 STEP 6: Test discovery with one entity")
    entities: List[EntityData] = [nutrient_entity]
    mapper.discover_document_equivalences(entities)
    logger.info("   ✅ Discovery with one entity succeeded")

    logger.info("")
    logger.info("🎉 All steps successful! The issue must be in the complex test.")

except (OSError, ImportError) as e:
    logger.error("❌ Import or module loading error: %s", e)
    logger.exception("Full traceback:")
except AttributeError as e:
    logger.error("❌ Attribute or method error: %s", e)
    logger.exception("Full traceback:")
except Exception as e:
    logger.error("❌ Unexpected error at current step: %s", e)
    logger.exception("Full traceback:")

logger.info("")
logger.info("🔧 Now we know where the problem is!")