import re
from collections import Counter

def split_atom(word):
    atoms = re.findall(r'[A-Z][a-z0-9]*', word)
    if len(atoms) > 1:
        return ''.join(atoms[:-1]), atoms[-1]
    elif len(atoms) == 1:
        return word, ""
    return "", ""

entities_by_folio = {}
global_entities = Counter()

with open('zenodo_voynich/corpus/voynich_sta.txt', 'r', encoding='utf-8') as f:
    for line in f:
        # Extraer el nombre del folio
        match = re.search(r'<(f[0-9]{1,3}[rv])', line)
        if not match: continue
        folio = match.group(1)
        
        # Solo sección Botánica (f1 a f57)
        if not re.match(r'f([1-9]|[1-4][0-9]|5[0-7])[rv]', folio):
            continue
            
        content = line.split('>')[1].strip() if '>' in line else ""
        if not content or content.startswith('<!'): continue
        
        tokens = [t.replace(',', '').replace('-', '').replace('*', '').replace('<', '') for t in content.split('.')]
        valid_tokens = [t for t in tokens if t.strip()]
        
        if not valid_tokens: continue
        
        # Analizar la Columna 1 (y a veces Columna 2 si es relevante)
        # Buscamos la etiqueta C1, que hemos definido como [ENTIDAD/SUJETO]
        for col_idx in range(min(2, len(valid_tokens))): 
            stem, suf = split_atom(valid_tokens[col_idx])
            
            if suf == 'C1' and len(stem) > 2: # Exigimos una raíz sustancial (>2 caracteres) para evitar ruido
                if folio not in entities_by_folio:
                    entities_by_folio[folio] = set()
                entities_by_folio[folio].add(stem)
                global_entities[stem] += 1

print("=== EXTRACTOR DE ENTIDADES PRIMARIAS (Sujetos C1 al inicio de línea) ===\n")

# Mostrar las entidades globales más repetidas (Posible vocabulario base de ingredientes)
print("1. TOP 10 'Entidades' (Raíces con etiqueta C1) que aparecen en múltiples folios botánicos:")
print(f"{'Raíz (Nombre/Ingrediente)':<30} | {'Frecuencia Global'}")
print("-" * 50)
for stem, count in global_entities.most_common(10):
    print(f"[{stem}]_C1 {'':<21} | {count}")

print("\n2. EXCLUSIVIDAD POR FOLIO (¿Cada planta tiene su propia clave primaria?)")
# Analizar si las entidades C1 de un folio son exclusivas de ese folio
exclusive_count = 0
total_extracted = 0

for folio, stems in list(entities_by_folio.items())[:10]: # Muestra los primeros 10 folios para no saturar
    print(f"\nFolio {folio}:")
    for stem in stems:
        total_extracted += 1
        occurrences_in_other_folios = sum(1 for f, s in entities_by_folio.items() if stem in s and f != folio)
        if occurrences_in_other_folios == 0:
            print(f"  - [{stem}]_C1  *(Exclusivo de esta página)*")
            exclusive_count += 1
        else:
            print(f"  - [{stem}]_C1  (Aparece en {occurrences_in_other_folios} folios más)")

# Estadística general
all_stems = set()
for stems in entities_by_folio.values():
    all_stems.update(stems)

total_unique_stems = len(all_stems)
total_exclusive_stems = sum(1 for stem in all_stems if sum(1 for s in entities_by_folio.values() if stem in s) == 1)

print("\n=== RESUMEN ESTADÍSTICO DE EXCLUSIVIDAD ===")
print(f"Total de 'Nombres de Entidades' únicos extraídos: {total_unique_stems}")
print(f"Entidades que SOLO aparecen en una página específica: {total_exclusive_stems} ({(total_exclusive_stems/total_unique_stems)*100:.1f}%)")

