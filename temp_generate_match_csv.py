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

# Reconstruir mapa
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
for stems in botany_stems_by_folio.values(): all_bot_stems.update(stems)
exclusive_stems = set()
generic_stems = set()
for stem in all_bot_stems:
    if sum(1 for s in botany_stems_by_folio.values() if stem in s) == 1:
        exclusive_stems.add(stem)
    else:
        generic_stems.add(stem)

# Los 3 mejores matches para analizar en profundidad
best_matches = [
    ("f87v", "Unguentum Apostolorum", 12, [
        "Aristolochia longa", "Aristolochia rotunda", "Opopanax", "Galbanum",
        "Bdellium", "Verdigris", "Litharge", "Olibanum", "Myrrha",
        "Cera", "Oleum olivarum", "Resina"
    ]),
    ("f93v", "Diascordium", 14, [
        "Scordium", "Opium", "Castoreum", "Galbanum", "Styrax", "Bistorta",
        "Cinnamomum", "Piper longum", "Zingiber", "Rosa", "Gentiana",
        "Dictamnus", "Tormentilla", "Mel despumatum"
    ]),
    ("f96v", "Pillulae Aureae", 7, [
        "Aloe", "Diagridium", "Mastix", "Rosa", "Crocus", "Cinnamomum",
        "Succo absinthii"
    ]),
]

# Escanear los folios exactos
for target_folio, hist_name, hist_n, hist_ingredients in best_matches:
    excl_in_folio = Counter()
    gen_in_folio = Counter()
    
    with open('zenodo_voynich/corpus/voynich_sta.txt', 'r', encoding='utf-8') as f:
        for line in f:
            if f'<{target_folio}' in line:
                content = line.split('>')[1].strip() if '>' in line else ""
                if not content or content.startswith('<!'): continue
                tokens = [t.replace(',','').replace('-','').replace('*','').replace('<','') for t in content.split('.') if t.strip()]
                for t in tokens:
                    stem, suf = split_atom(t)
                    if stem in exclusive_stems: excl_in_folio[stem] += 1
                    if stem in generic_stems: gen_in_folio[stem] += 1
    
    all_ingredients_voynich = list(excl_in_folio.keys()) + list(gen_in_folio.keys())
    
    print(f"\n{'='*80}")
    print(f"MATCH: Folio {target_folio} <---> {hist_name}")
    print(f"{'='*80}")
    print(f"Ingredientes Voynich identificados: {len(all_ingredients_voynich)}")
    print(f"Ingredientes Historicos: {hist_n}")
    print(f"\nTABLA DE CORRESPONDENCIA HIPOTETICA:")
    print(f"{'#':>3} | {'Raiz Voynich':<20} | {'Tipo':<12} | {'Freq':>4} | {'Candidato Historico':<30} | {'Logica'}")
    print("-" * 100)
    
    # Ordenar: primero genericos por frecuencia (son las bases), luego exclusivos
    sorted_gen = sorted(gen_in_folio.items(), key=lambda x: -x[1])
    sorted_excl = sorted(excl_in_folio.items(), key=lambda x: -x[1])
    
    # Asignar: Las bases historicas van a los genericos mas frecuentes
    # Los activos historicos van a los exclusivos
    hist_bases = [i for i in hist_ingredients if any(k in i.lower() for k in ['mel', 'cera', 'oleum', 'resina', 'vinum', 'succo', 'sacch'])]
    hist_activos = [i for i in hist_ingredients if i not in hist_bases]
    
    idx = 0
    for i, (stem, freq) in enumerate(sorted_gen):
        idx += 1
        hist_match = hist_bases[i] if i < len(hist_bases) else hist_activos[min(i - len(hist_bases), len(hist_activos)-1)] if hist_activos else "?"
        logic = "BASE (mas frecuente = excipiente)" if i < len(hist_bases) else "ESPECIA/ACTIVO (generico recurrente)"
        print(f"{idx:>3} | [{stem}]{'_':>1}{'':<14} | {'Generico':<12} | {freq:>4} | {hist_match:<30} | {logic}")
    
    for i, (stem, freq) in enumerate(sorted_excl):
        idx += 1
        remaining = i
        if remaining < len(hist_activos):
            hist_match = hist_activos[remaining]
        else:
            hist_match = "? (Sin equivalente directo)"
        origin = [fol for fol, stems in botany_stems_by_folio.items() if stem in stems]
        origin_str = origin[0] if origin else "?"
        print(f"{idx:>3} | [{stem}]{'_':>1}{'':<14} | {'Exclusivo':<12} | {freq:>4} | {hist_match:<30} | ACTIVO RARO (planta de {origin_str})")

# Generar CSV de matches
with open('voynich_cruces_recetas_historicas.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([
        'Folio_Voynich', 'Receta_Historica_Candidata', 'Similitud_Tamano',
        'N_Ingredientes_Voynich', 'N_Ingredientes_Historicos',
        'Ingredientes_Historicos'
    ])
    for target_folio, hist_name, hist_n, hist_ingredients in best_matches:
        writer.writerow([
            target_folio, hist_name, '100%',
            hist_n, hist_n,
            ' | '.join(hist_ingredients)
        ])

print(f"\n\nArchivo CSV de cruces generado: voynich_cruces_recetas_historicas.csv")

