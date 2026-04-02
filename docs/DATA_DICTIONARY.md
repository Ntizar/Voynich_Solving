# Data Dictionary -- All CSV Files

Every generated CSV file, its columns, and how to interpret them.

---

## 1. voynich_columnas_botanica.csv

**What:** Distribution of functional suffix tags by word position (column) in the Botany section.

| Column | Description |
|---|---|
| Posicion_Columna | Word position in line (1 = first word, 2 = second, etc.) |
| Total_Palabras | Total words at this position across all Botany lines |
| Tag_X | Count of tag X (A1, A2, B2, C1, G1, etc.) at this position |
| Pct_Tag_X | Percentage of tag X at this position |

**Use:** Create heatmap showing how tags shift from Entity (C1/G1) in early columns to Action (A2) in later columns.

---

## 2. voynich_secciones_etiquetas.csv

**What:** Distribution of functional suffix tags by manuscript section.

| Column | Description |
|---|---|
| Seccion | Manuscript section (Botanica, Astronomia, Biologia, Farmacia, Recetas) |
| Total_Palabras | Total words in section |
| Tag_X | Count of tag X in section |
| Pct_Tag_X | Percentage of tag X |

**Use:** Compare the "schema" of different sections. Botany is C1-heavy, Recipes are A2+B2-heavy.

---

## 3. voynich_cruce_ingredientes.csv

**What:** Survival rates of Exclusive vs Generic stems when crossing from Botany to Recipe sections.

| Column | Description |
|---|---|
| Tipo_Vocabulario | "Exclusiva" or "Comun (Generica)" |
| Total_Stems | How many stems of this type |
| Aparecen_en_Recetas | How many reappear in Recipe section |
| Pct_Supervivencia | Survival percentage |

**Key values:** 46.9% of Exclusives survive; 96.5% of Generics survive.

---

## 4. voynich_mega_indice_conexiones.csv

**MASTER FILE** -- The most important data file.

**What:** Complete index of 217 plant entity stems with full traceability.

| Column | Description |
|---|---|
| Raiz_Planta | The Voynich stem (STA1 atoms, minus final suffix) |
| Tipo_Vocabulario | "Exclusiva (Nombre Propio)" or "Comun (Generica)" |
| Folios_Origen_Botanica | Which Botany folio(s) this stem originates from |
| Apariciones_en_Recetas | Total count in Recipe section |
| Folios_Destino_Recetas | Which Recipe folios this stem appears in (with counts) |
| Etiquetas_Dominantes_en_Recetas | Most common suffixes when appearing in Recipes |

**Use:** This is the "foreign key table" of the manuscript. For any stem, you can trace it from its Botany origin to all its Recipe destinations.

---

## 5. voynich_todas_recetas_perfil.csv

**What:** Profile of every Recipe-section folio.

| Column | Description |
|---|---|
| Folio_Receta | Folio identifier (f87r, f87v, etc.) |
| Total_Palabras | Word count in folio |
| N_Ingredientes_Exclusivos | Count of Exclusive stems |
| N_Ingredientes_Genericos | Count of Generic stems |
| N_Acciones_A2 | Count of A2-tagged words (actions/verbs) |
| Ratio_Exclusivos_% | Percentage of exclusive stems |
| Ratio_Genericos_% | Percentage of generic stems |
| Ratio_Acciones_% | Percentage of action words |
| Lista_Exclusivos_Top5 | Top 5 exclusive stems with counts |
| Lista_Genericos_Top5 | Top 5 generic stems with counts |
| Etiquetas_Dominantes | Top 4 suffix tags with counts |

**Use:** Compare folio profiles against historical recipe profiles for matching.

---

## 6. recetas_historicas_medievales.csv

**What:** Database of 8 historical medieval pharmaceutical recipes.

| Column | Description |
|---|---|
| Nombre_Receta | Recipe name |
| Fuente | Historical source |
| Tipo | Recipe type (antidote, purgative, ointment, etc.) |
| Total_Ingredientes | Total ingredient count |
| N_Activos_Raros | Count of ACTIVO (active/rare) ingredients |
| N_Especias | Count of ESPECIA (spice) ingredients |
| N_Bases | Count of BASE (vehicle/base) ingredients |
| Ratio_Activos_% | ACTIVO percentage |
| Ratio_Especias_% | ESPECIA percentage |
| Ratio_Bases_% | BASE percentage |
| Lista_Activos | Pipe-separated list of ACTIVO ingredients |
| Lista_Especias | Pipe-separated list of ESPECIA ingredients |
| Lista_Bases | Pipe-separated list of BASE ingredients |

**Recipes included:**
1. Theriac Magna (64 ingredients)
2. Mithridatium (54 ingredients)
3. Diascordium (14 ingredients)
4. Pillulae Cochiae (5 ingredients)
5. Pillulae Aureae (7 ingredients)
6. Unguentum Apostolorum (12 ingredients)
7. Electuarium de Succo Rosarum (8 ingredients)
8. Aurea Alexandrina (22 ingredients)

---

## 7. voynich_cruces_recetas_historicas.csv

**What:** Direct matches between Voynich recipe folios and historical recipes.

| Column | Description |
|---|---|
| Folio_Voynich | Voynich folio |
| Receta_Historica_Candidata | Matched historical recipe |
| Similitud_Tamano | Size match percentage |
| N_Ingredientes_Voynich | Ingredient count in Voynich folio |
| N_Ingredientes_Historicos | Ingredient count in historical recipe |
| Ingredientes_Historicos | Full ingredient list of historical recipe |

**Perfect matches:** f87v=Ung.Apostolorum, f93v=Diascordium, f96v=Pill.Aureae

---

## 8. voynich_consistencia_cruzada.csv

**What:** Cross-consistency test results for 25 stems appearing in 2+ matched recipes.

| Column | Description |
|---|---|
| Raiz_Voynich | Voynich stem |
| Tipo_Vocabulario | Exclusive or Generic |
| N_Recetas_Donde_Aparece | How many matched recipes contain this stem |
| Es_Consistente | SI/NO -- is the category the same across all recipes? |
| Categorias_Asignadas | Categories assigned (ACTIVO/ESPECIA/BASE/DESCONOCIDO) |
| Match_N_Receta | Recipe name for match N |
| Match_N_Ingrediente | Assigned ingredient for match N |
| Match_N_Categoria | Assigned category for match N |

---

## 9. voynich_constraint_solver_results.csv

**What:** Output of the constraint propagation solver.

| Column | Description |
|---|---|
| Stem | Voynich stem |
| Type | Exclusive or Generic |
| Category | Functional category (ACTIVO/ESPECIA/DESCONOCIDO) |
| N_Recipes | Number of recipe matches |
| Origin | Origin folio |
| Intersection_Size | Size of ingredient intersection |
| Candidates | Candidate ingredients (pipe-separated) |
| Confidence | Confidence level |

---

## 10. voynich_identificaciones_final.csv

**What:** Final consolidated identification table.

| Column | Description |
|---|---|
| Stem_Voynich | Voynich stem |
| Identificacion | Identified ingredient or candidate list |
| Confianza | Confidence level with percentage |
| Categoria | ACTIVO or ESPECIA |
| Razonamiento | Brief reasoning |

---

## 11. voynich_identificaciones_candidatas.csv

**What:** Detailed identification table with full reasoning chains.

| Column | Description |
|---|---|
| Stem | Voynich stem |
| Tipo | Exclusive or Generic |
| Folio_Origen | Origin folio(s) |
| Categoria | Functional category |
| Identificacion | Candidate identification |
| Confianza | Confidence level |
| N_Candidatos | Number of candidates |
| Metodo | Method used |
| Cadena_Razonamiento | Full step-by-step reasoning chain |
| Verificacion_Visual | What to look for on voynich.nu |

---

## 12. voynich_unified_identifications_v7.csv

**What:** Current identification table (v7, 75 entries, 22 unique ingredients + 8 function words).

| Column | Description |
|---|---|
| Stem | Voynich stem (STA1 atoms) |
| Identified_Ingredient | Real medieval ingredient or "FUNCTION_WORD" |
| Confidence | Confidence percentage (0-100) |
| Tier | 0 (function), 1 (confirmed), 2 (high), 3 (strong), 4 (moderate) |
| Method | Identification method (constraint, elimination, intersection, etc.) |
| Source_Session | Session where identification was made |

**Note:** v7 identifications are **contaminated** (built using test data). See `docs/VALIDATION.md`.

---

## 13. voynich_matching_v7.csv

**What:** Best recipe match per folio using v7 identifications.

| Column | Description |
|---|---|
| Folio | Voynich folio (f87r, f87v, etc.) |
| Best_Recipe | Name of best-matching historical recipe |
| F1 | F1 score (0-1) **[UNDER REVIEW -- see Validation]** |
| Precision | Precision score |
| Recall | Recall score |
| N_Identified | Number of identified ingredients in folio |

---

## 14. voynich_expanded_matching_v7.csv

**What:** Full 48x50 matching matrix (v7).

Each row is a folio, each column is a recipe, values are F1 scores. Used for heatmap visualizations and comparative analysis.

---

## 15. recetas_historicas_ingredientes_flat.csv

**What:** Flat ingredient table (613 rows) for all 50 historical recipes.

| Column | Description |
|---|---|
| Nombre_Receta | Recipe name (foreign key to recipe database) |
| Ingrediente | Ingredient name |
| Categoria | ACTIVO / ESPECIA / BASE |

---

## 16. voynich_all_recipe_folio_stems.csv

**What:** Complete stem extraction from all 48 recipe folios (8,232 rows).

| Column | Description |
|---|---|
| Folio | Recipe folio identifier |
| Stem | Voynich stem (atoms minus final suffix) |
| Count | Number of occurrences in folio |
| Suffix | Most common final atom |

---

## Validation Output Files

These files are in the `output/` directory (gitignored -- regenerable by running the validation scripts).

### output/splits/blind_splits.json

**What:** Frozen train/test partitions with integrity hash.

| Field | Description |
|---|---|
| seed | Random seed used (42) |
| test_fraction | Test set fraction (0.2) |
| test_folios | List of 9 test folios |
| train_folios | List of 39 training folios |
| test_recipes | List of 10 test recipes |
| train_recipes | List of 40 training recipes |
| sha256 | Integrity hash of the partition data |

### output/validation/null_models_results.json

**What:** Results from 5 null models x 500 iterations each.

| Field | Description |
|---|---|
| model_name | Name of null model (wrong_genre, random_stems, etc.) |
| system_f1 | System's mean F1 (81.9%) |
| null_mean_f1 | Mean F1 across 500 null iterations |
| null_std_f1 | Standard deviation of null F1 |
| p_value | Proportion of null iterations >= system F1 |
| delta_pp | Percentage point difference (system - null) |

### output/validation/baselines_results.json

**What:** Results from 5 rival baselines.

| Field | Description |
|---|---|
| baseline_name | Name of baseline (majority_recipe, most_common, etc.) |
| baseline_f1 | Baseline's mean F1 |
| system_f1 | System's mean F1 (81.9%) |
| system_wins | Whether system beats this baseline (boolean) |
