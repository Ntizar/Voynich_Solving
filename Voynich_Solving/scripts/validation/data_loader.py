"""
Voynich Validation Framework -- Unified Data Loader
====================================================
Single source of truth for loading all project data.
Every validation script imports from here instead of re-parsing files.

Usage:
    from scripts.validation.data_loader import load_all, load_corpus, load_recipes, ...
"""
import csv
import os
import re
from collections import defaultdict

from scripts.validation.config import PATHS, ATOM_PATTERN, FINAL_ATOMS


# ── Generic CSV loader ───────────────────────────────────────────────────────
def _load_csv(path):
    """Load a CSV file as a list of dicts."""
    rows = []
    with open(path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)
    return rows


# ── Corpus parser (STA1 / EVA IVTFF format) ─────────────────────────────────
def load_corpus(path=None):
    """Parse an IVTFF corpus file into structured records.

    Returns:
        list of dicts with keys: folio, line, paragraph, words (list of str)
    """
    path = path or PATHS["corpus_sta"]
    records = []
    header_re = re.compile(r'^<(f\d+[rv]\d?)\.([\d]+),([^>]+)>')

    with open(path, encoding='utf-8') as f:
        for raw_line in f:
            raw_line = raw_line.strip()
            if not raw_line or raw_line.startswith('#'):
                continue
            m = header_re.match(raw_line)
            if not m:
                continue
            folio = m.group(1)
            line_num = int(m.group(2))
            para = m.group(3)
            text = raw_line[m.end():].strip()
            # Split on . (word separator) and <-> (block separator)
            text = text.replace('<->', '.')
            words = [w.strip() for w in text.split('.') if w.strip()]
            records.append({
                'folio': folio,
                'line': line_num,
                'paragraph': para,
                'words': words,
            })
    return records


def corpus_to_folio_words(corpus_records):
    """Group corpus records into {folio: [list of all words]}."""
    folio_words = defaultdict(list)
    for rec in corpus_records:
        folio_words[rec['folio']].extend(rec['words'])
    return dict(folio_words)


# ── Atom / stem parsing ─────────────────────────────────────────────────────
def parse_atoms(word):
    """Split a Voynichese word into its STA1 atoms."""
    return ATOM_PATTERN.findall(word)


def split_stem_suffix(word):
    """Split a word into (stem, final_atom).

    The final atom is the last recognized atom if it belongs to FINAL_ATOMS.
    Returns (stem_string, suffix_string) or (word, None) if no suffix found.
    """
    atoms = parse_atoms(word)
    if not atoms:
        return word, None
    if atoms[-1] in FINAL_ATOMS:
        suffix = atoms[-1]
        stem = ''.join(atoms[:-1])
        return stem, suffix
    return ''.join(atoms), None


# ── Recipe data ──────────────────────────────────────────────────────────────
def load_recipes_main(path=None):
    """Load the master recipe table (50 recipes with ingredient counts/lists)."""
    return _load_csv(path or PATHS["recipes_main"])


def load_recipes_flat(path=None):
    """Load the flat ingredient table (613 rows: Receta, Ingrediente, Categoria, Normalizado)."""
    return _load_csv(path or PATHS["recipes_flat"])


def build_recipe_ingredients(flat_rows=None):
    """Build {recipe_name: set(normalized_ingredients)} from flat table."""
    if flat_rows is None:
        flat_rows = load_recipes_flat()
    ri = defaultdict(set)
    for row in flat_rows:
        ri[row['Receta']].add(row['Ingrediente_Normalizado'])
    return dict(ri)


def build_recipe_ingredient_categories(flat_rows=None):
    """Build {recipe_name: {ingredient: category}} from flat table."""
    if flat_rows is None:
        flat_rows = load_recipes_flat()
    ric = defaultdict(dict)
    for row in flat_rows:
        ric[row['Receta']][row['Ingrediente_Normalizado']] = row['Categoria']
    return dict(ric)


# ── Folio-stem data ──────────────────────────────────────────────────────────
def load_recipe_folio_stems(path=None):
    """Load the 8232-row folio-stem table."""
    return _load_csv(path or PATHS["recipe_folio_stems"])


def build_folio_stems(stem_rows=None):
    """Build {folio: set(stems)} from the folio-stem table."""
    if stem_rows is None:
        stem_rows = load_recipe_folio_stems()
    fs = defaultdict(set)
    for row in stem_rows:
        fs[row['Folio']].add(row['Stem'])
    return dict(fs)


def build_stem_folios(stem_rows=None):
    """Build {stem: set(folios)} from the folio-stem table."""
    if stem_rows is None:
        stem_rows = load_recipe_folio_stems()
    sf = defaultdict(set)
    for row in stem_rows:
        sf[row['Stem']].add(row['Folio'])
    return dict(sf)


# ── Identifications ──────────────────────────────────────────────────────────
def load_identifications(path=None):
    """Load the v7 identification table (75 entries)."""
    return _load_csv(path or PATHS["identifications_v7"])


def build_ident_map(ident_rows=None):
    """Build {stem: ingredient} from the identification table."""
    if ident_rows is None:
        ident_rows = load_identifications()
    return {row['Stem']: row['Ingredient'] for row in ident_rows}


def build_ident_ingredients(ident_rows=None):
    """Get set of all identified ingredients (excluding FUNCTION_WORD)."""
    if ident_rows is None:
        ident_rows = load_identifications()
    ings = set()
    for row in ident_rows:
        if row['Ingredient'] != 'FUNCTION_WORD':
            for sub in row['Ingredient'].split('|'):
                ings.add(sub.strip())
    return ings


# ── Matching results ─────────────────────────────────────────────────────────
def load_matching_v7(path=None):
    """Load the best-match-per-folio results."""
    return _load_csv(path or PATHS["matching_v7"])


def load_expanded_matching_v7(path=None):
    """Load the full 48x50 matching matrix."""
    return _load_csv(path or PATHS["expanded_matching_v7"])


# ── Other data ───────────────────────────────────────────────────────────────
def load_mega_index(path=None):
    """Load the 217-stem master index."""
    return _load_csv(path or PATHS["mega_index"])


def load_recipe_profiles(path=None):
    """Load the per-folio recipe profiles."""
    return _load_csv(path or PATHS["recipe_profiles"])


def load_consistency(path=None):
    """Load the cross-consistency test results."""
    return _load_csv(path or PATHS["consistency"])


# ── Convenience: load everything at once ─────────────────────────────────────
def load_all():
    """Load all key datasets into a single dict.

    Returns dict with keys:
        recipes_main, recipes_flat, recipe_ingredients,
        folio_stem_rows, folio_stems, stem_folios,
        identifications, ident_map, ident_ingredients,
        mega_index, recipe_profiles, matching_v7, expanded_matching_v7
    """
    recipes_flat = load_recipes_flat()
    folio_stem_rows = load_recipe_folio_stems()
    ident_rows = load_identifications()

    return {
        'recipes_main': load_recipes_main(),
        'recipes_flat': recipes_flat,
        'recipe_ingredients': build_recipe_ingredients(recipes_flat),
        'recipe_ingredient_categories': build_recipe_ingredient_categories(recipes_flat),
        'folio_stem_rows': folio_stem_rows,
        'folio_stems': build_folio_stems(folio_stem_rows),
        'stem_folios': build_stem_folios(folio_stem_rows),
        'identifications': ident_rows,
        'ident_map': build_ident_map(ident_rows),
        'ident_ingredients': build_ident_ingredients(ident_rows),
        'mega_index': load_mega_index(),
        'recipe_profiles': load_recipe_profiles(),
        'matching_v7': load_matching_v7(),
        'expanded_matching_v7': load_expanded_matching_v7(),
    }
