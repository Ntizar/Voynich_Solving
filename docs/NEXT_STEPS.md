# Next Steps -- Prioritized Roadmap

**Last updated:** Session 15 (April 2026)  
**Status:** Phase 4b DONE -- F1 metric fixed, system validated on discriminative metrics. Priority 1 is now v8 on training data.

---

## COMPLETED: Fix the F1 Metric (Phase 4b)

**Status:** DONE (Session 15, Phase 4b)

The broken F1 metric was fixed by implementing 7 alternative discriminative metrics in `scripts/validation/alternative_metrics.py`. Two interacting flaws were identified and corrected:

1. **`fn` only counted identified ingredients (22/152)** -- inflating recall for everyone
2. **`best_match` oracle** -- let baselines shop across 50 recipes for best score

With **fixed-target evaluation** (each folio scored against its v7 assigned recipe, no oracle), the system clearly beats all baselines:

| Key Metric | v7 System | Best Baseline | Gap |
|---|---|---|---|
| Rare ingredient F1 | **72.4%** | 31.9% | +40.5pp |
| MRR | **1.000** | 0.238 | +0.762 |
| P@1 | **100%** | 10.6% | +89.4pp |

**Caveat:** MRR/P@1 = 100% is tautological (v7 targets chosen by best-match). Real test needs v8 on blind set.

---

## Priority 1: Build v8 Identifications on Training Data Only

**Goal:** Create a v8 identification table using ONLY the 39 training folios, then evaluate on the 9 held-out test folios.

**Why:** v7 is contaminated -- the K1A3=Crocus identification explicitly references test folio f93v. Future claims require a clean train/test separation. Also, MRR/P@1 = 100% is tautological for v7 (targets chosen by best-match); v8 on blind test folios will give a real ranking test.

**How:**
1. Load only training folios from `output/splits/blind_splits.json`
2. Re-run all constraint solver, intersection analysis, and elimination chains using only training data
3. Generate `voynich_unified_identifications_v8.csv`
4. Evaluate v8 on test folios with the Phase 4b discriminative metrics
5. Compare v8 test performance against baselines
6. This is the **definitive test**: if v8 beats baselines on held-out folios, the methodology is confirmed end-to-end

---

## Priority 2: Complete Validation Phases 5-10

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

## Priority 3: Expand Historical Recipe Database to 100+

**Goal:** Add 50+ more recipes from Antidotarium Nicolai, Circa Instans, Thesaurus Pauperum, and Lumen Apothecariorum.

**Why:** More recipes serve two purposes:
1. **Better discrimination:** Recipes with unusual ingredient combinations will help the new discriminative metrics
2. **Break remaining deadlocks:** The Galanga/Cubeba/Nux moschata triple deadlock (47 TIED with 50 recipes) might break with rare recipes from different traditions
3. **Reduce base rates:** More recipes = more rare ingredients in the scoring pool = less inflation of trivial baselines

---

## Priority 4: Break Remaining Deadlocks

### Galanga / Cubeba / Nux moschata
- **Status:** PERMANENT with 50 recipes (47 TIED, 0 wins)
- **Path:** Only breakable with simpler recipes from non-standard sources (Circa Instans single-ingredient preparations, non-European pharmacopoeia)
- **Alternative:** Morphological analysis or botanical section cross-reference

### Opium / Castoreum
- **Status:** Partially broken (9 Castoreum stems confirmed at 75-83%)
- **Path:** Find folios matching Requies Magna (Opium without Castoreum) or identify morphological markers
- **Evidence so far:** Positional clustering (Opium=early folios, Castoreum=late folios), morphological differences (Opium stems shorter, Castoreum stems longer)

---

## Priority 5: Positional Grammar and Botany Section

**Goal:** Build formal grammar model from column positions and cross-correlate with botanical section.

**How:**
1. Formalize column schema: `[ENTITY C1/G1] -> [PROPERTY G1] -> [ACTION LIST A2]`
2. Test grammar predictions: can it predict missing words?
3. Cross-correlate 217 botany stems with known medieval simples (Circa Instans)
4. Verify identifications against botanical illustrations (Zingiber, Crocus are ideal test cases)

---

## Priority 6: Statistical Publication

**Goal:** Publish the structural discoveries as a statistical paper.

**What to publish:**
- Suffix channel: H=1.246 bits, Z=-210 (independent of all decipherment claims)
- Vertical alignment: 27% vs 8% in Latin/Spanish (novel finding with STA1 2.0)
- Cross-section foreign keys: 46.9% exclusive stem survival
- These results are **robust** and **unaffected** by the broken F1 metric

**What NOT to claim (yet):**
- MRR/P@1 = 100% (tautological for v7; needs v8 on blind test set)
- Specific ingredient identifications beyond Tier 1-2 (pending v8 validation on held-out data)

---

## Long-term Goals

- Build v8 on training data, evaluate on test set with discriminative metrics
- Complete Phases 5-10 of the validation framework
- Identify 100+ stems with validated metrics
- Attempt partial reading of a complete recipe page
- Publish findings (structural paper first, identification paper after v8 test-set validation)
- Build interactive web visualization of the ingredient network
