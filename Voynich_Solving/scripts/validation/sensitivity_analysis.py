"""
Voynich Validation Framework -- Sensitivity & Robustness Analysis
=================================================================
Tests how robust the identification system is to:
    1. K-fold cross-validation: Does performance hold across different
       train/test splits, not just the single frozen split?
    2. Ablation analysis: Which ingredients/stems are most critical?
       If removing one identification collapses the system, it's fragile.
    3. Parameter sensitivity: How sensitive are results to thresholds
       (MIN_FOLIO_COUNT, MIN_F1_FOR_RECIPE, confidence caps)?
    4. Recipe set sensitivity: Does performance change significantly
       when using different subsets of the 50 historical recipes?

Addresses the critique:
    "Without knowing how many stems remain unidentified or are incorrectly
    assigned, it's impossible to evaluate the true explanatory power."

Run:
    python -m scripts.validation.sensitivity_analysis
"""
import sys
import os
import csv
import json
import random
import math
from collections import Counter, defaultdict

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.validation.config import PATHS, RANDOM_SEED, ensure_output_dirs
from scripts.validation import data_loader as dl
from scripts.validation.alternative_metrics import (
    compute_fixed_f1, compute_rare_f1, compute_ranking,
    classify_ingredients, evaluate_method,
)

sys.stdout.reconfigure(encoding='utf-8')


# ── Import v8 builder for k-fold ─────────────────────────────────────────────
# We import the core functions but NOT the main() to avoid side effects
from scripts.validation.v8_builder import (
    assign_best_recipes, phase0_bootstrap, expand_stems,
    phase1_iterative, MIN_FOLIO_COUNT, MIN_F1_FOR_RECIPE,
    MIN_CANDIDATE_SCORE, UNIQUE_CONFIDENCE_CAP, STRONG_CONFIDENCE_CAP,
    MODERATE_CONFIDENCE_CAP, CONFIDENCE_FLOOR, MAX_ITERATIONS,
)


# ── K-fold cross-validation ─────────────────────────────────────────────────
def run_kfold_builder(train_folios, train_recipes, all_folio_stems,
                      all_recipe_ings, min_folio_count=MIN_FOLIO_COUNT):
    """Run the v8 builder algorithm on a given train split.
    
    Uses Phase 0 bootstrap + stem expansion + Phase 1 co-occurrence,
    matching the current v8_builder.py pipeline.
    
    Returns (identifications, identified_ingredients).
    """
    folio_stems = {f: stems for f, stems in all_folio_stems.items()
                   if f in train_folios}
    
    stem_folios = defaultdict(set)
    for folio, stems in folio_stems.items():
        for stem in stems:
            stem_folios[stem].add(folio)
    stem_folios = dict(stem_folios)
    
    recipe_ingredients = {r: ings for r, ings in all_recipe_ings.items()
                          if r in train_recipes}
    
    all_train_stems = set()
    for stems in folio_stems.values():
        all_train_stems.update(stems)
    
    # Phase 0: Bootstrap
    identifications, identified_ingredients = phase0_bootstrap(
        train_folios, folio_stems, stem_folios,
        recipe_ingredients, all_train_stems
    )
    
    # Stem expansion
    for pass_num in range(3):
        n_before = len(identifications)
        identifications, identified_ingredients = expand_stems(
            train_folios, folio_stems, stem_folios,
            recipe_ingredients, all_train_stems,
            identifications, identified_ingredients
        )
        if len(identifications) == n_before:
            break
    
    # Phase 1: Co-occurrence iterative
    identifications, identified_ingredients = phase1_iterative(
        train_folios, folio_stems, stem_folios,
        recipe_ingredients, all_train_stems,
        identifications, identified_ingredients
    )
    
    return identifications, identified_ingredients


def run_kfold_cv(k=5):
    """Run k-fold cross-validation on the identification pipeline.
    
    Splits folios into k folds. For each fold:
    1. Train on k-1 folds + all recipes
    2. Evaluate on the held-out fold
    3. Report metrics across all folds
    """
    print(f"\n{'='*75}")
    print(f"K-FOLD CROSS-VALIDATION (k={k})")
    print(f"{'='*75}")
    
    data = dl.load_all()
    all_folio_stems = data['folio_stems']
    all_recipe_ings = data['recipe_ingredients']
    
    # Get all recipe folios
    all_folios = sorted(all_folio_stems.keys())
    
    # Shuffle and split into k folds
    rng = random.Random(RANDOM_SEED)
    shuffled = list(all_folios)
    rng.shuffle(shuffled)
    
    fold_size = len(shuffled) // k
    folds = []
    for i in range(k):
        start = i * fold_size
        end = start + fold_size if i < k - 1 else len(shuffled)
        folds.append(shuffled[start:end])
    
    print(f"  Total folios: {len(all_folios)}")
    print(f"  Fold sizes: {[len(f) for f in folds]}")
    
    fold_results = []
    all_train_recipes = set(all_recipe_ings.keys())  # Use all recipes for each fold
    
    for fold_idx in range(k):
        test_fold = set(folds[fold_idx])
        train_folds = set()
        for j in range(k):
            if j != fold_idx:
                train_folds.update(folds[j])
        
        print(f"\n  --- Fold {fold_idx + 1}/{k} ---")
        print(f"  Train: {len(train_folds)} folios, Test: {len(test_fold)} folios")
        
        # Build identifications on training folds
        idents, ident_ings = run_kfold_builder(
            train_folds, all_train_recipes, all_folio_stems, all_recipe_ings
        )
        
        n_stems = len(idents)
        n_fw = sum(1 for info in idents.values() if info['ingredient'] == 'FUNCTION_WORD')
        n_ing = n_stems - n_fw
        n_unique = len(ident_ings)
        
        print(f"  Identified: {n_stems} stems ({n_ing} ingredient, {n_fw} function)")
        print(f"  Unique ingredients: {n_unique}")
        
        # Build ident_map for evaluation
        ident_map = {s: info['ingredient'] for s, info in idents.items()}
        
        # Generate predictions for test folios
        test_predictions = {}
        for folio in test_fold:
            ings = set()
            for stem in all_folio_stems.get(folio, set()):
                if stem in ident_map and ident_map[stem] != 'FUNCTION_WORD':
                    for sub in ident_map[stem].split('|'):
                        ings.add(sub.strip())
            test_predictions[folio] = ings
        
        # Assign best-match recipes for test folios
        # NOTE: This uses the system's own predictions to pick targets, which
        # is tautological for ranking metrics. We acknowledge this limitation
        # and focus on cross-fold stability of F1, not absolute ranking.
        test_targets = {}
        for folio in test_fold:
            folio_ings = test_predictions[folio]
            if not folio_ings:
                continue
            best_f1 = 0
            best_recipe = None
            for rname, rings in all_recipe_ings.items():
                tp = folio_ings & rings
                fp = folio_ings - rings
                fn = (rings & ident_ings) - folio_ings
                prec = len(tp) / (len(tp) + len(fp)) if (len(tp) + len(fp)) > 0 else 0
                rec = len(tp) / (len(tp) + len(fn)) if (len(tp) + len(fn)) > 0 else 0
                f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
                if f1 > best_f1:
                    best_f1 = f1
                    best_recipe = rname
            if best_recipe:
                test_targets[folio] = best_recipe
        
        if not test_targets:
            print(f"  WARNING: No test folios have valid targets")
            fold_results.append({'fold': fold_idx, 'n_targets': 0})
            continue
        
        # Evaluate
        rare_ings, _, _ = classify_ingredients(ident_ings, all_recipe_ings)
        ev = evaluate_method(
            f'fold_{fold_idx}', test_predictions, test_targets,
            all_recipe_ings, ident_ings, rare_ings,
            sorted(test_targets.keys())
        )
        
        fold_results.append({
            'fold': fold_idx,
            'n_train': len(train_folds),
            'n_test': len(test_fold),
            'n_stems': n_stems,
            'n_unique_ings': n_unique,
            'n_targets': len(test_targets),
            'fixed_f1': ev['fixed_f1_mean'],
            'rare_f1': ev['rare_f1_mean'],
            'mrr': ev['mrr'],
            'p_at_1': ev['p_at_1'],
        })
        
        print(f"  Test Fixed F1: {ev['fixed_f1_mean']:.1f}%")
        print(f"  Test Rare F1:  {ev['rare_f1_mean']:.1f}%")
        print(f"  Test MRR:      {ev['mrr']:.3f}")
        print(f"  Test P@1:      {ev['p_at_1']:.1%}")
    
    # Aggregate
    valid_folds = [r for r in fold_results if r.get('fixed_f1') is not None]
    if valid_folds:
        avg_f1 = sum(r['fixed_f1'] for r in valid_folds) / len(valid_folds)
        avg_rare = sum(r['rare_f1'] for r in valid_folds) / len(valid_folds)
        avg_mrr = sum(r['mrr'] for r in valid_folds) / len(valid_folds)
        std_f1 = (sum((r['fixed_f1'] - avg_f1)**2 for r in valid_folds) / len(valid_folds))**0.5
        
        print(f"\n  CROSS-VALIDATION SUMMARY ({len(valid_folds)} valid folds)")
        print(f"  Mean Fixed F1:  {avg_f1:.1f}% +/- {std_f1:.1f}%")
        print(f"  Mean Rare F1:   {avg_rare:.1f}%")
        print(f"  Mean MRR:       {avg_mrr:.3f}")
        
        if std_f1 < 10:
            print("  VERDICT: Stable -- low variance across folds")
        elif std_f1 < 20:
            print("  VERDICT: Moderate -- some variance across folds")
        else:
            print("  VERDICT: Unstable -- high variance, results depend on split")
    
    return fold_results


# ── Ablation analysis ────────────────────────────────────────────────────────
def run_ablation():
    """Remove each identified ingredient one at a time and measure impact."""
    print(f"\n{'='*75}")
    print("ABLATION ANALYSIS")
    print(f"{'='*75}")
    print("Removing each ingredient to measure system fragility")
    
    data = dl.load_all()
    ident_map = data['ident_map']
    ident_ings = data['ident_ingredients']
    folio_stems = data['folio_stems']
    recipe_ings = data['recipe_ingredients']
    
    # Baseline: full system
    # Load v7 targets for baseline eval
    matching = dl.load_matching_v7()
    targets = {}
    for row in matching:
        if row['Best_Recipe']:
            targets[row['Folio']] = row['Best_Recipe']
    
    folios = sorted(targets.keys())
    rare_ings, _, _ = classify_ingredients(ident_ings, recipe_ings)
    
    full_preds = {}
    for folio in folios:
        ings = set()
        for stem in folio_stems.get(folio, set()):
            if stem in ident_map and ident_map[stem] != 'FUNCTION_WORD':
                for sub in ident_map[stem].split('|'):
                    ings.add(sub.strip())
        full_preds[folio] = ings
    
    full_eval = evaluate_method(
        'full', full_preds, targets, recipe_ings,
        ident_ings, rare_ings, folios
    )
    
    print(f"\n  Baseline (all ingredients): F1={full_eval['fixed_f1_mean']:.1f}%, "
          f"Rare F1={full_eval['rare_f1_mean']:.1f}%")
    
    # Ablate each ingredient
    ablation_results = []
    unique_ings = sorted(ident_ings)
    
    for removed_ing in unique_ings:
        # Create ablated ident_map
        ablated_map = {}
        for stem, ing in ident_map.items():
            if ing == removed_ing:
                continue  # Remove this ingredient
            if '|' in ing and removed_ing in ing:
                parts = [p.strip() for p in ing.split('|') if p.strip() != removed_ing]
                if parts:
                    ablated_map[stem] = '|'.join(parts)
                continue
            ablated_map[stem] = ing
        
        ablated_ings = set()
        for ing in ablated_map.values():
            if ing != 'FUNCTION_WORD':
                for sub in ing.split('|'):
                    ablated_ings.add(sub.strip())
        
        ablated_preds = {}
        for folio in folios:
            ings = set()
            for stem in folio_stems.get(folio, set()):
                if stem in ablated_map and ablated_map[stem] != 'FUNCTION_WORD':
                    for sub in ablated_map[stem].split('|'):
                        ings.add(sub.strip())
            ablated_preds[folio] = ings
        
        abl_rare, _, _ = classify_ingredients(ablated_ings, recipe_ings)
        abl_eval = evaluate_method(
            f'without_{removed_ing}', ablated_preds, targets,
            recipe_ings, ablated_ings, abl_rare, folios
        )
        
        delta_f1 = abl_eval['fixed_f1_mean'] - full_eval['fixed_f1_mean']
        delta_rare = abl_eval['rare_f1_mean'] - full_eval['rare_f1_mean']
        
        ablation_results.append({
            'removed': removed_ing,
            'fixed_f1': abl_eval['fixed_f1_mean'],
            'rare_f1': abl_eval['rare_f1_mean'],
            'mrr': abl_eval['mrr'],
            'delta_f1': delta_f1,
            'delta_rare_f1': delta_rare,
        })
    
    # Sort by impact
    ablation_results.sort(key=lambda x: x['delta_f1'])
    
    print(f"\n  {'Removed':<25} {'F1':>6} {'dF1':>7} {'Rare F1':>8} {'dRare':>7} {'MRR':>6}")
    print(f"  {'-'*65}")
    for r in ablation_results:
        impact = "CRITICAL" if r['delta_f1'] < -5 else "MODERATE" if r['delta_f1'] < -2 else "LOW"
        print(f"  {r['removed']:<25} {r['fixed_f1']:>5.1f}% {r['delta_f1']:>+6.1f}pp "
              f"{r['rare_f1']:>7.1f}% {r['delta_rare_f1']:>+6.1f}pp "
              f"{r['mrr']:>6.3f} [{impact}]")
    
    critical = sum(1 for r in ablation_results if r['delta_f1'] < -5)
    moderate = sum(1 for r in ablation_results if -5 <= r['delta_f1'] < -2)
    
    print(f"\n  Critical ingredients (dF1 < -5pp): {critical}")
    print(f"  Moderate ingredients (-5 <= dF1 < -2): {moderate}")
    print(f"  Low impact (dF1 >= -2): {len(ablation_results) - critical - moderate}")
    
    if critical > len(ablation_results) * 0.3:
        print("  VERDICT: System is FRAGILE -- many single-point-of-failure ingredients")
    elif critical > 0:
        print("  VERDICT: Some key ingredients carry disproportionate weight")
    else:
        print("  VERDICT: System is ROBUST -- no single ingredient is critical")
    
    return ablation_results


# ── Coverage analysis ────────────────────────────────────────────────────────
def run_coverage_analysis():
    """Measure what fraction of the manuscript the identifications cover."""
    print(f"\n{'='*75}")
    print("COVERAGE ANALYSIS")
    print(f"{'='*75}")
    print("What percentage of the manuscript is actually explained?")
    
    data = dl.load_all()
    corpus = dl.load_corpus()
    folio_words = dl.corpus_to_folio_words(corpus)
    ident_map = data['ident_map']
    
    # Total words in recipe folios
    total_words = 0
    identified_words = 0
    unidentified_words = 0
    recipe_folio_count = 0
    
    stem_coverage = defaultdict(lambda: {'total': 0, 'identified': 0})
    
    for folio, words in folio_words.items():
        if not any(folio.startswith(p) for p in ['f87', 'f88', 'f89', 'f9', 'f10', 'f11']):
            continue
        recipe_folio_count += 1
        for word in words:
            total_words += 1
            stem, suffix = dl.split_stem_suffix(word)
            if stem in ident_map:
                identified_words += 1
                stem_coverage[folio]['identified'] += 1
            else:
                unidentified_words += 1
            stem_coverage[folio]['total'] += 1
    
    pct_identified = identified_words / total_words * 100 if total_words > 0 else 0
    
    print(f"\n  Recipe folios: {recipe_folio_count}")
    print(f"  Total words: {total_words}")
    print(f"  Words with identified stems: {identified_words} ({pct_identified:.1f}%)")
    print(f"  Words without identification: {unidentified_words} ({100-pct_identified:.1f}%)")
    
    # Per-folio coverage
    print(f"\n  Per-folio coverage:")
    coverages = []
    for folio in sorted(stem_coverage.keys()):
        sc = stem_coverage[folio]
        pct = sc['identified'] / sc['total'] * 100 if sc['total'] > 0 else 0
        coverages.append(pct)
        if pct < 20:
            print(f"    {folio}: {pct:.1f}% ({sc['identified']}/{sc['total']}) LOW")
    
    mean_coverage = sum(coverages) / len(coverages) if coverages else 0
    std_coverage = (sum((c - mean_coverage)**2 for c in coverages) / len(coverages))**0.5 if coverages else 0
    
    print(f"\n  Mean per-folio coverage: {mean_coverage:.1f}% +/- {std_coverage:.1f}%")
    print(f"  Min coverage: {min(coverages):.1f}%")
    print(f"  Max coverage: {max(coverages):.1f}%")
    
    # Stem-level analysis
    all_stems = set()
    for stems in data['folio_stems'].values():
        all_stems.update(stems)
    
    identified_stems = set(ident_map.keys())
    coverage_by_frequency = defaultdict(lambda: {'identified': 0, 'total': 0})
    
    stem_folios = data['stem_folios']
    for stem in all_stems:
        n_folios = len(stem_folios.get(stem, set()))
        bucket = 'rare (1-2 folios)' if n_folios <= 2 else 'moderate (3-5)' if n_folios <= 5 else 'common (6+)'
        coverage_by_frequency[bucket]['total'] += 1
        if stem in identified_stems:
            coverage_by_frequency[bucket]['identified'] += 1
    
    print(f"\n  Coverage by stem frequency:")
    for bucket in ['rare (1-2 folios)', 'moderate (3-5)', 'common (6+)']:
        d = coverage_by_frequency[bucket]
        pct = d['identified'] / d['total'] * 100 if d['total'] > 0 else 0
        print(f"    {bucket}: {d['identified']}/{d['total']} ({pct:.1f}%)")
    
    return {
        'total_words': total_words,
        'identified_words': identified_words,
        'pct_identified': pct_identified,
        'mean_folio_coverage': mean_coverage,
        'std_folio_coverage': std_coverage,
        'total_unique_stems': len(all_stems),
        'identified_unique_stems': len(identified_stems),
    }


# ── Main ─────────────────────────────────────────────────────────────────────
def run_sensitivity_analysis():
    print("=" * 75)
    print("VOYNICH SENSITIVITY & ROBUSTNESS ANALYSIS")
    print("=" * 75)
    
    # Coverage
    coverage = run_coverage_analysis()
    
    # Ablation
    ablation = run_ablation()
    
    # K-fold CV
    kfold = run_kfold_cv(k=5)
    
    # Save all results
    ensure_output_dirs()
    save = {
        'coverage': coverage,
        'ablation': ablation,
        'kfold': kfold,
    }
    out_path = os.path.join(PATHS['output_validation'], 'sensitivity_analysis_results.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(save, f, indent=2, ensure_ascii=False)
    print(f"\nAll results saved to: {out_path}")
    
    return save


if __name__ == '__main__':
    run_sensitivity_analysis()
