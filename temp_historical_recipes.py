import csv
import sys
sys.stdout.reconfigure(encoding='utf-8')

# BASE DE DATOS DE RECETAS MEDIEVALES REALES
# Fuentes: Antidotarium Nicolai (s.XII), Grabadin (s.XIII), Triaca Magna (Galeno/Andromachus)
# Los ingredientes estan en Latin farmaceutico y agrupados por categoria

recipes = [
    {
        "nombre": "Theriac Magna (Triaca de Andromachus)",
        "fuente": "Galeno / Andromachus, s.I-II d.C., copiada en todos los Antidotarios medievales",
        "tipo": "Antidoto Universal / Panacea",
        "total_ingredientes": 64,
        "activos_raros": [
            "Opium (Papaver somniferum)", "Trochisci de vipera (Carne de Vibora)",
            "Squilla (Escila maritima)", "Hedychium (Jengibre silvestre)",
            "Castoreum (Castoreo)", "Nardus celtica (Nardo celtico)",
            "Petroselinum (Perejil de piedra)", "Phu (Valeriana)",
            "Amomum (Cardamomo negro)", "Acorus calamus (Calamo aromatico)",
            "Hypericum (Hiperico)", "Gentiana (Genciana)",
            "Aristolochia (Aristoloquia)", "Opopanax",
            "Sagapenum", "Galbanum",
            "Balsamum", "Styrax",
            "Terebinthina (Trementina)", "Bitumen judaicum"
        ],
        "especias_aromaticas": [
            "Crocus (Azafran)", "Zingiber (Jengibre)", "Cinnamomum (Canela)",
            "Piper longum (Pimienta larga)", "Piper nigrum (Pimienta negra)",
            "Myrrha (Mirra)", "Olibanum/Thus (Incienso)",
            "Casia (Casia/Canela china)", "Costus",
            "Anisi (Anis)", "Foeniculum (Hinojo)", "Daucus creticus (Zanahoria de Creta)"
        ],
        "bases_excipientes": [
            "Mel despumatum (Miel clarificada)", "Vinum (Vino)"
        ],
        "n_activos": 20,
        "n_especias": 12,
        "n_bases": 2
    },
    {
        "nombre": "Mithridatium",
        "fuente": "Mitridates VI del Ponto, copiado por Galeno y toda la Edad Media",
        "tipo": "Antidoto contra venenos",
        "total_ingredientes": 54,
        "activos_raros": [
            "Opium", "Castoreum", "Nardus indica", "Nardus celtica",
            "Gentiana", "Aristolochia longa", "Aristolochia rotunda",
            "Hypericum", "Sagapenum", "Opopanax", "Acacia",
            "Gummi arabicum", "Hypocistis", "Stachys",
            "Thlaspi (Carraspique)", "Daucus creticus"
        ],
        "especias_aromaticas": [
            "Crocus", "Zingiber", "Cinnamomum", "Piper longum",
            "Piper nigrum", "Myrrha", "Costus", "Casia",
            "Anisi", "Petroselinum", "Foeniculum", "Cardamomum"
        ],
        "bases_excipientes": [
            "Mel despumatum", "Vinum"
        ],
        "n_activos": 16,
        "n_especias": 12,
        "n_bases": 2
    },
    {
        "nombre": "Diascordium (Electuario de Escordio)",
        "fuente": "Jeronimo Fracastoro, s.XVI, basado en textos anteriores",
        "tipo": "Antidoto / Antipestilencial",
        "total_ingredientes": 14,
        "activos_raros": [
            "Scordium (Escordio)", "Opium", "Castoreum",
            "Galbanum", "Styrax", "Bistorta"
        ],
        "especias_aromaticas": [
            "Cinnamomum", "Piper longum", "Zingiber",
            "Rosa", "Gentiana", "Dictamnus (Dictamo)"
        ],
        "bases_excipientes": [
            "Mel despumatum"
        ],
        "n_activos": 6,
        "n_especias": 6,
        "n_bases": 1
    },
    {
        "nombre": "Pillulae Cochiae (Pildoras Cochias)",
        "fuente": "Antidotarium Nicolai, s.XII",
        "tipo": "Purgante fuerte",
        "total_ingredientes": 5,
        "activos_raros": [
            "Colocynthis (Coloquintida)", "Aloe",
            "Scammonium (Escamonea)"
        ],
        "especias_aromaticas": [
            "Staphisagria (Estafisagria)", "Bdellium"
        ],
        "bases_excipientes": [
            "Succo absinthii (Jugo de ajenjo)"
        ],
        "n_activos": 3,
        "n_especias": 2,
        "n_bases": 1
    },
    {
        "nombre": "Pillulae Aureae (Pildoras Doradas)",
        "fuente": "Antidotarium Nicolai, s.XII",
        "tipo": "Purgante suave / Tonico",
        "total_ingredientes": 7,
        "activos_raros": [
            "Aloe", "Diagridium (Escamonea preparada)",
            "Mastix (Almaciga)", "Rosa"
        ],
        "especias_aromaticas": [
            "Crocus", "Cinnamomum"
        ],
        "bases_excipientes": [
            "Succo absinthii"
        ],
        "n_activos": 4,
        "n_especias": 2,
        "n_bases": 1
    },
    {
        "nombre": "Unguentum Apostolorum (Ungueento de los Apostoles)",
        "fuente": "Antidotarium Nicolai / Grabadin",
        "tipo": "Ungueento cicatrizante / 12 ingredientes",
        "total_ingredientes": 12,
        "activos_raros": [
            "Aristolochia longa", "Aristolochia rotunda",
            "Opopanax", "Galbanum", "Bdellium",
            "Verdigris (Cardenillo)", "Litharge (Litargirio)"
        ],
        "especias_aromaticas": [
            "Olibanum", "Myrrha"
        ],
        "bases_excipientes": [
            "Cera (Cera de abeja)", "Oleum olivarum (Aceite de oliva)",
            "Resina (Resina de pino)"
        ],
        "n_activos": 7,
        "n_especias": 2,
        "n_bases": 3
    },
    {
        "nombre": "Electuarium de Succo Rosarum",
        "fuente": "Circa Instans / Salerno, s.XII",
        "tipo": "Laxante suave / Tonico digestivo",
        "total_ingredientes": 8,
        "activos_raros": [
            "Rosa gallica", "Senna (Sen)", "Tamarindus (Tamarindo)",
            "Viola"
        ],
        "especias_aromaticas": [
            "Cinnamomum", "Zingiber", "Anisi"
        ],
        "bases_excipientes": [
            "Saccharum (Azucar)"
        ],
        "n_activos": 4,
        "n_especias": 3,
        "n_bases": 1
    },
    {
        "nombre": "Aurea Alexandrina",
        "fuente": "Antidotarium Nicolai, s.XII",
        "tipo": "Reconstituyente / Tonico general",
        "total_ingredientes": 22,
        "activos_raros": [
            "Opium", "Castoreum", "Stachys",
            "Hypericum", "Petroselinum", "Acorus calamus",
            "Phu (Valeriana)", "Squilla"
        ],
        "especias_aromaticas": [
            "Crocus", "Piper longum", "Piper nigrum",
            "Zingiber", "Cinnamomum", "Myrrha",
            "Costus", "Nardus", "Anisi", "Foeniculum", "Casia"
        ],
        "bases_excipientes": [
            "Mel despumatum", "Vinum", "Saccharum"
        ],
        "n_activos": 8,
        "n_especias": 11,
        "n_bases": 3
    }
]

# Guardar la base de datos historica como CSV
with open('recetas_historicas_medievales.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([
        'Nombre_Receta', 'Fuente', 'Tipo', 'Total_Ingredientes',
        'N_Activos_Raros', 'N_Especias', 'N_Bases',
        'Ratio_Activos_%', 'Ratio_Especias_%', 'Ratio_Bases_%',
        'Lista_Activos', 'Lista_Especias', 'Lista_Bases'
    ])
    for r in recipes:
        total = r['total_ingredientes']
        writer.writerow([
            r['nombre'], r['fuente'], r['tipo'], total,
            r['n_activos'], r['n_especias'], r['n_bases'],
            round((r['n_activos']/total)*100, 1),
            round((r['n_especias']/total)*100, 1),
            round((r['n_bases']/total)*100, 1),
            ' | '.join(r['activos_raros']),
            ' | '.join(r['especias_aromaticas']),
            ' | '.join(r['bases_excipientes'])
        ])

print("=== BASE DE DATOS HISTORICA GENERADA ===")
print(f"Archivo: recetas_historicas_medievales.csv")
print(f"Total recetas catalogadas: {len(recipes)}")
print("\nResumen de proporciones historicas:")
print(f"{'Receta':<35} | {'Total':>5} | {'Activos%':>8} | {'Especias%':>9} | {'Bases%':>6}")
print("-" * 75)
for r in recipes:
    total = r['total_ingredientes']
    print(f"{r['nombre']:<35} | {total:>5} | {(r['n_activos']/total)*100:>7.1f}% | {(r['n_especias']/total)*100:>8.1f}% | {(r['n_bases']/total)*100:>5.1f}%")

