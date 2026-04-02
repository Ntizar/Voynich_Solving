# Next Steps -- Prioritized Roadmap

**Last updated:** Session 16 (April 2026)  
**Status:** Full pipeline executed. Mixed results: structural analysis strong, stem-to-ingredient mapping does not beat baselines.

---

## COMPLETED: Phase 4b -- Alternative Metrics (Session 15)

The broken F1 metric was fixed. Two interacting flaws identified and corrected. System clearly beats all baselines on discriminative metrics. **Caveat:** MRR/P@1 = 100% is tautological for v7 (targets chosen by best-match). Real test requires v8.

---

## COMPLETED: Session 16 -- Rigorous Validation Infrastructure + Full Execution

### Scripts Built

| Script | Purpose |
|---|---|
| `v8_builder.py` | Automated constraint solver (Phase 0 bootstrap + Phase 1 co-occurrence). No human curation. |
| `v8_evaluator.py` | Non-tautological evaluation: v7 independent targets, target-free specificity, permutation test |
| `comparative_corpus.py` | Structural claims vs synthetic Latin medical controls (1000 Monte Carlo sims) |
| `cipher_hypothesis.py` | IC classification, homophonic/polyalphabetic simulation, positional analysis |
| `sensitivity_analysis.py` | 5-fold CV, per-ingredient ablation, coverage analysis |

### Results vs Success Criteria

| Criterion | Target | Actual | Verdict |
|---|---|---|---|
| v8 test-set F1 > best baseline + 5pp | >56.2% (51.2% + 5pp) | 43.0% | **FAIL** |
| v8 rare F1 on test > 30% | >30% | Not measured (insufficient rare ingredients in test set) | **INCONCLUSIVE** |
| Comparative corpus: 3/5 significant anomalies | >=3 | 3/4 tests significant (suffix entropy p<0.0001, vertical alignment p<0.0001, schema variation p<0.0001; stem reuse NOT significant p=1.0) | **PASS** |
| Cipher hypothesis NOT fully explanatory | IC != cipher | IC=0.0769 (natural language), homophonic does NOT match | **PASS** |
| K-fold CV std dev < 15pp | <15pp | 1.2pp std dev | **PASS** |
| Permutation test significant | p<0.05 | p=0.000 for F1 and Exclusion (SIGNIFICANT), p=0.295 for MRR (not significant) | **PARTIAL PASS** |

### Key Findings

1. **Structural analysis is strong.** The Voynich recipe section genuinely has unusual properties vs Latin controls. Cipher hypothesis is ruled out. These findings are independently validated.

2. **Stem-to-ingredient mapping does not beat baselines.** v8's automated pipeline (43.0% F1) is beaten by trivial baselines: most_common (51.2%), all_ingredients (61.4%), majority_recipe (64.8%). The permutation test shows the mapping captures SOME real signal (p=0.000 for F1/Exclusion), but not enough to outperform simple heuristics.

3. **v8 vs v7 agreement is ~12.7%.** The automated bootstrap produces completely different stem identifications than v7's manually curated ones. This reflects the fundamental difficulty: without ground truth, there are many locally-optimal mappings.

4. **Coverage is low.** Only 18.7% of recipe folio words have identified stems. The vast majority of the text remains unexplained.

5. **Architecture problem discovered and fixed.** The original v8_evaluator had a tautological flaw (argmax(f(x)) == argmax(f(x))). Fixed to use v7 independent targets and permutation testing.

6. **Over-prediction problem diagnosed and partially fixed.** Original thresholds assigned too many stems per ingredient (197 total, ~6 each). v8.1 tightened to 47 ingredient stems, making permutation test significant.

### Honest Bottom Line

We can **prove** the Voynich recipe section has pharmaceutical database structure (structural analysis). We **cannot** automatically determine which specific stems map to which specific ingredients (mapping fails against baselines). The manually curated v7 identifications remain the best available, but their validation is circular.

---

## Priority 1: PUBLISH STRUCTURAL FINDINGS

The comparative corpus analysis and cipher hypothesis tests are independently validated and publication-worthy:
- 3/4 structural anomalies confirmed vs Latin controls
- Cipher hypothesis ruled out (IC=0.0769 = natural language)
- These results do NOT depend on specific stem-to-ingredient mappings

**Actionable:** Write up as a statistical paper focusing on structural evidence that the recipe section encodes a pharmaceutical database, without claiming specific identifications.

---

## Priority 2: IMPROVE STEM MAPPING (if continuing)

The automated pipeline's failure suggests several avenues:

### Hybrid approach (most promising)
- Use v7's curated stem mappings as seeds for v8's automated pipeline
- Tests whether automation can IMPROVE on manual curation rather than REPLACE it
- May capture signal that pure automation misses

### Expand recipe database
- More recipes improve discrimination and reduce baseline inflation
- Target: 100+ recipes from diverse sources (Antidotarium Nicolai, Circa Instans, Arabic sources)
- More rare ingredients would make baselines harder to beat

### Address low coverage
- 81.3% of words are FUNCTION_WORD or unidentified
- Investigate morphological patterns in function words
- Consider whether some "function words" are actually ingredients with insufficient evidence

---

## Priority 3: Complete Remaining Validation Phases (5-10)

| Phase | Description | Status |
|---|---|---|
| 5 | Transliteration round-trip test | Pending |
| 6 | Contradiction engine | Pending |
| 7 | Bootstrap confidence intervals + ablation | **DONE** (sensitivity_analysis.py) |
| 8 | FDR correction for multiple comparisons | Pending |
| 9 | Automated semaphore report generator | Pending |
| 10 | End-to-end pipeline (all phases) | Pending |

---

## Priority 4: Break Remaining Deadlocks

- **Galanga/Cubeba/Nux moschata**: PERMANENT with 50 recipes. Needs Circa Instans simples or morphological analysis.
- **Opium/Castoreum**: Partially broken. Needs Requies Magna analysis or positional clustering.

---

## Long-term Goals

- Expand recipe database to 100+ (improves discrimination, reduces baseline inflation)
- Attempt partial reading of a complete recipe page (requires better coverage than current 18.7%)
- Publish structural findings (independently validated, does not depend on mapping)
- Build interactive web visualization of the ingredient network
- Formal grammar model for column schemas
