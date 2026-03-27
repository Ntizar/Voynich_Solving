import sys

sys.stdout.reconfigure(encoding='utf-8')

theriac_plants = [
    ('A1Q2A3', 'f34v'),
    ('K1J1A1A3', 'f55v'),
    ('K1A1B1A3', 'f8r'),  
    ('B2K1A1', 'f55r'),
    ('K1Q1A3', 'f27v'),
    ('AaQ1A3', 'f40r'),
    ('D1A1B1A3', 'f30r')
]

print("=== PLANTAS CANDIDATAS PARA BUSQUEDA VISUAL EN VOYNICH.NU ===\n")
print("Busca estos folios en http://www.voynich.nu/ para ver las teorias botanicas y cruzarlas con nuestra hipotesis de 'Antidoto/Triaca'.\n")

for root, origin in theriac_plants:
    # URL format adjustment: usually f34v translates directly to voynich.nu format
    print(f"--> Folio Origen: {origin} | Raiz Voynich: [{root}]")
    print(f"    Link de imagen: http://www.voynich.nu/fol/{origin}.html")
    print(f"    Nuestra hipotesis relacional: Ingrediente activo o especia usada en formulaciones complejas.")
    print(f"    Tarea de contraste: ¿Tiene la imagen raiz gruesa (Mandragora/Valeriana), bulbos (Escila), o es aromatica/venenosa?")
    print("-" * 60)

