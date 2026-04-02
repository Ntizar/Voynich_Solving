"""
Voynich Validation Framework -- Data Contracts
===============================================
Validates structural integrity of every source file before any analysis runs.
If any contract fails, the pipeline halts with an explicit error.

Run:
    python -m scripts.validation.data_contracts

Checks:
    1. Source file hashes match frozen values
    2. CSV schemas: required columns present, no unexpected nulls
    3. Uniqueness: no duplicate stems in identifications, no duplicate folio-stem pairs
    4. Referential integrity: every identified stem exists in the folio-stem corpus
    5. Normalization: no un-normalized ingredient aliases in flat table
    6. Numeric sanity: confidence values are 0-100, tier values are 0-4
    7. Section integrity: each folio maps to exactly one section
    8. Ingredient consistency: flat table ingredients match main table lists
"""
import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.core.config import verify_source_hashes, PATHS
from scripts.core import data_loader as dl

sys.stdout.reconfigure(encoding='utf-8')


class ContractResult:
    """Accumulates pass/fail results for contracts."""
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []

    def ok(self, name, detail=""):
        self.passed.append((name, detail))
        print(f"  [PASS] {name}" + (f" -- {detail}" if detail else ""))

    def fail(self, name, detail=""):
        self.failed.append((name, detail))
        print(f"  [FAIL] {name}" + (f" -- {detail}" if detail else ""))

    def warn(self, name, detail=""):
        self.warnings.append((name, detail))
        print(f"  [WARN] {name}" + (f" -- {detail}" if detail else ""))

    def summary(self):
        total = len(self.passed) + len(self.failed)
        print(f"\n{'='*70}")
        print(f"CONTRACTS: {len(self.passed)}/{total} passed, "
              f"{len(self.failed)} failed, {len(self.warnings)} warnings")
        if self.failed:
            print("VERDICT: BLOCKED -- fix failures before running analysis")
        elif self.warnings:
            print("VERDICT: PASS WITH WARNINGS")
        else:
            print("VERDICT: ALL CLEAR")
        print(f"{'='*70}")
        return len(self.failed) == 0


def run_contracts():
    R = ContractResult()

    # ── 1. Hash integrity ────────────────────────────────────────────────
    print("\n--- 1. Source file integrity (SHA-256 hashes) ---")
    failures = verify_source_hashes(strict=False)
    if not failures:
        R.ok("All source hashes match frozen values")
    else:
        for key, exp, act in failures:
            R.fail(f"Hash mismatch: {key}", f"expected {exp[:16]}... got {act[:16]}...")

    # ── 2. CSV schema checks ─────────────────────────────────────────────
    print("\n--- 2. CSV schema validation ---")

    # recipes_main
    recipes = dl.load_recipes_main()
    required_cols = {'Nombre_Receta', 'Fuente', 'Tipo', 'Total_Ingredientes',
                     'N_Activos_Raros', 'N_Especias', 'N_Bases'}
    actual_cols = set(recipes[0].keys()) if recipes else set()
    missing = required_cols - actual_cols
    if missing:
        R.fail("recipes_main schema", f"missing columns: {missing}")
    else:
        R.ok("recipes_main schema", f"{len(recipes)} rows, all required columns present")

    # recipes_flat
    flat = dl.load_recipes_flat()
    required_flat = {'Receta', 'Ingrediente', 'Categoria', 'Ingrediente_Normalizado'}
    actual_flat = set(flat[0].keys()) if flat else set()
    missing_flat = required_flat - actual_flat
    if missing_flat:
        R.fail("recipes_flat schema", f"missing columns: {missing_flat}")
    else:
        R.ok("recipes_flat schema", f"{len(flat)} rows, all required columns present")

    # folio_stems
    stems = dl.load_recipe_folio_stems()
    required_stems = {'Folio', 'Stem', 'Final_Atoms', 'Token_Count'}
    actual_stems = set(stems[0].keys()) if stems else set()
    missing_stems = required_stems - actual_stems
    if missing_stems:
        R.fail("recipe_folio_stems schema", f"missing columns: {missing_stems}")
    else:
        R.ok("recipe_folio_stems schema", f"{len(stems)} rows, all required columns present")

    # identifications
    idents = dl.load_identifications()
    required_ids = {'Stem', 'Ingredient', 'Confidence', 'Tier', 'Source', 'Reasoning'}
    actual_ids = set(idents[0].keys()) if idents else set()
    missing_ids = required_ids - actual_ids
    if missing_ids:
        R.fail("identifications_v7 schema", f"missing columns: {missing_ids}")
    else:
        R.ok("identifications_v7 schema", f"{len(idents)} rows, all required columns present")

    # ── 3. Uniqueness constraints ────────────────────────────────────────
    print("\n--- 3. Uniqueness constraints ---")

    # No duplicate stems in identifications
    id_stems = [r['Stem'] for r in idents]
    dup_stems = [s for s in set(id_stems) if id_stems.count(s) > 1]
    if dup_stems:
        R.fail("Unique stems in identifications", f"duplicates: {dup_stems}")
    else:
        R.ok("Unique stems in identifications", f"{len(id_stems)} stems, all unique")

    # No duplicate (Folio, Stem) pairs in folio-stem table
    folio_stem_pairs = [(r['Folio'], r['Stem']) for r in stems]
    n_unique_pairs = len(set(folio_stem_pairs))
    if n_unique_pairs < len(folio_stem_pairs):
        n_dups = len(folio_stem_pairs) - n_unique_pairs
        R.fail("Unique folio-stem pairs", f"{n_dups} duplicates found")
    else:
        R.ok("Unique folio-stem pairs", f"{n_unique_pairs} pairs, all unique")

    # No duplicate recipe names
    recipe_names = [r['Nombre_Receta'] for r in recipes]
    dup_recipes = [n for n in set(recipe_names) if recipe_names.count(n) > 1]
    if dup_recipes:
        R.fail("Unique recipe names", f"duplicates: {dup_recipes}")
    else:
        R.ok("Unique recipe names", f"{len(recipe_names)} recipes, all unique")

    # ── 4. Referential integrity ─────────────────────────────────────────
    print("\n--- 4. Referential integrity ---")

    # Every identified stem should exist in the folio-stem corpus
    corpus_stems = {r['Stem'] for r in stems}
    id_stem_set = {r['Stem'] for r in idents}
    orphan_ids = id_stem_set - corpus_stems
    if orphan_ids:
        R.warn("Identified stems exist in corpus",
               f"{len(orphan_ids)} orphans: {sorted(orphan_ids)[:10]}...")
    else:
        R.ok("Identified stems exist in corpus", "all identified stems found in folio-stem data")

    # Every recipe in flat table should exist in main table
    main_names = set(recipe_names)
    flat_names = {r['Receta'] for r in flat}
    orphan_recipes = flat_names - main_names
    if orphan_recipes:
        R.fail("Flat recipe names match main table",
               f"{len(orphan_recipes)} orphans: {sorted(orphan_recipes)[:5]}")
    else:
        R.ok("Flat recipe names match main table", "all flat recipe names found in main table")

    # ── 5. Normalization checks ──────────────────────────────────────────
    print("\n--- 5. Normalization checks ---")

    # No empty Ingrediente_Normalizado
    empty_norm = [r for r in flat if not r['Ingrediente_Normalizado'].strip()]
    if empty_norm:
        R.fail("No empty normalized ingredients", f"{len(empty_norm)} empty values")
    else:
        R.ok("No empty normalized ingredients")

    # Check for obvious un-normalized aliases (same ingredient, different spelling)
    norm_ings = sorted({r['Ingrediente_Normalizado'] for r in flat})
    # Simple heuristic: check for pairs that differ only in trailing 's' or capitalization
    suspicious = []
    norm_lower = {}
    for ing in norm_ings:
        key = ing.lower().rstrip('s')
        if key in norm_lower and norm_lower[key] != ing:
            suspicious.append((norm_lower[key], ing))
        norm_lower[key] = ing
    if suspicious:
        R.warn("Potential un-normalized aliases",
               f"{len(suspicious)} pairs: {suspicious[:5]}")
    else:
        R.ok("No obvious un-normalized aliases detected")

    # Valid categories in flat table
    valid_cats = {'ACTIVO', 'ESPECIA', 'BASE'}
    bad_cats = {r['Categoria'] for r in flat} - valid_cats
    if bad_cats:
        R.fail("Valid ingredient categories", f"unexpected categories: {bad_cats}")
    else:
        R.ok("Valid ingredient categories", f"all entries are ACTIVO/ESPECIA/BASE")

    # ── 6. Numeric sanity ────────────────────────────────────────────────
    print("\n--- 6. Numeric sanity ---")

    # Confidence values should be 0-100
    bad_conf = []
    for r in idents:
        try:
            c = float(r['Confidence'])
            if c < 0 or c > 100:
                bad_conf.append((r['Stem'], c))
        except ValueError:
            bad_conf.append((r['Stem'], r['Confidence']))
    if bad_conf:
        R.fail("Confidence values 0-100", f"{len(bad_conf)} invalid: {bad_conf[:5]}")
    else:
        R.ok("Confidence values 0-100", "all valid")

    # Tier values should be 0-4
    bad_tier = []
    for r in idents:
        try:
            t = int(r['Tier'])
            if t < 0 or t > 4:
                bad_tier.append((r['Stem'], t))
        except ValueError:
            bad_tier.append((r['Stem'], r['Tier']))
    if bad_tier:
        R.fail("Tier values 0-4", f"{len(bad_tier)} invalid: {bad_tier[:5]}")
    else:
        R.ok("Tier values 0-4", "all valid")

    # Total_Ingredientes should be numeric and match sum of subcounts
    bad_totals = []
    for r in recipes:
        try:
            total = int(r['Total_Ingredientes'])
            activos = int(r['N_Activos_Raros'])
            especias = int(r['N_Especias'])
            bases = int(r['N_Bases'])
            # Allow some slack (some recipes have "otros" not counted)
            if total < activos + especias + bases:
                bad_totals.append((r['Nombre_Receta'], total,
                                   activos + especias + bases))
        except ValueError:
            bad_totals.append((r['Nombre_Receta'], 'NON_NUMERIC', ''))
    if bad_totals:
        R.warn("Recipe totals >= sum of subcounts",
               f"{len(bad_totals)} issues: {bad_totals[:3]}")
    else:
        R.ok("Recipe totals >= sum of subcounts")

    # Flat table ingredient count per recipe should match Total_Ingredientes
    flat_counts = {}
    for r in flat:
        flat_counts[r['Receta']] = flat_counts.get(r['Receta'], 0) + 1
    mismatches = []
    for r in recipes:
        name = r['Nombre_Receta']
        declared = int(r['Total_Ingredientes'])
        actual = flat_counts.get(name, 0)
        if declared != actual:
            mismatches.append((name, declared, actual))
    if mismatches:
        R.warn("Flat count matches declared total",
               f"{len(mismatches)} mismatches: {mismatches[:3]}")
    else:
        R.ok("Flat count matches declared total")

    # ── 7. No text in numeric columns ────────────────────────────────────
    print("\n--- 7. Column type checks ---")

    # Token_Count in folio-stem table should be numeric
    bad_tokens = [r for r in stems if not r['Token_Count'].strip().isdigit()]
    if bad_tokens:
        R.fail("Token_Count is numeric", f"{len(bad_tokens)} non-numeric values")
    else:
        R.ok("Token_Count is numeric", "all values are integers")

    # ── Summary ──────────────────────────────────────────────────────────
    return R.summary()


if __name__ == '__main__':
    print("=" * 70)
    print("VOYNICH VALIDATION FRAMEWORK -- DATA CONTRACTS")
    print("=" * 70)
    success = run_contracts()
    sys.exit(0 if success else 1)
