#!/usr/bin/env python3
"""
Debug spaCy parsing of 'ist' constructions
"""

from typing import List
import spacy
from spacy.language import Language
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)




def analyze_sentence(sentence: str, nlp: Language, logger: logging.Logger) -> None:
    """
    Analyze a single sentence for 'ist' constructions and syntactic relationships.

    Args:
        sentence: Input sentence to analyze
        nlp: Trained spaCy Language model
        logger: Logger instance for output
    """
    logger.info("")
    logger.info("📝 ANALYZING: %s", sentence)
    doc = nlp(sentence)

    logger.info("")
    logger.info("🔍 TOKEN ANALYSIS:")
    logger.info("Token | Lemma | POS | Dep | Head | Children")
    logger.info("-" * 55)

    for token in doc:
        children = [child.text for child in token.children]
        # Split long f-string to stay under 88 characters
        token_info = f"{token.text:8} | {token.lemma_:8} | {token.pos_:4}"
        dep_info = f" | {token.dep_:8} | {token.head.text:8} | {children}"
        logger.debug("%s%s", token_info, dep_info)

    logger.info("")
    logger.info("🎯 ROOT ANALYSIS:")
    root_tokens = [token for token in doc if token.dep_ == "ROOT"]
    for root in root_tokens:
        logger.info("ROOT: %s (POS: %s, Lemma: %s)", root.text, root.pos_, root.lemma_)

        # Find subject
        subjects = [child for child in root.children
                   if child.dep_ in ["nsubj", "nsubjpass", "csubj"]]
        logger.info("SUBJECTS: %s", [s.text for s in subjects])

        # Find predicates/attributes
        predicatives = [child for child in root.children
                       if child.dep_ in ["attr", "acomp", "xcomp", "ccomp"]]
        logger.info("PREDICATIVES: %s", [p.text for p in predicatives])

        # Find objects
        objects = [child for child in root.children
                  if child.dep_ in ["dobj", "iobj", "pobj"]]
        logger.info("OBJECTS: %s", [o.text for o in objects])

    logger.info("=" * 50)


def process_sentences(sentences: List[str], nlp: Language) -> None:
    """
    Process a list of sentences for 'ist' construction analysis.

    Args:
        sentences: List of sentences to analyze
        nlp: Trained spaCy Language model
    """
    logger.info("🔍 SPACY 'IST' CONSTRUCTION ANALYSIS")
    logger.info("=" * 50)

    for sentence in sentences:
        analyze_sentence(sentence, nlp, logger)


if __name__ == "__main__":
    # Test "ist" sentences
    ist_sentences: List[str] = [
        "Vitamin B3 ist wasserlöslich.",
        "Niacin ist wichtig.",
        "Magnesium ist ein Mineral."
    ]

    # Load German model
    try:
        nlp = spacy.load('de_core_news_sm')
        logger.info("✅ German spaCy model loaded")
    except (OSError, ImportError) as e:
        logger.error("❌ Could not load German model: %s", e)
        logger.error("Install with: python -m spacy download de_core_news_sm")
        sys.exit(1)

    process_sentences(ist_sentences, nlp)