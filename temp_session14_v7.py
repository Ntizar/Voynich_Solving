#!/usr/bin/env python3
"""
Session 14 Part 2: Build v7 identification table + re-run matching.
Select only high-quality new identifications, build v7 CSV, and re-run content matching.
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
v6 = load_csv('voynich_unified_identifications_v6.csv')
corpus = load_csv('voynich_all_recipe_folio_stems.csv')
new_ids = load_csv('voynich_new_identifications_session14.csv')

recipe_ingredients = defaultdict(set)
for row in ingredients_flat:
    recipe_ingredients[row['Receta']].add(row['Ingrediente_Normalizado'])

folio_stems = defaultdict(set)
for row in corpus:
    folio_stems[row['Folio']].add(row['Stem'])

stem_folios = defaultdict(set)
for row in corpus:
    stem_folios[row['Stem']].add(row['Folio'])

all_folios = sorted(folio_stems.keys())

# ============================================================
# BUILD v7: Start from v6, add curated new identifications
# ============================================================

# Start with v6
v7 = []
for row in v6:
    v7.append(dict(row))

# Selection criteria for new identifications:
# 1. Zingiber: Only top stems with conf >= 75% (T3 quality) -> K1J1 (83%), K1K2 (80%)
# 2. Castoreum: Only stems with conf >= 75% from STRONG resolution -> top 9 stems
# 3. Petroselinum: All 3 stems at 90% confidence (NEW ingredient!)
# 4. Gentiana: Both stems at 90% confidence (NEW ingredient!)
# 5. Also add Opium stems from session 11 morphological analysis if we have strong ones

# Note: Q2A1B1A3 was listed as Opium-exclusive in session 11 (strong, 2+ opium folios, 0 cast)
# But here it resolves to Gentiana via intersection. Let's check...
# Q2A1B1A3 -> Gentiana at 90% from STRONG resolution. This overrides the weaker Opium signal.

print("="*80)
print("BUILDING v7 IDENTIFICATION TABLE")
print("="*80)

new_entries = []

# 1. ZINGIBER -- Top 2 stems with conf >= 80%
zingiber_stems = [
    ('K1J1', 83, 38, 'session14_intersection_UNIQUE', 'UNIQUE candidate across 10 diverse recipes. Only unidentified ingredient common to all: Zingiber. 38 folios, 100% presence, 67% absence. Top Zingiber stem.'),
    ('K1K2', 80, 37, 'session14_intersection_UNIQUE', 'UNIQUE candidate across 9 diverse recipes. Only unidentified ingredient common to all: Zingiber. 37 folios, 100% presence, 70% absence. Second Zingiber stem.'),
]

for stem, conf, nf, source, reasoning in zingiber_stems:
    new_entries.append({
        'Stem': stem, 'Ingredient': 'Zingiber', 'Confidence': str(conf),
        'Tier': '3', 'Source': source, 'Reasoning': reasoning
    })

# 2. CASTOREUM -- Top stems with conf >= 75% from STRONG resolution
castoreum_stems = [
    ('K1J1B1', 83, 26, 'session14_intersection_STRONG', 'Castoreum vs Zingiber: Castoreum wins by presence/absence differential. 26 folios, 100% presence, 67% absence.'),
    ('Q2A3', 82, 25, 'session14_intersection_STRONG', 'Castoreum vs Zingiber: Castoreum wins. 25 folios, 100% presence, 68% absence.'),
    ('K1U1', 79, 23, 'session14_intersection_STRONG', 'Castoreum vs Zingiber: Castoreum wins. 23 folios, 100% presence, 71% absence.'),
    ('A1Q2', 79, 23, 'session14_intersection_STRONG', 'Castoreum vs Zingiber: Castoreum wins. 23 folios, 100% presence, 71% absence.'),
    ('L1J1B1', 79, 23, 'session14_intersection_STRONG', 'Castoreum vs Zingiber: Castoreum wins. 23 folios, 100% presence, 71% absence.'),
    ('D1A1Q1K2B1', 78, 22, 'session14_intersection_STRONG', 'Castoreum vs Zingiber: Castoreum wins. 22 folios, 100% presence, 72% absence.'),
    ('B2A1', 77, 21, 'session14_intersection_STRONG', 'Castoreum vs Zingiber: Castoreum wins. 21 folios, 100% presence, 73% absence.'),
    ('B2Q1A3', 76, 20, 'session14_intersection_STRONG', 'Castoreum vs Zingiber: Castoreum wins. 20 folios, 100% presence, 74% absence.'),
    ('A1Q1K2B1', 75, 19, 'session14_intersection_STRONG', 'Castoreum vs Zingiber: Castoreum wins. 19 folios, 100% presence, 75% absence.'),
]

for stem, conf, nf, source, reasoning in castoreum_stems:
    new_entries.append({
        'Stem': stem, 'Ingredient': 'Castoreum', 'Confidence': str(conf),
        'Tier': '3', 'Source': source, 'Reasoning': reasoning
    })

# 3. PETROSELINUM -- 3 stems at 90% (NEW ingredient)
petroselinum_stems = [
    ('A1Q1K2Ba', 90, 9, 'session14_intersection_STRONG', 'Petroselinum vs Zingiber: Petroselinum wins decisively. 9 folios, 100% presence, only 39% absence. Petroselinum is rare enough to discriminate. NEW ingredient.'),
    ('A1Q2K1A1', 90, 8, 'session14_intersection_STRONG', 'Petroselinum vs Zingiber: Petroselinum wins. 8 folios, 100% presence, 41% absence. NEW ingredient.'),
    ('B1L1K2B1', 90, 3, 'session14_intersection_STRONG', 'Petroselinum vs Zingiber: Petroselinum wins. 3 folios, 100% presence, 48% absence. NEW ingredient.'),
]

for stem, conf, nf, source, reasoning in petroselinum_stems:
    new_entries.append({
        'Stem': stem, 'Ingredient': 'Petroselinum', 'Confidence': str(conf),
        'Tier': '3', 'Source': source, 'Reasoning': reasoning
    })

# 4. GENTIANA -- 2 stems at 90% (NEW ingredient)
gentiana_stems = [
    ('D1A1Q1K2Aa', 90, 3, 'session14_intersection_STRONG', 'Gentiana vs Zingiber: Gentiana wins decisively. 3 folios, 100% presence, only 18% absence. Gentiana is very rare -- only in antidote recipes. NEW ingredient.'),
    # Q2A1B1A3 was previously flagged as Opium-exclusive in morphological analysis.
    # But intersection analysis resolves it to Gentiana at 90%. This is because:
    # Its folios map to recipes where Gentiana is present but Opium is not always.
    # However -- we should be cautious. Let's add it but note the conflict.
    ('Q2A1B1A3', 85, 3, 'session14_intersection_STRONG_with_conflict', 'Gentiana vs Zingiber: Gentiana wins (100% presence, 18% absence). NOTE: Was flagged as Opium-exclusive in session 11 morphological analysis. Intersection method overrides: Gentiana fits recipe profile better. Present in antidote-type folios.'),
]

for stem, conf, nf, source, reasoning in gentiana_stems:
    new_entries.append({
        'Stem': stem, 'Ingredient': 'Gentiana', 'Confidence': str(conf),
        'Tier': '3', 'Source': source, 'Reasoning': reasoning
    })

# 5. PETROSELINUM extra: K1U1A3 at 90%
new_entries.append({
    'Stem': 'K1U1A3', 'Ingredient': 'Petroselinum', 'Confidence': '90',
    'Tier': '3', 'Source': 'session14_intersection_STRONG',
    'Reasoning': 'Petroselinum vs Zingiber: Petroselinum wins. 4 folios, 100% presence, 47% absence. NEW ingredient confirmation.'
})

print(f"\nAdding {len(new_entries)} new entries to v7:")
for e in new_entries:
    print(f"  {e['Stem']} -> {e['Ingredient']} ({e['Confidence']}%)")

# Add to v7
for e in new_entries:
    v7.append(e)

# Save v7
with open(os.path.join(ROOT, 'voynich_unified_identifications_v7.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['Stem','Ingredient','Confidence','Tier','Source','Reasoning'])
    w.writeheader()
    for row in v7:
        w.writerow(row)

print(f"\nv7 saved: {len(v7)} entries")

# Summary
v7_ingredients = set()
for row in v7:
    if row['Ingredient'] != 'FUNCTION_WORD':
        for sub in row['Ingredient'].split('|'):
            v7_ingredients.add(sub.strip())

print(f"Unique ingredients in v7: {len(v7_ingredients)}")
print(f"  {sorted(v7_ingredients)}")

# Count by ingredient
ing_counts = Counter()
for row in v7:
    if row['Ingredient'] != 'FUNCTION_WORD':
        ing_counts[row['Ingredient']] += 1
print(f"\nStems per ingredient:")
for ing, cnt in sorted(ing_counts.items(), key=lambda x: -x[1]):
    print(f"  {ing}: {cnt}")

# ============================================================
# RE-RUN CONTENT MATCHING WITH v7
# ============================================================

print("\n" + "="*80)
print("RE-RUNNING CONTENT MATCHING WITH v7")
print("="*80)

# Build v7 ident map
v7_ident = {}
for row in v7:
    v7_ident[row['Stem']] = row['Ingredient']

# All identified ingredients in v7
v7_id_ingredients = set()
for v in v7_ident.values():
    if v != 'FUNCTION_WORD':
        for sub in v.split('|'):
            v7_id_ingredients.add(sub.strip())

def compute_f1_v7(folio, recipe_ings):
    folio_identified = set()
    for stem in folio_stems.get(folio, set()):
        if stem in v7_ident:
            ing = v7_ident[stem]
            if ing != 'FUNCTION_WORD':
                for sub in ing.split('|'):
                    folio_identified.add(sub.strip())
    
    if not folio_identified or not recipe_ings:
        return 0.0, set(), set(), 0, 0
    
    tp = folio_identified & recipe_ings
    fp = folio_identified - recipe_ings
    fn = (recipe_ings & v7_id_ingredients) - folio_identified
    
    precision = len(tp) / (len(tp) + len(fp)) if (len(tp) + len(fp)) > 0 else 0
    recall = len(tp) / (len(tp) + len(fn)) if (len(tp) + len(fn)) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    return f1 * 100, tp, fp, len(tp), len(fn)

# Match each folio against all 50 recipes
matching_results = []
expanded_results = []

for folio in all_folios:
    best_f1 = 0
    best_recipe = ''
    best_tp = set()
    best_fp = set()
    
    folio_results = []
    for recipe in recipes_main:
        rname = recipe['Nombre_Receta']
        rings = recipe_ingredients[rname]
        f1, tp, fp, n_tp, n_fn = compute_f1_v7(folio, rings)
        folio_results.append((rname, f1, n_tp, tp, fp))
        
        if f1 > best_f1:
            best_f1 = f1
            best_recipe = rname
            best_tp = tp
            best_fp = fp
    
    # Count identified ingredients in this folio
    folio_ings = set()
    for stem in folio_stems.get(folio, set()):
        if stem in v7_ident and v7_ident[stem] != 'FUNCTION_WORD':
            for sub in v7_ident[stem].split('|'):
                folio_ings.add(sub.strip())
    
    n_matched = len(best_tp)
    precision = n_matched / len(folio_ings) * 100 if folio_ings else 0
    recall_ings = best_tp & recipe_ingredients.get(best_recipe, set()) & v7_id_ingredients
    n_possible = len(recipe_ingredients.get(best_recipe, set()) & v7_id_ingredients)
    recall = n_matched / n_possible * 100 if n_possible else 0
    
    matching_results.append({
        'Folio': folio,
        'Best_Recipe': best_recipe,
        'F1': best_f1,
        'N_Matched': n_matched,
        'Precision': precision,
        'Recall': recall,
        'TP_Ingredients': ' | '.join(sorted(best_tp)),
        'FP_Ingredients': ' | '.join(sorted(best_fp))
    })
    
    # Expanded: all recipe scores for this folio
    for rname, f1, n_tp, tp, fp in folio_results:
        expanded_results.append({
            'Folio': folio,
            'Recipe': rname,
            'F1': f1,
            'N_TP': n_tp
        })

# Save matching v7
with open(os.path.join(ROOT, 'voynich_matching_v7.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['Folio','Best_Recipe','F1','N_Matched','Precision','Recall','TP_Ingredients','FP_Ingredients'])
    w.writeheader()
    for r in matching_results:
        w.writerow({k: f"{v:.1f}" if isinstance(v, float) else v for k, v in r.items()})

# Save expanded
with open(os.path.join(ROOT, 'voynich_expanded_matching_v7.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['Folio','Recipe','F1','N_TP'])
    w.writeheader()
    for r in expanded_results:
        w.writerow({k: f"{v:.1f}" if isinstance(v, float) else v for k, v in r.items()})

# Save top 5 per folio
with open(os.path.join(ROOT, 'voynich_matching_v7_top5.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['Folio','Rank','Recipe','F1','N_TP'])
    for folio in all_folios:
        folio_exp = [(r['Recipe'], r['F1'], r['N_TP']) for r in expanded_results if r['Folio'] == folio]
        folio_exp.sort(key=lambda x: -x[1])
        for i, (rname, f1, ntp) in enumerate(folio_exp[:5]):
            w.writerow([folio, i+1, rname, f"{f1:.1f}", ntp])

# Print summary
print("\n--- Matching v7 Summary ---")
f1_vals = [r['F1'] for r in matching_results if r['F1'] > 0]
excellent = [r for r in matching_results if r['F1'] >= 80]
good = [r for r in matching_results if 50 <= r['F1'] < 80]
moderate = [r for r in matching_results if 30 <= r['F1'] < 50]
weak = [r for r in matching_results if 0 < r['F1'] < 30]
insuf = [r for r in matching_results if r['F1'] == 0]

print(f"  EXCELLENT (F1>=80%): {len(excellent)} folios")
for r in sorted(excellent, key=lambda x: -x['F1']):
    print(f"    {r['Folio']}: {r['F1']:.1f}% -> {r['Best_Recipe']} (TP: {r['TP_Ingredients']})")

print(f"  GOOD (50-80%): {len(good)} folios")
print(f"  MODERATE (30-50%): {len(moderate)} folios")
print(f"  WEAK (<30%): {len(weak)} folios")
print(f"  INSUFFICIENT (0%): {len(insuf)} folios")
print(f"  Mean F1 (non-zero): {sum(f1_vals)/len(f1_vals):.1f}%")

# Recipe frequency
recipe_freq = Counter(r['Best_Recipe'] for r in matching_results if r['F1'] > 0)
print(f"\nMost frequent best-match recipes:")
for rname, cnt in recipe_freq.most_common(10):
    print(f"  {rname}: {cnt} folios")

# Comparison with v6
print(f"\n--- Comparison v6 vs v7 ---")
print(f"  v6: 58 stems, 17 unique ingredients")
print(f"  v7: {len(v7)} stems, {len(v7_ingredients)} unique ingredients")
print(f"  New stems: +{len(new_entries)}")
print(f"  New ingredients: Zingiber, Castoreum, Petroselinum, Gentiana")
print(f"  v6 EXCELLENT: 0, v7 EXCELLENT: {len(excellent)}")
print(f"  v6 GOOD: 37, v7 GOOD: {len(good)}")
print(f"  v6 Mean F1: 54.3%, v7 Mean F1: {sum(f1_vals)/len(f1_vals):.1f}%")

print(f"\nSaved: voynich_unified_identifications_v7.csv")
print(f"Saved: voynich_matching_v7.csv")
print(f"Saved: voynich_expanded_matching_v7.csv")
print(f"Saved: voynich_matching_v7_top5.csv")
