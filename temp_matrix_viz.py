import re

def split_atom(word):
    atoms = re.findall(r'[A-Z][a-z0-9]*', word)
    if len(atoms) > 1:
        return ''.join(atoms[:-1]), atoms[-1]
    elif len(atoms) == 1:
        return word, ""
    return "", ""

lines_data = []
with open('zenodo_voynich/corpus/voynich_sta.txt', 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('<f1r.') and '>' in line:
            parts = line.split('>')
            content = parts[1].strip()
            if not content or content.startswith('<!'): continue
            
            tokens = content.split('.')
            valid_tokens = [t.replace(',', '').replace('-', '').replace('*', '') for t in tokens if t.strip()]
            lines_data.append(valid_tokens)
            if len(lines_data) >= 12: # Take first 12 lines for a good grid
                break

# Build Matrix
matrix = []
max_words = 0
for tokens in lines_data:
    row = []
    for t in tokens:
        if t:
            stem, suf = split_atom(t)
            row.append((stem, suf))
    matrix.append(row)
    if len(row) > max_words:
        max_words = len(row)

# Generate Markdown Table
header = "| Línea | " + " | ".join([f"Columna {i+1}" for i in range(max_words)]) + " |"
separator = "|" + "|".join(["---"] * (max_words + 1)) + "|"

print(header)
print(separator)

for i, row in enumerate(matrix):
    row_str = f"| **L{i+1}** | "
    for j in range(max_words):
        if j < len(row):
            stem, suf = row[j]
            suf_display = f"**{suf}**" if suf else ""
            
            # Check vertical alignment with row above
            if i > 0 and j < len(matrix[i-1]):
                _, prev_suf = matrix[i-1][j]
                if suf and suf == prev_suf:
                    suf_display = f"🔥**{suf}**" # Highlight exact vertical match
            
            stem_display = f"[{stem[:4]}..]" if len(stem)>4 else f"[{stem}]"
            if not stem: stem_display = "[]"
            
            row_str += f"{stem_display}_{suf_display} | "
        else:
            row_str += " | "
    print(row_str)

