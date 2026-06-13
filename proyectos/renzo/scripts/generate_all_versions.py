import subprocess
import sys
from pathlib import Path

project_dir = Path(__file__).resolve().parent.parent
repo_dir = project_dir.parent.parent
layouts_dir = project_dir / "datos_diseno" / "layouts"
planos_cad_dir = project_dir / "06_planos" / "fuentes"
generator_script = repo_dir / "herramientas" / "cad" / "scripts" / "dxf_generator.py"

planos_cad_dir.mkdir(parents=True, exist_ok=True)

# List of layouts to compile
layouts = [
    "primer_piso_v1", "primer_piso_v2", "primer_piso_v3",
    "segundo_piso_v1", "segundo_piso_v2", "segundo_piso_v3",
    "tercer_piso_v1", "tercer_piso_v2", "tercer_piso_v3",
    "primer_piso_nuevo", "segundo_piso_nuevo", "tercer_piso_nuevo"
]

fallos = []

for layout in layouts:
    json_path = layouts_dir / f"{layout}.json"
    dxf_path = planos_cad_dir / f"{layout}.dxf"

    print(f"Compilando: {json_path} -> {dxf_path}")

    cmd = [
        sys.executable, str(generator_script),
        "--input", str(json_path),
        "--output", str(dxf_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"SUCCESS: {layout} generado con éxito.")
    else:
        print(f"ERROR al compilar {layout}:")
        print(result.stderr)
        fallos.append(layout)

if fallos:
    print(f"Fallaron {len(fallos)} versiones: {', '.join(fallos)}")
    sys.exit(1)

print("Todas las versiones de planos CAD compiladas.")
