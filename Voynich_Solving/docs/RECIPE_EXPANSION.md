# Recipe Expansion

This document defines a strict workflow for expanding the historical recipe corpus.

## Principle

Do not add recipes just to increase the count.

Add recipes only when they improve one or more of these:

- blind-test ingredient support
- coverage of underrepresented recipe families
- support for ingredients missing from train but present in test
- discrimination against trivial baselines

## Current Problem

The diagnostics show three major corpus weaknesses:

1. **Ingredient concentration is high.** `Cinnamomum`, `Mel despumatum`, `Zingiber`, and `Crocus` dominate the corpus.
2. **Recipe overlap is high.** Several recipe pairs are near-duplicates, which inflates baseline performance.
3. **Some test recipes are under-supported by train.** The worst current case is `Unguentum Populeon`.

## Files

- `data/recipes/recipe_expansion_candidates_template.csv`
- `data/recipes/recipe_expansion_candidates_seed.csv`
- `scripts/validation/recipe_corpus_diagnostics.py`
- `scripts/validation/recipe_expansion_prioritizer.py`
- `output/validation/recipe_corpus_diagnostics.json`
- `output/validation/recipe_expansion_priorities.json`

## Workflow

1. Run corpus diagnostics.
2. Add or edit candidate rows in `recipe_expansion_candidates_seed.csv`.
3. Run the prioritizer.
4. Search for the top-ranked recipes in reliable editions or studies.
5. Add only recipes with a source and an explicit ingredient list.
6. Re-run:
   - `recipe_corpus_diagnostics.py`
   - `multi_representation_benchmark.py`
7. Keep the new recipes only if they improve the corpus without making it more redundant.

## Admission Rules

Prefer a new recipe when:

- it introduces ingredients currently missing from train but present in blind test recipes
- it belongs to an underrepresented family such as topical sedatives or non-standard antidotes
- it is not just another spice-heavy electuary with the same common core

Reject or deprioritize a new recipe when:

- it is mostly another near-copy of an existing train recipe
- it adds no new ingredients relevant to blind-test support
- it mostly repeats the common ingredient core already saturating the corpus

## First Search Queue

Top priority candidates right now:

1. `Unguentum Populeon` variants or close topical sedative parallels
2. `Diasatyrion` witnesses with `Satyrion`, `Orchis`, `Eruca`, `Pastinaca`, `Triphallus`
3. `Diascordium` witnesses carrying `Scordium`, `Bistorta`, `Dictamnus`, `Styrax`
4. `Mithridatium` witnesses with `Acacia`, `Hypocistis`, `Nardus celtica`, `Thlaspi`
5. `Theriac Magna` witnesses that preserve the missing actives instead of compressing them away

## Success Criterion

Expansion is successful only if, after re-running the benchmark, at least one of these happens:

- blind-test Fixed-F1 improves materially
- Rare-F1 improves materially
- the gap to the best baseline shrinks clearly
- under-supported test recipes gain train support without large redundancy growth
