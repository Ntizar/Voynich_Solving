"""
Voynich Validation Framework -- Multi-Representation Benchmark
==============================================================

Runs the same train/test builder + evaluator across multiple input
representations, without changing the recipes, blind splits, or metrics.

Goal:
    Test whether the stem-to-ingredient signal survives changes in the
    input encoding layer.

Representations included:
    1. sta_stem_frozen: current frozen STA-derived folio->stem table
    2. sta_token: full STA tokens, no stem/suffix decomposition
    3. eva_token: EVA tokens from an independent transcription

Interpretation:
    - If structural / mapping effects survive representation changes, they are
      more robust.
    - If only STA-derived stems work, the result is fragile and may depend on
      the transcription layer rather than the manuscript itself.

Run:
    python -m scripts.validation.multi_representation_benchmark
"""
import sys
import os
import re
import json
from collections import defaultdict, Counter

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.validation.config import PATHS, ensure_output_dirs
from scripts.validation import data_loader as dl
from scripts.validation.v8_builder import (
    load_blind_splits,
    phase0_bootstrap,
    expand_stems,
    phase1_iterative,
    MIN_FOLIO_COUNT,
)
from scripts.validation.alternative_metrics import classify_ingredients, evaluate_method
from scripts.validation.v8_evaluator import (
    make_predictions,
    baseline_most_common,
    baseline_all_ingredients,
    baseline_majority_recipe,
    run_permutation_test,
    compute_mean_f1_all_recipes,
)

sys.stdout.reconfigure(encoding='utf-8')


REPRESENTATIONS = {
    'sta_stem_frozen': {
        'kind': 'frozen_stem_table',
        'description': 'Current frozen STA stem inventory',
    },
    'sta_token': {
        'kind': 'corpus_tokens',
        'corpus_path': PATHS['corpus_sta'],
        'token_mode': 'sta_token',
        'description': 'STA tokens without stem decomposition',
    },
    'eva_token': {
        'kind': 'corpus_tokens',
        'corpus_path': os.path.join(os.path.dirname(PATHS['corpus_sta']), '..', '..',
                                    'zenodo_voynich', 'corpus', 'voynich_eva.txt'),
        'token_mode': 'eva_token',
        'description': 'Independent EVA token transcription',
    },
}


def normalize_folio(folio):
    """Map foldout sub-pages like f90r1 -> f90r."""
    return re.sub(r'^(f\d+[rv])\d+$', r'\1', folio)


def get_recipe_folios():
    """Use the frozen folio-stem table only to recover the recipe folio set."""
    rows = dl.load_recipe_folio_stems()
    return sorted({row['Folio'] for row in rows})


def clean_sta_token(word):
    """Remove IVTFF inline markup, keep STA token characters."""
    token = re.sub(r'<[^>]*>', '', word.strip())
    token = token.split(',')[0].strip()
    token = re.sub(r'[^A-Za-z0-9]', '', token)
    return token


def _replace_square(match):
    content = match.group(1)
    if ':' in content:
        return content.split(':')[-1]
    return content


def _replace_curly(match):
    return re.sub(r'[^A-Za-z]', '', match.group(1))


def clean_eva_token(word):
    """Best-effort cleanup for EVA IVTFF tokens.

    This is intentionally conservative and documented as approximate.
    It removes markup and resolves bracket alternatives by taking the
    right-hand variant when present.
    """
    token = word.strip()
    token = re.sub(r'<![^>]*>', '', token)
    token = re.sub(r'<[^>]*>', '', token)
    token = re.sub(r'\[([^\]]+)\]', _replace_square, token)
    token = re.sub(r'\{([^}]*)\}', _replace_curly, token)
    token = token.split(',')[0].strip()
    token = re.sub(r'[^A-Za-z]', '', token).lower()
    return token


def build_units_from_corpus(corpus_path, token_mode, recipe_folios):
    """Build {folio: set(units)} from a corpus file."""
    corpus = dl.load_corpus(corpus_path)
    folio_units = defaultdict(set)

    for rec in corpus:
        folio = normalize_folio(rec['folio'])
        if folio not in recipe_folios:
            continue

        for raw_word in rec['words']:
            if token_mode == 'sta_token':
                token = clean_sta_token(raw_word)
                if token:
                    folio_units[folio].add(token)
            elif token_mode == 'eva_token':
                token = clean_eva_token(raw_word)
                if token:
                    folio_units[folio].add(token)
            else:
                raise ValueError(f'Unknown token_mode: {token_mode}')

    return {folio: set(units) for folio, units in folio_units.items()}


def build_frozen_sta_stems():
    """Load the current frozen STA-derived folio->stem inventory."""
    return dl.build_folio_stems(dl.load_recipe_folio_stems())


def build_representation_folio_units(rep_name, recipe_folios):
    spec = REPRESENTATIONS[rep_name]
    if spec['kind'] == 'frozen_stem_table':
        return build_frozen_sta_stems()
    return build_units_from_corpus(spec['corpus_path'], spec['token_mode'], set(recipe_folios))


def build_stem_folios(folio_units):
    stem_folios = defaultdict(set)
    for folio, units in folio_units.items():
        for unit in units:
            stem_folios[unit].add(folio)
    return dict(stem_folios)


def build_ident_ingredients_from_map(ident_map):
    ings = set()
    for ingredient in ident_map.values():
        if ingredient == 'FUNCTION_WORD':
            continue
        for sub in ingredient.split('|'):
            sub = sub.strip()
            if sub:
                ings.add(sub)
    return ings


def load_v7_targets_for_test(test_folios):
    targets = {}
    for row in dl.load_matching_v7():
        if row['Folio'] in test_folios and row['Best_Recipe']:
            targets[row['Folio']] = row['Best_Recipe']
    return targets


def run_builder_for_representation(rep_name, all_folio_units, splits, all_recipe_ings):
    train_folios = set(splits['folio_split']['train'])
    train_recipes = set(splits['recipe_split']['train'])

    folio_units = {
        folio: set(units)
        for folio, units in all_folio_units.items()
        if folio in train_folios
    }
    stem_folios = build_stem_folios(folio_units)
    recipe_ingredients = {
        recipe: set(ings)
        for recipe, ings in all_recipe_ings.items()
        if recipe in train_recipes
    }

    all_train_stems = set()
    for units in folio_units.values():
        all_train_stems.update(units)

    identifications, identified_ingredients = phase0_bootstrap(
        train_folios, folio_units, stem_folios, recipe_ingredients, all_train_stems
    )

    for _ in range(5):
        prev_count = len(identifications)
        identifications, identified_ingredients = expand_stems(
            train_folios, folio_units, stem_folios, recipe_ingredients,
            all_train_stems, identifications, identified_ingredients
        )
        if len(identifications) == prev_count:
            break

    identifications, identified_ingredients = phase1_iterative(
        train_folios, folio_units, stem_folios, recipe_ingredients,
        all_train_stems, identifications, identified_ingredients
    )

    tier_counts = Counter(info['tier'] for info in identifications.values())
    ingredient_counts = Counter(
        info['ingredient']
        for info in identifications.values()
        if info['ingredient'] != 'FUNCTION_WORD'
    )

    return {
        'identifications': identifications,
        'tier_counts': dict(tier_counts),
        'ingredient_counts': dict(ingredient_counts),
        'n_train_units': len(all_train_stems),
        'n_train_units_ge3': sum(1 for unit, folios in stem_folios.items() if len(folios) >= MIN_FOLIO_COUNT),
    }


def evaluate_representation(rep_name, all_folio_units, identifications, all_recipe_ings, test_folios, v7_targets):
    ident_map = {unit: info['ingredient'] for unit, info in identifications.items()}
    ident_ings = build_ident_ingredients_from_map(ident_map)
    rare_ings, common_ings, freq = classify_ingredients(ident_ings, all_recipe_ings)

    target_folios = sorted(v7_targets.keys())
    preds = make_predictions(all_folio_units, ident_map, target_folios)

    methods = [
        (rep_name, preds, ident_ings, rare_ings),
        ('most_common', baseline_most_common(all_folio_units, ident_map, all_recipe_ings, ident_ings, target_folios), ident_ings, rare_ings),
        ('all_ingredients', baseline_all_ingredients(ident_ings, target_folios), ident_ings, rare_ings),
        ('majority_recipe', baseline_majority_recipe(all_recipe_ings, ident_ings, target_folios), ident_ings, rare_ings),
    ]

    results = {}
    for name, method_preds, method_ident_ings, method_rare_ings in methods:
        results[name] = evaluate_method(
            name,
            method_preds,
            v7_targets,
            all_recipe_ings,
            method_ident_ings,
            method_rare_ings,
            target_folios,
        )

    perm_results = run_permutation_test(
        all_folio_units,
        ident_map,
        v7_targets,
        all_recipe_ings,
        ident_ings,
        rare_ings,
        target_folios,
    )

    spec = compute_mean_f1_all_recipes(preds, all_recipe_ings, ident_ings, sorted(test_folios))
    specificity_values = [row['specificity'] for row in spec.values()] if spec else []
    avg_specificity = sum(specificity_values) / len(specificity_values) if specificity_values else 0.0

    baseline_names = ['most_common', 'all_ingredients', 'majority_recipe']
    best_baseline_name = max(baseline_names, key=lambda name: results[name]['fixed_f1_mean'])
    best_baseline_f1 = results[best_baseline_name]['fixed_f1_mean']
    system_f1 = results[rep_name]['fixed_f1_mean']

    verdict = 'fail'
    if system_f1 > best_baseline_f1 + 5:
        verdict = 'pass'
    elif system_f1 > best_baseline_f1:
        verdict = 'mixed'

    return {
        'n_identified_units': len(identifications),
        'n_identified_ingredients': len(ident_ings),
        'n_function_words': sum(1 for info in identifications.values() if info['ingredient'] == 'FUNCTION_WORD'),
        'n_rare_ingredients': len(rare_ings),
        'avg_specificity_test': avg_specificity,
        'strategy_1_v7_targets': {
            name: {
                key: value
                for key, value in ev.items()
                if key != 'details'
            }
            for name, ev in results.items()
        },
        'permutation': perm_results,
        'best_baseline': {
            'name': best_baseline_name,
            'fixed_f1_mean': best_baseline_f1,
        },
        'system_gap_vs_best_baseline': system_f1 - best_baseline_f1,
        'verdict': verdict,
    }


def print_summary_table(benchmark_rows):
    print("\n" + "=" * 105)
    print("MULTI-REPRESENTATION SUMMARY")
    print("=" * 105)
    print(f"{'Representation':<18} {'Units>=3':>8} {'Idents':>7} {'Ings':>6} {'Fix-F1':>7} {'BestBase':>9} {'Gap':>7} {'Rare-F1':>8} {'Excl':>7} {'p(F1)':>7} {'Verdict':>8}")
    print("-" * 105)

    for row in benchmark_rows:
        ev = row['evaluation']['strategy_1_v7_targets'][row['name']]
        best_base = row['evaluation']['best_baseline']['fixed_f1_mean']
        print(
            f"{row['name']:<18} "
            f"{row['builder']['n_train_units_ge3']:>8} "
            f"{row['evaluation']['n_identified_units']:>7} "
            f"{row['evaluation']['n_identified_ingredients']:>6} "
            f"{ev['fixed_f1_mean']:>6.1f}% "
            f"{best_base:>8.1f}% "
            f"{row['evaluation']['system_gap_vs_best_baseline']:>+6.1f} "
            f"{ev['rare_f1_mean']:>7.1f}% "
            f"{ev['exclusion_mean']:>6.1f}% "
            f"{row['evaluation']['permutation']['p_f1']:>7.3f} "
            f"{row['evaluation']['verdict']:>8}"
        )


def main():
    print("=" * 75)
    print("VOYNICH MULTI-REPRESENTATION BENCHMARK")
    print("Same split, same recipes, same builder, same evaluator")
    print("=" * 75)

    splits = load_blind_splits()
    test_folios = set(splits['folio_split']['test'])
    recipe_folios = get_recipe_folios()
    data = dl.load_all()
    all_recipe_ings = data['recipe_ingredients']
    v7_targets = load_v7_targets_for_test(test_folios)

    benchmark_rows = []

    for rep_name, spec in REPRESENTATIONS.items():
        print("\n" + "=" * 75)
        print(f"REPRESENTATION: {rep_name}")
        print(spec['description'])
        print("=" * 75)

        folio_units = build_representation_folio_units(rep_name, recipe_folios)
        builder = run_builder_for_representation(rep_name, folio_units, splits, all_recipe_ings)
        evaluation = evaluate_representation(
            rep_name,
            folio_units,
            builder['identifications'],
            all_recipe_ings,
            test_folios,
            v7_targets,
        )

        benchmark_rows.append({
            'name': rep_name,
            'description': spec['description'],
            'builder': {
                key: value
                for key, value in builder.items()
                if key != 'identifications'
            },
            'evaluation': evaluation,
        })

    print_summary_table(benchmark_rows)

    ensure_output_dirs()
    out_path = os.path.join(PATHS['output_validation'], 'multi_representation_benchmark.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({
            'blind_split_version': splits['version'],
            'representations': benchmark_rows,
        }, f, indent=2, ensure_ascii=False)

    print(f"\nSaved benchmark results to: {out_path}")


if __name__ == '__main__':
    main()
