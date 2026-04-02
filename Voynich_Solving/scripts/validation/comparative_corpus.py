"""
Voynich Validation Framework -- Comparative Corpus Analysis
============================================================
Tests whether the structural patterns claimed as evidence for a
"database-like" structure in the Voynich manuscript are genuinely
anomalous, or merely typical of medieval medical/pharmaceutical texts.

Addresses the critique:
    "Many medieval manuscripts present columnar dispositions for
    aesthetic reasons without implying relational schemas."

Tests:
    1. Suffix alignment rate: Is 27% vertical suffix alignment anomalous?
       Compare against synthetic Latin medical texts with known structure.
    2. Stem reuse with suffix change: Is 46.9% stem reuse anomalous?
       Compare against Latin medical vocabulary patterns.
    3. Entropy of suffix channel: Is H=1.246 bits anomalous?
       Compare against suffix entropy in Latin, Castilian, and random text.
    4. Cross-section schema test: Do different sections truly use different
       "schemas", or is this just topical variation?

Run:
    python -m scripts.validation.comparative_corpus
"""
import sys
import os
import math
import random
import json
from collections import Counter, defaultdict

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.validation.config import PATHS, RANDOM_SEED, FINAL_ATOMS, ensure_output_dirs
from scripts.validation import data_loader as dl

sys.stdout.reconfigure(encoding='utf-8')

N_SIMULATIONS = 1000


# ── Latin medical vocabulary (synthetic control corpus) ──────────────────────
# These are real Latin pharmaceutical terms from Antidotarium Nicolai,
# Circa Instans, and Tacuinum Sanitatis. We use them to simulate what
# a "known medical text" looks like when analyzed with the same tools.

LATIN_MEDICAL_STEMS = {
    # Ingredient names (simulating "stems")
    'myrrh': ['myrrha', 'myrrhae', 'myrrham', 'myrrhas'],
    'croc': ['crocus', 'croci', 'crocum', 'crocos'],
    'piper': ['piper', 'piperis', 'piperi', 'pipere'],
    'zingiber': ['zingiber', 'zingiberis', 'zingiberi', 'zingibere'],
    'cinnamom': ['cinnamomum', 'cinnamomi', 'cinnamomo', 'cinnamomis'],
    'castor': ['castoreum', 'castorei', 'castoreo'],
    'gentian': ['gentiana', 'gentianae', 'gentianam'],
    'cardamom': ['cardamomum', 'cardamomi', 'cardamomo'],
    'galban': ['galbanum', 'galbani', 'galbano'],
    'opopanac': ['opopanax', 'opopanacis', 'opopanaci'],
    'bdelli': ['bdellium', 'bdellii', 'bdellio'],
    'rosa': ['rosa', 'rosae', 'rosam', 'rosarum'],
    'mel': ['mel', 'mellis', 'melle', 'melli'],
    'sacchar': ['saccharum', 'sacchari', 'saccharo'],
    'petrosel': ['petroselinum', 'petroselini', 'petroselino'],
    'amom': ['amomum', 'amomi', 'amomo'],
    'styrax': ['styrax', 'styracis', 'styraci'],
    # Action/process words (simulating different "schema")
    'recip': ['recipe', 'recipis', 'recipiat', 'recipiunt'],
    'misc': ['misce', 'misces', 'misceat', 'miscentur'],
    'coque': ['coque', 'coques', 'coquat', 'coquantur'],
    'tere': ['tere', 'teris', 'terat', 'terunt'],
    'adde': ['adde', 'addis', 'addat', 'addunt'],
    'fac': ['fac', 'facis', 'faciat', 'faciunt'],
    # Measurement words (simulating structural words)
    'drachm': ['drachma', 'drachmae', 'drachmas', 'drachmarum'],
    'unci': ['uncia', 'unciae', 'uncias', 'unciarum'],
    'libr': ['libra', 'librae', 'libras', 'librarum'],
    'parti': ['partes', 'partium', 'partibus', 'partem'],
}

# Latin case endings (simulating suffixes)
LATIN_SUFFIXES = ['a', 'ae', 'am', 'as', 'arum', 'is', 'um', 'i', 'o',
                  'e', 'es', 'ium', 'ibus', 'us', 'em', 'orum']


def generate_synthetic_latin_recipe(recipe_size, rng):
    """Generate a synthetic Latin recipe text with realistic structure.
    
    Returns list of (stem, suffix) tuples, simulating what a real
    medieval pharmaceutical recipe looks like when decomposed.
    """
    words = []
    # Recipe header: "Recipe..." 
    stem_names = list(LATIN_MEDICAL_STEMS.keys())
    
    # 30% structural words, 50% ingredient names, 20% action words
    structural_stems = [s for s in stem_names if s in {'drachm', 'unci', 'libr', 'parti'}]
    ingredient_stems = [s for s in stem_names if s not in {'drachm', 'unci', 'libr', 'parti', 
                                                            'recip', 'misc', 'coque', 'tere', 'adde', 'fac'}]
    action_stems = [s for s in stem_names if s in {'recip', 'misc', 'coque', 'tere', 'adde', 'fac'}]
    
    for _ in range(recipe_size):
        r = rng.random()
        if r < 0.30:
            stem = rng.choice(structural_stems)
        elif r < 0.80:
            stem = rng.choice(ingredient_stems)
        else:
            stem = rng.choice(action_stems)
        
        forms = LATIN_MEDICAL_STEMS[stem]
        word = rng.choice(forms)
        
        # Extract suffix (last 1-4 chars that match a Latin ending)
        suffix = None
        for suf in sorted(LATIN_SUFFIXES, key=len, reverse=True):
            if word.endswith(suf) and len(word) > len(suf):
                suffix = suf
                break
        if suffix is None:
            suffix = word[-1] if len(word) > 1 else ''
        stem_part = word[:len(word)-len(suffix)] if suffix else word
        
        words.append((stem_part, suffix))
    
    return words


def compute_suffix_entropy(suffixes):
    """Compute Shannon entropy of suffix distribution."""
    total = len(suffixes)
    if total == 0:
        return 0.0
    counts = Counter(suffixes)
    entropy = 0.0
    for count in counts.values():
        p = count / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def compute_vertical_alignment(texts, column_width=5):
    """Compute vertical suffix alignment rate.
    
    For columnar text laid out in rows of column_width words,
    what fraction of same-column positions share the same suffix?
    """
    if not texts:
        return 0.0
    
    # Lay out words in columns
    columns = defaultdict(list)
    for i, (stem, suffix) in enumerate(texts):
        col = i % column_width
        columns[col].append(suffix)
    
    # For each column, compute alignment (fraction of most common suffix)
    alignments = []
    for col, suffixes in columns.items():
        if len(suffixes) < 2:
            continue
        counts = Counter(suffixes)
        most_common_count = counts.most_common(1)[0][1]
        alignment = most_common_count / len(suffixes)
        alignments.append(alignment)
    
    return sum(alignments) / len(alignments) if alignments else 0.0


def compute_stem_reuse_rate(texts):
    """Compute stem reuse with different suffixes.
    
    Of stems that appear more than once, what fraction appear with
    different suffixes?
    """
    stem_suffixes = defaultdict(set)
    for stem, suffix in texts:
        stem_suffixes[stem].add(suffix)
    
    multi_occurrence = {s: sfxs for s, sfxs in stem_suffixes.items() if len(sfxs) > 0}
    if not multi_occurrence:
        return 0.0
    
    reuse = sum(1 for sfxs in multi_occurrence.values() if len(sfxs) > 1)
    return reuse / len(multi_occurrence) * 100


# ── Voynich structural properties (from the manuscript) ──────────────────────
def compute_voynich_properties(data):
    """Compute the claimed structural properties from the Voynich corpus."""
    corpus = dl.load_corpus()
    folio_words = dl.corpus_to_folio_words(corpus)
    
    # Parse all words into (stem, suffix) pairs
    all_pairs = []
    folio_pairs = defaultdict(list)
    for folio, words in folio_words.items():
        for word in words:
            stem, suffix = dl.split_stem_suffix(word)
            if suffix:
                all_pairs.append((stem, suffix))
                folio_pairs[folio].append((stem, suffix))
    
    # Only recipe folios (f87r - f116v)
    recipe_folios = [f for f in folio_pairs.keys()
                     if any(f.startswith(p) for p in ['f87', 'f88', 'f89', 'f9',
                                                       'f10', 'f11'])]
    
    recipe_pairs = []
    for f in recipe_folios:
        recipe_pairs.extend(folio_pairs[f])
    
    suffix_entropy = compute_suffix_entropy([s for _, s in recipe_pairs])
    vertical_alignment = compute_vertical_alignment(recipe_pairs, column_width=5)
    stem_reuse = compute_stem_reuse_rate(recipe_pairs)
    
    # Suffix distribution
    suffix_dist = Counter(s for _, s in recipe_pairs)
    n_unique_suffixes = len(suffix_dist)
    n_unique_stems = len(set(s for s, _ in recipe_pairs))
    
    return {
        'suffix_entropy': suffix_entropy,
        'vertical_alignment': vertical_alignment * 100,
        'stem_reuse_rate': stem_reuse,
        'n_pairs': len(recipe_pairs),
        'n_unique_suffixes': n_unique_suffixes,
        'n_unique_stems': n_unique_stems,
        'suffix_distribution': dict(suffix_dist.most_common(20)),
    }


# ── Main comparative analysis ────────────────────────────────────────────────
def run_comparative_corpus():
    print("=" * 75)
    print("VOYNICH COMPARATIVE CORPUS ANALYSIS")
    print("Testing structural claims against control texts")
    print("=" * 75)

    # Compute Voynich properties
    print("\n--- Computing Voynich manuscript properties ---")
    data = dl.load_all()
    voynich_props = compute_voynich_properties(data)
    
    print(f"  Suffix entropy (H):       {voynich_props['suffix_entropy']:.3f} bits")
    print(f"  Vertical alignment:       {voynich_props['vertical_alignment']:.1f}%")
    print(f"  Stem reuse rate:          {voynich_props['stem_reuse_rate']:.1f}%")
    print(f"  Total stem-suffix pairs:  {voynich_props['n_pairs']}")
    print(f"  Unique suffixes:          {voynich_props['n_unique_suffixes']}")
    print(f"  Unique stems:             {voynich_props['n_unique_stems']}")
    print(f"  Top suffixes: {voynich_props['suffix_distribution']}")

    # ── Test 1: Suffix entropy comparison ────────────────────────────────
    print(f"\n{'='*75}")
    print("TEST 1: SUFFIX ENTROPY COMPARISON")
    print(f"{'='*75}")
    print("Claim: H = 1.246 bits is unusually low, suggesting a structured system")
    print("Null: Latin medical texts have similar or lower entropy")

    rng = random.Random(RANDOM_SEED)
    latin_entropies = []
    latin_alignments = []
    latin_reuse_rates = []
    
    for i in range(N_SIMULATIONS):
        sim_rng = random.Random(RANDOM_SEED + i)
        # Generate a synthetic Latin recipe corpus of similar size
        text = generate_synthetic_latin_recipe(voynich_props['n_pairs'], sim_rng)
        
        entropy = compute_suffix_entropy([s for _, s in text])
        alignment = compute_vertical_alignment(text, column_width=5) * 100
        reuse = compute_stem_reuse_rate(text)
        
        latin_entropies.append(entropy)
        latin_alignments.append(alignment)
        latin_reuse_rates.append(reuse)

    # Entropy comparison
    latin_ent_mean = sum(latin_entropies) / len(latin_entropies)
    latin_ent_std = (sum((e - latin_ent_mean)**2 for e in latin_entropies) / len(latin_entropies))**0.5
    p_value_entropy = sum(1 for e in latin_entropies if e <= voynich_props['suffix_entropy']) / N_SIMULATIONS
    
    print(f"\n  Voynich suffix entropy: {voynich_props['suffix_entropy']:.3f} bits")
    print(f"  Latin control mean:     {latin_ent_mean:.3f} +/- {latin_ent_std:.3f} bits")
    print(f"  Latin control range:    [{min(latin_entropies):.3f}, {max(latin_entropies):.3f}]")
    print(f"  p-value (Voynich <= Latin): {p_value_entropy:.4f}")
    
    if p_value_entropy < 0.05:
        print("  RESULT: Voynich suffix entropy is significantly LOWER than Latin controls")
        print("          This supports a more structured/constrained suffix system")
    else:
        print("  RESULT: Voynich suffix entropy is NOT significantly different from Latin")
        print("          The pattern is explainable by normal medical vocabulary")

    # ── Test 2: Vertical alignment comparison ────────────────────────────
    print(f"\n{'='*75}")
    print("TEST 2: VERTICAL SUFFIX ALIGNMENT COMPARISON")
    print(f"{'='*75}")
    print("Claim: 27% alignment is anomalously high")
    print("Null: Latin texts laid out in columns would show similar alignment")

    latin_align_mean = sum(latin_alignments) / len(latin_alignments)
    latin_align_std = (sum((a - latin_align_mean)**2 for a in latin_alignments) / len(latin_alignments))**0.5
    p_value_align = sum(1 for a in latin_alignments if a >= voynich_props['vertical_alignment']) / N_SIMULATIONS

    print(f"\n  Voynich alignment: {voynich_props['vertical_alignment']:.1f}%")
    print(f"  Latin control mean: {latin_align_mean:.1f}% +/- {latin_align_std:.1f}%")
    print(f"  Latin control range: [{min(latin_alignments):.1f}%, {max(latin_alignments):.1f}%]")
    print(f"  p-value (Voynich >= Latin): {p_value_align:.4f}")

    if p_value_align < 0.05:
        print("  RESULT: Voynich alignment is significantly HIGHER than Latin controls")
        print("          This supports a columnar/tabular structure not found in normal text")
    else:
        print("  RESULT: Voynich alignment is NOT significantly higher than Latin controls")
        print("          Normal Latin medical texts can produce similar alignment rates")

    # ── Test 3: Stem reuse rate comparison ───────────────────────────────
    print(f"\n{'='*75}")
    print("TEST 3: STEM REUSE WITH SUFFIX CHANGE")
    print(f"{'='*75}")
    print("Claim: 46.9% stem reuse rate suggests 'foreign key' relationships")
    print("Null: Latin vocabulary naturally reuses stems with different cases")

    latin_reuse_mean = sum(latin_reuse_rates) / len(latin_reuse_rates)
    latin_reuse_std = (sum((r - latin_reuse_mean)**2 for r in latin_reuse_rates) / len(latin_reuse_rates))**0.5
    p_value_reuse = sum(1 for r in latin_reuse_rates if r >= voynich_props['stem_reuse_rate']) / N_SIMULATIONS

    print(f"\n  Voynich stem reuse: {voynich_props['stem_reuse_rate']:.1f}%")
    print(f"  Latin control mean: {latin_reuse_mean:.1f}% +/- {latin_reuse_std:.1f}%")
    print(f"  Latin control range: [{min(latin_reuse_rates):.1f}%, {max(latin_reuse_rates):.1f}%]")
    print(f"  p-value (Voynich >= Latin): {p_value_reuse:.4f}")

    if p_value_reuse < 0.05:
        print("  RESULT: Voynich stem reuse is significantly HIGHER than Latin controls")
        print("          This is consistent with a 'foreign key' or cross-reference system")
    else:
        print("  RESULT: Voynich stem reuse is NOT significantly higher")
        print("          Latin inflectional morphology naturally produces similar reuse rates")

    # ── Test 4: Random text baseline ─────────────────────────────────────
    print(f"\n{'='*75}")
    print("TEST 4: RANDOM TEXT BASELINE")
    print(f"{'='*75}")
    print("Control: How do these metrics look with purely random 'words'?")
    
    random_entropies = []
    random_alignments = []
    random_reuse_rates = []
    
    for i in range(N_SIMULATIONS):
        sim_rng = random.Random(RANDOM_SEED + i + 100000)
        # Generate random stem-suffix pairs
        random_stems = [f"S{sim_rng.randint(1, 200)}" for _ in range(voynich_props['n_pairs'])]
        random_suffixes = [sim_rng.choice(LATIN_SUFFIXES) for _ in range(voynich_props['n_pairs'])]
        pairs = list(zip(random_stems, random_suffixes))
        
        random_entropies.append(compute_suffix_entropy(random_suffixes))
        random_alignments.append(compute_vertical_alignment(pairs, column_width=5) * 100)
        random_reuse_rates.append(compute_stem_reuse_rate(pairs))
    
    rand_ent_mean = sum(random_entropies) / len(random_entropies)
    rand_align_mean = sum(random_alignments) / len(random_alignments)
    rand_reuse_mean = sum(random_reuse_rates) / len(random_reuse_rates)
    
    print(f"\n  {'Metric':<25} {'Voynich':>10} {'Latin':>10} {'Random':>10}")
    print(f"  {'-'*60}")
    print(f"  {'Suffix entropy (bits)':<25} {voynich_props['suffix_entropy']:>10.3f} "
          f"{latin_ent_mean:>10.3f} {rand_ent_mean:>10.3f}")
    print(f"  {'Vertical alignment (%)':<25} {voynich_props['vertical_alignment']:>10.1f} "
          f"{latin_align_mean:>10.1f} {rand_align_mean:>10.1f}")
    print(f"  {'Stem reuse rate (%)':<25} {voynich_props['stem_reuse_rate']:>10.1f} "
          f"{latin_reuse_mean:>10.1f} {rand_reuse_mean:>10.1f}")

    # ── Test 5: Schema variation across sections ─────────────────────────
    print(f"\n{'='*75}")
    print("TEST 5: CROSS-SECTION SCHEMA VARIATION")
    print(f"{'='*75}")
    print("Claim: Different sections use different 'schemas'")
    print("Null: Any thematic text shows suffix distribution variation across topics")

    corpus = dl.load_corpus()
    folio_words = dl.corpus_to_folio_words(corpus)
    
    # Split recipe folios into early and late
    recipe_folio_list = sorted(
        [f for f in folio_words.keys()
         if any(f.startswith(p) for p in ['f87', 'f88', 'f89', 'f9',
                                           'f10', 'f11'])],
    )
    
    mid = len(recipe_folio_list) // 2
    early_folios = recipe_folio_list[:mid]
    late_folios = recipe_folio_list[mid:]
    
    early_suffixes = []
    late_suffixes = []
    for folio in early_folios:
        for word in folio_words[folio]:
            _, suffix = dl.split_stem_suffix(word)
            if suffix:
                early_suffixes.append(suffix)
    for folio in late_folios:
        for word in folio_words[folio]:
            _, suffix = dl.split_stem_suffix(word)
            if suffix:
                late_suffixes.append(suffix)
    
    early_dist = Counter(early_suffixes)
    late_dist = Counter(late_suffixes)
    all_suffixes_set = set(early_dist.keys()) | set(late_dist.keys())
    
    # Chi-squared-like divergence
    total_early = sum(early_dist.values())
    total_late = sum(late_dist.values())
    
    kl_divergence = 0.0
    for suffix in all_suffixes_set:
        p_early = (early_dist.get(suffix, 0) + 1) / (total_early + len(all_suffixes_set))
        p_late = (late_dist.get(suffix, 0) + 1) / (total_late + len(all_suffixes_set))
        kl_divergence += p_early * math.log2(p_early / p_late)
    
    print(f"\n  Early folios ({len(early_folios)}): {total_early} suffixes")
    print(f"  Late folios ({len(late_folios)}):  {total_late} suffixes")
    print(f"  KL divergence (early||late): {kl_divergence:.4f} bits")
    
    # Compare against random splits of Latin text
    latin_kl_values = []
    for i in range(N_SIMULATIONS):
        sim_rng = random.Random(RANDOM_SEED + i + 200000)
        text = generate_synthetic_latin_recipe(total_early + total_late, sim_rng)
        suffixes = [s for _, s in text]
        mid_s = len(suffixes) // 2
        
        e_dist = Counter(suffixes[:mid_s])
        l_dist = Counter(suffixes[mid_s:])
        all_s = set(e_dist.keys()) | set(l_dist.keys())
        
        t_e = sum(e_dist.values())
        t_l = sum(l_dist.values())
        
        kl = 0.0
        for s in all_s:
            pe = (e_dist.get(s, 0) + 1) / (t_e + len(all_s))
            pl = (l_dist.get(s, 0) + 1) / (t_l + len(all_s))
            kl += pe * math.log2(pe / pl)
        latin_kl_values.append(kl)
    
    latin_kl_mean = sum(latin_kl_values) / len(latin_kl_values)
    p_value_kl = sum(1 for k in latin_kl_values if k >= kl_divergence) / N_SIMULATIONS
    
    print(f"  Latin control KL mean: {latin_kl_mean:.4f} bits")
    print(f"  p-value (Voynich >= Latin): {p_value_kl:.4f}")
    
    if p_value_kl < 0.05:
        print("  RESULT: Voynich sections show significantly MORE schema variation")
        print("          This supports the claim of different structural schemas")
    else:
        print("  RESULT: Schema variation is NOT significantly different from Latin")
        print("          Normal topical variation can explain the observed differences")

    # ── Overall assessment ───────────────────────────────────────────────
    print(f"\n{'='*75}")
    print("OVERALL COMPARATIVE CORPUS ASSESSMENT")
    print(f"{'='*75}")
    
    tests_passed = 0
    tests_total = 4
    results_summary = {}
    
    for test_name, p_val, direction in [
        ("Suffix entropy", p_value_entropy, "lower"),
        ("Vertical alignment", p_value_align, "higher"),
        ("Stem reuse rate", p_value_reuse, "higher"),
        ("Schema variation", p_value_kl, "higher"),
    ]:
        sig = "SIGNIFICANT" if p_val < 0.05 else "NOT significant"
        if p_val < 0.05:
            tests_passed += 1
        print(f"  {test_name}: p={p_val:.4f} ({sig})")
        results_summary[test_name] = {
            'p_value': p_val,
            'significant': p_val < 0.05,
            'direction': direction,
        }
    
    print(f"\n  Tests with significant anomaly: {tests_passed}/{tests_total}")
    
    if tests_passed >= 3:
        print("  VERDICT: Voynich structural patterns are genuinely anomalous")
        print("  compared to Latin medical text controls.")
    elif tests_passed >= 2:
        print("  VERDICT: MIXED -- Some patterns are anomalous, others are not.")
        print("  The structural claims need to be qualified by which specific")
        print("  properties are genuinely unusual.")
    else:
        print("  VERDICT: Voynich structural patterns are NOT clearly anomalous")
        print("  compared to medieval Latin medical controls. The observed")
        print("  patterns could arise from normal text properties.")

    # Save results
    ensure_output_dirs()
    save = {
        'voynich_properties': voynich_props,
        'latin_control_means': {
            'suffix_entropy': latin_ent_mean,
            'vertical_alignment': latin_align_mean,
            'stem_reuse_rate': latin_reuse_mean,
        },
        'random_control_means': {
            'suffix_entropy': rand_ent_mean,
            'vertical_alignment': rand_align_mean,
            'stem_reuse_rate': rand_reuse_mean,
        },
        'test_results': results_summary,
        'tests_passed': tests_passed,
        'tests_total': tests_total,
        'n_simulations': N_SIMULATIONS,
    }
    out_path = os.path.join(PATHS['output_validation'], 'comparative_corpus_results.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(save, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to: {out_path}")

    return save


if __name__ == '__main__':
    run_comparative_corpus()
