#!/usr/bin/env python3
"""
Debug: Token structure analysis for compound names
"""

import logging
import sys
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import spacy
from spacy.tokens import Doc, Token
from local_insight_engine.services.processing_hub.fact_triplet_extractor import (
    FactTripletExtractor
)

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

logger.info("TOKEN STRUCTURE ANALYSIS")
logger.info("=" * 50)

# Initialize extractor
try:
    extractor = FactTripletExtractor()
    if not extractor.nlp:
        logger.error("ERROR: No spaCy model available")
        sys.exit(1)
    logger.info("✅ FactTripletExtractor initialized successfully")
except Exception as exc:
    logger.exception(
        "Failed to initialize FactTripletExtractor: %s", str(exc)
    )
    sys.exit(1)

# Test sentence
test_sentence: str = "Vitamin B3 ist wasserlöslich."
logger.info("Test sentence: %s", test_sentence)

try:
    doc: Doc = extractor.nlp(test_sentence)
except Exception as exc:
    logger.exception("Failed to process sentence with spaCy: %s", str(exc))
    sys.exit(1)

logger.info("\nALL TOKENS:")
for i, token in enumerate(doc):
    token: Token  # Type annotation for clarity
    children: List[str] = [child.text for child in token.children]
    logger.debug(
        "  %d: '%s' (pos: %s, dep: %s, head: %s, children: %s)",
        i, token.text, token.pos_, token.dep_, token.head.text, children
    )

# Find the subject token
subject_token: Optional[Token] = None
for token in doc:
    if token.dep_ == "sb":  # German subject
        subject_token = token
        break

if subject_token:
    logger.info("\nSUBJECT TOKEN: '%s'", subject_token.text)
    logger.info("  Position: %d", subject_token.i)
    logger.info(
        "  Head: '%s' (pos: %s, dep: %s)",
        subject_token.head.text, subject_token.head.pos_, subject_token.head.dep_
    )
    children: List[str] = [child.text for child in subject_token.children]
    logger.info("  Children: %s", children)

    # Check siblings (tokens with same head)
    siblings: List[Token] = [
        token for token in doc
        if token.head == subject_token.head and token != subject_token
    ]
    logger.debug("  Siblings: %s", [sib.text for sib in siblings])

    # Check if there are tokens that depend on the subject
    dependents: List[Token] = [
        token for token in doc if token.head == subject_token
    ]
    logger.debug("  Dependents: %s", [dep.text for dep in dependents])

    # Look for compound or modifier relationships
    logger.info("\nNEARBY TOKENS ANALYSIS:")
    for token in doc:
        if abs(token.i - subject_token.i) <= 2:  # Within 2 positions
            logger.info(
                "  %d: '%s' -> head: '%s', dep: %s",
                token.i, token.text, token.head.text, token.dep_
            )

logger.info("\n" + "=" * 50)


if __name__ == "__main__":
    pass  # All code above runs when script is executed directly