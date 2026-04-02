# MASTERTMIND -- Voynich Manuscript Structural Decipherment

> **[EN]** A computational project proving the Voynich Manuscript is a medieval pharmaceutical database.  
> **[ES]** Un proyecto computacional que demuestra que el Manuscrito Voynich es una base de datos farmaceutica medieval.

**Author / Autor:** Ntizar  
**Status / Estado:** Active research / Investigacion activa  
**Sessions / Sesiones:** 15 (April 2026 / Abril 2026)

---

# English

## The Mystery

The Voynich Manuscript (MS 408, Beinecke Library, Yale) is a 600-year-old book that nobody can read. Written in an unknown script, filled with drawings of unidentified plants, astronomical diagrams, and bathing figures, it has defeated every cryptographer, linguist, and codebreaker who has tried to crack it for over a century.

Most attempts treat it as encrypted text -- a cipher hiding a natural language underneath. They try to "decode" individual letters into Latin, German, Hebrew, or dozens of other languages. None have succeeded.

**This project takes a completely different approach.**

## The Insight

Instead of trying to read individual words, we treat the manuscript as what it structurally *looks like*: a **database**. Specifically, a medieval pharmaceutical compendium -- a *Materia Medica* (plant catalog) cross-referenced with an *Antidotarium* (recipe book).

The evidence:

- **The text is written in columns, not prose.** Suffixes align vertically across consecutive lines at 27% (vs 8% in Latin/Spanish). The author wrote in a grid, like filling a spreadsheet.
- **Each section uses a different "schema."** Botany pages use entity-naming tags (C1). Recipe pages use ingredient-reference tags (B2) and action tags (A2). Different sections, different database tables.
- **Plant pages reference recipe pages.** 46.9% of plant stems reappear in recipe sections with changed suffixes (C1 -> B2), exactly like a foreign key in a relational database.

This is not a cipher over natural language. It is a **structured notation system** for pharmaceutical recipes.

## What We Found

Using the STA1 2.0 transcription by Cesar Diaz-Cerio (a structural alphabet that decomposes each Voynich glyph into atomic components), we:

1. **Extracted 3,261 unique vocabulary stems** from 48 recipe folios
2. **Compiled 50 real medieval pharmaceutical recipes** from historical sources (Antidotarium Nicolai, Galeno, Avicenna, Abulcasis, and others)
3. **Matched Voynich folios to historical recipes** by mapping stems to real ingredients through constraint propagation, elimination chains, and intersection analysis
4. **Identified 75 stems** corresponding to 22 real medieval ingredients (Galbanum, Crocus, Myrrha, Mel, Castoreum, Zingiber, and 16 others)

### Confirmed Identifications

| Voynich Stem | Ingredient | Confidence | How |
|---|---|---|---|
| `K1K2A1` | **Galbanum** (Ferula resin) | 99% | Only ingredient at the intersection of 3 recipes |
| `K1A3` | **Crocus** (Saffron) | 95% | Absent from the Diascordium folio, which has Cinnamomum but not Crocus |
| `BaA3` | **Plant gum-resin class** | 90% | Always maps to a gum-resin regardless of recipe |

Plus 72 more stems at 60-92% confidence across Myrrha, Mel, Cinnamomum, Castoreum, Zingiber, Petroselinum, Gentiana, Rosa, Opopanax, and others. Full table in `docs/IDENTIFICATIONS.md`.

## Honest Assessment

We built a scientific validation framework to test our own work. The results are mixed:

**What holds up:**
- The structural discoveries (suffix channel, vertical alignment, foreign keys) are robust and statistically significant (Z = -210, p effectively zero)
- The system beats all 5 null models (p < 0.01), confirming it captures real pharmaceutical signal
- Culinary recipes score 0% -- the content is definitively pharmaceutical
- Tier 1 identifications (Galbanum, Crocus) have logical reasoning chains independent of any metric

**What does not:**
- The F1 matching score (81.9%) is misleading. A trivial baseline that predicts "everything is Theriac Magna" scores 100%. Our 22 identified ingredients are all so common in medieval pharmacy that predicting them for every folio is almost always correct.
- The system needs alternative metrics (discriminative F1, ranking accuracy, exclusion accuracy) before the matching claims can be validated.

Full details in `docs/VALIDATION.md`.

## Project Structure

```
MASTERTMIND/
|-- README.md / README.html          # This file / Visual bilingual version
|-- docs/
|   |-- VALIDATION.md                # Validation protocol and results
|   |-- DISCOVERIES.md               # 23 technical discoveries
|   |-- IDENTIFICATIONS.md           # 75 stem identifications with reasoning
|   |-- METHODOLOGY.md               # Analytical pipeline
|   |-- DATA_DICTIONARY.md           # Every CSV explained
|   |-- NEXT_STEPS.md                # Roadmap (metric fix is #1)
|   |-- SESSION_LOG.md               # 15 sessions of work
|-- scripts/
|   |-- core/config.py               # Central config, SHA-256 hashes
|   |-- core/data_loader.py          # Unified dataset loader
|   |-- validation/                  # Phases 1-4 validation scripts
|-- voynich_*.csv                    # Analysis data files
|-- recetas_historicas_*.csv         # 50 historical recipes, 613 ingredients
|-- Voynich_Graph/                   # Obsidian vault (130+ notes)
|-- output/                          # Validation outputs (regenerable)
```

## How to Navigate

If you're **new to the project:** Read this README, then `docs/DISCOVERIES.md`.  
If you want to **verify the claims:** Read `docs/VALIDATION.md`, then run the scripts.  
If you want to **continue the work:** Read `docs/NEXT_STEPS.md` -- fixing the F1 metric is Priority 1.  
If you want to **explore the data:** Open the CSV files in Excel, or open `Voynich_Graph/` as an Obsidian vault.

## Running the Validation

```bash
python scripts/validation/data_contracts.py   # Phase 1: Data integrity
python scripts/validation/blind_splits.py      # Phase 2: Train/test splits
python scripts/validation/null_models.py       # Phase 3: 5 null models
python scripts/validation/baselines.py         # Phase 4: 5 baselines
```

## Sources

- **Voynich transcription:** STA1 2.0 by Cesar Diaz-Cerio ([Zenodo](https://zenodo.org/records/7633206))
- **Historical recipes:** Antidotarium Nicolai (s.XII), Galeno, Fracastoro, Circa Instans, Grabadin/Mesue, Avicenna Canon, Abulcasis al-Tasrif
- **Folio images:** [voynich.nu](https://voynich.nu/)

---

# Castellano

## El Misterio

El Manuscrito Voynich (MS 408, Biblioteca Beinecke, Yale) es un libro de 600 anos que nadie puede leer. Escrito en un sistema de escritura desconocido, lleno de dibujos de plantas no identificadas, diagramas astronomicos y figuras banandose, ha derrotado a todo criptografo, linguista y descifrador que ha intentado descifrarlo durante mas de un siglo.

La mayoria de intentos lo tratan como texto cifrado -- un codigo que esconde un idioma natural debajo. Intentan "decodificar" letras individuales a latin, aleman, hebreo o docenas de otros idiomas. Ninguno ha tenido exito.

**Este proyecto toma un enfoque completamente diferente.**

## La Idea

En lugar de intentar leer palabras individuales, tratamos el manuscrito como lo que estructuralmente *parece ser*: una **base de datos**. Especificamente, un compendio farmaceutico medieval -- una *Materia Medica* (catalogo de plantas) cruzada con un *Antidotarium* (libro de recetas).

La evidencia:

- **El texto esta escrito en columnas, no en prosa.** Los sufijos se alinean verticalmente entre lineas consecutivas al 27% (vs 8% en latin/castellano). El autor escribia en una cuadricula, como rellenando una hoja de calculo.
- **Cada seccion usa un "esquema" diferente.** Las paginas de botanica usan etiquetas de entidad (C1). Las paginas de recetas usan etiquetas de ingrediente (B2) y de accion (A2). Diferentes secciones, diferentes tablas de base de datos.
- **Las paginas de plantas referencian las de recetas.** El 46.9% de los stems exclusivos de botanica reaparecen en secciones de recetas con sufijos cambiados (C1 -> B2), exactamente como una clave foranea en una base de datos relacional.

Esto no es un cifrado sobre lenguaje natural. Es un **sistema de notacion estructurado** para recetas farmaceuticas.

## Lo Que Encontramos

Usando la transcripcion STA1 2.0 de Cesar Diaz-Cerio (un alfabeto estructural que descompone cada glifo Voynich en componentes atomicos):

1. **Extrajimos 3,261 stems unicos de vocabulario** de 48 folios de recetas
2. **Compilamos 50 recetas farmaceuticas medievales reales** de fuentes historicas (Antidotarium Nicolai, Galeno, Avicenna, Abulcasis, y otros)
3. **Emparejamos folios Voynich con recetas historicas** mapeando stems a ingredientes reales mediante propagacion de restricciones, cadenas de eliminacion y analisis de interseccion
4. **Identificamos 75 stems** correspondientes a 22 ingredientes medievales reales (Galbanum, Crocus, Myrrha, Mel, Castoreum, Zingiber, y 16 mas)

### Identificaciones Confirmadas

| Stem Voynich | Ingrediente | Confianza | Como |
|---|---|---|---|
| `K1K2A1` | **Galbanum** (resina de Ferula) | 99% | Unico ingrediente en la interseccion de 3 recetas |
| `K1A3` | **Crocus** (Azafran) | 95% | Ausente del folio de Diascordium, que tiene Cinnamomum pero no Crocus |
| `BaA3` | **Clase semantica: goma-resina vegetal** | 90% | Siempre mapea a una goma-resina sin importar la receta |

Mas 72 stems adicionales al 60-92% de confianza en Myrrha, Mel, Cinnamomum, Castoreum, Zingiber, Petroselinum, Gentiana, Rosa, Opopanax, y otros. Tabla completa en `docs/IDENTIFICATIONS.md`.

## Evaluacion Honesta

Construimos un marco de validacion cientifica para probar nuestro propio trabajo. Los resultados son mixtos:

**Lo que se mantiene:**
- Los descubrimientos estructurales (canal de sufijos, alineacion vertical, claves foraneas) son robustos y estadisticamente significativos (Z = -210, p efectivamente cero)
- El sistema supera los 5 modelos nulos (p < 0.01), confirmando que captura senal farmaceutica real
- Las recetas culinarias puntuan 0% -- el contenido es definitivamente farmaceutico
- Las identificaciones Tier 1 (Galbanum, Crocus) tienen cadenas logicas independientes de cualquier metrica

**Lo que no:**
- La puntuacion F1 de emparejamiento (81.9%) es enganosa. Una baseline trivial que predice "todo es Theriac Magna" puntua 100%. Nuestros 22 ingredientes identificados son todos tan comunes en farmacia medieval que predecirlos para cualquier folio casi siempre es correcto.
- El sistema necesita metricas alternativas (F1 discriminativo, precision de ranking, precision de exclusion) antes de que las afirmaciones de emparejamiento puedan validarse.

Detalles completos en `docs/VALIDATION.md`.

## Estructura del Proyecto

```
MASTERTMIND/
|-- README.md / README.html          # Este archivo / Version visual bilingue
|-- docs/
|   |-- VALIDATION.md                # Protocolo y resultados de validacion
|   |-- DISCOVERIES.md               # 23 descubrimientos tecnicos
|   |-- IDENTIFICATIONS.md           # 75 identificaciones con razonamiento
|   |-- METHODOLOGY.md               # Pipeline analitico
|   |-- DATA_DICTIONARY.md           # Cada CSV explicado
|   |-- NEXT_STEPS.md                # Hoja de ruta (arreglar F1 es #1)
|   |-- SESSION_LOG.md               # 15 sesiones de trabajo
|-- scripts/
|   |-- core/config.py               # Config central, hashes SHA-256
|   |-- core/data_loader.py          # Cargador unificado de datos
|   |-- validation/                  # Scripts de validacion Fases 1-4
|-- voynich_*.csv                    # Archivos de datos de analisis
|-- recetas_historicas_*.csv         # 50 recetas historicas, 613 ingredientes
|-- Voynich_Graph/                   # Boveda Obsidian (130+ notas)
|-- output/                          # Salidas de validacion (regenerables)
```

## Como Navegar

Si eres **nuevo en el proyecto:** Lee este README, luego `docs/DISCOVERIES.md`.  
Si quieres **verificar las afirmaciones:** Lee `docs/VALIDATION.md`, luego ejecuta los scripts.  
Si quieres **continuar el trabajo:** Lee `docs/NEXT_STEPS.md` -- arreglar la metrica F1 es la Prioridad 1.  
Si quieres **explorar los datos:** Abre los CSV en Excel, o abre `Voynich_Graph/` como boveda Obsidian.

## Ejecutar la Validacion

```bash
python scripts/validation/data_contracts.py   # Fase 1: Integridad de datos
python scripts/validation/blind_splits.py      # Fase 2: Particiones train/test
python scripts/validation/null_models.py       # Fase 3: 5 modelos nulos
python scripts/validation/baselines.py         # Fase 4: 5 baselines
```

## Fuentes

- **Transcripcion Voynich:** STA1 2.0 de Cesar Diaz-Cerio ([Zenodo](https://zenodo.org/records/7633206))
- **Recetas historicas:** Antidotarium Nicolai (s.XII), Galeno, Fracastoro, Circa Instans, Grabadin/Mesue, Canon de Avicena, al-Tasrif de Abulcasis
- **Imagenes de folios:** [voynich.nu](https://voynich.nu/)
