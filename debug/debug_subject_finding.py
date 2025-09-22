#!/usr/bin/env python3
"""
Debug: Subject finding in detail
"""

import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
from spacy.tokens import Doc, Span, Token

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from local_insight_engine.services.processing_hub.fact_triplet_extractor import FactTripletExtractor

logger.debug("DETAILED SUBJECT FINDING DEBUG")
logger.debug("=" * 50)

# Initialize extractor
extractor = FactTripletExtractor()

if not extractor.nlp:
    logger.error("❌ No spaCy model available")
    sys.exit(1)

# Test sentence
test_sentence: str = "Vitamin B3 ist wasserlöslich."
logger.info(f"📝 Test sentence: {test_sentence}")

doc: Doc = extractor.nlp(test_sentence)
sentence_span: Span = list(doc.sents)[0]

# Find root verb
root_verb: Optional[Token] = None
for token in doc:
    if token.dep_ == "ROOT":
        root_verb = token
        break

if root_verb is None:
    logger.warning("⚠️ No root verb found")
    subject = None
else:
    logger.info(f"🎯 ROOT VERB: {root_verb.text}")
    # Test _find_subject method
    subject = extractor._find_subject(root_verb)
    logger.info(f"📊 _find_subject() result: '{subject}'")

# Debug the subject finding process step by step
if root_verb is not None:
    logger.debug("🔍 Manual subject finding:")
    german_labels: Dict[str, Any] = extractor.dependency_labels['german']
    subject_labels: List[str] = german_labels['subject']
    logger.debug(f"Subject labels: {subject_labels}")

    logger.debug(f"Children of ROOT verb '{root_verb.text}':")
    for child in root_verb.children:
        logger.debug(f"  {child.text} (dep: {child.dep_}, pos: {child.pos_})")
        if child.dep_ in subject_labels:
            logger.debug(f"    ✅ This is a subject! Calling _get_full_phrase()...")
            full_phrase: str = extractor._get_full_phrase(child)
            logger.debug(f"    📝 Full phrase: '{full_phrase}'")

logger.debug("=" * 50)