#!/usr/bin/env python3
"""
Debug: Triple creation step-by-step
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from local_insight_engine.services.processing_hub.fact_triplet_extractor import FactTripletExtractor

print("TRIPLE CREATION DEBUG")
print("=" * 50)

# Initialize extractor
extractor = FactTripletExtractor()

if not extractor.nlp:
    print("ERROR: No spaCy model available")
    sys.exit(1)

# Focus on the failing case
test_sentence = "Vitamin B3 ist wasserlöslich."
print(f"TEST: {test_sentence}")

doc = extractor.nlp(test_sentence)
sentence_span = list(doc.sents)[0]

# Find root verb
root_verb = None
for token in doc:
    if token.dep_ == "ROOT":
        root_verb = token
        break

print(f"ROOT VERB: {root_verb.text}")

# Step by step extraction
print(f"\nSTEP 1: Find subject")
subject = extractor._find_subject(root_verb)
print(f"  subject = '{subject}'")
print(f"  subject is truthy: {bool(subject)}")

print(f"\nSTEP 2: Find objects")
objects = extractor._find_objects(root_verb)
print(f"  objects = {objects}")
print(f"  objects is truthy: {bool(objects)}")

print(f"\nSTEP 2.5: Pre-filter self-referential objects")
if subject:
    normalized_subject = extractor._normalize_entity(subject)
    print(f"  normalized_subject = '{normalized_subject}'")
    original_objects = objects.copy()
    objects = [obj for obj in objects
              if extractor._normalize_entity(obj) != normalized_subject]
    print(f"  objects after filter = {objects} (was: {original_objects})")

print(f"\nSTEP 3: Check copula")
is_copula = extractor._is_copula_verb(root_verb)
print(f"  is_copula = {is_copula}")

if not objects and is_copula:
    print(f"\nSTEP 4: Find copula predicatives")
    copula_predicatives = extractor._find_copula_predicatives(root_verb)
    print(f"  copula_predicatives = {copula_predicatives}")
    print(f"  Setting objects = copula_predicatives")
    objects = copula_predicatives

print(f"\nFINAL CHECK:")
print(f"  subject = '{subject}' (truthy: {bool(subject)})")
print(f"  objects = {objects} (truthy: {bool(objects)})")
print(f"  subject and objects = {bool(subject and objects)}")

if subject and objects:
    print(f"\n  SHOULD CREATE TRIPLE!")
    predicate = extractor._normalize_copula_predicate(root_verb)
    print(f"  predicate = '{predicate}'")
else:
    print(f"\n  NO TRIPLE CREATED - MISSING DATA")

print("\n" + "=" * 50)