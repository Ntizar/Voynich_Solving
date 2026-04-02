# Methodology -- Analytical Pipeline and Tools

> **Cleanup note (Session 15):** Some exploratory scripts referenced below (v1-v6 solvers,
> visualization tools, etc.) have been removed from the repository. The methodology they
> implemented is preserved here for reference. Current validation scripts are in `scripts/`.
> Provenance scripts that generated the frozen CSV data remain as `temp_*.py` in the root.

## Data Sources

### Primary: STA1 2.0 Transcription

- **File:** `zenodo_voynich/corpus/voynich_sta.txt`
- **Format:** IVTFF (Interlinear Voynich Text File Format)
- **Author:** Cesar Diaz-Cerio (Zenodo repository)
- **What it is:** The Voynich text transcribed using "Structural Transcription Alphabet 1" version 2.0, which represents each glyph group as a sequence of atomic symbols (A1, B2, K1, J1, etc.) rather than the traditional EVA alphabet
- **Why STA1:** STA1 atoms are designed to capture structural/positional features of glyph components, enabling morphological analysis impossible with EVA

### Line Format

```
<f87v.3,+P0>      A2K1J1A1U1A2.A1Q1J1A2.U2A2<->A2Q2K2A1C1.S2A1C2
```

- `<f87v.3,+P0>` = Folio f87v, line 3, continuation paragraph
- Words separated by `.`
- `<->` separates text blocks (left/right of plant drawing)
- Each word is a sequence of STA1 atoms: `A2K1J1A1U1A2`

### STA1 Atom Categories

**Final atoms (functional suffixes):**
- `A1, A2, A3` -- Action-related (A2 = verb/instruction)
- `B1, B2, B3, B4` -- Reference-related (B2 = ingredient reference)
- `C1, C2` -- Entity-related (C1 = subject/name marker)
- `G1, G3` -- Property-related (G1 = attribute/description)
- `F1, F2, F3` -- Connector-related
- `E1, E2` -- Termination markers
- `H1` -- Special marker

**Stem atoms (structural components):**
- `K1, K2` -- Common structural atoms
- `J1` -- Connector within stems
- `L1` -- Lateral component
- `D1` -- Initial descender
- `Q1, Q2` -- Loop components
- `P1, P2` -- Plume components
- `U1, U2` -- Upper components
- `T1, T2` -- Table components
- `A1` (in non-final position) -- Within-stem connector

### Secondary: Historical Recipe Database

- **File:** `recetas_historicas_medievales.csv`
- **Flat file:** `recetas_historicas_ingredientes_flat.csv` (613 ingredient-recipe rows)
- **Sources:** Manually compiled from:
  - Antidotarium Nicolai (Salerno, s.XII)
  - Galeno / Andromachus (Theriac Magna)
  - Mitridates VI / Galeno (Mithridatium)
  - Jeronimo Fracastoro (Diascordium)
  - Circa Instans (Salerno, s.XII)
  - Grabadin / Mesue (compound medicines)
  - Avicenna Canon
  - Abulcasis al-Tasrif
  - Salernitano compilations
- **50 recipes** with full ingredient lists classified as ACTIVO/ESPECIA/BASE
- **152 unique ingredients**, 613 ingredient-recipe pairs

---

## Analytical Pipeline

### Phase 1: Structural Analysis

1. **Suffix extraction** (`temp_vertical_align.py`)
   - Parse each word into atoms using regex
   - Identify the final atom
   - Compute H(final | stem) conditional entropy
   - Compare against null model

2. **Vertical alignment test** (`temp_vertical_align.py`, `temp_compare_languages.py`)
   - For each pair of consecutive lines, check if final atoms at same position match
   - Compute match rate, compare against Latin/Spanish baselines

3. **Positional column analysis** (`temp_sql_schema.py`, `temp_grid_tags.py`)
   - For each word position (column 1, 2, 3...) compute tag distribution
   - Generate heatmaps per section

### Phase 2: Entity Extraction

4. **Stem extraction** (`temp_entity_extractor.py`)
   - Extract stems from Botany section columns 1-2 (C1-tagged words)
   - Classify as Exclusive (1 folio) vs Generic (multi-folio)
   - Build stem-to-folio mapping

5. **Cross-section traceability** (`temp_cross_reference.py`, `temp_mega_index.py`)
   - For each Botany stem, search Recipe/Pharmacy sections
   - Record destination folios, frequencies, and suffix changes
   - Generate master index (217 stems)

### Phase 3: Historical Matching

6. **Recipe profiling** (`temp_voynich_all_recipes.py`)
   - For each Recipe folio, count: unique stems, exclusive stems, generic stems
   - Compute ratios: exclusive%, generic%, action%

7. **Historical recipe compilation** (`temp_historical_recipes.py`)
   - Build database of 8 medieval recipes with full ingredient lists
   - Classify each ingredient as ACTIVO, ESPECIA, or BASE

8. **Match generation** (`temp_generate_match_csv.py`)
   - Compare each Voynich recipe folio's ingredient count against historical recipes
   - Generate similarity scores

### Phase 4: Identification

9. **Cross-consistency test** (`temp_consistency_matrix.py`)
   - Find stems appearing in 2+ matched recipe folios
   - Check if category assignment (ACTIVO/ESPECIA/BASE) is consistent

10. **Constraint propagation** (`temp_constraint_solver.py`)
    - For consistent stems, intersect ingredient lists of the matched historical recipes
    - If intersection = 1 ingredient --> confirmed identification

11. **Elimination solver** (`temp_elimination_solver.py`, `temp_final_identifications.py`)
    - Use confirmed IDs to eliminate candidates from other stems
    - Use folio absence/presence as logical constraints
    - Chain eliminations to derive further IDs

---

## Tools and Environment

- **Python 3.x** on Windows
- **Obsidian** for knowledge graph visualization
- All scripts use `sys.stdout.reconfigure(encoding='utf-8')` for Windows compatibility
- No external ML libraries -- all analysis is structural/statistical
- CSV files loadable in Excel for manual exploration

## Key Regex Pattern for STA1 Atom Parsing

```python
import re
ATOM_PATTERN = re.compile(
    r'(A[1-3]|B[1-4]|C[1-2]|D1|E[1-2]|F[1-3]|G[1-3]|H1|'
    r'J1|K[1ab]|L1|N1|P[12]|Q[12]|T[12]|U[12]|'
    r'Aa|Ba|Cm|Xb|Ab|Bd|Cl)'
)
```

## Important Caveats

1. The STA1 2.0 transcription has known ambiguities (see Cesar's validation notebook #08)
2. Our stem extraction treats the LAST recognized atom as the suffix -- compound suffixes (e.g., B2B1A2) are not yet handled
3. Historical recipe matching by ingredient count alone has limited discriminating power -- the same count could match multiple recipes. We use it as a FILTER, not a proof.
4. The 60% conflict rate in the consistency test suggests the frequency-rank heuristic for assigning ingredients to stems is too crude. The constraint solver approach (intersecting by CATEGORY, not by rank) produces much better results.
5. **CRITICAL (Session 15):** The F1 metric used for content-based matching is non-discriminative with only 22 identified ingredients. A majority-recipe baseline achieves 100% F1. See `docs/VALIDATION.md` for details.

---

## Phase 5: Validation Framework (Session 15)

A scientific validation framework was built to test the hypothesis rigorously:

### Validation Pipeline

12. **Data contracts** (`scripts/validation/data_contracts.py`)
    - 16 integrity checks: schema validation, uniqueness, referential integrity, normalization, numeric sanity
    - Detects data drift via SHA-256 hashes in `scripts/core/config.py`

13. **Blind splits** (`scripts/validation/blind_splits.py`)
    - Deterministic train/test partition (seed=42, 80/20 split)
    - Contamination detector for retrospective leakage analysis
    - Outputs: `output/splits/blind_splits.json`

14. **Null models** (`scripts/validation/null_models.py`)
    - 5 null models x 500 iterations each: wrong genre, random stems, shuffled ingredients, permuted stems, permuted folios
    - Computes p-values against the real system's F1
    - Outputs: `output/validation/null_models_results.json`

15. **Baselines** (`scripts/validation/baselines.py`)
    - 5 rival baselines: majority recipe, most common ingredients, all ingredients, frequency rank, random
    - Revealed F1 metric is non-discriminative (majority baseline = 100%)
    - Outputs: `output/validation/baselines_results.json`

### Configuration

- `scripts/core/config.py` -- Central config with paths, SHA-256 hashes, seeds, thresholds
- `scripts/core/data_loader.py` -- Unified loader for all 12 source files
- All validation scripts are deterministic (seed=42) and reproducible
