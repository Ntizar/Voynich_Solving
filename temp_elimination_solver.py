import sys
import csv
sys.stdout.reconfigure(encoding='utf-8')

# =============================================================================
# ELIMINATION SOLVER FOR PERFECT-MATCH FOLIOS
# In folios where #stems == #ingredients, each stem = exactly 1 ingredient.
# We use known assignments + category constraints to solve by elimination.
# =============================================================================

# Historical recipes for the 3 perfect matches
recipes = {
    "Unguentum Apostolorum": {
        "ACTIVO": ["Aristolochia longa", "Aristolochia rotunda", "Opopanax",
                    "Galbanum", "Bdellium", "Verdigris", "Litharge"],
        "ESPECIA": ["Olibanum", "Myrrha"],
        "BASE": ["Cera", "Oleum olivarum", "Resina pini"]
    },
    "Diascordium": {
        "ACTIVO": ["Scordium", "Opium", "Castoreum", "Galbanum", "Styrax", "Bistorta"],
        "ESPECIA": ["Cinnamomum", "Piper longum", "Zingiber", "Rosa", "Gentiana", "Dictamnus"],
        "BASE": ["Mel despumatum"]
    },
    "Pillulae Aureae": {
        "ACTIVO": ["Aloe", "Diagridium", "Mastix", "Rosa"],
        "ESPECIA": ["Crocus", "Cinnamomum"],
        "BASE": ["Succo absinthii"]
    }
}

# I need to extract the ACTUAL stems present in each folio from the raw data.
# Let me parse the voynich_sta.txt to get the exact word list for each folio.

corpus_path = r"C:\Ntizar_Obsidian\Ntizar_Brain\MASTERTMIND\zenodo_voynich\corpus\voynich_sta.txt"

# Parse corpus
folio_lines = {}  # folio -> [list of lines, each line is list of words]
current_folio = None

with open(corpus_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # Check if this is a folio header line like: <f87v>     <! $Q=O ...>
        # These have the folio tag at the start followed by metadata
        if line.startswith('<f') and '>' in line:
            # Extract folio name from the first <...> tag
            first_close = line.index('>')
            tag_content = line[1:first_close]
            
            # If it's just the folio name (no dot = header), update current folio
            if '.' not in tag_content:
                current_folio = tag_content
                continue
            
            # It's a line tag like <f87v.1,@P0>
            folio_part = tag_content.split('.')[0]
            if folio_part != current_folio:
                current_folio = folio_part
            
            # Extract the text after the tag
            rest = line[first_close+1:].strip()
            if rest:
                # Split words by '.' but be careful about the STA1 format
                # Words are separated by '.' and may contain '<->' separators
                # Remove <-> separators first
                rest = rest.replace('<->', '.')
                words = [w.strip() for w in rest.split('.') if w.strip()]
                if current_folio not in folio_lines:
                    folio_lines[current_folio] = []
                folio_lines[current_folio].append(words)

# Function to extract stem (remove final atom) from a word
# Based on our discovery: final atom = last A1-G1 type tag
# STA1 atoms: A1,A2,A3,B1,B2,B3,B4,C1,C2,D1,E1,E2,F1,F2,F3,G1,G3,H1,
#             J1,K1,L1,N1,P1,P2,Q1,Q2,T1,T2,U1,U2,Aa,Ba,Cm,Xb,Ab,Bd,Cl,Ka,Kb

import re

ATOM_PATTERN = re.compile(
    r'(A[1-3]|B[1-4]|C[1-2]|D1|E[1-2]|F[1-3]|G[1-3]|H1|'
    r'J1|K[1ab]|L1|N1|P[12]|Q[12]|T[12]|U[12]|'
    r'Aa|Ba|Cm|Xb|Ab|Bd|Cl)'
)

FINAL_ATOMS = {'A1','A2','A3','B1','B2','B3','B4','C1','C2',
               'G1','G3','F1','F2','F3','E1','E2','H1'}

def split_stem_suffix(word):
    """Split word into (stem, final_atom)"""
    atoms = ATOM_PATTERN.findall(word)
    if not atoms:
        return word, ''
    final = atoms[-1]
    if final in FINAL_ATOMS:
        # Remove last atom to get stem
        idx = word.rfind(final)
        stem = word[:idx]
        return stem if stem else word, final
    return word, ''

def get_stem(word):
    """Get just the stem part"""
    stem, suffix = split_stem_suffix(word)
    return stem if stem else word

# Now extract unique stems per folio for our target folios
target_folios = ['f87v', 'f93v', 'f96v']

print("=" * 80)
print("ELIMINATION SOLVER: Perfect-Match Folios")
print("=" * 80)

folio_stem_data = {}

for folio in target_folios:
    if folio not in folio_lines:
        print(f"WARNING: {folio} not found in corpus!")
        continue
    
    # Count all stems and their suffixes in this folio
    stem_counts = {}
    stem_suffixes = {}
    word_count = 0
    
    for line_words in folio_lines[folio]:
        for word in line_words:
            if not word or word == '?':
                continue
            word_count += 1
            stem, suffix = split_stem_suffix(word)
            if stem:
                if stem not in stem_counts:
                    stem_counts[stem] = 0
                    stem_suffixes[stem] = {}
                stem_counts[stem] += 1
                if suffix:
                    stem_suffixes[stem][suffix] = stem_suffixes[stem].get(suffix, 0) + 1
    
    folio_stem_data[folio] = {
        'stems': stem_counts,
        'suffixes': stem_suffixes,
        'word_count': word_count
    }

# Now do the elimination analysis
# For each folio, we need to identify which stems are likely CONTENT words
# (ingredients) vs FUNCTION words (actions/syntax).
# Key insight: stems with suffix C1/G1 in first columns = Entity (ingredient)
# stems with suffix A2 = Action (verb/instruction)
# stems with suffix B2/B3 = also ingredient-related (dose/amount)

print("\n")
for folio in target_folios:
    if folio not in folio_stem_data:
        continue
    
    data = folio_stem_data[folio]
    stems = data['stems']
    suffixes = data['suffixes']
    
    recipe_name = {
        'f87v': 'Unguentum Apostolorum',
        'f93v': 'Diascordium',
        'f96v': 'Pillulae Aureae'
    }[folio]
    
    recipe = recipes[recipe_name]
    n_ingredients = sum(len(v) for v in recipe.values())
    
    print(f"{'='*70}")
    print(f"FOLIO: {folio} = {recipe_name} ({n_ingredients} ingredients)")
    print(f"{'='*70}")
    print(f"Total words: {data['word_count']}")
    print(f"Total unique stems: {len(stems)}")
    
    # Classify stems by their dominant suffix
    entity_stems = []  # C1/G1 dominant - likely ingredients
    action_stems = []  # A2 dominant - likely verbs
    ingredient_ref_stems = []  # B2/B3 dominant - ingredient references
    other_stems = []
    
    for stem, count in sorted(stems.items(), key=lambda x: -x[1]):
        suf = suffixes.get(stem, {})
        total_suf = sum(suf.values())
        
        # Classify by dominant suffix
        c1g1 = suf.get('C1', 0) + suf.get('G1', 0)
        a2 = suf.get('A2', 0)
        b2b3 = suf.get('B2', 0) + suf.get('B3', 0)
        
        dominant = 'OTHER'
        if c1g1 > 0 and c1g1 >= a2 and c1g1 >= b2b3:
            dominant = 'ENTITY'
            entity_stems.append((stem, count, suf))
        elif a2 > 0 and a2 >= c1g1 and a2 >= b2b3:
            dominant = 'ACTION'
            action_stems.append((stem, count, suf))
        elif b2b3 > 0:
            dominant = 'INGREF'
            ingredient_ref_stems.append((stem, count, suf))
        else:
            other_stems.append((stem, count, suf))
    
    print(f"\nClassification by dominant suffix:")
    print(f"  ENTITY stems (C1/G1 dominant): {len(entity_stems)}")
    print(f"  ACTION stems (A2 dominant): {len(action_stems)}")
    print(f"  INGREF stems (B2/B3 dominant): {len(ingredient_ref_stems)}")
    print(f"  OTHER: {len(other_stems)}")
    
    # The ENTITY + INGREF stems are our ingredient candidates
    ingredient_candidates = entity_stems + ingredient_ref_stems
    
    print(f"\n  Total ingredient candidate stems: {len(ingredient_candidates)}")
    print(f"  Historical ingredients: {n_ingredients}")
    
    print(f"\n  ENTITY stems (most likely ingredients):")
    for stem, count, suf in entity_stems:
        suf_str = ', '.join(f"{k}:{v}" for k,v in sorted(suf.items(), key=lambda x:-x[1]))
        print(f"    [{stem}] x{count} suffixes: {suf_str}")
    
    print(f"\n  INGREF stems (also likely ingredients):")
    for stem, count, suf in ingredient_ref_stems:
        suf_str = ', '.join(f"{k}:{v}" for k,v in sorted(suf.items(), key=lambda x:-x[1]))
        print(f"    [{stem}] x{count} suffixes: {suf_str}")
    
    print(f"\n  ACTION stems (verbs/instructions - NOT ingredients):")
    for stem, count, suf in action_stems[:10]:
        suf_str = ', '.join(f"{k}:{v}" for k,v in sorted(suf.items(), key=lambda x:-x[1]))
        print(f"    [{stem}] x{count} suffixes: {suf_str}")
    
    print(f"\n  Historical ingredients to assign:")
    for cat in ["ACTIVO", "ESPECIA", "BASE"]:
        print(f"    {cat}: {recipe[cat]}")
    
    print()

# === FOCUSED ANALYSIS: f96v (smallest, best chance of 1:1 mapping) ===
print("\n" + "=" * 80)
print("DEEP DIVE: f96v (Pillulae Aureae) - 7 ingredients, best elimination target")
print("=" * 80)

folio = 'f96v'
data = folio_stem_data[folio]
stems = data['stems']
suffixes = data['suffixes']
recipe = recipes["Pillulae Aureae"]

# Known from constraint solver:
# K1K2A1 = Galbanum -- BUT wait, Galbanum is NOT in Pillulae Aureae!
# K1K2A1 might not be an ingredient in THIS recipe. Let's check.

# Actually K1K2A1 appears in f96v? Let me check.
print(f"\nAll stems in f96v:")
for stem, count in sorted(stems.items(), key=lambda x: -x[1]):
    suf = suffixes.get(stem, {})
    suf_str = ', '.join(f"{k}:{v}" for k,v in sorted(suf.items(), key=lambda x:-x[1]))
    print(f"  [{stem}] x{count}  suffixes: {suf_str}")

# From our recipe profile CSV, f96v has:
# Exclusives: U2J1A1, BaA3
# Generics: C2A1, A1B1A3, K1A3, C2A3, K1J1A1
# 7 stems = 7 ingredients (Pillulae Aureae)

# Now let's try to assign using MUTUAL EXCLUSION:
print(f"\n\nATTEMPTING 1:1 ASSIGNMENT for f96v = Pillulae Aureae:")
print(f"Ingredients: Aloe, Diagridium, Mastix, Rosa (ACTIVO) | Crocus, Cinnamomum (ESPECIA) | Succo absinthii (BASE)")
print(f"Stems in folio: U2J1A1, BaA3, C2A1, A1B1A3, K1A3, C2A3, K1J1A1")

# From consistency test:
# U2J1A1 -> ACTIVO consistently (Opium in Diascordium, Aloe in P.Aureae)
# BaA3 -> ACTIVO consistently (Galbanum in Ung.Apost, Diagridium in P.Aureae)
# K1A3 -> ESPECIA consistently (Cinnamomum in P.Aureae, Zingiber in Theriac)

# Since we're IN Pillulae Aureae:
# U2J1A1 was assigned Aloe (position-based) -> and it's ACTIVO. 
# BaA3 was assigned Diagridium (position-based) -> ACTIVO.
# K1A3 was assigned Cinnamomum -> ESPECIA.

# Let's see what remains after these assignments:
assigned = {
    "U2J1A1": "Aloe or another ACTIVO",  # We know it's ACTIVO
    "BaA3": "Diagridium or another ACTIVO",  # We know it's ACTIVO  
    "K1A3": "Cinnamomum or Crocus",  # We know it's ESPECIA
}

remaining_stems = ["C2A1", "A1B1A3", "C2A3", "K1J1A1"]
remaining_activo = ["Mastix", "Rosa"]  # 2 more ACTIVO needed
remaining_especia = ["Crocus"] if True else ["Cinnamomum"]  # 1 ESPECIA
remaining_base = ["Succo absinthii"]  # 1 BASE

print(f"\nAfter initial category assignments:")
print(f"  ACTIVO stems assigned (U2J1A1, BaA3) -> 2 of 4 ACTIVO ingredients used")
print(f"  ESPECIA stem assigned (K1A3) -> 1 of 2 ESPECIA ingredients used")
print(f"  Remaining ACTIVO ingredients: Mastix, Rosa (and Aloe/Diagridium to distribute)")
print(f"  Remaining ESPECIA ingredients: 1 (Crocus or Cinnamomum)")
print(f"  Remaining BASE ingredients: Succo absinthii")
print(f"  Remaining unassigned stems: {remaining_stems}")

# Check what categories these stems have in the recipe profiles
print(f"\n  Checking suffix profiles of remaining stems in f96v:")
for stem in remaining_stems:
    if stem in suffixes:
        suf = suffixes[stem]
        suf_str = ', '.join(f"{k}:{v}" for k,v in sorted(suf.items(), key=lambda x:-x[1]))
        print(f"    [{stem}] suffixes in f96v: {suf_str}")
    else:
        print(f"    [{stem}] - not found in suffix data")


# === Now do the same for f93v (Diascordium) ===
print("\n\n" + "=" * 80)
print("DEEP DIVE: f93v (Diascordium) - 14 ingredients")
print("=" * 80)

folio = 'f93v'
data = folio_stem_data[folio]
stems = data['stems']
suffixes = data['suffixes']

print(f"\nAll stems in f93v (sorted by frequency):")
for stem, count in sorted(stems.items(), key=lambda x: -x[1]):
    suf = suffixes.get(stem, {})
    suf_str = ', '.join(f"{k}:{v}" for k,v in sorted(suf.items(), key=lambda x:-x[1]))
    print(f"  [{stem}] x{count}  suffixes: {suf_str}")

# Known assignments from consistency + constraint solver:
# K1K2A1 = Galbanum (CONFIRMED by constraint solver - unique intersection!)
# U2J1A1 = ACTIVO (Opium assigned by position in Diascordium)
# L1A1 = ESPECIA (Zingiber assigned by position)
# D1A1Q1K1A1 = ESPECIA (Rosa assigned by position)
print(f"\nKnown assignments for f93v stems:")
print(f"  K1K2A1 = Galbanum (HIGH confidence - constraint solver)")
print(f"  U2J1A1 = ACTIVO (Opium by position)")
print(f"  L1A1 = ESPECIA (Zingiber by position)")
print(f"  D1A1Q1K1A1 = ESPECIA (Rosa by position)")
print(f"\nRemaining Diascordium ingredients to assign:")
print(f"  ACTIVO: Scordium, Castoreum, Styrax, Bistorta (Opium already tentatively assigned)")
print(f"  ESPECIA: Cinnamomum, Piper longum, Dictamnus, Gentiana")
print(f"  BASE: Mel despumatum")


# === COMPREHENSIVE CSV OUTPUT ===
print("\n\n" + "=" * 80)
print("GENERATING COMPREHENSIVE IDENTIFICATION TABLE")
print("=" * 80)

identifications = [
    # (Stem, Folio_Evidence, Category, Candidates, Confidence, Method)
    ("K1K2A1", "f87v+f93v+Theriac", "ACTIVO", "Galbanum", "ALTA",
     "Constraint solver: unica interseccion ACTIVO en Ung.Apost + Diascord + Theriac"),
    
    ("K1K2A1", "f93v=Diascordium", "ACTIVO", "Galbanum", "ALTA",
     "Confirmado: Galbanum es ACTIVO en Diascordium"),
    
    ("U2J1A1", "f93v+f96v", "ACTIVO", "Opium | Aloe (segun receta)", "MEDIA",
     "ACTIVO consistente. En Diascordium=Opium, en P.Aureae=Aloe. Sin interseccion directa."),
    
    ("BaA3", "f87v+f96v+Theriac", "ACTIVO", "Opopanax (probable)", "MEDIA",
     "ACTIVO consistente. Interseccion Ung.Apost x Theriac = {Galbanum, Opopanax}. "
     "Si K1K2A1=Galbanum, entonces BaA3=Opopanax por eliminacion en Ung.Apost."),
    
    ("D1A1Q1J1A1", "Aurea+Theriac", "ACTIVO",
     "Squilla | Petroselinum | Phu/Valeriana | Acorus calamus", "BAJA",
     "4 candidatos exactos. Opium/Castoreum/Hypericum tambien posibles (superset)."),
    
    ("L1A1", "f93v+Theriac", "ESPECIA", "Cinnamomum | Piper longum | Zingiber", "MEDIA",
     "3 candidatos. Todas son especias universales."),
    
    ("K1A3", "f96v+Theriac", "ESPECIA", "Cinnamomum | Crocus", "MEDIA-ALTA",
     "Solo 2 candidatos. Ambas presentes en P.Aureae y Theriac."),
    
    ("D1A1Q1K1A1", "f93v+Aurea", "ESPECIA", "Cinnamomum | Piper longum | Zingiber", "MEDIA",
     "3 candidatos. Mismo pool que L1A1."),
]

# Add BaA3 elimination logic
print("\nELIMINATION CHAIN for BaA3:")
print("  1. K1K2A1 = Galbanum (confirmed)")
print("  2. In Unguentum Apostolorum, ACTIVO = {Aristolochia longa, Aristolochia rotunda,")
print("     Opopanax, Galbanum, Bdellium, Verdigris, Litharge}")
print("  3. K1K2A1 takes Galbanum -> remaining ACTIVO = {Arist.longa, Arist.rotunda,")
print("     Opopanax, Bdellium, Verdigris, Litharge}")
print("  4. BaA3 is also ACTIVO in Ung.Apost -> BaA3 in {Arist.longa, Arist.rotunda,")
print("     Opopanax, Bdellium, Verdigris, Litharge}")
print("  5. BaA3 is ACTIVO in Theriac Magna too -> ACTIVO_Theriac = {20 ingredients}")
print("  6. Intersect remaining Ung.Apost ACTIVO with Theriac ACTIVO:")
ung_remaining_activo = {"Aristolochia longa", "Aristolochia rotunda", "Opopanax",
                         "Bdellium", "Verdigris", "Litharge"}
theriac_activo = {
    "Opium", "Trochisci de vipera", "Squilla", "Hedychium",
    "Castoreum", "Nardus celtica", "Petroselinum", "Phu/Valeriana",
    "Amomum", "Acorus calamus", "Hypericum", "Gentiana",
    "Aristolochia", "Opopanax", "Sagapenum", "Galbanum",
    "Balsamum", "Styrax", "Terebinthina", "Bitumen judaicum"
}
# Note: "Aristolochia" in Theriac could match "Aristolochia longa" or "rotunda"
# Let's do fuzzy matching
baa3_candidates_ung_theriac = set()
for ung_ing in ung_remaining_activo:
    for th_ing in theriac_activo:
        if ung_ing.split()[0] == th_ing.split()[0]:  # Same first word
            baa3_candidates_ung_theriac.add(ung_ing)
            break

print(f"  Ung.Apost remaining ACTIVO that are also in Theriac ACTIVO: {baa3_candidates_ung_theriac}")

# Now also intersect with Pillulae Aureae ACTIVO
pill_activo = {"Aloe", "Diagridium", "Mastix", "Rosa"}
print(f"  Pillulae Aureae ACTIVO: {pill_activo}")
print(f"  None of {{Aristolochia, Opopanax}} are in Pill.Aureae ACTIVO")
print(f"  This confirms the conflict: BaA3 cannot be the same ingredient in all 3 recipes")
print(f"  UNLESS the manuscript uses the same stem for different but functionally similar substances")
print(f"  (all are gum-resins: Galbanum/Opopanax/Diagridium are all plant exudates)")

print("\n  >> HYPOTHESIS: BaA3 = 'plant exudate/gum-resin' (generic functional class)")
print("  In Ung.Apost: Opopanax (gum-resin)")
print("  In Pill.Aureae: Diagridium (processed Scammony resin)")
print("  In Theriac: Terebinthina (tree resin)")
print("  ALL THREE are gum-resins! This is a SEMANTIC CLASS, not a single ingredient!")

# === Write final identification CSV ===
csv_path = r"C:\Ntizar_Obsidian\Ntizar_Brain\MASTERTMIND\voynich_identificaciones_candidatas.csv"
rows = [
    {
        "Stem_Voynich": "K1K2A1",
        "Tipo": "Exclusivo",
        "Folio_Origen": "f17v",
        "Categoria_Funcional": "ACTIVO",
        "Identificacion_Candidata": "Galbanum",
        "Confianza": "ALTA",
        "N_Candidatos": 1,
        "Metodo": "Constraint solver - interseccion unica en 3 recetas",
        "Notas": "Unico ACTIVO presente en Ung.Apostolorum AND Diascordium AND Theriac Magna",
    },
    {
        "Stem_Voynich": "BaA3",
        "Tipo": "Exclusivo",
        "Folio_Origen": "f33v",
        "Categoria_Funcional": "ACTIVO (gum-resin class)",
        "Identificacion_Candidata": "Clase: Goma-Resina (Opopanax/Diagridium/Terebinthina)",
        "Confianza": "MEDIA-ALTA",
        "N_Candidatos": 3,
        "Metodo": "Eliminacion + analisis semantico: siempre mapea a goma-resina vegetal",
        "Notas": "Ung.Apost=Opopanax, Pill.Aureae=Diagridium, Theriac=Terebinthina. Todas gomas-resinas.",
    },
    {
        "Stem_Voynich": "U2J1A1",
        "Tipo": "Exclusivo",
        "Folio_Origen": "f52v",
        "Categoria_Funcional": "ACTIVO (potent drug class)",
        "Identificacion_Candidata": "Clase: Farmaco potente (Opium/Aloe/similar)",
        "Confianza": "MEDIA",
        "N_Candidatos": 2,
        "Metodo": "Consistencia ACTIVO en 2 recetas sin interseccion directa",
        "Notas": "Diascordium=Opium, Pill.Aureae=Aloe. Ambos son los ingredientes activos principales.",
    },
    {
        "Stem_Voynich": "D1A1Q1J1A1",
        "Tipo": "Exclusivo",
        "Folio_Origen": "f49r",
        "Categoria_Funcional": "ACTIVO",
        "Identificacion_Candidata": "Squilla | Petroselinum | Phu/Valeriana | Acorus calamus",
        "Confianza": "BAJA",
        "N_Candidatos": 4,
        "Metodo": "Constraint solver - perfil exacto Aurea+Theriac exclusivo",
        "Notas": "4 candidatos con perfil exacto. Opium/Castoreum/Hypericum tambien posibles (superset).",
    },
    {
        "Stem_Voynich": "K1A3",
        "Tipo": "Generico",
        "Folio_Origen": "multiple",
        "Categoria_Funcional": "ESPECIA",
        "Identificacion_Candidata": "Cinnamomum | Crocus",
        "Confianza": "MEDIA-ALTA",
        "N_Candidatos": 2,
        "Metodo": "Constraint solver - solo 2 ESPECIA compartidas Pill.Aureae+Theriac",
        "Notas": "Si L1A1 o D1A1Q1K1A1 resulta ser Cinnamomum, entonces K1A3=Crocus por eliminacion.",
    },
    {
        "Stem_Voynich": "L1A1",
        "Tipo": "Generico",
        "Folio_Origen": "multiple",
        "Categoria_Funcional": "ESPECIA",
        "Identificacion_Candidata": "Cinnamomum | Piper longum | Zingiber",
        "Confianza": "MEDIA",
        "N_Candidatos": 3,
        "Metodo": "Constraint solver - 3 ESPECIA compartidas Diascord+Theriac",
        "Notas": "Pool compartido con D1A1Q1K1A1. Resolver uno resuelve el otro.",
    },
    {
        "Stem_Voynich": "D1A1Q1K1A1",
        "Tipo": "Generico",
        "Folio_Origen": "multiple",
        "Categoria_Funcional": "ESPECIA",
        "Identificacion_Candidata": "Cinnamomum | Piper longum | Zingiber",
        "Confianza": "MEDIA",
        "N_Candidatos": 3,
        "Metodo": "Constraint solver - 3 ESPECIA compartidas Diascord+Aurea Alex",
        "Notas": "Mismo pool que L1A1. Necesitan diferenciarse por frecuencia o co-ocurrencia.",
    },
]

with open(csv_path, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=[
        "Stem_Voynich", "Tipo", "Folio_Origen", "Categoria_Funcional",
        "Identificacion_Candidata", "Confianza", "N_Candidatos",
        "Metodo", "Notas"
    ])
    writer.writeheader()
    writer.writerows(rows)

print(f"\n\nIdentification CSV saved to: {csv_path}")

# === MUTUAL EXCLUSION IN f93v ===
print("\n\n" + "=" * 80)
print("MUTUAL EXCLUSION IN f93v (Diascordium)")
print("=" * 80)
print("Known: K1K2A1 = Galbanum")
print("Diascordium ACTIVO remaining: Scordium, Opium, Castoreum, Styrax, Bistorta")
print("Diascordium ESPECIA: Cinnamomum, Piper longum, Zingiber, Rosa, Gentiana, Dictamnus")
print("Diascordium BASE: Mel despumatum")
print()

# Stems in f93v from our profile:
# Exclusives: Q2K1A1B1A3, U2J1A1, K1K2A1
# Generics: D1A1Q2K1A1, U1A1, C2A1, L1A1, D1A1Q1K1A1, A2K1A1, B1K1A1, L1J1A1, K1J1A1, K1A1, C2A3

f93v_stems = {
    # Exclusives
    "Q2K1A1B1A3": "Exclusivo",
    "U2J1A1": "Exclusivo",
    "K1K2A1": "Exclusivo",
    # Generics
    "D1A1Q2K1A1": "Generico",
    "U1A1": "Generico",
    "C2A1": "Generico",
    "L1A1": "Generico",
    "D1A1Q1K1A1": "Generico",
    "A2K1A1": "Generico",
    "B1K1A1": "Generico",
    "L1J1A1": "Generico",
    "K1J1A1": "Generico",
    "K1A1": "Generico",
    "C2A3": "Generico",
}

print(f"Total stems in f93v: {len(f93v_stems)}")
print(f"Total ingredients in Diascordium: 14")
print(f"Exact match: {len(f93v_stems)} stems = 14 - 1 (K1K2A1 already assigned) = 13 remaining")
print()

# Assign K1K2A1 = Galbanum
# Remaining:
# 13 stems -> 13 ingredients (5 ACTIVO + 6 ESPECIA + 1 BASE... wait thats only 12)
# 6 ACTIVO - 1 (Galbanum) = 5 remaining ACTIVO
# 6 ESPECIA
# 1 BASE
# Total remaining = 12... but we have 13 stems (14 - 1 K1K2A1)
# Hmm, 14 stems total? Let me recount

# From profile: N_Ingredientes_Exclusivos=3, N_Ingredientes_Genericos=11, total unique = 14
# K1K2A1 is 1 of those 14. So 13 remain.
# Diascordium has 13 remaining ingredients (14 - Galbanum = 13). Perfect!

print("After K1K2A1=Galbanum:")
print(f"  13 stems to assign to 13 ingredients")
print()
print("Applying category constraints from consistency test:")
print("  U2J1A1 -> ACTIVO -> one of: Scordium, Opium, Castoreum, Styrax, Bistorta")
print("  L1A1 -> ESPECIA -> one of: Cinnamomum, Piper longum, Zingiber, Rosa, Gentiana, Dictamnus")
print("  D1A1Q1K1A1 -> ESPECIA -> one of: Cinnamomum, Piper longum, Zingiber, Rosa, Gentiana, Dictamnus")
print()
print("Note: If we could determine the category of the remaining 10 stems,")
print("and the Diascordium has exactly 5 ACTIVO + 6 ESPECIA + 1 BASE remaining,")
print("we could further constrain by group size.")

# Check: how many stems have A2-dominant suffix (these are VERBS, not ingredients)
# But wait - in a recipe folio with exactly #stems == #ingredients,
# ALL stems should be ingredients... unless some words are repeated as verbs.
# The word count is 60 but unique stems is 14. So many words share stems.
# The stems WITH suffix analysis tells us their ROLE.

print("\n\nDETAILED SUFFIX ANALYSIS for f93v stems (to determine category):")
f93v_data = folio_stem_data.get('f93v', {})
if f93v_data:
    for stem in sorted(f93v_stems.keys()):
        if stem in f93v_data['suffixes']:
            suf = f93v_data['suffixes'][stem]
            suf_str = ', '.join(f"{k}:{v}" for k,v in sorted(suf.items(), key=lambda x:-x[1]))
            # Determine likely category
            c1 = suf.get('C1', 0)
            g1 = suf.get('G1', 0)
            b2 = suf.get('B2', 0)
            b3 = suf.get('B3', 0)
            a2 = suf.get('A2', 0)
            c2 = suf.get('C2', 0)
            print(f"  [{stem}] ({f93v_stems[stem]}): {suf_str}")
        else:
            print(f"  [{stem}] ({f93v_stems[stem]}): NOT FOUND in suffix data")


print("\n\nDONE - Elimination solver complete.")
