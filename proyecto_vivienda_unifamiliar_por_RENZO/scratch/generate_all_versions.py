import os
import subprocess

base_dir = r"C:\Users\renzo\instalacion-electricas"
project_dir = os.path.join(base_dir, "proyecto_vivienda_unifamiliar_por_RENZO")
layouts_dir = os.path.join(project_dir, "layouts")
planos_cad_dir = os.path.join(project_dir, "planos_cad")
generator_script = os.path.join(base_dir, "herramientas", "ia-cad-casas", "scripts", "dxf_generator.py")

os.makedirs(planos_cad_dir, exist_ok=True)

# List of layouts to compile
layouts = [
    "primer_piso_v1", "primer_piso_v2", "primer_piso_v3",
    "segundo_piso_v1", "segundo_piso_v2", "segundo_piso_v3",
    "tercer_piso_v1", "tercer_piso_v2", "tercer_piso_v3"
]

for layout in layouts:
    json_path = os.path.join(layouts_dir, f"{layout}.json")
    dxf_path = os.path.join(planos_cad_dir, f"{layout}.dxf")
    
    print(f"Compilando: {json_path} -> {dxf_path}")
    
    cmd = [
        "python", generator_script,
        "--input", json_path,
        "--output", dxf_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"SUCCESS: {layout} generado con éxito.")
    else:
        print(f"ERROR al compilar {layout}:")
        print(result.stderr)

print("Todas las versiones de planos CAD compiladas.")
