# spaCy German Model Analysis - Post-Upgrade Verification Guide

## Status: Pre-Upgrade Analysis Complete (de_core_news_sm → de_core_news_lg)

This document summarizes all parsing issues identified with the small German model and provides systematic tests to verify improvements after upgrading to the large model.

## 🔍 **IDENTIFIED PROBLEMS (with de_core_news_sm)**

### Problem 1: Inconsistent Copula Subject Detection
**Issue:** Same sentence pattern, different dependency labels
- ✅ "Niacin ist wichtig" → "Niacin" = **sb** (subject)
- ❌ "Magnesium ist ein Mineral" → "Magnesium" = **pd** (predicative)

**Expected after upgrade:** Consistent **sb** labels for subjects

### Problem 2: Conjunction Splitting Failure
**Issue:** Compound sentences treated as single ROOT
- ❌ "Vitamin B3 hilft bei der Regeneration und ist wichtig für den Körper"
- Only ROOT = "hilft", "ist wichtig" as **cj** (conjunction) ignored

**Expected after upgrade:** Better recognition of coordinated clauses

### Problem 3: Modal Verb Complex Constructions
**Issue:** Nested verb-object relationships not captured
- ❌ "Ein Mangel an Vitamin B3 kann zu Müdigkeit führen"
- ROOT = "kann", "führen" = **oc**, "Müdigkeit" deeply nested

**Expected after upgrade:** Clearer modal-infinitive-object chains

### Problem 4: Weird Sentence Splitting
**Issue:** Incorrect sentence boundaries
- "Ein Mangel an Vitamin B3 kann zu Müdigkeit führen"
- Split into: "Ein Mangel an Vitamin" + "B3 kann zu Müdigkeit führen"

**Expected after upgrade:** Proper sentence boundary detection

## ✅ **WORKING PATTERNS (to verify no regression)**

1. **Simple Copula:** "Vitamin B3 ist wasserlöslich" → (Vitamin_B3, has_property, wasserlöslich)
2. **Simple Transitive:** "Vitamin B3 unterstützt den Energiestoffwechsel"
3. **Negation with Prep:** "Ohne Niacin funktioniert der Stoffwechsel nicht"

## 🧪 **SYSTEMATIC VERIFICATION TESTS**

### Test 1: Debug Scripts Comparison
**Commands:**
```bash
cd debug
python debug_complex_sentences.py > output_before_upgrade.txt
# After model change:
python debug_complex_sentences.py > output_after_upgrade.txt
diff output_before_upgrade.txt output_after_upgrade.txt
```

### Test 2: Semantic Triples Test Status
**Command:**
```bash
python -m pytest test_semantic_triples.py -v
```
**Current Status:** 7/9 GREEN
**Target after upgrade:** 9/9 GREEN (without code changes)

### Test 3: Specific Copula Consistency Test
**Target sentences:**
- "Vitamin B3 ist wasserlöslich" → should maintain functionality
- "Niacin ist wichtig" → should maintain functionality
- "Magnesium ist ein Mineral" → should FIX subject detection

### Test 4: Conjunction Analysis
**Target sentence:**
- "Vitamin B3 hilft bei der Regeneration und ist wichtig für den Körper"
- Expected improvement: Better clause coordination recognition

### Test 5: Modal Construction Analysis
**Target sentences:**
- "Ein Mangel an Vitamin B3 kann zu Müdigkeit führen"
- "Vitamin B3 sollte täglich eingenommen werden"
- Expected improvement: Clearer verb-object relationships

## 📋 **POST-UPGRADE CHECKLIST**

### Phase 1: Model Integration
- [ ] Update spaCy model name in code: `de_core_news_sm` → `de_core_news_lg`
- [ ] Verify model loads successfully
- [ ] Run regression tests (all existing GREEN tests remain GREEN)

### Phase 2: Parsing Quality Verification
- [ ] Run debug_complex_sentences.py with new model
- [ ] Compare dependency structures (before/after)
- [ ] Document parsing improvements

### Phase 3: Test Impact Assessment
- [ ] Run test_semantic_triples.py
- [ ] Check if failed tests turn GREEN automatically
- [ ] Identify remaining issues requiring code changes

### Phase 4: TDD Cycle Planning
- [ ] Update TDD_DIARY.md with new status
- [ ] Plan next RED-GREEN-REFACTOR cycles for remaining failures
- [ ] Focus on logic improvements vs. parsing corrections

## 🎯 **SUCCESS METRICS**

**Minimum Success:**
- No regression in existing GREEN tests
- At least 1 additional test turns GREEN
- Improved dependency consistency

**Optimal Success:**
- All 9/9 tests GREEN without code changes
- Consistent copula subject detection
- Better modal verb parsing

## 📁 **REFERENCE FILES**

**Debug Scripts:**
- `debug_complex_sentences.py` - Main analysis tool
- `debug_spacy_parsing.py` - General spaCy debugging

**Test Files:**
- `test_semantic_triples.py` - Target for 9/9 GREEN
- `test_orchestrator.py` - Regression prevention

**Documentation:**
- `TDD_DIARY.md` - Current status tracking
- `SEMANTIC_TRIPLES_ROADMAP.md` - Original problem analysis

## 🚀 **NEXT ACTIONS**

1. **Update model name** in spaCy loader code
2. **Run verification checklist** systematically
3. **Document improvements** vs. remaining challenges
4. **Plan targeted fixes** for any remaining failures

---
*Created during spaCy model upgrade analysis - September 2025*