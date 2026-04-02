import re
import csv
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')

def split_atom(word):
    atoms = re.findall(r'[A-Z][a-z0-9]*', word)
    if len(atoms) > 1:
        return ''.join(atoms[:-1]), atoms[-1]
    elif len(atoms) == 1:
        return word, ""
    return "", ""

# 1. Reconstruir clasificacion de stems
botany_stems_by_folio = defaultdict(set)
with open('zenodo_voynich/corpus/voynich_sta.txt', 'r', encoding='utf-8') as f:
    for line in f:
        match = re.search(r'<(f[0-9]{1,3}[rv])', line)
        if not match: continue
        folio = match.group(1)
        if re.match(r'f([1-9]|[1-4][0-9]|5[0-7])[rv]', folio):
            content = line.split('>')[1].strip() if '>' in line else ""
            tokens = [t.replace(',','').replace('-','').replace('*','').replace('<','') for t in content.split('.') if t.strip()]
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

# 2. Definir recetas historicas (categorias simplificadas)
historical_recipes = {
    "Theriac Magna": [
        ("Mel despumatum", "BASE"), ("Vinum", "BASE"),
        ("Opium", "ACTIVO"), ("Trochisci viperae", "ACTIVO"),
        ("Squilla", "ACTIVO"), ("Castoreum", "ACTIVO"),
        ("Phu/Valeriana", "ACTIVO"), ("Gentiana", "ACTIVO"),
        ("Aristolochia", "ACTIVO"), ("Hypericum", "ACTIVO"),
        ("Opopanax", "ACTIVO"), ("Sagapenum", "ACTIVO"),
        ("Galbanum", "ACTIVO"), ("Balsamum", "ACTIVO"),
        ("Styrax", "ACTIVO"), ("Terebinthina", "ACTIVO"),
        ("Nardus celtica", "ACTIVO"), ("Acorus calamus", "ACTIVO"),
        ("Bitumen judaicum", "ACTIVO"), ("Hedychium", "ACTIVO"),
        ("Crocus/Azafran", "ESPECIA"), ("Zingiber", "ESPECIA"),
        ("Cinnamomum", "ESPECIA"), ("Piper longum", "ESPECIA"),
        ("Piper nigrum", "ESPECIA"), ("Myrrha", "ESPECIA"),
        ("Olibanum/Thus", "ESPECIA"), ("Casia", "ESPECIA"),
        ("Costus", "ESPECIA"), ("Anisi", "ESPECIA"),
        ("Foeniculum", "ESPECIA"), ("Daucus creticus", "ESPECIA"),
        ("Petroselinum", "ESPECIA"),
    ],
    "Diascordium": [
        ("Mel despumatum", "BASE"),
        ("Scordium", "ACTIVO"), ("Opium", "ACTIVO"),
        ("Castoreum", "ACTIVO"), ("Galbanum", "ACTIVO"),
        ("Styrax", "ACTIVO"), ("Bistorta", "ACTIVO"),
        ("Cinnamomum", "ESPECIA"), ("Piper longum", "ESPECIA"),
        ("Zingiber", "ESPECIA"), ("Rosa", "ESPECIA"),
        ("Gentiana", "ESPECIA"), ("Dictamnus", "ESPECIA"),
        ("Tormentilla", "ESPECIA"),
    ],
    "Pillulae Aureae": [
        ("Succo absinthii", "BASE"),
        ("Aloe", "ACTIVO"), ("Diagridium", "ACTIVO"),
        ("Mastix", "ACTIVO"), ("Rosa", "ACTIVO"),
        ("Crocus/Azafran", "ESPECIA"), ("Cinnamomum", "ESPECIA"),
    ],
    "Unguentum Apostolorum": [
        ("Cera", "BASE"), ("Oleum olivarum", "BASE"), ("Resina pini", "BASE"),
        ("Aristolochia longa", "ACTIVO"), ("Aristolochia rotunda", "ACTIVO"),
        ("Opopanax", "ACTIVO"), ("Galbanum", "ACTIVO"),
        ("Bdellium", "ACTIVO"), ("Verdigris", "ACTIVO"),
        ("Litharge", "ACTIVO"),
        ("Olibanum/Thus", "ESPECIA"), ("Myrrha", "ESPECIA"),
    ],
    "Aurea Alexandrina": [
        ("Mel despumatum", "BASE"), ("Vinum", "BASE"), ("Saccharum", "BASE"),
        ("Opium", "ACTIVO"), ("Castoreum", "ACTIVO"),
        ("Stachys", "ACTIVO"), ("Hypericum", "ACTIVO"),
        ("Petroselinum", "ACTIVO"), ("Acorus calamus", "ACTIVO"),
        ("Phu/Valeriana", "ACTIVO"), ("Squilla", "ACTIVO"),
        ("Crocus/Azafran", "ESPECIA"), ("Piper longum", "ESPECIA"),
        ("Piper nigrum", "ESPECIA"), ("Zingiber", "ESPECIA"),
        ("Cinnamomum", "ESPECIA"), ("Myrrha", "ESPECIA"),
        ("Costus", "ESPECIA"), ("Nardus", "ESPECIA"),
        ("Anisi", "ESPECIA"), ("Foeniculum", "ESPECIA"), ("Casia", "ESPECIA"),
    ],
}

# 3. Escanear folios de recetas
folio_ingredients = {}
target_folios = ['f87v', 'f93v', 'f96v', 'f90r', 'f113r']

with open('zenodo_voynich/corpus/voynich_sta.txt', 'r', encoding='utf-8') as f:
    for line in f:
        match = re.search(r'<(f[0-9]{1,3}[rv])', line)
        if not match: continue
        folio = match.group(1)
        if folio not in target_folios: continue

        content = line.split('>')[1].strip() if '>' in line else ""
        if not content or content.startswith('<!'): continue
        tokens = [t.replace(',','').replace('-','').replace('*','').replace('<','') for t in content.split('.') if t.strip()]

        if folio not in folio_ingredients:
            folio_ingredients[folio] = {'generics': Counter(), 'exclusives': Counter()}

        for t in tokens:
            stem, suf = split_atom(t)
            if stem in generic_stems: folio_ingredients[folio]['generics'][stem] += 1
            if stem in exclusive_stems: folio_ingredients[folio]['exclusives'][stem] += 1

# 4. Asignar candidatos historicos
stem_assignments = defaultdict(list)

best_folio_matches = [
    ('f87v', 'Unguentum Apostolorum'),
    ('f93v', 'Diascordium'),
    ('f96v', 'Pillulae Aureae'),
    ('f90r', 'Aurea Alexandrina'),
    ('f113r', 'Theriac Magna'),
]

for v_folio, h_name in best_folio_matches:
    if v_folio not in folio_ingredients: continue
    h_ingr = historical_recipes[h_name]

    h_bases = [i for i in h_ingr if i[1] == 'BASE']
    h_activos = [i for i in h_ingr if i[1] == 'ACTIVO']
    h_especias = [i for i in h_ingr if i[1] == 'ESPECIA']

    gen_sorted = sorted(folio_ingredients[v_folio]['generics'].items(), key=lambda x: -x[1])
    excl_sorted = sorted(folio_ingredients[v_folio]['exclusives'].items(), key=lambda x: -x[1])

    for i, (stem, freq) in enumerate(gen_sorted):
        if i < len(h_bases):
            assigned = h_bases[i]
        elif i - len(h_bases) < len(h_especias):
            assigned = h_especias[i - len(h_bases)]
        else:
            assigned = ("?", "DESCONOCIDO")
        stem_assignments[stem].append((v_folio, h_name, assigned[0], assigned[1], freq))

    for i, (stem, freq) in enumerate(excl_sorted):
        if i < len(h_activos):
            assigned = h_activos[i]
        else:
            assigned = ("?", "DESCONOCIDO")
        stem_assignments[stem].append((v_folio, h_name, assigned[0], assigned[1], freq))

# 5. TEST DE CONSISTENCIA
print("=" * 120)
print("TEST DE CONSISTENCIA CRUZADA: Palabras Voynich que aparecen en MULTIPLES recetas")
print("=" * 120)
print("")
print(f"{'Raiz Voynich':<20} | {'Tipo':<10} | {'N Rec':>5} | {'OK?':>3} | Asignaciones")
print("-" * 120)

consistent_count = 0
inconsistent_count = 0
multi_stems = []

for stem, assignments in sorted(stem_assignments.items(), key=lambda x: -len(x[1])):
    if len(assignments) < 2: continue

    tipo = "Generico" if stem in generic_stems else "Exclusivo"
    unique_recipes = set(a[1] for a in assignments)
    if len(unique_recipes) < 2: continue

    categories = set(a[3] for a in assignments)
    is_consistent = len(categories) == 1
    if is_consistent:
        consistent_count += 1
        status = "SI"
    else:
        inconsistent_count += 1
        status = "NO"

    assign_str = " | ".join([f"{a[1][:15]}->'{a[2]}' ({a[3]})" for a in assignments])

    print(f"[{stem}]{'':>{18-len(stem)}} | {tipo:<10} | {len(unique_recipes):>5} | {status:>3} | {assign_str}")
    multi_stems.append((stem, tipo, assignments, is_consistent))

total_multi = consistent_count + inconsistent_count
if total_multi > 0:
    print(f"\n{'='*80}")
    print(f"RESUMEN DE CONSISTENCIA:")
    print(f"  Palabras en 2+ recetas: {total_multi}")
    print(f"  CONSISTENTES (misma categoria): {consistent_count} ({(consistent_count/total_multi)*100:.1f}%)")
    print(f"  CONFLICTOS (categoria cambia):  {inconsistent_count} ({(inconsistent_count/total_multi)*100:.1f}%)")

# 6. Generar CSV
with open('voynich_consistencia_cruzada.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([
        'Raiz_Voynich', 'Tipo_Vocabulario', 'N_Recetas_Donde_Aparece',
        'Es_Consistente', 'Categorias_Asignadas',
        'Match_1_Receta', 'Match_1_Ingrediente', 'Match_1_Categoria',
        'Match_2_Receta', 'Match_2_Ingrediente', 'Match_2_Categoria',
        'Match_3_Receta', 'Match_3_Ingrediente', 'Match_3_Categoria',
        'Match_4_Receta', 'Match_4_Ingrediente', 'Match_4_Categoria',
        'Match_5_Receta', 'Match_5_Ingrediente', 'Match_5_Categoria',
    ])
    for stem, tipo, assignments, is_consistent in multi_stems:
        categories = set(a[3] for a in assignments)
        row = [stem, tipo, len(set(a[1] for a in assignments)),
               'SI' if is_consistent else 'NO',
               ' / '.join(categories)]
        for i in range(5):
            if i < len(assignments):
                row.extend([assignments[i][1], assignments[i][2], assignments[i][3]])
            else:
                row.extend(['', '', ''])
        writer.writerow(row)

print(f"\nArchivo generado: voynich_consistencia_cruzada.csv")
