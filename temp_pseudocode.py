import re
from collections import Counter, defaultdict

def parse_corpus(filepath):
    words = []
    lines_data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('<') and '>' in line:
                parts = line.split('>')
                meta = parts[0] + '>'
                content = parts[1].strip()
                if not content or content.startswith('<!'): continue
                
                # Split content into words by '.'
                tokens = content.split('.')
                valid_tokens = []
                for t in tokens:
                    # Clean punctuation
                    t = t.replace(',', '').replace('-', '').replace('*', '')
                    if t:
                        valid_tokens.append(t)
                        words.append(t)
                
                lines_data.append((meta, valid_tokens))
    return words, lines_data

def split_atom(word):
    # Regex to capture atoms: uppercase letter followed by optional lowercase letters/numbers
    atoms = re.findall(r'[A-Z][a-z0-9]*', word)
    if len(atoms) > 1:
        return ''.join(atoms[:-1]), atoms[-1]
    elif len(atoms) == 1:
        return word, ""
    return "", ""

words, lines_data = parse_corpus('zenodo_voynich/corpus/voynich_sta.txt')

# Count stems
stems = Counter()
suffixes = Counter()

for w in words:
    stem, suffix = split_atom(w)
    if stem:
        stems[stem] += 1
    if suffix:
        suffixes[suffix] += 1

# Get top 30 stems and assign IDs
top_stems = {stem: f"S{i:02d}" for i, (stem, _) in enumerate(stems.most_common(30))}

# Target folio (e.g., f1r)
print("Folio f1r Pseudocode Translation:")
print("-" * 50)
for meta, tokens in lines_data[:10]:
    if not meta.startswith('<f1r.'): continue
    
    pseudo_line = []
    for t in tokens:
        stem, suffix = split_atom(t)
        
        stem_str = top_stems.get(stem, f"[{stem}]") if stem else "[]"
        suffix_str = f"_{suffix}" if suffix else ""
        
        if not suffix:
            pseudo_line.append(f"{stem_str}(PART)")
        else:
            pseudo_line.append(f"{stem_str}{suffix_str}")
            
    print(f"{meta:<15} {' '.join(pseudo_line)}")

