import re

def check_vertical_alignments(filepath):
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
                
    alignments = 0
    total_pairs = 0
    
    # Simple check: same token index in consecutive lines within the same paragraph/folio
    for i in range(len(lines_data) - 1):
        meta1, tokens1 = lines_data[i]
        meta2, tokens2 = lines_data[i+1]
        
        # Check if they are in the same folio/block (rough heuristic: same prefix before dot)
        folio1 = meta1.split('.')[0] if '.' in meta1 else meta1
        folio2 = meta2.split('.')[0] if '.' in meta2 else meta2
        
        if folio1 == folio2:
            min_len = min(len(tokens1), len(tokens2))
            for j in range(min_len):
                total_pairs += 1
                if tokens1[j] == tokens2[j] and len(tokens1[j]) > 1:
                    alignments += 1
                    # print(f"Alignment at idx {j}: {tokens1[j]} in {meta1} and {meta2}")
                    
    print(f"Total consecutive line token index checks: {total_pairs}")
    print(f"Total exact vertical alignments found: {alignments}")
    print(f"Probability of alignment: {alignments/total_pairs:.4f}")

check_vertical_alignments('zenodo_voynich/corpus/voynich_sta.txt')
