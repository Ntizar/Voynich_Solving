#!/usr/bin/env python3
"""
Session 12 - Step 1: Update v5->v6 identifications + re-run matching + search Zingiber
1. Update 5 Zingiber|Mel stems to Mel despumatum (41-0 deadlock verdict)
2. Re-run content-based matching with v6
3. Search for NEW Zingiber candidate stems
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import csv
import re
from collections import defaultdict

# ============================================================
# STEP 1: Create v6 identification table
# ============================================================
print("=" * 70)
print("STEP 1: Updating identification table v5 -> v6")
print("=" * 70)

# Read v5
v5_rows = []
with open('voynich_unified_identifications_v5.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        v5_rows.append(row)

# The 5 stems to update
mel_stems = {'Q1A1', 'Q2A1', 'Q2K1A1', 'U1A1', 'U2A1'}

v6_rows = []
updated_count = 0
for row in v5_rows:
    if row['Stem'] in mel_stems:
        row['Ingredient'] = 'Mel despumatum'
        row['Confidence'] = '88'
        row['Source'] = 'deadlock_zingiber_mel_broken'
        row['Reasoning'] = (
            'Zingiber|Mel deadlock BROKEN: 41 folios favor Mel, 0 favor Zingiber, '
            '6 tied. Using 2 Zingiber-only recipes (Benedicta Laxativa, Elec. de Succo Rosarum) '
            'vs 4 Mel-only recipes (Hiera Picra, Theriac Diatessaron, Theriac Diatessaron Magna, '
            'Tiryaq al-Arba). Overwhelming statistical signal.'
        )
        updated_count += 1
    v6_rows.append(row)

# Write v6
with open('voynich_unified_identifications_v6.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(v6_rows)

print(f"  Updated {updated_count} stems from Zingiber|Mel -> Mel despumatum")
print(f"  Written to voynich_unified_identifications_v6.csv")

# Summary of v6
tier_counts = defaultdict(int)
ingredient_counts = defaultdict(int)
for row in v6_rows:
    tier_counts[int(row['Tier'])] += 1
    ingredient_counts[row['Ingredient']] += 1

print(f"\n  v6 Summary: {len(v6_rows)} entries")
for t in sorted(tier_counts.keys()):
    print(f"    Tier {t}: {tier_counts[t]} entries")
print(f"\n  Unique ingredients: {len(ingredient_counts)}")
for ing, cnt in sorted(ingredient_counts.items(), key=lambda x: -x[1]):
    print(f"    {ing}: {cnt} stems")

# ============================================================
# STEP 2: Re-run content-based matching with v6
# ============================================================
print("\n" + "=" * 70)
print("STEP 2: Content-based matching with v6 identifications")
print("=" * 70)

# Load v6 identifications (skip tier 0 = function words)
id_map = {}  # stem -> ingredient
for row in v6_rows:
    if int(row['Tier']) > 0:
        stem = row['Stem']
        ing = row['Ingredient']
        # Handle remaining pairs (Galanga|Cubeba|Nux moschata)
        if '|' in ing:
            ingredients = [x.strip() for x in ing.split('|')]
            for i in ingredients:
                id_map.setdefault(stem, []).append(i) if isinstance(id_map.get(stem), list) else None
            if stem not in id_map:
                id_map[stem] = ingredients
        else:
            id_map[stem] = ing

# Load recipe ingredients
recipe_ingredients = defaultdict(set)
with open('recetas_historicas_ingredientes_flat.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        recipe_ingredients[row['Receta']].add(row['Ingrediente_Normalizado'])

# Load corpus
def split_atom(word):
    return re.findall(r'[A-Z][a-z0-9]*', word)

def extract_stem(word):
    atoms = split_atom(word)
    if len(atoms) < 2:
        return word, ''
    return ''.join(atoms[:-1]), atoms[-1]

folio_stems = defaultdict(set)
current_folio = None

with open('voynich_sta.txt', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        
        # Check for folio header
        header_match = re.match(r'<(f\d+[rv]\d*)>', line)
        if header_match:
            raw = header_match.group(1)
            current_folio = re.sub(r'^(f\d+[rv])\d+$', r'\1', raw)
            continue
        
        if '<!>' in line or '<!' in line:
            continue
        
        # Content line
        content_match = re.search(r'<(f\d+[rv]\d*)', line)
        if content_match:
            raw = content_match.group(1)
            current_folio = re.sub(r'^(f\d+[rv])\d+$', r'\1', raw)
        
        if current_folio is None:
            continue
        
        # Extract tokens
        text_part = re.sub(r'<[^>]*>', '', line)
        tokens = re.findall(r'[A-Z][A-Za-z0-9]+', text_part)
        
        for token in tokens:
            stem, final = extract_stem(token)
            if stem and len(split_atom(stem)) >= 1:
                folio_stems[current_folio].add(stem)

# Filter to recipe folios (f87+ range)
recipe_folios = {f: stems for f, stems in folio_stems.items() 
                 if re.match(r'f(8[7-9]|9\d|1[01]\d)', f)}

print(f"  Loaded {len(recipe_folios)} recipe folios, {len(recipe_ingredients)} recipes")

# For each folio, find which identified ingredients are present
def get_folio_ingredients(folio):
    """Get the set of identified ingredients present in a folio."""
    stems = folio_stems.get(folio, set())
    ingredients = set()
    for stem in stems:
        if stem in id_map:
            val = id_map[stem]
            if isinstance(val, list):
                for v in val:
                    ingredients.add(v)
            else:
                ingredients.add(val)
    return ingredients

# Compute F1 between folio ingredient set and recipe ingredient set
def compute_f1(folio_ings, recipe_ings):
    if not folio_ings or not recipe_ings:
        return 0.0
    overlap = folio_ings & recipe_ings
    if not overlap:
        return 0.0
    precision = len(overlap) / len(folio_ings)
    recall = len(overlap) / len(recipe_ings)
    f1 = 2 * precision * recall / (precision + recall)
    return f1 * 100

# Match each recipe folio against all recipes
results = []
for folio in sorted(recipe_folios.keys(), key=lambda x: (int(re.search(r'\d+', x).group()), x)):
    folio_ings = get_folio_ingredients(folio)
    
    if not folio_ings:
        results.append({
            'Folio': folio,
            'N_Identified': 0,
            'Identified_Ingredients': '',
            'Best_Recipe': '',
            'Best_F1': 0.0,
            'Best_Overlap': 0,
            'Best_Precision': 0.0,
            'Best_Recall': 0.0,
            'Top5_Recipes': ''
        })
        continue
    
    scores = []
    for recipe, r_ings in recipe_ingredients.items():
        f1 = compute_f1(folio_ings, r_ings)
        overlap = folio_ings & r_ings
        prec = len(overlap) / len(folio_ings) * 100 if folio_ings else 0
        rec = len(overlap) / len(r_ings) * 100 if r_ings else 0
        scores.append((recipe, f1, len(overlap), prec, rec, overlap))
    
    scores.sort(key=lambda x: -x[1])
    best = scores[0]
    top5 = '; '.join([f"{s[0]}({s[1]:.1f}%)" for s in scores[:5]])
    
    results.append({
        'Folio': folio,
        'N_Identified': len(folio_ings),
        'Identified_Ingredients': '|'.join(sorted(folio_ings)),
        'Best_Recipe': best[0],
        'Best_F1': best[1],
        'Best_Overlap': best[2],
        'Best_Precision': best[3],
        'Best_Recall': best[4],
        'Top5_Recipes': top5
    })

# Write results
match_fields = ['Folio', 'N_Identified', 'Identified_Ingredients', 'Best_Recipe', 
                'Best_F1', 'Best_Overlap', 'Best_Precision', 'Best_Recall', 'Top5_Recipes']
with open('voynich_matching_v6.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=match_fields)
    writer.writeheader()
    writer.writerows(results)

# Summary statistics
f1_values = [r['Best_F1'] for r in results if r['Best_F1'] > 0]
excellent = sum(1 for f in f1_values if f >= 80)
good = sum(1 for f in f1_values if 50 <= f < 80)
moderate = sum(1 for f in f1_values if 30 <= f < 50)
weak = sum(1 for f in f1_values if 0 < f < 30)
insufficient = sum(1 for r in results if r['Best_F1'] == 0)

print(f"\n  MATCHING v6 RESULTS:")
print(f"    Total folios: {len(results)}")
print(f"    EXCELLENT (F1>=80%): {excellent}")
print(f"    GOOD (F1 50-80%): {good}")
print(f"    MODERATE (F1 30-50%): {moderate}")
print(f"    WEAK (F1 <30%): {weak}")
print(f"    INSUFFICIENT (no identified ingredients): {insufficient}")
print(f"    Mean F1 (non-zero): {sum(f1_values)/len(f1_values):.1f}%" if f1_values else "    N/A")

# Compare with v3 (the previous matching)
print("\n  Top matches per folio:")
for r in results:
    if r['Best_F1'] > 0:
        quality = "EXCELLENT" if r['Best_F1'] >= 80 else "GOOD" if r['Best_F1'] >= 50 else "MODERATE" if r['Best_F1'] >= 30 else "WEAK"
        print(f"    {r['Folio']:8s} -> {r['Best_Recipe'][:45]:45s} F1={r['Best_F1']:.1f}% [{quality}]")

# Also write full matrix (all folio x recipe F1 scores)
print("\n  Writing full matching matrix...")
full_results = []
for folio in sorted(recipe_folios.keys(), key=lambda x: (int(re.search(r'\d+', x).group()), x)):
    folio_ings = get_folio_ingredients(folio)
    for recipe, r_ings in recipe_ingredients.items():
        f1 = compute_f1(folio_ings, r_ings)
        overlap = folio_ings & r_ings
        full_results.append({
            'Folio': folio,
            'Recipe': recipe,
            'F1': round(f1, 1),
            'Overlap': len(overlap),
            'Folio_N': len(folio_ings),
            'Recipe_N': len(r_ings),
            'Overlap_Ingredients': '|'.join(sorted(overlap)) if overlap else ''
        })

with open('voynich_expanded_matching_v6.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['Folio', 'Recipe', 'F1', 'Overlap', 'Folio_N', 'Recipe_N', 'Overlap_Ingredients'])
    writer.writeheader()
    writer.writerows(full_results)

# Write top 5 per folio 
top5_results = []
for folio in sorted(recipe_folios.keys(), key=lambda x: (int(re.search(r'\d+', x).group()), x)):
    folio_ings = get_folio_ingredients(folio)
    scores = []
    for recipe, r_ings in recipe_ingredients.items():
        f1 = compute_f1(folio_ings, r_ings)
        overlap = folio_ings & r_ings
        scores.append((recipe, f1, len(overlap), overlap))
    scores.sort(key=lambda x: -x[1])
    for rank, (recipe, f1, n_overlap, overlap_set) in enumerate(scores[:5], 1):
        top5_results.append({
            'Folio': folio,
            'Rank': rank,
            'Recipe': recipe,
            'F1': round(f1, 1),
            'N_Overlap': n_overlap,
            'Overlap_Ingredients': '|'.join(sorted(overlap_set)) if overlap_set else ''
        })

with open('voynich_matching_v6_top5.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['Folio', 'Rank', 'Recipe', 'F1', 'N_Overlap', 'Overlap_Ingredients'])
    writer.writeheader()
    writer.writerows(top5_results)

print(f"  Written: voynich_matching_v6.csv, voynich_expanded_matching_v6.csv, voynich_matching_v6_top5.csv")

# ============================================================
# STEP 3: Search for NEW Zingiber candidate stems
# ============================================================
print("\n" + "=" * 70)
print("STEP 3: Searching for NEW Zingiber candidate stems")
print("=" * 70)

# Strategy: Find stems that appear in Zingiber-containing recipes but NOT in Mel-only recipes
# Zingiber appears in many recipes. We need stems that:
# 1. Appear in folios matching Zingiber-containing recipes
# 2. Do NOT already have an identification
# 3. Have a pattern consistent with being a single ingredient

# Zingiber-only recipes (have Zingiber but NOT Mel):
# Benedicta Laxativa (has Zingiber + Saccharum, no Mel)
# Electuarium de Succo Rosarum (has Zingiber + Saccharum, no Mel)
# Confectio Hamech (has Zingiber + Saccharum + Mel) -- has both, skip
# Diasatyrion (has Zingiber + Saccharum + Mel) -- has both, skip

# Let's be more systematic: find recipes with Zingiber
zing_recipes = set()
mel_recipes = set()
for recipe, ings in recipe_ingredients.items():
    if 'Zingiber' in ings:
        zing_recipes.add(recipe)
    if 'Mel despumatum' in ings:
        mel_recipes.add(recipe)

zing_only_recipes = zing_recipes - mel_recipes
mel_only_recipes = mel_recipes - zing_recipes
both_recipes = zing_recipes & mel_recipes

print(f"  Zingiber-only recipes ({len(zing_only_recipes)}): {zing_only_recipes}")
print(f"  Mel-only recipes ({len(mel_only_recipes)}): {mel_only_recipes}")
print(f"  Both Zingiber+Mel recipes ({len(both_recipes)}): {len(both_recipes)} recipes")

# Strategy: A Zingiber stem should appear more in folios matching Zingiber recipes 
# than in folios matching non-Zingiber recipes.
# More specifically: look at unidentified stems and check their presence pattern.

# Get all identified stems (to exclude)
identified_stems = set(id_map.keys())
# Also exclude function words
function_stems = set()
for row in v6_rows:
    if row['Ingredient'] == 'FUNCTION_WORD':
        function_stems.add(row['Stem'])
identified_stems |= function_stems

# For each unidentified stem, count how many Zingiber-recipe folios it appears in
# vs non-Zingiber-recipe folios
# First, determine which folios best-match to Zingiber vs non-Zingiber recipes
folio_best_recipe = {}
for r in results:
    if r['Best_F1'] > 0:
        folio_best_recipe[r['Folio']] = r['Best_Recipe']

# Alternative approach: for each stem, count presence in:
# a) Folios whose best match is a Zingiber-containing recipe
# b) Folios whose best match is NOT a Zingiber-containing recipe

zing_folios = set()
non_zing_folios = set()
for folio, recipe in folio_best_recipe.items():
    if recipe in zing_recipes:
        zing_folios.add(folio)
    else:
        non_zing_folios.add(folio)

print(f"\n  Folios matching Zingiber recipes: {len(zing_folios)}")
print(f"  Folios matching non-Zingiber recipes: {len(non_zing_folios)}")

# For each unidentified stem, compute enrichment
import math

stem_zing_counts = defaultdict(int)
stem_nonzing_counts = defaultdict(int)
stem_total = defaultdict(int)

for folio, stems in recipe_folios.items():
    for stem in stems:
        if stem in identified_stems:
            continue
        stem_total[stem] += 1
        if folio in zing_folios:
            stem_zing_counts[stem] += 1
        elif folio in non_zing_folios:
            stem_nonzing_counts[stem] += 1

# Filter: stem must appear in at least 3 Zingiber folios
zing_candidates = []
n_zing = len(zing_folios) if zing_folios else 1
n_nonzing = len(non_zing_folios) if non_zing_folios else 1

for stem in stem_total:
    if stem_total[stem] < 3:
        continue
    z = stem_zing_counts.get(stem, 0)
    nz = stem_nonzing_counts.get(stem, 0)
    
    # Enrichment ratio 
    rate_zing = z / n_zing
    rate_nonzing = nz / n_nonzing if n_nonzing > 0 else 0
    
    if rate_zing > 0 and rate_nonzing > 0:
        log_or = math.log(rate_zing / rate_nonzing)
    elif rate_zing > 0:
        log_or = 3.0  # strong enrichment
    else:
        log_or = -3.0
    
    zing_candidates.append({
        'Stem': stem,
        'In_Zing_Folios': z,
        'In_NonZing_Folios': nz,
        'Total_Folios': stem_total[stem],
        'Rate_Zing': round(rate_zing, 4),
        'Rate_NonZing': round(rate_nonzing, 4),
        'LogOR': round(log_or, 3),
        'Atoms': '|'.join(split_atom(stem)),
        'Length': len(split_atom(stem))
    })

# Sort by LogOR descending (most enriched in Zingiber folios)
zing_candidates.sort(key=lambda x: -x['LogOR'])

# Write all candidates
with open('voynich_zingiber_candidates.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['Stem', 'In_Zing_Folios', 'In_NonZing_Folios', 
                                            'Total_Folios', 'Rate_Zing', 'Rate_NonZing', 
                                            'LogOR', 'Atoms', 'Length'])
    writer.writeheader()
    writer.writerows(zing_candidates)

# Show top Zingiber-enriched stems
print(f"\n  TOP 30 Zingiber-enriched unidentified stems:")
print(f"  {'Stem':<25s} {'Zing':>5s} {'NonZ':>5s} {'Total':>5s} {'LogOR':>7s} {'Atoms'}")
for c in zing_candidates[:30]:
    print(f"  {c['Stem']:<25s} {c['In_Zing_Folios']:5d} {c['In_NonZing_Folios']:5d} {c['Total_Folios']:5d} {c['LogOR']:7.3f} {c['Atoms']}")

# ============================================================
# STEP 4: Compare v3 vs v6 matching improvements
# ============================================================
print("\n" + "=" * 70)
print("STEP 4: v3 vs v6 matching comparison")
print("=" * 70)

# Load v3 results for comparison
v3_results = {}
try:
    with open('voynich_matching_v3_top5.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row['Rank']) == 1:
                v3_results[row['Folio']] = float(row['F1'])
except:
    print("  Could not load v3 results for comparison")

if v3_results:
    improvements = []
    for r in results:
        folio = r['Folio']
        v6_f1 = r['Best_F1']
        v3_f1 = v3_results.get(folio, 0)
        delta = v6_f1 - v3_f1
        improvements.append((folio, v3_f1, v6_f1, delta))
    
    improvements.sort(key=lambda x: -x[3])
    
    print(f"\n  Folios with IMPROVED matching (v6 vs v3):")
    improved = [(f, v3, v6, d) for f, v3, v6, d in improvements if d > 0.5]
    for f, v3, v6, d in improved[:20]:
        print(f"    {f:8s}: v3={v3:.1f}% -> v6={v6:.1f}% (+{d:.1f}%)")
    
    worsened = [(f, v3, v6, d) for f, v3, v6, d in improvements if d < -0.5]
    if worsened:
        print(f"\n  Folios with WORSENED matching:")
        for f, v3, v6, d in sorted(worsened, key=lambda x: x[3])[:10]:
            print(f"    {f:8s}: v3={v3:.1f}% -> v6={v6:.1f}% ({d:.1f}%)")
    
    mean_v3 = sum(v3_results.values()) / len(v3_results) if v3_results else 0
    mean_v6 = sum(f1_values) / len(f1_values) if f1_values else 0
    print(f"\n  OVERALL: Mean F1 v3={mean_v3:.1f}% -> v6={mean_v6:.1f}%")
    print(f"  Improved: {len(improved)}, Worsened: {len(worsened)}, Unchanged: {len(improvements) - len(improved) - len(worsened)}")

# ============================================================
# STEP 5: Recipe frequency analysis - which recipe is most common best-match?
# ============================================================
print("\n" + "=" * 70)
print("STEP 5: Best-match recipe frequency (v6)")
print("=" * 70)

recipe_freq = defaultdict(int)
for r in results:
    if r['Best_Recipe']:
        recipe_freq[r['Best_Recipe']] += 1

for recipe, cnt in sorted(recipe_freq.items(), key=lambda x: -x[1]):
    print(f"  {recipe:50s}: {cnt} folios")

print("\n" + "=" * 70)
print("ALL DONE. Session 12 Step 1 complete.")
print("=" * 70)
