#!/usr/bin/env python3
"""
Debug Content Flow - Trace einen Beispielsatz durch das System
"""

import sys
import os
import uuid
import traceback
from datetime import datetime
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from local_insight_engine.services.processing_hub.text_processor import TextProcessor
from local_insight_engine.models.document import Document, DocumentMetadata

# Beispiel-Dokument mit unserem Test-Satz
test_text = """
Vitamin B3 (Niacin) spielt eine wichtige Rolle im Energiestoffwechsel und hilft bei der Regeneration.
Vitamin B3 unterstützt die Funktion des Nervensystems und trägt zur normalen psychischen Funktion bei.
Ein Mangel an Vitamin B3 kann zu Müdigkeit und Konzentrationsproblemen führen.
"""

print("=" * 80)
print("🧪 CONTENT FLOW DEBUG - Vitamin B3 Beispiel")
print("=" * 80)

# Mock Document erstellen
metadata = DocumentMetadata(
    file_path=Path("test.txt"),
    file_format="txt",
    file_size=len(test_text),
    extraction_date=datetime.now().isoformat()
)

document = Document(
    id=str(uuid.uuid4()),
    text_content=test_text,
    metadata=metadata,
    paragraph_mapping={0: (0, len(test_text))},
    page_mapping={1: (0, len(test_text))},
    section_mapping={"main_section": (0, len(test_text))}
)

# Text Processor initialisieren
processor = TextProcessor(chunk_size=200, chunk_overlap=50)

print("\n📝 ORIGINAL TEXT:")
print(f"'{test_text.strip()}'")

print("\n🔍 PROCESSING MIT SACHBUCH-MODUS (bypass_anonymization=True):")
try:
    processed_factual = processor.process(document, bypass_anonymization=True)

    print(f"\n✅ Chunks erstellt: {len(processed_factual.chunks)}")
    print(f"✅ Entities extrahiert: {len(processed_factual.all_entities)}")

    for i, entity in enumerate(processed_factual.all_entities[:5]):
        print(f"  Entity {i+1}: '{entity.text}' -> {entity.label} (confidence: {entity.confidence:.2f})")

    print(f"\n📦 CHUNK CONTENT (was ans Q&A System geht):")
    for i, chunk in enumerate(processed_factual.chunks):
        print(f"\n--- CHUNK {i+1} ---")
        print(f"Word count: {chunk.word_count}")
        print(f"Entities in chunk: {len(chunk.entities)}")
        for entity in chunk.entities:
            print(f"  - {entity.text} ({entity.label})")
        print(f"\n📄 NEUTRALIZED CONTENT (an Claude):")
        print(f"'{chunk.neutralized_content}'")
        print("-" * 40)

except Exception as e:
    print(f"❌ ERROR: {e}")
    traceback.print_exc()

print("\n🔍 PROCESSING MIT NORMAL-MODUS (bypass_anonymization=False):")
try:
    processed_normal = processor.process(document, bypass_anonymization=False)

    print(f"\n✅ Chunks erstellt: {len(processed_normal.chunks)}")
    print(f"✅ Entities extrahiert: {len(processed_normal.all_entities)}")

    for i, entity in enumerate(processed_normal.all_entities[:5]):
        print(f"  Entity {i+1}: '{entity.text}' -> {entity.label} (confidence: {entity.confidence:.2f})")

    print(f"\n📦 CHUNK CONTENT (was ans Q&A System geht):")
    for i, chunk in enumerate(processed_normal.chunks):
        print(f"\n--- CHUNK {i+1} ---")
        print(f"📄 NEUTRALIZED CONTENT (an Claude):")
        print(f"'{chunk.neutralized_content}'")
        print("-" * 40)

except Exception as e:
    print(f"❌ ERROR: {e}")
    traceback.print_exc()

print("\n" + "=" * 80)
print("🎯 ANALYSE: Vergleiche die neutralized_content zwischen beiden Modi!")
print("=" * 80)