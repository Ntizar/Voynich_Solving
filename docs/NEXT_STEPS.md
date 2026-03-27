# Next Steps -- Prioritized Roadmap

## Priority 1: Expand Historical Recipe Database

**Goal:** Add 10-20 more recipes from Antidotarium Nicolai to increase matching candidates and reduce ambiguity.

**Why:** Currently we have 8 recipes. Many Voynich recipe folios (especially the large ones with 100-500+ words) don't match any of our 8 recipes. The Antidotarium Nicolai alone has ~140 formulas. Adding more will:
- Create new perfect matches (more folios identified)
- Provide more intersection constraints (narrow down stem candidates)
- Help disambiguate L1A1 vs D1A1Q1K1A1 (Zingiber vs Piper longum)

**How:**
- Research Antidotarium Nicolai formulas online or from academic sources
- Focus on recipes with distinctive ingredient counts (3-15 ingredients)
- Classify each ingredient as ACTIVO/ESPECIA/BASE
- Add to `recetas_historicas_medievales.csv`
- Re-run the constraint solver

**Specific recipes to add:**
- Confectio Hamech (purgative, ~8 ingredients)
- Pillulae de Hiera (Hiera Picra, ~6 ingredients)
- Trifera Magna (~15 ingredients)
- Unguentum Basilicon (~5 ingredients)
- Unguentum Populeon (~7 ingredients)
- Electuarium de Citro (~10 ingredients)
- Requies Magna (~12 ingredients)
- Oximel scilliticum (~4 ingredients)
- Syrupus de Rosis (~5 ingredients)
- Diacatholicon (~10 ingredients)

---

## Priority 2: Co-occurrence Network Analysis

**Goal:** Build a graph where nodes are Voynich stems and edges represent co-occurrence in the same recipe folio. Compare against a parallel graph of historical ingredients.

**Why:** If two Voynich stems always appear together in recipe folios, and two historical ingredients always appear together in historical recipes, that's a stronger signal than frequency rank alone.

**How:**
1. For each recipe folio, list all unique stems
2. Create edges between every pair of stems that co-occur
3. Weight edges by number of folios where both appear
4. Do the same for historical ingredients across recipes
5. Use graph similarity metrics to find matching subgraphs
6. Specifically: check if the K1K2A1-BaA3-U2J1A1 co-occurrence triangle matches any historical ingredient triangle

**Output:** Network visualization data (node list + edge list CSV) for import into Obsidian graph, Gephi, or similar.

---

## Priority 3: Confirm K1J1A1 = Cinnamomum

**Goal:** Strengthen the tentative Cinnamomum identification from 65% to 90%+.

**How:**
1. List ALL recipe folios where K1J1A1 appears (it has 159 instances)
2. For each matched recipe (not just the 3 perfect matches), check if that recipe contains Cinnamomum
3. If K1J1A1 appears in EVERY folio matched to a recipe with Cinnamomum, and is ABSENT from folios matched to recipes WITHOUT Cinnamomum, that's strong confirmation
4. Cross-check: does K1J1A1's frequency in each folio correlate with Cinnamomum's typical dose proportion?

---

## Priority 4: Disambiguate L1A1 vs D1A1Q1K1A1

**Goal:** Determine which is Zingiber and which is Piper longum.

**How:**
1. **Frequency argument:** L1A1 (66 instances) >> D1A1Q1K1A1 (7 instances). Zingiber (ginger) is prescribed much more frequently than Piper longum in medieval recipes. So L1A1 = Zingiber is the prior.
2. **Folio analysis:** Check if D1A1Q1K1A1 appears ONLY in folios matching recipes that contain Piper longum, and is absent from recipes with Zingiber but not Piper longum. This requires expanding the recipe database (Priority 1).
3. **Botany origin:** D1A1Q1K1A1 originates from 6 Botany folios vs L1A1 from 23. Piper longum is a more specific/rare ingredient, consistent with fewer origin folios.

---

## Priority 5: Identify [A1Q2A3] (The "Tree of Life")

**Goal:** Determine what the most-used Exclusive stem in the manuscript represents.

**Why:** A1Q2A3 has 298+ recipe appearances across 33 folios, originating from f34v. It's the single most connected ingredient. Identifying it would anchor a large portion of the recipe network.

**How:**
1. Check which CATEGORY A1Q2A3 falls in (ACTIVO/ESPECIA/BASE) by analyzing its suffix distribution in recipes
2. Its very high frequency suggests a BASE ingredient (honey, wine, oil) or an extremely common ESPECIA (rose, sugar)
3. Compare its folio-presence profile against historical ingredient profiles
4. Check f34v on voynich.nu for the plant illustration

---

## Priority 6: Resolve the 60% Conflict Rate

**Goal:** Reduce conflicts in the cross-consistency test.

**Why:** 60% of multi-recipe stems show category inconsistency. This may be because:
- The frequency-rank heuristic assigns wrong positions
- Some stems are function words (verbs, prepositions) not ingredients
- Some stems represent semantic classes (like BaA3) that cross categories

**How:**
1. Filter out stems with A2-dominant suffixes (these are verbs, not ingredients)
2. Re-run consistency test with ONLY B2/C1-dominant stems
3. For remaining conflicts, check if they follow the "semantic class" pattern (like BaA3)
4. Use the constraint solver instead of frequency-rank for ALL assignments

---

## Priority 7: Visual Verification Campaign

**Goal:** Check specific Botany folios on voynich.nu to see if plant illustrations match predicted identifications.

**Folios to check:**
- **f17v** (K1K2A1 = Galbanum): Should show Ferula-type umbelliferous plant
- **f34v** (A1Q2A3 = unknown): Most important plant to identify visually
- **f33v** (BaA3 = gum-resin class): Should show plant with visible resin/latex
- **f52v** (U2J1A1 = Opium?): Should show Papaver somniferum or Aloe vera
- **f49r** (D1A1Q1J1A1 = Squilla?): Should show bulbous maritime plant

---

## Priority 8: Build Automated Pipeline

**Goal:** Consolidate all temp_*.py scripts into a clean, rerunnable pipeline.

**Why:** Currently there are 22 temp scripts. A future session should be able to:
1. Run one master script that regenerates all CSVs from the raw corpus
2. Add new historical recipes and re-run identification
3. Get updated results automatically

---

## Long-term Goals

- Identify 50+ stems (currently at 8)
- Attempt partial reading of a complete recipe page
- Publish findings (after verification by medieval pharmacopoeia experts)
- Build interactive web visualization of the ingredient network
