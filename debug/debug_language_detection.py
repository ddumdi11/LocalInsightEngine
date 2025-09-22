#!/usr/bin/env python3
"""
Debug: Check language detection and copula handling in FactTripletExtractor
"""

import sys
sys.path.append('../src')

from local_insight_engine.services.processing_hub.fact_triplet_extractor import FactTripletExtractor

print("🔍 LANGUAGE DETECTION & COPULA DEBUG")
print("=" * 50)

# Initialize extractor
extractor = FactTripletExtractor()

if not extractor.nlp:
    print("❌ No spaCy model available")
    sys.exit(1)

print("✅ FactTripletExtractor initialized")

# Check current language setting
print(f"\n🌍 Current language: {extractor.current_language}")
print(f"📝 Available languages: {list(extractor.dependency_labels.keys())}")

# Test German sentence
test_sentence = "Vitamin B3 ist wasserlöslich."
print(f"\n📝 Test sentence: {test_sentence}")

doc = extractor.nlp(test_sentence)
sentence_span = list(doc.sents)[0]

# Language is already set to German - no detection needed
print(f"🔍 Language already set correctly: {extractor.current_language}")

# Manually check German labels
german_labels = extractor.dependency_labels['german']
print(f"\n🇩🇪 German dependency labels:")
print(f"   Subject: {german_labels['subject']}")
print(f"   Object: {german_labels['object']}")
print(f"   Copula: {german_labels['copula']}")

# Debug the actual parsing
print(f"\n🔍 Manual parsing with German labels:")
for token in doc:
    if token.dep_ == "ROOT":
        print(f"ROOT: {token.text} (POS: {token.pos_})")

        # Test subject finding with German labels
        for child in token.children:
            if child.dep_ in german_labels['subject']:
                print(f"   ✅ SUBJECT found: {child.text} (dep: {child.dep_})")
            elif child.dep_ in german_labels['copula']:
                print(f"   ✅ COPULA found: {child.text} (dep: {child.dep_})")
            else:
                print(f"   ➡️  Child: {child.text} (dep: {child.dep_})")

# Test actual extraction
print(f"\n🧪 Actual triple extraction:")
triples = extractor._extract_triples_from_sentence(sentence_span)
print(f"   Extracted {len(triples)} triples:")
for triple in triples:
    print(f"      • {triple}")

print("\n" + "=" * 50)