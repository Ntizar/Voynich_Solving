#!/usr/bin/env python3
"""
VOYNICH SOLVER v4c: ZINGIBER/MEL DISAMBIGUATION + FINAL TABLE
===============================================================
Key insight from v4b: 5 stems reduce to exactly {Mel despumatum, Zingiber}.
Discriminator: Mel despumatum is in 6/9 matched recipes, Zingiber in 6/9 but DIFFERENT ones.

Mel despumatum: Confectio Hamech, Trifera, Diascordium, Diaciminum, Aurea Alex, Philonium Persicum
                NOT in: Ung.Apostolorum, Pillulae Aureae, Diamargariton
Zingiber:       Confectio Hamech, Trifera, Diascordium, Diaciminum, Aurea Alex, Philonium Persicum
                NOT in: Ung.Apostolorum, Pillulae Aureae, Diamargariton

Wait -- they have IDENTICAL profiles in our 9 matched recipes!
Both are in the same 6 and absent from the same 3.
So they cannot be disambiguated by recipe matching.
We need MORPHOLOGICAL or FREQUENCY analysis.

However: we CAN identify the Zingiber/Mel PAIR and mark them as a group.
Also: Galanga/Cubeba/Nux moschata cluster for Diamargariton-exclusive stems.

This script produces the FINAL identification table v4c.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import csv
import os
from collections import defaultdict

BASE = r'C:\Ntizar_Obsidian\Ntizar_Brain\MASTERTMIND'

# Load all identifications from v4
v4_ids = {}
with open(os.path.join(BASE, 'voynich_unified_identifications_v4.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        v4_ids[row['Stem']] = row

# Load recipe data
recipe_ingredients = defaultdict(set)
ingredient_category = {}
with open(os.path.join(BASE, 'recetas_historicas_ingredientes_flat.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        rname = row['Receta'].split('(')[0].strip()
        ing = row['Ingrediente_Normalizado']
        recipe_ingredients[rname].add(ing)
        ingredient_category[ing] = row['Categoria']

# Load stem folios
stem_folios = {}
with open(os.path.join(BASE, 'voynich_stems_in_matched_folios.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        stem = row['Stem']
        folios = [x.strip() for x in row['Matched_Folios'].split('|')]
        stem_folios[stem] = {'type': row['Type'], 'folios': folios}

# Load v3 results
v3_results = {}
with open(os.path.join(BASE, 'voynich_constraint_solver_v3_results.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        v3_results[row['Stem']] = row

print("=" * 80)
print("VOYNICH SOLVER v4c: FINAL UNIFIED TABLE")
print("=" * 80)

# ============================================================
# NEW IDENTIFICATIONS
# ============================================================

new_ids = []

# 1. Zingiber/Mel despumatum PAIR
# Stems that reduce to exactly {Zingiber, Mel despumatum}:
# Q1A1, Q2A1, Q2K1A1, U1A1, U2A1
# These have identical recipe profiles -- CANNOT be separated.
# However, we KNOW both exist. Best approach: group them.

# Check which of these stems appear in f93v (Diascordium) -- both Z and M are in Diascordium
# Check which appear in f87r (Confectio Hamech) -- both Z and M are in Confectio Hamech
# So recipe profiles are identical.

# Morphological approach: 
# Q1A1, Q2A1 share "Q_A1" pattern
# Q2K1A1 has Q2+K1+A1
# U1A1, U2A1 share "U_A1" pattern
# Maybe the U-prefix = Mel (liquid/base) and Q-prefix = Zingiber (spice)?
# This is speculative but noteworthy.

MEL_ZINGIBER_PAIR = ['Q1A1', 'Q2A1', 'Q2K1A1', 'U1A1', 'U2A1']
for stem in MEL_ZINGIBER_PAIR:
    new_ids.append({
        'Stem': stem,
        'Ingredient': 'Zingiber|Mel despumatum',
        'Confidence': 85,
        'Tier': 3,
        'Source': 'elimination_to_pair',
        'Reasoning': 'Reduced to exactly 2 candidates with identical recipe profiles. Both are present in same 6 recipes and absent from same 3. Cannot disambiguate further without morphological/frequency analysis.'
    })

print(f"\n1. Zingiber/Mel despumatum PAIR: {len(MEL_ZINGIBER_PAIR)} stems")
for s in MEL_ZINGIBER_PAIR:
    n_fol = len(stem_folios.get(s, {}).get('folios', []))
    print(f"   {s:20s} ({n_fol} folios)")

# 2. Galanga/Cubeba/Nux moschata cluster (Diamargariton exclusive)
# Stems K1A1B2B1A3 and T1A1 reduce to {Galanga, Cubeba, Nux moschata}
# All three are in Diamargariton + Trifera Magna but NOT in other recipes.
GALANGA_CLUSTER = ['K1A1B2B1A3', 'T1A1']
for stem in GALANGA_CLUSTER:
    new_ids.append({
        'Stem': stem,
        'Ingredient': 'Galanga|Cubeba|Nux moschata',
        'Confidence': 75,
        'Tier': 4,
        'Source': 'diamargariton_exclusive',
        'Reasoning': 'Only in Diamargariton+Trifera. After eliminating Cardamomum, Casia, Crocus, Cinnamomum, only Galanga/Cubeba/Nux moschata remain. These 3 have identical recipe profiles.'
    })

print(f"\n2. Galanga/Cubeba/Nux moschata cluster: {len(GALANGA_CLUSTER)} stems")
for s in GALANGA_CLUSTER:
    print(f"   {s}")

# 3. NEW function words discovered by v4b (0 candidates after intersection)
NEW_FUNCTION_WORDS = {
    'C2A1': '14 folios, 8 recipes. Zero candidates after intersection. Grammatical marker.',
    'A1Q1J1A1': '12 folios, 6 recipes. Zero candidates. Likely structural word.',
    'U2J1A1': '10 folios, 6 recipes. Zero candidates. Likely structural/measurement word.',
    'A1Q2A3': '16 folios, 5 recipes. Zero candidates. High frequency structural word.',
    'D1A1Q1J1A1': '14 folios, 5 recipes. Zero candidates. Complex stem, structural.',
    'A1B1A3': '13 folios, 5 recipes. Zero candidates after intersection.',
    'L1J1A1': '18 folios, 5 recipes. Zero candidates. Structural word.',
    'L1A1': '18 folios, 6 recipes. Zero candidates. Structural word.',
}

for stem, reason in NEW_FUNCTION_WORDS.items():
    new_ids.append({
        'Stem': stem,
        'Ingredient': 'FUNCTION_WORD',
        'Confidence': 90,
        'Tier': 0,
        'Source': 'intersection_empty',
        'Reasoning': reason
    })

print(f"\n3. NEW function words: {len(NEW_FUNCTION_WORDS)} stems")

# 4. Castoreum/Opium/Zingiber/Mel cluster (4 candidates)
# Many stems reduce to {Castoreum, Opium, Zingiber, Mel despumatum}
# These have nearly identical profiles in our recipe set.
# Mark as a semantic cluster.
OPIUM_CLUSTER_STEMS = []
for stem, v3 in v3_results.items():
    if stem in v4_ids:
        continue
    if stem in NEW_FUNCTION_WORDS:
        continue
    if stem in MEL_ZINGIBER_PAIR:
        continue
    cands_raw = v3['All_Candidates']
    cands = [c.strip().split('(')[0].strip() for c in cands_raw.split('|')]
    # After removing already identified
    already_id = set(r['Ingredient'] for r in v4_ids.values()) | {'Zingiber', 'Mel despumatum'}
    remaining = [c for c in cands if c not in already_id or c in ('Zingiber', 'Mel despumatum', 'Castoreum', 'Opium')]
    
    # Check if stem maps to the Opium/Castoreum/Zingiber/Mel cluster
    cluster = {'Opium', 'Castoreum', 'Zingiber', 'Mel despumatum'}
    cand_set = set(cands)
    if cand_set >= {'Opium', 'Castoreum'} and len(cand_set) <= 6:
        OPIUM_CLUSTER_STEMS.append(stem)

print(f"\n4. Opium/Castoreum/Zingiber/Mel cluster: {len(OPIUM_CLUSTER_STEMS)} stems")
print("   (Cannot disambiguate without Requies Magna or Pillulae Fetidae folios)")

# ============================================================
# CONSOLIDATE ALL IDENTIFICATIONS
# ============================================================
print("\n" + "=" * 80)
print("CONSOLIDATED IDENTIFICATION TABLE v4c")
print("=" * 80)

all_results = []

# Add v4 identifications
for stem, row in v4_ids.items():
    all_results.append({
        'Stem': stem,
        'Ingredient': row['Ingredient'],
        'Confidence': int(row['Confidence']),
        'Tier': int(row['Tier']),
        'Source': row['Source'],
        'Reasoning': row['Reasoning'],
    })

# Add new v4c identifications
for item in new_ids:
    all_results.append(item)

# Sort
all_results.sort(key=lambda x: (x['Tier'], -x['Confidence']))

# Stats
ingredient_stems = defaultdict(list)
function_count = 0
for r in all_results:
    if r['Ingredient'] == 'FUNCTION_WORD':
        function_count += 1
    else:
        ingredient_stems[r['Ingredient']].append(r['Stem'])

unique_single = set()
unique_pair = set()
for ing in ingredient_stems:
    if '|' in ing:
        for i in ing.split('|'):
            unique_pair.add(i.strip())
    else:
        unique_single.add(ing)

print(f"\n--- SUMMARY ---")
print(f"Total entries: {len(all_results)}")
print(f"  Function words: {function_count}")
print(f"  Single-ingredient IDs: {sum(1 for r in all_results if r['Ingredient'] != 'FUNCTION_WORD' and '|' not in r['Ingredient'])}")
print(f"  Pair/cluster IDs: {sum(1 for r in all_results if '|' in r['Ingredient'])}")
print(f"  Unique ingredients (single): {len(unique_single)}")
print(f"  Additional ingredients (in pairs): {len(unique_pair - unique_single)}")
print(f"  TOTAL unique ingredients touched: {len(unique_single | unique_pair)}")

print(f"\n--- TIER BREAKDOWN ---")
for tier in sorted(set(r['Tier'] for r in all_results)):
    tier_items = [r for r in all_results if r['Tier'] == tier]
    tier_label = {0: 'Function Words', 1: 'Confirmed', 2: 'High', 3: 'Strong', 4: 'Moderate'}
    print(f"  Tier {tier} ({tier_label.get(tier, '?')}): {len(tier_items)} entries")

# Print full table
print(f"\n{'Stem':25s} {'Ingredient':28s} {'Conf':>4s} {'Tier':>4s} {'Source':25s}")
print("-" * 95)
for r in all_results:
    ing_display = r['Ingredient'][:28]
    print(f"{r['Stem']:25s} {ing_display:28s} {r['Confidence']:>4d} {r['Tier']:>4d} {r['Source']:25s}")

# Write CSV
out_path = os.path.join(BASE, 'voynich_unified_identifications_v4c.csv')
with open(out_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['Stem', 'Ingredient', 'Confidence', 'Tier', 'Source', 'Reasoning'])
    writer.writeheader()
    for r in all_results:
        writer.writerow(r)

print(f"\nSaved to: {out_path}")

# ============================================================
# INGREDIENT DICTIONARY
# ============================================================
print("\n" + "=" * 80)
print("INGREDIENT DICTIONARY (sorted by confidence)")
print("=" * 80)

for ing in sorted(ingredient_stems.keys(), key=lambda x: -max(r['Confidence'] for r in all_results if r['Ingredient'] == x)):
    stems = ingredient_stems[ing]
    max_conf = max(r['Confidence'] for r in all_results if r['Ingredient'] == ing)
    cat = ingredient_category.get(ing.split('|')[0].strip(), '?')
    print(f"\n  [{cat:8s}] {ing}")
    print(f"    Max confidence: {max_conf}%")
    print(f"    Stems ({len(stems)}): {', '.join(sorted(stems))}")
    
    # Which matched folios contain these stems?
    fol_set = set()
    for s in stems:
        if s in stem_folios:
            fol_set.update(stem_folios[s]['folios'])
    if fol_set:
        print(f"    Appears in folios: {', '.join(sorted(fol_set)[:10])}")

# ============================================================  
# COVERAGE ANALYSIS
# ============================================================
print("\n" + "=" * 80)
print("COVERAGE ANALYSIS PER RECIPE")
print("=" * 80)

PERFECT_MATCHES = {
    'f87r': 'Confectio Hamech',
    'f87v': 'Unguentum Apostolorum',
    'f88r': 'Trifera Magna',
    'f93v': 'Diascordium',
    'f96v': 'Pillulae Aureae',
    'f100r': 'Diamargariton',
    'f100v': 'Diaciminum',
}

all_identified_ings = unique_single | unique_pair

for folio, recipe in PERFECT_MATCHES.items():
    ings = recipe_ingredients.get(recipe, set())
    covered = ings & all_identified_ings
    pct = 100 * len(covered) / len(ings) if ings else 0
    print(f"\n  {folio} = {recipe}: {len(covered)}/{len(ings)} ingredients covered ({pct:.0f}%)")
    for ing in sorted(covered):
        print(f"    [OK] {ing}")
    for ing in sorted(ings - covered):
        print(f"    [??] {ing}")
