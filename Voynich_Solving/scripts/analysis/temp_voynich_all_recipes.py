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

# 1. Reconstruir clasificación de stems
botany_stems_by_folio = defaultdict(set)
with open('zenodo_voynich/corpus/voynich_sta.txt', 'r', encoding='utf-8') as f:
    for line in f:
        match = re.search(r'<(f[0-9]{1,3}[rv])', line)
        if not match: continue
        folio = match.group(1)
        if re.match(r'f([1-9]|[1-4][0-9]|5[0-7])[rv]', folio):
            content = line.split('>')[1].strip() if '>' in line else ""
            tokens = [t.replace(',', '').replace('-', '').replace('*', '').replace('<', '') for t in content.split('.') if t.strip()]
            for col_idx in range(min(2, len(tokens))): 
                stem, suf = split_atom(tokens[col_idx])
                if suf == 'C1' and len(stem) > 2:
                    botany_stems_by_folio[folio].add(stem)

all_bot_stems = set()
for stems in botany_stems_by_folio.values(): all_bot_stems.update(stems)
exclusive_stems = set()
generic_stems = set()
for stem in all_bot_stems:
    if sum(1 for s in botany_stems_by_folio.values() if stem in s) == 1:
        exclusive_stems.add(stem)
    else:
        generic_stems.add(stem)

# 2. Escanear TODOS los folios de Farmacia/Recetas y crear el perfil de cada uno
recipe_profiles = defaultdict(lambda: {
    'total_words': 0,
    'exclusives': Counter(),
    'generics': Counter(),
    'actions': 0,
    'tags': Counter(),
    'all_stems': Counter()
})

with open('zenodo_voynich/corpus/voynich_sta.txt', 'r', encoding='utf-8') as f:
    for line in f:
        match = re.search(r'<(f[0-9]{1,3}[rv])', line)
        if not match: continue
        folio = match.group(1)
        
        if not re.match(r'f(8[7-9]|9[0-9]|10[0-9]|11[0-6])[rv]', folio): continue
        
        content = line.split('>')[1].strip() if '>' in line else ""
        if not content or content.startswith('<!'): continue
        tokens = [t.replace(',', '').replace('-', '').replace('*', '').replace('<', '') for t in content.split('.') if t.strip()]
        
        for t in tokens:
            stem, suf = split_atom(t)
            recipe_profiles[folio]['total_words'] += 1
            recipe_profiles[folio]['all_stems'][stem] += 1
            if suf: recipe_profiles[folio]['tags'][suf] += 1
            if suf == 'A2': recipe_profiles[folio]['actions'] += 1
            if stem in exclusive_stems: recipe_profiles[folio]['exclusives'][stem] += 1
            if stem in generic_stems: recipe_profiles[folio]['generics'][stem] += 1

# 3. Generar CSV con el perfil completo de cada receta Voynich
with open('voynich_todas_recetas_perfil.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([
        'Folio_Receta', 'Total_Palabras',
        'N_Ingredientes_Exclusivos', 'N_Ingredientes_Genericos', 'N_Acciones_A2',
        'Ratio_Exclusivos_%', 'Ratio_Genericos_%', 'Ratio_Acciones_%',
        'Lista_Exclusivos_Top5', 'Lista_Genericos_Top5',
        'Etiquetas_Dominantes'
    ])
    
    for folio in sorted(recipe_profiles.keys(), key=lambda x: int(re.findall(r'\d+', x)[0])):
        p = recipe_profiles[folio]
        total = p['total_words']
        if total < 5: continue # Ignorar folios casi vacios
        
        n_excl = len(p['exclusives'])
        n_gen = len(p['generics'])
        n_act = p['actions']
        
        excl_list = ' | '.join([f"{s}({c})" for s, c in p['exclusives'].most_common(5)])
        gen_list = ' | '.join([f"{s}({c})" for s, c in p['generics'].most_common(5)])
        tags_list = ' | '.join([f"{t}:{c}" for t, c in p['tags'].most_common(4)])
        
        writer.writerow([
            folio, total,
            n_excl, n_gen, n_act,
            round((sum(p['exclusives'].values())/total)*100, 1),
            round((sum(p['generics'].values())/total)*100, 1),
            round((n_act/total)*100, 1),
            excl_list, gen_list, tags_list
        ])

# 4. AHORA: El cruce automático por proporciones
print("=== CRUCE AUTOMATICO: RECETAS VOYNICH vs RECETAS HISTORICAS ===\n")

# Definir las proporciones históricas como targets
historical = [
    ("Theriac Magna", 64, 31.2, 18.8, 3.1),
    ("Mithridatium", 54, 29.6, 22.2, 3.7),
    ("Diascordium", 14, 42.9, 42.9, 7.1),
    ("Pillulae Cochiae", 5, 60.0, 40.0, 20.0),
    ("Pillulae Aureae", 7, 57.1, 28.6, 14.3),
    ("Unguentum Apostolorum", 12, 58.3, 16.7, 25.0),
    ("Electuarium Rosarum", 8, 50.0, 37.5, 12.5),
    ("Aurea Alexandrina", 22, 36.4, 50.0, 13.6),
]

# Para cada receta Voynich, calcular la "distancia" a cada receta histórica
matches = []

for folio in sorted(recipe_profiles.keys(), key=lambda x: int(re.findall(r'\d+', x)[0])):
    p = recipe_profiles[folio]
    total = p['total_words']
    if total < 10: continue
    
    n_excl_unique = len(p['exclusives'])
    n_gen_unique = len(p['generics'])
    total_identified = n_excl_unique + n_gen_unique
    if total_identified == 0: continue
    
    ratio_excl = (n_excl_unique / total_identified) * 100
    ratio_gen = (n_gen_unique / total_identified) * 100
    
    for hist_name, hist_total, hist_act, hist_esp, hist_bas in historical:
        # Comparar por total de ingredientes identificados
        size_diff = abs(total_identified - hist_total) / hist_total
        
        # Marcar match si la diferencia de tamaño es menor al 60%
        if size_diff < 0.6:
            matches.append((folio, total_identified, hist_name, hist_total, size_diff))

print(f"{'Folio Voynich':<15} | {'Ingredientes':>12} | {'Receta Historica Candidata':<35} | {'Ingred. Hist.':>13} | {'Similitud':>9}")
print("-" * 95)

# Ordenar por similitud (menor diferencia primero)
matches.sort(key=lambda x: x[4])

shown = set()
for folio, v_total, hist_name, hist_total, diff in matches[:20]:
    key = f"{folio}-{hist_name}"
    if key not in shown:
        shown.add(key)
        similarity = (1 - diff) * 100
        print(f"{folio:<15} | {v_total:>12} | {hist_name:<35} | {hist_total:>13} | {similarity:>8.1f}%")

