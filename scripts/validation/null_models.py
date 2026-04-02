"""
Voynich Validation Framework -- Null Models & Negative Controls
===============================================================
Tests whether the system's F1 scores are meaningful by comparing against
null hypotheses that preserve various structural properties of the data.

If the system finds "excellent matches" in null data, it's overfitting.

Run:
    python -m scripts.validation.null_models

Null models:
    1. PERMUTED STEMS: Shuffle stem-to-ingredient assignments randomly.
       Preserves: number of identified stems, ingredient frequencies.
       Destroys: actual stem-ingredient mapping.

    2. PERMUTED FOLIOS: Shuffle which stems belong to which folio.
       Preserves: global stem frequencies, folio sizes.
       Destroys: folio-specific stem composition.

    3. RANDOM RECIPES: Replace historical recipes with random ingredient sets
       of the same size drawn from the ingredient pool.
       Preserves: recipe sizes, ingredient pool.
       Destroys: actual recipe compositions.

    4. SHUFFLED INGREDIENTS: For each recipe, keep the size but randomly
       reassign which ingredients it contains.
       Preserves: recipe sizes, ingredient pool size.
       Destroys: historical recipe authenticity.

    5. WRONG-GENRE RECIPES: Replace medieval pharmaceutical recipes with
       ingredient lists from a different domain (cooking, veterinary).
       Tests whether the match is specific to pharmaceutical knowledge.

Each null is run N_ITERATIONS times and the distribution of F1 scores
is compared against the real system's F1.
"""
import sys
import os
import random
import json
from collections import defaultdict

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.core.config import RANDOM_SEED, PATHS, THRESHOLDS, ensure_output_dirs
from scripts.core import data_loader as dl

sys.stdout.reconfigure(encoding='utf-8')

N_ITERATIONS = 500


# ── Core matching function (mirrors temp_session14_v7.py logic) ──────────────
def compute_f1(folio_stems_map, ident_map, ident_ingredients, folio, recipe_ings):
    """Compute F1 between a folio's identified ingredients and a recipe's ingredients."""
    folio_identified = set()
    for stem in folio_stems_map.get(folio, set()):
        if stem in ident_map:
            ing = ident_map[stem]
            if ing != 'FUNCTION_WORD':
                for sub in ing.split('|'):
                    folio_identified.add(sub.strip())

    if not folio_identified or not recipe_ings:
        return 0.0

    tp = folio_identified & recipe_ings
    fp = folio_identified - recipe_ings
    fn = (recipe_ings & ident_ingredients) - folio_identified

    precision = len(tp) / (len(tp) + len(fp)) if (len(tp) + len(fp)) > 0 else 0
    recall = len(tp) / (len(tp) + len(fn)) if (len(tp) + len(fn)) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    return f1 * 100


def compute_system_f1_distribution(folio_stems_map, ident_map, ident_ingredients,
                                   recipe_ingredients, folios):
    """Compute best-match F1 for each folio. Returns list of (folio, best_recipe, best_f1)."""
    results = []
    for folio in folios:
        best_f1 = 0
        best_recipe = ''
        for rname, rings in recipe_ingredients.items():
            f1 = compute_f1(folio_stems_map, ident_map, ident_ingredients, folio, rings)
            if f1 > best_f1:
                best_f1 = f1
                best_recipe = rname
        results.append((folio, best_recipe, best_f1))
    return results


# ── Null Model 1: Permuted stem-ingredient assignments ───────────────────────
def null_permuted_stems(data, rng):
    """Shuffle which ingredient each identified stem maps to."""
    ident_map = dict(data['ident_map'])
    # Collect non-function-word mappings
    non_fw = {s: i for s, i in ident_map.items() if i != 'FUNCTION_WORD'}
    stems = list(non_fw.keys())
    ingredients = list(non_fw.values())
    rng.shuffle(ingredients)
    null_map = dict(ident_map)  # keep function words
    for s, i in zip(stems, ingredients):
        null_map[s] = i
    return null_map


# ── Null Model 2: Permuted folio compositions ────────────────────────────────
def null_permuted_folios(data, rng):
    """Shuffle stems across folios while preserving folio sizes."""
    folio_stems = data['folio_stems']
    all_folios = sorted(folio_stems.keys())

    # Collect all (folio, stem) assignments
    all_stems_flat = []
    folio_sizes = {}
    for f in all_folios:
        stems = list(folio_stems[f])
        folio_sizes[f] = len(stems)
        all_stems_flat.extend(stems)

    rng.shuffle(all_stems_flat)

    # Reassign preserving sizes
    null_folio_stems = {}
    idx = 0
    for f in all_folios:
        size = folio_sizes[f]
        null_folio_stems[f] = set(all_stems_flat[idx:idx + size])
        idx += size

    return null_folio_stems


# ── Null Model 3: Random recipe compositions ─────────────────────────────────
def null_random_recipes(data, rng):
    """Replace each recipe's ingredients with random ones of the same size."""
    recipe_ings = data['recipe_ingredients']
    all_ings = list(data['ident_ingredients'])

    null_recipes = {}
    for rname, ings in recipe_ings.items():
        size = len(ings)
        if size <= len(all_ings):
            null_recipes[rname] = set(rng.sample(all_ings, size))
        else:
            null_recipes[rname] = set(rng.choices(all_ings, k=size))

    return null_recipes


# ── Null Model 4: Shuffled ingredients within recipes ────────────────────────
def null_shuffled_ingredients(data, rng):
    """Pool all ingredients across recipes, then redistribute preserving sizes."""
    recipe_ings = data['recipe_ingredients']
    # Pool all unique ingredients from all recipes
    all_pool = set()
    for ings in recipe_ings.values():
        all_pool.update(ings)
    all_pool = list(all_pool)

    null_recipes = {}
    for rname, ings in recipe_ings.items():
        size = len(ings)
        null_recipes[rname] = set(rng.sample(all_pool, min(size, len(all_pool))))

    return null_recipes


# ── Null Model 5: Wrong-genre ingredient lists ───────────────────────────────
def null_wrong_genre(data, rng):
    """Replace pharmaceutical ingredients with culinary/random names.

    This tests whether the match depends on actual pharmaceutical knowledge
    or just structural properties (sizes, overlaps).
    """
    # Fake culinary ingredients
    culinary = [
        'Sal', 'Piper', 'Allium', 'Cepa', 'Petroselinum_culinare',
        'Lac', 'Butyrum', 'Caseus', 'Ova', 'Farina',
        'Acetum', 'Oleum_olivae', 'Vinum_album', 'Aqua', 'Succus_citri',
        'Amygdalae', 'Nux', 'Prunus', 'Malum', 'Pyrus',
        'Caro_bovina', 'Caro_porcina', 'Piscis', 'Pullus', 'Agnus',
        'Raphanus', 'Brassica', 'Lactuca', 'Beta', 'Spinacia',
        'Cuminum_culinare', 'Coriandrum_culinare', 'Anethum', 'Mentha_culinare',
        'Thymus', 'Origanum', 'Satureja', 'Hyssopus_culinare', 'Salvia_culinare',
        'Rosmarinus', 'Laurus', 'Sinapis', 'Armoracia', 'Nasturtium',
    ]

    recipe_ings = data['recipe_ingredients']
    null_recipes = {}
    for rname, ings in recipe_ings.items():
        size = len(ings)
        null_recipes[rname] = set(rng.sample(culinary, min(size, len(culinary))))

    return null_recipes


# ── Run all null models ──────────────────────────────────────────────────────
def run_null_models():
    print("=" * 70)
    print("VOYNICH VALIDATION FRAMEWORK -- NULL MODELS & NEGATIVE CONTROLS")
    print("=" * 70)

    data = dl.load_all()
    folios = sorted(data['folio_stems'].keys())

    # Real system scores
    print("\n--- Real system (v7) ---")
    real_results = compute_system_f1_distribution(
        data['folio_stems'], data['ident_map'],
        data['ident_ingredients'], data['recipe_ingredients'], folios
    )
    real_f1s = [r[2] for r in real_results if r[2] > 0]
    real_mean = sum(real_f1s) / len(real_f1s) if real_f1s else 0
    real_excellent = sum(1 for f in real_f1s if f >= 80)
    print(f"  Mean F1 (non-zero): {real_mean:.1f}%")
    print(f"  EXCELLENT (>=80%): {real_excellent} folios")
    print(f"  Non-zero folios: {len(real_f1s)}/{len(folios)}")

    null_results = {}

    # ── Null 1: Permuted stems ───────────────────────────────────────────
    print(f"\n--- Null 1: Permuted stem-ingredient assignments ({N_ITERATIONS} iterations) ---")
    null1_means = []
    null1_excellents = []
    for i in range(N_ITERATIONS):
        rng = random.Random(RANDOM_SEED + i)
        null_map = null_permuted_stems(data, rng)
        null_ings = set()
        for v in null_map.values():
            if v != 'FUNCTION_WORD':
                for sub in v.split('|'):
                    null_ings.add(sub.strip())
        results = compute_system_f1_distribution(
            data['folio_stems'], null_map, null_ings,
            data['recipe_ingredients'], folios
        )
        f1s = [r[2] for r in results if r[2] > 0]
        null1_means.append(sum(f1s) / len(f1s) if f1s else 0)
        null1_excellents.append(sum(1 for f in f1s if f >= 80))

    null1_mean_avg = sum(null1_means) / len(null1_means)
    null1_exc_avg = sum(null1_excellents) / len(null1_excellents)
    null1_mean_max = max(null1_means)
    print(f"  Null mean F1: {null1_mean_avg:.1f}% (max: {null1_mean_max:.1f}%)")
    print(f"  Null EXCELLENT avg: {null1_exc_avg:.1f}")
    print(f"  Real vs Null: {real_mean:.1f}% vs {null1_mean_avg:.1f}% "
          f"(delta: +{real_mean - null1_mean_avg:.1f}pp)")
    exceeds = sum(1 for m in null1_means if m >= real_mean)
    pval = exceeds / N_ITERATIONS
    print(f"  p-value (null >= real): {pval:.4f} ({exceeds}/{N_ITERATIONS})")
    null_results['permuted_stems'] = {
        'null_mean': null1_mean_avg, 'null_max': null1_mean_max,
        'real_mean': real_mean, 'p_value': pval, 'delta_pp': real_mean - null1_mean_avg
    }

    # ── Null 2: Permuted folios ──────────────────────────────────────────
    print(f"\n--- Null 2: Permuted folio compositions ({N_ITERATIONS} iterations) ---")
    null2_means = []
    null2_excellents = []
    for i in range(N_ITERATIONS):
        rng = random.Random(RANDOM_SEED + i + 10000)
        null_fs = null_permuted_folios(data, rng)
        results = compute_system_f1_distribution(
            null_fs, data['ident_map'], data['ident_ingredients'],
            data['recipe_ingredients'], folios
        )
        f1s = [r[2] for r in results if r[2] > 0]
        null2_means.append(sum(f1s) / len(f1s) if f1s else 0)
        null2_excellents.append(sum(1 for f in f1s if f >= 80))

    null2_mean_avg = sum(null2_means) / len(null2_means)
    null2_exc_avg = sum(null2_excellents) / len(null2_excellents)
    null2_mean_max = max(null2_means)
    print(f"  Null mean F1: {null2_mean_avg:.1f}% (max: {null2_mean_max:.1f}%)")
    print(f"  Null EXCELLENT avg: {null2_exc_avg:.1f}")
    print(f"  Real vs Null: {real_mean:.1f}% vs {null2_mean_avg:.1f}% "
          f"(delta: +{real_mean - null2_mean_avg:.1f}pp)")
    exceeds2 = sum(1 for m in null2_means if m >= real_mean)
    pval2 = exceeds2 / N_ITERATIONS
    print(f"  p-value (null >= real): {pval2:.4f} ({exceeds2}/{N_ITERATIONS})")
    null_results['permuted_folios'] = {
        'null_mean': null2_mean_avg, 'null_max': null2_mean_max,
        'real_mean': real_mean, 'p_value': pval2, 'delta_pp': real_mean - null2_mean_avg
    }

    # ── Null 3: Random recipes ───────────────────────────────────────────
    print(f"\n--- Null 3: Random recipe compositions ({N_ITERATIONS} iterations) ---")
    null3_means = []
    null3_excellents = []
    for i in range(N_ITERATIONS):
        rng = random.Random(RANDOM_SEED + i + 20000)
        null_rec = null_random_recipes(data, rng)
        results = compute_system_f1_distribution(
            data['folio_stems'], data['ident_map'], data['ident_ingredients'],
            null_rec, folios
        )
        f1s = [r[2] for r in results if r[2] > 0]
        null3_means.append(sum(f1s) / len(f1s) if f1s else 0)
        null3_excellents.append(sum(1 for f in f1s if f >= 80))

    null3_mean_avg = sum(null3_means) / len(null3_means)
    null3_exc_avg = sum(null3_excellents) / len(null3_excellents)
    null3_mean_max = max(null3_means)
    print(f"  Null mean F1: {null3_mean_avg:.1f}% (max: {null3_mean_max:.1f}%)")
    print(f"  Null EXCELLENT avg: {null3_exc_avg:.1f}")
    print(f"  Real vs Null: {real_mean:.1f}% vs {null3_mean_avg:.1f}% "
          f"(delta: +{real_mean - null3_mean_avg:.1f}pp)")
    exceeds3 = sum(1 for m in null3_means if m >= real_mean)
    pval3 = exceeds3 / N_ITERATIONS
    print(f"  p-value (null >= real): {pval3:.4f} ({exceeds3}/{N_ITERATIONS})")
    null_results['random_recipes'] = {
        'null_mean': null3_mean_avg, 'null_max': null3_mean_max,
        'real_mean': real_mean, 'p_value': pval3, 'delta_pp': real_mean - null3_mean_avg
    }

    # ── Null 4: Shuffled ingredients ─────────────────────────────────────
    print(f"\n--- Null 4: Shuffled ingredients within recipes ({N_ITERATIONS} iterations) ---")
    null4_means = []
    null4_excellents = []
    for i in range(N_ITERATIONS):
        rng = random.Random(RANDOM_SEED + i + 30000)
        null_rec = null_shuffled_ingredients(data, rng)
        results = compute_system_f1_distribution(
            data['folio_stems'], data['ident_map'], data['ident_ingredients'],
            null_rec, folios
        )
        f1s = [r[2] for r in results if r[2] > 0]
        null4_means.append(sum(f1s) / len(f1s) if f1s else 0)
        null4_excellents.append(sum(1 for f in f1s if f >= 80))

    null4_mean_avg = sum(null4_means) / len(null4_means)
    null4_exc_avg = sum(null4_excellents) / len(null4_excellents)
    null4_mean_max = max(null4_means)
    print(f"  Null mean F1: {null4_mean_avg:.1f}% (max: {null4_mean_max:.1f}%)")
    print(f"  Null EXCELLENT avg: {null4_exc_avg:.1f}")
    print(f"  Real vs Null: {real_mean:.1f}% vs {null4_mean_avg:.1f}% "
          f"(delta: +{real_mean - null4_mean_avg:.1f}pp)")
    exceeds4 = sum(1 for m in null4_means if m >= real_mean)
    pval4 = exceeds4 / N_ITERATIONS
    print(f"  p-value (null >= real): {pval4:.4f} ({exceeds4}/{N_ITERATIONS})")
    null_results['shuffled_ingredients'] = {
        'null_mean': null4_mean_avg, 'null_max': null4_mean_max,
        'real_mean': real_mean, 'p_value': pval4, 'delta_pp': real_mean - null4_mean_avg
    }

    # ── Null 5: Wrong-genre ──────────────────────────────────────────────
    print(f"\n--- Null 5: Wrong-genre (culinary) recipe ingredients ---")
    rng5 = random.Random(RANDOM_SEED + 50000)
    null_rec5 = null_wrong_genre(data, rng5)
    results5 = compute_system_f1_distribution(
        data['folio_stems'], data['ident_map'], data['ident_ingredients'],
        null_rec5, folios
    )
    f1s_5 = [r[2] for r in results5 if r[2] > 0]
    null5_mean = sum(f1s_5) / len(f1s_5) if f1s_5 else 0
    null5_excellent = sum(1 for f in f1s_5 if f >= 80)
    print(f"  Wrong-genre mean F1: {null5_mean:.1f}%")
    print(f"  Wrong-genre EXCELLENT: {null5_excellent}")
    print(f"  Non-zero: {len(f1s_5)}/{len(folios)}")
    print(f"  Real vs Wrong-genre: {real_mean:.1f}% vs {null5_mean:.1f}%")
    null_results['wrong_genre'] = {
        'null_mean': null5_mean, 'real_mean': real_mean,
        'delta_pp': real_mean - null5_mean
    }

    # ── Summary ──────────────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print("NULL MODEL SUMMARY")
    print(f"{'='*70}")
    print(f"{'Model':<30} {'Null Mean':>10} {'Real Mean':>10} {'Delta':>8} {'p-value':>10}")
    print("-" * 70)
    for name, r in null_results.items():
        pv = r.get('p_value', '-')
        pv_str = f"{pv:.4f}" if isinstance(pv, float) else pv
        print(f"{name:<30} {r['null_mean']:>9.1f}% {r['real_mean']:>9.1f}% "
              f"{r['delta_pp']:>+7.1f}pp {pv_str:>10}")

    # Verdict
    all_significant = all(
        r.get('p_value', 1.0) < 0.01
        for r in null_results.values()
        if 'p_value' in r
    )
    if all_significant:
        print("\nVERDICT: System significantly outperforms ALL null models (p < 0.01)")
    else:
        weak = [n for n, r in null_results.items()
                if r.get('p_value', 0) >= 0.01]
        print(f"\nVERDICT: System does NOT clearly beat: {weak}")

    # Save results
    ensure_output_dirs()
    out_path = os.path.join(PATHS['output_validation'], 'null_models_results.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(null_results, f, indent=2)
    print(f"\nResults saved to: {out_path}")

    return null_results


if __name__ == '__main__':
    run_null_models()
