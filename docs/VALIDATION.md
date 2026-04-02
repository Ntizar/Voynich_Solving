# Validation Framework -- Protocol and Results

**Date:** Session 15 (April 2026)  
**Status:** Phases 0-4 complete. Phases 5-10 pending.  
**Critical finding:** The F1 metric is non-discriminative. Alternative metrics needed.

---

## Design Philosophy

This validation framework was designed as a **two-layer protocol**:

1. **Scientific validation:** Does the hypothesis survive contact with null models and rival baselines?
2. **Technical self-validation:** Are the data pipelines, splits, and contracts reproducible and correct?

The framework is deliberately adversarial. The goal is not to confirm the hypothesis but to find its weakest points. Every test that PASSES strengthens the claim; every test that FAILS reveals a real problem.

---

## Phase 0: Infrastructure

**Status:** COMPLETE

Built the validation framework infrastructure:

- `scripts/core/config.py` -- Central configuration with:
  - Paths to all 12 source files
  - SHA-256 hashes for data drift detection
  - Seeds (42 for reproducibility)
  - Threshold constants
  - STA1 atom regex pattern
- `scripts/core/data_loader.py` -- Unified loader for all datasets
- Directory structure: `scripts/core/`, `scripts/validation/`, `scripts/analysis/`
- Output directory: `output/` (splits, validation results)

---

## Phase 1: Data Contracts

**Status:** COMPLETE -- 16/16 PASS, 2 WARNINGS

`scripts/validation/data_contracts.py` validates 16 contracts across all datasets:

### Contract Results

| # | Contract | Target | Result |
|---|---|---|---|
| 1 | Identifications CSV schema | v7 table | PASS |
| 2 | Identifications uniqueness (no duplicate stems) | v7 table | PASS |
| 3 | Matching CSV schema | Best-match table | PASS |
| 4 | Matching uniqueness (no duplicate folios) | Best-match table | PASS |
| 5 | Expanded matching schema | 48x50 matrix | PASS |
| 6 | Expanded matching completeness (48x50) | Full matrix | PASS |
| 7 | Recipe database schema | 50 recipes | PASS |
| 8 | Recipe database uniqueness | No duplicate recipes | PASS |
| 9 | Ingredients flat schema | 613 rows | PASS |
| 10 | Ingredients flat referential integrity | All recipes referenced | PASS |
| 11 | Folio stems schema | 8232 rows | PASS |
| 12 | Folio stems normalization | Stem atoms valid | PASS |
| 13 | Subcategory counts vs flat table | Per-recipe validation | PASS (WARNING) |
| 14 | Numeric sanity (F1 range 0-1) | All scores | PASS |
| 15 | Mega index schema | 217 stems | PASS |
| 16 | Mega index uniqueness | No duplicate stems | PASS |

### Warnings

1. **Pillulae Cochiae subcategory mismatch:** Recipe header declares 5 ingredients but flat table has 6 rows. One ingredient may be double-counted or the header is wrong.
2. **Theriac/Mithridatium/Diascordium flat counts < declared totals:** These large recipes (40-64 ingredients) have fewer rows in the flat ingredient table than their declared totals. The flat table contains the "desglose" (breakdown) which is incomplete for very large recipes.

Both warnings are documentation issues, not data corruption. They don't affect the validation results.

---

## Phase 2: Blind Splits

**Status:** COMPLETE

`scripts/validation/blind_splits.py` creates deterministic train/test partitions:

### Parameters
- Seed: 42
- Test fraction: 0.2 (20%)
- Minimum test size: 5

### Test Sets
- **9 test folios:** f101r, f102v, f105r, f105v, f106v, f113v, f116v, f88r, f93v
- **10 test recipes:** Antidotum Hadriani, Benedicta Laxativa, Diacatholicon, Dialtea, Dianucum, Electuarium Justinum, Jawaarish Jalinusi, Oximel Compositum, Theriac Diatessaron, Unguentum Basilicon

### Integrity
- Output: `output/splits/blind_splits.json`
- SHA-256 hash embedded for tamper detection
- Contamination check: **v7 is confirmed contaminated** (expected -- it was built using all data). The identification `K1A3=Crocus` explicitly references test folio f93v in its reasoning chain.

### Implication
- The v7 identifications cannot be evaluated on the test set (circular reasoning)
- Future v8 identifications must be built using ONLY the training set, then evaluated on the test set

---

## Phase 3: Null Models

**Status:** COMPLETE -- System beats all null models (p < 0.01)

`scripts/validation/null_models.py` runs 5 null models x 500 iterations each:

### Results

| Null Model | Mean F1 | System F1 | Delta | p-value | Verdict |
|---|---|---|---|---|---|
| Wrong genre (culinary) | 0.0% | 81.9% | +81.9pp | < 0.001 | PASS |
| Random stems | 17.5% | 81.9% | +64.4pp | < 0.001 | PASS |
| Shuffled ingredients | 49.8% | 81.9% | +32.1pp | < 0.001 | PASS |
| Permuted stems | 74.5% | 81.9% | +7.4pp | < 0.01 | PASS (weak) |
| Permuted folios | 75.0% | 81.9% | +6.9pp | < 0.01 | PASS (weak) |

### Interpretation

1. **Wrong genre (0%):** The system is definitively pharmaceutical, not culinary. Zero overlap with random culinary ingredient sets. This is the strongest null-model rejection.

2. **Random stems (17.5%):** Assigning random ingredient labels to random stems produces very low F1. The system's identifications are far from random.

3. **Shuffled ingredients (49.8%):** Keeping the same folio-recipe assignments but shuffling ingredient lists within recipes still gets 49.8%. This means roughly half the F1 comes from the structural overlap between medieval recipes (many share common ingredients). The other half (+32pp) comes from getting the specific recipe compositions right.

4. **Permuted stems (74.5%):** Keeping the same ingredients but randomly reassigning which stems map to which ingredients still achieves 74.5%. **This is concerning.** It means most of the F1 comes from the FACT that we identified these 22 ingredients (all common), not from the SPECIFIC stem-to-ingredient mappings. Only +7.4pp comes from getting the mappings right.

5. **Permuted folios (75.0%):** Keeping the same stem-ingredient mappings but randomly reassigning which folio maps to which recipe achieves 75.0%. This confirms that folio-specific composition adds very little to the global F1 score.

### Key Insight

The null models reveal a hierarchy of information:
- **Genre choice** (pharmaceutical vs culinary): ~82pp of F1
- **Specific recipe compositions** (vs shuffled): ~32pp
- **Specific stem mappings** (vs permuted stems): ~7pp
- **Folio-specific assignments** (vs permuted folios): ~7pp

The system passes all null models but the margins for stem-level and folio-level specificity are thin.

---

## Phase 4: Baselines

**Status:** COMPLETE -- CRITICAL FINDING: F1 metric is broken

`scripts/validation/baselines.py` evaluates 5 rival baselines:

### Results

| Baseline | F1 Score | vs System (81.9%) | Verdict |
|---|---|---|---|
| Majority recipe | **100.0%** | +18.1pp | SYSTEM LOSES |
| Most common ingredients | **90.8%** | +8.9pp | SYSTEM LOSES |
| All ingredients | **87.2%** | +5.3pp | SYSTEM LOSES |
| Frequency rank | 66.7% | -15.2pp | System wins |
| Random baseline | 42.1% | -39.8pp | System wins |

### Explanation of Each Baseline

1. **Majority recipe (100% F1):** Predict that EVERY folio is "Theriac Magna" (the recipe with the most ingredients). Since Theriac Magna contains all 22 of our identified ingredients, this trivially achieves 100% precision and 100% recall for every folio. The F1 score is meaningless if this baseline can reach perfection.

2. **Most common ingredients (90.8%):** For each folio, predict the 22 most common ingredients across all 50 recipes (by frequency). Since our 22 identified ingredients ARE the most common ones in medieval pharmacology, this achieves 90.8%. This baseline uses NO Voynich data at all.

3. **All ingredients (87.2%):** Predict all 152 ingredients for every folio. High recall but lower precision due to many false positives. Still beats the system.

4. **Frequency rank (66.7%):** Rank ingredients by frequency and predict the top-N for each folio (N = number of stems in folio). This is the first baseline the system beats.

5. **Random baseline (42.1%):** Randomly sample ingredients. System wins easily.

### Root Cause Analysis

The F1 metric fails because:

1. **Small identified ingredient set:** We've only identified 22 of 152 total ingredients. These 22 are all ultra-common (Myrrha, Crocus, Castoreum, Galbanum, etc. appear in 30-80% of recipes).

2. **High base rates:** When an ingredient appears in 80% of recipes, predicting it for every folio gives 80% recall with only 20% false positive rate. With 22 such ingredients, the aggregate F1 is extremely high by default.

3. **No penalty for missing rare ingredients:** F1 doesn't penalize the system for failing to identify the 130 rare ingredients that would actually discriminate between recipes.

### Required Alternative Metrics

To properly evaluate the system, we need:

1. **Discriminative F1:** Exclude ingredients appearing in >80% of recipes from the score. Only count ingredients that are actually discriminative.

2. **Ranking accuracy:** For each folio, does the system rank the CORRECT recipe higher than incorrect ones? (Mean Reciprocal Rank, Precision@K)

3. **Exclusion accuracy:** Does the system correctly predict which ingredients are ABSENT from a folio? (True Negative Rate for ingredients not in the matched recipe)

4. **Rare ingredient precision:** Of the few discriminative ingredients (appearing in <30% of recipes), how many does the system correctly identify?

---

## Phases 5-10: Not Yet Implemented

| Phase | Description | Status |
|---|---|---|
| 5 | Transliteration round-trip test | Pending |
| 6 | Contradiction engine | Pending |
| 7 | Bootstrap confidence intervals + ablation | Pending |
| 8 | FDR correction for multiple comparisons | Pending |
| 9 | Automated semaphore report generator | Pending |
| 10 | End-to-end pipeline (all phases) | Pending |

### Phase 5: Transliteration Round-Trip
Test whether identified stems can "read" a recipe folio coherently: stem -> ingredient -> check against matched recipe's ingredient list -> compute round-trip accuracy.

### Phase 6: Contradiction Engine
Scan all identifications for logical contradictions: if stem X = ingredient A, but stem X appears in folio Y which matches recipe Z that does NOT contain ingredient A, that's a contradiction.

### Phase 7: Bootstrap + Ablation
- Bootstrap: resample folios with replacement, re-run matching 1000x, compute 95% CI for each metric
- Ablation: remove one identified stem at a time, measure impact on overall F1 (or replacement metric)

### Phase 8: FDR Correction
Apply Benjamini-Hochberg false discovery rate correction to all p-values across the 75 identifications and 48 folio matches.

### Phase 9: Semaphore Report
Auto-generate a color-coded report (GREEN/YELLOW/RED) for every identification, with all validation evidence aggregated.

### Phase 10: End-to-End
Single command that runs all phases sequentially and produces a final validation summary.

---

## Files

| File | Description |
|---|---|
| `scripts/core/config.py` | Central config with paths, SHA-256 hashes, seeds |
| `scripts/core/data_loader.py` | Unified data loader |
| `scripts/validation/data_contracts.py` | Phase 1: 16 data integrity contracts |
| `scripts/validation/blind_splits.py` | Phase 2: train/test partition generator |
| `scripts/validation/null_models.py` | Phase 3: 5 null models x 500 iterations |
| `scripts/validation/baselines.py` | Phase 4: 5 rival baselines |
| `output/splits/blind_splits.json` | Frozen partitions with integrity hash |
| `output/validation/null_models_results.json` | Null model results |
| `output/validation/baselines_results.json` | Baseline results |

---

## Summary

The validation framework reveals a mixed picture:

**Strengths:**
- Structural discoveries (suffix channel, vertical alignment, foreign keys) are robust and independent of F1
- System beats all null models (p < 0.01), confirming it captures real signal
- Wrong-genre null (0%) confirms pharmaceutical specificity
- Shuffled ingredients null (+32pp) confirms real recipe composition matters
- Data contracts pass 16/16 with only minor documentation warnings

**Weaknesses:**
- F1 metric is non-discriminative with 22 ultra-common ingredients
- Majority-recipe baseline achieves 100% F1 (metric is broken)
- Permuted stems null (+7.4pp) suggests most F1 comes from structural overlap, not specific mappings
- v7 identifications are contaminated (built using test data)

**Path Forward:**
1. Design alternative metrics (discriminative F1, ranking accuracy, exclusion accuracy)
2. Build v8 identifications using ONLY training data
3. Evaluate v8 on held-out test set with new metrics
4. Complete Phases 5-10
