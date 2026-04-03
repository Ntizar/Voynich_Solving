"""
Voynich Validation Framework -- Recipe Corpus Diagnostics
=========================================================

Quantifies how much the current historical recipe corpus limits semantic
discrimination.

Questions answered:
    1. How concentrated is the ingredient frequency distribution?
    2. How similar are recipes to one another?
    3. How much ingredient support do held-out test recipes have in train?
    4. Which ingredients and recipe families are most responsible for
       baseline inflation?

Run:
    python -m scripts.validation.recipe_corpus_diagnostics
"""
import sys
import os
import json
from collections import Counter, defaultdict

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.validation.config import PATHS, ensure_output_dirs
from scripts.validation import data_loader as dl
from scripts.validation.v8_builder import load_blind_splits

sys.stdout.reconfigure(encoding='utf-8')


def jaccard(a, b):
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def overlap_recall(target, source):
    if not target:
        return 0.0
    return len(target & source) / len(target)


def summarize_frequency(freq, n_recipes):
    rows = []
    for ing, count in freq.most_common():
        rows.append({
            'ingredient': ing,
            'count': count,
            'pct_recipes': count / n_recipes * 100,
        })
    return rows


def pairwise_recipe_similarity(recipe_ingredients):
    names = sorted(recipe_ingredients.keys())
    pairs = []
    for i, left in enumerate(names):
        left_ings = recipe_ingredients[left]
        for right in names[i + 1:]:
            right_ings = recipe_ingredients[right]
            sim = jaccard(left_ings, right_ings)
            inter = len(left_ings & right_ings)
            pairs.append({
                'left': left,
                'right': right,
                'jaccard': sim,
                'shared_ingredients': inter,
                'left_size': len(left_ings),
                'right_size': len(right_ings),
            })
    pairs.sort(key=lambda row: (-row['jaccard'], -row['shared_ingredients'], row['left'], row['right']))
    return pairs


def recipe_type_counts(recipes_main):
    counts = Counter()
    for row in recipes_main:
        counts[row['Tipo']] += 1
    return counts


def ingredient_type_spread(flat_rows):
    ing_to_types = defaultdict(set)
    ing_to_categories = defaultdict(set)
    recipe_to_type = {}
    for row in dl.load_recipes_main():
        recipe_to_type[row['Nombre_Receta']] = row['Tipo']

    for row in flat_rows:
        ing = row['Ingrediente_Normalizado']
        recipe = row['Receta']
        ing_to_categories[ing].add(row['Categoria'])
        if recipe in recipe_to_type:
            ing_to_types[ing].add(recipe_to_type[recipe])

    rows = []
    for ing in sorted(ing_to_types):
        rows.append({
            'ingredient': ing,
            'n_recipe_types': len(ing_to_types[ing]),
            'recipe_types': sorted(ing_to_types[ing]),
            'categories': sorted(ing_to_categories[ing]),
        })
    rows.sort(key=lambda row: (-row['n_recipe_types'], row['ingredient']))
    return rows


def test_recipe_support(train_recipes, test_recipes, recipe_ingredients):
    train_union = set()
    for recipe in train_recipes:
        train_union.update(recipe_ingredients[recipe])

    rows = []
    for recipe in sorted(test_recipes):
        ings = recipe_ingredients[recipe]
        seen = ings & train_union
        unseen = ings - train_union
        nearest_train = None
        nearest_jacc = -1.0
        for train_recipe in train_recipes:
            sim = jaccard(ings, recipe_ingredients[train_recipe])
            if sim > nearest_jacc:
                nearest_jacc = sim
                nearest_train = train_recipe
        rows.append({
            'recipe': recipe,
            'n_ingredients': len(ings),
            'support_in_train_pct': overlap_recall(ings, train_union) * 100,
            'n_unseen_ingredients': len(unseen),
            'unseen_ingredients': sorted(unseen),
            'nearest_train_recipe': nearest_train,
            'nearest_train_jaccard': nearest_jacc,
        })
    rows.sort(key=lambda row: (row['support_in_train_pct'], -row['n_unseen_ingredients'], row['recipe']))
    return rows


def mean_test_to_train_similarity(train_recipes, test_recipes, recipe_ingredients):
    rows = []
    for recipe in sorted(test_recipes):
        sims = [jaccard(recipe_ingredients[recipe], recipe_ingredients[train]) for train in train_recipes]
        rows.append({
            'recipe': recipe,
            'mean_train_jaccard': sum(sims) / len(sims) if sims else 0.0,
            'max_train_jaccard': max(sims) if sims else 0.0,
        })
    return rows


def concentration_stats(freq, n_recipes):
    counts = sorted(freq.values(), reverse=True)
    total = sum(counts)
    top5 = sum(counts[:5]) / total * 100 if total else 0.0
    top10 = sum(counts[:10]) / total * 100 if total else 0.0
    recurrent_50 = sum(1 for c in counts if c / n_recipes >= 0.50)
    recurrent_30 = sum(1 for c in counts if c / n_recipes >= 0.30)
    return {
        'top5_share_pct': top5,
        'top10_share_pct': top10,
        'ingredients_in_50pct_plus_recipes': recurrent_50,
        'ingredients_in_30pct_plus_recipes': recurrent_30,
    }


def main():
    print("=" * 78)
    print("VOYNICH RECIPE CORPUS DIAGNOSTICS")
    print("=" * 78)

    data = dl.load_all()
    flat = data['recipes_flat']
    recipes_main = data['recipes_main']
    recipe_ingredients = data['recipe_ingredients']
    splits = load_blind_splits()

    train_recipes = set(splits['recipe_split']['train'])
    test_recipes = set(splits['recipe_split']['test'])

    ingredient_freq = Counter()
    for ingredients in recipe_ingredients.values():
        for ing in ingredients:
            ingredient_freq[ing] += 1

    freq_rows = summarize_frequency(ingredient_freq, len(recipe_ingredients))
    pairwise = pairwise_recipe_similarity(recipe_ingredients)
    type_counts = recipe_type_counts(recipes_main)
    spread_rows = ingredient_type_spread(flat)
    test_support = test_recipe_support(train_recipes, test_recipes, recipe_ingredients)
    test_train_sim = mean_test_to_train_similarity(train_recipes, test_recipes, recipe_ingredients)
    concentration = concentration_stats(ingredient_freq, len(recipe_ingredients))

    print("\nTop recurring ingredients:")
    for row in freq_rows[:15]:
        print(f"  {row['ingredient']:<22} {row['count']:>2}/{len(recipe_ingredients)} recipes ({row['pct_recipes']:.1f}%)")

    print("\nConcentration:")
    print(f"  Top 5 ingredients account for {concentration['top5_share_pct']:.1f}% of all ingredient occurrences")
    print(f"  Top 10 ingredients account for {concentration['top10_share_pct']:.1f}% of all ingredient occurrences")
    print(f"  Ingredients in >=50% of recipes: {concentration['ingredients_in_50pct_plus_recipes']}")
    print(f"  Ingredients in >=30% of recipes: {concentration['ingredients_in_30pct_plus_recipes']}")

    print("\nRecipe type counts:")
    for recipe_type, count in type_counts.most_common():
        print(f"  {recipe_type}: {count}")

    print("\nMost overlapping recipe pairs:")
    for row in pairwise[:12]:
        print(
            f"  {row['left']}  <->  {row['right']} | "
            f"J={row['jaccard']:.3f}, shared={row['shared_ingredients']}"
        )

    print("\nTest recipe support from train:")
    for row in test_support:
        print(
            f"  {row['recipe']:<42} support={row['support_in_train_pct']:>5.1f}% "
            f"unseen={row['n_unseen_ingredients']:>2} nearest={row['nearest_train_jaccard']:.3f} -> {row['nearest_train_recipe']}"
        )

    print("\nHigh-spread ingredients across recipe types:")
    for row in spread_rows[:15]:
        print(f"  {row['ingredient']:<22} types={row['n_recipe_types']:>2} cats={','.join(row['categories'])}")

    ensure_output_dirs()
    out_path = os.path.join(PATHS['output_validation'], 'recipe_corpus_diagnostics.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({
            'frequency': freq_rows,
            'concentration': concentration,
            'recipe_type_counts': dict(type_counts),
            'pairwise_recipe_similarity_top50': pairwise[:50],
            'test_recipe_support': test_support,
            'test_recipe_train_similarity': test_train_sim,
            'ingredient_type_spread_top50': spread_rows[:50],
        }, f, indent=2, ensure_ascii=False)

    print(f"\nSaved diagnostics to: {out_path}")


if __name__ == '__main__':
    main()
