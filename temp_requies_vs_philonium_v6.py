#!/usr/bin/env python3
"""
REQUIES MAGNA vs PHILONIUM PERSICUM DISCRIMINATOR
===================================================
Session 7, Task 1: Break the Opium/Castoreum deadlock.

4 folios currently matched as Philonium Persicum (94.7%) with Requies Magna
as second-best (89.5%): f88v, f95v, f96r, f102r.

Strategy: Use ALREADY IDENTIFIED stems as diagnostic probes.
- Stems identified as ingredients ONLY in Philonium (not Requies) -> Philonium evidence
- Stems identified as ingredients ONLY in Requies (not Philonium) -> Requies evidence
- Also check for UNIDENTIFIED stems with clear differential profiles.

If we can reassign even ONE folio to Requies Magna, we break the Opium/Castoreum
deadlock (71 stems split into two groups).

Key discriminators:
  ONLY Philonium: Castoreum, Pyrethrum, Euphorbium, Nardus indica, Hypocistis, 
                  Styrax, Piper longum, Piper nigrum, Zingiber, Myrrha, Casia, 
                  Cardamomum, Mel despumatum
  ONLY Requies:   Mandragora, Papaver album, Lactuca, Psyllium, Amylum, Tragacantha,
                  Glycyrrhiza, Rosa, Nux moschata, Camphor, Saccharum, Aqua rosarum
  BOTH:           Opium, Hyoscyamus, Gummi arabicum, Crocus, Cinnamomum
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
import csv
import os
from collections import defaultdict, Counter

BASE = r'C:\Ntizar_Obsidian\Ntizar_Brain\MASTERTMIND'

# ============================================================
# 1. LOAD IDENTIFICATIONS
# ============================================================
identifications = {}
with open(os.path.join(BASE, 'voynich_unified_identifications_v5.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        identifications[row['Stem']] = {
            'ingredient': row['Ingredient'],
            'confidence': float(row['Confidence']),
            'tier': int(row['Tier']),
        }

# ============================================================
# 2. DEFINE RECIPE INGREDIENTS
# ============================================================
philonium_ingredients = {
    'Opium', 'Castoreum', 'Pyrethrum', 'Euphorbium', 'Hyoscyamus',
    'Nardus indica', 'Hypocistis', 'Gummi arabicum', 'Styrax',
    'Crocus', 'Piper longum', 'Piper nigrum', 'Zingiber', 'Cinnamomum',
    'Myrrha', 'Casia', 'Cardamomum', 'Mel despumatum',
}

requies_ingredients = {
    'Opium', 'Mandragora', 'Hyoscyamus', 'Papaver album', 'Lactuca',
    'Psyllium', 'Gummi arabicum', 'Amylum', 'Tragacantha', 'Glycyrrhiza',
    'Rosa', 'Cinnamomum', 'Nux moschata', 'Crocus', 'Camphor',
    'Saccharum', 'Aqua rosarum',
}

only_philonium = philonium_ingredients - requies_ingredients
only_requies = requies_ingredients - philonium_ingredients
shared_both = philonium_ingredients & requies_ingredients

print("=" * 80)
print("REQUIES MAGNA vs PHILONIUM PERSICUM DISCRIMINATOR")
print("=" * 80)
print(f"\nPhilonium Persicum: {len(philonium_ingredients)} ingredients")
print(f"Requies Magna: {len(requies_ingredients)} ingredients")
print(f"ONLY in Philonium ({len(only_philonium)}): {sorted(only_philonium)}")
print(f"ONLY in Requies ({len(only_requies)}): {sorted(only_requies)}")
print(f"In BOTH ({len(shared_both)}): {sorted(shared_both)}")

# ============================================================
# 3. MAP IDENTIFIED STEMS TO PHILONIUM vs REQUIES
# ============================================================
print("\n" + "=" * 80)
print("IDENTIFIED STEMS AS DIAGNOSTIC PROBES")
print("=" * 80)

philonium_probes = {}  # stem -> ingredient (signals Philonium)
requies_probes = {}    # stem -> ingredient (signals Requies)
ambiguous_probes = {}  # stem -> ingredient (in both)

for stem, info in identifications.items():
    ing = info['ingredient']
    if ing == 'FUNCTION_WORD':
        continue
    
    # Handle pairs (e.g., "Zingiber|Mel despumatum")
    ing_parts = [i.strip() for i in ing.split('|')]
    
    # Check each part
    any_philonium_only = any(i in only_philonium for i in ing_parts)
    any_requies_only = any(i in only_requies for i in ing_parts)
    any_in_philonium = any(i in philonium_ingredients for i in ing_parts)
    any_in_requies = any(i in requies_ingredients for i in ing_parts)
    
    if any_in_philonium and not any_in_requies:
        philonium_probes[stem] = ing
    elif any_in_requies and not any_in_philonium:
        requies_probes[stem] = ing
    elif any_philonium_only and any_requies_only:
        ambiguous_probes[stem] = ing  # pair spans both
    elif any_in_philonium and any_in_requies:
        ambiguous_probes[stem] = ing  # in both recipes

print(f"\nPhilonium-exclusive probes ({len(philonium_probes)}):")
for s, i in sorted(philonium_probes.items(), key=lambda x: x[1]):
    print(f"  {s:25s} = {i}")

print(f"\nRequies-exclusive probes ({len(requies_probes)}):")
for s, i in sorted(requies_probes.items(), key=lambda x: x[1]):
    print(f"  {s:25s} = {i}")

print(f"\nAmbiguous probes ({len(ambiguous_probes)}) -- in both recipes:")
for s, i in sorted(ambiguous_probes.items(), key=lambda x: x[1]):
    print(f"  {s:25s} = {i}")

# ============================================================
# 4. LOAD STEM DATA FOR CANDIDATE FOLIOS
# ============================================================
candidate_folios = ['f88v', 'f95v', 'f96r', 'f102r']

folio_stems = defaultdict(dict)  # folio -> {stem: count}
with open(os.path.join(BASE, 'voynich_all_recipe_folio_stems.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        if row['Folio'] in candidate_folios:
            folio_stems[row['Folio']][row['Stem']] = int(row['Token_Count'])

# ============================================================
# 5. SCORE EACH FOLIO: PHILONIUM vs REQUIES
# ============================================================
print("\n" + "=" * 80)
print("FOLIO-BY-FOLIO DIAGNOSTIC ANALYSIS")
print("=" * 80)

folio_scores = {}

for folio in candidate_folios:
    stems = folio_stems[folio]
    
    phil_hits = {}
    req_hits = {}
    amb_hits = {}
    
    for stem in stems:
        if stem in philonium_probes:
            phil_hits[stem] = (philonium_probes[stem], stems[stem])
        elif stem in requies_probes:
            req_hits[stem] = (requies_probes[stem], stems[stem])
        elif stem in ambiguous_probes:
            amb_hits[stem] = (ambiguous_probes[stem], stems[stem])
    
    phil_score = sum(count for _, count in phil_hits.values())
    req_score = sum(count for _, count in req_hits.values())
    amb_score = sum(count for _, count in amb_hits.values())
    
    folio_scores[folio] = {
        'phil_hits': phil_hits, 'req_hits': req_hits, 'amb_hits': amb_hits,
        'phil_unique_stems': len(phil_hits),
        'req_unique_stems': len(req_hits),
        'phil_tokens': phil_score,
        'req_tokens': req_score,
    }
    
    print(f"\n{'='*60}")
    print(f"  {folio}")
    print(f"  Total unique stems: {len(stems)}")
    print(f"{'='*60}")
    
    print(f"\n  PHILONIUM evidence ({len(phil_hits)} stems, {phil_score} tokens):")
    for stem, (ing, count) in sorted(phil_hits.items(), key=lambda x: -x[1][1]):
        print(f"    {stem:25s} = {ing:20s} x{count}")
    
    print(f"\n  REQUIES evidence ({len(req_hits)} stems, {req_score} tokens):")
    for stem, (ing, count) in sorted(req_hits.items(), key=lambda x: -x[1][1]):
        print(f"    {stem:25s} = {ing:20s} x{count}")
    
    print(f"\n  AMBIGUOUS / both ({len(amb_hits)} stems, {amb_score} tokens):")
    for stem, (ing, count) in sorted(amb_hits.items(), key=lambda x: -x[1][1]):
        print(f"    {stem:25s} = {ing:20s} x{count}")
    
    # Verdict
    if phil_score > 0 and req_score == 0:
        verdict = "PHILONIUM (only Philonium evidence found)"
    elif req_score > 0 and phil_score == 0:
        verdict = "*** REQUIES *** (only Requies evidence found!)"
    elif phil_score > req_score:
        ratio = phil_score / max(req_score, 1)
        verdict = f"Leans PHILONIUM ({ratio:.1f}x more tokens)"
    elif req_score > phil_score:
        ratio = req_score / max(phil_score, 1)
        verdict = f"*** Leans REQUIES *** ({ratio:.1f}x more tokens)"
    else:
        verdict = "AMBIGUOUS (equal evidence)"
    
    print(f"\n  >>> VERDICT: {verdict}")


# ============================================================
# 6. SECOND APPROACH: FULL UNIDENTIFIED STEM DIFFERENTIAL
# ============================================================
# For stems NOT yet identified, check if they appear in recipes that
# contain Philonium-only ingredients vs Requies-only ingredients.
# Specifically: stems that appear ONLY in candidate folios and folios 
# whose recipe has specific discriminator ingredients.

print("\n\n" + "=" * 80)
print("APPROACH 2: UNIDENTIFIED STEM DIFFERENTIAL ANALYSIS")
print("=" * 80)

# Load ALL recipe folio stems
all_folio_stems = defaultdict(set)  # stem -> set of folios
with open(os.path.join(BASE, 'voynich_all_recipe_folio_stems.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        all_folio_stems[row['Stem']].add(row['Folio'])

# Load recipe ingredients flat file
recipe_ingredients = defaultdict(set)
with open(os.path.join(BASE, 'recetas_historicas_ingredientes_flat.csv'), encoding='utf-8') as f:
    for row in csv.DictReader(f):
        rname = row['Receta'].split('(')[0].strip()
        recipe_ingredients[rname].add(row['Ingrediente_Normalizado'])

# All matched folios
PERFECT_MATCHES = {
    'f87r': 'Confectio Hamech', 'f87v': 'Unguentum Apostolorum',
    'f88r': 'Trifera Magna', 'f93v': 'Diascordium',
    'f96v': 'Pillulae Aureae', 'f100r': 'Diamargariton',
    'f100v': 'Diaciminum', 'f101v': 'Trifera Magna', 'f103v': 'Trifera Magna',
}
STRONG_MATCHES = {
    'f88v': 'Philonium Persicum', 'f90r': 'Aurea Alexandrina',
    'f90v': 'Aurea Alexandrina', 'f94r': 'Aurea Alexandrina',
    'f94v': 'Diascordium', 'f95r': 'Trifera Magna',
    'f95v': 'Philonium Persicum', 'f96r': 'Philonium Persicum',
    'f99r': 'Trifera Magna', 'f99v': 'Aurea Alexandrina',
    'f101r': 'Trifera Magna', 'f102r': 'Philonium Persicum',
    'f102v': 'Trifera Magna', 'f105r': 'Trifera Magna',
    'f105v': 'Trifera Magna', 'f108r': 'Trifera Magna',
    'f112r': 'Trifera Magna', 'f114v': 'Trifera Magna', 'f116r': 'Trifera Magna',
}
ALL_MATCHED = {**PERFECT_MATCHES, **STRONG_MATCHES}

# For discriminator ingredients, build folio sets
# Philonium-only ingredients: which folios' recipes contain them?
# If a stem appears in those folios AND in a candidate folio, it supports Philonium

# For each DISCRIMINATOR ingredient, determine which matched folios 
# have recipes containing that ingredient
print("\nDiscriminator ingredient -> matched folios:")

for ing in sorted(only_philonium):
    has_folios = [f for f, r in ALL_MATCHED.items() if ing in recipe_ingredients.get(r, set())]
    print(f"  [PHIL] {ing:25s} -> {len(has_folios)} folios: {sorted(has_folios)[:8]}")

for ing in sorted(only_requies):
    has_folios = [f for f, r in ALL_MATCHED.items() if ing in recipe_ingredients.get(r, set())]
    print(f"  [REQ ] {ing:25s} -> {len(has_folios)} folios: {sorted(has_folios)[:8]}")

# Now: for each candidate folio, find UNIDENTIFIED stems that are
# shared with SPECIFIC discriminator-ingredient folio sets
print("\n--- Unidentified stem overlaps with discriminator folios ---")

# Key insight: Myrrha-identified stems tell us a lot.
# Myrrha is ONLY in Philonium (not Requies).
# If a folio has Myrrha stems, it's Philonium.
# Similarly: Styrax, Piper nigrum, Piper longum, Casia, Cardamomum are all only in Philonium.
# Rosa, Nux moschata, Saccharum, Camphor are only in Requies.

# But let's also look at FULL PATTERN matching for unidentified stems.
# For each unidentified stem present in a candidate folio:
#   - Count how many Philonium-specific-ingredient folios also have it
#   - Count how many Requies-specific-ingredient folios also have it
#   (where "Philonium-specific-ingredient folio" = a matched folio whose recipe 
#    has at least one ingredient that's ONLY in Philonium)

# More precisely: for each candidate folio's stems, check if the stem's
# overall folio distribution better matches Philonium or Requies profile.

# Build ingredient profiles for ALL matched folios (excluding candidates)
# For each discriminator ingredient, get the set of non-candidate matched folios
non_candidate_matched = {f: r for f, r in ALL_MATCHED.items() if f not in candidate_folios}

# Folios that are CONFIRMED Philonium (none currently -- they're all candidates!)
# So we need to use other recipes that SHARE Philonium-only ingredients.
# e.g., Myrrha is in: UA, Trifera, Aurea Alex, Philonium, etc.
# Castoreum is in: Diascordium, Trifera, Aurea Alex, Philonium, etc.

# Actually, let's think differently. 
# For each candidate folio, count how many of its stems are shared with:
# (a) Folios matched to recipes that DON'T have Rosa/Nux moschata/Camphor/Saccharum
#     (i.e., non-Requies-like recipes)
# (b) Vs exclusively shared with candidate folios

# Better approach: PROFILE MATCHING
# Take the stem vector of each candidate folio and compute cosine similarity
# to the EXPECTED stem profile of Philonium vs Requies.
# Expected profile: union of stems from folios confirmed to share specific ingredients.

print("\n\n" + "=" * 80)
print("APPROACH 3: INGREDIENT-SPECIFIC STEM POOLS")
print("=" * 80)

# For each Philonium-only ingredient, build the expected stem pool
# from non-candidate folios that contain that ingredient.
# Then check if the candidate folio has those stems.

phil_only_stem_pools = {}
for ing in sorted(only_philonium):
    # Non-candidate folios whose recipe has this ingredient
    ref_folios = [f for f, r in non_candidate_matched.items() 
                  if ing in recipe_ingredients.get(r, set())]
    if len(ref_folios) < 2:
        continue
    
    # Stems that appear in ALL reference folios (very strict)
    # Or: stems that appear in MOST reference folios (relaxed)
    all_stems_here = set()
    stem_counts = Counter()
    for f in ref_folios:
        fstems = folio_stems.get(f, set())
        if isinstance(fstems, dict):
            fstems = set(fstems.keys())
        all_stems_here |= fstems
        for s in fstems:
            stem_counts[s] += 1
    
    # Stems in at least 60% of reference folios and NOT identified as something else
    threshold = max(2, int(len(ref_folios) * 0.6))
    consistent_stems = {s for s, c in stem_counts.items() 
                       if c >= threshold and s not in identifications}
    
    phil_only_stem_pools[ing] = {
        'ref_folios': ref_folios,
        'consistent_stems': consistent_stems,
    }
    if consistent_stems:
        print(f"\n  {ing} ({len(ref_folios)} ref folios, threshold={threshold}):")
        print(f"    {len(consistent_stems)} consistent unidentified stems")
        for s in sorted(consistent_stems)[:10]:
            print(f"      {s}")

req_only_stem_pools = {}
for ing in sorted(only_requies):
    ref_folios = [f for f, r in non_candidate_matched.items() 
                  if ing in recipe_ingredients.get(r, set())]
    if len(ref_folios) < 2:
        continue
    
    all_stems_here = set()
    stem_counts = Counter()
    for f in ref_folios:
        fstems = folio_stems.get(f, set())
        if isinstance(fstems, dict):
            fstems = set(fstems.keys())
        all_stems_here |= fstems
        for s in fstems:
            stem_counts[s] += 1
    
    threshold = max(2, int(len(ref_folios) * 0.6))
    consistent_stems = {s for s, c in stem_counts.items() 
                       if c >= threshold and s not in identifications}
    
    req_only_stem_pools[ing] = {
        'ref_folios': ref_folios,
        'consistent_stems': consistent_stems,
    }
    if consistent_stems:
        print(f"\n  {ing} ({len(ref_folios)} ref folios, threshold={threshold}):")
        print(f"    {len(consistent_stems)} consistent unidentified stems")
        for s in sorted(consistent_stems)[:10]:
            print(f"      {s}")

# Now check each candidate
print("\n\n" + "=" * 80)
print("APPROACH 3 RESULTS: CANDIDATE FOLIO SCORING")
print("=" * 80)

for folio in candidate_folios:
    stems = set(folio_stems[folio].keys())
    
    print(f"\n{'='*60}")
    print(f"  {folio} ({len(stems)} unique stems)")
    print(f"{'='*60}")
    
    # Philonium ingredient matches
    phil_evidence = {}
    for ing, pool in phil_only_stem_pools.items():
        overlap = stems & pool['consistent_stems']
        if overlap:
            phil_evidence[ing] = overlap
    
    # Requies ingredient matches
    req_evidence = {}
    for ing, pool in req_only_stem_pools.items():
        overlap = stems & pool['consistent_stems']
        if overlap:
            req_evidence[ing] = overlap
    
    phil_total = sum(len(v) for v in phil_evidence.values())
    req_total = sum(len(v) for v in req_evidence.values())
    
    print(f"\n  Philonium-only ingredient evidence ({phil_total} stem hits):")
    for ing, overlap in sorted(phil_evidence.items(), key=lambda x: -len(x[1])):
        print(f"    {ing:25s} -> {len(overlap)} stems: {sorted(overlap)[:5]}")
    
    print(f"\n  Requies-only ingredient evidence ({req_total} stem hits):")
    for ing, overlap in sorted(req_evidence.items(), key=lambda x: -len(x[1])):
        print(f"    {ing:25s} -> {len(overlap)} stems: {sorted(overlap)[:5]}")
    
    if phil_total > req_total:
        print(f"\n  >>> PHILONIUM ({phil_total} vs {req_total})")
    elif req_total > phil_total:
        print(f"\n  >>> *** REQUIES *** ({req_total} vs {phil_total})")
    else:
        print(f"\n  >>> TIED ({phil_total} vs {req_total})")


# ============================================================
# 7. APPROACH 4: INTER-CANDIDATE CORRELATION
# ============================================================
# If all 4 candidates are the SAME recipe, they should share many stems.
# If one is DIFFERENT (Requies), it should have LOW overlap with the other 3.
print("\n\n" + "=" * 80)
print("APPROACH 4: INTER-CANDIDATE OVERLAP MATRIX")
print("=" * 80)

print(f"\nPairwise Jaccard similarity between candidate folios:")
print(f"{'':>8s}", end='')
for f2 in candidate_folios:
    print(f"  {f2:>8s}", end='')
print()

for f1 in candidate_folios:
    print(f"{f1:>8s}", end='')
    s1 = set(folio_stems[f1].keys())
    for f2 in candidate_folios:
        s2 = set(folio_stems[f2].keys())
        if f1 == f2:
            print(f"    ---  ", end='')
        else:
            jaccard = len(s1 & s2) / len(s1 | s2) if s1 | s2 else 0
            print(f"  {jaccard:6.3f} ", end='')
    print()

# Also show overlap counts
print(f"\nPairwise overlap counts (shared stems / min stems):")
print(f"{'':>8s}", end='')
for f2 in candidate_folios:
    print(f"  {f2:>8s}", end='')
print()

for f1 in candidate_folios:
    print(f"{f1:>8s}", end='')
    s1 = set(folio_stems[f1].keys())
    for f2 in candidate_folios:
        s2 = set(folio_stems[f2].keys())
        if f1 == f2:
            print(f"    ---  ", end='')
        else:
            shared = len(s1 & s2)
            print(f"  {shared:>3d}/{min(len(s1), len(s2)):>3d} ", end='')
    print()

# Also compare each candidate to CONFIRMED Philonium-like recipes
# (Aurea Alexandrina has many shared ingredients with Philonium)
# and to folios matched to recipes with Requies-like profiles
print("\n\nSimilarity of each candidate to non-candidate matched folios (Jaccard):")
print("(Higher = more similar to that group)")

# Group non-candidate folios by their recipe
recipe_groups = defaultdict(list)
for f, r in non_candidate_matched.items():
    recipe_groups[r].append(f)

for folio in candidate_folios:
    s_cand = set(folio_stems[folio].keys())
    print(f"\n  {folio}:")
    
    # Average Jaccard with each recipe group
    group_sims = {}
    for recipe, folios_list in sorted(recipe_groups.items()):
        sims = []
        for f_ref in folios_list:
            s_ref = set(folio_stems.get(f_ref, {}).keys())
            if s_ref:
                j = len(s_cand & s_ref) / len(s_cand | s_ref)
                sims.append(j)
        if sims:
            avg = sum(sims) / len(sims)
            group_sims[recipe] = avg
    
    # Show top 5
    for recipe, avg in sorted(group_sims.items(), key=lambda x: -x[1])[:5]:
        n_folios = len(recipe_groups[recipe])
        print(f"    {recipe:30s} (n={n_folios:>2d}) avg Jaccard={avg:.4f}")


# ============================================================
# 8. APPROACH 5: DIRECT STEM COUNTING FOR KEY INGREDIENTS
# ============================================================
print("\n\n" + "=" * 80)
print("APPROACH 5: DIRECT IDENTIFIED-STEM PRESENCE TABLE")
print("=" * 80)

# For EVERY identified ingredient, show if its stems appear in each candidate
print(f"\n{'Ingredient':25s} {'Type':10s}", end='')
for f in candidate_folios:
    print(f" {f:>6s}", end='')
print(f"  {'In Phil?':>10s} {'In Req?':>10s}")
print("-" * 100)

ingredient_stems = defaultdict(set)
for stem, info in identifications.items():
    if info['ingredient'] != 'FUNCTION_WORD':
        ingredient_stems[info['ingredient']].add(stem)

for ing in sorted(ingredient_stems.keys()):
    stems_for_ing = ingredient_stems[ing]
    in_phil = 'Yes' if any(i.strip() in philonium_ingredients for i in ing.split('|')) else 'No'
    in_req = 'Yes' if any(i.strip() in requies_ingredients for i in ing.split('|')) else 'No'
    
    # Determine discriminator type
    if in_phil == 'Yes' and in_req == 'No':
        dtype = '[PHIL]'
    elif in_req == 'Yes' and in_phil == 'No':
        dtype = '[REQ]'
    elif in_phil == 'Yes' and in_req == 'Yes':
        dtype = '[BOTH]'
    else:
        dtype = '[NEITHER]'
    
    print(f"{ing:25s} {dtype:10s}", end='')
    for f in candidate_folios:
        present = stems_for_ing & set(folio_stems[f].keys())
        total_tokens = sum(folio_stems[f].get(s, 0) for s in present)
        if present:
            print(f" {total_tokens:>4d}t ", end='')
        else:
            print(f"    -  ", end='')
    print(f"  {in_phil:>10s} {in_req:>10s}")


# ============================================================
# 9. SUMMARY & FINAL VERDICT
# ============================================================
print("\n\n" + "=" * 80)
print("FINAL SUMMARY: WHICH FOLIO IS REQUIES?")
print("=" * 80)

for folio in candidate_folios:
    stems = set(folio_stems[folio].keys())
    
    # Count identified ingredient tokens for Philonium-only vs Requies-only
    phil_tok = 0
    phil_ings_found = set()
    req_tok = 0
    req_ings_found = set()
    
    for stem in stems:
        if stem in identifications:
            info = identifications[stem]
            ing = info['ingredient']
            if ing == 'FUNCTION_WORD':
                continue
            count = folio_stems[folio].get(stem, 0)
            
            parts = [i.strip() for i in ing.split('|')]
            is_phil_only = any(i in only_philonium for i in parts)
            is_req_only = any(i in only_requies for i in parts)
            
            if is_phil_only and not is_req_only:
                phil_tok += count
                phil_ings_found.update(i for i in parts if i in only_philonium)
            elif is_req_only and not is_phil_only:
                req_tok += count
                req_ings_found.update(i for i in parts if i in only_requies)
    
    # Verdict
    if phil_tok > 0 and req_tok == 0:
        verdict = "PHILONIUM"
    elif req_tok > 0 and phil_tok == 0:
        verdict = "*** REQUIES ***"
    elif phil_tok > req_tok:
        verdict = f"PHILONIUM ({phil_tok}:{req_tok})"
    elif req_tok > phil_tok:
        verdict = f"*** REQUIES ({req_tok}:{phil_tok}) ***"
    else:
        verdict = "UNDETERMINED"
    
    print(f"\n  {folio}: Phil={phil_tok} tokens ({len(phil_ings_found)} ings: {sorted(phil_ings_found)})")
    print(f"  {'':>6s}  Req ={req_tok} tokens ({len(req_ings_found)} ings: {sorted(req_ings_found)})")
    print(f"  >>> {verdict}")

print("\n\nDone.")
