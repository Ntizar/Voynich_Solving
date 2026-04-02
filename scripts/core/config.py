"""
Voynich Validation Framework -- Central Configuration
=====================================================
Every script in the validation framework reads from here.
If a source file hash changes, the pipeline detects it and halts.

Usage:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from scripts.core.config import CONFIG
"""
import os
import hashlib

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))

PATHS = {
    # Primary corpus
    "corpus_sta": os.path.join(ROOT, "voynich_sta.txt"),
    "corpus_eva": os.path.join(ROOT, "zenodo_voynich", "corpus", "voynich_eva.txt"),
    # Historical recipes
    "recipes_main": os.path.join(ROOT, "recetas_historicas_medievales.csv"),
    "recipes_flat": os.path.join(ROOT, "recetas_historicas_ingredientes_flat.csv"),
    # Stem & folio data
    "mega_index": os.path.join(ROOT, "voynich_mega_indice_conexiones.csv"),
    "recipe_folio_stems": os.path.join(ROOT, "voynich_all_recipe_folio_stems.csv"),
    "recipe_profiles": os.path.join(ROOT, "voynich_todas_recetas_perfil.csv"),
    # Identifications (versioned)
    "identifications_v7": os.path.join(ROOT, "voynich_unified_identifications_v7.csv"),
    # Matching results
    "matching_v7": os.path.join(ROOT, "voynich_matching_v7.csv"),
    "expanded_matching_v7": os.path.join(ROOT, "voynich_expanded_matching_v7.csv"),
    # Cross-checks
    "consistency": os.path.join(ROOT, "voynich_consistencia_cruzada.csv"),
    "historical_crosses": os.path.join(ROOT, "voynich_cruces_recetas_historicas.csv"),
    # Output directories
    "output_validation": os.path.join(ROOT, "output", "validation"),
    "output_splits": os.path.join(ROOT, "output", "splits"),
    "output_reports": os.path.join(ROOT, "output", "reports"),
}

# ── Reproducibility ──────────────────────────────────────────────────────────
RANDOM_SEED = 42
VERSION = "v7"
FRAMEWORK_VERSION = "0.1.0"

# ── Data integrity hashes (SHA-256, frozen at validation framework creation) ─
# These are the expected hashes. If a file changes, validation halts.
SOURCE_HASHES = {
    "corpus_sta": "81c331b7d8e76761e27d350c3b37ccfbe192848e6c8a227bcb5d40fb29259b17",
    "corpus_eva": "bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc",
    "recipes_main": "c6406ef2fcc491855b7c583b4c48d3372a0ec2142eb66e5314b03d87eb5c6ae3",
    "recipes_flat": "92e09259b6aa1a39b67fa8c1fd4d87097a334715c254d0b27bc440983963abb3",
    "mega_index": "58f40d3d88d533c80ea35aa0c9556365f9885af649fa631810b4d120a61f9793",
    "recipe_folio_stems": "400d35f4bb23f5f836d41ca088bd3208e40a028235fc853d5f96cdb25111867a",
    "identifications_v7": "6c6cf1272add2d87feab92086dfd830e7e3782ea72f254ec9e980d46c0a17ca4",
    "matching_v7": "0bdff75aa3363556e322916771d013a6629acd35c788f210d6cc1cf6f609af43",
    "expanded_matching_v7": "aaed68397cca9b97dfd5d99742e4a808cbf156871cb6ddad0ea59b53c60c86cb",
    "recipe_profiles": "ee5bbb7645847f375447abedf1845d4c5eb3f0dd7437b98120adcbd18b4878dd",
    "consistency": "3d35bce57648eb16eaf1d3ddd405cc84d5b235b570ef6e6962c4f7b156a9fd92",
    "historical_crosses": "8707d04cf5e81683628eafb8244d6af133deb9cb9a070d8e0b8fa7ff0066ab90",
}

# ── Blind split parameters ───────────────────────────────────────────────────
SPLIT = {
    "test_folio_fraction": 0.20,   # 20% of recipe folios held out
    "test_recipe_fraction": 0.20,  # 20% of historical recipes held out
    "seed": RANDOM_SEED,
}

# ── Validation thresholds ────────────────────────────────────────────────────
THRESHOLDS = {
    # A hypothesis needs at least this many independent evidence lines to
    # rise above "hypothesis" status
    "min_evidence_lines": 2,
    # Minimum margin (pp) between best match and runner-up to be "robust"
    "min_margin_pp": 10.0,
    # Bootstrap stability: min fraction of bootstrap runs where the top
    # hypothesis stays the same
    "min_stability": 0.70,
    # Maximum false-positive rate on negative controls
    "max_fp_rate_negatives": 0.10,
    # F1 floor: if the system scores below this on blind test, reject
    "min_f1_blind_test": 0.0,  # will be set after baselines are computed
    # FDR threshold for multiple-comparison correction
    "fdr_alpha": 0.05,
}

# ── STA1 atom pattern (from METHODOLOGY.md) ─────────────────────────────────
import re
ATOM_PATTERN = re.compile(
    r'(A[1-3]|B[1-4]|C[1-2]|D1|E[1-2]|F[1-3]|G[1-3]|H1|'
    r'J1|K[1ab2]|L1|N1|P[12]|Q[12]|T[12]|U[12]|'
    r'Aa|Ba|Cm|Xb|Ab|Bd|Cl)'
)

FINAL_ATOMS = {'A1','A2','A3','B1','B2','B3','B4','C1','C2',
               'E1','E2','F1','F2','F3','G1','G3','H1'}

# ── Hash verification function ───────────────────────────────────────────────
def verify_source_hashes(keys=None, strict=True):
    """Check that source files match their frozen hashes.
    
    Args:
        keys: list of SOURCE_HASHES keys to check, or None for all.
        strict: if True, raise on mismatch; if False, return list of failures.
    
    Returns:
        List of (key, expected, actual) tuples for failures. Empty = all OK.
    """
    failures = []
    check = keys or list(SOURCE_HASHES.keys())
    for key in check:
        path = PATHS.get(key)
        expected = SOURCE_HASHES.get(key)
        if not path or not expected:
            continue
        if not os.path.exists(path):
            failures.append((key, expected, "FILE_MISSING"))
            continue
        actual = hashlib.sha256(open(path, "rb").read()).hexdigest()
        if actual != expected:
            failures.append((key, expected, actual))
    
    if strict and failures:
        msg = "SOURCE FILE INTEGRITY CHECK FAILED:\n"
        for key, exp, act in failures:
            msg += f"  {key}: expected {exp[:16]}... got {act[:16]}...\n"
        msg += "Pipeline halted. Data has changed since validation framework was frozen."
        raise RuntimeError(msg)
    
    return failures


def ensure_output_dirs():
    """Create output directories if they don't exist."""
    for key in ("output_validation", "output_splits", "output_reports"):
        os.makedirs(PATHS[key], exist_ok=True)


# ── Convenience: full config dict ────────────────────────────────────────────
CONFIG = {
    "root": ROOT,
    "paths": PATHS,
    "seed": RANDOM_SEED,
    "version": VERSION,
    "framework_version": FRAMEWORK_VERSION,
    "source_hashes": SOURCE_HASHES,
    "split": SPLIT,
    "thresholds": THRESHOLDS,
    "atom_pattern": ATOM_PATTERN,
    "final_atoms": FINAL_ATOMS,
}
