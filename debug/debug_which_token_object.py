#!/usr/bin/env python3
"""
Debug: Which exact token is being detected as object?
"""

import logging
import sys
from pathlib import Path
from typing import List, Optional, Tuple, Iterable

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


def find_root_verb(doc: Doc) -> Optional[Token]:
    """Find the ROOT token in a spaCy document.

    Args:
        doc: spaCy document to analyze

    Returns:
        The ROOT token if found, None otherwise
    """
    for token in doc:
        if token.dep_ == "ROOT":
            logger.debug("Found ROOT verb: %s", token.text)
            return token
    logger.debug("No ROOT token found")
    return None


def analyze_objects(
    root_verb: Token,
    extractor: FactTripletExtractor,
    logger: Optional[logging.Logger] = None
) -> List[str]:
    """Analyze object detection for a given root verb.

    Args:
        root_verb: The root verb token to analyze
        extractor: The FactTripletExtractor instance
        logger: Logger instance for output

    Returns:
        List of detected object phrases
    """
    if logger is None:
        logger = logging.getLogger(__name__)

    logger.info("MANUAL _find_objects() ANALYSIS:")
    object_labels = extractor.dependency_labels['german']['object']
    logger.info("German object labels: %s", object_labels)

    objects = []
    logger.info("\nChecking children of '%s':", root_verb.text)

    for child in root_verb.children:
        logger.debug(
            "  Child: '%s' (dep: %s, pos: %s)",
            child.text, child.dep_, child.pos_
        )
        if child.dep_ in object_labels:
            full_phrase = extractor._get_full_phrase(child)
            logger.info(
                "    ✅ DETECTED AS OBJECT! Full phrase: '%s'",
                full_phrase
            )
            logger.debug(
                "    📍 Token details: i=%s, lemma='%s', head='%s'",
                child.i, child.lemma_, child.head.text
            )
            objects.append(full_phrase)
        else:
            logger.debug(
                "    ❌ Not an object ('%s' not in %s)",
                child.dep_, object_labels
            )

    logger.info("\nFINAL objects list: %s", objects)
    return objects


def analyze_token_overlap(
    root_verb: Token,
    extractor: FactTripletExtractor,
    object_labels: Iterable[str]
) -> List[Tuple[str, str]]:
    """Analyze overlap between subject and object token detection.

    Args:
        root_verb: The root verb token to analyze
        extractor: The FactTripletExtractor instance
        object_labels: Iterable of object dependency labels

    Returns:
        List of tuples (token_text, role_description) for analysis
    """
    logger.info("🔍 TOKEN OVERLAP ANALYSIS:")
    subject_labels = extractor.dependency_labels['german']['subject']
    logger.info("Subject labels: %s", subject_labels)

    analysis_results = []

    for child in root_verb.children:
        is_subject = child.dep_ in subject_labels
        is_object = child.dep_ in object_labels

        if is_subject and is_object:
            role_desc = f"both subject AND object (dep: {child.dep_})"
            logger.warning(
                "  ⚠️  OVERLAP: '%s' is %s",
                child.text, role_desc
            )
            analysis_results.append((child.text, f"OVERLAP: {role_desc}"))
        elif is_subject:
            role_desc = f"subject (dep: {child.dep_})"
            logger.info("  📝 SUBJECT: '%s' (dep: %s)", child.text, child.dep_)
            analysis_results.append((child.text, f"SUBJECT: {role_desc}"))
        elif is_object:
            role_desc = f"object (dep: {child.dep_})"
            logger.info("  📦 OBJECT: '%s' (dep: %s)", child.text, child.dep_)
            analysis_results.append((child.text, f"OBJECT: {role_desc}"))

    return analysis_results


def main() -> None:
    """Main function to run the debug analysis."""
    logger.info("WHICH TOKEN IS OBJECT DEBUG")
    logger.info("=" * 50)

    # Initialize extractor
    try:
        extractor = FactTripletExtractor()
        if not extractor.nlp:
            logger.error("ERROR: No spaCy model available")
            sys.exit(1)
        logger.info("✅ FactTripletExtractor initialized successfully")
    except Exception as exc:
        logger.exception("Failed to initialize FactTripletExtractor: %s", str(exc))
        sys.exit(1)

    test_sentence: str = "Vitamin B3 ist wasserlöslich."
    logger.info("TEST: %s", test_sentence)

    doc = extractor.nlp(test_sentence)
    root_verb = find_root_verb(doc)

    if root_verb:
        logger.info("ROOT VERB: %s\n", root_verb.text)
    else:
        logger.error("No ROOT verb found in sentence")
        sys.exit(1)

    # Also check what subject detection finds
    logger.info("🔍 SUBJECT DETECTION:")
    subject = extractor._find_subject(root_verb)
    logger.info("Subject found: '%s'", subject)

    # Run the analysis
    objects = analyze_objects(root_verb, extractor, logger)
    object_labels = extractor.dependency_labels['german']['object']
    analysis_results = analyze_token_overlap(root_verb, extractor, object_labels)

    logger.info("\n" + "=" * 50)


if __name__ == "__main__":
    main()