#!/usr/bin/env python3
"""
Session 14: Break Galanga|Cubeba|Nux moschata triple deadlock + explore new identifications.
"""
import sys, csv, re, os
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')

ROOT = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# LOAD DATA
# ============================================================

def load_csv(fname):
    rows = []
    with open(os.path.join(ROOT, fname), encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows

recipes_main = load_csv('recetas_historicas_medievales.csv')
ingredients_flat = load_csv('recetas_historicas_ingredientes_flat.csv')
identifications_v6 = load_csv('voynich_unified_identifications_v6.csv')
corpus = load_csv('voynich_all_recipe_folio_stems.csv')
morphology = load_csv('voynich_deadlock_morphology_v3.csv')

# Build recipe -> ingredients map
recipe_ingredients = defaultdict(set)
for row in ingredients_flat:
    recipe_ingredients[row['Receta']].add(row['Ingrediente_Normalizado'])

# Build folio -> stems map
folio_stems = defaultdict(set)
for row in corpus:
    folio_stems[row['Folio']].add(row['Stem'])

# Build stem -> folios map
stem_folios = defaultdict(set)
for row in corpus:
    stem_folios[row['Stem']].add(row['Folio'])

# Current identifications
identified = {}
for row in identifications_v6:
    identified[row['Stem']] = row['Ingredient']

# All active folios
all_folios = sorted(folio_stems.keys())
print(f"Loaded: {len(recipes_main)} recipes, {len(ingredients_flat)} ingredient pairs, {len(identifications_v6)} IDs, {len(all_folios)} folios, {len(stem_folios)} unique stems")

# ============================================================
# PART 1: GALANGA | CUBEBA | NUX MOSCHATA TRIPLE DEADLOCK
# ============================================================

print("\n" + "="*80)
print("PART 1: GALANGA | CUBEBA | NUX MOSCHATA TRIPLE DEADLOCK")
print("="*80)

# The two deadlocked stems
deadlock_stems = ['K1A1B2B1A3', 'T1A1']

# First, understand which recipes contain each ingredient
galanga_recipes = set()
cubeba_recipes = set()
nux_recipes = set()

for recipe, ings in recipe_ingredients.items():
    if 'Galanga' in ings:
        galanga_recipes.add(recipe)
    if 'Cubeba' in ings:
        cubeba_recipes.add(recipe)
    if 'Nux moschata' in ings:
        nux_recipes.add(recipe)

print(f"\nGalanga in {len(galanga_recipes)} recipes: {sorted(galanga_recipes)}")
print(f"Cubeba in {len(cubeba_recipes)} recipes: {sorted(cubeba_recipes)}")
print(f"Nux moschata in {len(nux_recipes)} recipes: {sorted(nux_recipes)}")

# Find discriminating recipes: recipes with ONLY ONE of the three
galanga_only = galanga_recipes - cubeba_recipes - nux_recipes
cubeba_only = cubeba_recipes - galanga_recipes - nux_recipes
nux_only = nux_recipes - galanga_recipes - cubeba_recipes

# Also: recipes with exactly two of the three
gal_cub_only = (galanga_recipes & cubeba_recipes) - nux_recipes
gal_nux_only = (galanga_recipes & nux_recipes) - cubeba_recipes
cub_nux_only = (cubeba_recipes & nux_recipes) - galanga_recipes
all_three = galanga_recipes & cubeba_recipes & nux_recipes

print(f"\n--- Discriminating recipes ---")
print(f"Galanga-ONLY (no Cubeba, no Nux): {len(galanga_only)} -> {sorted(galanga_only)}")
print(f"Cubeba-ONLY (no Galanga, no Nux): {len(cubeba_only)} -> {sorted(cubeba_only)}")
print(f"Nux moschata-ONLY (no Galanga, no Cubeba): {len(nux_only)} -> {sorted(nux_only)}")
print(f"\nGalanga+Cubeba (no Nux): {len(gal_cub_only)} -> {sorted(gal_cub_only)}")
print(f"Galanga+Nux (no Cubeba): {len(gal_nux_only)} -> {sorted(gal_nux_only)}")
print(f"Cubeba+Nux (no Galanga): {len(cub_nux_only)} -> {sorted(cub_nux_only)}")
print(f"All three: {len(all_three)} -> {sorted(all_three)}")

# ============================================================
# Content-based matching for the triple deadlock
# Using the same F1 methodology as previous deadlock breakers
# ============================================================

def compute_f1_for_recipe(folio, recipe_name, recipe_ings, ident_map):
    """Compute F1 between a folio's identified stems and a recipe's ingredients."""
    folio_identified_ings = set()
    for stem in folio_stems.get(folio, set()):
        if stem in ident_map:
            ing = ident_map[stem]
            if ing != 'FUNCTION_WORD':
                # Handle multi-ingredient assignments
                for sub_ing in ing.split('|'):
                    folio_identified_ings.add(sub_ing.strip())
    
    if not folio_identified_ings or not recipe_ings:
        return 0.0, set(), set()
    
    # Only count ingredients we can potentially identify
    # (ingredients that appear in our identification table)
    all_identified_ingredients = set()
    for v in ident_map.values():
        if v != 'FUNCTION_WORD':
            for sub in v.split('|'):
                all_identified_ingredients.add(sub.strip())
    
    # True positives: ingredients identified in folio AND in recipe
    tp = folio_identified_ings & recipe_ings
    # False positives: identified in folio but NOT in recipe
    fp = folio_identified_ings - recipe_ings
    # False negatives: in recipe AND in our id vocabulary but NOT identified in this folio
    fn = (recipe_ings & all_identified_ingredients) - folio_identified_ings
    
    precision = len(tp) / (len(tp) + len(fp)) if (len(tp) + len(fp)) > 0 else 0
    recall = len(tp) / (len(tp) + len(fn)) if (len(tp) + len(fn)) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    return f1 * 100, tp, fp

# For the deadlock, we need to test: what if the deadlocked stems are Galanga vs Cubeba vs Nux moschata?
# Create three alternative identification maps

results_gcn = []

for folio in all_folios:
    row = {'Folio': folio}
    
    for test_ingredient, label in [('Galanga', 'Galanga'), ('Cubeba', 'Cubeba'), ('Nux moschata', 'Nux')]:
        # Create modified ident map
        test_ident = dict(identified)
        for ds in deadlock_stems:
            test_ident[ds] = test_ingredient
        
        best_f1 = 0.0
        best_recipe = ''
        
        for recipe in recipes_main:
            rname = recipe['Nombre_Receta']
            rings = recipe_ingredients[rname]
            f1, tp, fp = compute_f1_for_recipe(folio, rname, rings, test_ident)
            if f1 > best_f1:
                best_f1 = f1
                best_recipe = rname
        
        row[f'{label}_F1'] = best_f1
        row[f'{label}_Recipe'] = best_recipe
    
    # Determine verdict
    vals = [row['Galanga_F1'], row['Cubeba_F1'], row['Nux_F1']]
    max_val = max(vals)
    
    if max_val == 0:
        verdict = 'INSUFFICIENT'
    else:
        winners = []
        if row['Galanga_F1'] == max_val:
            winners.append('GALANGA')
        if row['Cubeba_F1'] == max_val:
            winners.append('CUBEBA')
        if row['Nux_F1'] == max_val:
            winners.append('NUX')
        
        margin = max_val - sorted(vals)[-2] if len(set(vals)) > 1 else 0
        
        if len(winners) == 1 and margin >= 3.0:
            verdict = winners[0]
        elif len(winners) == 1 and margin > 0:
            verdict = winners[0] + '_WEAK'
        else:
            verdict = 'TIED'
    
    row['Verdict'] = verdict
    results_gcn.append(row)

# Tally
verdicts = Counter(r['Verdict'] for r in results_gcn)
print(f"\n--- Triple Deadlock Results ---")
for v, c in sorted(verdicts.items(), key=lambda x: -x[1]):
    print(f"  {v}: {c} folios")

# Analyze by strong vs weak
galanga_count = sum(1 for r in results_gcn if 'GALANGA' in r['Verdict'])
cubeba_count = sum(1 for r in results_gcn if 'CUBEBA' in r['Verdict'])
nux_count = sum(1 for r in results_gcn if 'NUX' in r['Verdict'])
tied_count = sum(1 for r in results_gcn if r['Verdict'] == 'TIED')

print(f"\n  Total GALANGA: {galanga_count}")
print(f"  Total CUBEBA: {cubeba_count}")
print(f"  Total NUX: {nux_count}")
print(f"  Total TIED: {tied_count}")

# Save CSV
with open(os.path.join(ROOT, 'voynich_galanga_cubeba_nux_deadlock.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['Folio','Galanga_F1','Galanga_Recipe','Cubeba_F1','Cubeba_Recipe','Nux_F1','Nux_Recipe','Verdict'])
    for r in results_gcn:
        w.writerow([r['Folio'], f"{r['Galanga_F1']:.1f}", r['Galanga_Recipe'], f"{r['Cubeba_F1']:.1f}", r['Cubeba_Recipe'], f"{r['Nux_F1']:.1f}", r['Nux_Recipe'], r['Verdict']])

print(f"\nSaved: voynich_galanga_cubeba_nux_deadlock.csv")

# Detailed analysis: look at discriminating recipes
print("\n--- Discriminating Recipe Analysis ---")
for test_name, disc_recipes in [('Galanga-only', galanga_only), ('Cubeba-only', cubeba_only), ('Nux-only', nux_only)]:
    if not disc_recipes:
        print(f"\n  {test_name}: NO discriminating recipes found!")
        continue
    print(f"\n  {test_name} recipes: {sorted(disc_recipes)}")
    for rname in sorted(disc_recipes):
        rings = recipe_ingredients[rname]
        # Check which folios match well with this specific recipe
        matches = []
        for folio in all_folios:
            f1, tp, fp = compute_f1_for_recipe(folio, rname, rings, identified)
            if f1 > 20:
                matches.append((folio, f1, tp))
        if matches:
            matches.sort(key=lambda x: -x[1])
            print(f"    {rname} ({len(rings)} ingredients): {len(matches)} folios with F1>20%")
            for f, f1, tp in matches[:5]:
                print(f"      {f}: F1={f1:.1f}%, TP={tp}")

# Check if the deadlocked stems actually appear in folios that match discriminating recipes
print("\n--- Deadlocked stems in discriminating recipe folios ---")
for ds in deadlock_stems:
    ds_folios = stem_folios.get(ds, set())
    print(f"\n  Stem {ds} appears in {len(ds_folios)} folios: {sorted(ds_folios)}")

# ============================================================
# Additional approach: Co-occurrence analysis
# Which OTHER identified stems co-occur with the deadlocked stems?
# ============================================================

print("\n--- Co-occurrence analysis for deadlocked stems ---")
for ds in deadlock_stems:
    ds_folios_list = sorted(stem_folios.get(ds, set()))
    co_occurring = Counter()
    for folio in ds_folios_list:
        for stem in folio_stems[folio]:
            if stem in identified and identified[stem] != 'FUNCTION_WORD' and stem != ds:
                co_occurring[identified[stem]] += 1
    print(f"\n  {ds} ({len(ds_folios_list)} folios) co-occurs with:")
    for ing, cnt in co_occurring.most_common(15):
        pct = cnt / len(ds_folios_list) * 100
        print(f"    {ing}: {cnt}/{len(ds_folios_list)} ({pct:.0f}%)")


# ============================================================
# PART 2: EXPLORE 948 UNIDENTIFIED STEMS FOR NEW IDENTIFICATIONS
# ============================================================

print("\n\n" + "="*80)
print("PART 2: EXPLORE UNIDENTIFIED STEMS FOR NEW IDENTIFICATIONS")
print("="*80)

# Strategy: For stems appearing in 3+ folios, use recipe intersection to find candidates
# This is the same solver logic used in sessions 1-5, now with the larger 50-recipe database

# Get all currently identified ingredients
id_ingredients = set()
for v in identified.values():
    if v != 'FUNCTION_WORD':
        for sub in v.split('|'):
            id_ingredients.add(sub.strip())

print(f"\nCurrently identified ingredients: {sorted(id_ingredients)}")
print(f"Total identified stems: {len(identified)}")

# All unidentified stems with 2+ folio appearances
unidentified_multi = {}
for stem, folios in stem_folios.items():
    if stem not in identified and len(folios) >= 2:
        unidentified_multi[stem] = folios

print(f"Unidentified stems with 2+ folios: {len(unidentified_multi)}")

# For each unidentified stem, find which recipes best match its folio distribution
# Method: For each stem's folios, get the best-match recipe per folio (using current v6 IDs)
# Then look at which ingredients appear in ALL those best-match recipes but are NOT yet identified

# Better method: Intersection approach
# For each stem, look at the BEST-MATCH recipes for the folios where it appears
# The stem's ingredient must be present in all those recipes
# Then subtract already-identified ingredients

def get_best_recipe_for_folio(folio):
    best_f1 = 0
    best_recipe = None
    for recipe in recipes_main:
        rname = recipe['Nombre_Receta']
        rings = recipe_ingredients[rname]
        f1, tp, fp = compute_f1_for_recipe(folio, rname, rings, identified)
        if f1 > best_f1:
            best_f1 = f1
            best_recipe = rname
    return best_recipe, best_f1

# Cache best recipe per folio
print("\nComputing best recipe per folio...")
folio_best_recipe = {}
for folio in all_folios:
    br, bf = get_best_recipe_for_folio(folio)
    folio_best_recipe[folio] = (br, bf)
    
print("Done. Best recipes:")
for f in sorted(folio_best_recipe.keys()):
    r, f1 = folio_best_recipe[f]
    print(f"  {f}: {r} (F1={f1:.1f}%)")

# For each unidentified stem: intersect ingredients of best-match recipes
# across the folios where it appears
new_candidates = []

for stem in sorted(unidentified_multi.keys(), key=lambda s: -len(unidentified_multi[s])):
    folios = unidentified_multi[stem]
    if len(folios) < 3:
        continue  # Need at least 3 for meaningful intersection
    
    # Get best recipes for these folios
    recipes_for_stem = []
    for f in folios:
        br, bf = folio_best_recipe[f]
        if br and bf > 20:
            recipes_for_stem.append(br)
    
    if len(recipes_for_stem) < 2:
        continue
    
    # Intersect ingredients across these recipes
    recipe_set = set(recipes_for_stem)
    if len(recipe_set) < 2:
        # All folios map to same recipe - not very discriminative
        ing_intersection = recipe_ingredients[recipes_for_stem[0]].copy()
    else:
        ing_lists = [recipe_ingredients[r] for r in recipe_set]
        ing_intersection = ing_lists[0].copy()
        for il in ing_lists[1:]:
            ing_intersection &= il
    
    # Remove already-identified ingredients and function words
    candidates = ing_intersection - id_ingredients
    # Also remove very common ingredients that are probably already in the identified set
    # (but they might not be, so keep them)
    
    if candidates:
        # Score: fewer candidates = better
        new_candidates.append({
            'stem': stem,
            'n_folios': len(folios),
            'n_recipes': len(recipe_set),
            'n_candidates': len(candidates),
            'candidates': sorted(candidates),
            'recipes': sorted(recipe_set),
            'folios': sorted(folios)
        })

# Sort by n_candidates (fewer = better), then by n_folios (more = better)
new_candidates.sort(key=lambda x: (x['n_candidates'], -x['n_folios']))

print(f"\n--- New Candidate Identifications ---")
print(f"Found {len(new_candidates)} stems with candidate ingredients")

# Show best candidates (1-3 candidates)
excellent = [c for c in new_candidates if c['n_candidates'] == 1]
strong = [c for c in new_candidates if c['n_candidates'] == 2]
moderate = [c for c in new_candidates if c['n_candidates'] == 3]
weak = [c for c in new_candidates if 4 <= c['n_candidates'] <= 6]

print(f"\n  UNIQUE (1 candidate): {len(excellent)}")
for c in excellent[:30]:
    print(f"    {c['stem']} ({c['n_folios']} folios, {c['n_recipes']} recipes) -> {c['candidates'][0]}")
    print(f"      Recipes: {c['recipes']}")

print(f"\n  STRONG (2 candidates): {len(strong)}")
for c in strong[:20]:
    print(f"    {c['stem']} ({c['n_folios']} folios, {c['n_recipes']} recipes) -> {c['candidates']}")

print(f"\n  MODERATE (3 candidates): {len(moderate)}")
for c in moderate[:15]:
    print(f"    {c['stem']} ({c['n_folios']} folios, {c['n_recipes']} recipes) -> {c['candidates']}")

print(f"\n  WEAK (4-6 candidates): {len(weak)}")
for c in weak[:10]:
    print(f"    {c['stem']} ({c['n_folios']} folios, {c['n_recipes']} recipes) -> {c['candidates']}")

# ============================================================
# PART 3: Absence-based validation
# For UNIQUE candidates, verify they are ABSENT from best recipes 
# of folios where the stem does NOT appear
# ============================================================

print("\n\n--- Absence Validation for UNIQUE candidates ---")
validated_new = []

for c in excellent:
    stem = c['stem']
    candidate_ing = c['candidates'][0]
    stem_fols = set(c['folios'])
    absent_folios = set(all_folios) - stem_fols
    
    # How many absent-folios' best recipes contain this ingredient?
    absent_with_ing = 0
    absent_total_valid = 0
    for f in absent_folios:
        br, bf = folio_best_recipe[f]
        if br and bf > 20:
            absent_total_valid += 1
            if candidate_ing in recipe_ingredients[br]:
                absent_with_ing += 1
    
    # Ideally: low absent_with_ing / absent_total_valid = ingredient is rare in absent recipes
    if absent_total_valid > 0:
        absent_pct = absent_with_ing / absent_total_valid * 100
    else:
        absent_pct = 0
    
    # Presence validation: what % of stem's folios' best recipes contain the ingredient?
    present_with_ing = 0
    for f in stem_fols:
        br, bf = folio_best_recipe[f]
        if br and bf > 20 and candidate_ing in recipe_ingredients[br]:
            present_with_ing += 1
    
    presence_pct = present_with_ing / len(stem_fols) * 100 if stem_fols else 0
    
    conf = max(50, min(95, presence_pct - absent_pct + 50))
    
    validated_new.append({
        'stem': stem,
        'ingredient': candidate_ing,
        'n_folios': len(stem_fols),
        'presence_pct': presence_pct,
        'absence_pct': absent_pct,
        'confidence': conf,
        'recipes': c['recipes']
    })
    
    print(f"  {stem} -> {candidate_ing}: presence={presence_pct:.0f}%, absence={absent_pct:.0f}%, conf={conf:.0f}%")

# Sort by confidence
validated_new.sort(key=lambda x: -x['confidence'])

# ============================================================
# Also validate STRONG (2-candidate) stems
# ============================================================
print("\n--- Validation for STRONG (2-candidate) stems ---")
validated_strong = []

for c in strong:
    stem = c['stem']
    stem_fols = set(c['folios'])
    absent_folios = set(all_folios) - stem_fols
    
    best_ing = None
    best_score = -999
    
    for candidate_ing in c['candidates']:
        # Presence score
        present_with = 0
        for f in stem_fols:
            br, bf = folio_best_recipe[f]
            if br and bf > 20 and candidate_ing in recipe_ingredients[br]:
                present_with += 1
        presence_pct = present_with / len(stem_fols) * 100 if stem_fols else 0
        
        # Absence score
        absent_with = 0
        absent_valid = 0
        for f in absent_folios:
            br, bf = folio_best_recipe[f]
            if br and bf > 20:
                absent_valid += 1
                if candidate_ing in recipe_ingredients[br]:
                    absent_with += 1
        absence_pct = absent_with / absent_valid * 100 if absent_valid > 0 else 0
        
        score = presence_pct - absence_pct
        if score > best_score:
            best_score = score
            best_ing = candidate_ing
            best_presence = presence_pct
            best_absence = absence_pct
    
    conf = max(50, min(90, best_score + 50))
    
    validated_strong.append({
        'stem': stem,
        'ingredient': best_ing,
        'all_candidates': c['candidates'],
        'n_folios': len(stem_fols),
        'presence_pct': best_presence,
        'absence_pct': best_absence,
        'confidence': conf,
        'recipes': c['recipes']
    })
    
    print(f"  {stem} -> {best_ing} (vs {[x for x in c['candidates'] if x != best_ing]}): pres={best_presence:.0f}%, abs={best_absence:.0f}%, conf={conf:.0f}%")

validated_strong.sort(key=lambda x: -x['confidence'])

# ============================================================
# SUMMARY: New identifications to add to v7
# ============================================================
print("\n\n" + "="*80)
print("SUMMARY: POTENTIAL NEW IDENTIFICATIONS FOR v7")
print("="*80)

print("\nFrom UNIQUE resolution:")
for v in validated_new:
    tier = 2 if v['confidence'] >= 85 else 3 if v['confidence'] >= 75 else 4
    print(f"  T{tier} {v['stem']} -> {v['ingredient']} ({v['confidence']:.0f}%) [{v['n_folios']} folios]")

print(f"\nFrom STRONG resolution:")
for v in validated_strong:
    tier = 3 if v['confidence'] >= 75 else 4
    print(f"  T{tier} {v['stem']} -> {v['ingredient']} ({v['confidence']:.0f}%) [{v['n_folios']} folios]")

# Count new unique ingredients
all_new_ings = set()
for v in validated_new:
    all_new_ings.add(v['ingredient'])
for v in validated_strong:
    all_new_ings.add(v['ingredient'])

truly_new = all_new_ings - id_ingredients
print(f"\nNew ingredients not previously identified: {sorted(truly_new)}")
print(f"Total new stems: {len(validated_new) + len(validated_strong)}")

# Save complete results
with open(os.path.join(ROOT, 'voynich_new_identifications_session14.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['Stem','Ingredient','Confidence','N_Folios','Presence_Pct','Absence_Pct','N_Candidates','Source','Recipes'])
    for v in validated_new:
        w.writerow([v['stem'], v['ingredient'], f"{v['confidence']:.0f}", v['n_folios'],
                     f"{v['presence_pct']:.1f}", f"{v['absence_pct']:.1f}", 1, 'UNIQUE', '|'.join(v['recipes'])])
    for v in validated_strong:
        w.writerow([v['stem'], v['ingredient'], f"{v['confidence']:.0f}", v['n_folios'],
                     f"{v['presence_pct']:.1f}", f"{v['absence_pct']:.1f}", 2, 'STRONG', '|'.join(v['recipes'])])

print(f"\nSaved: voynich_new_identifications_session14.csv")
print(f"Saved: voynich_galanga_cubeba_nux_deadlock.csv")
print("\nDone.")
