import re
import sys
from collections import Counter, defaultdict

# Forzar UTF-8 para evitar errores en Windows
sys.stdout.reconfigure(encoding='utf-8')

def split_atom(word):
    atoms = re.findall(r'[A-Z][a-z0-9]*', word)
    if len(atoms) > 1:
        return ''.join(atoms[:-1]), atoms[-1]
    elif len(atoms) == 1:
        return word, ""
    return "", ""

# 1. Reconstruir el mapa de Botánica (Orígenes)
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

exclusive_stems = set()
generic_stems = set()
all_stems = set()
for stems in botany_stems_by_folio.values(): all_stems.update(stems)

for stem in all_stems:
    occurrences = sum(1 for s in botany_stems_by_folio.values() if stem in s)
    if occurrences == 1: exclusive_stems.add(stem)
    else: generic_stems.add(stem)

# 2. Destripar la Súper Receta (Folio f113r)
f113r_tokens = []
f113r_generics = Counter()
f113r_exclusives = Counter()
f113r_actions = Counter() # Palabras que terminan en _A2
f113r_tags = Counter()

with open('zenodo_voynich/corpus/voynich_sta.txt', 'r', encoding='utf-8') as f:
    for line in f:
        if '<f113r' in line:
            content = line.split('>')[1].strip() if '>' in line else ""
            if not content or content.startswith('<!'): continue
            tokens = [t.replace(',', '').replace('-', '').replace('*', '').replace('<', '') for t in content.split('.') if t.strip()]
            
            for t in tokens:
                f113r_tokens.append(t)
                stem, suf = split_atom(t)
                
                if suf: f113r_tags[suf] += 1
                if suf == 'A2': f113r_actions[stem] += 1
                if stem in generic_stems: f113r_generics[stem] += 1
                if stem in exclusive_stems: f113r_exclusives[stem] += 1

print("=== ANATOMIA DE LA SUPER RECETA (Folio f113r) ===")
print(f"Total de palabras en la pagina: {len(f113r_tokens)}")

print("\n1. [Candidatos a BASE/EXCIPIENTE: Miel, Vino, Aceite]")
print("-> Palabras genericas mas repetidas. En una Triaca, la Miel aglutina todo.")
for stem, count in f113r_generics.most_common(4):
    print(f"   - Raiz [{stem}] : {count} veces (Aparece en toda la botanica)")

print("\n2. [Candidatos a INGREDIENTES ACTIVOS: Opio, Vibora, Azafran, Mirra]")
print("-> Plantas exclusivas (raras) concentradas en esta receta:")
for stem, count in f113r_exclusives.most_common(6):
    origin = [fol for fol, stems in botany_stems_by_folio.items() if stem in stems][0]
    print(f"   - Raiz [{stem}] : {count} veces (Dibujada originalmente en el Folio {origin})")

print("\n3. [Candidatos a VERBOS DE PREPARACION: Mezclar, Machacar, Hervir]")
print("-> Raices que llevan la etiqueta de Accion (_A2):")
for stem, count in f113r_actions.most_common(4):
    print(f"   - [{stem}]_A2 : {count} veces")

print("\n=== COMPARATIVA ESTADISTICA CON LA TRIACA MAGNA ===")
base_percent = (sum(f113r_generics.values()) / len(f113r_tokens)) * 100
active_percent = (sum(f113r_exclusives.values()) / len(f113r_tokens)) * 100
action_percent = (sum(f113r_actions.values()) / len(f113r_tokens)) * 100

print(f"Proporcion de Excipientes/Bases: {base_percent:.1f}% (Historico Triaca: ~30%)")
print(f"Proporcion de Plantas Activas: {active_percent:.1f}% (Historico Triaca: ~20%)")
print(f"Proporcion de Instrucciones/Verbos: {action_percent:.1f}%")

