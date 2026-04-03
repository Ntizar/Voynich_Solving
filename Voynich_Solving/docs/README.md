# Voynich Solving -- Structural Decipherment of the Voynich Manuscript

> **[EN]** A computational project investigating whether the Voynich Manuscript is a medieval pharmaceutical database.  
> **[ES]** Un proyecto computacional que investiga si el Manuscrito Voynich es una base de datos farmaceutica medieval.

**Author / Autor:** Ntizar  
**Status / Estado:** Research complete / Investigacion completada  
**Sessions / Sesiones:** 17 (April 2026 / Abril 2026)

---

# English

## The Mystery

The Voynich Manuscript (MS 408, Beinecke Library, Yale) is a 600-year-old book that nobody can read. Written in an unknown script, filled with drawings of unidentified plants, astronomical diagrams, and bathing figures, it has defeated every cryptographer, linguist, and codebreaker who has tried to crack it for over a century.

Most attempts treat it as encrypted text -- a cipher hiding a natural language underneath. None have succeeded.

**This project takes a completely different approach.**

## The Hypothesis

Instead of trying to read individual words, we treat the manuscript as what it structurally *looks like*: a **database**. Specifically, a medieval pharmaceutical compendium -- a *Materia Medica* (plant catalog) cross-referenced with an *Antidotarium* (recipe book).

## What We Proved

### Structural analysis (VALIDATED)

Three independent statistical tests confirm the Voynich recipe section has anomalous structure compared to Latin medical texts:

| Test | Voynich | Latin Controls | p-value | Verdict |
|---|---|---|---|---|
| Suffix entropy | 2.74 bits | 4.02 bits | < 0.0001 | **SIGNIFICANT** -- much lower entropy, consistent with structured notation |
| Vertical alignment | 38.9% | 12.5% | < 0.0001 | **SIGNIFICANT** -- text written in columnar grid, not prose |
| Schema variation (KL divergence) | 0.039 | 0.004 | < 0.0001 | **SIGNIFICANT** -- different sections use different "database schemas" |
| Stem reuse | 19.3% | 54.2% | 1.000 | NOT significant -- Voynich has less reuse, not more |

**3 out of 4 structural anomalies confirmed against 1000 Monte Carlo simulations of synthetic Latin medical controls.**

### Cipher hypothesis (RULED OUT)

- Index of Coincidence = 0.0769 -- matches natural language, rules out polyalphabetic cipher
- Homophonic substitution simulation does NOT match Voynich's entropy/IC profile
- **The text is not a cipher over a natural language.** It has the statistical properties of a natural language or structured notation, not an encryption.

### Cross-validation stability (CONFIRMED)

- 5-fold cross-validation: Mean F1 = 66.8% +/- 1.2% -- extremely stable
- Ablation: No single ingredient is critical (max impact -2.4pp for Crocus)
- Permutation test: p = 0.000 for F1 and Exclusion accuracy -- the mapping captures real signal

## What We Could NOT Prove

### Specific stem-to-ingredient identifications (FAILED against baselines)

We built v7 (manually curated, 75 stems, 22 ingredients) and v8 (fully automated, 47 ingredient stems, 34 ingredients). The results:

| Method | Fixed F1 | vs Best Baseline |
|---|---|---|
| v8 automated (test set) | 43.0% | **BEATEN** by most_common (51.2%), all_ings (61.4%), majority_recipe (64.8%) |
| v7 curated (all data) | 81.9% | Wins on discriminative metrics (Rare F1 72.4%), but MRR/P@1 = 100% is tautological |

**The automated pipeline captures some real signal (permutation test p=0.000) but cannot beat trivial baselines.** The manually curated v7 identifications perform better but their evaluation is circular (targets chosen by best-match).

### Final hard push (Session 17)

The project also tested a final series of stricter experiments:

- a shared benchmark across `STA stems`, `STA tokens`, and `EVA tokens`
- corpus diagnostics for recipe overlap and train-support gaps
- external-source mining from open Amsterdam pharmacopoeia witnesses
- an augmented recipe corpus tested in parallel, without overwriting the frozen validation corpus

The augmented benchmark still failed across all tested representations:

| Representation | Fixed F1 | Best Baseline | Verdict |
|---|---:|---:|---|
| `sta_stem_frozen` | 44.6% | 70.5% | FAIL |
| `sta_token` | 51.7% | 67.6% | FAIL |
| `eva_token` | 60.5% | 87.6% | FAIL |

This is the strongest reason the repository now separates **structure** from **reading**.

Key problems:
- **Coverage is only 18.7%** -- the vast majority of the text remains unexplained
- **v8 vs v7 agreement is 12.7%** -- without ground truth, multiple locally-optimal mappings exist
- The 22 identified ingredients are all ultra-common in medieval recipes, inflating baseline scores

## Honest Bottom Line

**What we can claim:**
1. The Voynich recipe section has statistically anomalous structure consistent with a pharmaceutical database (3/4 tests, p < 0.0001)
2. It is NOT a cipher (IC = 0.0769)
3. The structural patterns cannot be explained by normal Latin manuscript conventions

**What we cannot claim:**
1. That specific Voynich stems correspond to specific ingredients (mapping fails against baselines)
2. That we can "read" any part of the manuscript

The structural findings are publication-worthy. The decipherment remains unsolved.

The semantic track should be treated as unresolved unless a future blind-test experiment beats the best baseline by a clear and reproducible margin.

## Key Identifications (v7 -- manually curated, NOT independently validated)

| Voynich Stem | Ingredient | Confidence | How |
|---|---|---|---|
| `K1K2A1` | **Galbanum** (Ferula resin) | 99% | Only ingredient at the intersection of 3 recipes |
| `K1A3` | **Crocus** (Saffron) | 95% | Absent from the Diascordium folio, which has Cinnamomum but not Crocus |
| `BaA3` | **Plant gum-resin class** | 90% | Always maps to a gum-resin regardless of recipe |

Plus 72 more stems at 60-92% confidence. Full table in `IDENTIFICATIONS.md`. **Caveat:** These identifications have not been independently validated. v8 automated replication produced only 12.7% agreement.

## Project Structure

```
Voynich_Solving/
|-- docs/                              # Documentation
|   |-- README.md                      # This file (bilingual EN/ES)
|   |-- README.html                    # Visual bilingual landing page
|   |-- METHODOLOGY.md                 # Analytical pipeline
|   |-- DISCOVERIES.md                 # 29 technical discoveries
|   |-- IDENTIFICATIONS.md            # 75 stem identifications with reasoning
|   |-- VALIDATION.md                  # Validation protocol and results (Phases 0-4b)
|   |-- DATA_DICTIONARY.md            # Every CSV explained
|   |-- NEXT_STEPS.md                  # Roadmap and honest assessment
|   |-- SESSION_LOG.md                 # 16 sessions of work
|-- data/
|   |-- corpus/                        # Voynich transcription (STA1 2.0)
|   |-- identifications/               # Stem-to-ingredient mappings (v7)
|   |-- recipes/                       # 50 historical medieval recipes
|   |-- matching/                      # Folio-to-recipe matching results
|   |-- analysis/                      # Cross-consistency & mega-index
|-- scripts/
|   |-- validation/                    # Full validation framework
|   |   |-- config.py                  # Central config, SHA-256 hashes
|   |   |-- data_loader.py            # Unified dataset loader
|   |   |-- data_contracts.py         # Phase 1: Data integrity (16/16 PASS)
|   |   |-- blind_splits.py           # Phase 2: Train/test splits (seed=42)
|   |   |-- null_models.py            # Phase 3: 5 null models (all beaten)
|   |   |-- baselines.py              # Phase 4: 5 baselines
|   |   |-- alternative_metrics.py    # Phase 4b: 7 discriminative metrics
|   |   |-- v8_builder.py             # Automated constraint solver (no curation)
|   |   |-- v8_evaluator.py           # Non-tautological evaluation (3 strategies)
|   |   |-- comparative_corpus.py     # Structural analysis vs Latin controls
|   |   |-- cipher_hypothesis.py      # IC, homophonic, polyalphabetic tests
|   |   |-- sensitivity_analysis.py   # K-fold CV, ablation, coverage
|   |-- analysis/                      # Research session scripts (provenance)
|   |-- utils/                         # Hash generator, Obsidian vault generator
|-- output/                            # Validation outputs (regenerable)
|   |-- splits/                        # Frozen train/test split
|   |-- validation/                    # All validation results (JSON/CSV)
|-- dashboard/                         # Interactive dashboard + design system
```

## Running the Full Validation

```bash
cd Voynich_Solving

# Phase 1-4b: Core validation
python -m scripts.validation.data_contracts        # 16 data integrity contracts
python -m scripts.validation.blind_splits           # Train/test splits (seed=42)
python -m scripts.validation.null_models            # 5 null models x 500 iterations
python -m scripts.validation.baselines              # 5 rival baselines
python -m scripts.validation.alternative_metrics    # 7 discriminative metrics

# v8: Automated pipeline + blind test
python -m scripts.validation.v8_builder             # Build v8 identifications (train only)
python -m scripts.validation.v8_evaluator           # Evaluate on test set (non-tautological)

# Independent analyses
python -m scripts.validation.comparative_corpus     # Structural claims vs Latin controls
python -m scripts.validation.cipher_hypothesis      # Cipher hypothesis testing
python -m scripts.validation.sensitivity_analysis   # K-fold CV, ablation, coverage
```

## Sources

- **Voynich transcription:** STA1 2.0 by Cesar Diaz-Cerio ([Zenodo](https://zenodo.org/records/7633206))
- **Historical recipes:** Antidotarium Nicolai (s.XII), Galeno, Fracastoro, Circa Instans, Grabadin/Mesue, Avicenna Canon, Abulcasis al-Tasrif
- **Folio images:** [voynich.nu](https://voynich.nu/)

---

# Castellano

## El Misterio

El Manuscrito Voynich (MS 408, Biblioteca Beinecke, Yale) es un libro de 600 anos que nadie puede leer. Escrito en un sistema de escritura desconocido, ha derrotado a todo criptografo y linguista que ha intentado descifrarlo durante mas de un siglo.

**Este proyecto toma un enfoque completamente diferente.**

## La Hipotesis

En lugar de intentar leer palabras individuales, tratamos el manuscrito como lo que estructuralmente *parece ser*: una **base de datos farmaceutica medieval** -- una *Materia Medica* cruzada con un *Antidotarium*.

## Lo Que Demostramos

### Analisis estructural (VALIDADO)

Tres tests estadisticos independientes confirman que la seccion de recetas tiene estructura anomala vs textos medicos latinos:

| Test | Voynich | Controles Latinos | p-valor | Veredicto |
|---|---|---|---|---|
| Entropia de sufijos | 2.74 bits | 4.02 bits | < 0.0001 | **SIGNIFICATIVO** |
| Alineacion vertical | 38.9% | 12.5% | < 0.0001 | **SIGNIFICATIVO** |
| Variacion de esquema (KL) | 0.039 | 0.004 | < 0.0001 | **SIGNIFICATIVO** |
| Reutilizacion de stems | 19.3% | 54.2% | 1.000 | NO significativo |

**3 de 4 anomalias confirmadas contra 1000 simulaciones Monte Carlo.**

### Hipotesis del cifrado (DESCARTADA)

- Indice de Coincidencia = 0.0769 -- coincide con lenguaje natural, descarta cifrado polialfabetico
- La simulacion homofoica NO coincide con el perfil del Voynich
- **El texto no es un cifrado.** Tiene propiedades de lenguaje natural o notacion estructurada.

### Estabilidad (CONFIRMADA)

- Validacion cruzada 5-fold: F1 medio = 66.8% +/- 1.2%
- Ablacion: ningun ingrediente es critico (impacto maximo -2.4pp)
- Test de permutacion: p = 0.000 para F1 y Exclusion

## Lo Que NO Pudimos Demostrar

### Identificaciones especificas de stems (FALLO contra baselines)

| Metodo | F1 Fijo | vs Mejor Baseline |
|---|---|---|
| v8 automatizado (test) | 43.0% | **SUPERADO** por baselines triviales (51-65%) |
| v7 curado (todos los datos) | 81.9% | Gana en metricas discriminativas, pero MRR/P@1 = 100% es tautologico |

**El pipeline automatizado captura senal real (p=0.000) pero no puede superar heuristicas triviales.** La cobertura es solo del 18.7%.

## Conclusion Honesta

**Lo que podemos afirmar:**
1. La seccion de recetas tiene estructura anomala consistente con una base de datos farmaceutica (3/4 tests, p < 0.0001)
2. NO es un cifrado (IC = 0.0769)
3. Los patrones estructurales no se explican por convenciones normales de manuscritos latinos

**Lo que no podemos afirmar:**
1. Que stems especificos correspondan a ingredientes especificos (mapeo falla contra baselines)
2. Que podamos "leer" ninguna parte del manuscrito

Los hallazgos estructurales son publicables. El desciframiento sigue sin resolver.

## Ejecutar la Validacion Completa

```bash
cd Voynich_Solving

# Fases 1-4b: Validacion core
python -m scripts.validation.data_contracts
python -m scripts.validation.blind_splits
python -m scripts.validation.null_models
python -m scripts.validation.baselines
python -m scripts.validation.alternative_metrics

# v8: Pipeline automatizado + test ciego
python -m scripts.validation.v8_builder
python -m scripts.validation.v8_evaluator

# Analisis independientes
python -m scripts.validation.comparative_corpus
python -m scripts.validation.cipher_hypothesis
python -m scripts.validation.sensitivity_analysis
```

## Fuentes

- **Transcripcion Voynich:** STA1 2.0 de Cesar Diaz-Cerio ([Zenodo](https://zenodo.org/records/7633206))
- **Recetas historicas:** Antidotarium Nicolai (s.XII), Galeno, Fracastoro, Circa Instans, Grabadin/Mesue, Canon de Avicena, al-Tasrif de Abulcasis
- **Imagenes de folios:** [voynich.nu](https://voynich.nu/)
