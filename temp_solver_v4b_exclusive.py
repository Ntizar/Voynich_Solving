#!/usr/bin/env python3
"""
VOYNICH SOLVER v4b: FOLIO-EXCLUSIVE STEM EXPLOITATION
=====================================================
Focuses on stems exclusive to ONE perfect-match folio.
If a stem appears ONLY in f93v (=Diascordium, 13 ingredients), 
that stem MUST be one of those 13 ingredients.
Combined with elimination of already-identified ingredients,
this can pinpoint new identifications.

Also: Opium/Castoreum cluster disambiguation using 
Diascordium (has both) vs Pillulae Aureae (has neither).
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import csv
import os
from collections import defaultdict

BASE = r'C:\Ntizar_Obsidian\Ntizar_Brain\MASTERTMIND'

# Load data
recipe_ingredients = defaultdict(set)
ingredient_category = {}
with open(os.path.join(BASE, 'recetas_historicas_ingredientes_flat.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        rname = row['Receta'].split('(')[0].strip()
        ing = row['Ingrediente_Normalizado']
        recipe_ingredients[rname].add(ing)
        ingredient_category[ing] = row['Categoria']

stem_folios = {}
with open(os.path.join(BASE, 'voynich_stems_in_matched_folios.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        stem = row['Stem']
        folios = [x.strip() for x in row['Matched_Folios'].split('|')]
        stem_folios[stem] = {'type': row['Type'], 'folios': folios}

# Load confirmed identifications from v4
confirmed_ingredients = {}
with open(os.path.join(BASE, 'voynich_unified_identifications_v4.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        confirmed_ingredients[row['Stem']] = row['Ingredient']

already_identified = set(confirmed_ingredients.values())

# Perfect matches
PERFECT_MATCHES = {
    'f87r': 'Confectio Hamech',
    'f87v': 'Unguentum Apostolorum',
    'f88r': 'Trifera Magna',
    'f93v': 'Diascordium',
    'f96v': 'Pillulae Aureae',
    'f100r': 'Diamargariton',
    'f100v': 'Diaciminum',
    'f101v': 'Trifera Magna',
    'f103v': 'Trifera Magna',
}

# Strong matches (>=90%)
STRONG_MATCHES = {
    'f88v': 'Philonium Persicum',
    'f90r': 'Aurea Alexandrina',
    'f90v': 'Aurea Alexandrina',
    'f94r': 'Aurea Alexandrina',
    'f94v': 'Diascordium',
    'f95r': 'Trifera Magna',
    'f95v': 'Philonium Persicum',
    'f96r': 'Philonium Persicum',
    'f99r': 'Trifera Magna',
    'f99v': 'Aurea Alexandrina',
    'f100r': 'Diamargariton',
    'f100v': 'Diaciminum',
    'f101r': 'Trifera Magna',
    'f102r': 'Philonium Persicum',
    'f102v': 'Trifera Magna',
    'f105r': 'Trifera Magna',
    'f105v': 'Trifera Magna',
    'f108r': 'Trifera Magna',
    'f112r': 'Trifera Magna',
    'f114v': 'Trifera Magna',
    'f116r': 'Trifera Magna',
}

ALL_MATCHED = {**PERFECT_MATCHES, **STRONG_MATCHES}

print("=" * 80)
print("VOYNICH SOLVER v4b: FOLIO-EXCLUSIVE EXPLOITATION")
print("=" * 80)

# ============================================================
# ANALYSIS 1: For each non-Trifera perfect match, find exclusive stems
# and calculate remaining candidates after elimination
# ============================================================
print("\n--- SMALL-RECIPE PERFECT MATCHES (most constraining) ---\n")

SMALL_RECIPES = {
    'f87r': ('Confectio Hamech', 15),
    'f87v': ('Unguentum Apostolorum', 12),
    'f93v': ('Diascordium', 13),
    'f96v': ('Pillulae Aureae', 7),
    'f100r': ('Diamargariton', 16),
    'f100v': ('Diaciminum', 11),
}

for folio, (recipe, n_ing) in SMALL_RECIPES.items():
    print(f"\n{'='*60}")
    print(f"  {folio} = {recipe} ({n_ing} ingredients)")
    print(f"{'='*60}")
    
    recipe_ings = recipe_ingredients.get(recipe, set())
    
    # Already-identified ingredients in this recipe
    identified_here = recipe_ings & already_identified
    remaining_ings = recipe_ings - already_identified
    
    print(f"  Already identified: {len(identified_here)}/{n_ing}")
    for ing in sorted(identified_here):
        stems = [s for s, i in confirmed_ingredients.items() if i == ing]
        print(f"    {ing:25s} <- {stems}")
    
    print(f"\n  Remaining unidentified: {len(remaining_ings)}/{n_ing}")
    for ing in sorted(remaining_ings):
        cat = ingredient_category.get(ing, '?')
        print(f"    [{cat:8s}] {ing}")
    
    # Find stems that appear in this folio
    stems_in_folio = []
    for stem, data in stem_folios.items():
        if folio in data['folios']:
            if stem not in confirmed_ingredients:
                stems_in_folio.append(stem)
    
    print(f"\n  Unidentified stems in this folio: {len(stems_in_folio)}")
    
    # For each unidentified stem, list what other matched recipes it appears in
    for stem in sorted(stems_in_folio):
        other_matched = []
        for fol in stem_folios[stem]['folios']:
            if fol != folio and fol in ALL_MATCHED:
                other_matched.append(f"{fol}={ALL_MATCHED[fol]}")
        
        # If stem also appears in other folios, find intersection of recipes' ingredients
        other_recipes = set()
        for fol in stem_folios[stem]['folios']:
            if fol != folio and fol in ALL_MATCHED:
                other_recipes.add(ALL_MATCHED[fol])
        
        # Candidate ingredients = in THIS recipe AND in ALL other recipes where stem appears
        candidates = set(recipe_ings)
        for r in other_recipes:
            candidates &= recipe_ingredients.get(r, set())
        
        # Remove already identified
        candidates -= already_identified
        
        n_other = len(stem_folios[stem]['folios']) - 1
        if candidates:
            print(f"    {stem:25s} ({n_other} other folios) -> "
                  f"{len(candidates)} candidates: {sorted(candidates)}")


# ============================================================
# ANALYSIS 2: Opium/Castoreum cluster
# ============================================================
print("\n\n" + "=" * 80)
print("ANALYSIS 2: OPIUM/CASTOREUM DISAMBIGUATION")
print("=" * 80)

# Opium is in: Trifera Magna, Diascordium, Aurea Alex, Philonium Persicum (NOT Confectio Hamech, Diamargariton, Diaciminum, Pillulae Aureae, Ung.Apostolorum)
# Castoreum is in: Trifera Magna, Diascordium, Aurea Alex, Philonium Persicum (NOT Confectio Hamech, Diamargariton, Diaciminum, Pillulae Aureae, Ung.Apostolorum)
# They have IDENTICAL profiles! Cannot disambiguate by recipe matching alone.

opium_recipes = set()
castoreum_recipes = set()
for rname, ings in recipe_ingredients.items():
    if 'Opium' in ings:
        opium_recipes.add(rname)
    if 'Castoreum' in ings:
        castoreum_recipes.add(rname)

print(f"\nOpium in recipes: {sorted(opium_recipes)}")
print(f"Castoreum in recipes: {sorted(castoreum_recipes)}")
print(f"Difference (Opium-Castoreum): {opium_recipes - castoreum_recipes}")
print(f"Difference (Castoreum-Opium): {castoreum_recipes - opium_recipes}")

# Opium appears in Requies Magna but NOT Castoreum
# Castoreum in Pillulae Fetidae but NOT Opium
# These are NOT in our matched folios yet, so we can't use them directly.

# However, we CAN look at which AMBIGUOUS stems have Opium vs Castoreum as tied:
print("\nStems where Opium and Castoreum are co-tied as top candidates:")
v3_results = {}
with open(os.path.join(BASE, 'voynich_constraint_solver_v3_results.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        v3_results[row['Stem']] = row

opium_castoreum_stems = []
for stem, v3 in v3_results.items():
    if stem in confirmed_ingredients:
        continue
    cands = v3['All_Candidates']
    if 'Opium' in cands and 'Castoreum' in cands:
        opium_castoreum_stems.append(stem)

print(f"  Count: {len(opium_castoreum_stems)}")
print("  These stems likely represent ingredients in the Opium/Castoreum/Piper longum cluster")
print("  (all present in Trifera+Diascordium+Philonium+Aurea Alex)")
print("  Cannot disambiguate with current recipe set -- need Requies Magna or Pillulae Fetidae folios")


# ============================================================
# ANALYSIS 3: Zingiber targeting
# ============================================================
print("\n\n" + "=" * 80)
print("ANALYSIS 3: ZINGIBER TARGETING")
print("=" * 80)
print("\nZingiber is in 6 matched recipes: Confectio Hamech, Trifera, Diascordium,")
print("Diaciminum, Aurea Alex, Philonium Persicum")
print("But NOT in: Unguentum Apostolorum, Pillulae Aureae, Diamargariton")
print("This is a distinctive profile -- not identical to Cinnamomum (which IS in Diamargariton)")

zingiber_profile_positive = {'Confectio Hamech', 'Trifera Magna', 'Diascordium', 
                              'Diaciminum', 'Aurea Alexandrina', 'Philonium Persicum'}
zingiber_profile_negative = {'Unguentum Apostolorum', 'Pillulae Aureae', 'Diamargariton'}

print("\nStems with Zingiber as top candidate in v3 (AMBIGUOUS):")
for stem, v3 in v3_results.items():
    if stem in confirmed_ingredients:
        continue
    if v3['Best_Candidate'] == 'Zingiber':
        present = set(v3['Present_Recipes'].split(', '))
        absent = set(v3['Absent_Recipes'].split(', '))
        
        # Check if present recipes are subset of Zingiber's recipes
        zing_match = present <= zingiber_profile_positive
        zing_absent_match = zingiber_profile_negative <= absent
        
        n_fol = len(stem_folios.get(stem, {}).get('folios', []))
        label = ""
        if zing_match and zing_absent_match:
            label = " ** PERFECT ZINGIBER PROFILE **"
        elif zing_match:
            label = " (positive match)"
        
        print(f"  {stem:25s} present_in={list(present)[:3]}... absent_from={v3['N_Absent']} "
              f"folios={n_fol}{label}")


# ============================================================
# ANALYSIS 4: Most constrained unidentified stems
# ============================================================
print("\n\n" + "=" * 80)
print("ANALYSIS 4: MOST CONSTRAINED UNIDENTIFIED STEMS")
print("=" * 80)
print("\nStems appearing in the MOST diverse set of matched recipes (highest constraint power):\n")

# For each unidentified stem, calculate: how many DIFFERENT recipes does it map to?
stem_recipe_diversity = {}
for stem, data in stem_folios.items():
    if stem in confirmed_ingredients:
        continue
    recipes_set = set()
    for fol in data['folios']:
        if fol in ALL_MATCHED:
            recipes_set.add(ALL_MATCHED[fol])
    if len(recipes_set) >= 3:
        # Calculate candidate intersection
        candidates = None
        for r in recipes_set:
            r_ings = recipe_ingredients.get(r, set())
            if candidates is None:
                candidates = set(r_ings)
            else:
                candidates &= r_ings
        candidates -= already_identified
        
        stem_recipe_diversity[stem] = {
            'n_recipes': len(recipes_set),
            'recipes': recipes_set,
            'candidates': candidates,
            'n_folios': len(data['folios']),
        }

# Sort by fewest candidates (most constrained)
ranked = sorted(stem_recipe_diversity.items(), 
                key=lambda x: (len(x[1]['candidates']), -x[1]['n_recipes']))

print(f"{'Stem':25s} {'Recipes':>7s} {'Folios':>6s} {'Cand':>4s} Candidates")
print("-" * 100)
for stem, info in ranked[:30]:
    cands = sorted(info['candidates'])[:5]
    cand_str = ', '.join(cands)
    if len(info['candidates']) > 5:
        cand_str += f' +{len(info["candidates"])-5} more'
    print(f"{stem:25s} {info['n_recipes']:>7d} {info['n_folios']:>6d} {len(info['candidates']):>4d} {cand_str}")


# ============================================================
# ANALYSIS 5: Quick summary of progress
# ============================================================
print("\n\n" + "=" * 80)
print("PROGRESS SUMMARY")
print("=" * 80)

total_stems_tracked = len(stem_folios)
identified_stems = sum(1 for s in stem_folios if s in confirmed_ingredients)
function_stems = sum(1 for s in stem_folios if s in {'B1A3', 'K1A1', 'K1J1A1', 'C2A3', 'BaA3', 'Q1J1A1'})

print(f"\nStems tracked (appear in 2+ matched folios): {total_stems_tracked}")
print(f"Stems identified (ingredient assigned): {identified_stems} ({100*identified_stems/total_stems_tracked:.1f}%)")
print(f"Stems classified as function words: {function_stems}")
print(f"Stems unresolved: {total_stems_tracked - identified_stems - function_stems}")
print(f"\nUnique ingredients identified: {len(already_identified)}")
print(f"Total ingredients in all matched recipes: ~123")
print(f"Coverage: {len(already_identified)}/123 = {100*len(already_identified)/123:.1f}%")
