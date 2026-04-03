# Amsterdam 1701 Source Notes

This note records the limited recipe additions extracted from open Amsterdam pharmacopoeia witnesses.

## Scope

These additions are intentionally conservative.

Included now:

- `Mithridatium Damocratis (Amsterdam 1701)`
- `Philonium Mesuae (Amsterdam 1701)`
- `Populeum (Amsterdam 1701)`
- `Theriaca Andromachii (Amsterdam 1698 OCR subset)`

## Sources

- Internet Archive OCR/PDF:
  - `https://archive.org/details/b33009673`
  - `https://archive.org/download/b33009673/b33009673_djvu.txt`
  - `https://archive.org/details/ned-kbn-all-00004629-001`
  - `https://archive.org/download/ned-kbn-all-00004629-001/ned-kbn-all-00004629-001_djvu.txt`

## Confidence Policy

- `Mithridatium Damocratis`: usable working extraction
- `Philonium Mesuae`: usable working extraction
- `Populeum`: usable working extraction
- `Theriaca Andromachii`: subset only; OCR too noisy for full safe transcription

## Why Parallel Corpus

These rows are not merged into the frozen main recipe tables yet.

They live in `data/recipes/augmented/` so they can be tested without rewriting the validated baseline corpus.

## Intended Use

Use these rows only in augmented-corpus experiments. If they materially improve blind-test support or benchmark results, they can later be promoted into the main corpus after manual verification against page images.
