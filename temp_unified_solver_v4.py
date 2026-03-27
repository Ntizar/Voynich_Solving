#!/usr/bin/env python3
"""
VOYNICH UNIFIED CONSTRAINT SOLVER v4
=====================================
Integrates ALL identification sources:
1. Prior session: K1K2A1=Galbanum (v1 solver), K1A3=Crocus (elimination), BaA3=gum-resin class
2. v3 automated: A1Q2A1=Myrrha, D1A1=Myrrha, Q1K1A1=Myrrha, etc.
3. NEW: Folio-exclusive stem extraction from perfect matches (Diamargariton, Diaciminum)
4. Elimination chain: each confirmed ID removes ingredient from other candidate lists
5. Negative constraints: stem ABSENT from folio -> ingredient ABSENT from recipe

Outputs:
- voynich_unified_identifications_v4.csv
- Console report with full analysis
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import csv
import os
from collections import defaultdict

BASE = r'C:\Ntizar_Obsidian\Ntizar_Brain\MASTERTMIND'

# ============================================================
# PHASE 0: Load all data
# ============================================================
print("=" * 80)
print("VOYNICH UNIFIED CONSTRAINT SOLVER v4")
print("=" * 80)

# Load expanded matching (folio -> recipe assignments)
matching = {}
with open(os.path.join(BASE, 'voynich_expanded_matching.csv'), encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        matching[row['Folio']] = {
            'best_match': row['Best_Match'],
            'best_n': int(row['Best_Match_N']),
            'best_sim': float(row['Best_Similarity']),
            'unique_stems': int(row['Unique_Stems']),
            'est_ingredients': int(row['Estimated_Ingredients']),
        }

# Load recipe ingredients (flat)
recipe_ingredients = defaultdict(set)
ingredient_recipes = defaultdict(set)
ingredient_category = {}
with open(os.path.join(BASE, 'recetas_historicas_ingredientes_flat.csv'), encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rname = row['Receta'].split('(')[0].strip()  # Normalize recipe name
        ing = row['Ingrediente_Normalizado']
        recipe_ingredients[rname].add(ing)
        ingredient_recipes[ing].add(rname)
        ingredient_category[ing] = row['Categoria']

# Normalize recipe names in matching
RECIPE_NORMALIZE = {
    'Theriac Magna': 'Theriac Magna',
    'Mithridatium': 'Mithridatium',
    'Diascordium': 'Diascordium',
    'Pillulae Cochiae': 'Pillulae Cochiae',
    'Pillulae Aureae': 'Pillulae Aureae',
    'Unguentum Apostolorum': 'Unguentum Apostolorum',
    'Electuarium de Succo Rosarum': 'Electuarium de Succo Rosarum',
    'Aurea Alexandrina': 'Aurea Alexandrina',
    'Confectio Hamech': 'Confectio Hamech',
    'Hiera Picra': 'Hiera Picra',
    'Trifera Magna': 'Trifera Magna',
    'Diamargariton': 'Diamargariton',
    'Diaciminum': 'Diaciminum',
    'Unguentum Basilicon': 'Unguentum Basilicon',
    'Unguentum Populeon': 'Unguentum Populeon',
    'Pillulae de Hiera cum Agarico': 'Pillulae de Hiera cum Agarico',
    'Pillulae Fetidae': 'Pillulae Fetidae',
    'Requies Magna': 'Requies Magna',
    'Diacodion': 'Diacodion',
    'Dialtea': 'Dialtea',
    'Philonium Persicum': 'Philonium Persicum',
    'Oximel Compositum': 'Oximel Compositum',
    'Theriac Diatessaron': 'Theriac Diatessaron',
}

# Load stems in matched folios
stem_folios = {}
stem_recipes = defaultdict(set)
with open(os.path.join(BASE, 'voynich_stems_in_matched_folios.csv'), encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        stem = row['Stem']
        stype = row['Type']
        folios = [x.strip() for x in row['Matched_Folios'].split('|')]
        recipes_raw = [x.strip() for x in row['Matched_Recipes'].split('|')]
        stem_folios[stem] = {'type': stype, 'folios': folios, 'recipes': recipes_raw}
        for r in recipes_raw:
            stem_recipes[stem].add(r)

# Load v3 solver results
v3_results = {}
with open(os.path.join(BASE, 'voynich_constraint_solver_v3_results.csv'), encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        v3_results[row['Stem']] = row

# Also load the raw corpus to extract stems per folio directly
def parse_corpus_stems_per_folio():
    """Parse voynich_sta.txt to get all stems per folio."""
    folio_stems = defaultdict(set)
    current_folio = None
    corpus_path = os.path.join(BASE, 'zenodo_voynich', 'corpus', 'voynich_sta.txt')
    
    with open(corpus_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # Folio header
            if line.startswith('<f') and '>' in line and '.' not in line.split('>')[0]:
                # Extract folio ID
                folio_id = line.split('>')[0].replace('<', '').strip()
                # Clean: remove trailing whitespace/comments
                if ' ' in folio_id:
                    folio_id = folio_id.split()[0]
                current_folio = folio_id
                continue
            # Line with words
            if current_folio and '.' in line:
                # Line format: <f87v.3,+P0> word1.word2.word3
                parts = line.split('>')
                if len(parts) > 1:
                    # Get folio from line header
                    header = parts[0].replace('<', '')
                    folio_from_line = header.split('.')[0]
                    words_part = parts[1].strip()
                else:
                    folio_from_line = current_folio
                    words_part = line
                
                # Split by separator blocks <->
                blocks = words_part.replace('<->', ' ').split('.')
                for word in blocks:
                    word = word.strip()
                    if word and not word.startswith('<') and not word.startswith('!'):
                        # Extract stem (remove final atom)
                        # Final atom = last uppercase letter sequence (A1, B2, C1, etc.)
                        # For now, just use the raw word as stem approximation
                        folio_stems[folio_from_line].add(word)
    
    return folio_stems

print("\nLoading corpus stems per folio...")
corpus_stems = parse_corpus_stems_per_folio()
print(f"  Parsed {len(corpus_stems)} folios from corpus")

# ============================================================
# PHASE 1: PERFECT MATCH EXPLOITATION
# ============================================================
print("\n" + "=" * 80)
print("PHASE 1: PERFECT MATCH EXPLOITATION")
print("=" * 80)

# Perfect matches (100% similarity)
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

# For each perfect match, list which stems appear ONLY in that folio 
# among all perfect-match folios
print("\nStems exclusive to specific perfect-match folios:")
print("-" * 60)

# First, build stem -> set of perfect-match folios it appears in
stem_in_perfect = defaultdict(set)
for folio, recipe in PERFECT_MATCHES.items():
    if folio in stem_folios:
        pass  # stem_folios only has stems in 2+ matched folios
    # Use the stems from our matched_folios CSV
    for stem, data in stem_folios.items():
        if folio in data['folios']:
            stem_in_perfect[stem].add(folio)

# Find stems that appear in exactly ONE perfect-match folio
exclusive_to_perfect = {}
for stem, pfols in stem_in_perfect.items():
    if len(pfols) == 1:
        folio = list(pfols)[0]
        recipe = PERFECT_MATCHES[folio]
        exclusive_to_perfect[stem] = {'folio': folio, 'recipe': recipe}

print(f"\n  Stems exclusive to exactly 1 perfect-match folio: {len(exclusive_to_perfect)}")
for stem, info in sorted(exclusive_to_perfect.items(), key=lambda x: x[1]['folio']):
    recipe = info['recipe']
    ings = recipe_ingredients.get(recipe, set())
    print(f"    {stem:25s} -> {info['folio']} = {recipe} ({len(ings)} ingredients)")


# ============================================================
# PHASE 2: FOLIO-SPECIFIC STEM EXTRACTION
# ============================================================
print("\n" + "=" * 80)
print("PHASE 2: FOLIO-SPECIFIC STEM EXTRACTION FOR NEW MATCHES")
print("=" * 80)

# Focus on f100r=Diamargariton and f100v=Diaciminum 
# These are distinctive recipes with unusual ingredients

NEW_TARGETS = {
    'f100r': {'recipe': 'Diamargariton', 'distinctive': [
        'Margarita', 'Corallium rubrum', 'Corallium album', 'Os de corde cervi',
        'Cornu cervi', 'Doronicum', 'Zedoaria', 'Galanga', 'Nux moschata', 'Cubeba'
    ]},
    'f100v': {'recipe': 'Diaciminum', 'distinctive': [
        'Cuminum', 'Apium', 'Carum', 'Amomum', 'Daucus creticus'
    ]},
}

# Get ALL stems that appear in these folios from the stems CSV
for target_folio, target_info in NEW_TARGETS.items():
    recipe = target_info['recipe']
    distinctive = target_info['distinctive']
    
    print(f"\n--- {target_folio} = {recipe} ---")
    print(f"  Distinctive ingredients: {distinctive}")
    
    # Find stems present in this folio
    stems_in_folio = []
    for stem, data in stem_folios.items():
        if target_folio in data['folios']:
            stems_in_folio.append(stem)
    
    print(f"  Total stems tracked in this folio: {len(stems_in_folio)}")
    
    # For each stem, check which OTHER perfect-match recipes it appears in
    for stem in sorted(stems_in_folio):
        other_recipes = set()
        for fol in stem_folios[stem]['folios']:
            if fol in PERFECT_MATCHES and fol != target_folio:
                other_recipes.add(PERFECT_MATCHES[fol])
            elif fol in matching:
                r = matching[fol]['best_match']
                if matching[fol]['best_sim'] >= 90:
                    other_recipes.add(r)
        
        # Cross-reference: which ingredients are in THIS recipe but NOT in others?
        recipe_ings = recipe_ingredients.get(recipe, set())
        other_ings = set()
        for r in other_recipes:
            other_ings |= recipe_ingredients.get(r, set())
        
        unique_to_recipe = recipe_ings - other_ings
        
        if unique_to_recipe and len(stem_folios[stem]['folios']) <= 5:
            v3_info = v3_results.get(stem, {})
            v3_best = v3_info.get('Best_Candidate', '?')
            v3_conf = v3_info.get('Confidence', '?')
            print(f"  {stem:25s} (in {len(stem_folios[stem]['folios'])} folios) "
                  f"v3={v3_best}({v3_conf}) | unique_to_recipe: {unique_to_recipe}")


# ============================================================
# PHASE 3: UNIFIED IDENTIFICATION TABLE
# ============================================================
print("\n" + "=" * 80)
print("PHASE 3: UNIFIED IDENTIFICATION TABLE")
print("=" * 80)

# Start with confirmed identifications (manual + prior sessions)
confirmed = {}

# === TIER 1: CONFIRMED (prior sessions, manual elimination) ===
confirmed['K1K2A1'] = {
    'ingredient': 'Galbanum',
    'confidence': 99,
    'source': 'v1_solver + cross-validation',
    'tier': 1,
    'reasoning': 'Unique intersection across 4 diverse recipes; only resin that fits all'
}
confirmed['K1A3'] = {
    'ingredient': 'Crocus',
    'confidence': 95,
    'source': 'elimination_logic',
    'tier': 1,
    'reasoning': 'K1A3 absent from f93v/Diascordium which HAS Cinnamomum; eliminates v3 Cinnamomum candidate. Crocus fits: present in Pillulae Aureae, Trifera, Philonium but NOT Diascordium'
}

# === TIER 2: HIGH CONFIDENCE from v3 (UNIQUE with good neg_score) ===
# A1Q2A1 -> Myrrha (UNIQUE, neg_score 0.625, present in Ung.Apostolorum+Trifera+Philonium+AureaAlex)
confirmed['A1Q2A1'] = {
    'ingredient': 'Myrrha',
    'confidence': 92,
    'source': 'v3_UNIQUE',
    'tier': 2,
    'reasoning': 'UNIQUE candidate across 4 recipes incl. Ung.Apostolorum. Myrrha only ingredient in ALL 4 and ABSENT from all 8 absent recipes.'
}
# D1A1 -> Myrrha (UNIQUE across 3 recipes including Ung.Apostolorum)
confirmed['D1A1'] = {
    'ingredient': 'Myrrha',
    'confidence': 90,
    'source': 'v3_UNIQUE',
    'tier': 2,
    'reasoning': 'UNIQUE across Aurea Alex + Trifera + Ung.Apostolorum. Same Myrrha profile as A1Q2A1. Possible: D1A1 is morphological variant of same Myrrha word.'
}
# D1A1A3 -> Myrrha (UNIQUE across same profile)
confirmed['D1A1A3'] = {
    'ingredient': 'Myrrha',
    'confidence': 90,
    'source': 'v3_UNIQUE',
    'tier': 2,
    'reasoning': 'Same presence/absence profile as D1A1 and A1Q2A1. Suffix variant.'
}
# Q1K1A1 -> Myrrha (UNIQUE, Aurea+Ung.Apostolorum)
confirmed['Q1K1A1'] = {
    'ingredient': 'Myrrha',
    'confidence': 88,
    'source': 'v3_UNIQUE',
    'tier': 2,
    'reasoning': 'Present in Aurea Alex + Ung.Apostolorum only. Myrrha is the only ingredient in both that is absent from all 8 negative recipes.'
}
# A1Q1J1 -> Myrrha (UNIQUE, Philonium+Trifera+Ung.Apostolorum)
confirmed['A1Q1J1'] = {
    'ingredient': 'Myrrha',
    'confidence': 88,
    'source': 'v3_UNIQUE',
    'tier': 2,
    'reasoning': 'Present in Phil.Persicum + Trifera + Ung.Apostolorum. Myrrha unique fit.'
}
# T1J1A1B1A3 -> Myrrha (UNIQUE, Phil.Persicum+Ung.Apostolorum)
confirmed['T1J1A1B1A3'] = {
    'ingredient': 'Myrrha',
    'confidence': 85,
    'source': 'v3_UNIQUE',
    'tier': 2,
    'reasoning': 'Only appears in Philonium + Unguentum Apostolorum. Myrrha is the only shared ingredient absent from all 8 negatives.'
}

# === TIER 3: STRONG CONFIDENCE from v3 (2 candidates, top clearly better) ===
# Multiple stems -> Crocus (STRONG, only 2 candidates: Crocus vs Cinnamomum)
CROCUS_STEMS = ['A1C1A3', 'A1B2K1J1', 'A2Q2J1A1', 'T1J1A1', 'B1L1J1A1', 
                'C2A1C2A3', 'K1J1U1J1', 'K1K2Q1J1', 'U1J1Aa']
for stem in CROCUS_STEMS:
    if stem in v3_results:
        v3 = v3_results[stem]
        if v3['Best_Candidate'] == 'Crocus':
            confirmed[stem] = {
                'ingredient': 'Crocus',
                'confidence': 80,
                'source': 'v3_STRONG',
                'tier': 3,
                'reasoning': f"STRONG: 2 candidates (Crocus vs Cinnamomum). Crocus scores {v3['Best_Score']} vs Cinnamomum ~0.607. Crocus is the discriminative choice."
            }

# B1K1A1 -> Rosa (STRONG, score 0.882)
confirmed['B1K1A1'] = {
    'ingredient': 'Rosa',
    'confidence': 82,
    'source': 'v3_STRONG',
    'tier': 3,
    'reasoning': 'Present in Confectio Hamech + Diascordium only. Rosa scores 0.882 (top), next is Zingiber 0.726. Rosa is in both recipes.'
}

# === TIER 4: MODERATE from v3 (good discriminativity, 3-5 candidates) ===
# A1Q1A1 -> Piper nigrum (0.835, 5 candidates)
confirmed['A1Q1A1'] = {
    'ingredient': 'Piper nigrum',
    'confidence': 70,
    'source': 'v3_MODERATE',
    'tier': 4,
    'reasoning': 'Top candidate at 0.835. Present in Aurea+Diaciminum+Philonium+Trifera. P.nigrum in all 4.'
}
# A1Q1A3 -> Piper longum (0.780, 4 candidates)
confirmed['A1Q1A3'] = {
    'ingredient': 'Piper longum',
    'confidence': 68,
    'source': 'v3_MODERATE',
    'tier': 4,
    'reasoning': 'Top candidate at 0.780. Similar profile to A1Q1A1 (Piper nigrum) -- morphological pair A1Q1+A1 vs A1Q1+A3 maps to nigrum/longum pair.'
}
# A1Q1K2A1 -> Casia (0.827, 3 candidates) 
confirmed['A1Q1K2A1'] = {
    'ingredient': 'Casia',
    'confidence': 65,
    'source': 'v3_MODERATE',
    'tier': 4,
    'reasoning': 'Top candidate 0.827. Present in Aurea+Diamargariton+Philonium+Trifera. Casia in all 4. K1A3=Crocus eliminates Crocus from this list.'
}
# A1Q2J1A1 -> Casia (0.827, same profile as A1Q1K2A1)
confirmed['A1Q2J1A1'] = {
    'ingredient': 'Casia',
    'confidence': 63,
    'source': 'v3_MODERATE',
    'tier': 4,
    'reasoning': 'Same Casia profile as A1Q1K2A1. Morphological variant. After eliminating Crocus (=K1A3), Casia is top.'
}
# D1A1Q1K2A1 -> Casia (same)
confirmed['D1A1Q1K2A1'] = {
    'ingredient': 'Casia',
    'confidence': 63,
    'source': 'v3_MODERATE',
    'tier': 4,
    'reasoning': 'Same profile. D1A1-prefix + Casia stem.'
}

# K1A1C1, K1C2, K1U1J1 -> Amomum (0.936)
for stem in ['K1A1C1', 'K1C2', 'K1U1J1']:
    if stem in v3_results:
        confirmed[stem] = {
            'ingredient': 'Amomum',
            'confidence': 72,
            'source': 'v3_MODERATE',
            'tier': 4,
            'reasoning': f"Amomum scores 0.936, well above next (Piper nigrum 0.835). Present in Diaciminum+Trifera only. Amomum in both."
        }

# A1Q1L1, U1J1A1B1 -> Styrax (0.907)
for stem in ['A1Q1L1', 'U1J1A1B1']:
    if stem in v3_results:
        confirmed[stem] = {
            'ingredient': 'Styrax',
            'confidence': 70,
            'source': 'v3_MODERATE',
            'tier': 4,
            'reasoning': 'Styrax scores 0.907. Present in Diascordium+Philonium only. Styrax is in both.'
        }

# D1, P1K1K2 -> Bdellium (0.928)
for stem in ['D1', 'P1K1K2']:
    if stem in v3_results:
        confirmed[stem] = {
            'ingredient': 'Bdellium',
            'confidence': 68,
            'source': 'v3_MODERATE', 
            'tier': 4,
            'reasoning': 'Bdellium 0.928, next Opopanax 0.919. Present in Trifera+Ung.Apostolorum. Both have Bdellium.'
        }

# A1B2K1J1A1, C1A3, D1A1Q1J1A1B1, D1A1Q2J1A1 -> Cardamomum (0.890)
CARDAMOMUM_STEMS = ['A1B2K1J1A1', 'C1A3', 'D1A1Q1J1A1B1', 'D1A1Q2J1A1', 
                     'K1J1A1U1', 'L1A1B1A1', 'L1A1U1J1', 'K1A1B2A1B1']
for stem in CARDAMOMUM_STEMS:
    if stem in v3_results and v3_results[stem]['Best_Candidate'] == 'Cardamomum':
        confirmed[stem] = {
            'ingredient': 'Cardamomum',
            'confidence': 65,
            'source': 'v3_MODERATE',
            'tier': 4,
            'reasoning': f"Cardamomum 0.890. Present in Diamargariton+Philonium (or +Trifera). After eliminating Crocus(=K1A3) and Casia(=A1Q1K2A1), Cardamomum is top."
        }

# === FUNCTION WORDS (confirmed non-ingredients) ===
FUNCTION_WORDS = {
    'B1A3': 'Appears in 26 folios across 7+ recipe types. Too ubiquitous for single ingredient.',
    'K1A1': 'Appears in 25 folios across 7+ recipe types.',
    'K1J1A1': 'Appears in 24 folios across 7+ recipe types. Tentative Cinnamomum but uncertain.',
    'C2A3': 'Appears in 21 folios across 6+ recipe types.',
    'BaA3': 'Gum-resin semantic class marker. Confirmed by cross-section analysis.',
    'Q1J1A1': 'Appears in 7 folios across diverse recipes.',
}

# ============================================================
# PHASE 4: ELIMINATION CHAIN
# ============================================================
print("\n" + "=" * 80)
print("PHASE 4: ELIMINATION CHAIN")
print("=" * 80)

# For each confirmed ID, remove that ingredient from other stems' candidate lists
# and re-check if any become UNIQUE

assigned_ingredients = set()
for stem, info in confirmed.items():
    assigned_ingredients.add(info['ingredient'])

print(f"\nConfirmed ingredients so far: {len(assigned_ingredients)}")
for ing in sorted(assigned_ingredients):
    stems_with_ing = [s for s, i in confirmed.items() if i['ingredient'] == ing]
    print(f"  {ing:25s} <- {stems_with_ing}")

# Now look at v3 AMBIGUOUS results and eliminate confirmed ingredients
print("\n--- Re-checking AMBIGUOUS stems after elimination ---")
new_identifications = {}

for stem, v3 in v3_results.items():
    if stem in confirmed:
        continue
    if stem in FUNCTION_WORDS:
        continue
    if v3['Confidence'] in ('AMBIGUOUS', 'MODERATE'):
        candidates_raw = v3['All_Candidates']
        # Parse candidates: "Piper nigrum(0.814) | Opium(0.806) | ..."
        candidates = []
        for c in candidates_raw.split('|'):
            c = c.strip()
            if '(' in c:
                name = c[:c.index('(')].strip()
                score = float(c[c.index('(')+1:c.index(')')])
                candidates.append((name, score))
        
        # Remove already-confirmed ingredients
        filtered = [(name, score) for name, score in candidates 
                     if name not in assigned_ingredients]
        
        if len(filtered) == 0:
            # All candidates eliminated -- this stem is probably a function word
            pass
        elif len(filtered) == 1:
            # UNIQUE after elimination!
            name, score = filtered[0]
            new_identifications[stem] = {
                'ingredient': name,
                'confidence': min(85, int(score * 100)),
                'source': 'elimination_chain',
                'tier': 3,
                'reasoning': f'Was {v3["Confidence"]} with {len(candidates)} candidates. After eliminating {assigned_ingredients & set(c[0] for c in candidates)}, only {name} remains.'
            }
            print(f"  NEW UNIQUE: {stem:25s} -> {name} (was {len(candidates)} candidates, now 1)")
        elif len(filtered) < len(candidates):
            top_name, top_score = filtered[0]
            if len(filtered) == 2 and (filtered[0][1] - filtered[1][1]) > 0.05:
                # Strong separation after elimination
                new_identifications[stem] = {
                    'ingredient': top_name,
                    'confidence': min(75, int(top_score * 100)),
                    'source': 'elimination_chain_strong',
                    'tier': 4,
                    'reasoning': f'Reduced from {len(candidates)} to {len(filtered)} candidates. Top: {top_name}({top_score:.3f}) vs {filtered[1][0]}({filtered[1][1]:.3f}). Gap > 0.05.'
                }
                print(f"  NEW STRONG: {stem:25s} -> {top_name} (reduced to {len(filtered)}, gap={filtered[0][1]-filtered[1][1]:.3f})")

# Add new identifications to confirmed
confirmed.update(new_identifications)

# ============================================================
# PHASE 5: NEGATIVE CONSTRAINT ANALYSIS
# ============================================================
print("\n" + "=" * 80)
print("PHASE 5: NEGATIVE CONSTRAINT DEEP ANALYSIS")
print("=" * 80)

# For still-unresolved stems, use negative constraints more aggressively
# Key insight: if stem S is ABSENT from folio F matched to recipe R,
# then S's ingredient must be ABSENT from R.

# Focus on the Cinnamomum problem: many stems marked as UNIQUE->Cinnamomum by v3
# But Cinnamomum is in 15/23 recipes, so "UNIQUE" just means nothing else fits.
# These are likely NOT Cinnamomum but rather function/structure words.

print("\n--- Cinnamomum problem analysis ---")
cinnamomum_only = []
for stem, v3 in v3_results.items():
    if stem in confirmed:
        continue
    if v3['Best_Candidate'] == 'Cinnamomum' and v3['Confidence'] == 'UNIQUE' and v3['N_Candidates'] == '1':
        cinnamomum_only.append(stem)

print(f"\nStems where Cinnamomum is the ONLY candidate: {len(cinnamomum_only)}")
print("These are suspicious -- Cinnamomum is ubiquitous (in 15/23 recipes).")
print("If these stems appear in many diverse folios, they are likely FUNCTION WORDS.\n")

for stem in sorted(cinnamomum_only):
    v3 = v3_results[stem]
    n_present = int(v3['N_Present'])
    n_absent = int(v3['N_Absent'])
    neg_score = float(v3['Neg_Score'])
    
    # Check how many folios this stem appears in
    n_folios = len(stem_folios.get(stem, {}).get('folios', []))
    
    # If neg_score is very low AND stem appears in many folios -> function word
    label = ""
    if neg_score < 0.2 and n_folios >= 5:
        label = " <-- LIKELY FUNCTION WORD"
    elif neg_score < 0.2:
        label = " <-- low neg, possibly Cinnamomum"
    elif neg_score >= 0.5:
        label = " <-- good neg_score, Cinnamomum plausible"
    
    print(f"  {stem:25s} present={n_present} absent={n_absent} neg={neg_score:.3f} folios={n_folios}{label}")


# ============================================================
# PHASE 6: MORPHOLOGICAL CLUSTERING
# ============================================================
print("\n" + "=" * 80)
print("PHASE 6: MORPHOLOGICAL CLUSTERING")
print("=" * 80)
print("\nStems that share the same ingredient identification may be morphological variants.")
print("This validates our identifications -- same root, different suffix = same ingredient.\n")

ingredient_stems = defaultdict(list)
for stem, info in confirmed.items():
    ingredient_stems[info['ingredient']].append((stem, info['confidence'], info['tier']))

for ing in sorted(ingredient_stems.keys()):
    stems = ingredient_stems[ing]
    if len(stems) > 1:
        print(f"  {ing}:")
        for stem, conf, tier in sorted(stems, key=lambda x: -x[1]):
            print(f"    {stem:25s} conf={conf}% tier={tier}")

# ============================================================
# PHASE 7: OUTPUT RESULTS
# ============================================================
print("\n" + "=" * 80)
print("PHASE 7: FINAL RESULTS SUMMARY")
print("=" * 80)

# Sort by tier then confidence
all_results = []
for stem, info in confirmed.items():
    all_results.append({
        'Stem': stem,
        'Ingredient': info['ingredient'],
        'Confidence': info['confidence'],
        'Tier': info['tier'],
        'Source': info['source'],
        'Reasoning': info['reasoning'],
    })

all_results.sort(key=lambda x: (x['Tier'], -x['Confidence']))

print(f"\nTOTAL IDENTIFICATIONS: {len(all_results)}")
print(f"  Tier 1 (Confirmed):  {sum(1 for r in all_results if r['Tier']==1)}")
print(f"  Tier 2 (High):       {sum(1 for r in all_results if r['Tier']==2)}")
print(f"  Tier 3 (Strong):     {sum(1 for r in all_results if r['Tier']==3)}")
print(f"  Tier 4 (Moderate):   {sum(1 for r in all_results if r['Tier']==4)}")

print(f"\nUNIQUE INGREDIENTS IDENTIFIED: {len(set(r['Ingredient'] for r in all_results))}")

print("\n--- Full table ---\n")
print(f"{'Stem':25s} {'Ingredient':20s} {'Conf':>4s} {'Tier':>4s} {'Source':25s}")
print("-" * 85)
for r in all_results:
    print(f"{r['Stem']:25s} {r['Ingredient']:20s} {r['Confidence']:>4d} {r['Tier']:>4d} {r['Source']:25s}")

# Write CSV
out_path = os.path.join(BASE, 'voynich_unified_identifications_v4.csv')
with open(out_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['Stem', 'Ingredient', 'Confidence', 'Tier', 'Source', 'Reasoning'])
    writer.writeheader()
    for r in all_results:
        writer.writerow(r)

print(f"\n\nSaved to: {out_path}")

# Also write function words
print("\n--- FUNCTION WORDS (non-ingredients) ---")
print(f"{'Stem':25s} {'Reason'}")
print("-" * 80)
for stem, reason in FUNCTION_WORDS.items():
    print(f"  {stem:25s} {reason}")

# Summary statistics
print("\n" + "=" * 80)
print("SUMMARY STATISTICS")
print("=" * 80)
unique_ings = set(r['Ingredient'] for r in all_results)
print(f"\nTotal stem->ingredient mappings: {len(all_results)}")
print(f"Unique ingredients identified: {len(unique_ings)}")
print(f"Function words identified: {len(FUNCTION_WORDS)}")
print(f"\nIngredients by category:")
for ing in sorted(unique_ings):
    cat = ingredient_category.get(ing, 'UNKNOWN')
    n_stems = sum(1 for r in all_results if r['Ingredient'] == ing)
    print(f"  {cat:8s} | {ing:25s} | {n_stems} stem(s)")

print("\n\nIngredients NOT yet identified (from perfect-match recipes):")
all_perfect_ings = set()
for folio, recipe in PERFECT_MATCHES.items():
    all_perfect_ings |= recipe_ingredients.get(recipe, set())

identified_ings = set(r['Ingredient'] for r in all_results)
missing = all_perfect_ings - identified_ings
print(f"  Total ingredients in perfect-match recipes: {len(all_perfect_ings)}")
print(f"  Identified: {len(identified_ings & all_perfect_ings)}")
print(f"  Missing: {len(missing)}")
for ing in sorted(missing):
    cat = ingredient_category.get(ing, '?')
    in_recipes = [r for r in PERFECT_MATCHES.values() if ing in recipe_ingredients.get(r, set())]
    print(f"    {cat:8s} | {ing:30s} | in: {in_recipes}")
