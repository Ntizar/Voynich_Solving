import os
import csv
import re
from collections import defaultdict

# Crear carpeta para el grafo de Obsidian
vault_dir = "Voynich_Graph"
os.makedirs(vault_dir, exist_ok=True)
os.makedirs(os.path.join(vault_dir, "Plantas"), exist_ok=True)
os.makedirs(os.path.join(vault_dir, "Folios_Botanica"), exist_ok=True)
os.makedirs(os.path.join(vault_dir, "Folios_Recetas"), exist_ok=True)

# Leer el CSV generado previamente
plantas = []
with open('voynich_mega_indice_conexiones.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Solo coger plantas que viajan a recetas para que el grafo sea relevante
        if int(row['Apariciones_en_Recetas']) > 0:
            plantas.append(row)

# Generar archivos Markdown
for p in plantas:
    stem = p['Raiz_Planta']
    origen = p['Folios_Origen_Botanica'].split(' | ')[0] # Coger el principal
    destinos_raw = p['Folios_Destino_Recetas'].split(' | ')
    
    # Parsear destinos: "f88r (x3)" -> folio: f88r, count: 3
    destinos = []
    for d in destinos_raw:
        if d == "NINGUNO": continue
        match = re.search(r'(f\d+[rv])', d)
        if match:
            destinos.append(match.group(1))

    # 1. Crear Nota de la Planta
    planta_md = f"""---
tags: [voynich/planta, ingrediente]
origen: "[[Folio_{origen}]]"
frecuencia_recetas: {p['Apariciones_en_Recetas']}
---
# Planta: {stem}

## 🌿 Origen Botánico
Esta planta se describe e ilustra originalmente en el folio: **[[Folio_{origen}]]**.
*Enlace a imagen original:* [Ver {origen} en Voynich.nu](http://www.voynich.nu/fol/{origen}.html)

## ⚗️ Uso en Farmacia / Recetas
Esta planta es utilizada como ingrediente en las siguientes recetas médicas:
"""
    for d in destinos:
        planta_md += f"- Usado en receta: **[[Folio_{d}]]**\n"
        
    planta_md += f"\n## 📊 Etiquetas Dominantes en Recetas\n{p['Etiquetas_Dominantes_en_Recetas']}\n"
    
    with open(os.path.join(vault_dir, "Plantas", f"Planta_{stem}.md"), "w", encoding='utf-8') as mf:
        mf.write(planta_md)

    # 2. Crear Notas de los Folios de Botánica (si no existen)
    botanica_path = os.path.join(vault_dir, "Folios_Botanica", f"Folio_{origen}.md")
    if not os.path.exists(botanica_path):
        bot_md = f"""---
tags: [voynich/folio, botanica]
---
# Folio {origen} (Sección Botánica)

Aquí se ilustra la planta: **[[Planta_{stem}]]**.
[Ver imagen del manuscrito](http://www.voynich.nu/fol/{origen}.html)
"""
        with open(botanica_path, "w", encoding='utf-8') as bf:
            bot_md += f"- Contiene la descripción principal de: [[Planta_{stem}]]\n"
            bf.write(bot_md)
    else:
        with open(botanica_path, "a", encoding='utf-8') as bf:
            bf.write(f"- Contiene la descripción principal de: [[Planta_{stem}]]\n")

    # 3. Crear Notas de los Folios de Recetas (si no existen)
    for d in destinos:
        receta_path = os.path.join(vault_dir, "Folios_Recetas", f"Folio_{d}.md")
        if not os.path.exists(receta_path):
            receta_md = f"""---
tags: [voynich/folio, receta]
---
# Folio {d} (Sección Farmacia / Recetas)

Esta página contiene fórmulas médicas que mezclan múltiples ingredientes botánicos.
[Ver imagen del manuscrito](http://www.voynich.nu/fol/{d}.html)

## 🧪 Ingredientes Identificados:
- [[Planta_{stem}]]
"""
            with open(receta_path, "w", encoding='utf-8') as rf:
                rf.write(receta_md)
        else:
            with open(receta_path, "a", encoding='utf-8') as rf:
                rf.write(f"- [[Planta_{stem}]]\n")

print(f"Bóveda de Obsidian generada en la carpeta: {vault_dir}")
print(f"Se han creado archivos para {len(plantas)} plantas clave y sus folios conectados.")
