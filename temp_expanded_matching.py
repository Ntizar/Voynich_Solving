import re
import csv
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')

# =============================================================================
# EXPANDED FOLIO-RECIPE MATCHING
# Match ALL 47 Voynich recipe folios against 23 historical recipes
# Using ingredient count + stem profile analysis
# =============================================================================

def split_atom(word):
    atoms = re.findall(r'[A-Z][a-z0-9]*', word)
    if len(atoms) > 1:
        return ''.join(atoms[:-1]), atoms[-1]
    elif len(atoms) == 1:
        return word, ""
    return "", ""

# --- Step 1: Build botany stems (for exclusive/generic classification) ---
botany_stems_by_folio = defaultdict(set)
with open('zenodo_voynich/corpus/voynich_sta.txt', 'r', encoding='utf-8') as f:
    for line in f:
        match = re.search(r'<(f[0-9]{1,3}[rv])', line)
        if not match: continue
        folio = match.group(1)
        if re.match(r'f([1-9]|[1-4][0-9]|5[0-7])[rv]', folio):
            content = line.split('>')[1].strip() if '>' in line else ""
            tokens = [t.replace(',','').replace('-','').replace('*','').replace('<','') 
                      for t in content.split('.') if t.strip()]
            for col_idx in range(min(2, len(tokens))):
                stem, suf = split_atom(tokens[col_idx])
                if suf == 'C1' and len(stem) > 2:
                    botany_stems_by_folio[folio].add(stem)

all_bot_stems = set()
for stems in botany_stems_by_folio.values():
    all_bot_stems.update(stems)

exclusive_stems = set()
generic_stems = set()
for stem in all_bot_stems:
    if sum(1 for s in botany_stems_by_folio.values() if stem in s) == 1:
        exclusive_stems.add(stem)
    else:
        generic_stems.add(stem)

# --- Step 2: Profile each recipe folio ---
# Recipe section: folios f87r-f116r (approximately)
recipe_folio_profiles = {}

with open('zenodo_voynich/corpus/voynich_sta.txt', 'r', encoding='utf-8') as f:
    for line in f:
        match = re.search(r'<(f[0-9]{1,3}[rv])', line)
        if not match: continue
        folio = match.group(1)
        
        # Recipe section filter
        fmatch = re.match(r'f(\d+)([rv])', folio)
        if not fmatch: continue
        fnum = int(fmatch.group(1))
        fside = fmatch.group(2)
        if fnum < 87 or fnum > 116: continue
        
        content = line.split('>')[1].strip() if '>' in line else ""
        if not content or content.startswith('<!'):
            continue
        
        tokens = [t.replace(',','').replace('-','').replace('*','').replace('<','') 
                  for t in content.split('.') if t.strip()]
        
        if folio not in recipe_folio_profiles:
            recipe_folio_profiles[folio] = {
                'all_stems': Counter(),
                'excl_stems': Counter(),
                'gen_stems': Counter(),
                'total_words': 0,
                'unique_stems': set()
            }
        
        for t in tokens:
            stem, suf = split_atom(t)
            if len(stem) < 2: continue
            recipe_folio_profiles[folio]['total_words'] += 1
            recipe_folio_profiles[folio]['all_stems'][stem] += 1
            recipe_folio_profiles[folio]['unique_stems'].add(stem)
            if stem in exclusive_stems:
                recipe_folio_profiles[folio]['excl_stems'][stem] += 1
            if stem in generic_stems:
                recipe_folio_profiles[folio]['gen_stems'][stem] += 1

# --- Step 3: Estimate ingredient count per folio ---
# An "ingredient" is a unique stem that appears in entity position (C1 or G1 tag)
# Simpler proxy: count unique stems that are NOT purely action words (A2)
# Better proxy: count unique exclusive+generic stems from botany that appear here

print("=" * 100)
print("EXPANDED FOLIO-RECIPE MATCHING (23 recipes x 47 folios)")
print("=" * 100)
print()

# Historical recipes (from expanded database)
historical = [
    ("Theriac Magna", 64), ("Mithridatium", 54), ("Trifera Magna", 28),
    ("Aurea Alexandrina", 22), ("Philonium Persicum", 18), ("Requies Magna", 17),
    ("Diamargariton", 16), ("Confectio Hamech", 15), ("Diascordium", 14),
    ("Unguentum Apostolorum", 12), ("Unguentum Populeon", 12),
    ("Diaciminum", 11), ("Hiera Picra", 10), ("Dialtea", 10),
    ("Oximel Compositum", 10), ("Pillulae de Hiera", 9),
    ("Electuarium Rosarum", 8), ("Pillulae Fetidae", 8),
    ("Pillulae Aureae", 7), ("Unguentum Basilicon", 7),
    ("Diacodion", 6), ("Pillulae Cochiae", 5), ("Theriac Diatessaron", 5),
]

# For each folio, estimate ingredient count using multiple methods
folio_estimates = {}

for folio in sorted(recipe_folio_profiles.keys(), key=lambda x: (int(re.search(r'(\d+)', x).group(1)), x[-1])):
    prof = recipe_folio_profiles[folio]
    
    # Method 1: Count unique botany stems (exclusive + generic) present
    n_excl = len(prof['excl_stems'])
    n_gen = len(prof['gen_stems'])
    n_botany = n_excl + n_gen
    
    # Method 2: Count unique stems that appear <=3 times (likely ingredient names, not function words)
    low_freq_stems = sum(1 for s, c in prof['all_stems'].items() if c <= 3 and len(s) > 2)
    
    # Method 3: From the recipe profile CSV (pre-computed)
    # We already know N_Ingredientes_Exclusivos + N_Ingredientes_Genericos from CSV
    
    # Best estimate: use botany stems count as primary
    estimated_ingredients = n_botany
    
    folio_estimates[folio] = {
        'n_excl': n_excl,
        'n_gen': n_gen,
        'n_botany': n_botany,
        'n_low_freq': low_freq_stems,
        'total_words': prof['total_words'],
        'total_unique': len(prof['unique_stems'])
    }

# --- Step 4: Match folios to recipes ---
# Scoring: 
#   100% = exact ingredient count match
#   95%+ = off by 1
#   90%+ = off by 2

matches = []
perfect_matches = []
strong_matches = []

print(f"{'Folio':<8} | {'Words':>5} | {'Uniq':>4} | {'Bot':>3} | {'Est_Ing':>7} | {'Best Match':<35} | {'Hist_N':>6} | {'Sim%':>5} | {'2nd Match':<30} | {'Sim2%':>5}")
print("-" * 150)

for folio in sorted(folio_estimates.keys(), key=lambda x: (int(re.search(r'(\d+)', x).group(1)), x[-1])):
    est = folio_estimates[folio]
    n_est = est['n_botany']
    
    # Score all recipes
    scored = []
    for recipe_name, recipe_n in historical:
        if n_est == 0:
            sim = 0
        else:
            diff = abs(n_est - recipe_n)
            sim = max(0, 100 - (diff / max(n_est, recipe_n)) * 100)
        scored.append((recipe_name, recipe_n, sim))
    
    scored.sort(key=lambda x: -x[2])
    best = scored[0]
    second = scored[1]
    
    flag = ""
    if best[2] == 100:
        flag = " *** PERFECT ***"
        perfect_matches.append((folio, best[0], best[1], n_est, best[2]))
    elif best[2] >= 90:
        flag = " ** STRONG **"
        strong_matches.append((folio, best[0], best[1], n_est, best[2]))
    
    matches.append({
        'Folio': folio,
        'Total_Words': est['total_words'],
        'Unique_Stems': est['total_unique'],
        'Botany_Stems': est['n_botany'],
        'Estimated_Ingredients': n_est,
        'Best_Match': best[0],
        'Best_Match_N': best[1],
        'Best_Similarity': round(best[2], 1),
        'Second_Match': second[0],
        'Second_Match_N': second[1],
        'Second_Similarity': round(second[2], 1),
    })
    
    print(f"{folio:<8} | {est['total_words']:>5} | {est['total_unique']:>4} | {n_est:>3} | {n_est:>7} | {best[0]:<35} | {best[1]:>6} | {best[2]:>4.1f}% | {second[0]:<30} | {second[2]:>4.1f}%{flag}")

# --- Summary ---
print(f"\n{'='*100}")
print(f"RESUMEN DE MATCHES")
print(f"{'='*100}")
print(f"\nTotal folios analizados: {len(folio_estimates)}")
print(f"Matches perfectos (100%): {len(perfect_matches)}")
for m in perfect_matches:
    print(f"  {m[0]} = {m[1]} ({m[2]} ingredientes)")

print(f"\nMatches fuertes (>=90%): {len(strong_matches)}")
for m in strong_matches:
    print(f"  {m[0]} ~ {m[1]} ({m[2]} ing hist, {m[3]} ing voyn, {m[4]:.1f}%)")

# Which recipes have NO match?
matched_recipes = set(m[1] for m in perfect_matches + strong_matches)
unmatched = [r for r, n in historical if r not in matched_recipes]
print(f"\nRecetas sin match fuerte: {len(unmatched)}")
for r in unmatched:
    n = [n for name, n in historical if name == r][0]
    print(f"  {r} ({n} ingredientes)")

# Which folios have NO good match?
well_matched_folios = set(m[0] for m in perfect_matches + strong_matches)
poorly_matched = [m for m in matches if m['Folio'] not in well_matched_folios]
print(f"\nFolios sin match fuerte (sim < 90%): {len(poorly_matched)}")
for m in sorted(poorly_matched, key=lambda x: -x['Best_Similarity']):
    print(f"  {m['Folio']}: est={m['Estimated_Ingredients']} ing, best={m['Best_Match']} ({m['Best_Match_N']} ing, {m['Best_Similarity']}%)")

# --- Step 5: Analyze WHICH STEMS appear in multiple matched folios ---
# This is critical for constraint propagation
print(f"\n{'='*100}")
print(f"STEMS COMPARTIDOS ENTRE FOLIOS CON MATCH PERFECTO/FUERTE")
print(f"{'='*100}")
print(f"(Stems que aparecen en 2+ folios matched -> restricciones cruzadas)")
print()

all_matched_folios = [m[0] for m in perfect_matches + strong_matches]
stem_to_matched_folios = defaultdict(set)

for folio in all_matched_folios:
    if folio in recipe_folio_profiles:
        prof = recipe_folio_profiles[folio]
        for stem in list(prof['excl_stems'].keys()) + list(prof['gen_stems'].keys()):
            stem_to_matched_folios[stem].add(folio)

# Stems in 2+ matched folios
multi_match_stems = {s: f for s, f in stem_to_matched_folios.items() if len(f) >= 2}
print(f"Stems presentes en 2+ folios matched: {len(multi_match_stems)}")
print()

for stem in sorted(multi_match_stems.keys(), key=lambda x: -len(multi_match_stems[x])):
    folios = multi_match_stems[stem]
    recipe_matches_for_folios = []
    for m in perfect_matches + strong_matches:
        if m[0] in folios:
            recipe_matches_for_folios.append(f"{m[0]}={m[1]}")
    
    stem_type = "EXCL" if stem in exclusive_stems else "GEN" if stem in generic_stems else "???"
    print(f"  [{stem}] ({stem_type}) -> {len(folios)} folios: {', '.join(recipe_matches_for_folios)}")

# --- CSV Output ---
csv_path = 'voynich_expanded_matching.csv'
with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=[
        'Folio', 'Total_Words', 'Unique_Stems', 'Botany_Stems',
        'Estimated_Ingredients', 'Best_Match', 'Best_Match_N',
        'Best_Similarity', 'Second_Match', 'Second_Match_N', 'Second_Similarity'
    ])
    writer.writeheader()
    writer.writerows(matches)

print(f"\n\nCSV guardado: {csv_path}")

# --- CSV of stems in matched folios ---
csv_path2 = 'voynich_stems_in_matched_folios.csv'
with open(csv_path2, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Stem', 'Type', 'N_Matched_Folios', 'Matched_Folios', 'Matched_Recipes'])
    for stem in sorted(multi_match_stems.keys(), key=lambda x: -len(multi_match_stems[x])):
        folios = multi_match_stems[stem]
        recipe_names = []
        for m in perfect_matches + strong_matches:
            if m[0] in folios:
                recipe_names.append(m[1])
        stem_type = "EXCL" if stem in exclusive_stems else "GEN" if stem in generic_stems else "UNK"
        writer.writerow([
            stem, stem_type, len(folios),
            ' | '.join(sorted(folios)),
            ' | '.join(recipe_names)
        ])

print(f"CSV de stems en folios matched: {csv_path2}")
print("\nDONE.")
