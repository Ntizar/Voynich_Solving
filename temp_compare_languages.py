import re
from collections import Counter
import random

def get_voynich_stats():
    lines_data = []
    with open('zenodo_voynich/corpus/voynich_sta.txt', 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('<') and '>' in line:
                parts = line.split('>')
                content = parts[1].strip()
                if not content or content.startswith('<!'): continue
                
                tokens = [t.replace(',', '').replace('-', '').replace('*', '') for t in content.split('.')]
                tokens = [t for t in tokens if t]
                if tokens:
                    lines_data.append(tokens)

    def get_suffix(word):
        atoms = re.findall(r'[A-Z][a-z0-9]*', word)
        return atoms[-1] if len(atoms) > 1 else ""

    suffixes = []
    alignments = 0
    total_pairs = 0
    
    for i in range(len(lines_data) - 1):
        tokens1, tokens2 = lines_data[i], lines_data[i+1]
        min_len = min(len(tokens1), len(tokens2))
        
        for j in range(min_len):
            s1 = get_suffix(tokens1[j])
            s2 = get_suffix(tokens2[j])
            if s1 and s2:
                total_pairs += 1
                suffixes.extend([s1, s2])
                if s1 == s2:
                    alignments += 1

    # Frequencies for Expected Probability
    freq = Counter(suffixes)
    total_suffixes = sum(freq.values())
    expected_prob = sum((count/total_suffixes)**2 for count in freq.values())
    observed_prob = alignments / total_pairs if total_pairs > 0 else 0
    
    return observed_prob, expected_prob, total_pairs

def get_natural_language_stats(text, lang_name, chars_for_suffix=2):
    # Clean text
    words = re.findall(r'\b[a-zA-ZáéíóúÁÉÍÓÚñÑ]+\b', text.lower())
    
    # Voynich averages about 7-8 words per line. We simulate lines of 8 words.
    line_length = 8
    lines_data = [words[i:i + line_length] for i in range(0, len(words), line_length)]
    
    def get_suffix(word):
        # In natural languages, the last N letters often denote grammatical function 
        # (e.g., -ing, -ed in English; -os, -as, -um in Latin/Spanish)
        return word[-chars_for_suffix:] if len(word) >= chars_for_suffix else word

    suffixes = []
    alignments = 0
    total_pairs = 0
    
    for i in range(len(lines_data) - 1):
        tokens1, tokens2 = lines_data[i], lines_data[i+1]
        min_len = min(len(tokens1), len(tokens2))
        
        for j in range(min_len):
            s1 = get_suffix(tokens1[j])
            s2 = get_suffix(tokens2[j])
            total_pairs += 1
            suffixes.extend([s1, s2])
            if s1 == s2:
                alignments += 1
                
    freq = Counter(suffixes)
    total_suffixes = sum(freq.values())
    expected_prob = sum((count/total_suffixes)**2 for count in freq.values()) if total_suffixes else 0
    observed_prob = alignments / total_pairs if total_pairs > 0 else 0
    
    return observed_prob, expected_prob, total_pairs

# Samples
latin_text = """
In principio creavit Deus caelum et terram. Terra autem erat inanis et vacua, et tenebrae erant super faciem abyssi: et spiritus Dei ferebatur super aquas. Dixitque Deus: Fiat lux. Et facta est lux. Et vidit Deus lucem quod esset bona: et divisit lucem a tenebris. Appellavitque lucem Diem, et tenebras Noctem: factumque est vespere et mane, dies unus. Dixit quoque Deus: Fiat firmamentum in medio aquarum: et dividat aquas ab aquis. Et fecit Deus firmamentum, divisitque aquas, quae erant sub firmamento, ab his, quae erant super firmamentum. Et factum est ita. Vocavitque Deus firmamentum, Caelum: et factum est vespere et mane, dies secundus. Dixit vero Deus: Congregentur aquae, quae sub caelo sunt, in locum unum: et appareat arida. Et factum est ita. Et vocavit Deus aridam Terram, congregationesque aquarum appellavit Maria. Et vidit Deus quod esset bonum.
""" * 10 # Repeat to get a decent sample size

spanish_text = """
En un lugar de la Mancha, de cuyo nombre no quiero acordarme, no ha mucho tiempo que vivía un hidalgo de los de lanza en astillero, adarga antigua, rocín flaco y galgo corredor. Una olla de algo más vaca que carnero, salpicón las más noches, duelos y quebrantos los sábados, lantejas los viernes, algún palomino de añadidura los domingos, consumían las tres partes de su hacienda. El resto della concluían sayo de velarte, calzas de velludo para las fiestas con sus pantuflos de lo mismo, los días de entre semana se honraba con su vellori de lo más fino. Tenía en su casa una ama que pasaba de los cuarenta, y una sobrina que no llegaba a los veinte, y un mozo de campo y plaza, que así ensillaba el rocín como tomaba la podadera. Frisaba la edad de nuestro hidalgo con los cincuenta años.
""" * 10

v_obs, v_exp, v_pairs = get_voynich_stats()
l_obs, l_exp, l_pairs = get_natural_language_stats(latin_text, "Latín", chars_for_suffix=2)
s_obs, s_exp, s_pairs = get_natural_language_stats(spanish_text, "Español", chars_for_suffix=2)

print(f"{'Idioma / Texto':<20} | {'Alineación Observada':<22} | {'Alineación Esperada (Azar)':<28} | {'Diferencia (Obs - Esp)'}")
print("-" * 100)
print(f"{'Voynich (Etiquetas)':<20} | {v_obs*100:>19.2f}%   | {v_exp*100:>25.2f}%   | {((v_obs-v_exp)/v_exp)*100:>19.1f}% más que el azar")
print(f"{'Latín (Sufijos)':<20} | {l_obs*100:>19.2f}%   | {l_exp*100:>25.2f}%   | {((l_obs-l_exp)/l_exp)*100:>19.1f}% más que el azar")
print(f"{'Español (Sufijos)':<20} | {s_obs*100:>19.2f}%   | {s_exp*100:>25.2f}%   | {((s_obs-s_exp)/s_exp)*100:>19.1f}% más que el azar")
