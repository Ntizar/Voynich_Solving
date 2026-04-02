"""
Voynich Validation Framework -- v8 Identification Builder
==========================================================
Builds identifications using ONLY training data (39 folios + 40 recipes)
from blind_splits.json. NO human curation, NO hardcoded stems.

This is the definitive test: if v8 (built on train-only data) beats
baselines when evaluated on 9 held-out test folios, the methodology
is confirmed end-to-end.

The v7 methodology was INCREMENTAL (v1 solver -> v3 UNIQUE/STRONG ->
deadlock breaking -> v6 -> v7 intersection). The v8 builder replicates
this multi-stage bootstrapping using only training data:

    Phase 0: FREQUENCY-ALIGNMENT BOOTSTRAP
        - No prior identifications needed
        - Each folio gets a "plausible recipe pool" (top-K recipes by
          ingredient count ~ stem count alignment)
        - For each stem in 3+ folios, intersect plausible recipe pools
          across its folios to find candidate ingredients
        - Use presence/absence scoring to pick winners
        - This seeds the first identifications

    Phase 1+: ITERATIVE CONSTRAINT PROPAGATION
        - Now that we have seed identifications, compute F1-based
          best-recipe assignments (same as original v8 approach)
        - Run intersection solver on unidentified stems
        - Score via presence/absence differential
        - Repeat until convergence

Run:
    python -m scripts.validation.v8_builder
"""
import sys
import os
import csv
import json
import math
from collections import defaultdict, Counter

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.validation.config import PATHS, RANDOM_SEED, ensure_output_dirs
from scripts.validation import data_loader as dl

sys.stdout.reconfigure(encoding='utf-8')

# ── Configuration ────────────────────────────────────────────────────────────
MIN_FOLIO_COUNT = 3           # Stem must appear in at least this many train folios
MIN_F1_FOR_RECIPE = 20.0      # Minimum F1% to consider a folio's best-recipe valid
UNIQUE_CONFIDENCE_CAP = 95    # Max confidence for UNIQUE candidates
STRONG_CONFIDENCE_CAP = 90    # Max confidence for STRONG (2-candidate)
MODERATE_CONFIDENCE_CAP = 80  # Max confidence for MODERATE (3-candidate)
CONFIDENCE_FLOOR = 50         # Minimum confidence
MIN_CANDIDATE_SCORE = 5.0     # Minimum presence-absence differential to accept
FUNCTION_WORD_THRESHOLD = 0   # If intersection yields 0 candidates, mark as FUNCTION_WORD
MAX_ITERATIONS = 10           # Maximum constraint propagation iterations

# Phase 0 configuration
BOOTSTRAP_MIN_FOLIO_COUNT = 3   # Stem must appear in this many train folios for bootstrap
BOOTSTRAP_MIN_SCORE = 3.0       # Min presence-absence score for bootstrap acceptance
MIN_IDENTS_FOR_FW = 8           # Need this many unique ingredients before labeling FW

# Maximum stems per ingredient: cap = base + freq_factor * recipe_frequency
# This prevents high-frequency ingredients from absorbing all stems
# v8.1: Tightened caps -- original (2, 0.5, 15) caused every ingredient to
# hit its cap, producing 197 ingredient stems (6/ingredient avg) which
# destroyed discrimination. Permutation test p=0.29 proved signal was noise.
MAX_STEMS_BASE = 1              # Every ingredient gets at least this many stems
MAX_STEMS_FREQ_FACTOR = 0.1    # Additional stems per recipe appearance
MAX_STEMS_CEILING = 3           # Hard ceiling regardless of frequency
# With these settings: cap = min(3, 1 + 0.1*freq) so most ingredients get 2-3 stems

# Phase 1 co-occurrence quality thresholds
# Minimum lift to accept any ingredient assignment -- a lift of 1.5 means
# 50% more co-occurrence than expected by chance
COOCCUR_MIN_LIFT = 1.5


# ── Load blind splits ────────────────────────────────────────────────────────
def load_blind_splits():
    """Load the frozen train/test split."""
    split_path = os.path.join(PATHS['output_splits'], 'blind_splits.json')
    with open(split_path, encoding='utf-8') as f:
        return json.load(f)


# ── Core F1 computation ─────────────────────────────────────────────────────
def compute_f1(predicted_ings, recipe_ings, identifiable_ings):
    """F1 between a predicted ingredient set and a recipe's ingredients.

    fn is limited to ingredients in identifiable_ings (same as v7 logic).
    """
    if not predicted_ings or not recipe_ings:
        return 0.0, 0.0, 0.0
    tp = predicted_ings & recipe_ings
    fp = predicted_ings - recipe_ings
    fn = (recipe_ings & identifiable_ings) - predicted_ings

    prec = len(tp) / (len(tp) + len(fp)) if (len(tp) + len(fp)) > 0 else 0
    rec = len(tp) / (len(tp) + len(fn)) if (len(tp) + len(fn)) > 0 else 0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
    return f1 * 100, prec * 100, rec * 100


def get_folio_ingredients(folio, folio_stems, ident_map):
    """Get the set of identified ingredients for a folio."""
    ings = set()
    for stem in folio_stems.get(folio, set()):
        if stem in ident_map and ident_map[stem] != 'FUNCTION_WORD':
            for sub in ident_map[stem].split('|'):
                ings.add(sub.strip())
    return ings


# ── Best-match recipe assignment (F1-based, for Phase 1+) ───────────────────
def assign_best_recipes(train_folios, folio_stems, ident_map,
                        identifiable_ings, recipe_ingredients):
    """For each train folio, find the train recipe with highest F1.

    Returns {folio: (best_recipe, best_f1)}.
    """
    assignments = {}
    for folio in train_folios:
        folio_ings = get_folio_ingredients(folio, folio_stems, ident_map)
        best_f1 = 0.0
        best_recipe = None
        for rname, rings in recipe_ingredients.items():
            f1, _, _ = compute_f1(folio_ings, rings, identifiable_ings)
            if f1 > best_f1:
                best_f1 = f1
                best_recipe = rname
        assignments[folio] = (best_recipe, best_f1)
    return assignments


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 0: FREQUENCY-ALIGNMENT BOOTSTRAP
# ═══════════════════════════════════════════════════════════════════════════

def phase0_bootstrap(train_folios, folio_stems, stem_folios,
                     recipe_ingredients, all_train_stems):
    """Bootstrap initial identifications without any prior knowledge.

    Strategy: GREEDY CO-OCCURRENCE MATCHING
        1. Build ingredient co-occurrence matrix (from recipes)
        2. Build stem co-occurrence matrix (from folios)
        3. Sort ingredients by recipe frequency (descending)
        4. For the highest-frequency ingredient, find stems with matching
           folio-frequency and high co-occurrence consistency
        5. Accept the best mapping, then iterate: use co-occurrence
           structure to find the next ingredient's stem
        6. After seeding ~5-10 identifications, switch to F1-based
           intersection solver

    Returns:
        dict of {stem: {ingredient, confidence, tier, source, reasoning}}
    """
    print("\n" + "=" * 75)
    print("PHASE 0: GREEDY CO-OCCURRENCE BOOTSTRAP")
    print("=" * 75)

    n_train_folios = len(train_folios)
    n_train_recipes = len(recipe_ingredients)
    train_folios_list = sorted(train_folios)

    # ── Build ingredient frequency and co-occurrence data ────────────────
    ingredient_recipe_freq = Counter()
    ingredient_recipes = defaultdict(set)
    for rname, ings in recipe_ingredients.items():
        for ing in ings:
            ingredient_recipe_freq[ing] += 1
            ingredient_recipes[ing].add(rname)

    # Ingredient co-occurrence: how many recipes contain both I1 and I2?
    all_ingredients = sorted(set(ing for ings in recipe_ingredients.values()
                                 for ing in ings))
    ing_cooccur = defaultdict(int)
    for rname, ings in recipe_ingredients.items():
        ings_list = sorted(ings)
        for i, i1 in enumerate(ings_list):
            for i2 in ings_list[i+1:]:
                ing_cooccur[(i1, i2)] += 1
                ing_cooccur[(i2, i1)] += 1

    # ── Build stem frequency and co-occurrence data ──────────────────────
    stem_freq = {stem: len(folios) for stem, folios in stem_folios.items()}

    # Stem co-occurrence: how many folios contain both S1 and S2?
    # (Only for stems in 3+ folios to keep it manageable)
    eligible_stems = sorted([s for s in all_train_stems
                             if stem_freq.get(s, 0) >= BOOTSTRAP_MIN_FOLIO_COUNT])

    stem_cooccur = defaultdict(int)
    for folio, stems in folio_stems.items():
        eligible_in_folio = [s for s in stems if s in set(eligible_stems)]
        for i, s1 in enumerate(eligible_in_folio):
            for s2 in eligible_in_folio[i+1:]:
                stem_cooccur[(s1, s2)] += 1
                stem_cooccur[(s2, s1)] += 1

    print(f"\n  {n_train_folios} train folios, {n_train_recipes} train recipes")
    print(f"  {len(eligible_stems)} eligible stems (>={BOOTSTRAP_MIN_FOLIO_COUNT} folios)")
    print(f"  {len(all_ingredients)} unique ingredients")

    # ── Greedy matching ──────────────────────────────────────────────────
    identifications = {}
    identified_ingredients = set()
    mapped_stems = set()

    # Sort ingredients by frequency (most frequent first = most constrained)
    ingredients_by_freq = sorted(all_ingredients,
                                 key=lambda i: -ingredient_recipe_freq[i])

    # Only process ingredients appearing in enough recipes to be matchable
    matchable_ingredients = [i for i in ingredients_by_freq
                             if ingredient_recipe_freq[i] >= 3]

    print(f"  Matchable ingredients (in 3+ recipes): {len(matchable_ingredients)}")

    for ing in matchable_ingredients:
        if ing in identified_ingredients:
            continue

        i_freq = ingredient_recipe_freq[ing]
        i_norm = i_freq / n_train_recipes

        # Find candidate stems with matching frequency
        candidates = []
        for stem in eligible_stems:
            if stem in mapped_stems:
                continue
            s_freq = stem_freq[stem]
            s_norm = s_freq / n_train_folios
            ratio = s_norm / i_norm if i_norm > 0 else 0
            if 0.3 <= ratio <= 3.0:
                candidates.append(stem)

        if not candidates:
            continue

        # Score each candidate using co-occurrence consistency
        # with already-identified stems
        best_stem = None
        best_score = -999
        runner_up_score = -999

        for stem in candidates:
            s_freq_val = stem_freq[stem]
            s_norm = s_freq_val / n_train_folios

            # Base score: frequency alignment
            ratio = s_norm / i_norm if i_norm > 0 else 0
            freq_score = 1.0 - abs(ratio - 1.0)  # 1.0 = perfect match

            # Co-occurrence score: for each already-identified (stem', ingredient'),
            # check if co_occur(stem, stem')/max(freq) ≈ co_occur(ing, ingredient')/max(freq)
            cooccur_score = 0.0
            cooccur_count = 0

            for mapped_stem, info in identifications.items():
                mapped_ing = info['ingredient']
                if mapped_ing == 'FUNCTION_WORD':
                    continue

                # Stem co-occurrence rate
                s_co = stem_cooccur.get((stem, mapped_stem), 0)
                s_max = min(s_freq_val, stem_freq.get(mapped_stem, 0))
                s_rate = s_co / s_max if s_max > 0 else 0

                # Ingredient co-occurrence rate
                i_co = ing_cooccur.get((ing, mapped_ing), 0)
                i_max = min(i_freq, ingredient_recipe_freq.get(mapped_ing, 0))
                i_rate = i_co / i_max if i_max > 0 else 0

                # Similarity: how close are the co-occurrence rates?
                cooccur_score += 1.0 - abs(s_rate - i_rate)
                cooccur_count += 1

            if cooccur_count > 0:
                cooccur_score /= cooccur_count
                # Combined score: frequency + co-occurrence (weighted)
                total_score = freq_score * 0.3 + cooccur_score * 0.7
            else:
                # No prior mappings: use frequency alone
                total_score = freq_score

            if total_score > best_score:
                runner_up_score = best_score
                best_score = total_score
                best_stem = stem
            elif total_score > runner_up_score:
                runner_up_score = total_score

        if best_stem is None:
            continue

        gap = best_score - runner_up_score

        # Acceptance criteria:
        # - With no prior mappings: accept best frequency match even if
        #   multiple stems have similar frequency (will be corrected later)
        # - With prior mappings: require total_score > threshold AND gap
        accept = False
        n_prior = sum(1 for v in identifications.values()
                      if v['ingredient'] != 'FUNCTION_WORD')

        if n_prior == 0:
            # First mapping: accept best frequency match for HIGHEST-frequency
            # ingredient only (most constrained)
            s_norm = stem_freq[best_stem] / n_train_folios
            ratio = s_norm / i_norm if i_norm > 0 else 0
            freq_dist = abs(ratio - 1.0)
            # Only accept for very high-frequency ingredients where the signal is strong
            if freq_dist <= 0.15 and i_norm >= 0.5:
                accept = True
        elif n_prior < 3:
            # Early stage: moderate requirements
            if best_score > 0.55 and gap > 0.02:
                accept = True
        elif n_prior < 8:
            # Growing stage
            if best_score > 0.5 and gap > 0.015:
                accept = True
        else:
            # Mature stage: more relaxed
            if best_score > 0.45 and gap > 0.01:
                accept = True

        if accept:
            n_folios = stem_freq[best_stem]
            confidence = max(CONFIDENCE_FLOOR,
                             min(85, int(best_score * 100)))
            tier = 3 if confidence >= 75 else 4
            identifications[best_stem] = {
                'ingredient': ing,
                'confidence': confidence,
                'tier': tier,
                'source': 'v8_bootstrap_greedy',
                'reasoning': (f"Greedy co-occur: {ing} ({i_freq}/{n_train_recipes} recipes) "
                              f"-> {best_stem} ({n_folios}/{n_train_folios} folios). "
                              f"score={best_score:.3f}, gap={gap:.3f}, "
                              f"n_prior={n_prior}"),
            }
            identified_ingredients.add(ing)
            mapped_stems.add(best_stem)

    greedy_count = len(identifications)
    print(f"\n  Greedy matching identified: {greedy_count} stems")
    if identified_ingredients:
        print(f"  Ingredients: {sorted(identified_ingredients)}")

    # ════════════════════════════════════════════════════════════════════
    # Stage B+C: F1-seeded intersection (same as before)
    # Now that we have seed identifications, use F1 to assign folios to
    # recipes, then run intersection solver to discover more.
    # ════════════════════════════════════════════════════════════════════
    for bootstrap_pass in range(8):
        prev_count = len(identifications)

        current_ident_map = {stem: info['ingredient']
                             for stem, info in identifications.items()}
        identifiable = set()
        for info in identifications.values():
            if info['ingredient'] != 'FUNCTION_WORD':
                for sub in info['ingredient'].split('|'):
                    identifiable.add(sub.strip())

        folio_best_recipes = assign_best_recipes(
            train_folios, folio_stems, current_ident_map,
            identifiable, recipe_ingredients
        )

        valid_20 = sum(1 for r, f1 in folio_best_recipes.values()
                       if r and f1 >= MIN_F1_FOR_RECIPE)

        # Gradually tighten F1 threshold as identifications grow
        if len(identified_ingredients) < 5:
            bootstrap_f1_min = 1.0
        elif len(identified_ingredients) < 10:
            bootstrap_f1_min = 10.0
        else:
            bootstrap_f1_min = MIN_F1_FOR_RECIPE

        stage_count = 0
        unidentified = sorted(
            [s for s in all_train_stems
             if s not in identifications
             and stem_freq.get(s, 0) >= BOOTSTRAP_MIN_FOLIO_COUNT],
            key=lambda s: -stem_freq.get(s, 0)
        )

        for stem in unidentified:
            recipe_set, candidates, _ = intersection_solve(
                stem, stem_folios, folio_best_recipes,
                recipe_ingredients, identified_ingredients,
                min_f1=bootstrap_f1_min
            )
            if recipe_set is None:
                continue

            n_candidates = len(candidates)
            n_folios = len(stem_folios.get(stem, set()))

            if n_candidates == 1:
                candidate = candidates[0]
                score, pres, abse = score_candidate(
                    candidate, stem, stem_folios, folio_best_recipes,
                    recipe_ingredients, train_folios_list
                )
                if score >= BOOTSTRAP_MIN_SCORE:
                    confidence = max(CONFIDENCE_FLOOR,
                                     min(UNIQUE_CONFIDENCE_CAP, int(score + 50)))
                    identifications[stem] = {
                        'ingredient': candidate,
                        'confidence': confidence,
                        'tier': 2 if confidence >= 85 else 3,
                        'source': f'v8_bootstrap_pass{bootstrap_pass}_UNIQUE',
                        'reasoning': (f"Bootstrap pass {bootstrap_pass} UNIQUE: {candidate}. "
                                      f"{n_folios} folios, {pres:.0f}% pres, "
                                      f"{abse:.0f}% abs, score={score:.1f}"),
                    }
                    identified_ingredients.add(candidate)
                    stage_count += 1

            elif n_candidates == 2:
                scores = []
                for cand in candidates:
                    sc, pres, abse = score_candidate(
                        cand, stem, stem_folios, folio_best_recipes,
                        recipe_ingredients, train_folios_list
                    )
                    scores.append((cand, sc, pres, abse))
                scores.sort(key=lambda x: -x[1])
                best_cand, best_score, best_pres, best_abse = scores[0]
                runner_up = scores[1]
                gap = best_score - runner_up[1]
                if best_score >= BOOTSTRAP_MIN_SCORE and gap > 3:
                    confidence = max(CONFIDENCE_FLOOR,
                                     min(STRONG_CONFIDENCE_CAP, int(best_score + 50)))
                    identifications[stem] = {
                        'ingredient': best_cand,
                        'confidence': confidence,
                        'tier': 2 if confidence >= 85 else 3,
                        'source': f'v8_bootstrap_pass{bootstrap_pass}_STRONG',
                        'reasoning': (f"Bootstrap pass {bootstrap_pass} STRONG: "
                                      f"{best_cand}({best_score:.1f}) vs "
                                      f"{runner_up[0]}({runner_up[1]:.1f}). "
                                      f"{n_folios} folios, gap={gap:.1f}"),
                    }
                    identified_ingredients.add(best_cand)
                    stage_count += 1

            elif n_candidates == 3:
                remaining = [c for c in candidates if c not in identified_ingredients]
                if 1 <= len(remaining) <= 2:
                    scores_list = []
                    for cand in remaining:
                        sc, pres, abse = score_candidate(
                            cand, stem, stem_folios, folio_best_recipes,
                            recipe_ingredients, train_folios_list
                        )
                        scores_list.append((cand, sc, pres, abse))
                    scores_list.sort(key=lambda x: -x[1])
                    best_cand, best_score_val, best_pres, best_abse = scores_list[0]
                    gap = ((best_score_val - scores_list[1][1])
                           if len(scores_list) > 1 else best_score_val)
                    min_gap = 5 if len(remaining) == 2 else 0
                    if best_score_val >= BOOTSTRAP_MIN_SCORE and gap > min_gap:
                        confidence = max(CONFIDENCE_FLOOR,
                                         min(MODERATE_CONFIDENCE_CAP,
                                             int(best_score_val + 50)))
                        identifications[stem] = {
                            'ingredient': best_cand,
                            'confidence': confidence,
                            'tier': 3 if confidence >= 75 else 4,
                            'source': f'v8_bootstrap_pass{bootstrap_pass}_MODERATE',
                            'reasoning': (f"Bootstrap pass {bootstrap_pass}: 3 cand, "
                                          f"{len(remaining)} remain. "
                                          f"{best_cand}({best_score_val:.1f}) "
                                          f"gap={gap:.1f}. {n_folios} folios."),
                        }
                        identified_ingredients.add(best_cand)
                        stage_count += 1

        print(f"\n  Bootstrap pass {bootstrap_pass}: {stage_count} new, "
              f"total {len(identifications)}, "
              f"{len(identified_ingredients)} unique ingredients, "
              f"{valid_20} valid F1>={MIN_F1_FOR_RECIPE} assignments")

        if len(identifications) == prev_count:
            print(f"  Bootstrap converged after {bootstrap_pass + 1} passes.")
            break

    # ── Summary ──────────────────────────────────────────────────────────
    total = len(identifications)
    fw = sum(1 for v in identifications.values() if v['ingredient'] == 'FUNCTION_WORD')
    ing = total - fw
    unique_ings = len(identified_ingredients)
    print(f"\n  Phase0 TOTAL: {total} stems identified "
          f"({ing} ingredient + {fw} FUNCTION_WORD, {unique_ings} unique ingredients)")
    print(f"  Identified ingredients: {sorted(identified_ingredients)}")

    return identifications, identified_ingredients


# ═══════════════════════════════════════════════════════════════════════════
# STEM EXPANSION: Find additional stems for already-identified ingredients
# ═══════════════════════════════════════════════════════════════════════════

def expand_stems(train_folios, folio_stems, stem_folios,
                 recipe_ingredients, all_train_stems,
                 identifications, identified_ingredients):
    """Find additional stems that map to already-identified ingredients.

    For each identified (stem -> ingredient) pair:
    - Look at stem S's folio-set F(S)
    - For each unidentified stem S' whose folio-set F(S') overlaps significantly
      with F(S), check if S' could also be the same ingredient
    - Use the recipe structure to validate: if S' appears in folio F,
      does F's best-recipe contain the ingredient?

    Also uses intersection with recipe ingredients (NOT removing already-
    identified ingredients) to find stems whose intersection contains an
    already-identified ingredient.
    """
    print("\n" + "─" * 75)
    print("STEM EXPANSION: Finding additional stems for known ingredients")
    print("─" * 75)

    n_train_folios = len(train_folios)
    train_folios_list = sorted(train_folios)

    # Build current recipe assignments
    current_ident_map = {stem: info['ingredient']
                         for stem, info in identifications.items()}
    identifiable = set()
    for info in identifications.values():
        if info['ingredient'] != 'FUNCTION_WORD':
            for sub in info['ingredient'].split('|'):
                identifiable.add(sub.strip())

    folio_best_recipes = assign_best_recipes(
        train_folios, folio_stems, current_ident_map,
        identifiable, recipe_ingredients
    )

    # For each unidentified stem, run intersection but INCLUDING already-identified ingredients
    expanded = 0
    unidentified = sorted(
        [s for s in all_train_stems
         if s not in identifications
         and len(stem_folios.get(s, set())) >= MIN_FOLIO_COUNT],
        key=lambda s: -len(stem_folios.get(s, set()))
    )

    # Build ingredient stem counts for cap enforcement
    ingredient_stem_count = Counter()
    for info in identifications.values():
        ing = info['ingredient']
        if ing != 'FUNCTION_WORD':
            ingredient_stem_count[ing] += 1

    # Compute max stems per ingredient
    ingredient_recipe_freq_all = Counter()
    for rname, ings in recipe_ingredients.items():
        for ing in ings:
            ingredient_recipe_freq_all[ing] += 1

    for stem in unidentified:
        folios = stem_folios.get(stem, set())
        n_folios = len(folios)
        if n_folios < MIN_FOLIO_COUNT:
            continue

        # Get valid recipe assignments for this stem's folios
        recipe_set = set()
        for folio in folios:
            if folio not in folio_best_recipes:
                continue
            recipe, f1 = folio_best_recipes[folio]
            if recipe and f1 >= MIN_F1_FOR_RECIPE:
                recipe_set.add(recipe)

        if not recipe_set:
            continue

        # Intersect recipe ingredients (INCLUDING already-identified ones)
        ingredient_lists = [recipe_ingredients[r] for r in recipe_set]
        intersection = ingredient_lists[0].copy()
        for il in ingredient_lists[1:]:
            intersection &= il

        if not intersection:
            continue

        # Check if any already-identified ingredient is in the intersection
        known_in_intersection = intersection & identified_ingredients
        new_in_intersection = intersection - identified_ingredients

        if len(known_in_intersection) == 1 and len(new_in_intersection) == 0:
            # Exactly one known ingredient, no new ones: this stem maps to
            # the same ingredient
            candidate = list(known_in_intersection)[0]

            # Cap check: don't assign more stems than allowed
            freq = ingredient_recipe_freq_all.get(candidate, 0)
            max_stems = min(MAX_STEMS_CEILING,
                            MAX_STEMS_BASE + int(MAX_STEMS_FREQ_FACTOR * freq))
            if ingredient_stem_count.get(candidate, 0) >= max_stems:
                continue

            # Validate with presence/absence — require strong signal
            score, pres, abse = score_candidate(
                candidate, stem, stem_folios, folio_best_recipes,
                recipe_ingredients, train_folios_list
            )

            # Additional frequency alignment check: the stem's folio count
            # should be roughly proportional to the ingredient's recipe count
            ingredient_recipe_freq_local = sum(
                1 for r in recipe_ingredients.values() if candidate in r
            )
            s_norm = n_folios / n_train_folios
            i_norm = ingredient_recipe_freq_local / len(recipe_ingredients)
            freq_ratio = s_norm / i_norm if i_norm > 0 else 999

            # Require minimum score AND reasonable frequency alignment
            if (score >= MIN_CANDIDATE_SCORE * 2
                    and 0.3 <= freq_ratio <= 3.0):
                confidence = max(CONFIDENCE_FLOOR,
                                 min(UNIQUE_CONFIDENCE_CAP, int(score + 50)))
                identifications[stem] = {
                    'ingredient': candidate,
                    'confidence': confidence,
                    'tier': 2 if confidence >= 85 else 3,
                    'source': 'v8_expansion_UNIQUE_known',
                    'reasoning': (f"Expansion: only {candidate} (already known) in "
                                  f"intersection of {len(recipe_set)} recipes. "
                                  f"{n_folios} folios, {pres:.0f}% pres, "
                                  f"{abse:.0f}% abs, score={score:.1f}, "
                                  f"freq_ratio={freq_ratio:.2f}"),
                }
                ingredient_stem_count[candidate] += 1
                expanded += 1

        elif len(known_in_intersection) >= 1 and len(new_in_intersection) == 0:
            # Multiple known ingredients, no new: score them
            # Filter to only ingredients under their cap
            capped_known = [
                cand for cand in known_in_intersection
                if ingredient_stem_count.get(cand, 0) < min(
                    MAX_STEMS_CEILING,
                    MAX_STEMS_BASE + int(MAX_STEMS_FREQ_FACTOR * ingredient_recipe_freq_all.get(cand, 0))
                )
            ]
            if not capped_known:
                continue

            scores = []
            for cand in capped_known:
                sc, pres, abse = score_candidate(
                    cand, stem, stem_folios, folio_best_recipes,
                    recipe_ingredients, train_folios_list
                )
                scores.append((cand, sc, pres, abse))
            scores.sort(key=lambda x: -x[1])
            best_cand, best_score, best_pres, best_abse = scores[0]
            runner_up_score = scores[1][1] if len(scores) > 1 else -999
            gap = best_score - runner_up_score

            # Frequency alignment check for best candidate
            ingredient_recipe_freq_local = sum(
                1 for r in recipe_ingredients.values() if best_cand in r
            )
            s_norm = n_folios / n_train_folios
            i_norm = ingredient_recipe_freq_local / len(recipe_ingredients)
            freq_ratio = s_norm / i_norm if i_norm > 0 else 999

            if (best_score >= MIN_CANDIDATE_SCORE * 2
                    and gap > 8
                    and 0.3 <= freq_ratio <= 3.0):
                confidence = max(CONFIDENCE_FLOOR,
                                 min(STRONG_CONFIDENCE_CAP, int(best_score + 50)))
                identifications[stem] = {
                    'ingredient': best_cand,
                    'confidence': confidence,
                    'tier': 2 if confidence >= 85 else 3,
                    'source': 'v8_expansion_STRONG_known',
                    'reasoning': (f"Expansion: {best_cand} best of "
                                  f"{len(known_in_intersection)} known ingredients. "
                                  f"score={best_score:.1f}, gap={gap:.1f}, "
                                  f"{n_folios} folios, "
                                  f"freq_ratio={freq_ratio:.2f}"),
                }
                ingredient_stem_count[best_cand] += 1
                expanded += 1

    print(f"  Expanded: {expanded} additional stems for known ingredients")
    total_ing_stems = sum(1 for v in identifications.values()
                          if v['ingredient'] != 'FUNCTION_WORD')
    print(f"  Total ingredient stems: {total_ing_stems}")

    return identifications, identified_ingredients


# ═══════════════════════════════════════════════════════════════════════════
# INTERSECTION SOLVER (for Phase 1+)
# ═══════════════════════════════════════════════════════════════════════════

def intersection_solve(stem, stem_folios_map, folio_best_recipes,
                       recipe_ingredients, identified_ingredients,
                       min_f1=MIN_F1_FOR_RECIPE):
    """Run intersection analysis on a single unidentified stem.

    1. Get all train folios where this stem appears
    2. Get their best-match train recipes (with F1 > min_f1)
    3. Intersect recipe ingredient lists
    4. Remove already-identified ingredients
    5. Return candidate list
    """
    folios = stem_folios_map.get(stem, set())
    if len(folios) < MIN_FOLIO_COUNT:
        return None, [], {}

    # Collect valid best-match recipes
    recipe_set = set()
    folio_recipes = {}
    for folio in folios:
        if folio not in folio_best_recipes:
            continue
        recipe, f1 = folio_best_recipes[folio]
        if recipe and f1 >= min_f1:
            recipe_set.add(recipe)
            folio_recipes[folio] = recipe

    if not recipe_set:
        return None, [], {}

    # Intersect ingredient lists
    ingredient_lists = [recipe_ingredients[r] for r in recipe_set]
    intersection = ingredient_lists[0].copy()
    for il in ingredient_lists[1:]:
        intersection &= il

    # Remove already-identified ingredients
    candidates = intersection - identified_ingredients

    return recipe_set, sorted(candidates), folio_recipes


# ── Presence/absence confidence scoring ──────────────────────────────────
def score_candidate(candidate, stem, stem_folios_map, folio_best_recipes,
                    recipe_ingredients, all_train_folios):
    """Score a candidate ingredient by BASE-RATE-CORRECTED presence/absence.

    Raw presence_pct/absence_pct measure how often the candidate's recipe
    appears in folios where the stem is present/absent. But high-frequency
    ingredients (like Cinnamomum in 75% of recipes) will naturally have high
    presence_pct even for random stems.

    The corrected score measures EXCESS presence over base rate:
      base_rate = fraction of all valid folios whose recipe contains candidate
      score = (presence_pct - base_rate*100) - (absence_pct - base_rate*100)
            = presence_pct - absence_pct  (same formula, but we also return base_rate)

    However, we ADD a penalty for high-frequency ingredients: the score is
    divided by a dampening factor that increases with base rate, making it
    harder for ubiquitous ingredients to dominate.
    """
    stem_folios_set = stem_folios_map.get(stem, set())

    # Folios where stem is present
    present_folios = [f for f in stem_folios_set if f in folio_best_recipes]
    present_has_candidate = sum(
        1 for f in present_folios
        if candidate in recipe_ingredients.get(folio_best_recipes[f][0], set())
    )
    presence_pct = (present_has_candidate / len(present_folios) * 100
                    if present_folios else 0)

    # Folios where stem is absent (with valid recipe assignments)
    absent_folios = [
        f for f in all_train_folios
        if f not in stem_folios_set and f in folio_best_recipes
        and folio_best_recipes[f][1] >= MIN_F1_FOR_RECIPE
    ]
    absent_has_candidate = sum(
        1 for f in absent_folios
        if candidate in recipe_ingredients.get(folio_best_recipes[f][0], set())
    )
    absence_pct = (absent_has_candidate / len(absent_folios) * 100
                   if absent_folios else 0)

    raw_score = presence_pct - absence_pct

    # Base rate: what fraction of ALL valid folios map to recipes with this ingredient?
    all_valid = [f for f in all_train_folios if f in folio_best_recipes
                 and folio_best_recipes[f][1] >= MIN_F1_FOR_RECIPE]
    base_count = sum(
        1 for f in all_valid
        if candidate in recipe_ingredients.get(folio_best_recipes[f][0], set())
    )
    base_rate = base_count / len(all_valid) if all_valid else 0

    # Dampen score for high-frequency ingredients: divide by (1 + base_rate)
    # This means Cinnamomum (base_rate ~0.75) gets score / 1.75,
    # while a rare ingredient (base_rate ~0.1) gets score / 1.1
    dampened_score = raw_score / (1.0 + base_rate)

    return dampened_score, presence_pct, absence_pct


# ═══════════════════════════════════════════════════════════════════════════
# PHASE 1+: CO-OCCURRENCE-BASED ITERATIVE ASSIGNMENT
# ═══════════════════════════════════════════════════════════════════════════

def phase1_iterative(train_folios, folio_stems, stem_folios,
                     recipe_ingredients, all_train_stems,
                     identifications, identified_ingredients):
    """Iterative assignment using co-occurrence with identified ingredient stems.

    For each unidentified stem S, score each ingredient I by:
    1. Build I's folio-set = union of folio-sets of all stems identified as I
    2. Compute Jaccard similarity between S's folio-set and I's folio-set
    3. Compare to expected Jaccard under independence (base-rate correction)
    4. Score = observed_jaccard / expected_jaccard (lift)

    Stems with no strong ingredient signal are labeled FUNCTION_WORD.
    """
    iteration = 0
    while iteration < MAX_ITERATIONS:
        iteration += 1
        print(f"\n{'─'*75}")
        print(f"PHASE 1 -- ITERATION {iteration}")
        print(f"{'─'*75}")
        print(f"  Currently identified: {len(identifications)} stems -> "
              f"{len(identified_ingredients)} ingredients")

        # Build ingredient -> folio-set map from current identifications
        ingredient_folios = defaultdict(set)
        ingredient_stem_count = Counter()
        for stem, info in identifications.items():
            ing = info['ingredient']
            if ing == 'FUNCTION_WORD':
                continue
            for sub in ing.split('|'):
                sub = sub.strip()
                ingredient_folios[sub].update(stem_folios.get(stem, set()))
                ingredient_stem_count[sub] += 1

        n_train = len(train_folios)
        new_identifications = 0

        # Process unidentified stems in order of folio count (most constrained first)
        unidentified_stems = sorted(
            [s for s in all_train_stems if s not in identifications],
            key=lambda s: -len(stem_folios.get(s, set()))
        )

        for stem in unidentified_stems:
            stem_fol = stem_folios.get(stem, set())
            n_folios = len(stem_fol)
            if n_folios < MIN_FOLIO_COUNT:
                continue

            # Score against each identified ingredient
            scores = []
            for ing in sorted(identified_ingredients):
                # Skip if ingredient already at cap
                ing_count = ingredient_stem_count.get(ing, 0)
                freq = sum(1 for r in recipe_ingredients.values() if ing in r)
                max_stems = min(MAX_STEMS_CEILING,
                                MAX_STEMS_BASE + int(MAX_STEMS_FREQ_FACTOR * freq))
                if ing_count >= max_stems:
                    continue

                ing_fol = ingredient_folios.get(ing, set())
                if not ing_fol:
                    continue

                # Jaccard similarity
                intersection = len(stem_fol & ing_fol)
                union = len(stem_fol | ing_fol)
                jaccard = intersection / union if union > 0 else 0

                # Expected Jaccard under independence
                # P(in stem) = n_folios/n_train, P(in ing) = len(ing_fol)/n_train
                # Expected intersection ≈ n_folios * len(ing_fol) / n_train
                # Expected union ≈ n_folios + len(ing_fol) - expected_intersection
                expected_inter = n_folios * len(ing_fol) / n_train
                expected_union = n_folios + len(ing_fol) - expected_inter
                expected_jaccard = expected_inter / expected_union if expected_union > 0 else 0

                # Lift: how much more co-occurrence than expected by chance
                lift = jaccard / expected_jaccard if expected_jaccard > 0 else 0

                # Overlap fraction: what fraction of stem's folios overlap with ingredient
                overlap_frac = intersection / n_folios if n_folios > 0 else 0

                # Score combines lift with overlap fraction
                # lift > 1 means positive association; overlap_frac ensures
                # the stem actually appears in ingredient-relevant folios
                score = (lift - 1.0) * overlap_frac * 100  # Excess lift scaled by overlap

                if score > 0 and lift >= COOCCUR_MIN_LIFT:
                    scores.append((ing, score, jaccard, lift, overlap_frac))

            if not scores:
                # No positive association with any ingredient -> FUNCTION_WORD
                if len(identified_ingredients) >= MIN_IDENTS_FOR_FW:
                    identifications[stem] = {
                        'ingredient': 'FUNCTION_WORD',
                        'confidence': 85,
                        'tier': 0,
                        'source': f'v8_cooccur_fw_iter{iteration}',
                        'reasoning': (f"{n_folios} train folios. No positive ingredient "
                                      f"association (lift <= 1 for all). "
                                      f"Grammatical marker."),
                    }
                    new_identifications += 1
                continue

            scores.sort(key=lambda x: -x[1])
            best_ing, best_score, best_jacc, best_lift, best_overlap = scores[0]
            runner_score = scores[1][1] if len(scores) > 1 else 0
            gap = best_score - runner_score

            # Tier classification based on score and gap
            # v8.1: WEAK tier eliminated (was noise per permutation test p=0.29)
            # v8.1: MODERATE tightened from (score>=8,gap>=5) to (score>=15,gap>=8)
            # v8.1: Folio-set expansion disabled to prevent snowball effect
            if best_score >= 15 and gap >= 10:
                # Strong signal
                confidence = max(CONFIDENCE_FLOOR,
                                 min(STRONG_CONFIDENCE_CAP, int(best_score + 50)))
                identifications[stem] = {
                    'ingredient': best_ing,
                    'confidence': confidence,
                    'tier': 2 if confidence >= 85 else 3,
                    'source': f'v8_cooccur_strong_iter{iteration}',
                    'reasoning': (f"Co-occur STRONG: {best_ing} "
                                  f"score={best_score:.1f}, gap={gap:.1f}, "
                                  f"lift={best_lift:.2f}, overlap={best_overlap:.2f}, "
                                  f"{n_folios} folios."),
                }
                identified_ingredients.add(best_ing)
                # NOTE: Do NOT expand ingredient_folios to prevent snowball
                ingredient_stem_count[best_ing] += 1
                new_identifications += 1
            elif best_score >= 15 and gap >= 8:
                # Moderate signal (tightened from score>=8, gap>=5)
                confidence = max(CONFIDENCE_FLOOR,
                                 min(MODERATE_CONFIDENCE_CAP, int(best_score + 50)))
                identifications[stem] = {
                    'ingredient': best_ing,
                    'confidence': confidence,
                    'tier': 3 if confidence >= 75 else 4,
                    'source': f'v8_cooccur_moderate_iter{iteration}',
                    'reasoning': (f"Co-occur MODERATE: {best_ing} "
                                  f"score={best_score:.1f}, gap={gap:.1f}, "
                                  f"lift={best_lift:.2f}, overlap={best_overlap:.2f}, "
                                  f"{n_folios} folios."),
                }
                identified_ingredients.add(best_ing)
                # NOTE: Do NOT expand ingredient_folios to prevent snowball
                ingredient_stem_count[best_ing] += 1
                new_identifications += 1
            else:
                # Below threshold -> FUNCTION_WORD
                if len(identified_ingredients) >= MIN_IDENTS_FOR_FW:
                    identifications[stem] = {
                        'ingredient': 'FUNCTION_WORD',
                        'confidence': 80,
                        'tier': 0,
                        'source': f'v8_cooccur_below_thresh_iter{iteration}',
                        'reasoning': (f"{n_folios} folios. Best: {best_ing} "
                                      f"score={best_score:.1f}, gap={gap:.1f}, "
                                      f"lift={best_lift:.2f}. Below threshold."),
                    }
                    new_identifications += 1

        print(f"  New identifications this iteration: {new_identifications}")

        if new_identifications == 0:
            print(f"  Converged after {iteration} iterations.")
            break

    return identifications, identified_ingredients


# ═══════════════════════════════════════════════════════════════════════════
# MAIN BUILDER
# ═══════════════════════════════════════════════════════════════════════════

def build_v8():
    print("=" * 75)
    print("VOYNICH v8 IDENTIFICATION BUILDER")
    print("Using ONLY training data from blind_splits.json")
    print("=" * 75)

    # Load data
    splits = load_blind_splits()
    train_folios = set(splits['folio_split']['train'])
    test_folios = set(splits['folio_split']['test'])
    train_recipes = set(splits['recipe_split']['train'])
    test_recipes = set(splits['recipe_split']['test'])

    print(f"\nTrain folios: {len(train_folios)}")
    print(f"Test folios:  {len(test_folios)} (NEVER TOUCHED)")
    print(f"Train recipes: {len(train_recipes)}")
    print(f"Test recipes:  {len(test_recipes)} (NEVER TOUCHED)")

    # Load all data via standard loader
    data = dl.load_all()
    all_folio_stems = data['folio_stems']
    all_stem_folios = data['stem_folios']
    all_recipe_ings = data['recipe_ingredients']

    # FILTER: only train folios and train recipes
    folio_stems = {f: stems for f, stems in all_folio_stems.items()
                   if f in train_folios}

    # Build stem->folios map restricted to train folios
    stem_folios = defaultdict(set)
    for folio, stems in folio_stems.items():
        for stem in stems:
            stem_folios[stem].add(folio)
    stem_folios = dict(stem_folios)

    recipe_ingredients = {r: ings for r, ings in all_recipe_ings.items()
                          if r in train_recipes}

    # Count total stems in train folios
    all_train_stems = set()
    for stems in folio_stems.values():
        all_train_stems.update(stems)

    print(f"\nStems in train folios: {len(all_train_stems)}")
    print(f"Stems in 3+ train folios: "
          f"{sum(1 for s, fs in stem_folios.items() if len(fs) >= MIN_FOLIO_COUNT)}")

    # All unique ingredients across train recipes
    all_recipe_ingredient_pool = set()
    for ings in recipe_ingredients.values():
        all_recipe_ingredient_pool.update(ings)
    print(f"Unique ingredients in train recipes: {len(all_recipe_ingredient_pool)}")

    # ── Phase 0: Bootstrap ───────────────────────────────────────────────
    identifications, identified_ingredients = phase0_bootstrap(
        train_folios, folio_stems, stem_folios,
        recipe_ingredients, all_train_stems
    )

    # ── Phase 0b: Stem expansion ───────────────────────────────────────
    # Find additional stems for already-identified ingredients
    for expansion_pass in range(5):
        prev_count = len(identifications)
        identifications, identified_ingredients = expand_stems(
            train_folios, folio_stems, stem_folios,
            recipe_ingredients, all_train_stems,
            identifications, identified_ingredients
        )
        if len(identifications) == prev_count:
            print(f"  Stem expansion converged after {expansion_pass + 1} passes.")
            break

    # ── Phase 0b: (Removed — Phase 0 now has its own multi-stage bootstrap)

    # ── Phase 1+: Iterative constraint propagation ───────────────────────
    print(f"\n{'='*75}")
    print("PHASE 1+: ITERATIVE CONSTRAINT PROPAGATION")
    print(f"{'='*75}")
    print(f"Starting with {len(identifications)} seed identifications from Phase 0")

    identifications, identified_ingredients = phase1_iterative(
        train_folios, folio_stems, stem_folios,
        recipe_ingredients, all_train_stems,
        identifications, identified_ingredients
    )

    # ── Summary ──────────────────────────────────────────────────────────
    print(f"\n{'='*75}")
    print("v8 IDENTIFICATION SUMMARY")
    print(f"{'='*75}")

    tier_counts = Counter(info['tier'] for info in identifications.values())
    ingredient_counts = Counter()
    for info in identifications.values():
        if info['ingredient'] != 'FUNCTION_WORD':
            ingredient_counts[info['ingredient']] += 1

    total_stems = len(identifications)
    fw_stems = sum(1 for info in identifications.values()
                   if info['ingredient'] == 'FUNCTION_WORD')
    ing_stems = total_stems - fw_stems
    unique_ings = len(set(
        info['ingredient'] for info in identifications.values()
        if info['ingredient'] != 'FUNCTION_WORD'
    ))

    print(f"\nTotal stems identified: {total_stems}")
    print(f"  FUNCTION_WORD: {fw_stems}")
    print(f"  Ingredient stems: {ing_stems}")
    print(f"  Unique ingredients: {unique_ings}")
    print(f"\nBy tier:")
    for tier in sorted(tier_counts.keys()):
        print(f"  Tier {tier}: {tier_counts[tier]}")
    print(f"\nIdentified ingredients:")
    for ing, count in sorted(ingredient_counts.items(), key=lambda x: -x[1]):
        print(f"  {ing}: {count} stems")

    # Coverage statistics
    total_train_stems = len(all_train_stems)
    eligible_stems = sum(1 for s in all_train_stems
                         if len(stem_folios.get(s, set())) >= MIN_FOLIO_COUNT)
    print(f"\nCoverage:")
    print(f"  Total stems in train folios: {total_train_stems}")
    print(f"  Eligible stems (>={MIN_FOLIO_COUNT} folios): {eligible_stems}")
    if eligible_stems > 0:
        print(f"  Identified: {total_stems} ({total_stems/eligible_stems*100:.1f}% of eligible)")
        print(f"  Unidentified eligible: {eligible_stems - total_stems}")
    else:
        print(f"  Identified: {total_stems}")

    # ── By source breakdown ──────────────────────────────────────────────
    print(f"\nBy source:")
    source_counts = Counter(info['source'] for info in identifications.values())
    for source, count in sorted(source_counts.items(), key=lambda x: -x[1]):
        print(f"  {source}: {count}")

    # ── Comparison with v7 ───────────────────────────────────────────────
    print(f"\n{'='*75}")
    print("COMPARISON WITH v7 (for reference only)")
    print(f"{'='*75}")
    v7_idents = dl.load_identifications()
    v7_stems = {row['Stem'] for row in v7_idents}
    v8_stems = set(identifications.keys())

    shared = v7_stems & v8_stems
    v7_only = v7_stems - v8_stems
    v8_only = v8_stems - v7_stems

    print(f"  v7 stems: {len(v7_stems)}")
    print(f"  v8 stems: {len(v8_stems)}")
    print(f"  Shared:   {len(shared)}")
    print(f"  v7-only:  {len(v7_only)}")
    print(f"  v8-only:  {len(v8_only)}")

    # Check agreement on shared stems
    v7_map = {row['Stem']: row['Ingredient'] for row in v7_idents}
    agreements = 0
    disagreements = 0
    for stem in sorted(shared):
        v7_ing = v7_map[stem]
        v8_ing = identifications[stem]['ingredient']
        if v7_ing == v8_ing:
            agreements += 1
        else:
            disagreements += 1
            if disagreements <= 20:
                print(f"  DISAGREE: {stem} -> v7:{v7_ing} vs v8:{v8_ing}")

    if shared:
        print(f"\n  Agreement on shared stems: {agreements}/{len(shared)} "
              f"({agreements/len(shared)*100:.1f}%)")
    if disagreements > 20:
        print(f"  ({disagreements - 20} more disagreements not shown)")

    # ── Save v8 identifications ──────────────────────────────────────────
    ensure_output_dirs()
    out_path = os.path.join(PATHS['output_validation'],
                            'voynich_unified_identifications_v8.csv')
    with open(out_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Stem', 'Ingredient', 'Confidence', 'Tier',
                         'Source', 'Reasoning'])
        for stem in sorted(identifications.keys()):
            info = identifications[stem]
            writer.writerow([
                stem,
                info['ingredient'],
                info['confidence'],
                info['tier'],
                info['source'],
                info['reasoning'],
            ])
    print(f"\nv8 identifications saved to: {out_path}")

    # Also save metadata
    meta = {
        'version': 'v8',
        'train_folios': sorted(train_folios),
        'train_recipes': sorted(train_recipes),
        'n_train_folios': len(train_folios),
        'n_train_recipes': len(train_recipes),
        'total_stems': total_stems,
        'function_words': fw_stems,
        'ingredient_stems': ing_stems,
        'unique_ingredients': unique_ings,
        'tier_counts': {str(k): v for k, v in tier_counts.items()},
        'source_counts': dict(source_counts),
        'parameters': {
            'MIN_FOLIO_COUNT': MIN_FOLIO_COUNT,
            'MIN_F1_FOR_RECIPE': MIN_F1_FOR_RECIPE,
            'UNIQUE_CONFIDENCE_CAP': UNIQUE_CONFIDENCE_CAP,
            'STRONG_CONFIDENCE_CAP': STRONG_CONFIDENCE_CAP,
            'MODERATE_CONFIDENCE_CAP': MODERATE_CONFIDENCE_CAP,
            'CONFIDENCE_FLOOR': CONFIDENCE_FLOOR,
            'MIN_CANDIDATE_SCORE': MIN_CANDIDATE_SCORE,
            'MAX_ITERATIONS': MAX_ITERATIONS,
            'BOOTSTRAP_MIN_FOLIO_COUNT': BOOTSTRAP_MIN_FOLIO_COUNT,
            'BOOTSTRAP_MIN_SCORE': BOOTSTRAP_MIN_SCORE,
            'MIN_IDENTS_FOR_FW': MIN_IDENTS_FOR_FW,
        },
    }
    meta_path = os.path.join(PATHS['output_validation'], 'v8_build_metadata.json')
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"Build metadata saved to: {meta_path}")

    return identifications


if __name__ == '__main__':
    build_v8()
