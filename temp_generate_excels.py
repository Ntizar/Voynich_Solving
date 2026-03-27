import re
import csv
from collections import Counter, defaultdict

# Expresiones regulares para agrupar los folios en sus secciones temáticas clásicas
SECTIONS = {
    'Botanica': re.compile(r'<f([1-9]|[1-4][0-9]|5[0-7])[rv]'),
    'Astronomia': re.compile(r'<f(6[7-9]|7[0-3])[rv]'),
    'Biologia': re.compile(r'<f(7[5-9]|8[0-4])[rv]'),
    'Farmacia': re.compile(r'<f(8[7-9]|9[0-9]|10[0-2])[rv]'),
    'Recetas': re.compile(r'<f(10[3-9]|11[0-6])[rv]')
}

def split_atom(word):
    atoms = re.findall(r'[A-Z][a-z0-9]*', word)
    if len(atoms) > 1:
        return ''.join(atoms[:-1]), atoms[-1]
    elif len(atoms) == 1:
        return word, ""
    return "", ""

# Estructuras de datos
botany_positions = defaultdict(Counter) # {posicion_columna: Counter(etiquetas)}
section_suffix_dist = defaultdict(Counter) # {seccion: Counter(etiquetas)}
section_total_words = Counter()

with open('zenodo_voynich/corpus/voynich_sta.txt', 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('<') and '>' in line:
            parts = line.split('>')
            meta = parts[0] + '>'
            content = parts[1].strip()
            if not content or content.startswith('<!'): continue
            
            tokens = [t.replace(',', '').replace('-', '').replace('*', '') for t in content.split('.')]
            valid_tokens = [t for t in tokens if t.strip()]
            
            # Identificar la sección
            current_section = "Otro"
            for sec_name, sec_regex in SECTIONS.items():
                if sec_regex.match(meta):
                    current_section = sec_name
                    break
            
            # Análisis posicional (Columnas) SOLO para Botánica (f1-f57)
            if current_section == 'Botanica':
                for pos, token in enumerate(valid_tokens):
                    if pos >= 10: break # Limitar a las primeras 10 columnas
                    _, suf = split_atom(token)
                    if suf:
                        botany_positions[pos][suf] += 1
            
            # Análisis de distribución por Sección
            if current_section != "Otro":
                for token in valid_tokens:
                    _, suf = split_atom(token)
                    if suf:
                        section_suffix_dist[current_section][suf] += 1
                        section_total_words[current_section] += 1

# --- GENERAR EXCEL/CSV 1: Plantilla de Columnas (Botánica) ---
top_suffixes = ['A2', 'B2', 'C1', 'G1', 'F1', 'C2', 'E2'] # Las 7 etiquetas más comunes
with open('voynich_columnas_botanica.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Posicion_Columna'] + top_suffixes + ['Otras'])
    
    for pos in range(10): # Columnas 1 a 10
        row = [f'Columna {pos+1}']
        total_in_pos = sum(botany_positions[pos].values())
        if total_in_pos == 0: continue
        
        others_count = total_in_pos
        for suf in top_suffixes:
            count = botany_positions[pos].get(suf, 0)
            # Guardamos el porcentaje
            perc = (count / total_in_pos) * 100 if total_in_pos > 0 else 0
            row.append(round(perc, 2))
            others_count -= count
            
        row.append(round((others_count / total_in_pos) * 100, 2))
        writer.writerow(row)

# --- GENERAR EXCEL/CSV 2: Cambio de Formato por Sección ---
with open('voynich_secciones_etiquetas.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Seccion', 'Total_Palabras'] + top_suffixes + ['Otras'])
    
    for sec_name in SECTIONS.keys():
        total = section_total_words[sec_name]
        if total == 0: continue
        
        row = [sec_name, total]
        others_count = total
        for suf in top_suffixes:
            count = section_suffix_dist[sec_name].get(suf, 0)
            perc = (count / total) * 100 if total > 0 else 0
            row.append(round(perc, 2))
            others_count -= count
            
        row.append(round((others_count / total) * 100, 2))
        writer.writerow(row)

print("Archivos CSV generados con éxito.")
print("- voynich_columnas_botanica.csv")
print("- voynich_secciones_etiquetas.csv")
