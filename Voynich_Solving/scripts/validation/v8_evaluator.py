"""
Voynich Validation Framework -- v8 Test Set Evaluation (Fixed)
===============================================================
Evaluates v8 identifications (built on train-only data) on the
9 held-out test folios using Phase 4b discriminative metrics.

CRITICAL FIX: The original evaluator used self-assigned recipe targets
(pick recipe with best F1 against v8's own predictions, then measure rank).
This is tautological: MRR=1.0 by construction (argmax == argmax).

This version uses THREE non-circular evaluation strategies:
  1. v7 independent targets: use v7's recipe assignments as ground truth
     (determined by a different method, different era of the project)
  2. Mean reciprocal F1 across ALL recipes: for each folio, compute F1
     against every recipe and report the distribution -- no target needed
  3. Permutation test: shuffle stem->ingredient assignments N times and
     measure whether the real system outperforms shuffled versions

Run:
    python -m scripts.validation.v8_evaluator
"""
import sys
import os
import csv
import json
import random
from collections import Counter, defaultdict

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.validation.config import PATHS, RANDOM_SEED, ensure_output_dirs
from scripts.validation import data_loader as dl
from scripts.validation.alternative_metrics import (
    compute_fixed_f1, compute_rare_f1, compute_ranking,
    compute_exclusion, compute_rare_precision,
    classify_ingredients, evaluate_method,
)

sys.stdout.reconfigure(encoding='utf-8')

RARE_THRESHOLD = 0.30
N_PERMUTATIONS = 200  # for permutation test


def load_v8_identifications():
    """Load v8 identifications from CSV."""
    path = os.path.join(PATHS['output_validation'], 'voynich_unified_identifications_v8.csv')
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"v8 identifications not found at {path}. "
            "Run v8_builder.py first."
        )
    rows = []
    with open(path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


def build_v8_ident_map(v8_rows):
    """Build {stem: ingredient} from v8 identifications."""
    return {row['Stem']: row['Ingredient'] for row in v8_rows}


def build_v8_ident_ingredients(v8_rows):
    """Get set of all v8-identified ingredients (excluding FUNCTION_WORD)."""
    ings = set()
    for row in v8_rows:
        if row['Ingredient'] != 'FUNCTION_WORD':
            for sub in row['Ingredient'].split('|'):
                ings.add(sub.strip())
    return ings


def make_predictions(folio_stems, ident_map, folios):
    """Generate ingredient predictions for each folio from an ident_map."""
    predictions = {}
    for folio in folios:
        ings = set()
        for stem in folio_stems.get(folio, set()):
            if stem in ident_map and ident_map[stem] != 'FUNCTION_WORD':
                for sub in ident_map[stem].split('|'):
                    ings.add(sub.strip())
        predictions[folio] = ings
    return predictions


# ── Baseline generators ──────────────────────────────────────────────────────
def baseline_most_common(folio_stems, ident_map, recipe_ingredients,
                          ident_ings, folios):
    """Predict the N most common ingredients, where N = # ingredients predicted by system."""
    folio_ing_counts = {}
    for folio in folios:
        ings = set()
        for stem in folio_stems.get(folio, set()):
            if stem in ident_map and ident_map[stem] != 'FUNCTION_WORD':
                for sub in ident_map[stem].split('|'):
                    ings.add(sub.strip())
        folio_ing_counts[folio] = len(ings)

    all_ings = []
    for ings in recipe_ingredients.values():
        all_ings.extend(ings)
    common_ranked = [ing for ing, _ in Counter(all_ings).most_common()]

    return {
        folio: set(common_ranked[:folio_ing_counts.get(folio, 5)])
        for folio in folios
    }


def baseline_all_ingredients(ident_ings, folios):
    """Predict all identified ingredients for every folio."""
    return {folio: set(ident_ings) for folio in folios}


def baseline_majority_recipe(recipe_ingredients, ident_ings, folios):
    """Predict ingredients of the largest recipe (intersected with ident set)."""
    largest = max(recipe_ingredients.keys(), key=lambda r: len(recipe_ingredients[r]))
    pred_ings = recipe_ingredients[largest] & ident_ings
    return {folio: set(pred_ings) for folio in folios}


def baseline_random_shuffle(folio_stems, ident_map, folios, rng):
    """Shuffle ingredient assignments among ingredient-mapped stems."""
    # Get only ingredient stems (not FUNCTION_WORD)
    ing_stems = [s for s, i in ident_map.items() if i != 'FUNCTION_WORD']
    ingredients = [ident_map[s] for s in ing_stems]
    shuffled_ings = list(ingredients)
    rng.shuffle(shuffled_ings)
    shuffled_map = dict(ident_map)  # copy
    for stem, new_ing in zip(ing_stems, shuffled_ings):
        shuffled_map[stem] = new_ing
    return make_predictions(folio_stems, shuffled_map, folios)


# ── Mean F1 across all recipes (no target needed) ───────────────────────────
def compute_mean_f1_all_recipes(predictions, recipe_ingredients, ident_ings, folios):
    """For each folio, compute F1 against EVERY recipe. Return statistics.

    This metric doesn't require a target assignment.
    Higher mean = system predicts ingredients found in many recipes (common).
    Higher max-mean gap = system has specificity (some recipes score much higher).
    """
    results = {}
    for folio in folios:
        pred = predictions.get(folio, set())
        f1_scores = []
        best_recipe = None
        best_f1 = 0
        for rname, rings in recipe_ingredients.items():
            f1, prec, rec = compute_fixed_f1(pred, rings, ident_ings)
            f1_scores.append(f1)
            if f1 > best_f1:
                best_f1 = f1
                best_recipe = rname

        mean_f1 = sum(f1_scores) / len(f1_scores) if f1_scores else 0
        max_f1 = max(f1_scores) if f1_scores else 0
        # Specificity: how much does the best recipe stand out?
        specificity = max_f1 - mean_f1
        results[folio] = {
            'mean_f1': mean_f1,
            'max_f1': max_f1,
            'specificity': specificity,
            'best_recipe': best_recipe,
            'n_predicted': len(pred),
        }
    return results


# ── Permutation test ─────────────────────────────────────────────────────────
def run_permutation_test(folio_stems, ident_map, targets, recipe_ingredients,
                          ident_ings, rare_ings, folios, n_perms=N_PERMUTATIONS):
    """Shuffle stem->ingredient assignments and measure metrics.

    If the real system's score is in the top 5% of shuffled scores,
    the identifications carry genuine signal (p < 0.05).
    """
    rng = random.Random(RANDOM_SEED)
    real_preds = make_predictions(folio_stems, ident_map, folios)
    real_ev = evaluate_method(
        "real", real_preds, targets, recipe_ingredients,
        ident_ings, rare_ings, folios
    )

    perm_f1s = []
    perm_mrrs = []
    perm_excls = []

    for i in range(n_perms):
        shuf_preds = baseline_random_shuffle(folio_stems, ident_map, folios, rng)
        shuf_ev = evaluate_method(
            f"perm_{i}", shuf_preds, targets, recipe_ingredients,
            ident_ings, rare_ings, folios
        )
        perm_f1s.append(shuf_ev['fixed_f1_mean'])
        perm_mrrs.append(shuf_ev['mrr'])
        perm_excls.append(shuf_ev['exclusion_mean'])

    # Compute p-values (fraction of permutations >= real)
    p_f1 = sum(1 for x in perm_f1s if x >= real_ev['fixed_f1_mean']) / n_perms
    p_mrr = sum(1 for x in perm_mrrs if x >= real_ev['mrr']) / n_perms
    p_excl = sum(1 for x in perm_excls if x >= real_ev['exclusion_mean']) / n_perms

    return {
        'real_f1': real_ev['fixed_f1_mean'],
        'real_mrr': real_ev['mrr'],
        'real_excl': real_ev['exclusion_mean'],
        'perm_f1_mean': sum(perm_f1s) / len(perm_f1s),
        'perm_f1_std': (sum((x - sum(perm_f1s)/len(perm_f1s))**2 for x in perm_f1s) / len(perm_f1s)) ** 0.5,
        'perm_mrr_mean': sum(perm_mrrs) / len(perm_mrrs),
        'perm_excl_mean': sum(perm_excls) / len(perm_excls),
        'p_f1': p_f1,
        'p_mrr': p_mrr,
        'p_excl': p_excl,
        'n_permutations': n_perms,
    }


# ── Main evaluation ──────────────────────────────────────────────────────────
def run_v8_evaluation():
    print("=" * 75)
    print("VOYNICH v8 TEST SET EVALUATION (Non-Tautological)")
    print("=" * 75)

    # Load blind splits
    split_path = os.path.join(PATHS['output_splits'], 'blind_splits.json')
    with open(split_path, encoding='utf-8') as f:
        splits = json.load(f)
    train_folios = set(splits['folio_split']['train'])
    test_folios = set(splits['folio_split']['test'])
    train_recipes = set(splits['recipe_split']['train'])
    test_recipes = set(splits['recipe_split']['test'])

    # Load data
    data = dl.load_all()
    all_folio_stems = data['folio_stems']
    all_recipe_ings = data['recipe_ingredients']

    # Load v8 identifications
    v8_rows = load_v8_identifications()
    v8_ident_map = build_v8_ident_map(v8_rows)
    v8_ident_ings = build_v8_ident_ingredients(v8_rows)

    # For comparison, load v7
    v7_ident_map = data['ident_map']
    v7_ident_ings = data['ident_ingredients']

    print(f"\nv8 identifications: {len(v8_ident_map)} stems -> "
          f"{len(v8_ident_ings)} unique ingredients")
    print(f"v7 identifications: {len(v7_ident_map)} stems -> "
          f"{len(v7_ident_ings)} unique ingredients")

    # ══════════════════════════════════════════════════════════════════════
    # STRATEGY 1: Evaluate against v7's INDEPENDENT recipe assignments
    # ══════════════════════════════════════════════════════════════════════
    print(f"\n{'='*75}")
    print("STRATEGY 1: v7 INDEPENDENT TARGETS")
    print("Using v7's recipe assignments as ground truth (non-circular)")
    print(f"{'='*75}")

    v7_targets = {}
    for row in dl.load_matching_v7():
        if row['Folio'] in test_folios and row['Best_Recipe']:
            v7_targets[row['Folio']] = row['Best_Recipe']

    test_folios_with_v7_targets = sorted(v7_targets.keys())
    print(f"\nTest folios with v7 targets: {len(test_folios_with_v7_targets)}/9")
    for folio in test_folios_with_v7_targets:
        print(f"  {folio} -> {v7_targets[folio]}")

    if not test_folios_with_v7_targets:
        print("No test folios have v7 targets. Cannot evaluate Strategy 1.")
    else:
        # Classify ingredients for v8
        rare_ings_v8, common_ings_v8, freq_v8 = classify_ingredients(
            v8_ident_ings, all_recipe_ings)
        # Also classify for v7 (its own ingredient universe)
        rare_ings_v7, common_ings_v7, freq_v7 = classify_ingredients(
            v7_ident_ings, all_recipe_ings)

        print(f"\nv8 ingredient classification: {len(rare_ings_v8)} rare, "
              f"{len(common_ings_v8)} common (of {len(v8_ident_ings)})")
        print(f"v7 ingredient classification: {len(rare_ings_v7)} rare, "
              f"{len(common_ings_v7)} common (of {len(v7_ident_ings)})")

        # Generate predictions
        methods = [
            ("v8_system", make_predictions(all_folio_stems, v8_ident_map,
                                            test_folios_with_v7_targets),
             v8_ident_ings, rare_ings_v8),
            ("v7_system", make_predictions(all_folio_stems, v7_ident_map,
                                            test_folios_with_v7_targets),
             v7_ident_ings, rare_ings_v7),
            ("most_common(v8)", baseline_most_common(
                all_folio_stems, v8_ident_map, all_recipe_ings,
                v8_ident_ings, test_folios_with_v7_targets),
             v8_ident_ings, rare_ings_v8),
            ("all_ings(v8)", baseline_all_ingredients(
                v8_ident_ings, test_folios_with_v7_targets),
             v8_ident_ings, rare_ings_v8),
            ("majority_recipe(v8)", baseline_majority_recipe(
                all_recipe_ings, v8_ident_ings, test_folios_with_v7_targets),
             v8_ident_ings, rare_ings_v8),
        ]

        results_s1 = {}
        for name, preds, ident_ings, rare_ings in methods:
            ev = evaluate_method(
                name, preds, v7_targets, all_recipe_ings,
                ident_ings, rare_ings, test_folios_with_v7_targets
            )
            results_s1[name] = ev

        # Show prediction sizes
        print(f"\nPrediction sizes per folio:")
        for name, preds, _, _ in methods:
            sizes = [len(preds.get(f, set())) for f in test_folios_with_v7_targets]
            print(f"  {name:<22} avg={sum(sizes)/len(sizes):.1f} "
                  f"min={min(sizes)} max={max(sizes)}")

        # Comparison table
        print(f"\n{'='*75}")
        print("STRATEGY 1 METRICS (v7 independent targets on test folios)")
        print(f"{'='*75}")
        header = (f"{'Method':<22} {'Fix-F1':>7} {'Rare-F1':>8} {'MRR':>6} "
                  f"{'P@1':>5} {'P@3':>5} {'Rank':>5} {'Excl':>6} {'R-Prec':>7}")
        print(header)
        print("-" * 75)
        for name, ev in results_s1.items():
            label = f">> {name} <<" if name == 'v8_system' else name
            print(f"{label:<22} {ev['fixed_f1_mean']:>6.1f}% "
                  f"{ev['rare_f1_mean']:>7.1f}% "
                  f"{ev['mrr']:>6.3f} {ev['p_at_1']:>4.0%} {ev['p_at_3']:>4.0%} "
                  f"{ev['mean_rank']:>5.1f} {ev['exclusion_mean']:>5.1f}% "
                  f"{ev['rare_precision_mean']:>6.1f}%")

        # Per-folio detail
        print(f"\nPer-folio detail (v8 vs v7 targets):")
        v8_ev = results_s1['v8_system']
        for detail in v8_ev['details']:
            print(f"  {detail['folio']}: target={detail['target']}, "
                  f"F1={detail['fixed_f1']:.1f}%, rank={detail['rank']}, "
                  f"n_pred={detail['n_predicted']}")

    # ══════════════════════════════════════════════════════════════════════
    # STRATEGY 2: Target-free -- Mean F1 distribution across ALL recipes
    # ══════════════════════════════════════════════════════════════════════
    print(f"\n{'='*75}")
    print("STRATEGY 2: TARGET-FREE SPECIFICITY ANALYSIS")
    print("How specific are v8 predictions? (Higher specificity = better)")
    print(f"{'='*75}")

    all_test_folios_sorted = sorted(test_folios)

    method_specs = [
        ("v8_system", make_predictions(all_folio_stems, v8_ident_map,
                                        all_test_folios_sorted), v8_ident_ings),
        ("v7_system", make_predictions(all_folio_stems, v7_ident_map,
                                        all_test_folios_sorted), v7_ident_ings),
        ("most_common(v8)", baseline_most_common(
            all_folio_stems, v8_ident_map, all_recipe_ings,
            v8_ident_ings, all_test_folios_sorted), v8_ident_ings),
        ("all_ings(v8)", baseline_all_ingredients(
            v8_ident_ings, all_test_folios_sorted), v8_ident_ings),
    ]

    print(f"\n{'Method':<22} {'MeanF1':>7} {'MaxF1':>7} {'Specif':>7} "
          f"{'BestRecipe':<40}")
    print("-" * 85)
    for name, preds, ident_ings in method_specs:
        spec_results = compute_mean_f1_all_recipes(
            preds, all_recipe_ings, ident_ings, all_test_folios_sorted
        )
        mean_f1s = [r['mean_f1'] for r in spec_results.values()]
        max_f1s = [r['max_f1'] for r in spec_results.values()]
        specifics = [r['specificity'] for r in spec_results.values()]

        avg_mean = sum(mean_f1s) / len(mean_f1s) if mean_f1s else 0
        avg_max = sum(max_f1s) / len(max_f1s) if max_f1s else 0
        avg_spec = sum(specifics) / len(specifics) if specifics else 0

        # Most common best recipe
        best_recipes = [r['best_recipe'] for r in spec_results.values()]
        recipe_counts = Counter(best_recipes)
        top_recipe = recipe_counts.most_common(1)[0] if recipe_counts else ("N/A", 0)

        print(f"{name:<22} {avg_mean:>6.1f}% {avg_max:>6.1f}% {avg_spec:>6.1f}pp "
              f"{top_recipe[0]} ({top_recipe[1]}/{len(all_test_folios_sorted)})")

    # Per-folio detail for v8
    print(f"\nPer-folio specificity (v8_system):")
    v8_spec = compute_mean_f1_all_recipes(
        make_predictions(all_folio_stems, v8_ident_map, all_test_folios_sorted),
        all_recipe_ings, v8_ident_ings, all_test_folios_sorted
    )
    for folio in all_test_folios_sorted:
        r = v8_spec[folio]
        print(f"  {folio}: mean_F1={r['mean_f1']:.1f}%, max_F1={r['max_f1']:.1f}%, "
              f"specificity={r['specificity']:.1f}pp, best={r['best_recipe']}, "
              f"n_pred={r['n_predicted']}")

    # ══════════════════════════════════════════════════════════════════════
    # STRATEGY 3: Permutation test -- does stem-ingredient mapping matter?
    # ══════════════════════════════════════════════════════════════════════
    if test_folios_with_v7_targets:
        print(f"\n{'='*75}")
        print(f"STRATEGY 3: PERMUTATION TEST ({N_PERMUTATIONS} shuffles)")
        print("Shuffle stem->ingredient assignments; measure if real > random")
        print(f"{'='*75}")

        perm_results = run_permutation_test(
            all_folio_stems, v8_ident_map, v7_targets,
            all_recipe_ings, v8_ident_ings, rare_ings_v8,
            test_folios_with_v7_targets
        )

        print(f"\n  Real Fixed F1:   {perm_results['real_f1']:.1f}%  "
              f"(permuted mean: {perm_results['perm_f1_mean']:.1f}% "
              f"+/- {perm_results['perm_f1_std']:.1f}%)")
        print(f"  Real MRR:        {perm_results['real_mrr']:.3f}  "
              f"(permuted mean: {perm_results['perm_mrr_mean']:.3f})")
        print(f"  Real Exclusion:  {perm_results['real_excl']:.1f}%  "
              f"(permuted mean: {perm_results['perm_excl_mean']:.1f}%)")
        print(f"\n  p-value (F1):    {perm_results['p_f1']:.3f}  "
              f"{'SIGNIFICANT' if perm_results['p_f1'] < 0.05 else 'NOT significant'}")
        print(f"  p-value (MRR):   {perm_results['p_mrr']:.3f}  "
              f"{'SIGNIFICANT' if perm_results['p_mrr'] < 0.05 else 'NOT significant'}")
        print(f"  p-value (Excl):  {perm_results['p_excl']:.3f}  "
              f"{'SIGNIFICANT' if perm_results['p_excl'] < 0.05 else 'NOT significant'}")

    # ══════════════════════════════════════════════════════════════════════
    # OVERALL OVER-PREDICTION ANALYSIS
    # ══════════════════════════════════════════════════════════════════════
    print(f"\n{'='*75}")
    print("OVER-PREDICTION ANALYSIS")
    print(f"{'='*75}")

    v8_preds = make_predictions(all_folio_stems, v8_ident_map, all_test_folios_sorted)
    v7_preds = make_predictions(all_folio_stems, v7_ident_map, all_test_folios_sorted)

    # Average recipe size
    recipe_sizes = [len(ings) for ings in all_recipe_ings.values()]
    avg_recipe_size = sum(recipe_sizes) / len(recipe_sizes)
    median_recipe_size = sorted(recipe_sizes)[len(recipe_sizes)//2]

    v8_sizes = [len(v8_preds.get(f, set())) for f in all_test_folios_sorted]
    v7_sizes = [len(v7_preds.get(f, set())) for f in all_test_folios_sorted]

    print(f"\n  Average recipe ingredient count: {avg_recipe_size:.1f} "
          f"(median: {median_recipe_size})")
    print(f"  v8 avg predicted ingredients/folio: "
          f"{sum(v8_sizes)/len(v8_sizes):.1f} (of {len(v8_ident_ings)} possible)")
    print(f"  v7 avg predicted ingredients/folio: "
          f"{sum(v7_sizes)/len(v7_sizes):.1f} (of {len(v7_ident_ings)} possible)")
    print(f"\n  v8 prediction coverage: "
          f"{sum(v8_sizes)/len(v8_sizes)/len(v8_ident_ings)*100:.0f}% of its vocabulary")
    print(f"  v7 prediction coverage: "
          f"{sum(v7_sizes)/len(v7_sizes)/len(v7_ident_ings)*100:.0f}% of its vocabulary")

    if sum(v8_sizes)/len(v8_sizes) > avg_recipe_size * 1.5:
        print(f"\n  WARNING: v8 predicts {sum(v8_sizes)/len(v8_sizes):.0f} ingredients "
              f"per folio vs avg recipe size of {avg_recipe_size:.0f}.")
        print(f"  This massive over-prediction inflates recall at the cost of precision.")
        print(f"  The system predicts almost its entire vocabulary for every folio,")
        print(f"  making it unable to discriminate which ingredients are NOT present.")

    # ══════════════════════════════════════════════════════════════════════
    # FINAL VERDICT
    # ══════════════════════════════════════════════════════════════════════
    print(f"\n{'='*75}")
    print("FINAL VERDICT")
    print(f"{'='*75}")

    issues = []
    passes = []

    if test_folios_with_v7_targets:
        v8_ev = results_s1.get('v8_system', {})
        v7_ev = results_s1.get('v7_system', {})

        # Check if v8 beats baselines on Strategy 1
        for bname in ['most_common(v8)', 'all_ings(v8)', 'majority_recipe(v8)']:
            bev = results_s1.get(bname, {})
            if bev and bev.get('fixed_f1_mean', 0) > v8_ev.get('fixed_f1_mean', 0) + 2:
                issues.append(f"v8 BEATEN by {bname} on Fixed-F1 "
                              f"({bev['fixed_f1_mean']:.1f}% vs {v8_ev['fixed_f1_mean']:.1f}%)")

        if v8_ev.get('fixed_f1_mean', 0) > 30:
            passes.append(f"v8 test-set Fixed F1 = {v8_ev['fixed_f1_mean']:.1f}% against v7 targets")

        if v8_ev.get('mrr', 0) > 0.3:
            passes.append(f"v8 test-set MRR = {v8_ev['mrr']:.3f} against v7 targets")

        if v8_ev.get('exclusion_mean', 0) < 50:
            issues.append(f"Poor exclusion accuracy: {v8_ev['exclusion_mean']:.1f}% "
                          f"(system over-predicts)")

        # Check permutation test
        if 'perm_results' in dir():
            pass  # handled below

    if test_folios_with_v7_targets:
        try:
            if perm_results['p_f1'] < 0.05:
                passes.append(f"Permutation test SIGNIFICANT: p={perm_results['p_f1']:.3f}")
            else:
                issues.append(f"Permutation test NOT significant: p={perm_results['p_f1']:.3f} "
                              "(stem->ingredient mapping doesn't outperform random)")
        except NameError:
            pass

    # Over-prediction
    avg_v8_pred = sum(v8_sizes)/len(v8_sizes) if v8_sizes else 0
    if avg_v8_pred > avg_recipe_size * 1.5:
        issues.append(f"Severe over-prediction: {avg_v8_pred:.0f} ings/folio "
                      f"vs {avg_recipe_size:.0f} avg recipe size")

    print("\nPASSES:")
    for p in passes:
        print(f"  + {p}")
    if not passes:
        print("  (none)")

    print("\nISSUES:")
    for i in issues:
        print(f"  - {i}")
    if not issues:
        print("  (none)")

    if len(issues) > len(passes):
        print(f"\nOVERALL: FAIL -- v8 has more issues than passes.")
        print("The identification system needs fundamental improvements.")
    elif issues:
        print(f"\nOVERALL: MIXED -- v8 shows some signal but has significant issues.")
        print("Over-prediction and low exclusion accuracy suggest the stem-to-ingredient")
        print("mapping is too coarse (too many stems per ingredient).")
    else:
        print(f"\nOVERALL: PASS -- v8 survives non-tautological validation.")

    # ── Save results ─────────────────────────────────────────────────────
    ensure_output_dirs()
    save = {
        'strategy_1_v7_targets': {},
        'over_prediction': {
            'v8_avg_predicted': avg_v8_pred,
            'v7_avg_predicted': sum(v7_sizes)/len(v7_sizes) if v7_sizes else 0,
            'avg_recipe_size': avg_recipe_size,
        },
    }
    if test_folios_with_v7_targets:
        for name, ev in results_s1.items():
            save['strategy_1_v7_targets'][name] = {
                k: v for k, v in ev.items() if k != 'details'
            }
        try:
            save['strategy_3_permutation'] = perm_results
        except NameError:
            pass

    out_path = os.path.join(PATHS['output_validation'],
                             'v8_test_evaluation_results.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(save, f, indent=2)
    print(f"\nResults saved to: {out_path}")

    return save


if __name__ == '__main__':
    run_v8_evaluation()
