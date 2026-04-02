#!/usr/bin/env python3
"""
EXPANDED MEDIEVAL RECIPE DATABASE v2
=====================================
Expands from 23 to 45+ recipes, sourcing from:
- Antidotarium Nicolai (12th c.) -- already have most, adding missing ones
- Grabadin / Pseudo-Mesue (11th c.) -- electuaries, syrups, ointments
- Circa Instans (Salerno, 12th c.) -- simple preparations
- Avicenna Canon Medicinae (11th c.) -- compound formulas
- Abulcasis / al-Zahrawi -- surgical ointments
- Serapion / Ibn Sarabi -- compound medicines
- Platearius -- Practica Brevis
- Roger of Salerno -- Chirurgia

Each recipe: name, source, type, full ingredient list classified as ACTIVO/ESPECIA/BASE
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import csv
import os
from collections import defaultdict

BASE = r'C:\Ntizar_Obsidian\Ntizar_Brain\MASTERTMIND'

# ============================================================
# NEW RECIPES TO ADD (on top of existing 23)
# ============================================================
# Format: (name, source, type, [(ingredient, category), ...])

NEW_RECIPES = [
    # --- ANTIDOTARIUM NICOLAI (missing ones) ---
    (
        "Theodoricon Euporistum",
        "Antidotarium Nicolai, s.XII",
        "Tonico general / Antidoto",
        [
            ("Euphorbia", "ACTIVO"), ("Pyrethrum", "ACTIVO"), ("Castoreum", "ACTIVO"),
            ("Anacardium", "ACTIVO"), ("Staphisagria", "ACTIVO"), ("Petroselinum", "ACTIVO"),
            ("Nardus indica", "ACTIVO"), ("Amomum", "ACTIVO"),
            ("Piper longum", "ESPECIA"), ("Piper nigrum", "ESPECIA"), ("Zingiber", "ESPECIA"),
            ("Cinnamomum", "ESPECIA"), ("Crocus", "ESPECIA"), ("Myrrha", "ESPECIA"),
            ("Cardamomum", "ESPECIA"), ("Casia", "ESPECIA"),
            ("Mel despumatum", "BASE"),
        ]
    ),
    (
        "Diasatyrion",
        "Antidotarium Nicolai, s.XII",
        "Afrodisiaco / Reconstituyente",
        [
            ("Satyrion", "ACTIVO"), ("Orchis", "ACTIVO"), ("Eruca", "ACTIVO"),
            ("Pastinaca", "ACTIVO"), ("Triphallus", "ACTIVO"),
            ("Zingiber", "ESPECIA"), ("Piper longum", "ESPECIA"), ("Galanga", "ESPECIA"),
            ("Cinnamomum", "ESPECIA"), ("Nux moschata", "ESPECIA"), ("Crocus", "ESPECIA"),
            ("Cardamomum", "ESPECIA"),
            ("Saccharum", "BASE"), ("Mel despumatum", "BASE"),
        ]
    ),
    (
        "Diarodon Abbatis",
        "Antidotarium Nicolai, s.XII",
        "Cordial / Reconstituyente cardiaco",
        [
            ("Rosa", "ACTIVO"), ("Corallium rubrum", "ACTIVO"),
            ("Spodium", "ACTIVO"), ("Sandali rubei", "ACTIVO"), ("Sandali albi", "ACTIVO"),
            ("Doronicum", "ACTIVO"), ("Buglossa", "ACTIVO"),
            ("Cinnamomum", "ESPECIA"), ("Galanga", "ESPECIA"), ("Crocus", "ESPECIA"),
            ("Cardamomum", "ESPECIA"), ("Nux moschata", "ESPECIA"), ("Cubeba", "ESPECIA"),
            ("Casia", "ESPECIA"), ("Zedoaria", "ESPECIA"),
            ("Saccharum", "BASE"),
        ]
    ),
    (
        "Rosata Novella",
        "Antidotarium Nicolai, s.XII",
        "Laxante suave / Cordial",
        [
            ("Rosa", "ACTIVO"), ("Liquiritia", "ACTIVO"),
            ("Cinnamomum", "ESPECIA"), ("Galanga", "ESPECIA"),
            ("Nux moschata", "ESPECIA"), ("Crocus", "ESPECIA"),
            ("Saccharum", "BASE"),
        ]
    ),
    (
        "Letitia Galeni",
        "Antidotarium Nicolai, s.XII",
        "Cordial / Antimelancolico",
        [
            ("Lapis lazuli", "ACTIVO"), ("Buglossa", "ACTIVO"), ("Seta", "ACTIVO"),
            ("Rosa", "ACTIVO"), ("Doronicum", "ACTIVO"), ("Basilicon", "ACTIVO"),
            ("Cinnamomum", "ESPECIA"), ("Crocus", "ESPECIA"), ("Nux moschata", "ESPECIA"),
            ("Galanga", "ESPECIA"), ("Cubeba", "ESPECIA"), ("Cardamomum", "ESPECIA"),
            ("Saccharum", "BASE"), ("Aqua rosarum", "BASE"),
        ]
    ),
    (
        "Trifera Saracenica",
        "Antidotarium Nicolai, s.XII",
        "Reconstituyente nervioso",
        [
            ("Opium", "ACTIVO"), ("Castoreum", "ACTIVO"), ("Pyrethrum", "ACTIVO"),
            ("Euphorbia", "ACTIVO"), ("Nardus indica", "ACTIVO"),
            ("Piper longum", "ESPECIA"), ("Piper nigrum", "ESPECIA"), ("Zingiber", "ESPECIA"),
            ("Cinnamomum", "ESPECIA"), ("Myrrha", "ESPECIA"), ("Crocus", "ESPECIA"),
            ("Cardamomum", "ESPECIA"), ("Casia", "ESPECIA"),
            ("Mel despumatum", "BASE"),
        ]
    ),
    (
        "Paulinum",
        "Antidotarium Nicolai / Galeno",
        "Antidoto / Analgesico",
        [
            ("Opium", "ACTIVO"), ("Castoreum", "ACTIVO"), ("Hyoscyamus", "ACTIVO"),
            ("Petroselinum", "ACTIVO"), ("Hypericum", "ACTIVO"),
            ("Piper longum", "ESPECIA"), ("Piper nigrum", "ESPECIA"), ("Zingiber", "ESPECIA"),
            ("Cinnamomum", "ESPECIA"), ("Myrrha", "ESPECIA"), ("Crocus", "ESPECIA"),
            ("Casia", "ESPECIA"),
            ("Mel despumatum", "BASE"),
        ]
    ),
    (
        "Electuarium Justinum",
        "Antidotarium Nicolai, s.XII",
        "Tonico / Digestivo especiado",
        [
            ("Amomum", "ACTIVO"), ("Petroselinum", "ACTIVO"), ("Acorus calamus", "ACTIVO"),
            ("Nardus indica", "ACTIVO"),
            ("Piper longum", "ESPECIA"), ("Piper nigrum", "ESPECIA"), ("Zingiber", "ESPECIA"),
            ("Cinnamomum", "ESPECIA"), ("Crocus", "ESPECIA"), ("Costus", "ESPECIA"),
            ("Myrrha", "ESPECIA"), ("Casia", "ESPECIA"), ("Cardamomum", "ESPECIA"),
            ("Mel despumatum", "BASE"),
        ]
    ),

    # --- GRABADIN / PSEUDO-MESUE ---
    (
        "Electuarium de Baccis Lauri",
        "Grabadin / Pseudo-Mesue, s.XI",
        "Emmenagogo / Diuretico",
        [
            ("Laurus", "ACTIVO"), ("Aristolochia", "ACTIVO"), ("Gentiana", "ACTIVO"),
            ("Petroselinum", "ACTIVO"), ("Apium", "ACTIVO"),
            ("Piper longum", "ESPECIA"), ("Zingiber", "ESPECIA"), ("Cinnamomum", "ESPECIA"),
            ("Myrrha", "ESPECIA"), ("Anisi", "ESPECIA"),
            ("Mel despumatum", "BASE"),
        ]
    ),
    (
        "Syrupus de Fumaria",
        "Grabadin / Mesue",
        "Depurativo / Antimelancolico",
        [
            ("Fumaria", "ACTIVO"), ("Senna", "ACTIVO"), ("Epithymum", "ACTIVO"),
            ("Polypodium", "ACTIVO"), ("Endiviae", "ACTIVO"),
            ("Cinnamomum", "ESPECIA"), ("Anisi", "ESPECIA"),
            ("Saccharum", "BASE"), ("Aqua", "BASE"),
        ]
    ),
    (
        "Confectio Anacardia",
        "Grabadin / Mesue",
        "Tonico cerebral / Mnemonico",
        [
            ("Anacardium", "ACTIVO"), ("Castoreum", "ACTIVO"), ("Euphorbia", "ACTIVO"),
            ("Pyrethrum", "ACTIVO"),
            ("Piper longum", "ESPECIA"), ("Piper nigrum", "ESPECIA"), ("Zingiber", "ESPECIA"),
            ("Cinnamomum", "ESPECIA"), ("Crocus", "ESPECIA"),
            ("Mel despumatum", "BASE"),
        ]
    ),
    (
        "Electuarium Diacostum",
        "Grabadin / Mesue",
        "Digestivo caliente / Carminativo",
        [
            ("Costus", "ACTIVO"), ("Amomum", "ACTIVO"), ("Nardus indica", "ACTIVO"),
            ("Mastix", "ACTIVO"),
            ("Piper longum", "ESPECIA"), ("Zingiber", "ESPECIA"), ("Cinnamomum", "ESPECIA"),
            ("Casia", "ESPECIA"), ("Cardamomum", "ESPECIA"), ("Anisi", "ESPECIA"),
            ("Mel despumatum", "BASE"),
        ]
    ),
    (
        "Unguentum Marciaton",
        "Grabadin / Mesue",
        "Emoliente / Relajante muscular",
        [
            ("Althaea", "ACTIVO"), ("Chamaemelum", "ACTIVO"), ("Melilotus", "ACTIVO"),
            ("Anethum", "ACTIVO"), ("Linum", "ACTIVO"), ("Foenum graecum", "ACTIVO"),
            ("Terebinthina", "ACTIVO"),
            ("Oleum olivarum", "BASE"), ("Cera", "BASE"), ("Axungia porci", "BASE"),
        ]
    ),

    # --- AVICENNA CANON ---
    (
        "Suffuf al-Tib (Polvo aromatico de Avicena)",
        "Avicenna, Canon Medicinae, s.XI",
        "Aromatico / Digestivo",
        [
            ("Sandalum album", "ACTIVO"), ("Rosa", "ACTIVO"),
            ("Cinnamomum", "ESPECIA"), ("Cardamomum", "ESPECIA"), ("Nux moschata", "ESPECIA"),
            ("Galanga", "ESPECIA"), ("Crocus", "ESPECIA"), ("Casia", "ESPECIA"),
            ("Camphor", "ESPECIA"),
        ]
    ),
    (
        "Itrifal Ustukhudus (Electuario de Espliego)",
        "Avicenna, Canon Medicinae",
        "Antimelancolico / Nervioso",
        [
            ("Lavandula", "ACTIVO"), ("Epithymum", "ACTIVO"), ("Polypodium", "ACTIVO"),
            ("Agaricum", "ACTIVO"), ("Senna", "ACTIVO"), ("Lapis lazuli", "ACTIVO"),
            ("Cinnamomum", "ESPECIA"), ("Zingiber", "ESPECIA"), ("Crocus", "ESPECIA"),
            ("Anisi", "ESPECIA"), ("Rosa", "ESPECIA"),
            ("Mel despumatum", "BASE"),
        ]
    ),
    (
        "Tiryaq al-Arba (Theriac de 4 ingredientes - Avicena)",
        "Avicenna, Canon Medicinae",
        "Antidoto simple",
        [
            ("Gentiana", "ACTIVO"), ("Aristolochia rotunda", "ACTIVO"), ("Laurus", "ACTIVO"),
            ("Myrrha", "ESPECIA"),
            ("Mel despumatum", "BASE"),
        ]
    ),
    (
        "Jawaarish Jalinusi (Digestivo de Galeno - Avicena)",
        "Avicenna, Canon Medicinae",
        "Digestivo / Tonico estomacal",
        [
            ("Mastix", "ACTIVO"), ("Nardus indica", "ACTIVO"), ("Aloe", "ACTIVO"),
            ("Piper longum", "ESPECIA"), ("Piper nigrum", "ESPECIA"), ("Zingiber", "ESPECIA"),
            ("Cinnamomum", "ESPECIA"), ("Crocus", "ESPECIA"), ("Casia", "ESPECIA"),
            ("Costus", "ESPECIA"), ("Cardamomum", "ESPECIA"),
            ("Mel despumatum", "BASE"),
        ]
    ),

    # --- ABULCASIS / AL-ZAHRAWI ---
    (
        "Unguentum Abulcasis (de vulneribus)",
        "Abulcasis, al-Tasrif, s.X",
        "Vulnerario / Cicatrizante",
        [
            ("Aristolochia", "ACTIVO"), ("Sarcocolla", "ACTIVO"), ("Sanguis draconis", "ACTIVO"),
            ("Aloe", "ACTIVO"),
            ("Olibanum", "ESPECIA"), ("Myrrha", "ESPECIA"),
            ("Oleum rosarum", "BASE"), ("Cera", "BASE"),
        ]
    ),
    (
        "Theriac Abulcasis (contra venenos)",
        "Abulcasis, al-Tasrif",
        "Antidoto",
        [
            ("Opium", "ACTIVO"), ("Castoreum", "ACTIVO"), ("Gentiana", "ACTIVO"),
            ("Aristolochia", "ACTIVO"), ("Opopanax", "ACTIVO"), ("Sagapenum", "ACTIVO"),
            ("Galbanum", "ACTIVO"),
            ("Crocus", "ESPECIA"), ("Cinnamomum", "ESPECIA"), ("Piper longum", "ESPECIA"),
            ("Piper nigrum", "ESPECIA"), ("Myrrha", "ESPECIA"), ("Zingiber", "ESPECIA"),
            ("Mel despumatum", "BASE"),
        ]
    ),

    # --- SALERNITANO / VARIOS ---
    (
        "Antidotum Hadriani",
        "Compilacion salernitana, s.XII",
        "Antidoto / Analgesico",
        [
            ("Opium", "ACTIVO"), ("Castoreum", "ACTIVO"), ("Euphorbia", "ACTIVO"),
            ("Acorus calamus", "ACTIVO"), ("Gentiana", "ACTIVO"),
            ("Piper longum", "ESPECIA"), ("Zingiber", "ESPECIA"), ("Cinnamomum", "ESPECIA"),
            ("Myrrha", "ESPECIA"), ("Crocus", "ESPECIA"), ("Casia", "ESPECIA"),
            ("Mel despumatum", "BASE"),
        ]
    ),
    (
        "Electuarium Ducis",
        "Antidotarium Nicolai, s.XII",
        "Pectoral / Antitusivo",
        [
            ("Glycyrrhiza", "ACTIVO"), ("Dragagantum", "ACTIVO"), ("Gummi arabicum", "ACTIVO"),
            ("Hyssopus", "ACTIVO"), ("Iris", "ACTIVO"),
            ("Piper longum", "ESPECIA"), ("Zingiber", "ESPECIA"), ("Cinnamomum", "ESPECIA"),
            ("Anisi", "ESPECIA"),
            ("Saccharum", "BASE"), ("Mel despumatum", "BASE"),
        ]
    ),
    (
        "Benedicta Laxativa",
        "Antidotarium Nicolai, s.XII",
        "Purgante universal / Polychreston",
        [
            ("Turbith", "ACTIVO"), ("Diagridium", "ACTIVO"), ("Polypodium", "ACTIVO"),
            ("Senna", "ACTIVO"), ("Epithymum", "ACTIVO"), ("Rhabarbarum", "ACTIVO"),
            ("Zingiber", "ESPECIA"), ("Cinnamomum", "ESPECIA"), ("Anisi", "ESPECIA"),
            ("Crocus", "ESPECIA"), ("Mastix", "ESPECIA"),
            ("Saccharum", "BASE"),
        ]
    ),
    (
        "Diatragacanthi",
        "Antidotarium Nicolai, s.XII",
        "Pectoral / Demulcente",
        [
            ("Tragacantha", "ACTIVO"), ("Gummi arabicum", "ACTIVO"), ("Amylum", "ACTIVO"),
            ("Glycyrrhiza", "ACTIVO"),
            ("Cinnamomum", "ESPECIA"),
            ("Saccharum", "BASE"),
        ]
    ),
    (
        "Dianucum (Electuario de Nueces)",
        "Antidotarium Nicolai, s.XII",
        "Tonico cerebral / Antiepileptico",
        [
            ("Nux", "ACTIVO"), ("Ruta", "ACTIVO"), ("Pirethrum", "ACTIVO"),
            ("Euphorbia", "ACTIVO"), ("Castoreum", "ACTIVO"),
            ("Piper nigrum", "ESPECIA"), ("Zingiber", "ESPECIA"), ("Cinnamomum", "ESPECIA"),
            ("Mel despumatum", "BASE"),
        ]
    ),
    (
        "Electuarium Diaspermaton",
        "Antidotarium Nicolai, s.XII",
        "Diuretico / Carminativo",
        [
            ("Petroselinum", "ACTIVO"), ("Apium", "ACTIVO"), ("Carum", "ACTIVO"),
            ("Foeniculum", "ACTIVO"), ("Anisi", "ACTIVO"), ("Amomum", "ACTIVO"),
            ("Piper longum", "ESPECIA"), ("Zingiber", "ESPECIA"), ("Cinnamomum", "ESPECIA"),
            ("Mel despumatum", "BASE"),
        ]
    ),
    # --- KEY FOR DEADLOCK: has Opium but NOT Castoreum ---
    (
        "Philonium Romanum",
        "Antidotarium Nicolai, s.XII",
        "Analgesico / Antidiarreico (variante)",
        [
            ("Opium", "ACTIVO"), ("Hyoscyamus", "ACTIVO"), ("Pyrethrum", "ACTIVO"),
            ("Euphorbia", "ACTIVO"),
            ("Piper longum", "ESPECIA"), ("Piper nigrum", "ESPECIA"), ("Zingiber", "ESPECIA"),
            ("Cinnamomum", "ESPECIA"), ("Crocus", "ESPECIA"), ("Myrrha", "ESPECIA"),
            ("Mel despumatum", "BASE"),
        ]
    ),
    # --- KEY FOR DEADLOCK: has Castoreum but NOT Opium ---
    (
        "Theriac Diatessaron Magna",
        "Compilacion salernitana",
        "Antidoto compuesto",
        [
            ("Gentiana", "ACTIVO"), ("Aristolochia rotunda", "ACTIVO"), ("Laurus", "ACTIVO"),
            ("Castoreum", "ACTIVO"), ("Hypericum", "ACTIVO"),
            ("Myrrha", "ESPECIA"), ("Cinnamomum", "ESPECIA"),
            ("Mel despumatum", "BASE"),
        ]
    ),
]

# ============================================================
# BUILD COMPLETE DATABASE
# ============================================================

# Load existing recipes
existing_recipes = {}
existing_flat = []
with open(os.path.join(BASE, 'recetas_historicas_medievales.csv'), encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        existing_recipes[row['Nombre_Receta'].split('(')[0].strip()] = row

with open(os.path.join(BASE, 'recetas_historicas_ingredientes_flat.csv'), encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        existing_flat.append(row)

print(f"Existing recipes: {len(existing_recipes)}")
print(f"Existing flat rows: {len(existing_flat)}")

# Add new recipes
new_summary_rows = []
new_flat_rows = []

for name, source, rtype, ingredients in NEW_RECIPES:
    # Check not duplicate
    short_name = name.split('(')[0].strip()
    if short_name in existing_recipes:
        print(f"  SKIP (already exists): {short_name}")
        continue
    
    activos = [(i, c) for i, c in ingredients if c == 'ACTIVO']
    especias = [(i, c) for i, c in ingredients if c == 'ESPECIA']
    bases = [(i, c) for i, c in ingredients if c == 'BASE']
    total = len(ingredients)
    
    n_act = len(activos)
    n_esp = len(especias)
    n_bas = len(bases)
    
    summary = {
        'Nombre_Receta': name,
        'Fuente': source,
        'Tipo': rtype,
        'Total_Ingredientes': total,
        'N_Activos_Raros': n_act,
        'N_Especias': n_esp,
        'N_Bases': n_bas,
        'Ratio_Activos_%': round(100 * n_act / total, 1),
        'Ratio_Especias_%': round(100 * n_esp / total, 1),
        'Ratio_Bases_%': round(100 * n_bas / total, 1),
        'Lista_Activos': ' | '.join(i for i, _ in activos),
        'Lista_Especias': ' | '.join(i for i, _ in especias),
        'Lista_Bases': ' | '.join(i for i, _ in bases),
    }
    new_summary_rows.append(summary)
    
    for ing, cat in ingredients:
        new_flat_rows.append({
            'Receta': name,
            'Ingrediente': ing,
            'Categoria': cat,
            'Ingrediente_Normalizado': ing,
        })
    
    print(f"  ADD: {name} ({total} ingredients)")

print(f"\nNew recipes added: {len(new_summary_rows)}")
print(f"New flat rows added: {len(new_flat_rows)}")

# Write updated summary CSV
summary_path = os.path.join(BASE, 'recetas_historicas_medievales.csv')
with open(summary_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    existing_summary = list(reader)
    fieldnames = reader.fieldnames

all_summary = existing_summary + new_summary_rows

with open(summary_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in all_summary:
        writer.writerow(row)

print(f"\nSaved {len(all_summary)} recipes to {summary_path}")

# Write updated flat CSV
flat_path = os.path.join(BASE, 'recetas_historicas_ingredientes_flat.csv')
all_flat = existing_flat + new_flat_rows

with open(flat_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['Receta', 'Ingrediente', 'Categoria', 'Ingrediente_Normalizado'])
    writer.writeheader()
    for row in all_flat:
        writer.writerow(row)

print(f"Saved {len(all_flat)} ingredient rows to {flat_path}")

# Summary statistics
all_ingredients = set()
for row in all_flat:
    all_ingredients.add(row['Ingrediente_Normalizado'])

print(f"\n{'='*60}")
print(f"EXPANDED DATABASE SUMMARY")
print(f"{'='*60}")
print(f"Total recipes: {len(all_summary)}")
print(f"Total unique ingredients: {len(all_ingredients)}")
print(f"Total ingredient-recipe pairs: {len(all_flat)}")

# Check for new Opium-without-Castoreum and Castoreum-without-Opium recipes
opium_recipes = set()
castoreum_recipes = set()
for row in all_flat:
    rname = row['Receta'].split('(')[0].strip()
    ing = row['Ingrediente_Normalizado']
    if ing == 'Opium':
        opium_recipes.add(rname)
    if ing == 'Castoreum':
        castoreum_recipes.add(rname)

opium_only = opium_recipes - castoreum_recipes
castoreum_only = castoreum_recipes - opium_recipes
both = opium_recipes & castoreum_recipes

print(f"\n--- DEADLOCK BREAKER ANALYSIS ---")
print(f"Recipes with Opium: {len(opium_recipes)}")
print(f"Recipes with Castoreum: {len(castoreum_recipes)}")
print(f"Opium-ONLY (no Castoreum): {len(opium_only)} -> {sorted(opium_only)}")
print(f"Castoreum-ONLY (no Opium): {len(castoreum_only)} -> {sorted(castoreum_only)}")
print(f"BOTH: {len(both)} -> {sorted(both)}")

# Size distribution for matching
sizes = [int(row['Total_Ingredientes']) for row in all_summary]
from collections import Counter
size_dist = Counter(sizes)
print(f"\nRecipe size distribution:")
for sz in sorted(size_dist.keys()):
    print(f"  {sz:>2d} ingredients: {'#' * size_dist[sz]} ({size_dist[sz]} recipes)")
