# Stem Identification Hypotheses -- Complete Table and Reasoning Chains

This document records every Voynich stem-to-ingredient hypothesis, organized by confidence tier. **Current version: v7 exploratory set (75 entries, 22 unique ingredients + 8 function words).**

Last updated: Session 15

**VALIDATION NOTE (updated):** These entries should be treated as manual hypotheses, not established readings. Later validation work showed that v7 is contaminated by test-folio exposure, `MRR/P@1` are tautological for v7, and blind train-only automation does not beat trivial baselines. Tier 1-2 entries remain the strongest manual hypotheses because their reasoning chains are less dependent on global metrics, but they still await cleaner external validation. See `docs/VALIDATION.md` for full details.

---

## Summary

| Tier | Count | Description |
|---|---|---|
| 0 (Function Words) | 8 | Stems too ubiquitous for single ingredient |
| 1 (Strongest manual hypotheses) | 2 | K1K2A1=Galbanum (99%), K1A3=Crocus (95%) |
| 2 (High) | 6 | All Myrrha: A1Q2A1, D1A1, D1A1A3, Q1K1A1, A1Q1J1, T1J1A1B1A3 |
| 3 (Strong) | 36 | Crocus x9, Rosa x1, **Mel despumatum x5**, Cinnamomum x2, Opopanax x2, **Zingiber x2**, **Castoreum x9**, **Petroselinum x4**, **Gentiana x2** |
| 4 (Moderate) | 23 | Amomum x3, Piper nigrum x1, Styrax x2, Piper longum x1, Bdellium x2, Casia x3, Cardamomum x8, Saccharum x1, Galanga\|Cubeba\|Nux moschata x2 |
| **TOTAL** | **75** | **22 unique ingredients (19 single + Galanga\|Cubeba\|Nux moschata triple)** |

---

## Tier 0: Function Words

These stems appear across too many recipes to correspond to any single ingredient. They are structural/grammatical elements of Voynichese.

| Stem | Confidence | Source |
|---|---|---|
| C2A1 | 90% | v4c: appears in 24/48 recipe folios, all recipe types |
| A1Q1J1A1 | 90% | v4c: appears in 22/48 recipe folios |
| U2J1A1 | 90% | v4c: appears in 10/48 but all matched types |
| A1Q2A3 | 90% | v4c: "Tree of Life" stem, 298+ occurrences across 33 folios |
| D1A1Q1J1A1 | 90% | v4c: appears in 27/48 recipe folios |
| A1B1A3 | 90% | v4c: appears in 25/48 recipe folios |
| L1J1A1 | 90% | v4c: appears in 36/48 recipe folios |
| L1A1 | 90% | v4c: appears in 33/48 recipe folios |

---

## Tier 1: Strongest Manual Hypotheses

### [K1K2A1] = Galbanum (99%)

- **Type:** Exclusive stem (origin f17v)
- **Category:** ACTIVO
- **Recipe appearances:** 17 recipe folios

**Reasoning:** Triple intersection of ACTIVO ingredients in Ung. Apostolorum AND Diascordium AND Theriac Magna yields a **unique result: {Galbanum}**. The only ingredient classified as ACTIVO in all three recipes.

**What it is:** Yellow-brown gum-resin from Ferula galbaniflua, used as anti-inflammatory and wound healer.

### [K1A3] = Crocus / Saffron (95%)

- **Type:** Generic stem (10 Botany folios)
- **Category:** ESPECIA
- **Recipe appearances:** 25 recipe folios

**Reasoning:** ESPECIA intersection of Pillulae Aureae AND Theriac = {Cinnamomum, Crocus}. K1A3 is **absent from f93v** (Diascordium), which contains Cinnamomum. If K1A3 were Cinnamomum, it should appear in f93v. Therefore K1A3 = Crocus by elimination.

**What it is:** Crocus sativus, the most expensive medieval spice. Present in Theriac, Mithridatium, Pillulae Aureae, Aurea Alexandrina.

---

## Tier 2: High Confidence -- Myrrha (6 stems)

All 6 stems resolve to Myrrha through the same mechanism: they appear in recipes containing Myrrha (Trifera Magna, Aurea Alexandrina, Philonium Persicum, Ung. Apostolorum) and are absent from recipes lacking Myrrha.

| Stem | Confidence | Key evidence |
|---|---|---|
| A1Q2A1 | 92% | v3 UNIQUE: highest differential score, present in 25 folio sets |
| D1A1 | 90% | Present in 24 recipe folios matching Myrrha distribution |
| D1A1A3 | 90% | Present in 14 recipe folios, Myrrha-only profile |
| Q1K1A1 | 88% | Present in 6 recipe folios, all Myrrha-containing |
| A1Q1J1 | 88% | Present in 15 recipe folios, Myrrha profile |
| T1J1A1B1A3 | 85% | Present in 2 recipe folios (f87v, f102r), both Myrrha-containing |

**What it is:** Commiphora myrrha, a gum-resin used in medieval medicine as antiseptic, analgesic, and in compound medicines. One of the most common ACTIVO ingredients.

---

## Tier 3: Strong Identifications (36 stems)

### Crocus (9 additional stems, 80%)

These 9 stems share the same distribution profile as K1A3 (confirmed Crocus) but were identified through the v3 constraint solver rather than direct elimination.

| Stem | Confidence |
|---|---|
| A1C1A3 | 80% |
| A1B2K1J1 | 80% |
| A2Q2J1A1 | 80% |
| T1J1A1 | 80% |
| B1L1J1A1 | 80% |
| C2A1C2A3 | 80% |
| K1J1U1J1 | 80% |
| K1K2Q1J1 | 80% |
| U1J1Aa | 80% |

### Rosa (1 stem, 82%)

| Stem | Confidence | Key evidence |
|---|---|---|
| B1K1A1 | 82% | Present in f87r (Confectio Hamech), f93v (Diascordium), f94v, f96v -- all Rosa-containing recipes |

**What it is:** Rosa damascena/gallica. Petals, hips, and rosewater used ubiquitously in medieval pharmacy.

### Mel despumatum (5 stems, 88%) -- UPDATED in v6 (was Zingiber|Mel in v5)

These 5 stems were previously identified as the inseparable pair Zingiber|Mel despumatum (v5). In session 11-12, discriminating recipes (2 Zingiber-only, 4 Mel-only) broke the deadlock with a **41-0 unanimous verdict for Mel**. See Discovery 18.

| Stem | Confidence |
|---|---|
| Q1A1 | 88% |
| Q2A1 | 88% |
| Q2K1A1 | 88% |
| U1A1 | 88% |
| U2A1 | 88% |

**What it is:** Mel despumatum = clarified/skimmed honey. The most common BASE ingredient in medieval pharmacy, used as a binder, preservative, and vehicle for compound electuaries. Present in 30+ recipes.

### Cinnamomum (2 stems, 60%)

| Stem | Confidence | Key evidence |
|---|---|---|
| A2A3 | 60% | Elimination from K1A3=Crocus; present in recipes with Cinnamomum |
| P1K1J1A1 | 60% | Same elimination chain |

### Opopanax (2 stems, 78-80%) -- NEW in v5

| Stem | Confidence | Key evidence |
|---|---|---|
| A1B2B1A3 | 80% | Folio-level constraint from f87v (Ung. Apostolorum) remaining ingredients |
| A3F2 | 78% | Independent differential analysis; cross-validates A1B2B1A3 |

**What it is:** Oleo-gum-resin from Opopanax chironium. Used in Ung. Apostolorum and other compound medicines.

### Zingiber (2 stems, 80-83%) -- NEW in v7

These stems were identified via intersection analysis in session 14. They are the UNIQUE candidate (only unidentified ingredient) across 9-10 diverse recipes in their matched folios. Solves the open problem from Discovery 19.

| Stem | Confidence | Key evidence |
|---|---|---|
| K1J1 | 83% | UNIQUE across 10 recipes. 38 folios, 100% presence, 67% absence |
| K1K2 | 80% | UNIQUE across 9 recipes. 37 folios, 100% presence, 70% absence |

**What it is:** Zingiber officinale (ginger). One of the most common spices in medieval pharmacy, present in 27 of 50 recipes. Used in electuaries, theriacs, and digestive compounds.

### Castoreum (9 stems, 75-83%) -- NEW in v7

These stems were identified via intersection analysis in session 14 (STRONG: 2 candidates Castoreum vs Zingiber, Castoreum wins by presence/absence differential). Partially breaks the Opium/Castoreum deadlock from the Castoreum side.

| Stem | Confidence | Key evidence |
|---|---|---|
| K1J1B1 | 83% | 26 folios, 100% presence, 67% absence |
| Q2A3 | 82% | 25 folios, 100% presence, 68% absence |
| K1U1 | 79% | 23 folios, 100% presence, 71% absence |
| A1Q2 | 79% | 23 folios, 100% presence, 71% absence |
| L1J1B1 | 79% | 23 folios, 100% presence, 71% absence |
| D1A1Q1K2B1 | 78% | 22 folios, 100% presence, 72% absence |
| B2A1 | 77% | 21 folios, 100% presence, 73% absence |
| B2Q1A3 | 76% | 20 folios, 100% presence, 74% absence |
| A1Q1K2B1 | 75% | 19 folios, 100% presence, 75% absence |

**What it is:** Secretion from the castor sacs of beavers. Used as antispasmodic, sedative, and in antidote recipes. Present in Theriac, Mithridatium, Philonium, and other complex compounds.

### Petroselinum (4 stems, 90%) -- NEW in v7

These stems were identified via intersection analysis in session 14. They win decisively against Zingiber due to low folio counts but 100% presence in matched recipe ingredient lists.

| Stem | Confidence | Key evidence |
|---|---|---|
| A1Q1K2Ba | 90% | 9 folios, 100% presence, 39% absence |
| A1Q2K1A1 | 90% | 8 folios, 100% presence, 41% absence |
| B1L1K2B1 | 90% | 3 folios, 100% presence, 48% absence |
| K1U1A3 | 90% | 4 folios, 100% presence, 47% absence |

**What it is:** Petroselinum crispum (parsley). Seeds used in medieval pharmacy as carminative and diuretic. Present in Theodoricon Euporistum, Mithridatium, Electuarium de Baccis Lauri.

### Gentiana (2 stems, 85-90%) -- NEW in v7

These stems were identified via intersection analysis in session 14. They win against Zingiber with very low absence rates (18%), indicating presence only in rare antidote-type recipes.

| Stem | Confidence | Key evidence |
|---|---|---|
| D1A1Q1K2Aa | 90% | 3 folios, 100% presence, only 18% absence. Only in antidote recipes |
| Q2A1B1A3 | 85% | Overrides prior Opium morphological flag from session 11. Gentiana fits recipe profile better |

**What it is:** Gentiana lutea (yellow gentian). Root used as bitter tonic and in antidote preparations. One of the 4 ingredients in Theriac Diatessaron (the simplest theriac).

---

## Tier 4: Moderate Identifications (23 stems)

### Saccharum (1 stem, 75%)

| Stem | Confidence | Key evidence |
|---|---|---|
| K1J1A1B2 | 75% | Elimination chain from v4 solver |

### Galanga | Cubeba | Nux moschata (2 stems, 75%)

| Stem | Confidence |
|---|---|
| K1A1B2B1A3 | 75% |
| T1A1 | 75% |

### Amomum (3 stems, 72%)

| Stem | Confidence |
|---|---|
| K1A1C1 | 72% |
| K1C2 | 72% |
| K1U1J1 | 72% |

### Piper nigrum (1 stem, 70%)

| Stem | Confidence | Key evidence |
|---|---|---|
| A1Q1A1 | 70% | Present in Philonium-exclusive folio profiles (confirmed session 9) |

### Styrax (2 stems, 70%)

| Stem | Confidence |
|---|---|
| A1Q1L1 | 70% |
| U1J1A1B1 | 70% |

### Piper longum (1 stem, 68%)

| Stem | Confidence | Key evidence |
|---|---|---|
| A1Q1A3 | 68% | 9 occurrences in f95v alone (confirmed Philonium, session 9) |

### Bdellium (2 stems, 68%)

| Stem | Confidence |
|---|---|
| D1 | 68% |
| P1K1K2 | 68% |

### Casia (3 stems, 63-65%)

| Stem | Confidence |
|---|---|
| A1Q1K2A1 | 65% |
| A1Q2J1A1 | 63% |
| D1A1Q1K2A1 | 63% |

### Cardamomum (8 stems, 65%)

| Stem | Confidence |
|---|---|
| A1B2K1J1A1 | 65% |
| C1A3 | 65% |
| D1A1Q1J1A1B1 | 65% |
| D1A1Q2J1A1 | 65% |
| K1J1A1U1 | 65% |
| L1A1B1A1 | 65% |
| L1A1U1J1 | 65% |
| K1A1B2A1B1 | 65% |

---

## Mutual Exclusion Constraints

These stems are linked by mutual exclusion -- resolving one resolves others:

```
K1A3 = Crocus (CONFIRMED)
  |
  +--> eliminates Crocus from other ESPECIA pools
  |
  +--> A2A3, P1K1J1A1 likely = Cinnamomum
       |
       +--> eliminates Cinnamomum from remaining pools
       |
       +--> Zingiber|Mel deadlock (5 stems, inseparable)
       +--> Opium|Castoreum deadlock (structural, 71 stems blocked)
```

**Deadlock status:**
- Zingiber vs Mel despumatum: **RESOLVED** -- 41-0 verdict for Mel (session 11-12, Discovery 18)
- Zingiber: **FOUND** -- K1J1 (83%), K1K2 (80%) via intersection analysis (session 14, Discovery 21)
- Opium vs Castoreum: **PARTIALLY BROKEN** -- 9 Castoreum stems confirmed at 75-83% via intersection analysis (session 14). 6 Opium folios, 17 Castoreum folios from original deadlock breaker. Morphological differences identified (session 11, Discovery 16-17)
- Galanga vs Cubeba vs Nux moschata: **PERMANENT DEADLOCK** -- 47 TIED, 0 directional wins. No discriminating recipe exists in the 50-recipe database (session 14, Discovery 20)

---

## Validation Summary

| Test | Result |
|---|---|
| Zingiber\|Mel negative controls (3 folios) | 0/15 false positives |
| Zingiber vs Mel deadlock breaker (6 recipes) | 41-0 for Mel (session 11-12) |
| Philonium probes in f88v, f95v, f96r, f102r | All 4 confirmed PHILONIUM |
| Opopanax cross-validation (2 independent paths) | Both converge |
| Crocus absence from f93v (Diascordium) | Confirmed |
| Galbanum triple intersection uniqueness | Confirmed |
| Content-based matching v7 (48 folios x 50 recipes) | Mean F1 = 81.9% **[UNDER REVIEW]** |
| f100r = Diamargariton (perfect match) | 100% F1 **[metric non-discriminative]** |
| f113v = Theodoricon Euporistum | 96.0% F1 **[metric non-discriminative]** |
| Galanga\|Cubeba\|Nux moschata triple deadlock | 47 TIED -- confirmed unbreakable |
| Opium/Castoreum morphological analysis (948 stems) | 296 Opium-enriched, 363 Castoreum-enriched |
| Intersection analysis (session 14) | 77 UNIQUE + 160 STRONG candidates generated |
| **Data contracts (session 15)** | **16/16 PASS, 2 warnings** |
| **Null models (session 15)** | **System beats all 5 (p < 0.01)** |
| **Wrong genre null (session 15)** | **0% F1 -- confirms pharmaceutical** |
| **Permuted stems null (session 15)** | **74.5% -- only +7.4pp real advantage** |
| **Majority recipe baseline (session 15)** | **100% F1 -- F1 metric is broken** |
| **Most common ingredients baseline** | **90.8% F1 -- beats system** |
