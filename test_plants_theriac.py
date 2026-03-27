import csv
from collections import defaultdict

# Las plantas exclusivas detectadas en la Súper Receta (f113r)
theriac_plants = [
    ('A1Q2A3', 'f34v'),
    ('K1J1A1A3', 'f55v'),
    ('K1A1B1A3', 'f8r'),  # El "Guisante/Hiedra" descartado
    ('B2K1A1', 'f55r'),
    ('K1Q1A3', 'f27v'),
    ('AaQ1A3', 'f40r'),
    ('D1A1B1A3', 'f30r')
]

print("=== PLANTAS CANDIDATAS PARA BÚSQUEDA VISUAL EN VOYNICH.NU ===\n")
print("Busca estos folios en http://www.voynich.nu/fol/ para ver las teorias botanicas y cruzarlas con nuestra hipotesis de 'Antidoto/Triaca'.\n")

for root, origin in theriac_plants:
    print(f"📌 Folio Origen: {origin} | Raíz Voynich: [{root}]")
    print(f"   - Link de imagen: http://www.voynich.nu/fol/f{origin[1:]}.html")
    print(f"   - Nuestra hipotesis relacional: Ingrediente activo o especia usada en formulaciones complejas.")
    print(f"   - Tarea de contraste: ¿Tiene la imagen raiz gruesa (Mandragora/Valeriana), bulbos (Escila), o es aromatica/venenosa?")
    print("-" * 60)

