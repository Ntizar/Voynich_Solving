"""
Voynich Validation Framework -- Baseline Rivals
================================================
The system's F1 must clearly beat these simple baselines to be credible.
If a "dumb" method matches or exceeds the system, the system adds no value.

Run:
    python -m scripts.validation.baselines

Baselines:
    1. RANDOM ASSIGNMENT: Assign the most common N ingredients to every folio
       (where N = number of identified ingredients per folio in v7).
       This is the "always predict the prior" baseline.

    2. FREQUENCY BASELINE: Assign ingredients to stems by global frequency rank.
       Most common stem -> most common ingredient, etc.
       No structural reasoning at all.

    3. INGREDIENT COUNT MATCH: Match folios to recipes solely by matching
       the count of unique stems to the recipe's ingredient count.
       This is the original structural matching before content-based F1.

    4. ALL-INGREDIENTS BASELINE: For each folio, predict that it contains
       ALL identified ingredients. Maximum recall, zero precision filtering.

    5. MAJORITY RECIPE BASELINE: Always predict the recipe with the most
       ingredients (Theriac Magna). Tests if the system just defaults to
       the biggest recipe.

Metrics:
    - Mean F1 (non-zero)
    - Number of EXCELLENT (F1 >= 80%)
    - Top-1 accuracy (does the best match correspond to the same recipe as v7?)
    - Margin: average difference between best and second-best F1
"""
import sys
import os
import json
import random
from collections import Counter

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.core.config import RANDOM_SEED, PATHS, ensure_output_dirs
from scripts.core import data_loader as dl

sys.stdout.reconfigure(encoding='utf-8')


# ── Shared F1 computation ───────────────────────────────────────────────────
def compute_f1_sets(predicted_ings, recipe_ings, ident_ingredients):
    """F1 between predicted ingredient set and recipe ingredient set."""
    if not predicted_ings or not recipe_ings:
        return 0.0
    tp = predicted_ings & recipe_ings
    fp = predicted_ings - recipe_ings
    fn = (recipe_ings & ident_ingredients) - predicted_ings

    precision = len(tp) / (len(tp) + len(fp)) if (len(tp) + len(fp)) > 0 else 0
    recall = len(tp) / (len(tp) + len(fn)) if (len(tp) + len(fn)) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    return f1 * 100


def best_match(folio_ings, recipe_ingredients, ident_ingredients):
    """Find the recipe with highest F1 for a given folio's predicted ingredients."""
    best_f1 = 0
    best_recipe = ''
    second_f1 = 0
    for rname, rings in recipe_ingredients.items():
        f1 = compute_f1_sets(folio_ings, rings, ident_ingredients)
        if f1 > best_f1:
            second_f1 = best_f1
            best_f1 = f1
            best_recipe = rname
        elif f1 > second_f1:
            second_f1 = f1
    margin = best_f1 - second_f1
    return best_recipe, best_f1, margin


def evaluate_baseline(name, folio_predictions, recipe_ingredients, ident_ingredients, folios):
    """Evaluate a baseline's predictions and return summary metrics."""
    results = []
    for folio in folios:
        pred = folio_predictions.get(folio, set())
        recipe, f1, margin = best_match(pred, recipe_ingredients, ident_ingredients)
        results.append({
            'folio': folio,
            'best_recipe': recipe,
            'f1': f1,
            'margin': margin,
            'n_predicted': len(pred),
        })

    f1s = [r['f1'] for r in results if r['f1'] > 0]
    margins = [r['margin'] for r in results if r['f1'] > 0]
    mean_f1 = sum(f1s) / len(f1s) if f1s else 0
    excellent = sum(1 for f in f1s if f >= 80)
    mean_margin = sum(margins) / len(margins) if margins else 0
    nonzero = len(f1s)

    return {
        'name': name,
        'mean_f1': mean_f1,
        'excellent': excellent,
        'nonzero': nonzero,
        'total': len(folios),
        'mean_margin': mean_margin,
        'details': results,
    }


# ── Baseline 1: Most common ingredients ─────────────────────────────────────
def baseline_most_common(data, folios):
    """Predict the N most common ingredients for each folio (N = actual count in v7)."""
    ident_map = data['ident_map']
    folio_stems = data['folio_stems']

    # Count how many distinct ingredients each folio has in v7
    folio_ing_counts = {}
    for folio in folios:
        ings = set()
        for stem in folio_stems.get(folio, set()):
            if stem in ident_map and ident_map[stem] != 'FUNCTION_WORD':
                for sub in ident_map[stem].split('|'):
                    ings.add(sub.strip())
        folio_ing_counts[folio] = len(ings)

    # Get global ingredient frequency across all recipes
    all_ings = []
    for ings in data['recipe_ingredients'].values():
        all_ings.extend(ings)
    ing_freq = Counter(all_ings).most_common()
    common_ranked = [ing for ing, _ in ing_freq]

    predictions = {}
    for folio in folios:
        n = folio_ing_counts.get(folio, 5)
        predictions[folio] = set(common_ranked[:n])

    return predictions


# ── Baseline 2: Frequency rank assignment ────────────────────────────────────
def baseline_frequency_rank(data, folios):
    """Assign ingredients by frequency rank: most common stem -> most common ingredient."""
    ident_map = data['ident_map']
    folio_stems = data['folio_stems']

    # Rank stems by how many folios they appear in
    stem_folio_count = Counter()
    for folio in folios:
        for stem in folio_stems.get(folio, set()):
            stem_folio_count[stem] += 1

    # Only consider non-function-word identified stems
    id_stems = [(s, i) for s, i in ident_map.items() if i != 'FUNCTION_WORD']

    # Rank ingredients by recipe frequency
    all_ings = []
    for ings in data['recipe_ingredients'].values():
        all_ings.extend(ings)
    ing_ranked = [i for i, _ in Counter(all_ings).most_common()]

    # Sort identified stems by folio count (descending)
    id_stems_sorted = sorted(id_stems, key=lambda x: -stem_folio_count.get(x[0], 0))

    # Assign: most common stem -> most common ingredient
    freq_map = {}
    used_ings = set()
    for stem, _ in id_stems_sorted:
        for ing in ing_ranked:
            if ing not in used_ings:
                freq_map[stem] = ing
                used_ings.add(ing)
                break
        else:
            # Ran out of unique ingredients; reuse
            freq_map[stem] = ing_ranked[0] if ing_ranked else 'Unknown'

    predictions = {}
    for folio in folios:
        ings = set()
        for stem in folio_stems.get(folio, set()):
            if stem in freq_map:
                ings.add(freq_map[stem])
        predictions[folio] = ings

    return predictions


# ── Baseline 3: Ingredient count match ───────────────────────────────────────
def baseline_count_match(data, folios):
    """Match folios to recipes by closest ingredient count, then predict those ingredients."""
    folio_stems = data['folio_stems']
    recipe_ings = data['recipe_ingredients']

    # For each folio, count unique stems (proxy for ingredient count)
    predictions = {}
    for folio in folios:
        n_stems = len(folio_stems.get(folio, set()))
        # Find recipe with closest ingredient count
        best_recipe = min(recipe_ings.keys(),
                          key=lambda r: abs(len(recipe_ings[r]) - n_stems))
        # Predict that folio contains the ingredients of that recipe
        # But filter to only ingredients we have identifications for
        predictions[folio] = recipe_ings[best_recipe] & data['ident_ingredients']

    return predictions


# ── Baseline 4: All ingredients ──────────────────────────────────────────────
def baseline_all_ingredients(data, folios):
    """Predict ALL identified ingredients for every folio."""
    all_ings = data['ident_ingredients']
    return {folio: set(all_ings) for folio in folios}


# ── Baseline 5: Majority recipe ─────────────────────────────────────────────
def baseline_majority_recipe(data, folios):
    """Always predict the largest recipe's ingredients."""
    recipe_ings = data['recipe_ingredients']
    largest = max(recipe_ings.keys(), key=lambda r: len(recipe_ings[r]))
    pred_ings = recipe_ings[largest] & data['ident_ingredients']
    return {folio: set(pred_ings) for folio in folios}


# ── Real system predictions ─────────────────────────────────────────────────
def system_v7_predictions(data, folios):
    """Get the actual v7 predictions for comparison."""
    ident_map = data['ident_map']
    folio_stems = data['folio_stems']

    predictions = {}
    for folio in folios:
        ings = set()
        for stem in folio_stems.get(folio, set()):
            if stem in ident_map and ident_map[stem] != 'FUNCTION_WORD':
                for sub in ident_map[stem].split('|'):
                    ings.add(sub.strip())
        predictions[folio] = ings

    return predictions


# ── Main ─────────────────────────────────────────────────────────────────────
def run_baselines():
    print("=" * 70)
    print("VOYNICH VALIDATION FRAMEWORK -- BASELINE RIVALS")
    print("=" * 70)

    data = dl.load_all()
    folios = sorted(data['folio_stems'].keys())
    recipe_ings = data['recipe_ingredients']
    ident_ings = data['ident_ingredients']

    # Real system
    print("\n--- Evaluating v7 system ---")
    v7_preds = system_v7_predictions(data, folios)
    v7_eval = evaluate_baseline("v7_system", v7_preds, recipe_ings, ident_ings, folios)
    print(f"  Mean F1: {v7_eval['mean_f1']:.1f}%, EXCELLENT: {v7_eval['excellent']}, "
          f"Margin: {v7_eval['mean_margin']:.1f}pp")

    # Baselines
    baselines = [
        ("most_common_ings", baseline_most_common(data, folios)),
        ("frequency_rank", baseline_frequency_rank(data, folios)),
        ("count_match", baseline_count_match(data, folios)),
        ("all_ingredients", baseline_all_ingredients(data, folios)),
        ("majority_recipe", baseline_majority_recipe(data, folios)),
    ]

    results = {'v7_system': v7_eval}
    for name, preds in baselines:
        print(f"\n--- Baseline: {name} ---")
        ev = evaluate_baseline(name, preds, recipe_ings, ident_ings, folios)
        print(f"  Mean F1: {ev['mean_f1']:.1f}%, EXCELLENT: {ev['excellent']}, "
              f"Margin: {ev['mean_margin']:.1f}pp, Non-zero: {ev['nonzero']}/{ev['total']}")
        results[name] = ev

    # ── Comparative table ────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print("BASELINE COMPARISON TABLE")
    print(f"{'='*70}")
    print(f"{'Method':<25} {'Mean F1':>8} {'Excellent':>10} {'Margin':>8} {'Non-zero':>9}")
    print("-" * 70)

    # v7 system first
    for name, ev in results.items():
        label = ">>> v7_system <<<" if name == "v7_system" else name
        print(f"{label:<25} {ev['mean_f1']:>7.1f}% {ev['excellent']:>9} "
              f"{ev['mean_margin']:>7.1f}pp {ev['nonzero']:>4}/{ev['total']}")

    # ── Verdict ──────────────────────────────────────────────────────────
    print(f"\n{'='*70}")
    v7_f1 = v7_eval['mean_f1']
    beaten_by = [name for name, ev in results.items()
                 if name != 'v7_system' and ev['mean_f1'] >= v7_f1]
    close = [name for name, ev in results.items()
             if name != 'v7_system' and abs(ev['mean_f1'] - v7_f1) < 5]

    if beaten_by:
        print(f"WARNING: v7 is beaten or matched by: {beaten_by}")
        print("The system's claims should be downgraded.")
    elif close:
        print(f"CAUTION: v7 is within 5pp of: {close}")
        print("The system's advantage over simple baselines is narrow.")
    else:
        print("v7 clearly outperforms all baselines (>5pp margin on all).")

    # ── Delta table ──────────────────────────────────────────────────────
    print(f"\n{'Method':<25} {'Delta vs v7':>12} {'Status':>15}")
    print("-" * 55)
    for name, ev in results.items():
        if name == 'v7_system':
            continue
        delta = v7_f1 - ev['mean_f1']
        status = "CLEAR" if delta > 5 else "CLOSE" if delta > 0 else "BEATEN"
        print(f"{name:<25} {delta:>+11.1f}pp {status:>15}")

    # Save
    ensure_output_dirs()
    # Remove 'details' for JSON (too large)
    save_results = {}
    for name, ev in results.items():
        save_results[name] = {k: v for k, v in ev.items() if k != 'details'}
    out_path = os.path.join(PATHS['output_validation'], 'baselines_results.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(save_results, f, indent=2)
    print(f"\nResults saved to: {out_path}")

    return results


if __name__ == '__main__':
    run_baselines()
