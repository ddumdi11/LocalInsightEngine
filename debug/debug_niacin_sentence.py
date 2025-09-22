#!/usr/bin/env python3
"""
Debug: Warum funktioniert "Niacin fördert die Nervenfunktion" nicht?
"""

import logging
import sys
from typing import List, Optional

sys.path.append('src')

import spacy
from spacy.tokens import Doc, Token
from local_insight_engine.services.processing_hub.fact_triplet_extractor import (
    FactTripletExtractor
)
from local_insight_engine.models.semantic_triples import FactTriplet

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

logger.info("🔍 DEBUG: NIACIN SENTENCE ANALYSIS")
logger.info("=" * 45)

# Initialize extractor
try:
    extractor: FactTripletExtractor = FactTripletExtractor()
    if not extractor.nlp:
        logger.error("❌ No spaCy model available")
        sys.exit(1)
    logger.info("✅ FactTripletExtractor initialized successfully")
except Exception as exc:
    logger.exception(
        "Failed to initialize FactTripletExtractor: %s", str(exc)
    )
    sys.exit(1)

# Test sentence
sentence: str = "Niacin fördert die Nervenfunktion."
logger.info("📝 Analyzing: %s", sentence)

# Process with spaCy
doc: Doc = extractor.nlp(sentence)

logger.info("\n🔍 TOKEN ANALYSIS:")
logger.info("Token | Lemma | POS | Dep | Head | Children")
logger.info("-" * 55)

for token in doc:
    children: List[str] = [child.text for child in token.children]
    logger.info(
        "%s | %s | %s | %s | %s | %s",
        f"{token.text:8}",
        f"{token.lemma_:8}",
        f"{token.pos_:4}",
        f"{token.dep_:8}",
        f"{token.head.text:8}",
        children
    )

# Find ROOT verb
logger.info("\n🎯 ROOT VERB SEARCH:")
root_verb: Optional[Token] = None
for token in doc:
    if token.dep_ == "ROOT":
        logger.info("ROOT found: %s (Lemma: %s)", token.text, token.lemma_)
        root_verb = token
        break

if root_verb:
    logger.info("\n🔍 ANALYZING ROOT VERB: %s", root_verb.text)

    # Test subject finding
    logger.info("\nSUBJECT SEARCH:")
    subject: Optional[str] = extractor._find_subject(root_verb)
    logger.info("Found subject: %s", subject)

    # Test object finding
    logger.info("\nOBJECT SEARCH:")
    objects: List[str] = extractor._find_objects(root_verb)
    logger.info("Found objects: %s", objects)

    # Test entity normalization
    if subject:
        logger.info("\nENTITY NORMALIZATION:")
        normalized_subject = extractor._normalize_entity(subject)
        logger.info("'%s' → '%s'", subject, normalized_subject)

        # Test direct entity mapper
        direct_resolved = extractor.entity_mapper.resolve_entity_name(subject)
        logger.info(
            "Direct entity mapper: '%s' → '%s'",
            subject, direct_resolved
        )

    # Test predicate normalization
    predicate = extractor._normalize_predicate(root_verb.lemma_)
    logger.info("\nPREDICATE: '%s' → '%s'", root_verb.lemma_, predicate)

    # Try manual triple construction
    if subject and objects:
        for obj in objects:
            norm_obj = extractor._normalize_entity(obj)
            logger.info("\n🎯 MANUAL TRIPLE:")
            logger.info("   Subject: '%s' → '%s'", subject, normalized_subject)
            logger.info("   Predicate: '%s' → '%s'", root_verb.lemma_, predicate)
            logger.info("   Object: '%s' → '%s'", obj, norm_obj)
# Test actual extraction
logger.info("\n🧪 ACTUAL EXTRACTION TEST:")
sentence_span = list(doc.sents)[0]
triples: List[FactTriplet] = extractor._extract_triples_from_sentence(sentence_span)
logger.info("Extracted %d triples:", len(triples))
for triple in triples:
    logger.info("   %s", triple)

logger.info("\n🔧 This should help identify where the extraction fails!")


if __name__ == "__main__":
    pass  # All code above runs when script is executed directly