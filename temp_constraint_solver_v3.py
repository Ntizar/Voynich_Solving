import sys
import csv
import re
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')

# =============================================================================
# REFINED CONSTRAINT SOLVER v3
# Key improvement: Uses BOTH presence AND absence constraints.
# If stem X does NOT appear in folio matched to recipe R, then stem X
# CANNOT be an ingredient that IS in recipe R.
# =============================================================================

# --- RECIPE DATABASE (same as v2) ---
recipes = {
    "Theriac Magna": {
        "ACTIVO": {"Opium","Trochisci de vipera","Squilla","Hedychium","Castoreum",
                   "Nardus celtica","Petroselinum","Phu/Valeriana","Amomum",
                   "Acorus calamus","Hypericum","Gentiana","Aristolochia",
                   "Opopanax","Sagapenum","Galbanum","Balsamum","Styrax",
                   "Terebinthina","Bitumen judaicum"},
        "ESPECIA": {"Crocus","Zingiber","Cinnamomum","Piper longum","Piper nigrum",
                    "Myrrha","Olibanum","Casia","Costus","Anisi","Foeniculum",
                    "Daucus creticus"},
        "BASE": {"Mel despumatum","Vinum"}
    },
    "Mithridatium": {
        "ACTIVO": {"Opium","Castoreum","Nardus indica","Nardus celtica",
                   "Gentiana","Aristolochia longa","Aristolochia rotunda",
                   "Hypericum","Sagapenum","Opopanax","Acacia","Gummi arabicum",
                   "Hypocistis","Stachys","Thlaspi","Daucus creticus"},
        "ESPECIA": {"Crocus","Zingiber","Cinnamomum","Piper longum","Piper nigrum",
                    "Myrrha","Costus","Casia","Anisi","Petroselinum","Foeniculum",
                    "Cardamomum"},
        "BASE": {"Mel despumatum","Vinum"}
    },
    "Diascordium": {
        "ACTIVO": {"Scordium","Opium","Castoreum","Galbanum","Styrax","Bistorta"},
        "ESPECIA": {"Cinnamomum","Piper longum","Zingiber","Rosa","Gentiana","Dictamnus"},
        "BASE": {"Mel despumatum"}
    },
    "Pillulae Cochiae": {
        "ACTIVO": {"Colocynthis","Aloe","Scammonium"},
        "ESPECIA": {"Staphisagria","Bdellium"},
        "BASE": {"Succo absinthii"}
    },
    "Pillulae Aureae": {
        "ACTIVO": {"Aloe","Diagridium","Mastix","Rosa"},
        "ESPECIA": {"Crocus","Cinnamomum"},
        "BASE": {"Succo absinthii"}
    },
    "Unguentum Apostolorum": {
        "ACTIVO": {"Aristolochia longa","Aristolochia rotunda","Opopanax",
                   "Galbanum","Bdellium","Verdigris","Litharge"},
        "ESPECIA": {"Olibanum","Myrrha"},
        "BASE": {"Cera","Oleum olivarum","Resina pini"}
    },
    "Electuarium Rosarum": {
        "ACTIVO": {"Rosa gallica","Senna","Tamarindus","Viola"},
        "ESPECIA": {"Cinnamomum","Zingiber","Anisi"},
        "BASE": {"Saccharum"}
    },
    "Aurea Alexandrina": {
        "ACTIVO": {"Opium","Castoreum","Stachys","Hypericum","Petroselinum",
                   "Acorus calamus","Phu/Valeriana","Squilla"},
        "ESPECIA": {"Crocus","Piper longum","Piper nigrum","Zingiber","Cinnamomum",
                    "Myrrha","Costus","Nardus","Anisi","Foeniculum","Casia"},
        "BASE": {"Mel despumatum","Vinum","Saccharum"}
    },
    "Confectio Hamech": {
        "ACTIVO": {"Polypodium","Epithymum","Fumaria","Lapis lazuli",
                   "Myrobalanus indus","Myrobalanus citrinus","Myrobalanus kebulus",
                   "Senna","Rhabarbarum"},
        "ESPECIA": {"Zingiber","Anisi","Rosa","Cinnamomum"},
        "BASE": {"Saccharum","Mel despumatum"}
    },
    "Hiera Picra": {
        "ACTIVO": {"Aloe","Xylobalsamum","Asarum","Nardus indica","Crocus",
                   "Mastix","Spica nardi"},
        "ESPECIA": {"Cinnamomum","Casia"},
        "BASE": {"Mel despumatum"}
    },
    "Trifera Magna": {
        "ACTIVO": {"Opium","Castoreum","Euphorbia","Pyrethrum","Staphisagria",
                   "Sagapenum","Opopanax","Bdellium","Nardus indica","Hypericum",
                   "Amomum","Petroselinum","Squilla"},
        "ESPECIA": {"Crocus","Piper longum","Piper nigrum","Piper album","Zingiber",
                    "Cinnamomum","Casia","Costus","Myrrha","Galanga","Cardamomum",
                    "Cubeba","Nux moschata"},
        "BASE": {"Mel despumatum","Vinum"}
    },
    "Diamargariton": {
        "ACTIVO": {"Margarita","Corallium rubrum","Corallium album","Lapis lazuli",
                   "Os de corde cervi","Cornu cervi","Doronicum","Zedoaria"},
        "ESPECIA": {"Cinnamomum","Galanga","Nux moschata","Cubeba","Cardamomum",
                    "Crocus","Casia"},
        "BASE": {"Saccharum"}
    },
    "Diaciminum": {
        "ACTIVO": {"Cuminum","Apium","Carum","Amomum","Daucus creticus"},
        "ESPECIA": {"Piper longum","Piper nigrum","Zingiber","Anisi","Cinnamomum"},
        "BASE": {"Mel despumatum"}
    },
    "Unguentum Basilicon": {
        "ACTIVO": {"Resina pini","Pix","Galbanum"},
        "ESPECIA": {"Olibanum"},
        "BASE": {"Cera","Oleum olivarum","Sebum"}
    },
    "Unguentum Populeon": {
        "ACTIVO": {"Populus","Mandragora","Hyoscyamus","Papaver nigrum",
                   "Lactuca","Sempervivum","Solanum","Umbilicus veneris"},
        "ESPECIA": {"Viola"},
        "BASE": {"Axungia porci","Oleum olivarum","Cera"}
    },
    "Pillulae de Hiera": {
        "ACTIVO": {"Aloe","Agaricum","Coloquintida","Mastix","Euphorbia"},
        "ESPECIA": {"Crocus","Cinnamomum","Rosa"},
        "BASE": {"Succo absinthii"}
    },
    "Pillulae Fetidae": {
        "ACTIVO": {"Opopanax","Galbanum","Sagapenum","Castoreum","Asa foetida"},
        "ESPECIA": {"Myrrha","Bdellium"},
        "BASE": {"Succo rutae"}
    },
    "Requies Magna": {
        "ACTIVO": {"Opium","Mandragora","Hyoscyamus","Papaver album","Lactuca",
                   "Psyllium","Gummi arabicum","Amylum","Tragacantha","Glycyrrhiza"},
        "ESPECIA": {"Rosa","Cinnamomum","Nux moschata","Crocus","Camphor"},
        "BASE": {"Saccharum","Aqua rosarum"}
    },
    "Diacodion": {
        "ACTIVO": {"Papaver album","Glycyrrhiza","Gummi arabicum"},
        "ESPECIA": {"Cinnamomum"},
        "BASE": {"Saccharum","Aqua"}
    },
    "Dialtea": {
        "ACTIVO": {"Althaea","Linum","Foenum graecum","Terebinthina","Cera","Colophonia"},
        "ESPECIA": {"Olibanum"},
        "BASE": {"Oleum olivarum","Axungia porci","Aqua"}
    },
    "Philonium Persicum": {
        "ACTIVO": {"Opium","Castoreum","Pyrethrum","Euphorbium","Hyoscyamus",
                   "Nardus indica","Hypocistis","Gummi arabicum","Styrax"},
        "ESPECIA": {"Crocus","Piper longum","Piper nigrum","Zingiber","Cinnamomum",
                    "Myrrha","Casia","Cardamomum"},
        "BASE": {"Mel despumatum"}
    },
    "Oximel Compositum": {
        "ACTIVO": {"Squilla","Petroselinum","Apium","Foeniculum","Carum"},
        "ESPECIA": {"Zingiber","Piper longum","Anisi"},
        "BASE": {"Mel despumatum","Acetum"}
    },
    "Theriac Diatessaron": {
        "ACTIVO": {"Gentiana","Aristolochia rotunda","Laurus"},
        "ESPECIA": {"Myrrha"},
        "BASE": {"Mel despumatum"}
    },
}

# Folio-Recipe matches
all_matches = {
    # Perfect
    "f87r": "Confectio Hamech", "f87v": "Unguentum Apostolorum",
    "f88r": "Trifera Magna", "f93v": "Diascordium",
    "f96v": "Pillulae Aureae", "f100r": "Diamargariton",
    "f100v": "Diaciminum", "f101v": "Trifera Magna", "f103v": "Trifera Magna",
    # Strong
    "f88v": "Philonium Persicum", "f90r": "Aurea Alexandrina",
    "f90v": "Aurea Alexandrina", "f94r": "Aurea Alexandrina",
    "f94v": "Diascordium", "f95r": "Trifera Magna",
    "f95v": "Philonium Persicum", "f96r": "Philonium Persicum",
    "f99r": "Trifera Magna", "f99v": "Aurea Alexandrina",
    "f101r": "Trifera Magna", "f102r": "Philonium Persicum",
    "f102v": "Trifera Magna", "f105r": "Trifera Magna",
    "f105v": "Trifera Magna", "f108r": "Trifera Magna",
    "f112r": "Trifera Magna", "f114v": "Trifera Magna",
    "f116r": "Trifera Magna",
}

# =============================================================================
# STEP 1: Re-parse Voynich corpus to get stems per folio
# =============================================================================
def split_atom(word):
    atoms = re.findall(r'[A-Z][a-z0-9]*', word)
    if len(atoms) > 1:
        return ''.join(atoms[:-1]), atoms[-1]
    elif len(atoms) == 1:
        return word, ""
    return "", ""

# Build botany stems for classification
botany_stems_by_folio = defaultdict(set)
with open('zenodo_voynich/corpus/voynich_sta.txt', 'r', encoding='utf-8') as f:
    for line in f:
        m = re.search(r'<(f[0-9]{1,3}[rv])', line)
        if not m: continue
        folio = m.group(1)
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

# Build stems per recipe folio
recipe_folio_stems = defaultdict(set)
with open('zenodo_voynich/corpus/voynich_sta.txt', 'r', encoding='utf-8') as f:
    for line in f:
        m = re.search(r'<(f[0-9]{1,3}[rv])', line)
        if not m: continue
        folio = m.group(1)
        fm = re.match(r'f(\d+)([rv])', folio)
        if not fm: continue
        fnum = int(fm.group(1))
        if fnum < 87 or fnum > 116: continue
        
        content = line.split('>')[1].strip() if '>' in line else ""
        if not content or content.startswith('<!'):
            continue
        tokens = [t.replace(',','').replace('-','').replace('*','').replace('<','')
                  for t in content.split('.') if t.strip()]
        for t in tokens:
            stem, suf = split_atom(t)
            if len(stem) >= 2:
                recipe_folio_stems[folio].add(stem)

# =============================================================================
# STEP 2: For each stem, build its PRESENCE/ABSENCE profile
# across all matched folios
# =============================================================================
matched_folios = sorted(all_matches.keys())
all_matched_recipes = sorted(set(all_matches.values()))

# Build ingredient -> recipe presence map
ingredient_recipes = {}  # ingredient -> set of recipe names
for rname, rdata in recipes.items():
    for cat in ["ACTIVO", "ESPECIA", "BASE"]:
        for ing in rdata.get(cat, set()):
            if ing not in ingredient_recipes:
                ingredient_recipes[ing] = {"recipes": set(), "category": cat}
            ingredient_recipes[ing]["recipes"].add(rname)
            # Note: some ingredients appear in multiple categories across recipes
            # We take the FIRST category we see

print("=" * 100)
print("REFINED CONSTRAINT SOLVER v3 - PRESENCE/ABSENCE PROFILES")
print("=" * 100)
print()

# For each stem: build which MATCHED RECIPE TYPES it appears in vs doesn't
stem_profiles = {}
for stem in sorted(set(s for f in recipe_folio_stems.values() for s in f)):
    present_recipes = set()
    absent_recipes = set()
    
    for folio in matched_folios:
        recipe = all_matches[folio]
        if stem in recipe_folio_stems.get(folio, set()):
            present_recipes.add(recipe)
        else:
            absent_recipes.add(recipe)
    
    # Only consider stems that appear in at least 2 different matched recipes
    if len(present_recipes) < 2:
        continue
    
    # Skip stems that appear EVERYWHERE (likely function words)
    if len(absent_recipes) == 0:
        continue
    
    stem_profiles[stem] = {
        "present": present_recipes,
        "absent": absent_recipes,
        "type": "EXCL" if stem in exclusive_stems else "GEN" if stem in generic_stems else "UNK"
    }

print(f"Stems with valid presence/absence profile: {len(stem_profiles)}")
print()

# =============================================================================
# STEP 3: MATCH stem profiles against ingredient profiles
# For each stem: find ingredients whose recipe presence is a SUPERSET
# of stem's presence, AND whose recipe absence intersects stem's absence.
#
# Key logic:
# - If stem appears in folio for recipe R, the ingredient MUST be in recipe R
#   (positive constraint)
# - If stem does NOT appear in any folio for recipe R, the ingredient should
#   NOT be in recipe R (negative constraint - softer, since matching isn't perfect)
# =============================================================================

print(f"{'Stem':<20} | {'Type':<5} | {'#Pres':>5} | {'#Abs':>4} | {'Best Candidate':<30} | {'Score':>6} | {'2nd Candidate':<30} | {'Score2':>6}")
print("-" * 140)

results = []

for stem in sorted(stem_profiles.keys(), key=lambda x: -len(stem_profiles[x]['present'])):
    prof = stem_profiles[stem]
    present = prof['present']
    absent = prof['absent']
    stype = prof['type']
    
    # Score each ingredient
    scores = []
    for ing, ing_info in ingredient_recipes.items():
        ing_recipes = ing_info["recipes"]
        ing_cat = ing_info["category"]
        
        # Positive score: how many of stem's present recipes contain this ingredient?
        pos_match = len(present & ing_recipes)
        pos_total = len(present)
        pos_score = pos_match / pos_total if pos_total > 0 else 0
        
        # Negative score: how many of stem's absent recipes do NOT contain this ingredient?
        # (If stem is absent from a folio, and the ingredient is also absent from
        #  that recipe, that's a good sign)
        neg_match = len(absent - ing_recipes)  # absent recipes where ingredient is also absent
        neg_total = len(absent)
        neg_score = neg_match / neg_total if neg_total > 0 else 0
        
        # Discriminativity: penalize ingredients in nearly all recipes
        total_recipes_with_ingredient = len(ing_recipes)
        total_matched = len(set(all_matches.values()))
        discriminativity = 1 - (total_recipes_with_ingredient / len(recipes))
        
        # Combined score: positive match is CRITICAL, negative is supporting
        # An ingredient MUST be present in ALL recipes where the stem appears
        if pos_score < 1.0:
            combined = 0  # Hard constraint: must be in ALL present recipes
        else:
            combined = 0.5 * pos_score + 0.3 * neg_score + 0.2 * discriminativity
        
        if combined > 0:
            scores.append((ing, ing_cat, combined, pos_score, neg_score, discriminativity))
    
    scores.sort(key=lambda x: (-x[2], -x[4]))  # Sort by combined, then neg_score
    
    if len(scores) == 0:
        continue
    
    best = scores[0]
    second = scores[1] if len(scores) > 1 else ("", "", 0, 0, 0, 0)
    
    # Determine confidence
    if len(scores) == 1:
        confidence = "UNIQUE"
    elif best[2] - second[2] > 0.15:
        confidence = "STRONG"
    elif best[2] - second[2] > 0.05:
        confidence = "MODERATE"
    else:
        confidence = "AMBIGUOUS"
    
    # Only print interesting results
    if len(scores) <= 10 and best[2] > 0:
        print(f"{stem:<20} | {stype:<5} | {len(present):>5} | {len(absent):>4} | "
              f"{best[0]:<30} | {best[2]:>5.3f} | "
              f"{second[0]:<30} | {second[2]:>5.3f}  [{confidence}]  "
              f"(+{best[3]:.0%} -{best[4]:.0%} d{best[5]:.0%})")
        
        results.append({
            "Stem": stem, "Type": stype,
            "N_Present": len(present), "N_Absent": len(absent),
            "Present_Recipes": ', '.join(sorted(present)),
            "Absent_Recipes": ', '.join(sorted(absent)),
            "Best_Candidate": best[0], "Best_Category": best[1],
            "Best_Score": round(best[2], 3),
            "Pos_Score": round(best[3], 3), "Neg_Score": round(best[4], 3),
            "Discriminativity": round(best[5], 3),
            "N_Candidates": len(scores),
            "All_Candidates": ' | '.join(f"{s[0]}({s[2]:.3f})" for s in scores[:5]),
            "Confidence": confidence
        })

# =============================================================================
# ANALYSIS: Group by confidence
# =============================================================================
print(f"\n{'='*100}")
print("RESUMEN POR CONFIANZA")
print(f"{'='*100}")

for conf in ["UNIQUE", "STRONG", "MODERATE", "AMBIGUOUS"]:
    group = [r for r in results if r['Confidence'] == conf]
    if not group:
        continue
    print(f"\n--- {conf} ({len(group)} stems) ---")
    for r in group:
        n_cand = r['N_Candidates']
        print(f"  [{r['Stem']}] ({r['Type']}) -> {r['Best_Candidate']} [{r['Best_Category']}]"
              f"  (score={r['Best_Score']}, {n_cand} candidates, neg={r['Neg_Score']})")

# =============================================================================
# DEEP ANALYSIS: Top discriminative identifications
# These are stems where:
#   1. The best candidate has pos_score=100% (present in ALL recipes)
#   2. The neg_score is high (absent from recipes where stem is absent)
#   3. Few total candidates
# =============================================================================
print(f"\n{'='*100}")
print("TOP IDENTIFICACIONES DISCRIMINATIVAS")
print("(Alto pos_score + alto neg_score + pocos candidatos)")
print(f"{'='*100}")

# Sort by: neg_score DESC, then N_Candidates ASC
top = sorted(results, key=lambda r: (-r['Neg_Score'], r['N_Candidates']))

for r in top[:25]:
    print(f"\n  [{r['Stem']}] ({r['Type']}) = {r['Best_Candidate']} [{r['Best_Category']}]")
    print(f"    Score: {r['Best_Score']} | pos={r['Pos_Score']} neg={r['Neg_Score']} disc={r['Discriminativity']}")
    print(f"    Candidates total: {r['N_Candidates']}")
    print(f"    Top candidates: {r['All_Candidates']}")
    print(f"    PRESENT in: {r['Present_Recipes']}")
    print(f"    ABSENT from: {r['Absent_Recipes']}")

# =============================================================================
# SPECIAL: Stems that appear in EXACTLY the right set of recipes for a
# specific ingredient (perfect profile match)
# =============================================================================
print(f"\n{'='*100}")
print("PERFECT PROFILE MATCHES (stem's recipe set == ingredient's recipe set)")
print(f"{'='*100}")

for stem, prof in stem_profiles.items():
    present = prof['present']
    stype = prof['type']
    
    for ing, ing_info in ingredient_recipes.items():
        ing_recipes = ing_info["recipes"]
        # Only consider recipes that are in our matched set
        ing_matched = ing_recipes & set(all_matches.values())
        
        if ing_matched == present and len(present) >= 3:
            absent_violations = present - ing_recipes  # recipes where stem present but ingredient not
            print(f"  [{stem}] ({stype}) == {ing} [{ing_info['category']}]")
            print(f"    Both appear in exactly: {sorted(present)}")
            if absent_violations:
                print(f"    BUT ingredient missing from: {absent_violations}")
            else:
                print(f"    PERFECT MATCH across {len(present)} recipes!")

# =============================================================================
# CSV Output
# =============================================================================
csv_path = 'voynich_constraint_solver_v3_results.csv'
with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=[
        "Stem", "Type", "N_Present", "N_Absent",
        "Present_Recipes", "Absent_Recipes",
        "Best_Candidate", "Best_Category", "Best_Score",
        "Pos_Score", "Neg_Score", "Discriminativity",
        "N_Candidates", "All_Candidates", "Confidence"
    ])
    writer.writeheader()
    writer.writerows(results)

print(f"\n\nCSV: {csv_path}")
print("\nDONE.")
