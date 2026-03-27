import sys
import csv
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

# =============================================================================
# EXPANDED CONSTRAINT PROPAGATION SOLVER v2
# Now with 23 historical recipes and 9 perfect + 19 strong matches
# =============================================================================

# --- FULL 23-RECIPE DATABASE (normalized ingredient names) ---
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

# =============================================================================
# MATCH TABLE: Voynich Folio -> Historical Recipe (from expanded matching)
# =============================================================================
# Perfect matches (100%)
perfect = {
    "f87r": "Confectio Hamech",
    "f87v": "Unguentum Apostolorum",
    "f88r": "Trifera Magna",
    "f93v": "Diascordium",
    "f96v": "Pillulae Aureae",
    "f100r": "Diamargariton",
    "f100v": "Diaciminum",
    "f101v": "Trifera Magna",
    "f103v": "Trifera Magna",
}

# Strong matches (>=90%)
strong = {
    "f88v": "Philonium Persicum",
    "f90r": "Aurea Alexandrina",
    "f90v": "Aurea Alexandrina",
    "f94r": "Aurea Alexandrina",
    "f94v": "Diascordium",
    "f95r": "Trifera Magna",
    "f95v": "Philonium Persicum",
    "f96r": "Philonium Persicum",
    "f99r": "Trifera Magna",
    "f99v": "Aurea Alexandrina",
    "f101r": "Trifera Magna",
    "f102r": "Philonium Persicum",
    "f102v": "Trifera Magna",
    "f105r": "Trifera Magna",
    "f105v": "Trifera Magna",
    "f108r": "Trifera Magna",
    "f112r": "Trifera Magna",
    "f114v": "Trifera Magna",
    "f116r": "Trifera Magna",
}

all_matches = {**perfect, **strong}

# =============================================================================
# STEP 1: Build stem -> folio -> recipe mapping from the matching results
# For each stem, find which matched folios it appears in, and thus which
# historical recipes it should map to.
# =============================================================================

# Re-read the stems_in_matched_folios data
stem_recipe_map = defaultdict(lambda: {"folios": set(), "recipes": set()})

with open('voynich_stems_in_matched_folios.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        stem = row['Stem']
        stype = row['Type']
        folios = set(row['Matched_Folios'].split(' | '))
        recipe_names = row['Matched_Recipes'].split(' | ')
        
        stem_recipe_map[stem]['type'] = stype
        stem_recipe_map[stem]['folios'] = folios
        # Map each folio to its matched recipe
        for folio in folios:
            if folio in all_matches:
                stem_recipe_map[stem]['recipes'].add(all_matches[folio])

# =============================================================================
# STEP 2: For the most constrained stems (appear in 3+ different recipes),
# intersect ingredient lists
# =============================================================================

print("=" * 100)
print("EXPANDED CONSTRAINT PROPAGATION SOLVER v2")
print("=" * 100)
print(f"Database: {len(recipes)} historical recipes")
print(f"Matched folios: {len(perfect)} perfect + {len(strong)} strong = {len(all_matches)} total")
print(f"Stems in matched folios: {len(stem_recipe_map)}")
print()

# Focus on stems that appear in 3+ DISTINCT recipes (not just folios)
results = []

print(f"{'Stem':<20} | {'Type':<5} | {'#Fol':>4} | {'#Rec':>4} | {'Recipes':<60} | {'Intersection'}")
print("-" * 160)

for stem in sorted(stem_recipe_map.keys(), key=lambda x: -len(stem_recipe_map[x]['recipes'])):
    info = stem_recipe_map[stem]
    unique_recipes = info['recipes']
    n_folios = len(info['folios'])
    n_recipes = len(unique_recipes)
    stype = info.get('type', '?')
    
    if n_recipes < 2:
        continue  # Need at least 2 recipes for intersection
    
    # Try ALL three categories and find best intersection
    best_cat = None
    best_inter = None
    best_size = 999
    
    for cat in ["ACTIVO", "ESPECIA", "BASE"]:
        sets = []
        for rname in unique_recipes:
            if rname in recipes and cat in recipes[rname]:
                sets.append(recipes[rname][cat])
        
        if len(sets) >= 2:
            inter = sets[0].copy()
            for s in sets[1:]:
                inter &= s
            if len(inter) < best_size and len(inter) > 0:
                best_size = len(inter)
                best_inter = inter
                best_cat = cat
    
    # Also try: check if this stem has an empty intersection in ALL categories
    all_empty = True
    category_results = {}
    for cat in ["ACTIVO", "ESPECIA", "BASE"]:
        sets = []
        for rname in unique_recipes:
            if rname in recipes and cat in recipes[rname]:
                sets.append(recipes[rname][cat])
        if len(sets) >= 2:
            inter = sets[0].copy()
            for s in sets[1:]:
                inter &= s
            category_results[cat] = inter
            if len(inter) > 0:
                all_empty = False
        else:
            category_results[cat] = set()
    
    recipe_str = ', '.join(sorted(unique_recipes))[:58]
    
    if best_inter and len(best_inter) <= 5:
        inter_str = f"[{best_cat}] {', '.join(sorted(best_inter))}"
        
        if len(best_inter) == 1:
            confidence = "*** UNIQUE ***"
        elif len(best_inter) == 2:
            confidence = "** 2 candidates **"
        elif len(best_inter) == 3:
            confidence = "* 3 candidates *"
        else:
            confidence = f"{len(best_inter)} candidates"
        
        print(f"{stem:<20} | {stype:<5} | {n_folios:>4} | {n_recipes:>4} | {recipe_str:<60} | {inter_str} {confidence}")
        
        results.append({
            "Stem": stem, "Type": stype, "N_Folios": n_folios,
            "N_Recipes": n_recipes, "Recipes": ', '.join(sorted(unique_recipes)),
            "Best_Category": best_cat, "Intersection_Size": len(best_inter),
            "Candidates": ' | '.join(sorted(best_inter)),
            "Confidence": confidence
        })
    
    elif best_inter:
        inter_str = f"[{best_cat}] {len(best_inter)} candidates"
        print(f"{stem:<20} | {stype:<5} | {n_folios:>4} | {n_recipes:>4} | {recipe_str:<60} | {inter_str}")
        results.append({
            "Stem": stem, "Type": stype, "N_Folios": n_folios,
            "N_Recipes": n_recipes, "Recipes": ', '.join(sorted(unique_recipes)),
            "Best_Category": best_cat, "Intersection_Size": len(best_inter),
            "Candidates": f"{len(best_inter)} candidates",
            "Confidence": "LOW"
        })
    
    elif all_empty:
        # This stem has EMPTY intersection in all categories -> semantic class word
        print(f"{stem:<20} | {stype:<5} | {n_folios:>4} | {n_recipes:>4} | {recipe_str:<60} | ALL EMPTY -> FUNCTION WORD or SEMANTIC CLASS")
        results.append({
            "Stem": stem, "Type": stype, "N_Folios": n_folios,
            "N_Recipes": n_recipes, "Recipes": ', '.join(sorted(unique_recipes)),
            "Best_Category": "ALL_EMPTY", "Intersection_Size": 0,
            "Candidates": "FUNCTION/CLASS WORD",
            "Confidence": "FUNCTION WORD"
        })

# =============================================================================
# HIGHLIGHT: UNIQUE IDENTIFICATIONS
# =============================================================================
print(f"\n{'='*100}")
print(f"IDENTIFICACIONES UNICAS (interseccion = 1 ingrediente)")
print(f"{'='*100}")

unique_ids = [r for r in results if r['Intersection_Size'] == 1]
print(f"\nTotal identificaciones unicas: {len(unique_ids)}")
for r in unique_ids:
    print(f"\n  [{r['Stem']}] ({r['Type']}) = {r['Candidates']}")
    print(f"    Categoria: {r['Best_Category']}")
    print(f"    Aparece en {r['N_Folios']} folios, {r['N_Recipes']} recetas distintas")
    print(f"    Recetas: {r['Recipes']}")

# =============================================================================
# HIGHLIGHT: 2-CANDIDATE IDENTIFICATIONS
# =============================================================================
print(f"\n{'='*100}")
print(f"IDENTIFICACIONES CON 2 CANDIDATOS")
print(f"{'='*100}")

two_cands = [r for r in results if r['Intersection_Size'] == 2]
print(f"\nTotal: {len(two_cands)}")
for r in two_cands:
    print(f"\n  [{r['Stem']}] ({r['Type']}) = {{{r['Candidates']}}}")
    print(f"    Categoria: {r['Best_Category']}")
    print(f"    Aparece en {r['N_Folios']} folios, {r['N_Recipes']} recetas")
    print(f"    Recetas: {r['Recipes']}")

# =============================================================================
# HIGHLIGHT: FUNCTION/CLASS WORDS
# =============================================================================
print(f"\n{'='*100}")
print(f"PALABRAS FUNCIONALES / CLASES SEMANTICAS (interseccion vacia en todas las categorias)")
print(f"{'='*100}")

func_words = [r for r in results if r['Best_Category'] == 'ALL_EMPTY']
print(f"\nTotal: {len(func_words)}")
for r in func_words:
    print(f"  [{r['Stem']}] ({r['Type']}) -> {r['N_Folios']} folios, {r['N_Recipes']} recetas: {r['Recipes']}")

# =============================================================================
# SPECIAL ANALYSIS: K1J1A1 (tentative Cinnamomum)
# =============================================================================
print(f"\n{'='*100}")
print(f"ANALISIS ESPECIAL: K1J1A1 (candidato a Cinnamomum)")
print(f"{'='*100}")

k1j1a1_folios = stem_recipe_map.get('K1J1A1', {}).get('folios', set())
k1j1a1_recipes = stem_recipe_map.get('K1J1A1', {}).get('recipes', set())

print(f"\nK1J1A1 aparece en {len(k1j1a1_folios)} folios matched:")
for folio in sorted(k1j1a1_folios):
    recipe = all_matches.get(folio, '?')
    has_cinn = "Cinnamomum" in recipes.get(recipe, {}).get("ESPECIA", set())
    print(f"  {folio} = {recipe} -> Cinnamomum in recipe: {'SI' if has_cinn else '*** NO ***'}")

print(f"\nRecetas unicas: {sorted(k1j1a1_recipes)}")
print(f"\nPrueba de Cinnamomum:")
all_have_cinn = True
for rname in k1j1a1_recipes:
    has_it = "Cinnamomum" in recipes.get(rname, {}).get("ESPECIA", set())
    if not has_it:
        # Check ACTIVO too (Hiera Picra has Crocus in ACTIVO)
        has_it = "Cinnamomum" in recipes.get(rname, {}).get("ACTIVO", set())
    print(f"  {rname}: Cinnamomum presente = {'SI' if has_it else '*** NO ***'}")
    if not has_it:
        all_have_cinn = False

if all_have_cinn:
    print(f"\n  >>> CONFIRMADO: K1J1A1 = Cinnamomum (aparece como ESPECIA en TODAS las {len(k1j1a1_recipes)} recetas)")
else:
    print(f"\n  >>> PARCIAL: K1J1A1 podria no ser Cinnamomum (ausente en alguna receta)")

# =============================================================================
# SPECIAL ANALYSIS: L1A1 vs D1A1Q1K1A1 (Zingiber vs Piper longum)
# =============================================================================
print(f"\n{'='*100}")
print(f"ANALISIS: L1A1 vs D1A1Q1K1A1 (Zingiber vs Piper longum)")
print(f"{'='*100}")

for stem_name in ['L1A1', 'D1A1Q1K1A1']:
    s_info = stem_recipe_map.get(stem_name, {})
    s_recipes = s_info.get('recipes', set())
    s_folios = s_info.get('folios', set())
    
    print(f"\n[{stem_name}] -> {len(s_folios)} folios, {len(s_recipes)} recetas: {sorted(s_recipes)}")
    
    for candidate in ['Zingiber', 'Piper longum']:
        present_count = 0
        absent_count = 0
        for rname in s_recipes:
            has_it = candidate in recipes.get(rname, {}).get("ESPECIA", set())
            if has_it:
                present_count += 1
            else:
                absent_count += 1
        total = present_count + absent_count
        pct = (present_count / total * 100) if total > 0 else 0
        print(f"  {candidate}: presente en {present_count}/{total} recetas ({pct:.1f}%)")

# =============================================================================
# CSV OUTPUT
# =============================================================================
csv_path = 'voynich_constraint_solver_v2_results.csv'
with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=[
        "Stem", "Type", "N_Folios", "N_Recipes", "Recipes",
        "Best_Category", "Intersection_Size", "Candidates", "Confidence"
    ])
    writer.writeheader()
    writer.writerows(results)

print(f"\n\nCSV guardado: {csv_path}")
print("\nDONE.")
