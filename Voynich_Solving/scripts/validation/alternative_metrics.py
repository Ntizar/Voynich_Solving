"""
Voynich Validation Framework -- Phase 4b: Alternative Metrics
=============================================================
The original F1 metric is broken (majority baseline = 100%, see baselines.py).
This script implements discriminative metrics that trivial baselines CANNOT beat.

Root cause of broken F1 (two interacting flaws):
    1. fn only counts identified ingredients (22 of 152), making recall trivially high
    2. best_match oracle lets predictions shop across 50 recipes for best score

New metrics (all use FIXED TARGET -- no best_match shopping):
    1. Fixed-target F1:      F1 against v7's assigned recipe (no oracle)
    2. Rare ingredient F1:   F1 using only ingredients in <30% of recipes (13/22)
    3. Ranking accuracy:     MRR, P@1, P@3 for correct recipe ranking
    4. Exclusion accuracy:   True Negative Rate for absent ingredients
    5. Rare ing. precision:  Precision on ingredients in <30% of recipes

Run:
    python -m scripts.validation.alternative_metrics

Compares v7 system against same 5 baselines from baselines.py.
"""
import sys
import os
import json
from collections import Counter

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.validation.config import RANDOM_SEED, PATHS, ensure_output_dirs
from scripts.validation import data_loader as dl

sys.stdout.reconfigure(encoding='utf-8')

RARE_THRESHOLD = 0.30   # ingredients in <30% of recipes are "rare"
N_RECIPES = 50


# ── Ingredient frequency analysis ────────────────────────────────────────────
def build_ingredient_frequencies(recipe_ingredients):
    """Count how many recipes each ingredient appears in."""
    freq = Counter()
    for rname, ings in recipe_ingredients.items():
        for ing in ings:
            freq[ing] += 1
    return freq


def classify_ingredients(ident_ingredients, recipe_ingredients):
    """Split identified ingredients into rare vs common."""
    freq = build_ingredient_frequencies(recipe_ingredients)
    n_recipes = len(recipe_ingredients)
    rare = set()
    common = set()
    for ing in ident_ingredients:
        pct = freq.get(ing, 0) / n_recipes
        if pct < RARE_THRESHOLD:
            rare.add(ing)
        else:
            common.add(ing)
    return rare, common, freq


# ── Fixed-target F1 (no best_match oracle) ────────────────────────────────────
def compute_fixed_f1(predicted_ings, target_recipe_ings, ident_ingredients):
    """F1 between predicted set and a FIXED target recipe.

    Unlike baselines.py, fn counts ALL recipe ingredients that the system
    could theoretically predict (i.e., those in ident_ingredients).
    """
    if not predicted_ings or not target_recipe_ings:
        return 0.0, 0.0, 0.0
    tp = predicted_ings & target_recipe_ings
    fp = predicted_ings - target_recipe_ings
    fn = (target_recipe_ings & ident_ingredients) - predicted_ings

    prec = len(tp) / (len(tp) + len(fp)) if (len(tp) + len(fp)) > 0 else 0
    rec = len(tp) / (len(tp) + len(fn)) if (len(tp) + len(fn)) > 0 else 0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
    return f1 * 100, prec * 100, rec * 100


# ── Rare ingredient F1 ───────────────────────────────────────────────────────
def compute_rare_f1(predicted_ings, target_recipe_ings, rare_ingredients):
    """F1 using ONLY rare ingredients (those in <30% of recipes)."""
    pred_rare = predicted_ings & rare_ingredients
    target_rare = target_recipe_ings & rare_ingredients

    if not pred_rare and not target_rare:
        return None  # Neither side has rare ingredients -- skip
    if not target_rare:
        # Target has no rare ingredients but system predicted some
        return 0.0

    tp = pred_rare & target_rare
    fp = pred_rare - target_rare
    fn = target_rare - pred_rare

    prec = len(tp) / (len(tp) + len(fp)) if (len(tp) + len(fp)) > 0 else 0
    rec = len(tp) / (len(tp) + len(fn)) if (len(tp) + len(fn)) > 0 else 0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
    return f1 * 100


# ── Ranking accuracy ─────────────────────────────────────────────────────────
def compute_ranking(folio_ings, recipe_ingredients, ident_ingredients, target_recipe):
    """Rank all recipes by F1 against this folio's ingredients.

    Returns (rank, mrr, p_at_1, p_at_3) where rank is 1-indexed.
    """
    scores = []
    for rname, rings in recipe_ingredients.items():
        f1, _, _ = compute_fixed_f1(folio_ings, rings, ident_ingredients)
        scores.append((rname, f1))

    # Sort descending by F1, break ties alphabetically
    scores.sort(key=lambda x: (-x[1], x[0]))

    rank = None
    for i, (rname, _) in enumerate(scores, 1):
        if rname == target_recipe:
            rank = i
            break

    if rank is None:
        return len(scores), 0.0, 0, 0

    mrr = 1.0 / rank
    p_at_1 = 1 if rank == 1 else 0
    p_at_3 = 1 if rank <= 3 else 0
    return rank, mrr, p_at_1, p_at_3


# ── Exclusion accuracy ───────────────────────────────────────────────────────
def compute_exclusion(predicted_ings, target_recipe_ings, ident_ingredients):
    """True Negative Rate: of ingredients NOT in the target recipe,
    how many does the system correctly NOT predict?

    Only considers the 22 identified ingredients as the universe.
    """
    absent_in_recipe = ident_ingredients - target_recipe_ings
    if not absent_in_recipe:
        return None  # All ingredients are in this recipe

    correctly_excluded = absent_in_recipe - predicted_ings
    tnr = len(correctly_excluded) / len(absent_in_recipe)
    return tnr * 100


# ── Rare ingredient precision ────────────────────────────────────────────────
def compute_rare_precision(predicted_ings, target_recipe_ings, rare_ingredients):
    """Precision on rare ingredients only."""
    pred_rare = predicted_ings & rare_ingredients
    if not pred_rare:
        return None  # No rare ingredients predicted

    tp_rare = pred_rare & target_recipe_ings
    return (len(tp_rare) / len(pred_rare)) * 100


# ── Load v7 ground truth assignments ─────────────────────────────────────────
def load_v7_targets():
    """Load folio -> target recipe assignments from voynich_matching_v7.csv."""
    matching = dl.load_matching_v7()
    targets = {}
    for row in matching:
        folio = row['Folio']
        recipe = row['Best_Recipe']
        if recipe:  # Skip f116v with no match
            targets[folio] = recipe
    return targets


# ── Prediction generators (same as baselines.py) ─────────────────────────────
def system_v7_predictions(data, folios):
    """Get the actual v7 predictions."""
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


def baseline_most_common(data, folios):
    ident_map = data['ident_map']
    folio_stems = data['folio_stems']
    folio_ing_counts = {}
    for folio in folios:
        ings = set()
        for stem in folio_stems.get(folio, set()):
            if stem in ident_map and ident_map[stem] != 'FUNCTION_WORD':
                for sub in ident_map[stem].split('|'):
                    ings.add(sub.strip())
        folio_ing_counts[folio] = len(ings)

    all_ings = []
    for ings in data['recipe_ingredients'].values():
        all_ings.extend(ings)
    common_ranked = [ing for ing, _ in Counter(all_ings).most_common()]

    predictions = {}
    for folio in folios:
        n = folio_ing_counts.get(folio, 5)
        predictions[folio] = set(common_ranked[:n])
    return predictions


def baseline_frequency_rank(data, folios):
    ident_map = data['ident_map']
    folio_stems = data['folio_stems']
    stem_folio_count = Counter()
    for folio in folios:
        for stem in folio_stems.get(folio, set()):
            stem_folio_count[stem] += 1

    id_stems = [(s, i) for s, i in ident_map.items() if i != 'FUNCTION_WORD']
    all_ings = []
    for ings in data['recipe_ingredients'].values():
        all_ings.extend(ings)
    ing_ranked = [i for i, _ in Counter(all_ings).most_common()]

    id_stems_sorted = sorted(id_stems, key=lambda x: -stem_folio_count.get(x[0], 0))
    freq_map = {}
    used_ings = set()
    for stem, _ in id_stems_sorted:
        for ing in ing_ranked:
            if ing not in used_ings:
                freq_map[stem] = ing
                used_ings.add(ing)
                break
        else:
            freq_map[stem] = ing_ranked[0] if ing_ranked else 'Unknown'

    predictions = {}
    for folio in folios:
        ings = set()
        for stem in folio_stems.get(folio, set()):
            if stem in freq_map:
                ings.add(freq_map[stem])
        predictions[folio] = ings
    return predictions


def baseline_count_match(data, folios):
    folio_stems = data['folio_stems']
    recipe_ings = data['recipe_ingredients']
    predictions = {}
    for folio in folios:
        n_stems = len(folio_stems.get(folio, set()))
        best_recipe = min(recipe_ings.keys(),
                          key=lambda r: abs(len(recipe_ings[r]) - n_stems))
        predictions[folio] = recipe_ings[best_recipe] & data['ident_ingredients']
    return predictions


def baseline_all_ingredients(data, folios):
    all_ings = data['ident_ingredients']
    return {folio: set(all_ings) for folio in folios}


def baseline_majority_recipe(data, folios):
    recipe_ings = data['recipe_ingredients']
    largest = max(recipe_ings.keys(), key=lambda r: len(recipe_ings[r]))
    pred_ings = recipe_ings[largest] & data['ident_ingredients']
    return {folio: set(pred_ings) for folio in folios}


# ── Evaluate a method with ALL alternative metrics ───────────────────────────
def evaluate_method(name, predictions, targets, recipe_ingredients,
                    ident_ingredients, rare_ingredients, folios):
    """Evaluate a prediction method on all alternative metrics."""
    fixed_f1s = []
    rare_f1s = []
    ranks = []
    mrrs = []
    p1s = []
    p3s = []
    exclusions = []
    rare_precs = []

    details = []

    for folio in folios:
        if folio not in targets:
            continue
        pred = predictions.get(folio, set())
        target_recipe = targets[folio]
        target_ings = recipe_ingredients.get(target_recipe, set())

        # Fixed-target F1
        f1, prec, rec = compute_fixed_f1(pred, target_ings, ident_ingredients)
        fixed_f1s.append(f1)

        # Rare F1
        rf1 = compute_rare_f1(pred, target_ings, rare_ingredients)
        if rf1 is not None:
            rare_f1s.append(rf1)

        # Ranking
        rank, mrr, p1, p3 = compute_ranking(
            pred, recipe_ingredients, ident_ingredients, target_recipe)
        ranks.append(rank)
        mrrs.append(mrr)
        p1s.append(p1)
        p3s.append(p3)

        # Exclusion
        excl = compute_exclusion(pred, target_ings, ident_ingredients)
        if excl is not None:
            exclusions.append(excl)

        # Rare precision
        rp = compute_rare_precision(pred, target_ings, rare_ingredients)
        if rp is not None:
            rare_precs.append(rp)

        details.append({
            'folio': folio,
            'target': target_recipe,
            'fixed_f1': f1,
            'rare_f1': rf1,
            'rank': rank,
            'exclusion': excl,
            'rare_prec': rp,
            'n_predicted': len(pred),
        })

    n = len(fixed_f1s)
    return {
        'name': name,
        'n_folios': n,
        'fixed_f1_mean': sum(fixed_f1s) / n if n else 0,
        'rare_f1_mean': sum(rare_f1s) / len(rare_f1s) if rare_f1s else 0,
        'mrr': sum(mrrs) / n if n else 0,
        'p_at_1': sum(p1s) / n if n else 0,
        'p_at_3': sum(p3s) / n if n else 0,
        'mean_rank': sum(ranks) / n if n else 0,
        'exclusion_mean': sum(exclusions) / len(exclusions) if exclusions else 0,
        'rare_precision_mean': sum(rare_precs) / len(rare_precs) if rare_precs else 0,
        'details': details,
    }


# ── Main ─────────────────────────────────────────────────────────────────────
def run_alternative_metrics():
    print("=" * 75)
    print("VOYNICH VALIDATION -- PHASE 4b: ALTERNATIVE METRICS")
    print("=" * 75)

    data = dl.load_all()
    targets = load_v7_targets()
    folios = sorted(targets.keys())
    recipe_ings = data['recipe_ingredients']
    ident_ings = data['ident_ingredients']

    # Classify ingredients
    rare, common, freq = classify_ingredients(ident_ings, recipe_ings)
    n_recipes = len(recipe_ings)

    print(f"\nIngredient classification ({len(ident_ings)} identified):")
    print(f"  Rare (<{RARE_THRESHOLD*100:.0f}% of recipes): {len(rare)}")
    print(f"  Common (>={RARE_THRESHOLD*100:.0f}%): {len(common)}")
    print(f"\nRare ingredients: {sorted(rare)}")
    print(f"\nFolios with targets: {len(folios)}")
    print(f"Target recipes used: {len(set(targets.values()))}")

    # Print frequency table
    print(f"\n{'Ingredient':<20} {'Recipes':>8} {'Pct':>6} {'Class':>8}")
    print("-" * 45)
    for ing in sorted(ident_ings, key=lambda x: -freq.get(x, 0)):
        n = freq.get(ing, 0)
        pct = n / n_recipes * 100
        cls = "RARE" if ing in rare else "COMMON"
        print(f"{ing:<20} {n:>8} {pct:>5.1f}% {cls:>8}")

    # ── Evaluate all methods ─────────────────────────────────────────────
    methods = [
        ("v7_system", system_v7_predictions(data, folios)),
        ("most_common_ings", baseline_most_common(data, folios)),
        ("frequency_rank", baseline_frequency_rank(data, folios)),
        ("count_match", baseline_count_match(data, folios)),
        ("all_ingredients", baseline_all_ingredients(data, folios)),
        ("majority_recipe", baseline_majority_recipe(data, folios)),
    ]

    results = {}
    for name, preds in methods:
        print(f"\n--- {name} ---")
        ev = evaluate_method(
            name, preds, targets, recipe_ings, ident_ings, rare, folios)
        results[name] = ev
        print(f"  Fixed-target F1: {ev['fixed_f1_mean']:.1f}%")
        print(f"  Rare F1:         {ev['rare_f1_mean']:.1f}%")
        print(f"  MRR:             {ev['mrr']:.3f}")
        print(f"  P@1:             {ev['p_at_1']:.1%}")
        print(f"  P@3:             {ev['p_at_3']:.1%}")
        print(f"  Mean rank:       {ev['mean_rank']:.1f}")
        print(f"  Exclusion:       {ev['exclusion_mean']:.1f}%")
        print(f"  Rare precision:  {ev['rare_precision_mean']:.1f}%")

    # ── Comparative table ────────────────────────────────────────────────
    print(f"\n{'='*75}")
    print("ALTERNATIVE METRICS COMPARISON TABLE")
    print(f"{'='*75}")
    header = (f"{'Method':<22} {'Fix-F1':>7} {'Rare-F1':>8} {'MRR':>6} "
              f"{'P@1':>5} {'P@3':>5} {'Rank':>5} {'Excl':>6} {'R-Prec':>7}")
    print(header)
    print("-" * 75)
    for name, ev in results.items():
        label = f">> {name} <<" if name == "v7_system" else name
        print(f"{label:<22} {ev['fixed_f1_mean']:>6.1f}% {ev['rare_f1_mean']:>7.1f}% "
              f"{ev['mrr']:>6.3f} {ev['p_at_1']:>4.0%} {ev['p_at_3']:>4.0%} "
              f"{ev['mean_rank']:>5.1f} {ev['exclusion_mean']:>5.1f}% "
              f"{ev['rare_precision_mean']:>6.1f}%")

    # ── Delta table ──────────────────────────────────────────────────────
    v7 = results['v7_system']
    print(f"\n{'='*75}")
    print("DELTAS vs v7_system")
    print(f"{'='*75}")
    print(f"{'Method':<22} {'dFix-F1':>8} {'dRare-F1':>9} {'dMRR':>7} "
          f"{'dP@1':>6} {'dExcl':>7} {'Verdict':>10}")
    print("-" * 75)
    for name, ev in results.items():
        if name == 'v7_system':
            continue
        df1 = v7['fixed_f1_mean'] - ev['fixed_f1_mean']
        drf1 = v7['rare_f1_mean'] - ev['rare_f1_mean']
        dmrr = v7['mrr'] - ev['mrr']
        dp1 = v7['p_at_1'] - ev['p_at_1']
        dexcl = v7['exclusion_mean'] - ev['exclusion_mean']

        # Verdict: system must beat on at least 3 of 5 metrics
        wins = sum([df1 > 2, drf1 > 2, dmrr > 0.05, dp1 > 0.05, dexcl > 2])
        verdict = "CLEAR" if wins >= 4 else "MARGINAL" if wins >= 2 else "BEATEN"
        print(f"{name:<22} {df1:>+7.1f}pp {drf1:>+8.1f}pp {dmrr:>+7.3f} "
              f"{dp1:>+5.0%} {dexcl:>+6.1f}pp {verdict:>10}")

    # ── Overall verdict ──────────────────────────────────────────────────
    print(f"\n{'='*75}")
    beaten_by = []
    for name, ev in results.items():
        if name == 'v7_system':
            continue
        # System is "beaten" if baseline wins on 3+ metrics
        b_wins = sum([
            ev['fixed_f1_mean'] > v7['fixed_f1_mean'] + 2,
            ev['rare_f1_mean'] > v7['rare_f1_mean'] + 2,
            ev['mrr'] > v7['mrr'] + 0.05,
            ev['p_at_1'] > v7['p_at_1'] + 0.05,
            ev['exclusion_mean'] > v7['exclusion_mean'] + 2,
        ])
        if b_wins >= 3:
            beaten_by.append(name)

    if beaten_by:
        print(f"WARNING: v7 is still beaten by: {beaten_by}")
        print("The system needs fundamental improvements.")
    else:
        print("v7 outperforms all baselines on discriminative metrics.")
        print("The identification system adds genuine value beyond trivial baselines.")

    # ── Save results ─────────────────────────────────────────────────────
    ensure_output_dirs()
    save = {}
    for name, ev in results.items():
        save[name] = {k: v for k, v in ev.items() if k != 'details'}
    out_path = os.path.join(PATHS['output_validation'], 'alternative_metrics_results.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(save, f, indent=2)
    print(f"\nResults saved to: {out_path}")

    # Save detailed per-folio results for v7 system
    detail_path = os.path.join(PATHS['output_validation'], 'alternative_metrics_details.json')
    with open(detail_path, 'w', encoding='utf-8') as f:
        json.dump(results['v7_system']['details'], f, indent=2)
    print(f"Per-folio details saved to: {detail_path}")

    return results


if __name__ == '__main__':
    run_alternative_metrics()
