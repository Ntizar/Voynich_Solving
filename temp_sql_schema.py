import re
from collections import Counter

def split_atom(word):
    atoms = re.findall(r'[A-Z][a-z0-9]*', word)
    if len(atoms) > 1:
        return ''.join(atoms[:-1]), atoms[-1]
    elif len(atoms) == 1:
        return word, ""
    return "", ""

# Mapeo Hipotético de Tipos de Datos (Basado en nuestras estadísticas de columnas)
# C1 y G1 dominan el inicio. A2 domina el centro y final. B2 es secundario.
TAG_TO_TYPE = {
    'C1': '[ENTIDAD/SUJETO]',   # Ej: Nombre de la planta, ingrediente principal
    'G1': '[PROPIEDAD/ESTADO]', # Ej: Seco, verde, raíz, hoja
    'A2': '[ACCION/PROCESO]',   # Ej: Hervir, cortar, aplicar, esperar
    'B2': '[MEDIDA/CONTEXTO]',  # Ej: Dos onzas, en la luna llena, con agua
    'F1': '[VARIABLE_F]',
    'C2': '[VARIABLE_C2]',
    'E2': '[VARIABLE_E2]'
}

lines_data = []
botany_patterns = []

with open('zenodo_voynich/corpus/voynich_sta.txt', 'r', encoding='utf-8') as f:
    for line in f:
        # Solo sección Botánica (f1 a f57)
        if re.match(r'<f([1-9]|[1-4][0-9]|5[0-7])[rv]', line) and '>' in line:
            meta = line.split('>')[0] + '>'
            content = line.split('>')[1].strip()
            if not content or content.startswith('<!'): continue
            
            tokens = [t.replace(',', '').replace('-', '').replace('*', '') for t in content.split('.')]
            valid_tokens = [t for t in tokens if t.strip()]
            
            if len(valid_tokens) > 3: # Ignorar líneas muy cortas o rotas
                lines_data.append((meta, valid_tokens))
                
                # Extraer solo la secuencia de etiquetas (el "esqueleto")
                skeleton = []
                for t in valid_tokens:
                    _, suf = split_atom(t)
                    skeleton.append(suf if suf else 'NULL')
                botany_patterns.append(skeleton)

# 1. MOSTRAR TRADUCCIÓN VISUAL (Esquema SQL de 3 líneas del Folio f1v)
print("=== TRADUCCIÓN A ESQUEMA DE BASE DE DATOS (Folio f1v) ===")
print(f"{'Posición':<10} | {'Palabra Original':<15} | {'Etiqueta':<8} | {'Tipo de Dato Asignado (SQL)'}")
print("-" * 70)

for meta, tokens in lines_data:
    if '<f1v.1,' in meta or '<f1v.2,' in meta or '<f1v.3,' in meta:
        print(f"\n[{meta}]")
        for i, t in enumerate(tokens):
            stem, suf = split_atom(t)
            suf_display = suf if suf else 'NULL'
            data_type = TAG_TO_TYPE.get(suf, '[OTRO]')
            if not suf: data_type = '[DATO_HUERFANO]'
            print(f"Columna {i+1:<2} | {t:<15} | {suf_display:<8} | {data_type}")
    if len(botany_patterns) > 0 and '<f1v.4' in meta: # Parar después de 3 líneas
        break

# 2. EVALUACIÓN ESTADÍSTICA DEL "MOLDE" EN TODA LA SECCIÓN
print("\n=== EVALUACIÓN ESTADÍSTICA DEL MOLDE (Toda la Botánica) ===")
total_lines = len(botany_patterns)

# Patrón A: "Empieza con Entidad/Propiedad (C1/G1) y luego ejecuta Acciones (A2)"
# Es decir, una sintaxis tipo: Registro de Base de datos
match_pattern_A = 0
match_pattern_A2_heavy = 0

for skel in botany_patterns:
    if skel[0] in ['C1', 'G1']:
        # Comprobar si el resto de la línea tiene al menos un 40% de acciones (A2)
        a2_count = skel[1:].count('A2')
        if len(skel[1:]) > 0 and (a2_count / len(skel[1:])) >= 0.3:
            match_pattern_A += 1
            
    # Líneas que son puramente listas de acciones (más del 50% de la línea es A2)
    if skel.count('A2') / len(skel) >= 0.5:
        match_pattern_A2_heavy += 1

print(f"Total de líneas analizadas en Botánica: {total_lines}")
print(f"Líneas que siguen el esquema estricto [ENTIDAD/PROPIEDAD] -> [ACCIONES...]: {match_pattern_A} ({(match_pattern_A/total_lines)*100:.1f}%)")
print(f"Líneas que son listas de ejecución puras (>50% ACCIONES): {match_pattern_A2_heavy} ({(match_pattern_A2_heavy/total_lines)*100:.1f}%)")

