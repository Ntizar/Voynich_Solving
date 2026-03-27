import re
import csv
from collections import Counter, defaultdict

def split_atom(word):
    atoms = re.findall(r'[A-Z][a-z0-9]*', word)
    if len(atoms) > 1:
        return ''.join(atoms[:-1]), atoms[-1]
    elif len(atoms) == 1:
        return word, ""
    return "", ""

botany_stems_by_folio = defaultdict(set)

pharmacy_occurrences = Counter()
recipes_occurrences = Counter()
pharmacy_tags = defaultdict(Counter)
recipes_tags = defaultdict(Counter)

# 1. Extraer Entidades de Botánica (Columna 1 y 2 con etiqueta C1)
with open('zenodo_voynich/corpus/voynich_sta.txt', 'r', encoding='utf-8') as f:
    for line in f:
        match = re.search(r'<(f[0-9]{1,3}[rv])', line)
        if not match: continue
        folio = match.group(1)
        
        content = line.split('>')[1].strip() if '>' in line else ""
        if not content or content.startswith('<!'): continue
        
        tokens = [t.replace(',', '').replace('-', '').replace('*', '').replace('<', '') for t in content.split('.')]
        valid_tokens = [t for t in tokens if t.strip()]
        
        # Botánica (f1-f57)
        if re.match(r'f([1-9]|[1-4][0-9]|5[0-7])[rv]', folio):
            for col_idx in range(min(2, len(valid_tokens))): 
                stem, suf = split_atom(valid_tokens[col_idx])
                if suf == 'C1' and len(stem) > 2:
                    botany_stems_by_folio[folio].add(stem)

# Determinar cuáles son Exclusivos y cuáles Comunes
all_botany_stems = set()
for stems in botany_stems_by_folio.values():
    all_botany_stems.update(stems)

exclusive_botany_stems = set()
common_botany_stems = set()

for stem in all_botany_stems:
    occurrences = sum(1 for s in botany_stems_by_folio.values() if stem in s)
    if occurrences == 1:
        exclusive_botany_stems.add(stem)
    else:
        common_botany_stems.add(stem)

# 2. Escanear Farmacia y Recetas buscando estos "Nombres"
with open('zenodo_voynich/corpus/voynich_sta.txt', 'r', encoding='utf-8') as f:
    for line in f:
        match = re.search(r'<(f[0-9]{1,3}[rv])', line)
        if not match: continue
        folio = match.group(1)
        
        content = line.split('>')[1].strip() if '>' in line else ""
        tokens = [t.replace(',', '').replace('-', '').replace('*', '').replace('<', '') for t in content.split('.')]
        valid_tokens = [t for t in tokens if t.strip()]
        
        is_pharmacy = re.match(r'f(8[7-9]|9[0-9]|10[0-2])[rv]', folio)
        is_recipes = re.match(r'f(10[3-9]|11[0-6])[rv]', folio)
        
        if is_pharmacy or is_recipes:
            for t in valid_tokens:
                stem, suf = split_atom(t)
                if stem in all_botany_stems:
                    if is_pharmacy:
                        pharmacy_occurrences[stem] += 1
                        if suf: pharmacy_tags[stem][suf] += 1
                    if is_recipes:
                        recipes_occurrences[stem] += 1
                        if suf: recipes_tags[stem][suf] += 1

# 3. Calcular Estadísticas
def calculate_stats(stem_set):
    found_in_pharmacy = sum(1 for s in stem_set if s in pharmacy_occurrences)
    found_in_recipes = sum(1 for s in stem_set if s in recipes_occurrences)
    found_in_both = sum(1 for s in stem_set if s in pharmacy_occurrences and s in recipes_occurrences)
    found_anywhere_later = sum(1 for s in stem_set if s in pharmacy_occurrences or s in recipes_occurrences)
    return len(stem_set), found_in_pharmacy, found_in_recipes, found_in_both, found_anywhere_later

ex_total, ex_pharm, ex_rec, ex_both, ex_any = calculate_stats(exclusive_botany_stems)
com_total, com_pharm, com_rec, com_both, com_any = calculate_stats(common_botany_stems)

print("=== CRUCE DE DATOS: BOTÁNICA VS FARMACIA/RECETAS ===")
print("\n[A] Nombres Propios (Aparecen en 1 sola página de Botánica)")
print(f"Total identificados: {ex_total}")
print(f"- Reaparecen en Farmacia: {ex_pharm} ({(ex_pharm/ex_total)*100:.1f}%)")
print(f"- Reaparecen en Recetas: {ex_rec} ({(ex_rec/ex_total)*100:.1f}%)")
print(f"- SUPERVIVENCIA TOTAL LUEGO: {ex_any} de {ex_total} ({(ex_any/ex_total)*100:.1f}%)")

print("\n[B] Nombres Genéricos (Aparecen en >1 página de Botánica)")
print(f"Total identificados: {com_total}")
print(f"- Reaparecen en Farmacia: {com_pharm} ({(com_pharm/com_total)*100:.1f}%)")
print(f"- Reaparecen en Recetas: {com_rec} ({(com_rec/com_total)*100:.1f}%)")
print(f"- SUPERVIVENCIA TOTAL LUEGO: {com_any} de {com_total} ({(com_any/com_total)*100:.1f}%)")

# Generar CSV para gráficos
with open('voynich_cruce_ingredientes.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Tipo_Vocabulario', 'Total_Botanica', 'Reaparece_Farmacia', 'Reaparece_Recetas', 'No_Reaparece_Nunca'])
    writer.writerow(['Nombres_Propios_Exclusivos', ex_total, ex_pharm, ex_rec, ex_total - ex_any])
    writer.writerow(['Nombres_Genericos_Comunes', com_total, com_pharm, com_rec, com_total - com_any])

print("\nArchivo 'voynich_cruce_ingredientes.csv' generado para graficar.")
