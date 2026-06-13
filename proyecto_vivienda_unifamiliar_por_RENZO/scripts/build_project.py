#!/usr/bin/env python3
"""
Orquestador Principal del Expediente Técnico
Compila todo el proyecto en un solo comando:
1. Compilación de layouts de fondo (JSON a DXF).
2. Generación de planos eléctricos y diagramas (IE-02 a IE-06).
3. Actualización de tablas de metrados y presupuestos en LaTeX.
4. Compilación del documento maestro main.tex (LaTeX) para generar build/main.pdf.
"""

import os
import sys
import subprocess
from pathlib import Path

# Configurar codificacion de consola para evitar UnicodeEncodeError en Windows
if sys.platform.startswith('win'):
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Obtener rutas
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent

def run_script(script_name, cwd=PROJECT_DIR):
    script_path = SCRIPT_DIR / script_name
    print(f"\n====== Ejecutando: {script_name} ======")
    cmd = [sys.executable, str(script_path)]
    result = subprocess.run(cmd, cwd=str(cwd))
    if result.returncode != 0:
        print(f"[ERROR] El script {script_name} falló.")
        sys.exit(1)
    print(f"[OK] {script_name} completado.")

def compile_latex():
    print("\n====== Compilando Documento LaTeX (main.tex) ======")
    # Crear directorio build si no existe
    os.makedirs(PROJECT_DIR / "build", exist_ok=True)
    
    cmd = [
        "pdflatex",
        "-interaction=nonstopmode",
        "-output-directory=build",
        "main.tex"
    ]
    
    # Primera pasada
    print("-> Primera pasada para resolver índices y referencias...")
    result1 = subprocess.run(cmd, cwd=str(PROJECT_DIR))
    if result1.returncode != 0:
        print("[ERROR] en la primera pasada de compilación LaTeX.")
        sys.exit(1)
        
    # Segunda pasada
    print("-> Segunda pasada para resolver referencias cruzadas...")
    result2 = subprocess.run(cmd, cwd=str(PROJECT_DIR))
    if result2.returncode != 0:
        print("[ERROR] en la segunda pasada de compilación LaTeX.")
        sys.exit(1)
        
    pdf_path = PROJECT_DIR / "build" / "main.pdf"
    if pdf_path.exists():
        print(f"[SUCCESS] ¡EXPEDIENTE COMPILADO CON ÉXITO! PDF en: {pdf_path}")
    else:
        print("[ERROR] No se encontró el PDF final.")
        sys.exit(1)

def main():
    print("=============================================================")
    print("      INICIANDO PIPELINE DE COMPILACIÓN DEL EXPEDIENTE       ")
    print("=============================================================")
    
    # 1. Compilar versiones y layouts base
    run_script("generate_all_versions.py")
    
    # 2. Generar planos eléctricos (luz, tomacorriente, unifilar, puesta a tierra)
    run_script("generate_electrical_drawings.py")
    
    # 3. Actualizar metrados y presupuestos en LaTeX
    run_script("update_latex_metrados.py")
    
    # 4. Compilar documento LaTeX final
    compile_latex()
    
    print("\n=============================================================")
    print("           PROCESO DE COMPILACIÓN COMPLETADO                 ")
    print("=============================================================")

if __name__ == "__main__":
    main()
