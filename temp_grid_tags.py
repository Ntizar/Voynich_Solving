import re
from collections import Counter

def check_suffix_vertical_alignments(filepath):
    lines_data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('<') and '>' in line:
                parts = line.split('>')
                meta = parts[0] + '>'
                content = parts[1].strip()
                if not content or content.startswith('<!'): continue
                
                tokens = content.split('.')
                valid_tokens = []
                for t in tokens:
                    t = t.replace(',', '').replace('-', '').replace('*', '')
                    if t:
                        valid_tokens.append(t)
                lines_data.append((meta, valid_tokens))
                
    def get_suffix(word):
        atoms = re.findall(r'[A-Z][a-z0-9]*', word)
        return atoms[-1] if len(atoms) > 1 else ""

    alignments = 0
    total_pairs = 0
    suffix_pairs = Counter()
    
    for i in range(len(lines_data) - 1):
        meta1, tokens1 = lines_data[i]
        meta2, tokens2 = lines_data[i+1]
        
        folio1 = meta1.split('.')[0] if '.' in meta1 else meta1
        folio2 = meta2.split('.')[0] if '.' in meta2 else meta2
        
        if folio1 == folio2:
            min_len = min(len(tokens1), len(tokens2))
            for j in range(min_len):
                s1 = get_suffix(tokens1[j])
                s2 = get_suffix(tokens2[j])
                
                if s1 and s2:  # Only compare if both have suffixes
                    total_pairs += 1
                    suffix_pairs[(s1, s2)] += 1
                    if s1 == s2:
                        alignments += 1
                    
    print(f"Total vertical suffix comparisons: {total_pairs}")
    print(f"Exact identical suffix alignments (e.g. C1 over C1): {alignments}")
    print(f"Probability of exact suffix alignment: {alignments/total_pairs:.4f}")
    print("\nTop vertical suffix transitions (Line 1 -> Line 2 same column):")
    for (s1, s2), count in suffix_pairs.most_common(10):
        print(f"{s1} -> {s2}: {count} times")

check_suffix_vertical_alignments('zenodo_voynich/corpus/voynich_sta.txt')
