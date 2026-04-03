# Voynich Solving -- Structural Analysis and Mapping Hypotheses

> **[EN]** A computational research project on whether the Voynich recipe section behaves like a medieval pharmaceutical database.  
> **[ES]** Un proyecto de investigacion computacional sobre si la seccion de recetas del Voynich se comporta como una base de datos farmaceutica medieval.

**Author / Autor:** Ntizar  
**Status / Estado:** Research complete, semantic track unresolved / Investigacion completada, linea semantica sin resolver  
**Sessions / Sesiones:** 17 (April 2026 / Abril 2026)

---

# English

## Current Position

The project now distinguishes between two separate claims:

1. **Structural claim:** the Voynich recipe section shows unusual statistical structure compatible with a pharmaceutical database.
2. **Reading claim:** specific `stem -> ingredient` assignments remain working hypotheses, not demonstrated decipherment.

That distinction matters because the repository's own blind-validation work found that:

- v7 manual identifications are contaminated by test-folio exposure
- v7 ranking metrics (`MRR`, `P@1`) are tautological because targets were chosen by best match
- v8 train-only automation captures some signal but does **not** beat trivial baselines on blind test folios
- multi-representation testing (`STA stems`, `STA tokens`, `EVA tokens`) also fails to beat baselines
- a final augmented-corpus experiment with externally sourced Amsterdam pharmacopoeia witnesses also fails to produce a decisive semantic win

## What Holds Up Best

The strongest result in the repository is the **structural analysis**, not the semantic mapping.

- Structural anomalies vs Latin medical controls: 3 of 4 tests significant
- Cipher hypothesis: not supported by the observed entropy / IC profile
- Cross-validation / permutation analyses: indicate real non-random structure is present

Defensible summary:

> The Voynich recipe section has statistically unusual structure compatible with a pharmaceutical database, but specific stem-to-ingredient readings remain provisional.

## What Does Not Yet Hold Up

The repository does **not** currently justify a claim of decipherment.

- v7 uses all folios in manual reasoning, including test folios
- fixed-target discriminative metrics are informative, but v7 is still exploratory because of contamination
- v8 test-set evaluation underperforms simple baselines
- only 18.7% of recipe-folio words are covered by identified stems
- v8 and v7 agree on only about 12.7% of mappings

## Final Session Outcome

The final session pushed the semantic track as far as the current methodology could reasonably go:

- built a shared benchmark across multiple input representations
- diagnosed corpus overlap and train-support weaknesses
- searched open external sources for additional recipe witnesses
- integrated a conservative augmented corpus in parallel
- re-ran blind benchmarking on the augmented corpus

Result:

- `sta_stem_frozen`: `44.6%` Fixed-F1 vs best baseline `70.5%`
- `sta_token`: `51.7%` Fixed-F1 vs best baseline `67.6%`
- `eva_token`: `60.5%` Fixed-F1 vs best baseline `87.6%`

These experiments moved some numbers but did **not** produce the kind of clear, reproducible blind-test advantage needed to claim semantic decoding.

Final technical position:

> The structural thesis survives. The specific stem-to-ingredient reading thesis remains unproven.

## Repository Split

The project is now organized conceptually as two products:

### `structural_analysis/`

Claims that are comparatively robust and publication-facing:

- suffix/selectivity structure
- vertical alignment / columnar writing
- section-level schema variation
- cipher-vs-notation diagnostics
- comparative corpus tests against controls

Entry point: `structural_analysis/README.md`

### `mapping_hypotheses/`

Exploratory material that should be treated as hypothesis generation:

- v7 manual stem identifications
- v8 automated train-only mapping
- folio-to-recipe matching
- contradiction checks, FDR, round-trip validation, and coverage work still pending or partial

Entry point: `mapping_hypotheses/README.md`

## Key Files

- `docs/README.md` -- honest project overview
- `docs/VALIDATION.md` -- validation framework, limits, and blind-test results
- `docs/IDENTIFICATIONS.md` -- v7 exploratory stem hypotheses
- `docs/NEXT_STEPS.md` -- current roadmap
- `docs/RECIPE_EXPANSION.md` -- disciplined corpus expansion workflow
- `docs/SOURCE_NOTES_AMSTERDAM_1701.md` -- external-source notes for augmented-corpus experiments
- `structural_analysis/README.md` -- robust structural track
- `mapping_hypotheses/README.md` -- exploratory semantic track

## Recommended Reading Order

1. `docs/README.md`
2. `structural_analysis/README.md`
3. `docs/VALIDATION.md`
4. `mapping_hypotheses/README.md`
5. `docs/NEXT_STEPS.md`
6. `docs/RECIPE_EXPANSION.md`

---

# Castellano

## Posicion Actual

El proyecto ahora separa dos afirmaciones distintas:

1. **Afirmacion estructural:** la seccion de recetas del Voynich muestra una estructura estadistica anomala compatible con una base de datos farmaceutica.
2. **Afirmacion de lectura:** las asignaciones concretas `stem -> ingrediente` siguen siendo hipotesis de trabajo, no un desciframiento demostrado.

La distincion importa porque la propia validacion del repositorio encontro que:

- v7 manual esta contaminado por exposicion a folios de test
- las metricas de ranking de v7 (`MRR`, `P@1`) son tautologicas porque los targets se eligieron por best match
- v8, construido solo con train, captura algo de senal pero **no** supera baselines triviales en test ciego

## Lo Mas Solido

El resultado mas fuerte del repositorio es el **analisis estructural**, no el mapeo semantico.

- Anomalias estructurales frente a controles latinos: 3 de 4 tests significativos
- Hipotesis de cifrado: no queda respaldada por el perfil observado de entropia / IC
- Validacion cruzada / permutacion: indican que existe estructura real no aleatoria

Resumen defendible:

> La seccion de recetas del Voynich tiene una estructura estadisticamente anomala compatible con una base de datos farmaceutica, pero las lecturas stem-a-ingrediente siguen siendo provisionales.

## Lo Que Aun No Se Sostiene

El repositorio **no** justifica todavia una afirmacion de desciframiento.

- v7 usa todos los folios en el razonamiento manual, incluidos los de test
- las metricas discriminativas son utiles, pero v7 sigue siendo exploratorio por la contaminacion
- la evaluacion ciega de v8 rinde peor que baselines simples
- solo el 18.7% de las palabras de recetas queda cubierto por stems identificados
- v8 y v7 solo coinciden en torno al 12.7% de los mapeos

## Division del Repositorio

El proyecto queda dividido conceptualmente en dos productos:

### `structural_analysis/`

Afirmaciones mas robustas y orientadas a publicacion:

- estructura de sufijos / selectividad
- alineacion vertical / escritura columnar
- variacion de esquemas por seccion
- diagnosticos cifrado-vs-notacion
- comparativas contra corpus de control

Entrada: `structural_analysis/README.md`

### `mapping_hypotheses/`

Material exploratorio que debe leerse como generacion de hipotesis:

- identificaciones manuales v7
- mapeo automatizado v8 con train-only
- matching folio-receta
- contradicciones, FDR, round-trip y cobertura aun pendientes o parciales

Entrada: `mapping_hypotheses/README.md`

## Archivos Clave

- `docs/README.md` -- resumen honesto del proyecto
- `docs/VALIDATION.md` -- marco de validacion, limites y resultados ciegos
- `docs/IDENTIFICATIONS.md` -- hipotesis exploratorias de stems v7
- `docs/NEXT_STEPS.md` -- hoja de ruta actual
- `structural_analysis/README.md` -- linea estructural robusta
- `mapping_hypotheses/README.md` -- linea semantica exploratoria

## Orden Recomendado de Lectura

1. `docs/README.md`
2. `structural_analysis/README.md`
3. `docs/VALIDATION.md`
4. `mapping_hypotheses/README.md`
5. `docs/NEXT_STEPS.md`
