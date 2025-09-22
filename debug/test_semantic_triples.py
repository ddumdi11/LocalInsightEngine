#!/usr/bin/env python3
"""
Test Semantic Triples Pipeline - Direct testing of fact extraction
"""

import logging
import sys
from typing import List, Tuple

sys.path.append('src')

import spacy
from spacy.tokens import Doc, Span
from local_insight_engine.services.processing_hub.fact_triplet_extractor import (
    FactTripletExtractor
)
from local_insight_engine.models.semantic_triples import Triple

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

logger.info("🧪 SEMANTIC TRIPLES PIPELINE - DIRECT TEST")
logger.info("=" * 60)

# Test sentences with Vitamin B3
test_sentences: List[str] = [
    "Vitamin B3 unterstützt den Energiestoffwechsel.",
    "Vitamin B3 ist wasserlöslich.",
    "Niacin fördert die Nervenfunktion.",
    "Vitamin B3 hilft bei der Regeneration und ist wichtig für den Körper.",
    "Ein Mangel an Vitamin B3 kann zu Müdigkeit führen."
]

logger.info("🔧 Initializing FactTripletExtractor...")
try:
    extractor: FactTripletExtractor = FactTripletExtractor()
    if not extractor.nlp:
        logger.error("❌ No spaCy model available - install with:")
        logger.error("   python -m spacy download de_core_news_sm")
        sys.exit(1)
    logger.info("✅ spaCy model loaded successfully!")
except Exception as exc:
    logger.exception(
        "Failed to initialize FactTripletExtractor: %s", str(exc)
    )
    sys.exit(1)

logger.info("")

for i, sentence in enumerate(test_sentences, 1):
    sentence: str  # Type annotation for clarity
    logger.info("📝 SENTENCE %d: %s", i, sentence)

    # Process with spaCy
    try:
        doc: Doc = extractor.nlp(sentence)
        sentence_span: Span = list(doc.sents)[0]

        # Extract triples using private method (required for detailed testing)
        # Note: Using private method for debugging purposes to test extraction logic
        triples: List[Triple] = extractor._extract_triples_from_sentence(sentence_span)

        logger.info("   🔍 Extracted %d triples:", len(triples))
        for triple in triples:
            logger.info("      %s", triple)

    except Exception as exc:
        logger.exception("Failed to process sentence: %s", str(exc))
        continue

    logger.info("")

logger.info("🎯 VITAMIN B3 SEARCH TEST:")
logger.info("=" * 30)

# Simulate search for Vitamin B3 information
all_triples: List[Triple] = []
for sentence in test_sentences:
    sentence: str  # Type annotation for clarity
    try:
        doc: Doc = extractor.nlp(sentence)
        for sent in doc.sents:
            sent: Span  # Type annotation for clarity
            # Using private method for detailed triple extraction testing
            triples: List[Triple] = extractor._extract_triples_from_sentence(sent)
            all_triples.extend(triples)
    except Exception as exc:
        logger.exception("Failed to extract triples from sentence: %s", str(exc))
        continue

# Find triples about Vitamin B3
vitamin_b3_triples: List[Triple] = []
for triple in all_triples:
    if ('vitamin_b3' in triple.subject.lower() or
        'vitamin_b3' in triple.object.lower()):
        vitamin_b3_triples.append(triple)

logger.info("📊 Found %d facts about Vitamin B3:", len(vitamin_b3_triples))
for triple in vitamin_b3_triples:
    logger.info(
        "   • %s → %s → %s",
        triple.subject, triple.predicate, triple.object
    )

logger.info("🤖 LLM CONTEXT FORMAT:")
logger.info("-" * 25)

if vitamin_b3_triples:
    context_lines: List[str] = ["EXTRACTED FACTS ABOUT VITAMIN B3:"]
    for triple in vitamin_b3_triples:
        context_lines.append(
            f"- {triple.subject} {triple.predicate} {triple.object}"
        )

    context: str = "\n".join(context_lines)
    logger.info(context)
else:
    logger.warning("❌ No facts about Vitamin B3 found!")

logger.info("🎉 Test complete! Ready for full pipeline integration.")


if __name__ == "__main__":
    pass  # All code above runs when script is executed directly