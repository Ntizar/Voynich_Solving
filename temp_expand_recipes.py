import csv
import sys
sys.stdout.reconfigure(encoding='utf-8')

# =============================================================================
# EXPANDED HISTORICAL RECIPE DATABASE
# 23 recipes total (8 original + 15 new)
# Sources: Antidotarium Nicolai (s.XII), Circa Instans, Grabadin,
#          Liber de Simplici Medicina, Canon de Avicena
# =============================================================================

recipes = [
    # ===== ORIGINAL 8 RECIPES =====
    {
        "nombre": "Theriac Magna (Triaca de Andromachus)",
        "fuente": "Galeno / Andromachus, s.I-II d.C.",
        "tipo": "Antidoto Universal / Panacea",
        "total_ingredientes": 64,
        "activos_raros": [
            "Opium", "Trochisci de vipera", "Squilla", "Hedychium",
            "Castoreum", "Nardus celtica", "Petroselinum", "Phu/Valeriana",
            "Amomum", "Acorus calamus", "Hypericum", "Gentiana",
            "Aristolochia", "Opopanax", "Sagapenum", "Galbanum",
            "Balsamum", "Styrax", "Terebinthina", "Bitumen judaicum"
        ],
        "especias_aromaticas": [
            "Crocus", "Zingiber", "Cinnamomum", "Piper longum",
            "Piper nigrum", "Myrrha", "Olibanum", "Casia",
            "Costus", "Anisi", "Foeniculum", "Daucus creticus"
        ],
        "bases_excipientes": ["Mel despumatum", "Vinum"]
    },
    {
        "nombre": "Mithridatium",
        "fuente": "Mitridates VI, copiado por Galeno",
        "tipo": "Antidoto contra venenos",
        "total_ingredientes": 54,
        "activos_raros": [
            "Opium", "Castoreum", "Nardus indica", "Nardus celtica",
            "Gentiana", "Aristolochia longa", "Aristolochia rotunda",
            "Hypericum", "Sagapenum", "Opopanax", "Acacia",
            "Gummi arabicum", "Hypocistis", "Stachys",
            "Thlaspi", "Daucus creticus"
        ],
        "especias_aromaticas": [
            "Crocus", "Zingiber", "Cinnamomum", "Piper longum",
            "Piper nigrum", "Myrrha", "Costus", "Casia",
            "Anisi", "Petroselinum", "Foeniculum", "Cardamomum"
        ],
        "bases_excipientes": ["Mel despumatum", "Vinum"]
    },
    {
        "nombre": "Diascordium",
        "fuente": "Fracastoro, s.XVI, basado en textos anteriores",
        "tipo": "Antidoto / Antipestilencial",
        "total_ingredientes": 14,
        "activos_raros": [
            "Scordium", "Opium", "Castoreum",
            "Galbanum", "Styrax", "Bistorta"
        ],
        "especias_aromaticas": [
            "Cinnamomum", "Piper longum", "Zingiber",
            "Rosa", "Gentiana", "Dictamnus"
        ],
        "bases_excipientes": ["Mel despumatum"]
    },
    {
        "nombre": "Pillulae Cochiae",
        "fuente": "Antidotarium Nicolai, s.XII",
        "tipo": "Purgante fuerte",
        "total_ingredientes": 5,
        "activos_raros": ["Colocynthis", "Aloe", "Scammonium"],
        "especias_aromaticas": ["Staphisagria", "Bdellium"],
        "bases_excipientes": ["Succo absinthii"]
    },
    {
        "nombre": "Pillulae Aureae",
        "fuente": "Antidotarium Nicolai, s.XII",
        "tipo": "Purgante suave / Tonico",
        "total_ingredientes": 7,
        "activos_raros": ["Aloe", "Diagridium", "Mastix", "Rosa"],
        "especias_aromaticas": ["Crocus", "Cinnamomum"],
        "bases_excipientes": ["Succo absinthii"]
    },
    {
        "nombre": "Unguentum Apostolorum",
        "fuente": "Antidotarium Nicolai / Grabadin",
        "tipo": "Ungueento cicatrizante",
        "total_ingredientes": 12,
        "activos_raros": [
            "Aristolochia longa", "Aristolochia rotunda", "Opopanax",
            "Galbanum", "Bdellium", "Verdigris", "Litharge"
        ],
        "especias_aromaticas": ["Olibanum", "Myrrha"],
        "bases_excipientes": ["Cera", "Oleum olivarum", "Resina pini"]
    },
    {
        "nombre": "Electuarium de Succo Rosarum",
        "fuente": "Circa Instans / Salerno, s.XII",
        "tipo": "Laxante suave / Tonico digestivo",
        "total_ingredientes": 8,
        "activos_raros": ["Rosa gallica", "Senna", "Tamarindus", "Viola"],
        "especias_aromaticas": ["Cinnamomum", "Zingiber", "Anisi"],
        "bases_excipientes": ["Saccharum"]
    },
    {
        "nombre": "Aurea Alexandrina",
        "fuente": "Antidotarium Nicolai, s.XII",
        "tipo": "Reconstituyente / Tonico general",
        "total_ingredientes": 22,
        "activos_raros": [
            "Opium", "Castoreum", "Stachys", "Hypericum",
            "Petroselinum", "Acorus calamus", "Phu/Valeriana", "Squilla"
        ],
        "especias_aromaticas": [
            "Crocus", "Piper longum", "Piper nigrum", "Zingiber",
            "Cinnamomum", "Myrrha", "Costus", "Nardus",
            "Anisi", "Foeniculum", "Casia"
        ],
        "bases_excipientes": ["Mel despumatum", "Vinum", "Saccharum"]
    },

    # ===== 15 NEW RECIPES =====

    # --- ANTIDOTARIUM NICOLAI: Confectiones (electuarios compuestos) ---
    {
        "nombre": "Confectio Hamech",
        "fuente": "Antidotarium Nicolai, s.XII",
        "tipo": "Purgante melancolico / Antimelancolico",
        "total_ingredientes": 15,
        "activos_raros": [
            "Polypodium", "Epithymum", "Fumaria", "Lapis lazuli",
            "Myrobalanus indus", "Myrobalanus citrinus", "Myrobalanus kebulus",
            "Senna", "Rhabarbarum"
        ],
        "especias_aromaticas": [
            "Zingiber", "Anisi", "Rosa", "Cinnamomum"
        ],
        "bases_excipientes": ["Saccharum", "Mel despumatum"]
    },
    {
        "nombre": "Hiera Picra (Hiera de Galeno)",
        "fuente": "Galeno, copiado en Antidotarium Nicolai",
        "tipo": "Purgante / Colagogo",
        "total_ingredientes": 10,
        "activos_raros": [
            "Aloe", "Xylobalsamum", "Asarum", "Nardus indica",
            "Crocus", "Mastix", "Spica nardi"
        ],
        "especias_aromaticas": [
            "Cinnamomum", "Casia"
        ],
        "bases_excipientes": ["Mel despumatum"]
    },
    {
        "nombre": "Trifera Magna",
        "fuente": "Antidotarium Nicolai, s.XII",
        "tipo": "Reconstituyente nervioso / Afrodisiaco",
        "total_ingredientes": 28,
        "activos_raros": [
            "Opium", "Castoreum", "Euphorbia", "Pyrethrum",
            "Staphisagria", "Sagapenum", "Opopanax", "Bdellium",
            "Nardus indica", "Hypericum", "Amomum",
            "Petroselinum", "Squilla"
        ],
        "especias_aromaticas": [
            "Crocus", "Piper longum", "Piper nigrum", "Piper album",
            "Zingiber", "Cinnamomum", "Casia", "Costus",
            "Myrrha", "Galanga", "Cardamomum", "Cubeba",
            "Nux moschata"
        ],
        "bases_excipientes": ["Mel despumatum", "Vinum"]
    },
    {
        "nombre": "Diamargariton (Electuario de Perlas)",
        "fuente": "Antidotarium Nicolai, s.XII",
        "tipo": "Cordial / Reconstituyente cardiaco",
        "total_ingredientes": 16,
        "activos_raros": [
            "Margarita (Perla)", "Corallium rubrum", "Corallium album",
            "Lapis lazuli", "Os de corde cervi", "Cornu cervi",
            "Doronicum", "Zedoaria"
        ],
        "especias_aromaticas": [
            "Cinnamomum", "Galanga", "Nux moschata", "Cubeba",
            "Cardamomum", "Crocus", "Casia"
        ],
        "bases_excipientes": ["Saccharum"]
    },
    {
        "nombre": "Diaciminum (Electuario de Comino)",
        "fuente": "Antidotarium Nicolai, s.XII",
        "tipo": "Digestivo / Carminativo",
        "total_ingredientes": 11,
        "activos_raros": [
            "Cuminum", "Apium", "Carum (Alcaravea)",
            "Amomum", "Daucus creticus"
        ],
        "especias_aromaticas": [
            "Piper longum", "Piper nigrum", "Zingiber",
            "Anisi", "Cinnamomum"
        ],
        "bases_excipientes": ["Mel despumatum"]
    },
    {
        "nombre": "Unguentum Basilicon",
        "fuente": "Grabadin / Mesue, s.XI",
        "tipo": "Ungueento supurativo / Madurativo",
        "total_ingredientes": 7,
        "activos_raros": [
            "Resina pini", "Pix (Pez)", "Galbanum"
        ],
        "especias_aromaticas": [
            "Olibanum"
        ],
        "bases_excipientes": ["Cera", "Oleum olivarum", "Sebum"]
    },
    {
        "nombre": "Unguentum Populeon",
        "fuente": "Nicolaus Praepositus / Salerno",
        "tipo": "Analgesico / Sedante topico",
        "total_ingredientes": 12,
        "activos_raros": [
            "Populus (Yemas de alamo)", "Mandragora", "Hyoscyamus",
            "Papaver nigrum", "Lactuca", "Sempervivum",
            "Solanum", "Umbilicus veneris"
        ],
        "especias_aromaticas": [
            "Viola"
        ],
        "bases_excipientes": ["Axungia porci (Grasa de cerdo)", "Oleum olivarum", "Cera"]
    },
    {
        "nombre": "Pillulae de Hiera cum Agarico",
        "fuente": "Antidotarium Nicolai, s.XII",
        "tipo": "Purgante flematico",
        "total_ingredientes": 9,
        "activos_raros": [
            "Aloe", "Agaricum", "Coloquintida",
            "Mastix", "Euphorbia"
        ],
        "especias_aromaticas": [
            "Crocus", "Cinnamomum", "Rosa"
        ],
        "bases_excipientes": ["Succo absinthii"]
    },
    {
        "nombre": "Pillulae Fetidae (Pildoras Fetidas)",
        "fuente": "Antidotarium Nicolai, s.XII",
        "tipo": "Emmenagogo / Antihist'erico",
        "total_ingredientes": 8,
        "activos_raros": [
            "Opopanax", "Galbanum", "Sagapenum",
            "Castoreum", "Asa foetida"
        ],
        "especias_aromaticas": [
            "Myrrha", "Bdellium"
        ],
        "bases_excipientes": ["Succo rutae"]
    },
    {
        "nombre": "Requies Magna (Requies Nicolai)",
        "fuente": "Antidotarium Nicolai, s.XII",
        "tipo": "Somnifero / Analgesico potente",
        "total_ingredientes": 17,
        "activos_raros": [
            "Opium", "Mandragora", "Hyoscyamus", "Papaver album",
            "Lactuca", "Psyllium", "Gummi arabicum", "Amylum",
            "Tragacantha", "Glycyrrhiza"
        ],
        "especias_aromaticas": [
            "Rosa", "Cinnamomum", "Nux moschata",
            "Crocus", "Camphor"
        ],
        "bases_excipientes": ["Saccharum", "Aqua rosarum"]
    },
    {
        "nombre": "Diacodion (Jarabe de Adormidera)",
        "fuente": "Antidotarium Nicolai / Mesue",
        "tipo": "Antitusivo / Somnifero suave",
        "total_ingredientes": 6,
        "activos_raros": [
            "Papaver album (capita)", "Glycyrrhiza",
            "Gummi arabicum"
        ],
        "especias_aromaticas": [
            "Cinnamomum"
        ],
        "bases_excipientes": ["Saccharum", "Aqua"]
    },
    {
        "nombre": "Dialtea (Ungueento de Altea)",
        "fuente": "Grabadin / Salerno",
        "tipo": "Emoliente / Antiinflamatorio topico",
        "total_ingredientes": 10,
        "activos_raros": [
            "Althaea (Malvavisco)", "Linum (Linaza)",
            "Foenum graecum (Alholva)", "Terebinthina",
            "Cera", "Colophonia"
        ],
        "especias_aromaticas": [
            "Olibanum"
        ],
        "bases_excipientes": ["Oleum olivarum", "Axungia porci", "Aqua"]
    },
    {
        "nombre": "Philonium Persicum",
        "fuente": "Antidotarium Nicolai, s.XII",
        "tipo": "Analgesico / Antidiarreico",
        "total_ingredientes": 18,
        "activos_raros": [
            "Opium", "Castoreum", "Pyrethrum", "Euphorbium",
            "Hyoscyamus", "Nardus indica", "Hypocistis",
            "Gummi arabicum", "Styrax"
        ],
        "especias_aromaticas": [
            "Crocus", "Piper longum", "Piper nigrum",
            "Zingiber", "Cinnamomum", "Myrrha",
            "Casia", "Cardamomum"
        ],
        "bases_excipientes": ["Mel despumatum"]
    },
    {
        "nombre": "Oximel Compositum",
        "fuente": "Antidotarium Nicolai / Mesue",
        "tipo": "Expectorante / Digestivo",
        "total_ingredientes": 10,
        "activos_raros": [
            "Squilla", "Petroselinum", "Apium",
            "Foeniculum (radix)", "Carum"
        ],
        "especias_aromaticas": [
            "Zingiber", "Piper longum", "Anisi"
        ],
        "bases_excipientes": ["Mel despumatum", "Acetum"]
    },
    {
        "nombre": "Theriac Diatessaron",
        "fuente": "Antidotarium Nicolai / Galeno",
        "tipo": "Antidoto simple (4 ingredientes)",
        "total_ingredientes": 5,
        "activos_raros": [
            "Gentiana", "Aristolochia rotunda", "Laurus (Laurel)"
        ],
        "especias_aromaticas": [
            "Myrrha"
        ],
        "bases_excipientes": ["Mel despumatum"]
    },
]

# =============================================================================
# GENERATE EXPANDED CSV
# =============================================================================

csv_path = 'recetas_historicas_medievales.csv'

with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([
        'Nombre_Receta', 'Fuente', 'Tipo', 'Total_Ingredientes',
        'N_Activos_Raros', 'N_Especias', 'N_Bases',
        'Ratio_Activos_%', 'Ratio_Especias_%', 'Ratio_Bases_%',
        'Lista_Activos', 'Lista_Especias', 'Lista_Bases'
    ])
    for r in recipes:
        n_a = len(r['activos_raros'])
        n_e = len(r['especias_aromaticas'])
        n_b = len(r['bases_excipientes'])
        total = r['total_ingredientes']
        writer.writerow([
            r['nombre'], r['fuente'], r['tipo'], total,
            n_a, n_e, n_b,
            round((n_a/total)*100, 1),
            round((n_e/total)*100, 1),
            round((n_b/total)*100, 1),
            ' | '.join(r['activos_raros']),
            ' | '.join(r['especias_aromaticas']),
            ' | '.join(r['bases_excipientes'])
        ])

print("=" * 80)
print("BASE DE DATOS HISTORICA EXPANDIDA")
print("=" * 80)
print(f"Total recetas: {len(recipes)} (8 originales + {len(recipes)-8} nuevas)")
print()

# Summary table
print(f"{'Receta':<40} | {'Total':>5} | {'Act%':>5} | {'Esp%':>5} | {'Base%':>5} | {'Fuente'}")
print("-" * 105)
for r in recipes:
    n_a = len(r['activos_raros'])
    n_e = len(r['especias_aromaticas'])
    n_b = len(r['bases_excipientes'])
    total = r['total_ingredientes']
    print(f"{r['nombre']:<40} | {total:>5} | {(n_a/total)*100:>4.1f}% | {(n_e/total)*100:>4.1f}% | {(n_b/total)*100:>4.1f}% | {r['fuente'][:30]}")

# =============================================================================
# INGREDIENT COUNT DISTRIBUTION (for Voynich matching)
# =============================================================================
print("\n\nDISTRIBUCION DE TAMANOS (para matching con folios Voynich):")
from collections import Counter
sizes = Counter(r['total_ingredientes'] for r in recipes)
for size in sorted(sizes.keys()):
    names = [r['nombre'] for r in recipes if r['total_ingredientes'] == size]
    print(f"  {size:>3} ingredientes: {len(names)} recetas -> {', '.join(names)}")

# =============================================================================
# INGREDIENT FREQUENCY ACROSS ALL RECIPES (critical for constraint propagation)
# =============================================================================
print("\n\nFRECUENCIA DE INGREDIENTES ACTIVOS EN TODAS LAS RECETAS:")
print("(Ingredientes que aparecen en mas recetas = mas restricciones = mejor)")
print()

activo_freq = {}
especia_freq = {}
base_freq = {}

for r in recipes:
    for ing in r['activos_raros']:
        # Normalize ingredient names
        key = ing.split('(')[0].strip().split('/')[0].strip()
        activo_freq[key] = activo_freq.get(key, 0) + 1
    for ing in r['especias_aromaticas']:
        key = ing.split('(')[0].strip().split('/')[0].strip()
        especia_freq[key] = especia_freq.get(key, 0) + 1
    for ing in r['bases_excipientes']:
        key = ing.split('(')[0].strip().split('/')[0].strip()
        base_freq[key] = base_freq.get(key, 0) + 1

print("TOP ACTIVOS (aparecen en N recetas):")
for ing, count in sorted(activo_freq.items(), key=lambda x: -x[1])[:20]:
    recipe_names = [r['nombre'][:25] for r in recipes if any(ing in a for a in r['activos_raros'])]
    print(f"  {ing:<30} {count:>2}x -> {', '.join(recipe_names)}")

print("\nTOP ESPECIAS (aparecen en N recetas):")
for ing, count in sorted(especia_freq.items(), key=lambda x: -x[1])[:15]:
    recipe_names = [r['nombre'][:25] for r in recipes if any(ing in a for a in r['especias_aromaticas'])]
    print(f"  {ing:<30} {count:>2}x -> {', '.join(recipe_names)}")

print("\nTOP BASES (aparecen en N recetas):")
for ing, count in sorted(base_freq.items(), key=lambda x: -x[1])[:10]:
    recipe_names = [r['nombre'][:25] for r in recipes if any(ing in a for a in r['bases_excipientes'])]
    print(f"  {ing:<30} {count:>2}x -> {', '.join(recipe_names)}")

# =============================================================================
# KEY INGREDIENT CO-OCCURRENCE SIGNATURES
# Which PAIRS of ingredients always appear together?
# =============================================================================
print("\n\nPARES DE INGREDIENTES FRECUENTES (co-ocurrencia en mismas recetas):")
print("(Util para confirmar identificaciones por co-ocurrencia en Voynich)")
print()

# Build ingredient -> set of recipe names
all_ingredients = {}
for r in recipes:
    name = r['nombre']
    for ing in r['activos_raros'] + r['especias_aromaticas']:
        key = ing.split('(')[0].strip().split('/')[0].strip()
        if key not in all_ingredients:
            all_ingredients[key] = set()
        all_ingredients[key].add(name)

# Find pairs with high overlap
top_pairs = []
ing_list = [k for k, v in all_ingredients.items() if len(v) >= 3]  # only frequent ones
for i in range(len(ing_list)):
    for j in range(i+1, len(ing_list)):
        overlap = all_ingredients[ing_list[i]] & all_ingredients[ing_list[j]]
        if len(overlap) >= 4:
            top_pairs.append((ing_list[i], ing_list[j], len(overlap), overlap))

top_pairs.sort(key=lambda x: -x[2])
for a, b, n, recs in top_pairs[:20]:
    print(f"  {a:<25} + {b:<25} -> {n} recetas juntos")

# =============================================================================
# GENERATE EXPANDED CONSTRAINT SOLVER DATA
# =============================================================================
print("\n\nGENERANDO DATOS PARA CONSTRAINT SOLVER EXPANDIDO...")
csv_path2 = 'recetas_historicas_ingredientes_flat.csv'

with open(csv_path2, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Receta', 'Ingrediente', 'Categoria', 'Ingrediente_Normalizado'])
    for r in recipes:
        name = r['nombre']
        for ing in r['activos_raros']:
            key = ing.split('(')[0].strip().split('/')[0].strip()
            writer.writerow([name, ing, 'ACTIVO', key])
        for ing in r['especias_aromaticas']:
            key = ing.split('(')[0].strip().split('/')[0].strip()
            writer.writerow([name, ing, 'ESPECIA', key])
        for ing in r['bases_excipientes']:
            key = ing.split('(')[0].strip().split('/')[0].strip()
            writer.writerow([name, ing, 'BASE', key])

print(f"Archivo flat de ingredientes: {csv_path2}")
print(f"\nTotal unique ingredients across all {len(recipes)} recipes:")
all_unique = set()
for r in recipes:
    for ing in r['activos_raros'] + r['especias_aromaticas'] + r['bases_excipientes']:
        all_unique.add(ing.split('(')[0].strip().split('/')[0].strip())
print(f"  ACTIVOS unicos: {len(set(k.split('(')[0].strip().split('/')[0].strip() for r in recipes for k in r['activos_raros']))}")
print(f"  ESPECIAS unicas: {len(set(k.split('(')[0].strip().split('/')[0].strip() for r in recipes for k in r['especias_aromaticas']))}")
print(f"  BASES unicas: {len(set(k.split('(')[0].strip().split('/')[0].strip() for r in recipes for k in r['bases_excipientes']))}")
print(f"  TOTAL unicos: {len(all_unique)}")

print("\n\nDONE. Base expandida lista para constraint solver.")
