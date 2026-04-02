# Next Steps -- Prioritized Roadmap

**Last updated:** Session 15 (April 2026)  
**Critical change:** Metric fix is now Priority 1 (the F1 metric is broken).

---

## Priority 1: CRITICAL -- Fix the F1 Metric

**Goal:** Replace the broken F1 metric with discriminative alternatives that trivial baselines cannot beat.

**Why:** Session 15 validation revealed that a majority-recipe baseline achieves 100% F1, and most-common-ingredients achieves 90.8%. The current F1 cannot discriminate between a real system and trivial baselines because all 22 identified ingredients are ultra-common in medieval pharmacology.

**Required alternative metrics:**

1. **Discriminative F1:** Exclude ingredients appearing in >80% of recipes. Only count ingredients that actually discriminate between recipes.

2. **Ranking accuracy (MRR, P@K):** For each folio, does the system rank the correct recipe higher than incorrect ones? Mean Reciprocal Rank and Precision@K measure this.

3. **Exclusion accuracy:** Does the system correctly predict which ingredients are ABSENT from a folio? True Negative Rate for ingredients not in the matched recipe.

4. **Rare ingredient precision:** Of the few discriminative ingredients (appearing in <30% of recipes), how many does the system correctly identify?

**How:**
- Add these metrics to `scripts/validation/baselines.py`
- Re-run all baselines with new metrics
- Re-evaluate the v7 system with new metrics
- Determine if the system genuinely outperforms baselines on discriminative measures

---

## Priority 2: Build v8 Identifications on Training Data Only

**Goal:** Create a v8 identification table using ONLY the 39 training folios, then evaluate on the 9 held-out test folios.

**Why:** v7 is contaminated -- the K1A3=Crocus identification explicitly references test folio f93v. Future claims require a clean train/test separation.

**How:**
1. Load only training folios from `output/splits/blind_splits.json`
2. Re-run all constraint solver, intersection analysis, and elimination chains using only training data
3. Generate `voynich_unified_identifications_v8.csv`
4. Evaluate v8 on test folios with the new discriminative metrics
5. Compare v8 test performance against baselines

---

## Priority 3: Complete Validation Phases 5-10

**Goal:** Run the remaining 6 validation phases for comprehensive confidence calibration.

| Phase | Description |
|---|---|
| 5 | Transliteration round-trip test |
| 6 | Contradiction engine |
| 7 | Bootstrap confidence intervals + ablation analysis |
| 8 | FDR correction for multiple comparisons |
| 9 | Automated semaphore report generator |
| 10 | End-to-end pipeline (all phases) |

**Priority within these:**
- Phase 6 (contradiction engine) is most immediately useful -- it will reveal logical inconsistencies in the identifications
- Phase 7 (bootstrap + ablation) will tell us which identifications are robust vs fragile
- Phase 8 (FDR) will adjust confidence levels for the 75 identifications

---

## Priority 4: Expand Historical Recipe Database to 100+

**Goal:** Add 50+ more recipes from Antidotarium Nicolai, Circa Instans, Thesaurus Pauperum, and Lumen Apothecariorum.

**Why:** More recipes serve two purposes:
1. **Better discrimination:** Recipes with unusual ingredient combinations will help the new discriminative metrics
2. **Break remaining deadlocks:** The Galanga/Cubeba/Nux moschata triple deadlock (47 TIED with 50 recipes) might break with rare recipes from different traditions
3. **Reduce base rates:** More recipes = more rare ingredients in the scoring pool = less inflation of trivial baselines

---

## Priority 5: Break Remaining Deadlocks

### Galanga / Cubeba / Nux moschata
- **Status:** PERMANENT with 50 recipes (47 TIED, 0 wins)
- **Path:** Only breakable with simpler recipes from non-standard sources (Circa Instans single-ingredient preparations, non-European pharmacopoeia)
- **Alternative:** Morphological analysis or botanical section cross-reference

### Opium / Castoreum
- **Status:** Partially broken (9 Castoreum stems confirmed at 75-83%)
- **Path:** Find folios matching Requies Magna (Opium without Castoreum) or identify morphological markers
- **Evidence so far:** Positional clustering (Opium=early folios, Castoreum=late folios), morphological differences (Opium stems shorter, Castoreum stems longer)

---

## Priority 6: Positional Grammar and Botany Section

**Goal:** Build formal grammar model from column positions and cross-correlate with botanical section.

**How:**
1. Formalize column schema: `[ENTITY C1/G1] -> [PROPERTY G1] -> [ACTION LIST A2]`
2. Test grammar predictions: can it predict missing words?
3. Cross-correlate 217 botany stems with known medieval simples (Circa Instans)
4. Verify identifications against botanical illustrations (Zingiber, Crocus are ideal test cases)

---

## Priority 7: Statistical Publication

**Goal:** Publish the structural discoveries as a statistical paper.

**What to publish:**
- Suffix channel: H=1.246 bits, Z=-210 (independent of all decipherment claims)
- Vertical alignment: 27% vs 8% in Latin/Spanish (novel finding with STA1 2.0)
- Cross-section foreign keys: 46.9% exclusive stem survival
- These results are **robust** and **unaffected** by the broken F1 metric

**What NOT to claim (yet):**
- The 81.9% F1 matching score (broken metric)
- Specific ingredient identifications beyond Tier 1-2 (pending new metrics)

---

## Long-term Goals

- Design and validate alternative metrics (discriminative F1, ranking accuracy)
- Build v8 on training data, evaluate on test set
- Identify 100+ stems with validated metrics
- Attempt partial reading of a complete recipe page
- Publish findings (structural paper first, identification paper after metric fix)
- Build interactive web visualization of the ingredient network
