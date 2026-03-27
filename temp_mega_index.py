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

# Diccionarios de almacenamiento
botany_origins = defaultdict(set) # stem -> set(folios de botánica)
recipe_destinations = defaultdict(list) # stem -> list(folios de recetas)
recipe_tags = defaultdict(Counter) # stem -> Counter(etiquetas en recetas)

# 1. Escanear Botánica (Orígenes)
with open('zenodo_voynich/corpus/voynich_sta.txt', 'r', encoding='utf-8') as f:
    for line in f:
        match = re.search(r'<(f[0-9]{1,3}[rv])', line)
        if not match: continue
        folio = match.group(1)
        
        # Filtrar sección de botánica (f1 a f57)
        if re.match(r'f([1-9]|[1-4][0-9]|5[0-7])[rv]', folio):
            content = line.split('>')[1].strip() if '>' in line else ""
            if not content or content.startswith('<!'): continue
            
            tokens = [t.replace(',', '').replace('-', '').replace('*', '').replace('<', '') for t in content.split('.') if t.strip()]
            
            # Extraer raíces con etiqueta C1 en las primeras 2 columnas
            for col_idx in range(min(2, len(tokens))): 
                stem, suf = split_atom(tokens[col_idx])
                if suf == 'C1' and len(stem) > 2:
                    botany_origins[stem].add(folio)

# 2. Escanear Farmacia y Recetas (Destinos)
with open('zenodo_voynich/corpus/voynich_sta.txt', 'r', encoding='utf-8') as f:
    for line in f:
        match = re.search(r'<(f[0-9]{1,3}[rv])', line)
        if not match: continue
        folio = match.group(1)
        
        # Filtrar sección de Farmacia y Recetas (f87 a f116)
        if re.match(r'f(8[7-9]|9[0-9]|10[0-9]|11[0-6])[rv]', folio):
            content = line.split('>')[1].strip() if '>' in line else ""
            if not content or content.startswith('<!'): continue
            
            tokens = [t.replace(',', '').replace('-', '').replace('*', '').replace('<', '') for t in content.split('.') if t.strip()]
            
            for t in tokens:
                stem, suf = split_atom(t)
                if stem in botany_origins:
                    recipe_destinations[stem].append(folio)
                    if suf:
                        recipe_tags[stem][suf] += 1

# 3. Generar CSV Mega-Índice
csv_filename = 'voynich_mega_indice_conexiones.csv'
with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    # Cabeceras
    writer.writerow([
        'Raiz_Planta', 
        'Tipo_Vocabulario', 
        'Folios_Origen_Botanica', 
        'Apariciones_en_Recetas', 
        'Folios_Destino_Recetas', 
        'Etiquetas_Dominantes_en_Recetas'
    ])
    
    # Procesar y escribir datos
    for stem, origins in botany_origins.items():
        origins_list = sorted(list(origins))
        tipo = "Exclusiva (Nombre Propio)" if len(origins_list) == 1 else "Comun (Generica)"
        origenes_str = " | ".join(origins_list)
        
        destinos = recipe_destinations.get(stem, [])
        total_apariciones = len(destinos)
        
        if total_apariciones > 0:
            # Agrupar destinos para no tener listas enormes, ej: f88r (x3)
            dest_counts = Counter(destinos)
            destinos_str = " | ".join([f"{f} (x{c})" for f, c in dest_counts.most_common()])
            
            # Top 3 etiquetas en recetas
            tags = recipe_tags.get(stem, Counter())
            tags_str = " | ".join([f"{t}:{c}" for t, c in tags.most_common(3)])
        else:
            destinos_str = "NINGUNO"
            tags_str = "N/A"
            
        writer.writerow([
            stem,
            tipo,
            origenes_str,
            total_apariciones,
            destinos_str,
            tags_str
        ])

print(f"Archivo generado: {csv_filename}")
print(f"Total de raíces procesadas: {len(botany_origins)}")
print(f"Total de raíces que viajan a recetas: {len([s for s in botany_origins if s in recipe_destinations])}")

