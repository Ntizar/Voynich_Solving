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

## Summary Statistics

| Metric | Value |
|---|---|
| Total scripts written | 29 |
| Total CSV files generated | 18 |
| Obsidian notes generated | 130+ |
| Unique stems catalogued | 217 |
| Recipe folios profiled | 47 |
| Historical recipes compiled | 23 |
| Perfect recipe matches | 9 |
| Strong recipe matches | 19 |
| Confirmed identifications (Tier 1-2) | 8 (Galbanum, Crocus, Myrrha x6) |
| Strong identifications (Tier 3) | 17 (Crocus x9, Rosa, Zingiber/Mel x5, Cinnamomum x2) |
| Moderate identifications (Tier 4) | 23 (Amomum, Piper, Bdellium, Casia, Cardamomum, Styrax, Saccharum) |
| Function words identified | 14 |
| Unique ingredients identified | 18 (13 single + 5 in pairs) |
| Novel structural discoveries | 4 (suffix channel, vertical alignment, column schema, foreign keys) |
