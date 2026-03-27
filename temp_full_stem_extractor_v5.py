#!/usr/bin/env python3
"""
VOYNICH FULL STEM EXTRACTOR FOR ALL RECIPE FOLIOS
===================================================
Extracts ALL stems (not just shared ones) from every recipe folio in the corpus.
This fills the critical gap: the previous stems file only had stems appearing
in 2+ matched folios. We need folio-exclusive stems to identify unique ingredients.

Output: voynich_all_recipe_folio_stems.csv
  Columns: Folio, Stem, Final_Atom, Token_Count, Is_Shared (appears in 2+ recipe folios)

Also builds: voynich_folio_stem_matrix.csv
  Binary matrix: rows=stems, columns=folios, 1/0 presence
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
import csv
import os
from collections import defaultdict, Counter

BASE = r'C:\Ntizar_Obsidian\Ntizar_Brain\MASTERTMIND'

# Recipe folios (all matched folios from expanded matching)
RECIPE_FOLIOS = [
    'f87r', 'f87v', 'f88r', 'f88v', 'f89r', 'f89v',
    'f90r', 'f90v', 'f93r', 'f93v', 'f94r', 'f94v',
    'f95r', 'f95v', 'f96r', 'f96v', 'f99r', 'f99v',
    'f100r', 'f100v', 'f101r', 'f101v', 'f102r', 'f102v',
    'f103r', 'f103v', 'f104r', 'f104v', 'f105r', 'f105v',
    'f106r', 'f106v', 'f107r', 'f107v', 'f108r', 'f108v',
    'f111r', 'f111v', 'f112r', 'f112v', 'f113r', 'f113v',
    'f114r', 'f114v', 'f115r', 'f115v', 'f116r', 'f116v',
]

def split_atom(word):
    """Split a Voynich word into stem + final atom."""
    atoms = re.findall(r'[A-Z][a-z0-9]*', word)
    if len(atoms) > 1:
        return ''.join(atoms[:-1]), atoms[-1]
    elif len(atoms) == 1:
        return word, ""
    return "", ""

# Parse corpus
folio_data = defaultdict(lambda: {'stems': Counter(), 'words': Counter(), 'lines': 0})
current_folio = None

with open(os.path.join(BASE, 'zenodo_voynich', 'corpus', 'voynich_sta.txt'), 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        
        # Folio header line: <f87v> or <f90r1> (foldout sub-pages)
        folio_header = re.match(r'^<(f\d+[rv]\d*)>\s', line)
        if folio_header:
            raw_folio = folio_header.group(1)
            # Map foldout sub-pages to parent: f90r1 -> f90r, f95v2 -> f95v
            current_folio = re.sub(r'^(f\d+[rv])\d+$', r'\1', raw_folio)
            continue
        
        # Content line: <f87v.1,@P0> or <f90r1.3,@P0> (foldout sub-pages)
        line_match = re.match(r'^<(f\d+[rv]\d*)\.\d+,[^>]*>\s+(.*)', line)
        if not line_match:
            continue
        
        raw_line_folio = line_match.group(1)
        # Map foldout sub-pages to parent
        line_folio = re.sub(r'^(f\d+[rv])\d+$', r'\1', raw_line_folio)
        content = line_match.group(2).strip()
        
        # Skip if not a recipe folio
        if line_folio not in RECIPE_FOLIOS:
            continue
        
        if not content:
            continue
        
        folio_data[line_folio]['lines'] += 1
        
        # Split by separator <-> (left/right text blocks)
        blocks = content.split('<->')
        
        for block in blocks:
            # Split into tokens by '.'
            tokens = block.strip().split('.')
            for token in tokens:
                token = token.strip()
                # Clean token: remove <>, *, commas, hyphens but keep alphanumeric
                token = re.sub(r'[<>*\-]', '', token)
                # Remove trailing/leading commas and what follows (comma-separated annotations)
                token = token.split(',')[0].strip()
                
                if not token or len(token) < 2:
                    continue
                
                # Check if it looks like a valid STA1 word (contains uppercase letter)
                if not re.search(r'[A-Z]', token):
                    continue
                
                stem, final = split_atom(token)
                if stem and len(stem) >= 1:
                    folio_data[line_folio]['words'][token] += 1
                    folio_data[line_folio]['stems'][stem] += 1

print("=" * 80)
print("FULL STEM EXTRACTION FROM ALL RECIPE FOLIOS")
print("=" * 80)

# Summary
total_stems_all = set()
for folio in RECIPE_FOLIOS:
    data = folio_data[folio]
    n_words = sum(data['words'].values())
    n_unique_words = len(data['words'])
    n_unique_stems = len(data['stems'])
    total_stems_all.update(data['stems'].keys())
    
# Build stem -> folio presence matrix
stem_folio_presence = defaultdict(set)
for folio in RECIPE_FOLIOS:
    for stem in folio_data[folio]['stems']:
        stem_folio_presence[stem].add(folio)

print(f"\nTotal unique stems across all recipe folios: {len(total_stems_all)}")

# Focus on our key matched folios
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

# For each SMALL perfect match, show full stem inventory
print("\n" + "=" * 80)
print("DETAILED STEM INVENTORIES FOR SMALL PERFECT MATCHES")
print("=" * 80)

for folio in ['f87v', 'f87r', 'f93v', 'f96v', 'f100r', 'f100v']:
    recipe = PERFECT_MATCHES.get(folio, '?')
    data = folio_data[folio]
    stems = data['stems']
    
    print(f"\n{'='*60}")
    print(f"  {folio} = {recipe}")
    print(f"  Lines: {data['lines']}, Total tokens: {sum(data['words'].values())}")
    print(f"  Unique words: {len(data['words'])}, Unique stems: {len(stems)}")
    print(f"{'='*60}")
    
    # Categorize stems
    # How many other MATCHED recipe folios does each stem appear in?
    for stem in sorted(stems.keys(), key=lambda s: -stems[s]):
        count = stems[stem]
        other_matched = stem_folio_presence[stem] & set(ALL_MATCHED.keys()) - {folio}
        n_other_matched = len(other_matched)
        n_total_recipe = len(stem_folio_presence[stem] & set(RECIPE_FOLIOS))
        
        # Determine unique words for this stem in this folio
        words_here = [w for w in data['words'] if split_atom(w)[0] == stem]
        
        marker = ""
        if n_other_matched == 0:
            marker = " ** FOLIO-EXCLUSIVE **"
        elif n_other_matched <= 2:
            marker = " * rare *"
        
        print(f"  {stem:25s} x{count:>2d}  (in {n_total_recipe:>2d} recipe folios, "
              f"{n_other_matched:>2d} other matched)  words: {words_here[:4]}{marker}")


# Now specifically analyze f87v for exclusive stems
print("\n\n" + "=" * 80)
print("f87v EXCLUSIVE STEM ANALYSIS (FOR UNG. APOSTOLORUM)")
print("=" * 80)

# Load current identifications
current_ids = {}
with open(os.path.join(BASE, 'voynich_unified_identifications_v4c.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        current_ids[row['Stem']] = row

f87v_stems = folio_data['f87v']['stems']
f87v_exclusive = []
f87v_rare = []

for stem in sorted(f87v_stems.keys(), key=lambda s: -f87v_stems[s]):
    other_matched = stem_folio_presence[stem] & set(ALL_MATCHED.keys()) - {'f87v'}
    
    if stem in current_ids:
        ing = current_ids[stem]['Ingredient']
        print(f"  [IDENTIFIED] {stem:25s} = {ing}")
    elif len(other_matched) == 0:
        f87v_exclusive.append(stem)
        total_recipe = len(stem_folio_presence[stem] & set(RECIPE_FOLIOS))
        print(f"  [EXCLUSIVE ] {stem:25s} x{f87v_stems[stem]:>2d}  "
              f"(in {total_recipe} total recipe folios)")
    elif len(other_matched) <= 2:
        f87v_rare.append(stem)
        recipes = [ALL_MATCHED[f] for f in other_matched]
        print(f"  [RARE      ] {stem:25s} x{f87v_stems[stem]:>2d}  "
              f"also in: {sorted(other_matched)} ({recipes})")
    else:
        n = len(other_matched)
        print(f"  [COMMON    ] {stem:25s} x{f87v_stems[stem]:>2d}  (in {n} other matched folios)")

print(f"\nf87v summary:")
print(f"  Total unique stems: {len(f87v_stems)}")
print(f"  Already identified: {sum(1 for s in f87v_stems if s in current_ids)}")
print(f"  EXCLUSIVE to f87v (among matched folios): {len(f87v_exclusive)}")
print(f"  RARE (1-2 other matched folios): {len(f87v_rare)}")

# The exclusive stems of f87v MUST map to UA ingredients
# UA remaining: Aristolochia longa/rotunda, Cera, Litharge, Oleum olivarum,
#               Olibanum, Opopanax, Resina pini, Verdigris
print(f"\n  Exclusive stems ({len(f87v_exclusive)}) must map to remaining "
      f"UA ingredients (9):")
print(f"  Ratio: {len(f87v_exclusive)}/9 = {len(f87v_exclusive)/9:.1f}")

# For rare stems, check intersection of UA + other recipe ingredients
recipe_ingredients = defaultdict(set)
with open(os.path.join(BASE, 'recetas_historicas_ingredientes_flat.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        rname = row['Receta'].split('(')[0].strip()
        recipe_ingredients[rname].add(row['Ingrediente_Normalizado'])

already_identified_ings = set()
for row in current_ids.values():
    if row['Ingredient'] != 'FUNCTION_WORD':
        for i in row['Ingredient'].split('|'):
            already_identified_ings.add(i.strip())

ua_remaining = recipe_ingredients['Unguentum Apostolorum'] - already_identified_ings

print(f"\n--- RARE STEMS: CROSS-RECIPE CONSTRAINT ---")
for stem in f87v_rare:
    other_matched = stem_folio_presence[stem] & set(ALL_MATCHED.keys()) - {'f87v'}
    other_recipes = set(ALL_MATCHED[f] for f in other_matched)
    
    # Candidate = UA ingredients that are ALSO in all other recipes
    candidates = set(ua_remaining)
    for r in other_recipes:
        candidates &= recipe_ingredients.get(r, set())
    candidates -= already_identified_ings
    
    recipes_str = ', '.join(sorted(other_recipes))
    print(f"  {stem:25s} also in [{recipes_str}]")
    if candidates:
        print(f"    -> {len(candidates)} candidates: {sorted(candidates)}")
    else:
        print(f"    -> 0 candidates (likely function word)")


# ============================================================
# WRITE COMPREHENSIVE FOLIO-STEM CSV
# ============================================================
out_path = os.path.join(BASE, 'voynich_all_recipe_folio_stems.csv')
rows = []
for folio in RECIPE_FOLIOS:
    data = folio_data[folio]
    for stem, count in data['stems'].most_common():
        # Get final atoms for this stem
        words = [w for w in data['words'] if split_atom(w)[0] == stem]
        finals = set(split_atom(w)[1] for w in words)
        
        n_matched_folios = len(stem_folio_presence[stem] & set(ALL_MATCHED.keys()))
        n_total_recipe_folios = len(stem_folio_presence[stem] & set(RECIPE_FOLIOS))
        
        rows.append({
            'Folio': folio,
            'Stem': stem,
            'Final_Atoms': '|'.join(sorted(finals)),
            'Token_Count': count,
            'N_Matched_Folios': n_matched_folios,
            'N_Total_Recipe_Folios': n_total_recipe_folios,
            'Is_Identified': stem in current_ids,
            'Identification': current_ids.get(stem, {}).get('Ingredient', ''),
        })

with open(out_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['Folio', 'Stem', 'Final_Atoms', 'Token_Count', 
                                            'N_Matched_Folios', 'N_Total_Recipe_Folios',
                                            'Is_Identified', 'Identification'])
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

print(f"\nSaved {len(rows)} rows to: {out_path}")

# ============================================================
# DIFFERENTIAL ANALYSIS WITH FULL STEM DATA
# ============================================================
print("\n\n" + "=" * 80)
print("DIFFERENTIAL ANALYSIS WITH FULL FOLIO-LEVEL STEM DATA")
print("=" * 80)

# For each unidentified ingredient, find stems with best differential:
# present in folios whose recipe HAS the ingredient,
# absent from folios whose recipe DOES NOT
# Using the full stem data (not just the old shared-stems file)

all_possible_ings = set()
for recipe in ALL_MATCHED.values():
    all_possible_ings |= recipe_ingredients.get(recipe, set())
unidentified_ings = all_possible_ings - already_identified_ings

# Build full stem presence for matched folios
full_stem_presence = defaultdict(set)  # stem -> set of matched folios
for folio in ALL_MATCHED:
    for stem in folio_data[folio]['stems']:
        full_stem_presence[stem].add(folio)

# For each ingredient, compute should_have and should_not folio sets
ingredient_differential = {}
for ing in unidentified_ings:
    should_have = set()
    should_not = set()
    for folio, recipe in ALL_MATCHED.items():
        if ing in recipe_ingredients.get(recipe, set()):
            should_have.add(folio)
        else:
            should_not.add(folio)
    ingredient_differential[ing] = (should_have, should_not)

# Now for each stem, find best ingredient match
best_matches = []
for stem in full_stem_presence:
    if stem in current_ids:
        continue
    
    stem_fols = full_stem_presence[stem]
    
    for ing in unidentified_ings:
        should_have, should_not = ingredient_differential[ing]
        
        in_pos = stem_fols & should_have
        in_neg = stem_fols & should_not
        
        if len(should_have) == 0:
            continue
        
        pct_pos = len(in_pos) / len(should_have)
        pct_neg = len(in_neg) / len(should_not) if should_not else 0
        
        # Only consider strong signals
        if pct_pos >= 0.4 and pct_neg <= 0.10 and len(in_pos) >= 2:
            score = pct_pos * (1 - pct_neg)
            best_matches.append({
                'stem': stem,
                'ingredient': ing,
                'score': score,
                'pct_pos': pct_pos,
                'pct_neg': pct_neg,
                'n_pos': len(in_pos),
                'total_pos': len(should_have),
                'n_neg': len(in_neg),
                'total_neg': len(should_not),
                'n_folios': len(stem_fols),
            })

best_matches.sort(key=lambda x: (-x['score'], x['n_neg']))

# Show top results, grouping by ingredient
print(f"\nFound {len(best_matches)} strong differential matches")
print(f"\n--- TOP DIFFERENTIAL MATCHES (score >= 0.5, zero negative) ---")
print(f"{'Stem':25s} {'Ingredient':25s} {'Score':>6s} {'Pos':>8s} {'Neg':>8s} {'Folios':>6s}")
print("-" * 85)

shown = set()
for m in best_matches:
    if m['score'] < 0.5 or m['n_neg'] > 0:
        continue
    key = (m['stem'], m['ingredient'])
    if key in shown:
        continue
    shown.add(key)
    
    print(f"{m['stem']:25s} {m['ingredient']:25s} {m['score']:6.3f} "
          f"{m['n_pos']}/{m['total_pos']:>2d}={m['pct_pos']:.0%}  "
          f"{m['n_neg']}/{m['total_neg']:>2d}={m['pct_neg']:.0%}  "
          f"{m['n_folios']:>4d}")
    if len(shown) >= 50:
        break

# Find stems that are UNIQUE to a single ingredient (only one good match)
print(f"\n--- UNIQUE DIFFERENTIAL MATCHES (only ONE ingredient with score>=0.5, 0 neg) ---")
stem_best = defaultdict(list)
for m in best_matches:
    if m['score'] >= 0.5 and m['n_neg'] == 0:
        stem_best[m['stem']].append(m)

unique_matches = []
for stem, matches in stem_best.items():
    if len(matches) == 1:
        m = matches[0]
        unique_matches.append(m)
        print(f"  *** {m['stem']:25s} = {m['ingredient']:25s} "
              f"(score={m['score']:.3f}, {m['n_pos']}/{m['total_pos']} pos, 0 neg)")

print(f"\nTotal unique differential matches: {len(unique_matches)}")

# Save comprehensive differential results
diff_path = os.path.join(BASE, 'voynich_differential_analysis_v5.csv')
with open(diff_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['stem', 'ingredient', 'score', 'pct_pos', 'pct_neg',
                                            'n_pos', 'total_pos', 'n_neg', 'total_neg', 'n_folios'])
    writer.writeheader()
    for m in best_matches[:500]:
        writer.writerow(m)

print(f"\nSaved top 500 differential matches to: {diff_path}")
