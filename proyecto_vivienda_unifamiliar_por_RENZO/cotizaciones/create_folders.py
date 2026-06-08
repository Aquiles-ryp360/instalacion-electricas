import os

base_dir = r"C:\Users\renzo\instalacion-electricas\proyecto_vivienda_unifamiliar_por_RENZO"

folders = [
    "planos",
    "layouts",
    "planos_cad",
    "planos_electricos",
    "cuadro_cargas",
    "maxima_demanda",
    "diagrama_unifilar",
    "memoria_descriptiva",
    "memoria_calculo",
    "especificaciones",
    "revisiones",
    "salidas",
    "docs"
]

for folder in folders:
    path = os.path.join(base_dir, folder)
    os.makedirs(path, exist_ok=True)
    print(f"Creado: {path}")

print("Carpetas creadas con éxito.")
