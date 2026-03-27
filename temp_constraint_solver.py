import sys
import csv
sys.stdout.reconfigure(encoding='utf-8')

# =============================================================================
# CONSTRAINT PROPAGATION SOLVER
# Para cada stem Voynich consistente, intersectar las listas de ingredientes
# historicos de la misma categoria en todas las recetas donde aparece.
# Si la interseccion es pequena -> identificacion candidata.
# =============================================================================

# --- HISTORICAL RECIPE DATABASE ---
# Each recipe: name -> {ACTIVO: set(), ESPECIA: set(), BASE: set()}

recipes = {
    "Theriac Magna": {
        "ACTIVO": {
            "Opium", "Trochisci de vipera", "Squilla", "Hedychium",
            "Castoreum", "Nardus celtica", "Petroselinum", "Phu/Valeriana",
            "Amomum", "Acorus calamus", "Hypericum", "Gentiana",
            "Aristolochia", "Opopanax", "Sagapenum", "Galbanum",
            "Balsamum", "Styrax", "Terebinthina", "Bitumen judaicum"
        },
        "ESPECIA": {
            "Crocus", "Zingiber", "Cinnamomum", "Piper longum",
            "Piper nigrum", "Myrrha", "Olibanum", "Casia",
            "Costus", "Anisi", "Foeniculum", "Daucus creticus"
        },
        "BASE": {"Mel despumatum", "Vinum"}
    },
    "Mithridatium": {
        "ACTIVO": {
            "Opium", "Castoreum", "Nardus indica", "Nardus celtica",
            "Gentiana", "Aristolochia longa", "Aristolochia rotunda",
            "Hypericum", "Sagapenum", "Opopanax", "Acacia",
            "Gummi arabicum", "Hypocistis", "Stachys",
            "Thlaspi", "Daucus creticus"
        },
        "ESPECIA": {
            "Crocus", "Zingiber", "Cinnamomum", "Piper longum",
            "Piper nigrum", "Myrrha", "Costus", "Casia",
            "Anisi", "Petroselinum", "Foeniculum", "Cardamomum"
        },
        "BASE": {"Mel despumatum", "Vinum"}
    },
    "Diascordium": {
        "ACTIVO": {
            "Scordium", "Opium", "Castoreum", "Galbanum",
            "Styrax", "Bistorta"
        },
        "ESPECIA": {
            "Cinnamomum", "Piper longum", "Zingiber",
            "Rosa", "Gentiana", "Dictamnus"
        },
        "BASE": {"Mel despumatum"}
    },
    "Pillulae Cochiae": {
        "ACTIVO": {"Colocynthis", "Aloe", "Scammonium"},
        "ESPECIA": {"Staphisagria", "Bdellium"},
        "BASE": {"Succo absinthii"}
    },
    "Pillulae Aureae": {
        "ACTIVO": {"Aloe", "Diagridium", "Mastix", "Rosa"},
        "ESPECIA": {"Crocus", "Cinnamomum"},
        "BASE": {"Succo absinthii"}
    },
    "Unguentum Apostolorum": {
        "ACTIVO": {
            "Aristolochia longa", "Aristolochia rotunda", "Opopanax",
            "Galbanum", "Bdellium", "Verdigris", "Litharge"
        },
        "ESPECIA": {"Olibanum", "Myrrha"},
        "BASE": {"Cera", "Oleum olivarum", "Resina pini"}
    },
    "Electuarium Rosarum": {
        "ACTIVO": {"Rosa gallica", "Senna", "Tamarindus", "Viola"},
        "ESPECIA": {"Cinnamomum", "Zingiber", "Anisi"},
        "BASE": {"Saccharum"}
    },
    "Aurea Alexandrina": {
        "ACTIVO": {
            "Opium", "Castoreum", "Stachys", "Hypericum",
            "Petroselinum", "Acorus calamus", "Phu/Valeriana", "Squilla"
        },
        "ESPECIA": {
            "Crocus", "Piper longum", "Piper nigrum", "Zingiber",
            "Cinnamomum", "Myrrha", "Costus", "Nardus",
            "Anisi", "Foeniculum", "Casia"
        },
        "BASE": {"Mel despumatum", "Vinum", "Saccharum"}
    }
}

# --- CONSISTENT STEMS FROM OUR CROSS-CONSISTENCY TEST ---
# Format: stem -> [(recipe_name, ingredient_assigned, category), ...]
consistent_stems = {
    "K1K2A1": {
        "category": "ACTIVO",
        "type": "Exclusivo",
        "origin_folio": "f17v",
        "assignments": [
            ("Unguentum Apostolorum", "Aristolochia longa"),
            ("Diascordium", "Castoreum"),
            ("Theriac Magna", "Hedychium"),
        ]
    },
    "BaA3": {
        "category": "ACTIVO",
        "type": "Exclusivo",
        "origin_folio": "f33v",
        "assignments": [
            ("Unguentum Apostolorum", "Galbanum"),
            ("Pillulae Aureae", "Diagridium"),
            ("Theriac Magna", "Terebinthina"),
        ]
    },
    "U2J1A1": {
        "category": "ACTIVO",
        "type": "Exclusivo",
        "origin_folio": "f52v",
        "assignments": [
            ("Diascordium", "Opium"),
            ("Pillulae Aureae", "Aloe"),
        ]
    },
    "D1A1Q1J1A1": {
        "category": "ACTIVO",
        "type": "Exclusivo",
        "origin_folio": "f49r",
        "assignments": [
            ("Aurea Alexandrina", "Opium"),
            ("Theriac Magna", "Bitumen judaicum"),
        ]
    },
    "L1A1": {
        "category": "ESPECIA",
        "type": "Generico",
        "origin_folio": "multiple",
        "assignments": [
            ("Diascordium", "Zingiber"),
            ("Theriac Magna", "Piper nigrum"),
        ]
    },
    "K1A3": {
        "category": "ESPECIA",
        "type": "Generico",
        "origin_folio": "multiple",
        "assignments": [
            ("Pillulae Aureae", "Cinnamomum"),
            ("Theriac Magna", "Zingiber"),
        ]
    },
    "D1A1Q1K1A1": {
        "category": "ESPECIA",
        "type": "Generico",
        "origin_folio": "multiple",
        "assignments": [
            ("Diascordium", "Rosa"),
            ("Aurea Alexandrina", "Anisi"),
        ]
    },
    "D1A1": {
        "category": "DESCONOCIDO",
        "type": "Generico",
        "origin_folio": "multiple",
        "assignments": [
            ("Unguentum Apostolorum", "?"),
            ("Theriac Magna", "?"),
        ]
    },
    "A2K1A1": {
        "category": "DESCONOCIDO",
        "type": "Generico",
        "origin_folio": "multiple",
        "assignments": [
            ("Diascordium", "?"),
            ("Aurea Alexandrina", "?"),
        ]
    },
    "A1Q1A1": {
        "category": "DESCONOCIDO",
        "type": "Generico",
        "origin_folio": "multiple",
        "assignments": [
            ("Aurea Alexandrina", "?"),
            ("Theriac Magna", "?"),
        ]
    },
}

print("=" * 80)
print("CONSTRAINT PROPAGATION SOLVER - Voynich Stem Identification")
print("=" * 80)
print()

results = []

for stem, info in consistent_stems.items():
    cat = info["category"]
    stem_type = info["type"]
    origin = info["origin_folio"]
    assignments = info["assignments"]
    
    print(f"--- STEM: [{stem}] (Type: {stem_type}, Category: {cat}) ---")
    print(f"    Origin folio: {origin}")
    print(f"    Appears in {len(assignments)} recipe matches:")
    
    if cat == "DESCONOCIDO":
        print(f"    Category UNKNOWN - cannot constrain. Skipping.")
        print()
        results.append({
            "Stem": stem, "Type": stem_type, "Category": cat,
            "N_Recipes": len(assignments), "Origin": origin,
            "Intersection_Size": "N/A",
            "Candidates": "UNKNOWN CATEGORY",
            "Confidence": "NONE"
        })
        continue
    
    # Collect the set of ingredients of this category from each recipe
    ingredient_sets = []
    for recipe_name, assigned_ingredient in assignments:
        print(f"    - {recipe_name}: assigned={assigned_ingredient}")
        if recipe_name in recipes and cat in recipes[recipe_name]:
            ingredient_sets.append((recipe_name, recipes[recipe_name][cat]))
    
    if len(ingredient_sets) < 2:
        print(f"    Not enough recipes with category {cat}. Skipping.")
        print()
        results.append({
            "Stem": stem, "Type": stem_type, "Category": cat,
            "N_Recipes": len(assignments), "Origin": origin,
            "Intersection_Size": "N/A",
            "Candidates": "INSUFFICIENT DATA",
            "Confidence": "NONE"
        })
        continue
    
    # Intersect all ingredient sets
    intersection = ingredient_sets[0][1].copy()
    recipe_names = [ingredient_sets[0][0]]
    for recipe_name, ing_set in ingredient_sets[1:]:
        intersection = intersection & ing_set
        recipe_names.append(recipe_name)
    
    print(f"\n    INTERSECTION of {cat} ingredients across {recipe_names}:")
    print(f"    Size: {len(intersection)}")
    
    if len(intersection) == 0:
        print(f"    >> EMPTY INTERSECTION - No ingredient is {cat} in ALL these recipes")
        confidence = "CONFLICT"
    elif len(intersection) == 1:
        print(f"    >> UNIQUE MATCH: {intersection}")
        confidence = "HIGH (unique)"
    elif len(intersection) <= 3:
        print(f"    >> NARROW CANDIDATES: {intersection}")
        confidence = "MEDIUM (2-3 candidates)"
    elif len(intersection) <= 6:
        print(f"    >> MODERATE CANDIDATES: {intersection}")
        confidence = "LOW (4-6 candidates)"
    else:
        print(f"    >> WIDE SET: {intersection}")
        confidence = "VERY LOW (>6 candidates)"
    
    for ing in sorted(intersection):
        print(f"       - {ing}")
    
    print()
    
    results.append({
        "Stem": stem, "Type": stem_type, "Category": cat,
        "N_Recipes": len(assignments), "Origin": origin,
        "Intersection_Size": len(intersection),
        "Candidates": " | ".join(sorted(intersection)) if intersection else "EMPTY",
        "Confidence": confidence
    })

# --- SUMMARY ---
print("\n" + "=" * 80)
print("SUMMARY OF CONSTRAINT PROPAGATION RESULTS")
print("=" * 80)

high = [r for r in results if "HIGH" in r["Confidence"]]
medium = [r for r in results if "MEDIUM" in r["Confidence"]]
low = [r for r in results if "LOW" in r["Confidence"] and "VERY" not in r["Confidence"]]
conflict = [r for r in results if "CONFLICT" in r["Confidence"]]
unknown = [r for r in results if "NONE" in r["Confidence"]]

print(f"\nHIGH confidence (unique match): {len(high)}")
for r in high:
    print(f"  [{r['Stem']}] = {r['Candidates']}")

print(f"\nMEDIUM confidence (2-3 candidates): {len(medium)}")
for r in medium:
    print(f"  [{r['Stem']}] in {{{r['Candidates']}}}")

print(f"\nLOW confidence (4-6 candidates): {len(low)}")
for r in low:
    print(f"  [{r['Stem']}] in {{{r['Candidates']}}}")

print(f"\nCONFLICTS (empty intersection): {len(conflict)}")
for r in conflict:
    print(f"  [{r['Stem']}]")

print(f"\nUNKNOWN/INSUFFICIENT: {len(unknown)}")
for r in unknown:
    print(f"  [{r['Stem']}]")

# --- SECOND PASS: For stems with empty intersection, try PAIRWISE ---
print("\n\n" + "=" * 80)
print("SECOND PASS: PAIRWISE INTERSECTION FOR CONFLICT STEMS")
print("=" * 80)

for stem, info in consistent_stems.items():
    cat = info["category"]
    if cat == "DESCONOCIDO":
        continue
    
    assignments = info["assignments"]
    ingredient_sets = []
    for recipe_name, _ in assignments:
        if recipe_name in recipes and cat in recipes[recipe_name]:
            ingredient_sets.append((recipe_name, recipes[recipe_name][cat]))
    
    # Full intersection
    if len(ingredient_sets) >= 2:
        full_inter = ingredient_sets[0][1].copy()
        for _, s in ingredient_sets[1:]:
            full_inter &= s
        if len(full_inter) == 0 and len(ingredient_sets) >= 3:
            print(f"\n--- [{stem}] ({cat}) - Full intersection EMPTY, trying pairs ---")
            for i in range(len(ingredient_sets)):
                for j in range(i+1, len(ingredient_sets)):
                    pair_inter = ingredient_sets[i][1] & ingredient_sets[j][1]
                    print(f"  {ingredient_sets[i][0]} x {ingredient_sets[j][0]}: "
                          f"{len(pair_inter)} shared -> {sorted(pair_inter)[:5]}...")

# --- THIRD PASS: Additional stems that appear in matched folios ---
# For the 3 perfect recipe matches (f87v, f93v, f96v), we know EXACTLY which
# historical ingredients are in the recipe. Every Voynich stem in those folios
# MUST be one of those ingredients. Let's check which stems appear ONLY in one
# of these folios and can be directly assigned.
print("\n\n" + "=" * 80)
print("THIRD PASS: DIRECT ASSIGNMENT FROM PERFECT-MATCH FOLIOS")
print("=" * 80)
print("For folios with 100% size match, stems that appear ONLY in that recipe")
print("folio (and nowhere else in recipe section) can be directly assigned.")

# Read the recipe profiles to get stems per folio
# f87v = Unguentum Apostolorum (12 ing): ACTIVO x7, ESPECIA x2, BASE x3
# f93v = Diascordium (14 ing): ACTIVO x6, ESPECIA x6, BASE x1
# f96v = Pillulae Aureae (7 ing): ACTIVO x4, ESPECIA x2, BASE x1

perfect_matches = {
    "f87v": {
        "recipe": "Unguentum Apostolorum",
        "total": 12,
        "exclusives": ["K1K2A1", "D1A1Q1A1B1A3", "AbQ1A3", "BaA3"],
        "generics": ["K1J1A1", "C2A3", "B1A3", "A1Q2A1", "Q1K1A1",
                      "D1A1", "A1Q2A1", "D1A1Q1A1B1A3"],
    },
    "f93v": {
        "recipe": "Diascordium",
        "total": 14,
        "exclusives": ["Q2K1A1B1A3", "U2J1A1", "K1K2A1"],
        "generics": ["D1A1Q2K1A1", "U1A1", "C2A1", "L1A1", "D1A1Q1K1A1",
                     "A2K1A1", "B1K1A1", "L1J1A1", "K1J1A1", "K1A1", "C2A3"],
    },
    "f96v": {
        "recipe": "Pillulae Aureae",
        "total": 7,
        "exclusives": ["U2J1A1", "BaA3"],
        "generics": ["C2A1", "A1B1A3", "K1A3", "C2A3", "K1J1A1"],
    }
}

for folio, data in perfect_matches.items():
    print(f"\n--- {folio} = {data['recipe']} ({data['total']} ingredients) ---")
    print(f"  Exclusive stems in this folio: {data['exclusives']}")
    print(f"  Generic stems in this folio: {data['generics']}")
    
    recipe_name = data['recipe']
    r = recipes[recipe_name]
    all_ingredients = []
    for cat in ["ACTIVO", "ESPECIA", "BASE"]:
        for ing in sorted(r[cat]):
            all_ingredients.append(f"{ing} ({cat})")
    
    print(f"  Historical ingredients: {len(r['ACTIVO'])} ACTIVO, {len(r['ESPECIA'])} ESPECIA, {len(r['BASE'])} BASE")
    for ing in all_ingredients:
        print(f"    {ing}")
    
    total_stems = len(data['exclusives']) + len(data['generics'])
    print(f"  Total unique stems in folio: ~{total_stems}")
    print(f"  Historical ingredients: {data['total']}")
    
    if total_stems <= data['total']:
        print(f"  >> GOOD: Stems <= Ingredients. Each stem maps to one ingredient.")
    else:
        print(f"  >> NOTE: More stems ({total_stems}) than ingredients ({data['total']}). "
              f"Some stems may be syntax/function words, not ingredients.")


# --- WRITE CSV ---
csv_path = r"C:\Ntizar_Obsidian\Ntizar_Brain\MASTERTMIND\voynich_constraint_solver_results.csv"
with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=[
        "Stem", "Type", "Category", "N_Recipes", "Origin",
        "Intersection_Size", "Candidates", "Confidence"
    ])
    writer.writeheader()
    writer.writerows(results)

print(f"\n\nCSV saved to: {csv_path}")


# === FOURTH PASS: CROSS-STEM CO-OCCURRENCE CONSTRAINTS ===
print("\n\n" + "=" * 80)
print("FOURTH PASS: CO-OCCURRENCE CONSTRAINTS")
print("=" * 80)
print("If two stems always appear together in Voynich recipe folios,")
print("AND two ingredients always appear together in historical recipes,")
print("this strengthens the mapping.")
print()

# Which stems appear in which recipe folios?
# From the consistency CSV, we know which recipe-matched folios each stem appears in
stem_to_matched_folios = {
    "K1K2A1": {"f87v", "f93v", "f96r", "f90v", "f88r", "f88v", "f89v",
               "f100v", "f101v", "f102v", "f104r", "f104v", "f112v",
               "f113r", "f114v", "f115r", "f115v"},
    "BaA3":   {"f87v", "f96v", "f89r", "f89v", "f94r", "f94v", "f95r",
               "f95v", "f96r", "f99r", "f100r", "f101v", "f102r",
               "f103r", "f103v", "f104r", "f105r", "f105v", "f106r",
               "f106v", "f107v", "f108r", "f108v", "f111r", "f112r",
               "f113r", "f113v", "f114r", "f114v", "f116r"},
    "U2J1A1": {"f93v", "f96v", "f88r", "f90v", "f96r", "f99r", "f99v",
               "f100r", "f101r", "f102v"},
    "D1A1Q1J1A1": {"f88r", "f88v", "f89r", "f89v", "f90r", "f90v",
                    "f96r", "f99r", "f99v", "f100r", "f100v", "f101r",
                    "f101v", "f102r", "f102v", "f103r", "f104r", "f104v",
                    "f106r", "f107r", "f107v", "f108r", "f108v", "f111r",
                    "f111v", "f113r", "f115r"},
}

# Check co-occurrence between consistent ACTIVO stems
activo_stems = ["K1K2A1", "BaA3", "U2J1A1", "D1A1Q1J1A1"]
print("Co-occurrence matrix for ACTIVO stems (in recipe folios):")
print(f"{'':>20}", end="")
for s in activo_stems:
    print(f"{s:>18}", end="")
print()

for s1 in activo_stems:
    print(f"{s1:>20}", end="")
    for s2 in activo_stems:
        overlap = stem_to_matched_folios[s1] & stem_to_matched_folios[s2]
        print(f"{len(overlap):>18}", end="")
    print()

print()

# Now check: which PAIRS of historical ACTIVO ingredients appear together
# in the SAME sets of recipes?
print("Historical ACTIVO ingredient co-occurrence across matched recipes:")
print("(Which ACTIVO ingredients appear together in Ung.Apost + Diascord + Theriac + Pill.Aureae + Aurea Alex?)")
print()

# Build ingredient-to-recipe map for ACTIVO category
activo_ing_recipes = {}
for recipe_name, recipe_data in recipes.items():
    for ing in recipe_data.get("ACTIVO", set()):
        if ing not in activo_ing_recipes:
            activo_ing_recipes[ing] = set()
        activo_ing_recipes[ing].add(recipe_name)

# Find ingredients that appear in exactly the same set of recipes as our stems
# Our stems appear in these matched recipes:
# K1K2A1: Ung.Apost, Diascord, Theriac
# BaA3: Ung.Apost, Pill.Aureae, Theriac
# U2J1A1: Diascord, Pill.Aureae
# D1A1Q1J1A1: Aurea Alex, Theriac

stem_recipe_sets = {
    "K1K2A1": {"Unguentum Apostolorum", "Diascordium", "Theriac Magna"},
    "BaA3": {"Unguentum Apostolorum", "Pillulae Aureae", "Theriac Magna"},
    "U2J1A1": {"Diascordium", "Pillulae Aureae"},
    "D1A1Q1J1A1": {"Aurea Alexandrina", "Theriac Magna"},
}

print("Looking for ACTIVO ingredients whose recipe profile matches each stem:")
for stem, stem_recipes in stem_recipe_sets.items():
    print(f"\n  [{stem}] appears in ACTIVO of: {stem_recipes}")
    matches = []
    for ing, ing_recipes in activo_ing_recipes.items():
        # The ingredient must be ACTIVO in at least these recipes
        if stem_recipes.issubset(ing_recipes):
            matches.append((ing, ing_recipes))
        # Also check: ingredient present in exactly these recipes
    
    exact_matches = []
    superset_matches = []
    for ing, ing_recipes in activo_ing_recipes.items():
        if ing_recipes == stem_recipes:
            exact_matches.append(ing)
        elif stem_recipes.issubset(ing_recipes):
            superset_matches.append((ing, ing_recipes))
    
    if exact_matches:
        print(f"  >> EXACT PROFILE MATCH: {exact_matches}")
    else:
        print(f"  >> No exact profile match")
    
    if superset_matches:
        print(f"  >> SUPERSET matches (ingredient in these + more):")
        for ing, recs in superset_matches:
            print(f"     {ing}: {recs}")


# === ESPECIA stems ===
print("\n\nLooking for ESPECIA ingredients whose recipe profile matches each stem:")

especia_ing_recipes = {}
for recipe_name, recipe_data in recipes.items():
    for ing in recipe_data.get("ESPECIA", set()):
        if ing not in especia_ing_recipes:
            especia_ing_recipes[ing] = set()
        especia_ing_recipes[ing].add(recipe_name)

especia_stem_recipe_sets = {
    "L1A1": {"Diascordium", "Theriac Magna"},
    "K1A3": {"Pillulae Aureae", "Theriac Magna"},
    "D1A1Q1K1A1": {"Diascordium", "Aurea Alexandrina"},
}

for stem, stem_recipes in especia_stem_recipe_sets.items():
    print(f"\n  [{stem}] appears in ESPECIA of: {stem_recipes}")
    
    exact_matches = []
    superset_matches = []
    for ing, ing_recipes in especia_ing_recipes.items():
        if ing_recipes == stem_recipes:
            exact_matches.append(ing)
        elif stem_recipes.issubset(ing_recipes):
            superset_matches.append((ing, ing_recipes))
    
    if exact_matches:
        print(f"  >> EXACT PROFILE MATCH: {exact_matches}")
    else:
        print(f"  >> No exact profile match")
    
    if superset_matches:
        print(f"  >> SUPERSET matches:")
        for ing, recs in superset_matches:
            print(f"     {ing}: {recs}")


print("\n\nDONE.")
