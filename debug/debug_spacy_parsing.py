#!/usr/bin/env python3
"""
Debug spaCy Dependency Parsing - Find out why no triples are extracted
"""

import logging
import sys
from typing import List, Optional

sys.path.append('src')
import spacy
from spacy.language import Language
from spacy.tokens import Doc, Token

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(message)s')

logger.info("🔍 SPACY DEPENDENCY PARSING DEBUG")
logger.info("=" * 50)

# Load German model
try:
    nlp: Language = spacy.load('de_core_news_sm')
    logger.info("✅ German spaCy model loaded")
except (OSError, ImportError) as exc:
    logger.error("❌ Could not load German model: %s", str(exc))
    sys.exit(1)

# Test sentence
test_sentence: str = "Vitamin B3 unterstützt den Energiestoffwechsel."
logger.info("\n📝 ANALYZING: %s", test_sentence)

doc: Doc = nlp(test_sentence)

logger.info("\n🔍 TOKEN ANALYSIS:")
logger.info("Token | Lemma | POS | Dep | Head | Children")
logger.info("-" * 55)

for token in doc:
    children: List[str] = [child.text for child in token.children]
    logger.info("%s | %s | %s | %s | %s | %s",
                f"{token.text:8}", f"{token.lemma_:8}", f"{token.pos_:4}",
                f"{token.dep_:8}", f"{token.head.text:8}", children)

logger.info("\n🎯 ROOT VERB SEARCH:")
root_verb: Optional[Token] = None
for token in doc:
    if token.dep_ == "ROOT":
        logger.info("ROOT found: %s (POS: %s, Lemma: %s)", token.text, token.pos_, token.lemma_)
        root_verb = token
        break

if not root_verb:
    logger.info("❌ No ROOT token found!")
    for token in doc:
        if token.pos_ == "VERB":
            logger.info("Alternative VERB found: %s (Dep: %s)", token.text, token.dep_)

if root_verb:
    logger.info("\n🔍 ANALYZING ROOT VERB: %s", root_verb.text)

    logger.info("\nSUBJECT SEARCH:")
    for child in root_verb.children:
        if child.dep_ in ["nsubj", "nsubjpass", "csubj"]:
            logger.info("  ✅ Subject found: %s (dep: %s)", child.text, child.dep_)
        else:
            logger.info("  - Child: %s (dep: %s)", child.text, child.dep_)

    logger.info("\nOBJECT SEARCH:")
    for child in root_verb.children:
        if child.dep_ in ["dobj", "iobj", "pobj", "attr", "oprd"]:
            logger.info("  ✅ Object found: %s (dep: %s)", child.text, child.dep_)
        elif child.dep_ == "prep":
            logger.info("  🔍 Preposition: %s", child.text)
            for grandchild in child.children:
                if grandchild.dep_ == "pobj":
                    logger.info("    ✅ Prep Object: %s", grandchild.text)

logger.info("\n" + "=" * 50)
logger.info("🧪 MANUAL TRIPLE EXTRACTION TEST:")

# Manual extraction logic
subject: Optional[str] = None
predicate: Optional[str] = None
objects: List[str] = []

# Find subject
for token in doc:
    if token.dep_ in ["nsubj", "nsubjpass"]:
        subject = token.text
        logger.debug("Found subject: %s (sentence: %s)", subject, doc.text)
        break

# Find predicate (ROOT verb)
for token in doc:
    if token.dep_ == "ROOT" and token.pos_ in ["VERB", "AUX"]:
        predicate = token.lemma_
        logger.debug("Found predicate: %s (sentence: %s)", predicate, doc.text)
        break

# Find objects
for token in doc:
    if token.dep_ in ["dobj", "pobj"]:
        objects.append(token.text)
        logger.debug("Found object: %s (sentence: %s)", token.text, doc.text)
    elif token.dep_ == "prep":
        for child in token.children:
            if child.dep_ == "pobj":
                objects.append(child.text)
                logger.debug("Found prep object: %s (sentence: %s)", child.text, doc.text)

logger.info("Subject: %s", subject)
logger.info("Predicate: %s", predicate)
logger.info("Objects: %s", objects)

if subject and predicate and objects:
    for obj in objects:
        logger.info("🎯 EXTRACTED TRIPLE: (%s, %s, %s)", subject, predicate, obj)
else:
    logger.error("❌ Could not extract complete triple")

logger.info("\n🔧 TRYING ALTERNATIVE SENTENCES:")
alternative_sentences: List[str] = [
    "Vitamin B3 ist wichtig.",
    "Das Vitamin unterstützt den Körper.",
    "B3 hilft dem Menschen."
]

for alt_sent in alternative_sentences:
    logger.info("\n📝 %s", alt_sent)
    alt_doc = nlp(alt_sent)

    alt_subject: Optional[str] = None
    alt_predicate: Optional[str] = None
    alt_objects: List[str] = []

    for token in alt_doc:
        logger.debug("Token: %s, Dep: %s, Lemma: %s", token.text, token.dep_, token.lemma_)
        if token.dep_ in ["nsubj", "nsubjpass"]:
            alt_subject = token.text
            logger.debug("Found alt subject: %s", alt_subject)
        elif token.dep_ == "ROOT":
            alt_predicate = token.lemma_
            logger.debug("Found alt predicate: %s", alt_predicate)
        elif token.dep_ in ["dobj", "pobj", "attr"]:
            alt_objects.append(token.text)
            logger.debug("Found alt object: %s", token.text)

    if alt_subject and alt_predicate and alt_objects:
        logger.info("   ✅ Triple: (%s, %s, %s)", alt_subject, alt_predicate, alt_objects[0])
    else:
        logger.info("   ❌ Incomplete: subj=%s, pred=%s, obj=%s", alt_subject, alt_predicate, alt_objects)


if __name__ == "__main__":
    pass  # All code above runs when script is executed directly