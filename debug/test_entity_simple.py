#!/usr/bin/env python3
"""
MINIMAL Entity Equivalence Test - Just the basics
"""

import sys
sys.path.append('src')

from local_insight_engine.services.processing_hub.entity_equivalence_mapper import EntityEquivalenceMapper

print("🧬 MINIMAL ENTITY EQUIVALENCE TEST")
print("=" * 40)

try:
    # Initialize mapper
    print("🔧 Creating EntityEquivalenceMapper...")
    mapper = EntityEquivalenceMapper()
    print("✅ Mapper created successfully!")

    # Test basic name resolution
    print("\n📝 Basic name resolution test:")
    test_cases = [
        ("Niacin", "Vitamin_B3"),
        ("Vitamin B3", "Vitamin_B3"),
        ("B3", "Vitamin_B3"),
        ("Unknown", "Unknown")
    ]

    for input_name, expected in test_cases:
        try:
            result = mapper.resolve_entity_name(input_name)
            status = "✅" if result == expected else "❌"
            print(f"   {status} '{input_name}' → '{result}' (expected: '{expected}')")
        except Exception as e:
            print(f"   ❌ ERROR with '{input_name}': {e}")

    print("\n🎉 Basic test completed!")

except Exception as e:
    print(f"❌ FATAL ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n🔧 If this works, we can add more features step by step.")