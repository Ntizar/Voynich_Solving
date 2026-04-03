# Mapping Hypotheses

This track contains the exploratory `stem -> ingredient` work.

## Scope

- v7 manual identifications
- v8 train-only automated builder
- folio-to-recipe matching
- discriminative metrics, null models, baselines, and blind-test evaluation

## Current Status

- v7 remains the richest manual hypothesis set, but it is contaminated by test-folio exposure
- v7 ranking metrics are tautological and should not be treated as independent evidence
- v8 captures some signal but fails against trivial baselines on blind test folios
- coverage is low and agreement between v7 and v8 is weak

## Correct Interpretation

Use this material as hypothesis generation, prioritization, and manual reasoning support.

Do not treat it as demonstrated decipherment.

## Main Sources

- `docs/IDENTIFICATIONS.md`
- `docs/VALIDATION.md`
- `docs/NEXT_STEPS.md`
- `scripts/validation/v8_builder.py`
- `scripts/validation/v8_evaluator.py`
- `output/validation/v8_test_evaluation_results.json`
- `output/validation/voynich_unified_identifications_v8.csv`

## Required Before Stronger Claims

- contradiction engine
- FDR correction
- cross-representation benchmark
- stronger blind-test wins over baselines
- better text coverage
