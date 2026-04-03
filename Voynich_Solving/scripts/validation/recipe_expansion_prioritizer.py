"""
Voynich Validation Framework -- Recipe Expansion Prioritizer
============================================================

Scores candidate recipes for corpus expansion.

The goal is not to add many recipes, but to add recipes that reduce the
current blind-test support gaps and avoid adding redundant near-duplicates.

Input:
    data/recipes/recipe_expansion_candidates_seed.csv
    or any compatible CSV with the same schema.

Output:
    output/validation/recipe_expansion_priorities.json
"""
import sys
import os
import csv
import json
from collections import defaultdict

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.validation.config import PATHS, ROOT, ensure_output_dirs

sys.stdout.reconfigure(encoding='utf-8')


INPUT_PATH = os.path.join(ROOT, 'data', 'recipes', 'recipe_expansion_candidates_seed.csv')
DIAG_PATH = os.path.join(PATHS['output_validation'], 'recipe_corpus_diagnostics.json')


PRIORITY_WEIGHT = {
    'critical': 40,
    'high': 28,
    'medium': 16,
    'low': 8,
}

RISK_PENALTY = {
    'low': 0,
    'medium': 8,
    'high': 18,
}


def load_csv(path):
    rows = []
    with open(path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def split_pipe(value):
    if not value.strip():
        return []
    return [part.strip() for part in value.split('|') if part.strip()]


def main():
    if not os.path.exists(DIAG_PATH):
        raise FileNotFoundError(
            f"Missing diagnostics file: {DIAG_PATH}. Run recipe_corpus_diagnostics first."
        )

    candidates = load_csv(INPUT_PATH)
    with open(DIAG_PATH, encoding='utf-8') as f:
        diagnostics = json.load(f)

    test_support = {
        row['recipe']: row
        for row in diagnostics['test_recipe_support']
    }

    ranked = []
    for row in candidates:
        target_names = split_pipe(row['Target_Test_Recipe'])
        target_ings = split_pipe(row['Target_Unseen_Ingredients'])
        expected_new = split_pipe(row['Expected_New_Ingredients'])

        support_bonus = 0.0
        for recipe_name in target_names:
            if recipe_name in test_support:
                support_bonus += max(0.0, 100.0 - test_support[recipe_name]['support_in_train_pct'])

        score = 0.0
        score += PRIORITY_WEIGHT.get(row['Priority'].strip().lower(), 0)
        score += len(set(target_ings)) * 6.0
        score += len(set(expected_new)) * 5.0
        score += support_bonus * 0.35
        score -= RISK_PENALTY.get(row['Likely_Overlap_Risk'].strip().lower(), 0)

        ranked.append({
            'candidate_recipe': row['Candidate_Recipe'],
            'source': row['Source'],
            'type': row['Type'],
            'status': row['Status'],
            'priority': row['Priority'],
            'target_test_recipe': target_names,
            'target_unseen_ingredients': target_ings,
            'expected_new_ingredients': expected_new,
            'overlap_risk': row['Likely_Overlap_Risk'],
            'why_this_helps': row['Why_This_Helps'],
            'notes': row['Notes'],
            'priority_score': round(score, 2),
        })

    ranked.sort(key=lambda row: (-row['priority_score'], row['candidate_recipe']))

    print("=" * 88)
    print("RECIPE EXPANSION PRIORITIES")
    print("=" * 88)
    print(f"{'Score':>7} {'Priority':<8} {'Risk':<6} {'Candidate':<42} {'Target'}")
    print("-" * 88)
    for row in ranked:
        target = ', '.join(row['target_test_recipe'])
        print(f"{row['priority_score']:>7.2f} {row['priority']:<8} {row['overlap_risk']:<6} {row['candidate_recipe']:<42} {target}")

    ensure_output_dirs()
    out_path = os.path.join(PATHS['output_validation'], 'recipe_expansion_priorities.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({'ranked_candidates': ranked}, f, indent=2, ensure_ascii=False)

    print(f"\nSaved priorities to: {out_path}")


if __name__ == '__main__':
    main()
