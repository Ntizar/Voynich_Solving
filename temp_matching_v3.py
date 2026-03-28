#!/usr/bin/env python3
"""
MATCHING ENGINE v3 -- Content-Based Recipe-Folio Matching
==========================================================
Uses the v5 identification table (58 stem->ingredient mappings) to do
CONTENT-BASED matching: for each folio, look at which identified stems
are present/absent, and match against the actual ingredient lists of 50
historical recipes.

Two scoring methods:
  1. STRUCTURAL: ingredient-count similarity (as before, but with 50 recipes)
  2. CONTENT: Jaccard-like overlap of identified ingredients in folio vs recipe

Also runs the DEADLOCK BREAKER analysis:
  - Philonium Romanum has Opium but NOT Castoreum
  - Theriac Diatessaron Magna has Castoreum but NOT Opium
  - If a folio matches one but not the other, we can split the deadlocked stems.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import re, csv, os
from collections import Counter, defaultdict

BASE = r'C:\Ntizar_Obsidian\Ntizar_Brain\MASTERTMIND'

def split_atom(word):
    atoms = re.findall(r'[A-Z][a-z0-9]*', word)
    if len(atoms) > 1:
        return ''.join(atoms[:-1]), atoms[-1]
    elif len(atoms) == 1:
        return word, ""
    return "", ""

# ==============================================================
# 1. Load v5 identifications
# ==============================================================
identifications = {}  # stem -> (ingredient_or_pair, confidence, tier)
with open(os.path.join(BASE, 'voynich_unified_identifications_v5.csv'), encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        stem = row['Stem']
        ing = row['Ingredient']
        conf = float(row['Confidence'])
        tier = int(row['Tier'])
        identifications[stem] = (ing, conf, tier)

print(f"Loaded {len(identifications)} identifications")

# ==============================================================
# 2. Load expanded recipe database (50 recipes)
# ==============================================================
recipe_ingredients = defaultdict(set)  # recipe_name -> set of ingredients
recipe_meta = {}  # recipe_name -> {source, type, total}

with open(os.path.join(BASE, 'recetas_historicas_ingredientes_flat.csv'), encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rname = row['Receta']
        ing = row['Ingrediente_Normalizado']
        recipe_ingredients[rname].add(ing)

with open(os.path.join(BASE, 'recetas_historicas_medievales.csv'), encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rname = row['Nombre_Receta']
        recipe_meta[rname] = {
            'source': row['Fuente'],
            'type': row['Tipo'],
            'total': int(row['Total_Ingredientes']),
        }

print(f"Loaded {len(recipe_ingredients)} recipes with {sum(len(v) for v in recipe_ingredients.values())} ingredient-recipe pairs")

# ==============================================================
# 3. Parse Voynich corpus -- extract stems per folio (recipe section)
# ==============================================================
folio_stems = defaultdict(Counter)  # folio -> Counter of stems
folio_unique_stems = defaultdict(set)

with open(os.path.join(BASE, 'zenodo_voynich/corpus/voynich_sta.txt'), 'r', encoding='utf-8') as f:
    for line in f:
        # Parse folio from content lines like <f87r.1,@P0> or header <f87r>
        m = re.search(r'<(f\d+[rv]\d*)', line)
        if not m:
            continue
        raw_folio = m.group(1)
        folio = re.sub(r'^(f\d+[rv])\d+$', r'\1', raw_folio)  # collapse foldouts
        
        fmatch = re.match(r'f(\d+)([rv])', folio)
        if not fmatch:
            continue
        fnum = int(fmatch.group(1))
        if fnum < 87 or fnum > 116:
            continue
        
        # Skip header lines (contain <! or no content after >)
        if '<!' in line:
            continue
        content_parts = line.split('>')
        if len(content_parts) < 2:
            continue
        content = content_parts[-1].strip()
        if not content:
            continue
        
        tokens = [t.replace(',','').replace('-','').replace('*','').replace('<','').strip()
                  for t in content.split('.') if t.strip()]
        
        for t in tokens:
            stem, suf = split_atom(t)
            if len(stem) < 2:
                continue
            folio_stems[folio][stem] += 1
            folio_unique_stems[folio].add(stem)

print(f"Parsed {len(folio_stems)} recipe folios")

# ==============================================================
# 4. For each folio, determine which identified ingredients are present
# ==============================================================
folio_identified_ingredients = {}  # folio -> set of ingredient names

for folio in sorted(folio_stems.keys()):
    present_ingredients = set()
    for stem in folio_unique_stems[folio]:
        if stem in identifications:
            ing, conf, tier = identifications[stem]
            if ing == 'FUNCTION_WORD':
                continue
            # For pairs like "Zingiber|Mel despumatum", add both
            for single_ing in ing.split('|'):
                present_ingredients.add(single_ing.strip())
    folio_identified_ingredients[folio] = present_ingredients

# ==============================================================
# 5. CONTENT-BASED MATCHING
# ==============================================================
# For each folio-recipe pair, compute:
#   - overlap: |folio_ings INTERSECT recipe_ings|
#   - folio_coverage: overlap / |folio_ings|  (how much of what we see is in the recipe)
#   - recipe_coverage: overlap / |recipe_ings|  (how much of recipe we can confirm)
#   - combined_score: harmonic mean (F1) of folio_coverage and recipe_coverage

print("\n" + "=" * 120)
print("CONTENT-BASED MATCHING: Identified Ingredients vs Recipe Ingredient Lists")
print("=" * 120)

all_matches = []

for folio in sorted(folio_stems.keys(), key=lambda x: (int(re.search(r'(\d+)', x).group(1)), x[-1])):
    n_unique = len(folio_unique_stems[folio])
    n_total = sum(folio_stems[folio].values())
    present_ings = folio_identified_ingredients[folio]
    
    scored = []
    for rname, ring in recipe_ingredients.items():
        overlap = present_ings & ring
        n_overlap = len(overlap)
        
        folio_cov = n_overlap / len(present_ings) if present_ings else 0
        recipe_cov = n_overlap / len(ring) if ring else 0
        
        if folio_cov + recipe_cov > 0:
            f1 = 2 * folio_cov * recipe_cov / (folio_cov + recipe_cov)
        else:
            f1 = 0
        
        # Also compute structural score (ingredient count similarity)
        recipe_n = recipe_meta.get(rname, {}).get('total', len(ring))
        diff = abs(n_unique - recipe_n)
        struct_sim = max(0, 100 - (diff / max(n_unique, recipe_n)) * 100) if max(n_unique, recipe_n) > 0 else 0
        
        scored.append({
            'recipe': rname,
            'overlap': n_overlap,
            'overlap_ings': sorted(overlap),
            'folio_cov': folio_cov,
            'recipe_cov': recipe_cov,
            'f1': f1,
            'struct_sim': struct_sim,
            'recipe_n': recipe_n,
        })
    
    # Sort by F1 first, then by overlap count
    scored.sort(key=lambda x: (-x['f1'], -x['overlap']))
    best = scored[0]
    second = scored[1] if len(scored) > 1 else None
    
    all_matches.append({
        'Folio': folio,
        'Total_Words': n_total,
        'Unique_Stems': n_unique,
        'Identified_Ingredients': len(present_ings),
        'Ingredients_List': ' | '.join(sorted(present_ings)) if present_ings else '(none)',
        'Best_Match': best['recipe'],
        'Best_Overlap': best['overlap'],
        'Best_Overlap_Ings': ' | '.join(best['overlap_ings']),
        'Best_F1': round(best['f1'] * 100, 1),
        'Best_Folio_Cov': round(best['folio_cov'] * 100, 1),
        'Best_Recipe_Cov': round(best['recipe_cov'] * 100, 1),
        'Best_Struct_Sim': round(best['struct_sim'], 1),
        'Second_Match': second['recipe'] if second else '',
        'Second_F1': round(second['f1'] * 100, 1) if second else 0,
        'all_scored': scored,  # keep for deadlock analysis
    })
    
    flag = ""
    if best['f1'] >= 0.8:
        flag = " *** EXCELLENT ***"
    elif best['f1'] >= 0.5:
        flag = " ** GOOD **"
    elif best['overlap'] >= 5:
        flag = " * NOTABLE *"
    
    print(f"{folio:<8} | {n_total:>4}w {n_unique:>3}s | ID'd: {len(present_ings):>2} [{', '.join(sorted(present_ings)[:5])}{'...' if len(present_ings)>5 else ''}] | Best: {best['recipe']:<35} OVL={best['overlap']:>2} F1={best['f1']*100:>5.1f}% FC={best['folio_cov']*100:>5.1f}% RC={best['recipe_cov']*100:>5.1f}%{flag}")


# ==============================================================
# 6. CSV Output -- full matching results
# ==============================================================
csv_path = os.path.join(BASE, 'voynich_expanded_matching_v3.csv')
with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=[
        'Folio', 'Total_Words', 'Unique_Stems', 'Identified_Ingredients',
        'Ingredients_List', 'Best_Match', 'Best_Overlap', 'Best_Overlap_Ings',
        'Best_F1', 'Best_Folio_Cov', 'Best_Recipe_Cov', 'Best_Struct_Sim',
        'Second_Match', 'Second_F1',
    ])
    writer.writeheader()
    for m in all_matches:
        row = {k: v for k, v in m.items() if k != 'all_scored'}
        writer.writerow(row)

print(f"\nCSV guardado: {csv_path}")

# Also save detailed per-folio top-5 matches
csv_path2 = os.path.join(BASE, 'voynich_matching_v3_top5.csv')
with open(csv_path2, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Folio', 'Rank', 'Recipe', 'Overlap', 'Overlap_Ingredients', 'F1_pct', 'Folio_Coverage_pct', 'Recipe_Coverage_pct', 'Structural_Sim_pct', 'Recipe_N_Ingredients'])
    for m in all_matches:
        for rank, s in enumerate(m['all_scored'][:5], 1):
            writer.writerow([
                m['Folio'], rank, s['recipe'], s['overlap'],
                ' | '.join(s['overlap_ings']),
                round(s['f1']*100, 1), round(s['folio_cov']*100, 1),
                round(s['recipe_cov']*100, 1), round(s['struct_sim'], 1),
                s['recipe_n'],
            ])

print(f"CSV top-5 guardado: {csv_path2}")

# ==============================================================
# 7. DEADLOCK BREAKER ANALYSIS
# ==============================================================
print("\n" + "=" * 120)
print("DEADLOCK BREAKER: OPIUM vs CASTOREUM")
print("=" * 120)

# Key recipes for breaking the deadlock:
# - Philonium Romanum: has Opium, does NOT have Castoreum
# - Theriac Diatessaron Magna: has Castoreum, does NOT have Opium
# - Confectio Anacardia: has Castoreum, does NOT have Opium
# - Dianucum: has Castoreum, does NOT have Opium
# - Theodoricon Euporistum: has Castoreum, does NOT have Opium

opium_only_recipes = set()
castoreum_only_recipes = set()
both_recipes = set()

for rname, ring in recipe_ingredients.items():
    has_opium = 'Opium' in ring
    has_castoreum = 'Castoreum' in ring
    if has_opium and not has_castoreum:
        opium_only_recipes.add(rname)
    elif has_castoreum and not has_opium:
        castoreum_only_recipes.add(rname)
    elif has_opium and has_castoreum:
        both_recipes.add(rname)

print(f"\nOpium-ONLY recipes ({len(opium_only_recipes)}): {sorted(opium_only_recipes)}")
print(f"Castoreum-ONLY recipes ({len(castoreum_only_recipes)}): {sorted(castoreum_only_recipes)}")
print(f"BOTH recipes ({len(both_recipes)}): {sorted(both_recipes)}")

# For each folio, compute separate scores for Opium-only vs Castoreum-only recipes
print("\n--- Per-Folio Opium vs Castoreum Discriminator ---")
print(f"{'Folio':<8} | {'Opium-Only Score':>18} | {'Cast-Only Score':>18} | {'Both Score':>12} | {'Verdict':>15}")
print("-" * 85)

deadlock_results = []

for m in all_matches:
    folio = m['Folio']
    scored = m['all_scored']
    
    # Best score among opium-only recipes
    opium_scores = [s for s in scored if s['recipe'] in opium_only_recipes]
    cast_scores = [s for s in scored if s['recipe'] in castoreum_only_recipes]
    both_scores = [s for s in scored if s['recipe'] in both_recipes]
    
    best_opium = max(opium_scores, key=lambda x: x['f1']) if opium_scores else None
    best_cast = max(cast_scores, key=lambda x: x['f1']) if cast_scores else None
    best_both = max(both_scores, key=lambda x: x['f1']) if both_scores else None
    
    o_f1 = best_opium['f1'] * 100 if best_opium else 0
    c_f1 = best_cast['f1'] * 100 if best_cast else 0
    b_f1 = best_both['f1'] * 100 if best_both else 0
    
    o_name = best_opium['recipe'][:25] if best_opium else '-'
    c_name = best_cast['recipe'][:25] if best_cast else '-'
    
    # Verdict
    if o_f1 > c_f1 + 5 and o_f1 > 10:
        verdict = "OPIUM"
    elif c_f1 > o_f1 + 5 and c_f1 > 10:
        verdict = "CASTOREUM"
    elif o_f1 > 0 and c_f1 > 0 and abs(o_f1 - c_f1) <= 5:
        verdict = "TIED"
    else:
        verdict = "INSUFFICIENT"
    
    deadlock_results.append({
        'Folio': folio,
        'Opium_F1': round(o_f1, 1),
        'Opium_Recipe': o_name,
        'Cast_F1': round(c_f1, 1),
        'Cast_Recipe': c_name,
        'Both_F1': round(b_f1, 1),
        'Verdict': verdict,
    })
    
    if verdict in ('OPIUM', 'CASTOREUM') or o_f1 > 15 or c_f1 > 15:
        print(f"{folio:<8} | {o_name:>18} {o_f1:>5.1f}% | {c_name:>18} {c_f1:>5.1f}% | {b_f1:>10.1f}% | {verdict:>15}")

# Summary
opium_folios = [d for d in deadlock_results if d['Verdict'] == 'OPIUM']
cast_folios = [d for d in deadlock_results if d['Verdict'] == 'CASTOREUM']
tied_folios = [d for d in deadlock_results if d['Verdict'] == 'TIED']

print(f"\n--- DEADLOCK BREAKER SUMMARY ---")
print(f"Folios favoring OPIUM: {len(opium_folios)}")
for d in opium_folios:
    print(f"  {d['Folio']}: Opium={d['Opium_F1']}% vs Cast={d['Cast_F1']}%")
print(f"Folios favoring CASTOREUM: {len(cast_folios)}")
for d in cast_folios:
    print(f"  {d['Folio']}: Cast={d['Cast_F1']}% vs Opium={d['Opium_F1']}%")
print(f"TIED: {len(tied_folios)}")

# ==============================================================
# 8. STEM-LEVEL DEADLOCK ANALYSIS
# ==============================================================
# For stems currently deadlocked as Opium|Castoreum, check if they appear
# preferentially in folios that favor one side

# First, identify all stems currently blocked by Opium/Castoreum deadlock
# These are stems NOT yet identified that appear in folios matching both
# Opium and Castoreum recipes

print("\n" + "=" * 120)
print("STEM-LEVEL DEADLOCK ANALYSIS")
print("=" * 120)

# Which stems appear in OPIUM-favoring folios vs CASTOREUM-favoring folios?
opium_folio_names = set(d['Folio'] for d in opium_folios)
cast_folio_names = set(d['Folio'] for d in cast_folios)

if opium_folio_names or cast_folio_names:
    stem_opium_count = Counter()
    stem_cast_count = Counter()
    
    for folio in opium_folio_names:
        if folio in folio_unique_stems:
            for stem in folio_unique_stems[folio]:
                if stem not in identifications:  # only unidentified stems
                    stem_opium_count[stem] += 1
    
    for folio in cast_folio_names:
        if folio in folio_unique_stems:
            for stem in folio_unique_stems[folio]:
                if stem not in identifications:
                    stem_cast_count[stem] += 1
    
    # Find stems exclusive to one side
    all_deadlock_stems = set(stem_opium_count.keys()) | set(stem_cast_count.keys())
    
    opium_exclusive = []
    cast_exclusive = []
    
    for stem in all_deadlock_stems:
        o = stem_opium_count.get(stem, 0)
        c = stem_cast_count.get(stem, 0)
        if o > 0 and c == 0:
            opium_exclusive.append((stem, o))
        elif c > 0 and o == 0:
            cast_exclusive.append((stem, c))
    
    opium_exclusive.sort(key=lambda x: -x[1])
    cast_exclusive.sort(key=lambda x: -x[1])
    
    print(f"\nStems ONLY in Opium-favoring folios: {len(opium_exclusive)}")
    for stem, count in opium_exclusive[:20]:
        print(f"  {stem}: {count}x in {count} Opium folios")
    
    print(f"\nStems ONLY in Castoreum-favoring folios: {len(cast_exclusive)}")
    for stem, count in cast_exclusive[:20]:
        print(f"  {stem}: {count}x in {count} Castoreum folios")
else:
    print("No clear Opium/Castoreum discrimination found at content level.")
    print("This is expected -- we need MORE identified ingredients to create contrast.")
    print("The deadlock may need to be broken via morphological or positional analysis instead.")

# ==============================================================
# 9. CSV of deadlock analysis
# ==============================================================
csv_path3 = os.path.join(BASE, 'voynich_deadlock_breaker_v3.csv')
with open(csv_path3, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=[
        'Folio', 'Opium_F1', 'Opium_Recipe', 'Cast_F1', 'Cast_Recipe', 'Both_F1', 'Verdict'
    ])
    writer.writeheader()
    writer.writerows(deadlock_results)

print(f"\nCSV deadlock: {csv_path3}")

# ==============================================================
# 10. GLOBAL SUMMARY
# ==============================================================
print("\n" + "=" * 120)
print("GLOBAL MATCHING SUMMARY")
print("=" * 120)

excellent = [m for m in all_matches if m['Best_F1'] >= 80]
good = [m for m in all_matches if 50 <= m['Best_F1'] < 80]
moderate = [m for m in all_matches if 20 <= m['Best_F1'] < 50]
weak = [m for m in all_matches if m['Best_F1'] < 20]

print(f"\n50 recipes x {len(all_matches)} folios")
print(f"Excellent matches (F1>=80%): {len(excellent)}")
for m in excellent:
    print(f"  {m['Folio']} -> {m['Best_Match']} (F1={m['Best_F1']}%, OVL={m['Best_Overlap']})")
print(f"Good matches (50-80%): {len(good)}")
for m in good:
    print(f"  {m['Folio']} -> {m['Best_Match']} (F1={m['Best_F1']}%, OVL={m['Best_Overlap']})")
print(f"Moderate matches (20-50%): {len(moderate)}")
for m in moderate:
    print(f"  {m['Folio']} -> {m['Best_Match']} (F1={m['Best_F1']}%, OVL={m['Best_Overlap']})")
print(f"Weak matches (<20%): {len(weak)}")

# Which recipes are most frequently the best match?
recipe_match_counts = Counter(m['Best_Match'] for m in all_matches)
print(f"\nRecipe frequency as best match:")
for recipe, count in recipe_match_counts.most_common(15):
    print(f"  {recipe:<40} -> {count} folios")

print("\nDONE.")
