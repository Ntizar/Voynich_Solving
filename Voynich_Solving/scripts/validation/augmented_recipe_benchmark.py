"""
Voynich Validation Framework -- Augmented Recipe Corpus Benchmark
================================================================

Runs the multi-representation benchmark against a recipe corpus augmented with
new externally sourced recipe witnesses.

This does NOT overwrite the frozen core corpus. It is an experimental track.

Run:
    python -m scripts.validation.augmented_recipe_benchmark
"""
import sys
import os
import json
from collections import defaultdict

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.validation.config import ROOT, PATHS, ensure_output_dirs
from scripts.validation import data_loader as dl
from scripts.validation.v8_builder import load_blind_splits
from scripts.validation.multi_representation_benchmark import (
    REPRESENTATIONS,
    get_recipe_folios,
    build_representation_folio_units,
    run_builder_for_representation,
    evaluate_representation,
    print_summary_table,
)

sys.stdout.reconfigure(encoding='utf-8')


AUGMENTED_MAIN = os.path.join(ROOT, 'data', 'recipes', 'augmented', 'recetas_historicas_medievales_augmented.csv')
AUGMENTED_FLAT = os.path.join(ROOT, 'data', 'recipes', 'augmented', 'recetas_historicas_ingredientes_flat_augmented.csv')


def load_augmented_recipe_ingredients():
    base_rows = dl.load_recipes_flat()
    augmented_rows = dl.load_recipes_flat(AUGMENTED_FLAT)
    combined = list(base_rows) + list(augmented_rows)
    return dl.build_recipe_ingredients(combined)


def load_augmented_recipe_names():
    base = dl.load_recipes_main()
    extra = dl.load_recipes_main(AUGMENTED_MAIN)
    return [row['Nombre_Receta'] for row in base] + [row['Nombre_Receta'] for row in extra]


def build_augmented_splits(base_splits, augmented_recipe_names):
    splits = json.loads(json.dumps(base_splits))
    train = list(splits['recipe_split']['train'])
    train.extend([name for name in augmented_recipe_names if name not in train and name not in splits['recipe_split']['test']])
    splits['recipe_split']['train'] = sorted(train)
    splits['recipe_split']['n_train'] = len(splits['recipe_split']['train'])
    return splits


def main():
    print('=' * 78)
    print('VOYNICH AUGMENTED RECIPE CORPUS BENCHMARK')
    print('Parallel experiment; frozen core corpus remains unchanged')
    print('=' * 78)

    base_splits = load_blind_splits()
    recipe_folios = get_recipe_folios()
    test_folios = set(base_splits['folio_split']['test'])
    augmented_recipe_ingredients = load_augmented_recipe_ingredients()
    augmented_recipe_names = [row['Nombre_Receta'] for row in dl.load_recipes_main(AUGMENTED_MAIN)]
    splits = build_augmented_splits(base_splits, augmented_recipe_names)

    v7_targets = {}
    for row in dl.load_matching_v7():
        if row['Folio'] in test_folios and row['Best_Recipe']:
            v7_targets[row['Folio']] = row['Best_Recipe']

    benchmark_rows = []
    for rep_name, spec in REPRESENTATIONS.items():
        print('\n' + '=' * 75)
        print(f'REPRESENTATION: {rep_name}')
        print(spec['description'])
        print('=' * 75)

        folio_units = build_representation_folio_units(rep_name, recipe_folios)
        builder = run_builder_for_representation(rep_name, folio_units, splits, augmented_recipe_ingredients)
        evaluation = evaluate_representation(
            rep_name,
            folio_units,
            builder['identifications'],
            augmented_recipe_ingredients,
            test_folios,
            v7_targets,
        )
        benchmark_rows.append({
            'name': rep_name,
            'description': spec['description'],
            'builder': {k: v for k, v in builder.items() if k != 'identifications'},
            'evaluation': evaluation,
        })

    print_summary_table(benchmark_rows)

    ensure_output_dirs()
    out_path = os.path.join(PATHS['output_validation'], 'augmented_recipe_benchmark.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({
            'added_recipe_witnesses': augmented_recipe_names,
            'representations': benchmark_rows,
        }, f, indent=2, ensure_ascii=False)

    print(f'\nSaved augmented benchmark to: {out_path}')


if __name__ == '__main__':
    main()
