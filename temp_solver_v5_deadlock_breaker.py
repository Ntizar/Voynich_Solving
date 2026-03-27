#!/usr/bin/env python3
"""
VOYNICH SOLVER v5: DEADLOCK BREAKER
=====================================
Three parallel attacks:

ATTACK 1: Break Opium/Castoreum deadlock
  - Requies Magna has Opium but NOT Castoreum
  - Pillulae Fetidae has Castoreum but NOT Opium
  - Find folios that could match these and check which deadlocked stems appear/don't appear

ATTACK 2: Exploit f87v (Ung. Apostolorum) exclusive stems  
  - 9/12 ingredients still unidentified
  - Many are HIGHLY distinctive (Aristolochia, Opopanax, Litharge, Verdigris)
  - Stems exclusive to f87v can be mapped

ATTACK 3: Validate Zingiber/Mel with Diamargariton contradiction
  - Diamargariton has NEITHER Zingiber NOR Mel despumatum
  - Any Zingiber/Mel stem appearing in f100r (=Diamargariton) is a FALSE POSITIVE
  - This validates our pair and potentially identifies frequency differences

ATTACK 4: Co-occurrence differential analysis
  - For each pair of "adjacent" recipes (one has ingredient X, other doesn't),
    identify stems that appear in one folio but not the other
  - These stems are strong candidates for ingredient X
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import csv
import os
from collections import defaultdict

BASE = r'C:\Ntizar_Obsidian\Ntizar_Brain\MASTERTMIND'

# ============================================================
# LOAD ALL DATA
# ============================================================
recipe_ingredients = defaultdict(set)
ingredient_category = {}
ingredient_recipes = defaultdict(set)

with open(os.path.join(BASE, 'recetas_historicas_ingredientes_flat.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        rname = row['Receta'].split('(')[0].strip()
        ing = row['Ingrediente_Normalizado']
        recipe_ingredients[rname].add(ing)
        ingredient_category[ing] = row['Categoria']
        ingredient_recipes[ing].add(rname)

stem_data = {}
with open(os.path.join(BASE, 'voynich_stems_in_matched_folios.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        stem = row['Stem']
        folios = [x.strip() for x in row['Matched_Folios'].split('|')]
        stem_data[stem] = {'type': row['Type'], 'folios': folios}

# Load current best identifications
current_ids = {}
with open(os.path.join(BASE, 'voynich_unified_identifications_v4c.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        current_ids[row['Stem']] = row

already_identified_ings = set()
for row in current_ids.values():
    ing = row['Ingredient']
    if ing != 'FUNCTION_WORD':
        for i in ing.split('|'):
            already_identified_ings.add(i.strip())

# Load expanded matching
folio_matches = {}
with open(os.path.join(BASE, 'voynich_expanded_matching.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        folio_matches[row['Folio']] = row

# Load v3 results for detailed scores
v3_results = {}
with open(os.path.join(BASE, 'voynich_constraint_solver_v3_results.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        v3_results[row['Stem']] = row

# Perfect and strong matches
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

# Build folio->stem index (reverse of stem_data)
folio_stems = defaultdict(set)
for stem, data in stem_data.items():
    for fol in data['folios']:
        folio_stems[fol].add(stem)


print("=" * 80)
print("VOYNICH SOLVER v5: DEADLOCK BREAKER")
print("=" * 80)

# ============================================================
# ATTACK 1: OPIUM/CASTOREUM DEADLOCK
# ============================================================
print("\n" + "=" * 80)
print("ATTACK 1: OPIUM/CASTOREUM DEADLOCK BREAKER")
print("=" * 80)

# Key insight:
# Requies Magna: has Opium, NOT Castoreum
# Pillulae Fetidae: has Castoreum, NOT Opium
# If we can identify which folios match these recipes,
# stems present in Requies=folio but absent from Pillulae=folio -> Opium candidates
# stems present in Pillulae=folio but absent from Requies=folio -> Castoreum candidates

# Check which folios have Requies Magna or Pillulae Fetidae as potential matches
print("\n--- Folios with Requies Magna as 2nd best match ---")
requies_folios = []
for folio, data in folio_matches.items():
    if 'Requies' in data.get('Second_Match', ''):
        sim = float(data['Second_Similarity'])
        best = data['Best_Match']
        best_sim = float(data['Best_Similarity'])
        est_ing = int(data['Estimated_Ingredients'])
        print(f"  {folio}: Best={best}({best_sim}%), Requies=2nd({sim}%), Est.Ingredients={est_ing}")
        if sim >= 85:
            requies_folios.append(folio)

# Requies Magna: 17 ingredients 
# Opium, Mandragora, Hyoscyamus, Papaver album, Lactuca, Psyllium, 
# Gummi arabicum, Amylum, Tragacantha, Glycyrrhiza
# Rosa, Cinnamomum, Nux moschata, Crocus, Camphor
# Saccharum, Aqua rosarum
requies_ings = recipe_ingredients.get('Requies Magna', set())
philonium_ings = recipe_ingredients.get('Philonium Persicum', set())

print(f"\nRequies Magna ingredients ({len(requies_ings)}): {sorted(requies_ings)}")
print(f"\nDISCRIMINATORS between Philonium Persicum and Requies Magna:")
print(f"  In Requies but NOT Philonium: {sorted(requies_ings - philonium_ings)}")
print(f"  In Philonium but NOT Requies: {sorted(philonium_ings - requies_ings)}")

# CRITICAL INSIGHT:
# f88v, f95v, f96r all match Philonium(94.7%) and Requies(89.5%)
# Both have Opium. Only Philonium has Castoreum; Requies does NOT.
# So: if Requies is the TRUE match for some folio, stems there mapping to 
# Castoreum would be ABSENT.
# 
# But we ASSIGNED these to Philonium, not Requies. Let's check:
# The similarity gap is small (94.7 vs 89.5 = 5.2 pts).
# What if some of these ARE actually Requies Magna?

# Better approach: Differential analysis
# Philonium has: Castoreum, Pyrethrum, Euphorbium, Nardus indica, Hypocistis, 
#                Gummi arabicum, Styrax, Casia, Cardamomum
# Requies has:   Mandragora, Hyoscyamus, Papaver album, Lactuca, Psyllium,
#                Gummi arabicum, Amylum, Tragacantha, Glycyrrhiza, 
#                Rosa, Nux moschata, Camphor, Saccharum, Aqua rosarum

# Shared: Opium, Crocus, Piper longum, Piper nigrum, Zingiber, Cinnamomum, Myrrha
# Wait-- Requies does NOT have these spices! Let me re-check...

print("\n--- DETAILED DISCRIMINATOR ANALYSIS ---")
# Requies Magna ingredients:
# ACTIVO: Opium, Mandragora, Hyoscyamus, Papaver album, Lactuca, Psyllium, Gummi arabicum, Amylum, Tragacantha, Glycyrrhiza
# ESPECIA: Rosa, Cinnamomum, Nux moschata, Crocus, Camphor
# BASE: Saccharum, Aqua rosarum
# NOTE: Requies does NOT have Castoreum, Piper, Zingiber, Myrrha, Casia, etc.

philonium_only = philonium_ings - requies_ings
requies_only = requies_ings - philonium_ings
shared = philonium_ings & requies_ings

print(f"\n  SHARED ingredients ({len(shared)}):")
for ing in sorted(shared):
    print(f"    {ing}")
print(f"\n  PHILONIUM-ONLY ingredients ({len(philonium_only)}):")
for ing in sorted(philonium_only):
    print(f"    {ing}")
print(f"\n  REQUIES-ONLY ingredients ({len(requies_only)}):")
for ing in sorted(requies_only):
    print(f"    {ing}")

# Now: for each "Philonium-matched" folio, check if stems identified as 
# Castoreum/Opium cluster can be split
print("\n--- CROSS-FOLIO DIFFERENTIAL FOR OPIUM vs CASTOREUM ---")
print("\nStrategy: Compare folios matched to Philonium (has BOTH Opium+Castoreum)")
print("with folios matched to Requies (has Opium but NOT Castoreum).")
print("If we had a Requies-matched folio, stems PRESENT there but NOT in")
print("Castoreum-only recipes would indicate Opium.")

# Actually, let's use a different approach:
# Pillulae Fetidae: Castoreum but NOT Opium
# Look at ALL 23 recipes for Opium vs Castoreum distribution
print("\n--- RECIPE DISTRIBUTION: OPIUM vs CASTOREUM ---")
opium_set = set()
castoreum_set = set()
for rname, ings in recipe_ingredients.items():
    if 'Opium' in ings:
        opium_set.add(rname)
    if 'Castoreum' in ings:
        castoreum_set.add(rname)

print(f"\nOpium in ({len(opium_set)}): {sorted(opium_set)}")
print(f"Castoreum in ({len(castoreum_set)}): {sorted(castoreum_set)}")
print(f"\nOpium ONLY (not Castoreum): {sorted(opium_set - castoreum_set)}")
print(f"Castoreum ONLY (not Opium): {sorted(castoreum_set - opium_set)}")
print(f"Both: {sorted(opium_set & castoreum_set)}")

# Within our MATCHED recipes:
opium_matched = set()
castoreum_matched = set()
for folio, recipe in ALL_MATCHED.items():
    ings = recipe_ingredients.get(recipe, set())
    if 'Opium' in ings:
        opium_matched.add(folio)
    if 'Castoreum' in ings:
        castoreum_matched.add(folio)

no_opium_no_castoreum = set(ALL_MATCHED.keys()) - opium_matched - castoreum_matched
print(f"\nIn MATCHED folios:")
print(f"  Opium+Castoreum folios ({len(opium_matched & castoreum_matched)})")
print(f"  No Opium, No Castoreum folios ({len(no_opium_no_castoreum)}): {sorted(no_opium_no_castoreum)}")

# Key: f87r (Confectio Hamech), f87v (Ung.Apostolorum), f96v (Pillulae Aureae), 
# f100r (Diamargariton), f100v (Diaciminum) -- NONE have Opium or Castoreum.
# ALL Philonium, Aurea, Trifera, Diascordium folios have BOTH.
# So within our matched set, Opium and Castoreum profiles are IDENTICAL.
# The deadlock is REAL -- we literally cannot break it without matching a folio to 
# Requies Magna (Opium only) or Pillulae Fetidae (Castoreum only).

# BUT: Can we match any unmatched folios to these?
# Pillulae Fetidae has only 8 ingredients (small recipe).
# Look for folios with ~8 unique stems that might match.
print("\n--- SEARCHING FOR PILLULAE FETIDAE / REQUIES MAGNA CANDIDATE FOLIOS ---")
pillulae_fetidae_ings = recipe_ingredients.get('Pillulae Fetidae', set())
print(f"\nPillulae Fetidae ({len(pillulae_fetidae_ings)}): {sorted(pillulae_fetidae_ings)}")

# Pillulae Fetidae: Opopanax, Galbanum, Sagapenum, Castoreum, Asa foetida, Myrrha, Bdellium, Succo rutae
# Check if K1K2A1 (=Galbanum) appears in any small folios not yet matched
print("\nFolios where K1K2A1 (=Galbanum) appears:")
galbanum_folios = stem_data.get('K1K2A1', {}).get('folios', [])
for fol in sorted(galbanum_folios):
    recipe = ALL_MATCHED.get(fol, '?')
    est_ing = folio_matches.get(fol, {}).get('Estimated_Ingredients', '?')
    print(f"  {fol}: matched={recipe}, est_ingredients={est_ing}")

# Pillulae Fetidae is very distinctive: all gum-resins + Castoreum + Myrrha
# D1 and P1K1K2 are mapped to Bdellium
# Myrrha stems: A1Q2A1, D1A1, D1A1A3, Q1K1A1, A1Q1J1, T1J1A1B1A3
# K1K2A1 = Galbanum

# Check: is there a folio that has K1K2A1 + Bdellium stems + Myrrha stems 
# but NOT the Opium cluster?
print("\n--- CHECKING FOLIO-LEVEL INGREDIENT SIGNATURES FOR PILLULAE FETIDAE ---")
myrrha_stems = [s for s, row in current_ids.items() if row['Ingredient'] == 'Myrrha']
bdellium_stems = [s for s, row in current_ids.items() if row['Ingredient'] == 'Bdellium']
galbanum_stems = [s for s, row in current_ids.items() if row['Ingredient'] == 'Galbanum']

print(f"  Myrrha stems: {myrrha_stems}")
print(f"  Bdellium stems: {bdellium_stems}")
print(f"  Galbanum stems: {galbanum_stems}")

# For each folio, count how many Pillulae Fetidae "signature" ingredients are present
pf_signature = galbanum_stems + myrrha_stems + bdellium_stems
for folio in sorted(folio_stems.keys()):
    pf_count = sum(1 for s in pf_signature if s in folio_stems[folio])
    total_stems = len(folio_stems[folio])
    if pf_count >= 3:
        recipe = ALL_MATCHED.get(folio, 'UNMATCHED')
        print(f"  {folio}: {pf_count}/{len(pf_signature)} PF-signature stems, "
              f"total stems={total_stems}, matched={recipe}")

# ============================================================
# ATTACK 2: EXPLOIT f87v (UNGUENTUM APOSTOLORUM)
# ============================================================
print("\n\n" + "=" * 80)
print("ATTACK 2: f87v (UNGUENTUM APOSTOLORUM) EXCLUSIVE STEMS")
print("=" * 80)

# Ung. Apostolorum: 12 ingredients
# ALREADY IDENTIFIED: Galbanum (K1K2A1), Myrrha (6 stems), Bdellium (D1, P1K1K2)
# That's 3/12 identified.
# REMAINING 9: Aristolochia longa, Aristolochia rotunda, Opopanax, 
#              Verdigris, Litharge, Olibanum, Cera, Oleum olivarum, Resina pini

ua_recipe = 'Unguentum Apostolorum'
ua_ings = recipe_ingredients.get(ua_recipe, set())
ua_identified = ua_ings & already_identified_ings
ua_remaining = ua_ings - already_identified_ings

print(f"\nUng. Apostolorum total ingredients: {len(ua_ings)}")
print(f"Already identified: {len(ua_identified)}: {sorted(ua_identified)}")
print(f"Remaining unidentified: {len(ua_remaining)}:")
for ing in sorted(ua_remaining):
    cat = ingredient_category.get(ing, '?')
    # In how many of our 23 recipes does this ingredient appear?
    in_recipes = ingredient_recipes.get(ing, set())
    print(f"  [{cat:8s}] {ing:25s} (in {len(in_recipes)} recipes: {sorted(in_recipes)})")

print(f"\n--- Stems in f87v ---")
f87v_stems = folio_stems.get('f87v', set())
print(f"Total stems in f87v: {len(f87v_stems)}")

# Categorize stems
identified_here = set()
function_words = set()
unidentified = set()

for stem in sorted(f87v_stems):
    if stem in current_ids:
        if current_ids[stem]['Ingredient'] == 'FUNCTION_WORD':
            function_words.add(stem)
        else:
            identified_here.add(stem)
    else:
        unidentified.add(stem)

print(f"  Already identified (ingredient): {len(identified_here)}")
for s in sorted(identified_here):
    print(f"    {s} = {current_ids[s]['Ingredient']} ({current_ids[s]['Confidence']}%)")
print(f"  Function words: {len(function_words)}")
print(f"  UNIDENTIFIED: {len(unidentified)}")

# For unidentified stems in f87v, check which OTHER folios they appear in
print(f"\n--- UNIDENTIFIED STEMS: CROSS-FOLIO ANALYSIS ---")
exclusive_to_f87v = []
multi_folio = []

for stem in sorted(unidentified):
    if stem in stem_data:
        other_folios = [f for f in stem_data[stem]['folios'] if f != 'f87v']
        other_recipes = set()
        for fol in other_folios:
            if fol in ALL_MATCHED:
                other_recipes.add(ALL_MATCHED[fol])
        
        # Candidate = intersection of UA ingredients with all other recipe ingredients
        candidates = set(ua_ings)
        for r in other_recipes:
            candidates &= recipe_ingredients.get(r, set())
        candidates -= already_identified_ings
        
        if len(other_folios) == 0:
            exclusive_to_f87v.append((stem, candidates))
            print(f"  ** EXCLUSIVE ** {stem:25s} -> {len(candidates)} candidates: {sorted(candidates)}")
        else:
            print(f"  {stem:25s} ({len(other_folios)} other folios, {len(other_recipes)} recipes) "
                  f"-> {len(candidates)} candidates: {sorted(candidates)[:6]}")
            multi_folio.append((stem, candidates, other_recipes))
    else:
        # Stem not in stem_data (appears in only 1 matched folio = f87v)
        exclusive_to_f87v.append((stem, ua_remaining))
        print(f"  ** EXCLUSIVE ** {stem:25s} -> {len(ua_remaining)} candidates (all remaining)")

print(f"\n--- EXCLUSIVE STEMS SUMMARY ---")
print(f"Stems exclusive to f87v (only matched folio): {len(exclusive_to_f87v)}")
print(f"These can ONLY be one of {len(ua_remaining)} remaining UA ingredients:")
for ing in sorted(ua_remaining):
    print(f"  {ing}")

if len(exclusive_to_f87v) > 0 and len(ua_remaining) > 0:
    # If #exclusive_stems <= #remaining_ingredients, each exclusive stem maps to one ingredient
    # If #exclusive_stems > #remaining_ingredients, some stems are function words or variants
    ratio = len(exclusive_to_f87v) / len(ua_remaining) if ua_remaining else 0
    print(f"\nRatio exclusive stems / remaining ingredients: {len(exclusive_to_f87v)}/{len(ua_remaining)} = {ratio:.1f}")
    if ratio <= 1.5:
        print("  -> Good ratio! Most exclusive stems likely map 1:1 to ingredients.")
    else:
        print("  -> High ratio. Some exclusive stems are likely function words or morphological variants.")

# For multi-folio stems, check if any reduce to a SINGLE candidate
print(f"\n--- MULTI-FOLIO STEMS WITH STRONG CONSTRAINTS ---")
new_identifications = []
for stem, candidates, other_recipes in multi_folio:
    if len(candidates) == 1:
        ing = list(candidates)[0]
        print(f"  *** UNIQUE *** {stem:25s} -> {ing} (appears in UA + {sorted(other_recipes)})")
        new_identifications.append((stem, ing, 'ua_unique_intersection', other_recipes))
    elif len(candidates) == 2:
        print(f"  ** PAIR ** {stem:25s} -> {sorted(candidates)}")

# Also check: stems in f87v that are NOT in stem_data but appear in the raw corpus
# These are stems that only appear in f87v among ALL recipe folios

# ============================================================
# ATTACK 3: ZINGIBER/MEL DIAMARGARITON CONTRADICTION TEST
# ============================================================
print("\n\n" + "=" * 80)
print("ATTACK 3: ZINGIBER/MEL DIAMARGARITON CONTRADICTION TEST")  
print("=" * 80)

# Diamargariton (f100r) has NEITHER Zingiber NOR Mel despumatum
# Any stem from the Zingiber/Mel pair appearing in f100r is:
#   a) A function word (misidentified as Zingiber/Mel)
#   b) OR: the folio match is wrong

zingiber_mel_stems = [s for s, row in current_ids.items() 
                      if 'Zingiber' in row['Ingredient'] or 'Mel' in row['Ingredient']]

print(f"\nZingiber/Mel stems: {zingiber_mel_stems}")
print(f"f100r (Diamargariton) stems: {len(folio_stems.get('f100r', set()))}")

contradiction_count = 0
for stem in zingiber_mel_stems:
    in_f100r = stem in folio_stems.get('f100r', set())
    if in_f100r:
        print(f"  !! CONTRADICTION: {stem} appears in f100r (Diamargariton has no Zingiber/Mel)")
        contradiction_count += 1
    else:
        print(f"  OK: {stem} NOT in f100r (consistent)")

if contradiction_count == 0:
    print(f"\n  All {len(zingiber_mel_stems)} Zingiber/Mel stems pass the Diamargariton test!")
else:
    print(f"\n  {contradiction_count} contradictions found -- these stems need reclassification")

# Additional validation: check against Pillulae Aureae (f96v) -- no Zingiber, no Mel
print("\nValidation against f96v (Pillulae Aureae, no Zingiber/Mel):")
for stem in zingiber_mel_stems:
    in_f96v = stem in folio_stems.get('f96v', set())
    if in_f96v:
        print(f"  !! CONTRADICTION: {stem} appears in f96v")
    else:
        print(f"  OK: {stem} NOT in f96v")

# Validation: check against Ung. Apostolorum (f87v) -- no Zingiber, no Mel
print("\nValidation against f87v (Ung. Apostolorum, no Zingiber/Mel):")
for stem in zingiber_mel_stems:
    in_f87v = stem in folio_stems.get('f87v', set())
    if in_f87v:
        print(f"  !! CONTRADICTION: {stem} appears in f87v")
    else:
        print(f"  OK: {stem} NOT in f87v")

# Now: frequency analysis
# If we had token frequencies per folio, Mel (being a base/vehicle) might appear
# more often per folio than Zingiber (a single spice ingredient).
# Let's check raw token counts from the corpus.

# ============================================================
# ATTACK 4: DIFFERENTIAL ANALYSIS -- NEW IDENTIFICATIONS 
# ============================================================
print("\n\n" + "=" * 80)
print("ATTACK 4: SYSTEMATIC DIFFERENTIAL ANALYSIS")
print("=" * 80)

# For each unidentified ingredient in our matched recipes,
# find which folios SHOULD have it vs SHOULD NOT.
# Then look at stems present in SHOULD-HAVE but absent from SHOULD-NOT.

# Focus on ingredients NOT yet identified
all_possible_ings = set()
for recipe in ALL_MATCHED.values():
    all_possible_ings |= recipe_ingredients.get(recipe, set())

unidentified_ings = all_possible_ings - already_identified_ings
print(f"\nTotal possible ingredients across all matched recipes: {len(all_possible_ings)}")
print(f"Already identified: {len(already_identified_ings)}")
print(f"Remaining unidentified: {len(unidentified_ings)}")

# For each unidentified ingredient, calculate differential
print(f"\n--- DIFFERENTIAL CANDIDATES FOR KEY UNIDENTIFIED INGREDIENTS ---\n")

best_differentials = []

for ing in sorted(unidentified_ings):
    # Which matched folios SHOULD have this ingredient?
    should_have = set()
    should_not = set()
    for folio, recipe in ALL_MATCHED.items():
        r_ings = recipe_ingredients.get(recipe, set())
        if ing in r_ings:
            should_have.add(folio)
        else:
            should_not.add(folio)
    
    if len(should_have) == 0 or len(should_not) == 0:
        continue  # No differential power
    
    # Find stems present in ALL should_have folios but NONE of should_not
    # (This is the strongest possible differential signal)
    # Relax: present in >=70% of should_have, absent from >=70% of should_not
    
    for stem in stem_data:
        if stem in current_ids:
            continue  # Already identified
        
        stem_fols = set(stem_data[stem]['folios'])
        
        # How many should_have folios contain this stem?
        in_should = stem_fols & should_have
        in_shouldnt = stem_fols & should_not
        
        pct_pos = len(in_should) / len(should_have) if should_have else 0
        pct_neg = len(in_shouldnt) / len(should_not) if should_not else 0
        
        # Strong signal: high positive rate, low negative rate
        if pct_pos >= 0.5 and pct_neg <= 0.15 and len(in_should) >= 2:
            score = pct_pos * (1 - pct_neg)
            best_differentials.append({
                'stem': stem,
                'ingredient': ing,
                'score': score,
                'pct_pos': pct_pos,
                'pct_neg': pct_neg,
                'in_should': len(in_should),
                'total_should': len(should_have),
                'in_shouldnt': len(in_shouldnt),
                'total_shouldnt': len(should_not),
            })

# Sort by score
best_differentials.sort(key=lambda x: -x['score'])

# Print top results
print(f"Found {len(best_differentials)} strong differential signals")
print(f"\nTop 40 differential candidates:")
print(f"{'Stem':25s} {'Ingredient':25s} {'Score':>6s} {'Pos':>8s} {'Neg':>8s}")
print("-" * 80)

seen_stems = set()
for d in best_differentials[:60]:
    if d['stem'] in seen_stems and d['score'] < 0.8:
        continue
    seen_stems.add(d['stem'])
    print(f"{d['stem']:25s} {d['ingredient']:25s} {d['score']:6.3f} "
          f"{d['in_should']}/{d['total_should']:>2d}={d['pct_pos']:.0%}  "
          f"{d['in_shouldnt']}/{d['total_shouldnt']:>2d}={d['pct_neg']:.0%}")
    if len(seen_stems) >= 40:
        break

# ============================================================
# ATTACK 5: OLIBANUM TARGETING
# ============================================================
print("\n\n" + "=" * 80)
print("ATTACK 5: OLIBANUM TARGETING")
print("=" * 80)

# Olibanum (Frankincense) has a DISTINCTIVE profile:
# In: Ung. Apostolorum (f87v), Ung. Basilicon, Dialtea, Theriac Magna
# Among our matched recipes: only Ung. Apostolorum (f87v)!
# So Olibanum stems should appear in f87v but NOT in most other matched folios.
# This is almost like a "f87v-exclusive" ingredient.

olibanum_recipes = ingredient_recipes.get('Olibanum', set())
print(f"\nOlibanum in recipes: {sorted(olibanum_recipes)}")
print(f"Among our matched recipes: {sorted(olibanum_recipes & set(ALL_MATCHED.values()))}")

# Olibanum is in Ung.Apostolorum, Ung.Basilicon, Dialtea, Theriac Magna
# Only Ung.Apostolorum is in our matched set.
# So stems for Olibanum should appear in f87v and potentially in the 
# large Theriac-like folios (f89r/f89v which are close to Theriac/Mithridatium)

# Check: which stems appear in f87v but in very few other matched folios?
print("\nStems appearing in f87v and <=1 other matched folio (Olibanum candidates):")
for stem in sorted(folio_stems.get('f87v', set())):
    if stem in current_ids:
        continue
    matched_fols = set(stem_data.get(stem, {}).get('folios', [])) & set(ALL_MATCHED.keys())
    if 1 <= len(matched_fols) <= 2 and 'f87v' in matched_fols:
        other = matched_fols - {'f87v'}
        print(f"  {stem:25s} also in: {sorted(other) if other else 'NOWHERE ELSE'}")

# ============================================================
# SUMMARY: NEW IDENTIFICATIONS FROM v5
# ============================================================
print("\n\n" + "=" * 80)
print("SUMMARY: NEW v5 IDENTIFICATIONS")
print("=" * 80)

# Collect all new identifications from attacks 2 and 4
all_new = []

# From Attack 2 (f87v unique intersection)
for stem, ing, source, recipes in new_identifications:
    all_new.append({
        'Stem': stem,
        'Ingredient': ing,
        'Confidence': 80,
        'Tier': 3,
        'Source': source,
        'Reasoning': f"Unique intersection of UA + {sorted(recipes)}. Only {ing} survives elimination."
    })

# From Attack 4 (differential analysis) -- only top-scoring with score >= 0.9
# and not already captured
already_new = set(x['Stem'] for x in all_new)
for d in best_differentials:
    if d['stem'] in already_new or d['stem'] in current_ids:
        continue
    if d['score'] >= 0.85 and d['pct_neg'] == 0:
        # Check if this stem already has a higher-scoring assignment
        existing = [x for x in all_new if x['Stem'] == d['stem']]
        if not existing:
            conf = int(min(95, 70 + d['score'] * 25))
            all_new.append({
                'Stem': d['stem'],
                'Ingredient': d['ingredient'],
                'Confidence': conf,
                'Tier': 3 if d['score'] >= 0.9 else 4,
                'Source': 'differential_v5',
                'Reasoning': f"Present in {d['in_should']}/{d['total_should']} should-have folios, "
                             f"0/{d['total_shouldnt']} should-not. Score={d['score']:.3f}"
            })
            already_new.add(d['stem'])

print(f"\nNew identifications from v5: {len(all_new)}")
for item in all_new:
    print(f"  {item['Stem']:25s} = {item['Ingredient']:25s} ({item['Confidence']}%, {item['Source']})")

# Write new CSV (v5)
v5_results = []

# Import all v4c results
for stem, row in current_ids.items():
    v5_results.append({
        'Stem': stem,
        'Ingredient': row['Ingredient'],
        'Confidence': int(row['Confidence']),
        'Tier': int(row['Tier']),
        'Source': row['Source'],
        'Reasoning': row['Reasoning'],
    })

# Add v5 results (only if stem not already in v4c)
existing_stems = set(r['Stem'] for r in v5_results)
for item in all_new:
    if item['Stem'] not in existing_stems:
        v5_results.append(item)
        existing_stems.add(item['Stem'])

v5_results.sort(key=lambda x: (x['Tier'], -x['Confidence']))

# Stats
ingredient_counts = defaultdict(int)
for r in v5_results:
    if r['Ingredient'] != 'FUNCTION_WORD':
        for ing in r['Ingredient'].split('|'):
            ingredient_counts[ing.strip()] += 1

all_ings_v5 = set(ingredient_counts.keys())
print(f"\n--- v5 SUMMARY ---")
print(f"Total entries: {len(v5_results)}")
print(f"  v4c entries: {len(current_ids)}")
print(f"  New v5 entries: {len(v5_results) - len(current_ids)}")
print(f"Unique ingredients: {len(all_ings_v5)}")

out_path = os.path.join(BASE, 'voynich_unified_identifications_v5.csv')
with open(out_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['Stem', 'Ingredient', 'Confidence', 'Tier', 'Source', 'Reasoning'])
    writer.writeheader()
    for r in v5_results:
        writer.writerow(r)

print(f"\nSaved to: {out_path}")

# Coverage analysis for v5
print("\n--- v5 COVERAGE PER PERFECT-MATCH RECIPE ---")
PERFECT_MATCHES_RECIPES = {
    'f87r': 'Confectio Hamech',
    'f87v': 'Unguentum Apostolorum',
    'f88r': 'Trifera Magna',
    'f93v': 'Diascordium',
    'f96v': 'Pillulae Aureae',
    'f100r': 'Diamargariton',
    'f100v': 'Diaciminum',
}

for folio, recipe in PERFECT_MATCHES_RECIPES.items():
    ings = recipe_ingredients.get(recipe, set())
    covered = ings & all_ings_v5
    pct = 100 * len(covered) / len(ings) if ings else 0
    print(f"  {folio} = {recipe}: {len(covered)}/{len(ings)} ({pct:.0f}%)")
    uncovered = sorted(ings - covered)
    if uncovered:
        print(f"    Still missing: {uncovered}")
