import re
from collections import Counter, defaultdict

def split_atom(word):
    atoms = re.findall(r'[A-Z][a-z0-9]*', word)
    if len(atoms) > 1:
        return ''.join(atoms[:-1]), atoms[-1]
    elif len(atoms) == 1:
        return word, ""
    return "", ""

# 1. Re-identify exclusive botany stems
botany_stems_by_folio = defaultdict(set)
with open('zenodo_voynich/corpus/voynich_sta.txt', 'r', encoding='utf-8') as f:
    for line in f:
        match = re.search(r'<(f[0-9]{1,3}[rv])', line)
        if not match: continue
        folio = match.group(1)
        if not re.match(r'f([1-9]|[1-4][0-9]|5[0-7])[rv]', folio): continue
        
        content = line.split('>')[1].strip() if '>' in line else ""
        tokens = [t.replace(',', '').replace('-', '').replace('*', '').replace('<', '') for t in content.split('.') if t.strip()]
        for col_idx in range(min(2, len(tokens))): 
            stem, suf = split_atom(tokens[col_idx])
            if suf == 'C1' and len(stem) > 2:
                botany_stems_by_folio[folio].add(stem)

all_botany_stems = set()
for stems in botany_stems_by_folio.values(): all_botany_stems.update(stems)

exclusive_botany_stems = set()
for stem in all_botany_stems:
    if sum(1 for s in botany_stems_by_folio.values() if stem in s) == 1:
        exclusive_botany_stems.add(stem)

# 2. Find the best candidate (highest frequency in Pharmacy/Recipes)
candidate_counts = Counter()
lines_with_candidate = []

with open('zenodo_voynich/corpus/voynich_sta.txt', 'r', encoding='utf-8') as f:
    for line in f:
        match = re.search(r'<(f[0-9]{1,3}[rv])', line)
        if not match: continue
        folio = match.group(1)
        content = line.split('>')[1].strip() if '>' in line else ""
        if not content or content.startswith('<!'): continue
        tokens = [t.replace(',', '').replace('-', '').replace('*', '').replace('<', '') for t in content.split('.') if t.strip()]
        
        for t in tokens:
            stem, suf = split_atom(t)
            if stem in exclusive_botany_stems:
                is_pharm_rec = re.match(r'f(8[7-9]|9[0-9]|10[0-9]|11[0-6])[rv]', folio)
                if is_pharm_rec:
                    candidate_counts[stem] += 1

best_candidate = candidate_counts.most_common(1)[0][0]

# 3. Extract Contexts for Best Candidate
botany_contexts = []
pharmacy_contexts = []

with open('zenodo_voynich/corpus/voynich_sta.txt', 'r', encoding='utf-8') as f:
    for line in f:
        match = re.search(r'<(f[0-9]{1,3}[rv])', line)
        if not match: continue
        folio = match.group(1)
        content = line.split('>')[1].strip() if '>' in line else ""
        if not content or content.startswith('<!'): continue
        tokens = [t.replace(',', '').replace('-', '').replace('*', '').replace('<', '') for t in content.split('.') if t.strip()]
        
        has_candidate = False
        for t in tokens:
            stem, suf = split_atom(t)
            if stem == best_candidate:
                has_candidate = True
                break
                
        if has_candidate:
            formatted_tokens = []
            for t in tokens:
                stem, suf = split_atom(t)
                suf_str = f"_{suf}" if suf else ""
                if stem == best_candidate:
                    formatted_tokens.append(f"**[{stem}]{suf_str}**")
                else:
                    formatted_tokens.append(f"{stem}{suf_str}")
                    
            context_str = " ".join(formatted_tokens)
            
            if re.match(r'f([1-9]|[1-4][0-9]|5[0-7])[rv]', folio):
                botany_contexts.append((folio, context_str))
            elif re.match(r'f(8[7-9]|9[0-9]|10[0-9]|11[0-6])[rv]', folio):
                pharmacy_contexts.append((folio, context_str))

print(f"=== EL ÁRBOL DE VIDA DE LA PLANTA: '{best_candidate}' ===\n")
print(f"Aparece originalmente SOLO en Botánica en el folio: {botany_contexts[0][0] if botany_contexts else 'N/A'}")
print(f"Reaparece en Farmacia/Recetas {candidate_counts[best_candidate]} veces.\n")

print("--- FASE 1: LA PLANTA EN SU HÁBITAT (Sección Botánica) ---")
for folio, ctx in botany_contexts:
    print(f"[{folio}] {ctx}")

print("\n--- FASE 2: LA PLANTA COMO INGREDIENTE (Sección Farmacia/Recetas) ---")
for folio, ctx in pharmacy_contexts[:8]: # Limit to 8 lines to avoid spam
    print(f"[{folio}] {ctx}")
if len(pharmacy_contexts) > 8:
    print(f"... (y {len(pharmacy_contexts) - 8} menciones más en recetas)")

