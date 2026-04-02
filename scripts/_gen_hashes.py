"""Temporary script to generate SHA-256 hashes of all source files."""
import hashlib
import os

ROOT = r"C:\Ntizar_Obsidian\Ntizar_Brain\MASTERTMIND"

files = [
    "voynich_sta.txt",
    "zenodo_voynich/corpus/voynich_sta.txt",
    "zenodo_voynich/corpus/voynich_eva.txt",
    "recetas_historicas_medievales.csv",
    "recetas_historicas_ingredientes_flat.csv",
    "voynich_mega_indice_conexiones.csv",
    "voynich_all_recipe_folio_stems.csv",
    "voynich_unified_identifications_v7.csv",
    "voynich_matching_v7.csv",
    "voynich_expanded_matching_v7.csv",
    "voynich_todas_recetas_perfil.csv",
    "voynich_consistencia_cruzada.csv",
    "voynich_cruces_recetas_historicas.csv",
]

for f in files:
    full = os.path.join(ROOT, f)
    if os.path.exists(full):
        h = hashlib.sha256(open(full, "rb").read()).hexdigest()
        print(f'    "{f}": "{h}",')
    else:
        print(f"    # MISSING: {f}")
