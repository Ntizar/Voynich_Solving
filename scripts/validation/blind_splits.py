"""
Voynich Validation Framework -- Blind Splits
=============================================
Creates and manages train/test partitions for folios and recipes.
Once created, splits are frozen with a hash. Any analysis that touches
test data before final evaluation is flagged as contaminated.

Run:
    python -m scripts.validation.blind_splits          # create splits
    python -m scripts.validation.blind_splits --check   # verify existing splits

Design:
    - 20% of recipe folios (10 of 48) are held out as TEST
    - 20% of historical recipes (10 of 50) are held out as TEST
    - Stratification: test folios are sampled to cover diverse sizes (small/medium/large)
    - Splits are deterministic (seed=42) and saved with SHA-256 hash
    - A leakage detector checks whether any test folio/recipe was used in training artifacts
"""
import sys
import os
import json
import hashlib
import random

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.core.config import PATHS, SPLIT, RANDOM_SEED, ensure_output_dirs
from scripts.core import data_loader as dl

sys.stdout.reconfigure(encoding='utf-8')


def create_folio_split(folio_stems, seed=RANDOM_SEED, test_fraction=None):
    """Split recipe folios into train and test sets.

    Stratification: folios are sorted by stem count and then every Nth folio
    is assigned to test, ensuring the test set covers small, medium and large folios.

    Returns:
        (train_folios: list, test_folios: list)
    """
    test_fraction = test_fraction or SPLIT['test_folio_fraction']
    folios_by_size = sorted(folio_stems.keys(),
                            key=lambda f: len(folio_stems[f]))

    n_test = max(1, int(len(folios_by_size) * test_fraction))

    # Stratified systematic sampling: pick every N-th folio from the sorted list
    rng = random.Random(seed)
    step = len(folios_by_size) / n_test
    # Add small random offset per stratum to avoid deterministic bias
    test_indices = set()
    for i in range(n_test):
        base = int(i * step)
        # small jitter within the stratum
        jitter = rng.randint(0, max(0, int(step) - 1))
        idx = min(base + jitter, len(folios_by_size) - 1)
        test_indices.add(idx)

    # If we got fewer due to collisions, fill from remaining
    remaining = [i for i in range(len(folios_by_size)) if i not in test_indices]
    rng.shuffle(remaining)
    while len(test_indices) < n_test and remaining:
        test_indices.add(remaining.pop())

    test_folios = sorted([folios_by_size[i] for i in test_indices])
    train_folios = sorted([f for f in folios_by_size if f not in set(test_folios)])

    return train_folios, test_folios


def create_recipe_split(recipes_main, seed=RANDOM_SEED, test_fraction=None):
    """Split historical recipes into train and test sets.

    Stratification by recipe type to ensure test covers diverse types.

    Returns:
        (train_recipes: list, test_recipes: list)
    """
    test_fraction = test_fraction or SPLIT['test_recipe_fraction']
    recipe_names = [r['Nombre_Receta'] for r in recipes_main]
    n_test = max(1, int(len(recipe_names) * test_fraction))

    # Group by type for stratification
    by_type = {}
    for r in recipes_main:
        t = r.get('Tipo', 'Unknown')
        by_type.setdefault(t, []).append(r['Nombre_Receta'])

    rng = random.Random(seed)
    test_recipes = []

    # Take at least 1 from each type if possible
    types = sorted(by_type.keys())
    for t in types:
        names = by_type[t][:]
        rng.shuffle(names)
        if len(test_recipes) < n_test and names:
            test_recipes.append(names.pop(0))

    # Fill remaining test slots randomly from what's left
    remaining = [n for n in recipe_names if n not in set(test_recipes)]
    rng.shuffle(remaining)
    while len(test_recipes) < n_test and remaining:
        test_recipes.append(remaining.pop())

    test_recipes = sorted(test_recipes)
    train_recipes = sorted([n for n in recipe_names if n not in set(test_recipes)])

    return train_recipes, test_recipes


def save_splits(train_folios, test_folios, train_recipes, test_recipes):
    """Save splits to JSON with integrity hash."""
    ensure_output_dirs()

    splits = {
        'version': 'v1',
        'seed': RANDOM_SEED,
        'folio_split': {
            'train': train_folios,
            'test': test_folios,
            'n_train': len(train_folios),
            'n_test': len(test_folios),
        },
        'recipe_split': {
            'train': train_recipes,
            'test': test_recipes,
            'n_train': len(train_recipes),
            'n_test': len(test_recipes),
        },
    }

    # Compute deterministic hash of the split content
    content = json.dumps(splits, sort_keys=True, ensure_ascii=False)
    splits['integrity_hash'] = hashlib.sha256(content.encode()).hexdigest()

    out_path = os.path.join(PATHS['output_splits'], 'blind_splits.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(splits, f, indent=2, ensure_ascii=False)

    return out_path, splits


def load_splits():
    """Load existing splits from disk."""
    path = os.path.join(PATHS['output_splits'], 'blind_splits.json')
    if not os.path.exists(path):
        return None
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def verify_splits(splits):
    """Verify the integrity hash of loaded splits."""
    stored_hash = splits.pop('integrity_hash', None)
    content = json.dumps(splits, sort_keys=True, ensure_ascii=False)
    actual_hash = hashlib.sha256(content.encode()).hexdigest()
    splits['integrity_hash'] = stored_hash  # restore
    return stored_hash == actual_hash


def check_leakage(splits, ident_rows, matching_rows):
    """Check if any test folio or recipe was used in the identification or matching process.

    This is a RETROSPECTIVE check: since the current v7 identifications were built
    using ALL data, we expect leakage. The point is to quantify it and flag it.

    Returns:
        dict with leakage details
    """
    test_folios = set(splits['folio_split']['test'])
    test_recipes = set(splits['recipe_split']['test'])

    # Check: do any identifications reference test folios in their reasoning?
    ident_leaks = []
    for row in ident_rows:
        reasoning = row.get('Reasoning', '').lower()
        source = row.get('Source', '').lower()
        for tf in test_folios:
            if tf.lower() in reasoning or tf.lower() in source:
                ident_leaks.append((row['Stem'], row['Ingredient'], tf))

    # Check: are test folios present in matching results?
    matching_leaks = []
    for row in matching_rows:
        if row['Folio'] in test_folios:
            matching_leaks.append((row['Folio'], row.get('Best_Recipe', '')))

    # Check: are test recipes used as best matches for train folios?
    recipe_leaks = []
    for row in matching_rows:
        if row.get('Best_Recipe', '') in test_recipes:
            recipe_leaks.append((row['Folio'], row['Best_Recipe']))

    return {
        'ident_leaks': ident_leaks,
        'matching_leaks': matching_leaks,
        'recipe_leaks': recipe_leaks,
        'is_contaminated': bool(ident_leaks or matching_leaks),
        'note': ('EXPECTED: v7 was built with all data. This check establishes '
                 'the baseline contamination. Future runs must use train-only data.')
    }


def main(check_only=False):
    print("=" * 70)
    print("VOYNICH VALIDATION FRAMEWORK -- BLIND SPLITS")
    print("=" * 70)

    if check_only:
        splits = load_splits()
        if splits is None:
            print("[FAIL] No splits file found. Run without --check to create.")
            return False
        if verify_splits(splits):
            print("[PASS] Splits integrity verified.")
        else:
            print("[FAIL] Splits integrity hash mismatch -- file was modified!")
            return False
        print(f"  Folios: {splits['folio_split']['n_train']} train / "
              f"{splits['folio_split']['n_test']} test")
        print(f"  Recipes: {splits['recipe_split']['n_train']} train / "
              f"{splits['recipe_split']['n_test']} test")
        return True

    # Load data
    data = dl.load_all()
    folio_stems = data['folio_stems']
    recipes_main = data['recipes_main']

    # Create splits
    print("\n--- Creating folio split ---")
    train_f, test_f = create_folio_split(folio_stems)
    print(f"  Train folios ({len(train_f)}): {train_f}")
    print(f"  Test folios  ({len(test_f)}): {test_f}")

    # Show size distribution in test set
    test_sizes = [(f, len(folio_stems[f])) for f in test_f]
    print(f"  Test folio sizes: {test_sizes}")

    print("\n--- Creating recipe split ---")
    train_r, test_r = create_recipe_split(recipes_main)
    print(f"  Train recipes ({len(train_r)}):")
    for r in train_r:
        print(f"    {r}")
    print(f"  Test recipes  ({len(test_r)}):")
    for r in test_r:
        print(f"    {r}")

    # Save
    print("\n--- Saving splits ---")
    out_path, splits = save_splits(train_f, test_f, train_r, test_r)
    print(f"  Saved to: {out_path}")
    print(f"  Integrity hash: {splits['integrity_hash'][:32]}...")

    # Leakage check (retrospective)
    print("\n--- Retrospective leakage check (v7 was built with all data) ---")
    leakage = check_leakage(
        splits,
        data['identifications'],
        data['matching_v7']
    )
    print(f"  Identification leaks (test folios in reasoning): {len(leakage['ident_leaks'])}")
    for stem, ing, folio in leakage['ident_leaks'][:5]:
        print(f"    {stem} -> {ing} references {folio}")
    print(f"  Matching leaks (test folios in results): {len(leakage['matching_leaks'])}")
    print(f"  Recipe leaks (test recipes as best match): {len(leakage['recipe_leaks'])}")
    print(f"  Contaminated: {leakage['is_contaminated']}")
    print(f"  Note: {leakage['note']}")

    print(f"\n{'='*70}")
    print("SPLITS CREATED. From now on, test data must NOT be used during development.")
    print("Future analysis scripts must call load_splits() and respect the partition.")
    print(f"{'='*70}")

    return True


if __name__ == '__main__':
    check_only = '--check' in sys.argv
    success = main(check_only=check_only)
    sys.exit(0 if success else 1)
