import os
import subprocess

script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
base_dir = os.path.dirname(project_dir)
layouts_dir = os.path.join(project_dir, "datos_diseno", "layouts")
planos_cad_dir = os.path.join(project_dir, "06_planos", "fuentes")
generator_script = os.path.join(base_dir, "herramientas", "ia-cad-casas", "scripts", "dxf_generator.py")

os.makedirs(planos_cad_dir, exist_ok=True)

# List of layouts to compile
layouts = [
    "primer_piso_v1", "primer_piso_v2", "primer_piso_v3",
    "segundo_piso_v1", "segundo_piso_v2", "segundo_piso_v3",
    "tercer_piso_v1", "tercer_piso_v2", "tercer_piso_v3",
    "primer_piso_nuevo", "segundo_piso_nuevo", "tercer_piso_nuevo"
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
