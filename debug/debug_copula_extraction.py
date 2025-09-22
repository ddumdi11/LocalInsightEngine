#!/usr/bin/env python3
"""
Debug: Copula extraction detailed analysis
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from local_insight_engine.services.processing_hub.fact_triplet_extractor import FactTripletExtractor

print("COPULA EXTRACTION DEBUG")
print("=" * 50)

# Initialize extractor
extractor = FactTripletExtractor()

if not extractor.nlp:
    print("ERROR: No spaCy model available")
    sys.exit(1)

# Test sentences
test_sentences = [
    "Vitamin B3 ist wasserlöslich.",
    "Niacin ist wichtig.",
    "Magnesium ist ein Mineral."
]

for sentence in test_sentences:
    print(f"\nTEST: {sentence}")
    doc = extractor.nlp(sentence)
    sentence_span = list(doc.sents)[0]

    # Show all tokens first
    print("  ALL TOKENS:")
    for i, token in enumerate(doc):
        print(f"    {i}: '{token.text}' (pos: {token.pos_}, dep: {token.dep_}, head: {token.head.text})")

    # Find root verb
    root_verb = None
    for token in doc:
        if token.dep_ == "ROOT":
            root_verb = token
            break

    print(f"\n  ROOT: {root_verb.text} (pos: {root_verb.pos_})")
    print(f"  Is copula: {extractor._is_copula_verb(root_verb)}")

    if extractor._is_copula_verb(root_verb):
        print("  COPULA ANALYSIS:")

        # Check subject
        subject = extractor._find_subject(root_verb)
        print(f"    Subject: '{subject}'")

        # Check copula predicatives
        predicatives = extractor._find_copula_predicatives(root_verb)
        print(f"    Predicatives: {predicatives}")

        # Check German copula labels
        german_labels = extractor.dependency_labels['german']
        print(f"    German copula labels: {german_labels['copula']}")

    # Try actual extraction
    triples = extractor._extract_triples_from_sentence(sentence_span)
    print(f"\n  EXTRACTED: {len(triples)} triples")
    for triple in triples:
        print(f"    {triple}")

    print("-" * 30)

print("\n" + "=" * 50)