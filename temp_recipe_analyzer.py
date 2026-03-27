import csv
from collections import defaultdict

recipe_ingredients = defaultdict(list)

with open('voynich_mega_indice_conexiones.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        stem = row['Raiz_Planta']
        tipo = row['Tipo_Vocabulario']
        destinos_raw = row['Folios_Destino_Recetas'].split(' | ')
        
        for d in destinos_raw:
            if d == "NINGUNO": continue
            # El formato es "f88r (x3)", extraemos solo "f88r"
            folio = d.split(' ')[0]
            recipe_ingredients[folio].append((stem, tipo))

# Ordenar las recetas por el número de ingredientes botánicos ÚNICOS que contienen
sorted_recipes = sorted(recipe_ingredients.items(), key=lambda x: len(x[1]), reverse=True)

print("=== TOP RECETAS DEL VOYNICH (Ordenadas por complejidad de ingredientes) ===\n")
for folio, ingredients in sorted_recipes[:5]: # Mostrar las 5 más complejas
    exclusivos = [i[0] for i in ingredients if "Exclusiva" in i[1]]
    comunes = [i[0] for i in ingredients if "Comun" in i[1]]
    print(f"[{folio}] - Total ingredientes mapeados desde botánica: {len(ingredients)}")
    print(f"   🌿 Plantas Específicas (Nombres Propios): {len(exclusivos)}")
    if exclusivos: print(f"       {', '.join(exclusivos[:5])}" + ("..." if len(exclusivos)>5 else ""))
    print(f"   💧 Bases/Excipientes (Comunes): {len(comunes)}")
    if comunes: print(f"       {', '.join(comunes[:5])}" + ("..." if len(comunes)>5 else ""))
    print("-" * 60)

