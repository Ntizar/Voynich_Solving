# Session Log -- Chronological Record

## Session 1: Foundation and Structural Analysis

### Work Done

1. **Audited Cesar's Zenodo repository**
   - Read `zenodo_voynich/README.md`
   - Examined JSON results from 48 notebooks and 19 decoding models
   - Understood STA1 2.0 transcription format and atom categories

2. **Discovered Functional Suffix Channel**
   - Split all Voynich words into STEM + FINAL_ATOM
   - Computed conditional entropy: H(final|stem) = 1.246 bits vs null 2.096 bits
   - Z-score = -210 (effectively impossible by chance)
   - 82.2% of stems take only one specific final atom
   - 4 dominant endings (A2, B2, C1, G1) account for 79.1% of all endings

3. **Discovered 2D Vertical Alignment (NOVEL)**
   - Tested vertical alignment of suffixes across consecutive lines
   - Voynich: 27% match rate vs Latin/Spanish: ~8%
   - 3.4x higher than natural languages
   - Proves "invisible column" writing pattern

4. **Mapped Positional Column Schema**
   - Columns 1-2: C1/G1 dominant (Entity/Property)
   - Columns 3+: A2 dominant (Action)
   - 19.1% strict [ENTITY] -> [ACTION LIST] pattern
   - Generated `voynich_columnas_botanica.csv`

5. **Mapped Section-Level Tag Distributions**
   - Each section uses different "database schema"
   - Generated `voynich_secciones_etiquetas.csv`

### Scripts Written
- `temp_vertical_align.py`
- `temp_compare_languages.py`
- `temp_grid_tags.py`
- `temp_matrix_viz.py`, `temp_matrix_viz2.py`
- `temp_sql_schema.py`
- `temp_pseudocode.py`

---

## Session 2: Entity Extraction and Cross-Section Analysis

### Work Done

1. **Extracted 217 Entity Stems from Botany**
   - Stems tagged C1 in columns 1-2
   - Classified: 160 Exclusive (73.7%) vs 57 Generic (26.3%)
   - Generated `voynich_mega_indice_conexiones.csv`

2. **Built Cross-Section Traceability Index**
   - Tracked which Botany stems appear in Recipe sections
   - 46.9% Exclusive survival, 96.5% Generic survival
   - Systematic suffix shift: C1->B2 (Subject->Ingredient)
   - Generated `voynich_cruce_ingredientes.csv`

3. **Generated Obsidian Vault**
   - 130+ interconnected Markdown notes
   - Plant notes, Botany folio notes, Recipe folio notes
   - Wikilinks and voynich.nu image links
   - Directory: `Voynich_Graph/`

4. **Profiled All Recipe Folios**
   - 47 recipe folios profiled with ingredient counts and ratios
   - Generated `voynich_todas_recetas_perfil.csv`

5. **Discovered "Tree of Life" Stem [A1Q2A3]**
   - 298+ appearances across 33 recipe folios
   - Single most-used exclusive ingredient

### Scripts Written
- `temp_entity_extractor.py`
- `temp_cross_reference.py`
- `temp_mega_index.py`
- `temp_tree_of_life.py`
- `temp_generate_excels.py`
- `temp_voynich_all_recipes.py`

---

## Session 3: Historical Matching and Identification

### Work Done

1. **Built Historical Recipe Database (8 recipes)**
   - Theriac Magna, Mithridatium, Diascordium, Pillulae Cochiae
   - Pillulae Aureae, Unguentum Apostolorum, Electuarium Rosarum, Aurea Alexandrina
   - Full ingredient lists classified as ACTIVO/ESPECIA/BASE
   - Generated `recetas_historicas_medievales.csv`

2. **Matched Voynich Folios to Historical Recipes**
   - 3 perfect matches: f87v, f93v, f96v (100% ingredient count match)
   - 2 strong matches: f90r (95.5%), f113r (85.2%)
   - Generated `voynich_cruces_recetas_historicas.csv`

3. **Ran Cross-Consistency Test**
   - 25 stems across 2+ matched recipes
   - 40% consistent, 60% conflicting
   - Generated `voynich_consistencia_cruzada.csv`

4. **Built Constraint Propagation Solver**
   - Intersected ingredient lists by category across recipes
   - Found K1K2A1 = Galbanum (unique intersection, 99% confidence)
   - Found 2 empty intersections (BaA3, U2J1A1) and 3 narrow sets
   - Generated `voynich_constraint_solver_results.csv`

5. **Ran Elimination Solver**
   - Used K1K2A1=Galbanum to eliminate from other assignments
   - Discovered BaA3 = semantic class "gum-resin" (all 3 assignments are gum-resins)
   - Proved K1A3 = Crocus by absence from f93v (Diascordium has Cinnamomum but not K1A3)
   - Identified K1J1A1 as Cinnamomum candidate (tentative, 65%)
   - Generated `voynich_identificaciones_final.csv`, `voynich_identificaciones_candidatas.csv`

6. **Discovered Semantic Classes in Vocabulary**
   - Some stems don't map to single ingredients but to functional classes
   - BaA3 = "gum-resin" (Opopanax/Diagridium/Terebinthina)
   - U2J1A1 = "potent drug" (Opium/Aloe)

7. **Created Complete Documentation**
   - README.md, DISCOVERIES.md, IDENTIFICATIONS.md
   - METHODOLOGY.md, DATA_DICTIONARY.md, NEXT_STEPS.md
   - This SESSION_LOG.md

### Scripts Written
- `temp_historical_recipes.py`
- `temp_generate_match_csv.py`
- `temp_recipe_analyzer.py`, `temp_recipe_analyzer_ascii.py`
- `temp_theriac_hack.py`
- `temp_consistency_matrix.py`
- `temp_constraint_solver.py`
- `temp_elimination_solver.py`
- `temp_final_identifications.py`

---

## Session 4: Expanded Matching and Constraint Solver v3

### Work Done

1. **Expanded Historical Recipe Database from 8 to 23 recipes**
   - Added: Confectio Hamech, Hiera Picra, Trifera Magna, Diamargariton, Diaciminum, Unguentum Basilicon, Unguentum Populeon, Pillulae de Hiera, Pillulae Fetidae, Requies Magna, Diacodion, Dialtea, Philonium Persicum, Oximel Compositum, Theriac Diatessaron
   - Total unique ingredients: 123
   - Generated updated `recetas_historicas_medievales.csv` + new `recetas_historicas_ingredientes_flat.csv`

2. **Re-matched all 47 Voynich recipe folios against 23 recipes**
   - 9 perfect matches (100%): f87r, f87v, f88r, f93v, f96v, f100r, f100v, f101v, f103v
   - 19 strong matches (>=90%)
   - Generated `voynich_expanded_matching.csv`, `voynich_stems_in_matched_folios.csv`

3. **Ran Constraint Solver v2 (naive intersection)**
   - Found 45 "unique" identifications
   - Discovered Cinnamomum/Mel despumatum BIAS problem (ubiquitous ingredients dominate)
   - Generated `voynich_constraint_solver_v2_results.csv`

4. **Ran Refined Constraint Solver v3 (presence/absence scoring)**
   - Scoring: 0.5*pos_score + 0.3*neg_score + 0.2*discriminativity
   - 29 UNIQUE + 10 STRONG + 32 MODERATE identifications
   - Key: A1Q2A1 -> Myrrha (UNIQUE), K1A1C1/K1C2 -> Amomum, A1Q1A1 -> Piper nigrum
   - Discovered 7 FUNCTION WORDS (stems too ubiquitous for single ingredient)
   - Generated `voynich_constraint_solver_v3_results.csv`

### Scripts Written
- `temp_expand_recipes.py`
- `temp_expanded_matching.py`
- `temp_constraint_solver_v2.py`
- `temp_constraint_solver_v3.py`

---

## Session 5: Unified Solver v4 and Elimination Chains

### Work Done

1. **Built Unified Solver v4 reconciling ALL prior sources**
   - Merged: v1 (Galbanum), elimination logic (Crocus), v3 automated (Myrrha, Amomum, etc.)
   - Classified into 4 tiers: Confirmed (2), High (6), Strong (12), Moderate (21)
   - Ran elimination chain: each confirmed ID reduces other candidate lists
   - NEW from elimination: A2A3=Cinnamomum, P1K1J1A1=Cinnamomum, K1J1A1B2=Saccharum
   - Generated `voynich_unified_identifications_v4.csv`

2. **Folio-Exclusive Stem Exploitation (v4b)**
   - Found 29 stems exclusive to single perfect-match folios
   - For small recipes (Confectio Hamech, Ung.Apostolorum, Diascordium, Pillulae Aureae, Diamargariton, Diaciminum): tracked remaining unidentified ingredients
   - Discovered Zingiber/Mel despumatum cannot be separated (identical recipe profiles in our set)
   - Identified 23 stems with "perfect Zingiber profile"
   - Confirmed Opium/Castoreum cannot be disambiguated without Requies Magna or Pillulae Fetidae folios

3. **Final Consolidated Table v4c**
   - 56 total entries: 8 function words + 41 single-ingredient + 7 pair/cluster IDs
   - 13 unique single ingredients + 5 additional ingredients in pairs = 18 total
   - NEW: 8 additional function words discovered (C2A1, A1Q1J1A1, U2J1A1, A1Q2A3, D1A1Q1J1A1, A1B1A3, L1J1A1, L1A1)
   - NEW pairs: Zingiber|Mel despumatum (5 stems), Galanga|Cubeba|Nux moschata (2 stems)
   - Coverage per recipe: Trifera Magna 50%, Diascordium 54%, Diaciminum 55%, Diamargariton 50%
   - Generated `voynich_unified_identifications_v4c.csv`

4. **Key methodological insights**
   - Many v3 "UNIQUE->Cinnamomum" results are actually function words (low neg_score + high folio count)
   - Opium and Castoreum have identical recipe profiles -- 71 stems stuck in this cluster
   - Zingiber and Mel despumatum also have identical profiles in our 9-recipe set
   - Next disambiguation requires matching folios to Requies Magna (has Opium not Castoreum) or Pillulae Fetidae (has Castoreum not Opium)

### Scripts Written
- `temp_unified_solver_v4.py`
- `temp_solver_v4b_exclusive.py`
- `temp_solver_v4c_final.py`

---

## Session 6: Full Corpus Extraction and Deadlock Breaker

### Work Done

1. **Full Corpus Stem Extraction**
   - Extracted ALL stems from all 48 recipe folios (not just shared ones)
   - 7,097 rows, 2,902 unique stems across 40/48 folios
   - Discovered 8 folios missing (parsing bug, see Session 8)
   - Generated `voynich_all_recipe_folio_stems.csv`

2. **Opopanax Identification**
   - A1B2B1A3 and A3F2 independently resolve to Opopanax
   - Cross-validated: two independent stems converge to same ingredient
   - NOT yet added to v4c at end of session

3. **Zingiber/Mel Validation**
   - Tested against 3 negative-control folios (f93v, f96v, f100v)
   - All 5 Zingiber|Mel stems correctly ABSENT from controls
   - Validates the elimination-to-pair methodology

4. **Opium/Castoreum Deadlock Confirmed**
   - Structurally impossible to disambiguate with current recipe set
   - Both ingredients appear in identical recipe profiles
   - Need Requies Magna or Pillulae Fetidae folio match to break

5. **Five-Pronged Deadlock Breaker**
   - Script `temp_solver_v5_deadlock_breaker.py` with 5 attack approaches
   - Frequency analysis, co-occurrence, suffix patterns, folio-exclusive probes, sub-recipe blocks
   - Partial progress but deadlock holds for Opium/Castoreum

### Scripts Written
- `temp_full_stem_extractor_v5.py`
- `temp_solver_v5_deadlock_breaker.py`

---

## Session 7: Requies vs Philonium Discriminator and GitHub

### Work Done

1. **Requies vs Philonium Discriminator**
   - Built 5-approach discriminator using identified stems as diagnostic probes
   - 26 Philonium-exclusive probes vs 4 Requies-exclusive probes
   - Confirmed: f88v = PHILONIUM (12 tokens, 8 stems), f96r = PHILONIUM (7 tokens, 6 stems)
   - f95v and f102r: UNDETERMINED due to corpus parsing bug (folios not in extracted data)

2. **Critical Bug Discovery: 8 Missing Folios**
   - Folios f90r, f90v, f95r, f95v, f102r, f102v not found in corpus extraction
   - Root cause: foldout pages use sub-indices (f90r1, f90r2, etc.)
   - Parser regex `^<(f\d+[rv])>` doesn't match `f90r1`
   - Full diagnosis deferred to next session

3. **GitHub Repository Created**
   - `git init`, `.gitignore` configured
   - Initial commit: 307 files
   - `gh repo create Ntizar/Voynich_Solving --public`
   - Pushed to origin/master
   - Repository: https://github.com/Ntizar/Voynich_Solving

### Scripts Written
- `temp_requies_vs_philonium_v6.py`

---

## Session 8: Dashboard, Bug Fix, and Opopanax Integration

### Work Done

1. **Investigated Ntizar Design System**
   - Found `design-system/ntizar.css` (1379 lines) -- "Liquid Glass UI" with Azul/Naranja palette
   - Includes glassmorphism at 3 levels, cards, badges, progress bars, tooltips, SVG refraction filter
   - Found `design-system/demo.html` as reference implementation

2. **Fixed Corpus Parsing Bug**
   - Root cause confirmed: foldout folios use numeric sub-indices
   - f90r -> f90r1+f90r2, f90v -> f90v1+f90v2, f95r -> f95r1+f95r2, f95v -> f95v1+f95v2, f102r -> f102r1+f102r2, f102v -> f102v1+f102v2
   - Fixed regex in `temp_full_stem_extractor_v5.py`: `f\d+[rv]` -> `f\d+[rv]\d*` with parent mapping
   - +12 sub-folios recovered

3. **Added Opopanax to v5 Identification Table**
   - A1B2B1A3 = Opopanax (80%, Tier 3)
   - A3F2 = Opopanax (78%, Tier 3)
   - Updated `voynich_unified_identifications_v5.csv` (now 59 entries)

4. **Built Comprehensive HTML Dashboard**
   - Full visual dashboard using Ntizar CSS design system
   - Sections: Overview stats, Identification table, Recipe matching, Folio-recipe heatmap, 5 Chart.js graphs, Folio viewer with voynich.nu images
   - Interactive: filterable tables, tabbed views, clickable folio thumbnails
   - Generated `dashboard_voynich.html`

### Scripts Written/Modified
- `temp_full_stem_extractor_v5.py` (regex fix)
- `dashboard_voynich.html` (new)

---

## Session 9: Corpus Recovery and Philonium Confirmation

### Work Done

1. **Re-ran Fixed Corpus Extractor**
   - `temp_full_stem_extractor_v5.py` executed with patched regex
   - All 8 missing folios recovered: f89r, f89v, f90r, f90v, f95r, f95v, f102r, f102v
   - Results: 8,232 rows (+1,135), 3,261 unique stems (+359), 48/48 folios (complete)
   - Updated `voynich_all_recipe_folio_stems.csv`

2. **Re-ran Requies vs Philonium Discriminator**
   - Updated `temp_requies_vs_philonium_v6.py` to use v5 identifications
   - With recovered f95v and f102r data, ALL 4 candidates confirmed PHILONIUM:
     - f88v: Phil=12 tokens (7 ings) vs Req=0
     - f95v: Phil=11 tokens (3 ings) vs Req=0 (previously UNDETERMINED)
     - f96r: Phil=7 tokens (5 ings) vs Req=0
     - f102r: Phil=17 tokens (6 ings) vs Req=0 (previously UNDETERMINED)
   - Conclusion: Requies Magna is NOT present in our matched folios
   - Opium/Castoreum deadlock cannot be broken via this route

3. **Updated Documentation**
   - `DISCOVERIES.md`: Added discoveries 10-14 (Opopanax, Zingiber/Mel validation, Opium/Castoreum deadlock, corpus bug, Philonium confirmation)
   - `IDENTIFICATIONS.md`: Complete rewrite with all 58 v5 entries organized by tier
   - `SESSION_LOG.md`: Added Session 9, updated summary statistics

### Scripts Modified
- `temp_requies_vs_philonium_v6.py` (updated to use v5 identifications)

---

## Session 10: Recipe Expansion, Content-Based Matching v3, and Deadlock Breaker

### Work Done

1. **Expanded Historical Recipe Database from 23 to 50 recipes**
   - Added 27 new recipes from: Antidotarium Nicolai, Grabadin/Mesue, Avicenna Canon, Abulcasis, Salernitano
   - Total unique ingredients: 152 (was 123)
   - Total ingredient-recipe pairs: 613 (was 314)
   - Key deadlock-breaking additions:
     - **Philonium Romanum** (Opium WITHOUT Castoreum)
     - **Requies Magna** (Opium WITHOUT Castoreum)
     - **Theriac Diatessaron Magna** (Castoreum WITHOUT Opium)
     - **Pillulae Fetidae** (Castoreum WITHOUT Opium)
     - **Confectio Anacardia** (Castoreum WITHOUT Opium)
   - Script: `temp_expand_recipes_v2.py`

2. **Built Content-Based Matching Engine v3**
   - Uses v5 identification table (58 entries) to map stems to ingredients
   - For each folio: identifies which real ingredients are present via identified stems
   - Matches identified ingredient sets against all 50 recipes using F1 score
   - Results (48 folios x 50 recipes):
     - **1 EXCELLENT match (F1>=80%):** f113v = Electuarium Justinum (F1=80%, 10 ingredient overlap: Amomum, Cardamomum, Casia, Cinnamomum, Crocus, Mel, Myrrha, P.longum, P.nigrum, Zingiber)
     - **40 GOOD matches (F1 50-79%):** covering most recipe folios
     - **5 MODERATE (30-49%), 2 WEAK (<30%)**
   - Most frequent best-match recipes: Electuarium Justinum (14 folios), Trifera Saracenica (13 folios)
   - Generated: `voynich_expanded_matching_v3.csv`, `voynich_matching_v3_top5.csv`
   - Script: `temp_matching_v3.py`

3. **Ran Opium vs Castoreum Deadlock Breaker**
   - Method: compare each folio's best F1 score against Opium-only recipes vs Castoreum-only recipes
   - Opium-only recipes: Philonium Romanum, Requies Magna
   - Castoreum-only recipes: Confectio Anacardia, Dianucum, Pillulae Fetidae, Theodoricon Euporistum, Theriac Diatessaron Magna
   - Results:
     - **6 OPIUM-favoring folios:** f90r, f94r, f94v, f95r, f101v, f114r
     - **17 CASTOREUM-favoring folios:** f87v, f95v, f99r, f102v, f103r, f103v, f104v, f106v, f108r, f108v, f111r, f111v, f112r, f113r, f113v, f115r, f116r
     - **24 TIED, 1 INSUFFICIENT** (f116v -- only 2 words)
   - Margins are thin (typically 5-10% F1 difference) -- deadlock NOT fully broken
   - Generated: `voynich_deadlock_breaker_v3.csv`

4. **Copied Voynich Corpus to Repo Root**
   - `voynich_sta.txt` copied from `zenodo_voynich/corpus/` to repo root
   - Verified NOT gitignored at root level

5. **Built Bilingual README.html**
   - Full Ntizar CSS (Liquid Glass UI) inlined
   - English/Spanish language toggle
   - Glassmorphism cards, progress bars, stats, discovery summaries
   - Future exploration paths documented
   - 523 lines

### Scripts Written
- `temp_expand_recipes_v2.py`
- `temp_matching_v3.py`

### Files Generated
- `voynich_expanded_matching_v3.csv` -- Full 48x50 matching matrix
- `voynich_matching_v3_top5.csv` -- Top 5 recipe matches per folio
- `voynich_deadlock_breaker_v3.csv` -- Opium vs Castoreum F1 per folio
- `README.html` -- Bilingual dashboard README

---

## Session 11: Morphological Deadlock Analysis and Zingiber/Mel Breakthrough

### Work Done

1. **Opium/Castoreum Morphological Analysis**
   - Comprehensive analysis of all 948 unidentified stems for Opium vs Castoreum enrichment
   - Used Log Odds Ratio to classify stems: 296 Opium-enriched, 363 Castoreum-enriched, 288 neutral
   - Found 5 strong Opium-exclusive stems (in 2+ opium folios, 0 castoreum): Q2A1B1A3, A1B2Q1A1, BaA1, K1A1B2Q1, K1Aa
   - Found 301 strong Castoreum-exclusive stems (in 2+ castoreum folios, 0 opium)
   - Morphological differences: Opium stems shorter (more 2-atom), more A1/B1-initial; Castoreum stems longer (6+ atom), more B2/P1-initial, L1J1-containing

2. **Positional Ordering Analysis**
   - 78.4% of (opium, castoreum) folio pairs have opium BEFORE castoreum
   - Mean folio position: Opium = 196.3, Castoreum = 213.0
   - Consistent with medieval pharmacopoeia organization (analgesics before stimulants)

3. **Ingredient Profile Differences**
   - Opium folios: 3.5x more Zingiber|Mel, 2.1x more P. nigrum
   - Castoreum folios: 2.4x more Crocus, 3.8x more Cardamomum, exclusive Casia/Styrax/Rosa

4. **Zingiber/Mel Deadlock -- BROKEN**
   - Found discriminating recipes: 2 Zingiber-only (Benedicta Laxativa, Elec. de Succo Rosarum), 4 Mel-only (Hiera Picra, Theriac Diatessaron, Theriac Diatessaron Magna, Tiryaq al-Arba)
   - Result: **41 folios favor MEL, 0 favor ZINGIBER, 6 tied, 1 insufficient**
   - Unanimous verdict: 5 Zingiber|Mel stems are Mel despumatum (honey)

### Scripts Written
- Inline analysis (no named script -- morphological analysis run in session)

### Files Generated
- `voynich_deadlock_morphology_v3.csv` -- Enrichment analysis for all 948 unidentified stems
- `voynich_zingiber_mel_deadlock.csv` -- Per-folio F1 comparison (41-0 verdict)

---

## Session 12: v6 Identification Update, Re-matching, and Zingiber Search

### Work Done

1. **Updated Identification Table v5 -> v6**
   - Changed 5 Zingiber|Mel stems (Q1A1, Q2A1, Q2K1A1, U1A1, U2A1) to Mel despumatum at 88% confidence
   - v6 has 58 entries, 17 unique ingredients (was 19 counting pairs)
   - Generated `voynich_unified_identifications_v6.csv`

2. **Re-ran Content-Based Matching with v6**
   - 48 folios x 50 recipes matching using v6 identifications
   - Results: 0 EXCELLENT (f113v dropped from 80% to 75% due to Mel being single ingredient), 37 GOOD, 8 MODERATE, 2 WEAK, 1 INSUFFICIENT
   - Mean F1 (non-zero): 54.3%
   - Most frequent best-match: Electuarium Justinum (14 folios), Trifera Saracenica (14 folios)
   - Generated `voynich_matching_v6.csv`, `voynich_expanded_matching_v6.csv`, `voynich_matching_v6_top5.csv`

3. **Searched for New Zingiber Stems**
   - Attempted enrichment analysis for stems appearing in Zingiber-containing recipe folios
   - 42/47 active folios match Zingiber-containing recipes -- enrichment non-discriminative
   - No strong candidates identified; requires alternative approaches (morphological pairing, co-occurrence, recipe-specific probing)
   - Generated `voynich_zingiber_candidates.csv`

4. **Updated DISCOVERIES.md**
   - Added discoveries 17 (Morphological Opium/Castoreum Analysis), 18 (Zingiber/Mel Broken 41-0), 19 (Zingiber Search Inconclusive)
   - Now has 19 documented discoveries

### Scripts Written
- `temp_v6_update_and_match.py`

### Files Generated
- `voynich_unified_identifications_v6.csv` -- v6 identification table (58 entries)
- `voynich_matching_v6.csv` -- Best match per folio (v6)
- `voynich_expanded_matching_v6.csv` -- Full 48x50 matching matrix (v6)
- `voynich_matching_v6_top5.csv` -- Top 5 recipe matches per folio (v6)
- `voynich_zingiber_candidates.csv` -- Zingiber enrichment analysis

---

## Session 13 (Dashboard & Housekeeping)

**Date:** March 2026  
**Duration:** ~1 hour  
**Focus:** Dashboard Zingiber/Mel chart JS, session 11-12 file commit, docs update

### Summary

Housekeeping session focused on updating the interactive dashboard and committing all work from sessions 11-12.

### Key Activities

1. **Dashboard Zingiber/Mel Chart JS**
   - Added `renderZingiberMelChart()` function to `dashboard_voynich.html`
   - Chart shows Zingiber F1 vs Mel F1 for all 48 folios, visually demonstrating the 41-0 verdict
   - Green bars for Mel-winning folios, gray for tied

2. **Git Commit**
   - Committed all session 11-12 files: `71cda4b`
   - Includes: `voynich_zingiber_mel_deadlock.csv`, `voynich_unified_identifications_v6.csv`, `voynich_matching_v6.csv`, `voynich_expanded_matching_v6.csv`, `voynich_matching_v6_top5.csv`, `voynich_zingiber_candidates.csv`

3. **Documentation Update**
   - Updated SESSION_LOG.md through session 12
   - Updated DISCOVERIES.md with discoveries 17-19

### Files Modified
- `dashboard_voynich.html` -- Zingiber/Mel chart added
- `docs/SESSION_LOG.md` -- Updated through session 12
- `docs/DISCOVERIES.md` -- Updated through discovery 19

---

## Session 14 (v7 Breakthrough -- Intersection Analysis)

**Date:** March 2026  
**Duration:** ~4 hours  
**Focus:** Triple deadlock analysis, intersection-based stem exploration, v7 identification table, v7 matching

### Summary

Major breakthrough session. Used intersection analysis across all recipe-folio profiles to explore 237 candidate stems. Identified 17 new stems (4 entirely new ingredients: Zingiber, Castoreum, Petroselinum, Gentiana). The v7 identification table (75 entries, 22 ingredients) produced a massive leap in matching quality: 35 EXCELLENT matches at F1>=80%, mean F1 81.9% (up from 0 EXCELLENT and 54.3% in v6).

### Key Activities

1. **Triple Deadlock Analysis: Galanga | Cubeba | Nux moschata**
   - Tested whether any of the 50 recipes could discriminate between Galanga, Cubeba, and Nux moschata
   - Result: 47 TIED, 0 directional wins in any direction
   - Conclusion: **UNBREAKABLE** with current 50-recipe database -- all recipes that include one always include all three
   - Generated `voynich_galanga_cubeba_nux_deadlock.csv`

2. **Intersection-Based Stem Exploration**
   - For each of 948 unidentified stems, computed the intersection of candidate ingredients across all matched recipe folios
   - Found **77 UNIQUE-resolution stems** (intersection = exactly 1 candidate) -- all point to **Zingiber**
   - Found **160 STRONG stems** (intersection = exactly 2 candidates) -- mostly Castoreum vs Zingiber
   - Applied presence/absence differential to disambiguate STRONG stems
   - Generated `voynich_new_identifications_session14.csv` (237 entries)

3. **v7 Identification Table**
   - Added 17 new entries to the identification table:
     - Zingiber x2 (K1J1 at 83%, K1K2 at 80%)
     - Castoreum x9 (K1J1B1, Q2A3, K1U1, A1Q2, L1J1B1, D1A1Q1K2B1, B2A1, B2Q1A3, A1Q1K2B1 at 75-83%)
     - Petroselinum x4 (A1Q1K2Ba, A1Q2K1A1, B1L1K2B1, K1U1A3 at 90%)
     - Gentiana x2 (D1A1Q1K2Aa at 90%, Q2A1B1A3 at 85%)
   - Total: 75 entries, 22 unique ingredients (up from 58/17)
   - Generated `voynich_unified_identifications_v7.csv`

4. **v7 Matching Re-run**
   - Re-ran content-based matching (48 folios x 50 recipes) with v7 identifications
   - Results:
     - **35 EXCELLENT** (F1 >= 80%) -- up from 0 in v6
     - **12 GOOD** (F1 50-79%) -- down from 37 (promoted to EXCELLENT)
     - **0 MODERATE, 0 WEAK, 1 INSUFFICIENT** (f116v = 2 words)
     - Mean F1 (non-zero): **81.9%** -- up from 54.3% in v6
     - **f100r = 100% F1** (perfect match to Diamargariton)
     - **f113v = 96.0% F1** (Theodoricon Euporistum)
     - Most frequent best-match: Trifera Saracenica (10 folios), Theodoricon Euporistum (10 folios)
   - Generated `voynich_matching_v7.csv`, `voynich_expanded_matching_v7.csv`, `voynich_matching_v7_top5.csv`

5. **Dashboard Update (partial)**
   - Updated navbar badges, hero stats, identification table section, matching section, stat cards
   - Replaced IDENTIFICATIONS and MV3 JS arrays with v7 data
   - Added Session 14 Breakthrough section with v6-vs-v7 comparison table
   - Still pending: README.html full rewrite

### Scripts Written
- `temp_session14_analysis.py` -- Triple deadlock + intersection exploration
- `temp_session14_v7.py` -- v7 table builder + matching re-run

### Files Generated
- `voynich_unified_identifications_v7.csv` -- v7 identification table (75 entries, 22 ingredients)
- `voynich_matching_v7.csv` -- Best match per folio (v7)
- `voynich_expanded_matching_v7.csv` -- Full 48x50 matching matrix (v7)
- `voynich_matching_v7_top5.csv` -- Top 5 recipe matches per folio (v7)
- `voynich_galanga_cubeba_nux_deadlock.csv` -- Triple deadlock results (47 TIED)
- `voynich_new_identifications_session14.csv` -- All 237 candidate identifications from intersection analysis

---

## Session 15 (Scientific Validation Framework)

**Date:** April 2026  
**Duration:** ~6 hours  
**Focus:** Build and run scientific validation framework (Phases 0-4), discover F1 metric is broken, update all documentation

### Summary

Built a comprehensive scientific validation framework with two layers: scientific validation (null models, baselines) and technical self-validation (data contracts, blind splits). The framework revealed a **critical finding**: the F1 metric used to evaluate the v7 matching system is non-discriminative. A trivial majority-recipe baseline achieves 100% F1, and a most-common-ingredients baseline achieves 90.8%, both beating the system's 81.9%. The structural discoveries remain robust. All documentation updated to honestly reflect these findings.

### Key Activities

1. **Phase 0: Infrastructure**
   - Created `scripts/core/config.py` with central configuration, SHA-256 hashes for all 12 source files, seed=42, threshold constants, STA1 atom regex
   - Created `scripts/core/data_loader.py` for unified dataset loading
   - Organized directory structure: `scripts/core/`, `scripts/validation/`, `scripts/analysis/`

2. **Phase 1: Data Contracts**
   - Built `scripts/validation/data_contracts.py` with 16 integrity contracts
   - Result: **16/16 PASS, 2 warnings**
   - Warning 1: Pillulae Cochiae subcategory count mismatch (5 vs 6)
   - Warning 2: Theriac/Mithridatium/Diascordium flat tables incomplete for large recipes

3. **Phase 2: Blind Splits**
   - Built `scripts/validation/blind_splits.py` with deterministic train/test partitions (seed=42)
   - 9 test folios, 10 test recipes
   - v7 confirmed contaminated (expected -- K1A3=Crocus references test folio f93v)
   - Output: `output/splits/blind_splits.json` with SHA-256 integrity hash

4. **Phase 3: Null Models -- System beats ALL (p < 0.01)**
   - Built `scripts/validation/null_models.py` with 5 null models x 500 iterations
   - Wrong genre (culinary): 0% vs 81.9% -- confirms pharmaceutical specificity
   - Shuffled ingredients: 49.8% vs 81.9% -- real recipe composition matters (+32pp)
   - **Permuted stems: 74.5% -- only +7.4pp real advantage from specific mappings**
   - Permuted folios: 75.0% -- folio-specific composition adds little
   - Random stems: 17.5% -- system far from random

5. **Phase 4: Baselines -- CRITICAL: F1 metric is broken**
   - Built `scripts/validation/baselines.py` with 5 rival baselines
   - **Majority recipe baseline = 100% F1** (predicting Theriac Magna for everything)
   - **Most common ingredients = 90.8%** (beats system without using any Voynich data)
   - **All ingredients = 87.2%** (also beats system)
   - Frequency rank = 66.7% (system wins)
   - Root cause: 22 identified ingredients are all ultra-common, F1 can't discriminate

6. **Documentation Update**
   - Created `docs/VALIDATION.md` with full protocol and results
   - Updated `README.md` with validation status, honest assessment, new structure
   - Updated `README.html` with validation alert, corrected stats, revised priorities
   - Updated all docs/ files (DISCOVERIES, METHODOLOGY, DATA_DICTIONARY, NEXT_STEPS, SESSION_LOG)
   - Fixed `.gitignore` to include `scripts/` (was accidentally excluded!)

### Scripts Written
- `scripts/core/config.py` -- Central config with SHA-256 hashes
- `scripts/core/data_loader.py` -- Unified data loader
- `scripts/validation/data_contracts.py` -- 16 data integrity contracts
- `scripts/validation/blind_splits.py` -- Train/test partition generator
- `scripts/validation/null_models.py` -- 5 null models x 500 iterations
- `scripts/validation/baselines.py` -- 5 rival baselines
- `scripts/_gen_hashes.py` -- Temporary hash generation helper

### Files Generated
- `output/splits/blind_splits.json` -- Frozen train/test partitions with integrity hash
- `output/validation/null_models_results.json` -- Null model results (5 models x 500 iterations)
- `output/validation/baselines_results.json` -- Baseline comparison results
- `docs/VALIDATION.md` -- New: full validation protocol and results document

---

## Summary Statistics

| Metric | Value |
|---|---|
| Total scripts written | 40+ |
| Total CSV files generated | 34 |
| HTML files | 2 (dashboard_voynich.html, README.html) |
| Obsidian notes generated | 130+ |
| Unique stems in corpus | 3,261 (recipe folios, post-recovery) |
| Unique entity stems (Botany) | 217 |
| Recipe folios profiled | 48 (complete) |
| Historical recipes compiled | 50 (expanded from 23 in session 10) |
| Unique historical ingredients | 152 |
| Ingredient-recipe pairs | 613 |
| Structural matching: perfect (100%) | 9 |
| Structural matching: strong (>=90%) | 19 |
| Content-based matching v7: best F1 | 100.0% (f100r = Diamargariton) |
| Content-based matching v7: EXCELLENT (F1>=80%) | 35 |
| Content-based matching v7: GOOD (F1 50-79%) | 12 |
| Content-based matching v7: mean F1 | 81.9% **[UNDER REVIEW -- see Validation]** |
| Confirmed identifications (Tier 1-2) | 8 (Galbanum, Crocus, Myrrha x6) |
| Strong identifications (Tier 3) | 36 (Crocus x9, Rosa, Mel x5, Cinnamomum x2, Opopanax x2, Zingiber x2, Castoreum x9, Petroselinum x4, Gentiana x2) |
| Moderate identifications (Tier 4) | 23 (Amomum, Piper, Bdellium, Casia, Cardamomum, Styrax, Saccharum, Galanga\|Cubeba\|Nux moschata) |
| Function words identified | 8 |
| Total identification entries (v7) | 75 |
| Unique ingredients identified | 22 (Galbanum, Crocus, Myrrha, Mel, Rosa, Cinnamomum, Opopanax, Zingiber, Castoreum, Petroselinum, Gentiana, Amomum, P.nigrum, P.longum, Styrax, Bdellium, Casia, Cardamomum, Saccharum + Galanga\|Cubeba\|Nux moschata triple) |
| Novel structural discoveries | 4 (suffix channel, vertical alignment, column schema, foreign keys) |
| Total documented discoveries | 23 |
| Deadlocks resolved | 1 (Zingiber/Mel -- 41-0 verdict for Mel) |
| Deadlocks partially broken | 1 (Opium/Castoreum -- 9 Castoreum stems confirmed in v7) |
| Deadlocks permanent | 1 (Galanga/Cubeba/Nux moschata -- 47 TIED, unbreakable with 50 recipes) |
| Philonium folios confirmed | 4 (f88v, f95v, f96r, f102r) |
| Requies Magna folios found | 0 |
| Validation phases complete | 4 of 10 |
| Data contracts | 16/16 PASS (2 warnings) |
| Null models | 5/5 system beats (p < 0.01) |
| Baselines | 3/5 beat the system (F1 metric broken) |
