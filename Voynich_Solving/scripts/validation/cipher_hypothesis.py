"""
Voynich Validation Framework -- Cipher Hypothesis Tester
========================================================
Tests whether the structural patterns observed in the Voynich manuscript
could be explained by simple cipher systems rather than a pharmaceutical
database structure.

Addresses the critique:
    "The project dismisses cipher theories too quickly. Even if the
    manuscript functions as a database, it could still employ some type
    of coding or conventional notation."

Tests:
    1. Homophonic substitution: Can a simple cipher produce the observed
       entropy and suffix distribution?
    2. Frequency analysis: Does the Voynich frequency distribution match
       known ciphers, natural languages, or something else?
    3. Token uniqueness: Is the type/token ratio consistent with cipher,
       natural language, or a coding system?
    4. Bigram/contact patterns: Do glyph contact patterns match cipher
       or natural language behavior?

Run:
    python -m scripts.validation.cipher_hypothesis
"""
import sys
import os
import math
import random
import json
from collections import Counter, defaultdict

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.validation.config import PATHS, RANDOM_SEED, ensure_output_dirs
from scripts.validation import data_loader as dl

sys.stdout.reconfigure(encoding='utf-8')

N_SIMULATIONS = 500


# ── Reference frequency distributions ────────────────────────────────────────
# These are approximate letter/glyph frequencies from known historical sources

LATIN_LETTER_FREQ = {
    'e': 0.120, 'i': 0.110, 'a': 0.095, 'u': 0.085, 's': 0.075,
    't': 0.070, 'n': 0.065, 'r': 0.060, 'o': 0.055, 'm': 0.040,
    'c': 0.035, 'l': 0.030, 'd': 0.025, 'p': 0.020, 'b': 0.015,
    'g': 0.012, 'f': 0.010, 'h': 0.008, 'q': 0.005, 'x': 0.003,
    'v': 0.002, 'y': 0.001, 'z': 0.001,
}

CASTILIAN_LETTER_FREQ = {
    'e': 0.127, 'a': 0.116, 'o': 0.088, 's': 0.072, 'r': 0.069,
    'n': 0.067, 'i': 0.063, 'l': 0.050, 'd': 0.047, 't': 0.046,
    'c': 0.044, 'u': 0.039, 'm': 0.031, 'p': 0.025, 'b': 0.014,
    'g': 0.010, 'v': 0.009, 'h': 0.007, 'f': 0.007, 'q': 0.005,
    'y': 0.009, 'j': 0.004, 'x': 0.002, 'z': 0.005,
}


# ── Helper functions ─────────────────────────────────────────────────────────
def compute_entropy(distribution):
    """Shannon entropy from a frequency distribution."""
    total = sum(distribution.values())
    if total == 0:
        return 0.0
    entropy = 0.0
    for count in distribution.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)
    return entropy


def compute_index_of_coincidence(distribution):
    """Index of Coincidence (IC) -- a key cipher detection metric.
    
    IC = sum(f_i * (f_i - 1)) / (N * (N - 1))
    
    Natural language: ~0.065 (English), ~0.072 (Latin)
    Random text:      ~0.038 (1/26)
    Simple substitution: same as source language
    Polyalphabetic:   between random and language
    """
    total = sum(distribution.values())
    if total <= 1:
        return 0.0
    ic = sum(c * (c - 1) for c in distribution.values()) / (total * (total - 1))
    return ic


def chi_squared_distance(observed, expected):
    """Chi-squared distance between two frequency distributions."""
    all_keys = set(observed.keys()) | set(expected.keys())
    total_obs = sum(observed.values())
    total_exp = sum(expected.values())
    
    if total_obs == 0 or total_exp == 0:
        return float('inf')
    
    chi2 = 0.0
    for key in all_keys:
        obs_freq = observed.get(key, 0) / total_obs
        exp_freq = expected.get(key, 0) / total_exp
        if exp_freq > 0:
            chi2 += (obs_freq - exp_freq)**2 / exp_freq
    return chi2


def generate_homophonic_cipher(source_freq, n_symbols, text_length, rng):
    """Generate text from a homophonic substitution cipher.
    
    Each source letter is mapped to 1-4 symbols proportional to its frequency.
    This produces uniform-ish symbol frequencies (a key feature of homophonic
    ciphers that makes them harder to crack by frequency analysis).
    """
    # Assign symbols to letters proportional to frequency
    letters = sorted(source_freq.keys(), key=lambda x: -source_freq[x])
    symbol_map = {}
    current_symbol = 0
    
    for letter in letters:
        n_assigned = max(1, int(source_freq[letter] * n_symbols))
        symbols = list(range(current_symbol, current_symbol + n_assigned))
        if current_symbol + n_assigned > n_symbols:
            symbols = list(range(current_symbol, n_symbols))
        symbol_map[letter] = symbols
        current_symbol += n_assigned
        if current_symbol >= n_symbols:
            break
    
    # Ensure all remaining symbols are assigned to high-frequency letters
    remaining = list(range(current_symbol, n_symbols))
    for i, sym in enumerate(remaining):
        letter = letters[i % len(letters)]
        symbol_map[letter].append(sym)
    
    # Generate cipher text
    text = []
    for _ in range(text_length):
        # Pick a source letter by frequency
        r = rng.random()
        cumulative = 0
        chosen_letter = letters[0]
        for letter in letters:
            cumulative += source_freq[letter]
            if r < cumulative:
                chosen_letter = letter
                break
        # Pick a random symbol from its homophones
        if symbol_map.get(chosen_letter):
            text.append(rng.choice(symbol_map[chosen_letter]))
        else:
            text.append(0)
    
    return text


def generate_polyalphabetic_cipher(source_freq, n_alphabets, text_length, rng):
    """Generate text from a polyalphabetic cipher (like Vigenere).
    
    Cycles through n_alphabets different substitution alphabets.
    Each alphabet is a random permutation of the source alphabet.
    """
    letters = sorted(source_freq.keys())
    alphabets = []
    for _ in range(n_alphabets):
        perm = list(letters)
        rng.shuffle(perm)
        alphabets.append({orig: perm[i] for i, orig in enumerate(letters)})
    
    text = []
    for i in range(text_length):
        # Pick source letter
        r = rng.random()
        cumulative = 0
        chosen = letters[0]
        for letter in sorted(source_freq.keys(), key=lambda x: -source_freq[x]):
            cumulative += source_freq[letter]
            if r < cumulative:
                chosen = letter
                break
        # Apply current alphabet
        alphabet = alphabets[i % n_alphabets]
        text.append(alphabet.get(chosen, chosen))
    
    return text


# ── Voynich atom-level analysis ──────────────────────────────────────────────
def analyze_voynich_atoms():
    """Analyze the Voynich manuscript at the atom level (STA1 glyphs)."""
    corpus = dl.load_corpus()
    folio_words = dl.corpus_to_folio_words(corpus)
    
    # Get atoms from recipe folios
    all_atoms = []
    word_lengths = []  # in atoms
    
    for folio, words in folio_words.items():
        # Only recipe folios
        if not any(folio.startswith(p) for p in ['f87', 'f88', 'f89', 'f9', 'f10', 'f11']):
            continue
        for word in words:
            atoms = dl.parse_atoms(word)
            if atoms:
                all_atoms.extend(atoms)
                word_lengths.append(len(atoms))
    
    atom_freq = Counter(all_atoms)
    word_freq = Counter(tuple(dl.parse_atoms(w)) for folio, words in folio_words.items()
                        for w in words
                        if any(folio.startswith(p) for p in ['f87', 'f88', 'f89', 'f9', 'f10', 'f11'])
                        and dl.parse_atoms(w))
    
    # Type/token ratio
    n_tokens = len(all_atoms)
    n_types = len(atom_freq)
    ttr = n_types / n_tokens if n_tokens > 0 else 0
    
    # Word type/token ratio
    all_words = []
    for folio, words in folio_words.items():
        if any(folio.startswith(p) for p in ['f87', 'f88', 'f89', 'f9', 'f10', 'f11']):
            all_words.extend(words)
    word_type_count = len(set(all_words))
    word_token_count = len(all_words)
    word_ttr = word_type_count / word_token_count if word_token_count > 0 else 0
    
    return {
        'atom_freq': dict(atom_freq),
        'n_atoms': n_tokens,
        'n_unique_atoms': n_types,
        'atom_ttr': ttr,
        'atom_entropy': compute_entropy(atom_freq),
        'atom_ic': compute_index_of_coincidence(atom_freq),
        'word_types': word_type_count,
        'word_tokens': word_token_count,
        'word_ttr': word_ttr,
        'mean_word_length': sum(word_lengths) / len(word_lengths) if word_lengths else 0,
    }


# ── Main cipher hypothesis testing ──────────────────────────────────────────
def run_cipher_hypothesis():
    print("=" * 75)
    print("VOYNICH CIPHER HYPOTHESIS TESTER")
    print("Can cipher systems explain the observed structural patterns?")
    print("=" * 75)

    # Analyze Voynich
    print("\n--- Analyzing Voynich manuscript atoms ---")
    voynich = analyze_voynich_atoms()
    
    print(f"  Total atoms:      {voynich['n_atoms']}")
    print(f"  Unique atoms:     {voynich['n_unique_atoms']}")
    print(f"  Atom TTR:         {voynich['atom_ttr']:.4f}")
    print(f"  Atom entropy:     {voynich['atom_entropy']:.3f} bits")
    print(f"  Index of Coinc.:  {voynich['atom_ic']:.4f}")
    print(f"  Word types:       {voynich['word_types']}")
    print(f"  Word tokens:      {voynich['word_tokens']}")
    print(f"  Word TTR:         {voynich['word_ttr']:.4f}")
    print(f"  Mean word length: {voynich['mean_word_length']:.2f} atoms")
    print(f"  Top atoms: {Counter(voynich['atom_freq']).most_common(10)}")

    # ── Test 1: Index of Coincidence classification ──────────────────────
    print(f"\n{'='*75}")
    print("TEST 1: INDEX OF COINCIDENCE (IC) CLASSIFICATION")
    print(f"{'='*75}")
    print("IC distinguishes between natural language, simple substitution,")
    print("polyalphabetic ciphers, and random text.")
    
    # Reference IC values
    ic_references = {
        'Latin (natural)': 0.072,
        'Castilian (natural)': 0.078,
        'English (natural)': 0.065,
        'Simple substitution': 0.070,  # Same as source language
        'Polyalphabetic (5 alphabets)': 0.045,
        'Random (uniform)': 1.0 / voynich['n_unique_atoms'],
    }
    
    print(f"\n  Voynich IC: {voynich['atom_ic']:.4f}")
    print(f"\n  Reference IC values:")
    for name, ic in ic_references.items():
        distance = abs(voynich['atom_ic'] - ic)
        print(f"    {name:<35} IC={ic:.4f}  distance={distance:.4f}")
    
    # Find closest match
    closest = min(ic_references.items(), key=lambda x: abs(x[1] - voynich['atom_ic']))
    print(f"\n  Closest match: {closest[0]} (IC={closest[1]:.4f})")
    
    if voynich['atom_ic'] > 0.06:
        print("  ASSESSMENT: IC is consistent with natural language or simple substitution")
        print("  This does NOT rule out cipher, but rules out polyalphabetic systems")
    elif voynich['atom_ic'] > 0.045:
        print("  ASSESSMENT: IC is between natural language and polyalphabetic cipher")
        print("  Could indicate a mild polyalphabetic system or specialized vocabulary")
    else:
        print("  ASSESSMENT: IC is consistent with polyalphabetic cipher or random text")

    # ── Test 2: Homophonic substitution simulation ───────────────────────
    print(f"\n{'='*75}")
    print("TEST 2: HOMOPHONIC SUBSTITUTION CIPHER SIMULATION")
    print(f"{'='*75}")
    print(f"Testing if a homophonic cipher over Latin (using {voynich['n_unique_atoms']} symbols)")
    print("can produce similar entropy and IC values.")
    
    homo_entropies = []
    homo_ics = []
    homo_ttrs = []
    
    for i in range(N_SIMULATIONS):
        rng = random.Random(RANDOM_SEED + i)
        cipher_text = generate_homophonic_cipher(
            LATIN_LETTER_FREQ, voynich['n_unique_atoms'],
            voynich['n_atoms'], rng
        )
        freq = Counter(cipher_text)
        homo_entropies.append(compute_entropy(freq))
        homo_ics.append(compute_index_of_coincidence(freq))
        homo_ttrs.append(len(freq) / len(cipher_text))
    
    homo_ent_mean = sum(homo_entropies) / len(homo_entropies)
    homo_ic_mean = sum(homo_ics) / len(homo_ics)
    homo_ttr_mean = sum(homo_ttrs) / len(homo_ttrs)
    
    p_ent_homo = sum(1 for e in homo_entropies
                     if abs(e - voynich['atom_entropy']) < 0.1) / N_SIMULATIONS
    p_ic_homo = sum(1 for ic in homo_ics
                    if abs(ic - voynich['atom_ic']) < 0.005) / N_SIMULATIONS
    
    print(f"\n  {'Metric':<25} {'Voynich':>10} {'Homophonic':>12}")
    print(f"  {'-'*50}")
    print(f"  {'Entropy (bits)':<25} {voynich['atom_entropy']:>10.3f} {homo_ent_mean:>12.3f}")
    print(f"  {'IC':<25} {voynich['atom_ic']:>10.4f} {homo_ic_mean:>12.4f}")
    print(f"  {'TTR':<25} {voynich['atom_ttr']:>10.4f} {homo_ttr_mean:>12.4f}")
    
    print(f"\n  p(entropy match): {p_ent_homo:.3f}")
    print(f"  p(IC match): {p_ic_homo:.3f}")
    
    if p_ent_homo > 0.05 and p_ic_homo > 0.05:
        print("  ASSESSMENT: Homophonic cipher CAN produce similar statistical properties")
        print("  This means the cipher hypothesis CANNOT be dismissed on these grounds alone")
    else:
        print("  ASSESSMENT: Homophonic cipher does NOT match Voynich properties well")
        print("  The Voynich shows distinct statistical signatures from homophonic ciphers")

    # ── Test 3: Polyalphabetic cipher simulation ─────────────────────────
    print(f"\n{'='*75}")
    print("TEST 3: POLYALPHABETIC CIPHER SIMULATION")
    print(f"{'='*75}")
    
    for n_alpha in [3, 5, 7]:
        poly_ics = []
        for i in range(N_SIMULATIONS):
            rng = random.Random(RANDOM_SEED + i + n_alpha * 10000)
            cipher_text = generate_polyalphabetic_cipher(
                LATIN_LETTER_FREQ, n_alpha, voynich['n_atoms'], rng
            )
            freq = Counter(cipher_text)
            poly_ics.append(compute_index_of_coincidence(freq))
        
        poly_ic_mean = sum(poly_ics) / len(poly_ics)
        p_ic_poly = sum(1 for ic in poly_ics
                        if abs(ic - voynich['atom_ic']) < 0.005) / N_SIMULATIONS
        
        print(f"  {n_alpha} alphabets: IC mean = {poly_ic_mean:.4f}, "
              f"p(match Voynich IC) = {p_ic_poly:.3f}")

    # ── Test 4: Word-level analysis (cipher vs natural language) ─────────
    print(f"\n{'='*75}")
    print("TEST 4: WORD-LEVEL TYPE/TOKEN RATIO")
    print(f"{'='*75}")
    print("Natural languages have TTR that follows Heaps' law.")
    print("Ciphers have different TTR depending on their type.")
    
    # Heaps' law prediction for natural language
    # V = K * N^beta, where beta ~ 0.4-0.6 for natural languages
    for beta in [0.4, 0.5, 0.6]:
        K = voynich['word_types'] / (voynich['word_tokens'] ** beta)
        predicted_types = K * (voynich['word_tokens'] ** beta)
        print(f"  Heaps' law (beta={beta}): predicted {predicted_types:.0f} types "
              f"(actual: {voynich['word_types']})")
    
    # Compute best-fit beta
    if voynich['word_tokens'] > 0 and voynich['word_types'] > 0:
        # V/N = K * N^(beta-1), so log(V/N) = log(K) + (beta-1)*log(N)
        # Simple approximation: beta = log(V) / log(N)
        best_beta = math.log(voynich['word_types']) / math.log(voynich['word_tokens'])
        print(f"\n  Best-fit Heaps beta: {best_beta:.3f}")
        if 0.35 <= best_beta <= 0.65:
            print("  ASSESSMENT: TTR is consistent with natural language (beta 0.4-0.6)")
        elif best_beta > 0.65:
            print("  ASSESSMENT: TTR is HIGH -- more word diversity than typical language")
            print("  This could indicate a coding system with many unique symbols")
        else:
            print("  ASSESSMENT: TTR is LOW -- less word diversity than typical language")
            print("  This could indicate constrained vocabulary (database/formulary)")
    
    # ── Test 5: First/last position distributions ────────────────────────
    print(f"\n{'='*75}")
    print("TEST 5: POSITIONAL GLYPH DISTRIBUTIONS")
    print(f"{'='*75}")
    print("Natural languages show different distributions in word-initial,")
    print("word-medial, and word-final positions. Simple substitution preserves")
    print("these positional biases; polyalphabetic ciphers flatten them.")
    
    corpus = dl.load_corpus()
    folio_words = dl.corpus_to_folio_words(corpus)
    
    first_atoms = []
    last_atoms = []
    
    for folio, words in folio_words.items():
        if not any(folio.startswith(p) for p in ['f87', 'f88', 'f89', 'f9', 'f10', 'f11']):
            continue
        for word in words:
            atoms = dl.parse_atoms(word)
            if atoms:
                first_atoms.append(atoms[0])
                last_atoms.append(atoms[-1])
    
    first_dist = Counter(first_atoms)
    last_dist = Counter(last_atoms)
    
    first_entropy = compute_entropy(first_dist)
    last_entropy = compute_entropy(last_dist)
    
    print(f"\n  First-atom entropy:  {first_entropy:.3f} bits ({len(first_dist)} unique)")
    print(f"  Last-atom entropy:   {last_entropy:.3f} bits ({len(last_dist)} unique)")
    print(f"  Overall atom entropy: {voynich['atom_entropy']:.3f} bits")
    
    entropy_ratio = last_entropy / first_entropy if first_entropy > 0 else 0
    print(f"  Last/First entropy ratio: {entropy_ratio:.3f}")
    
    if entropy_ratio < 0.7:
        print("  ASSESSMENT: Strong positional bias -- last position is more constrained")
        print("  This is consistent with an inflectional system (suffixes)")
        print("  Simple substitution would preserve this; polyalphabetic would not")
    elif entropy_ratio > 1.3:
        print("  ASSESSMENT: Last position has MORE entropy than first")
        print("  This is unusual for natural language")
    else:
        print("  ASSESSMENT: Moderate positional bias, consistent with natural language")

    # ── Overall assessment ───────────────────────────────────────────────
    print(f"\n{'='*75}")
    print("OVERALL CIPHER HYPOTHESIS ASSESSMENT")
    print(f"{'='*75}")
    
    findings = []
    
    # IC assessment
    if voynich['atom_ic'] > 0.055:
        findings.append(("IC suggests natural language or simple substitution", "AGAINST polyalphabetic"))
    else:
        findings.append(("IC is consistent with polyalphabetic cipher", "FOR cipher"))
    
    # Homophonic match
    if p_ent_homo > 0.05 and p_ic_homo > 0.05:
        findings.append(("Homophonic cipher CAN match observed statistics", "FOR cipher"))
    else:
        findings.append(("Homophonic cipher does NOT match well", "AGAINST cipher"))
    
    # Positional bias
    if entropy_ratio < 0.8:
        findings.append(("Strong suffix constraint (positional bias)", "FOR natural language/database"))
    else:
        findings.append(("Weak positional bias", "NEUTRAL"))
    
    # Word TTR
    if voynich['word_ttr'] < 0.3:
        findings.append(("Low word TTR -- constrained vocabulary", "FOR database/formulary"))
    elif voynich['word_ttr'] > 0.5:
        findings.append(("High word TTR -- diverse vocabulary", "FOR natural language or cipher"))
    else:
        findings.append(("Moderate word TTR", "NEUTRAL"))
    
    for finding, assessment in findings:
        print(f"  {assessment:<30} {finding}")
    
    cipher_for = sum(1 for _, a in findings if "FOR cipher" in a)
    cipher_against = sum(1 for _, a in findings if "AGAINST" in a and "cipher" in a.lower())
    
    print(f"\n  Evidence for cipher: {cipher_for}/{len(findings)}")
    print(f"  Evidence against cipher: {cipher_against}/{len(findings)}")
    print(f"\n  VERDICT: ", end="")
    
    if cipher_for > cipher_against:
        print("Cipher hypothesis CANNOT be dismissed")
        print("  The observed patterns are compatible with certain cipher types.")
        print("  Further analysis (e.g., Sukhotin's algorithm, vowel/consonant")
        print("  separation) would be needed to distinguish cipher from database.")
    elif cipher_against > cipher_for:
        print("Cipher hypothesis is UNLIKELY but not impossible")
        print("  The positional constraints and structural patterns are more")
        print("  consistent with a natural notation system than a cipher.")
    else:
        print("INCONCLUSIVE -- both hypotheses remain viable")
        print("  The evidence does not clearly favor either interpretation.")

    # Save results
    ensure_output_dirs()
    save = {
        'voynich_stats': {k: v for k, v in voynich.items() if k != 'atom_freq'},
        'ic_references': ic_references,
        'homophonic_comparison': {
            'entropy_mean': homo_ent_mean,
            'ic_mean': homo_ic_mean,
            'p_entropy_match': p_ent_homo,
            'p_ic_match': p_ic_homo,
        },
        'positional_analysis': {
            'first_atom_entropy': first_entropy,
            'last_atom_entropy': last_entropy,
            'entropy_ratio': entropy_ratio,
        },
        'findings': [{'finding': f, 'assessment': a} for f, a in findings],
    }
    out_path = os.path.join(PATHS['output_validation'], 'cipher_hypothesis_results.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(save, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to: {out_path}")

    return save


if __name__ == '__main__':
    run_cipher_hypothesis()
