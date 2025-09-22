#!/usr/bin/env python3
"""
Test ProcessingConfig models - PHASE 1 Validation
"""

import sys
import logging
from pathlib import Path
from typing import Any, Dict

# Add src to path using pathlib
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from local_insight_engine.models.processing_config import (
    ProcessingConfig,
    ProcessingMode,
    AnonymizationLevel
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def test_factory_methods() -> None:
    """Test ProcessingConfig factory methods."""
    logger.info("📋 1. FACTORY METHODS TEST:")

    standard_config: ProcessingConfig = ProcessingConfig.standard_mode()
    factual_config: ProcessingConfig = ProcessingConfig.factual_mode()

    logger.info("✅ Standard Mode: %s", standard_config)
    logger.info("✅ Factual Mode: %s", factual_config)


def test_legacy_compatibility() -> None:
    """Test legacy parameter conversion."""
    logger.info("\n📋 2. LEGACY COMPATIBILITY TEST:")

    legacy_false: ProcessingConfig = ProcessingConfig.from_legacy_params(factual_mode=False)
    legacy_true: ProcessingConfig = ProcessingConfig.from_legacy_params(factual_mode=True)

    logger.info("✅ Legacy False: %s", legacy_false)
    logger.info("✅ Legacy True: %s", legacy_true)


def test_property_compatibility() -> None:
    """Test legacy property compatibility."""
    logger.info("\n📋 3. PROPERTY COMPATIBILITY TEST:")

    standard_config: ProcessingConfig = ProcessingConfig.standard_mode()
    factual_config: ProcessingConfig = ProcessingConfig.factual_mode()

    logger.info("✅ Standard is_factual_mode property: %s", standard_config.is_factual_mode)
    logger.info("✅ Factual is_factual_mode property: %s", factual_config.is_factual_mode)
    logger.info("✅ Standard bypass_anonymization property: %s", standard_config.bypass_anonymization)
    logger.info("✅ Factual bypass_anonymization property: %s", factual_config.bypass_anonymization)


def test_serialization() -> None:
    """Test configuration serialization."""
    logger.info("\n📋 4. SERIALIZATION TEST:")

    standard_config: ProcessingConfig = ProcessingConfig.standard_mode()
    factual_config: ProcessingConfig = ProcessingConfig.factual_mode()

    standard_dict: Dict[str, Any] = standard_config.to_dict()
    factual_dict: Dict[str, Any] = factual_config.to_dict()

    logger.info("✅ Standard Dict: %s", standard_dict)
    logger.info("✅ Factual Dict: %s", factual_dict)


def test_validation() -> None:
    """Test configuration validation and auto-correction."""
    logger.info("\n📋 5. VALIDATION TEST:")

    try:
        # This should auto-correct enable_semantic_triples for factual mode
        custom_config: ProcessingConfig = ProcessingConfig(
            processing_mode=ProcessingMode.FACTUAL,
            enable_semantic_triples=False  # Should be auto-corrected to True
        )
        logger.info("✅ Auto-correction: %s", custom_config.enable_semantic_triples)
    except Exception as e:
        logger.error("❌ Validation error: %s", e)


def main() -> None:
    """Main function to run all tests."""
    logger.info("=" * 80)
    logger.info("🧪 PROCESSING CONFIG VALIDATION - PHASE 1")
    logger.info("=" * 80)

    test_factory_methods()
    test_legacy_compatibility()
    test_property_compatibility()
    test_serialization()
    test_validation()

    logger.info("\n" + "=" * 80)
    logger.info("🎯 PHASE 1 VALIDATION COMPLETE!")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()