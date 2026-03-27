# MASTERTMIND: Structural Decipherment of the Voynich Manuscript

**Status:** Active research -- Partial structural decipherment achieved  
**Author:** Ntizar  
**Base data:** STA1 2.0 transcription (Cesar Diaz-Cerio, Zenodo)  
**Approach:** 2D structural analysis + cross-reference with medieval pharmacopoeia  

---

## What Is This?

This repository contains the working data, analysis scripts, and findings of an ongoing project to structurally decipher the Voynich Manuscript (MS 408, Beinecke Library, Yale).

Unlike previous attempts that focus on decrypting individual glyphs or identifying the underlying language, this project treats the manuscript as a **medieval pharmaceutical database** and works at the **structural level**: matching recipe architectures, ingredient counts, and cross-section references against real historical formulas.

## Key Thesis

> The Voynich Manuscript is a **Materia Medica + Antidotarium** (pharmaceutical compendium) organized as a relational database, where Botany pages define ingredients and Recipe/Pharmacy pages reference them via consistent vocabulary stems.

## Results Summary

### Confirmed Identifications

| Voynich Stem | Historical Ingredient | Confidence | Method |
|---|---|---|---|
| `[K1K2A1]` | **Galbanum** (Ferula galbaniflua resin) | 99% | Unique intersection across 3 recipes |
| `[K1A3]` | **Crocus / Saffron** | 95% | Logical elimination: absent from Diascordium folio |
| `[BaA3]` | **Semantic class: plant gum-resin** | 90% | Always maps to gum-resin (Opopanax/Diagridium/Terebinthina) |

### Partial Identifications (2-4 candidates)

| Voynich Stem | Candidates | Confidence |
|---|---|---|
| `[U2J1A1]` | Opium / Aloe (potent drug class) | 70% |
| `[K1J1A1]` | Cinnamomum (cinnamon) | 65% |
| `[L1A1]` | Piper longum or Zingiber | 60% |
| `[D1A1Q1K1A1]` | Piper longum or Zingiber | 60% |
| `[D1A1Q1J1A1]` | Squilla, Petroselinum, Valeriana, or Acorus | 40% |

### Structural Discoveries

1. **Functional Suffix Channel** -- Voynich words decompose as STEM + FINAL_ATOM where the final atom is a constrained syntactic tag (H = 1.246 bits, Z = -210 vs null)
2. **2D Vertical Alignment** -- Suffixes align vertically across consecutive lines at 27% (vs 8% in Latin/Spanish), proving "invisible column" writing
3. **Positional Column Schema** -- Columns 1-2 favor Entity tags (C1/G1), columns 3+ favor Action tags (A2), resembling SQL table structure
4. **Cross-Section Foreign Keys** -- 46.9% of exclusive Botany stems reappear in Recipe sections with changed suffixes (C1->B2), proving relational referencing
5. **Recipe-Historical Matching** -- 3 perfect matches by ingredient count: f87v=Unguentum Apostolorum, f93v=Diascordium, f96v=Pillulae Aureae

## Repository Structure

```
MASTERTMIND/
|
|-- README.md                          # This file
|-- docs/
|   |-- DISCOVERIES.md                 # Detailed technical findings
|   |-- IDENTIFICATIONS.md             # All stem identifications with reasoning
|   |-- METHODOLOGY.md                 # Analytical pipeline and tools
|   |-- DATA_DICTIONARY.md             # Every CSV file explained
|   |-- NEXT_STEPS.md                  # Roadmap for future work
|   |-- SESSION_LOG.md                 # Chronological work record
|
|-- zenodo_voynich/                    # Source data (Cesar's Zenodo study)
|   |-- corpus/voynich_sta.txt         # Primary STA1 2.0 transcription
|   |-- results/*.json                 # Cesar's 48-notebook analysis results
|   |-- notebooks/*.ipynb              # Cesar's Jupyter notebooks
|   |-- papers/*.pdf                   # Cesar's published papers
|   |-- README.md                      # Cesar's study documentation
|
|-- Voynich_Graph/                     # Obsidian vault (130+ interconnected notes)
|   |-- Plantas/                       # One note per identified plant stem
|   |-- Folios_Botanica/               # One note per botany folio
|   |-- Folios_Recetas/                # One note per recipe folio
|
|-- scripts/                           # Analysis scripts (Python)
|   |-- (temp_*.py scripts moved here for organization)
|
|-- voynich_*.csv                      # Generated data files (10 CSVs)
|-- recetas_historicas_medievales.csv   # Historical recipe database
```

## How to Continue This Work

1. Read `docs/DISCOVERIES.md` for the full chain of findings
2. Read `docs/IDENTIFICATIONS.md` for each identification's reasoning
3. Read `docs/NEXT_STEPS.md` for the prioritized roadmap
4. Open the CSV files in Excel to explore the data
5. Open `Voynich_Graph/` as an Obsidian vault to see the knowledge graph

## Data Sources

- **Voynich transcription:** STA1 2.0 by Cesar Diaz-Cerio (Zenodo DOI: see zenodo_voynich/README.md)
- **Historical recipes:** Manually compiled from Antidotarium Nicolai (s.XII), Galeno, Fracastoro, Circa Instans
- **Folio images:** Available at https://voynich.nu/

## Important Notes

- All scripts use `sys.stdout.reconfigure(encoding='utf-8')` for Windows cp1252 compatibility
- The STA1 2.0 transcription uses atomic symbols (A1, B2, K1, etc.), NOT the traditional EVA alphabet
- "Exclusive" stems appear in only one Botany folio (= proper plant names); "Generic" stems appear across many folios (= common words like "water", "leaf")
