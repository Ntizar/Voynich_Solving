import csv
from collections import defaultdict
import sys

sys.stdout.reconfigure(encoding='utf-8')

recipe_ingredients = defaultdict(list)

with open('voynich_mega_indice_conexiones.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        stem = row['Raiz_Planta']
        tipo = row['Tipo_Vocabulario']
        destinos_raw = row['Folios_Destino_Recetas'].split(' | ')
        
        for d in destinos_raw:
            if d == "NINGUNO": continue
            folio = d.split(' ')[0]
            recipe_ingredients[folio].append((stem, tipo))

sorted_recipes = sorted(recipe_ingredients.items(), key=lambda x: len(x[1]), reverse=True)

print("=== TOP RECETAS DEL VOYNICH (Ordenadas por complejidad) ===\n")
for folio, ingredients in sorted_recipes[:5]:
    exclusivos = [i[0] for i in ingredients if "Exclusiva" in i[1]]
    comunes = [i[0] for i in ingredients if "Comun" in i[1]]
    print(f"[{folio}] - Total ingredientes mapeados: {len(ingredients)}")
    print(f"  -> Plantas Especificas (Nombres Propios): {len(exclusivos)}")
    if exclusivos: print(f"     Ej: {', '.join(exclusivos[:5])}" + ("..." if len(exclusivos)>5 else ""))
    print(f"  -> Bases/Excipientes (Comunes): {len(comunes)}")
    if comunes: print(f"     Ej: {', '.join(comunes[:5])}" + ("..." if len(comunes)>5 else ""))
    print("-" * 60)

