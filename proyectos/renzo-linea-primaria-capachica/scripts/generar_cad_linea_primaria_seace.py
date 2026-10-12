#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/generar_cad_linea_primaria_seace.py
Integración y exportación de modelos paramétricos CAD (3D y DXF) de Línea Primaria 22.9 kV
utilizando el framework SEACE CAD Intelligence (seace_cad_intelligence).
Proyecto: Línea Primaria 22.9 kV Sector Chifrón (Capachica, Puno)
Autor: Br. Renzo Gabriel Mamani Galindo (Cód. 228447)
"""

import os
import sys

# Agregar la ruta del repositorio seace-cad-intelligence al sys.path
RUTA_SEACE_REPO = os.path.abspath(r"C:\Users\renzo\workspace\seace-cad-intelligence")
if RUTA_SEACE_REPO not in sys.path:
    sys.path.insert(0, RUTA_SEACE_REPO)

try:
    from seace_cad_intelligence.cad_bridge.export_manager import CADCodeExporter
    from seace_cad_intelligence.cad_bridge.parametric_primary_line import PrimaryLineParametricGenerator
except ImportError as err:
    print(f"[-] Error al importar el framework seace_cad_intelligence: {err}")
    sys.exit(1)


def generar_entregables_cad_linea_primaria():
    """Genera planos DXF oficiales y scripts CadQuery 3D para la Línea Primaria."""
    directorio_base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "entregables", "planos", "cad_linea_primaria"))
    directorio_scripts_3d = os.path.join(directorio_base, "scripts_cadquery_3d")
    os.makedirs(directorio_base, exist_ok=True)
    os.makedirs(directorio_scripts_3d, exist_ok=True)

    componentes = [
        {"tipo": "ps1", "nombre_dxf": "PLANO_DGE_PS1_SUSPENSION_22.9KV.dxf", "nombre_py": "armado_dge_ps1_3d.py"},
        {"tipo": "pa1", "nombre_dxf": "PLANO_DGE_PA1_ANGULO_22.9KV.dxf", "nombre_py": "armado_dge_pa1_3d.py"},
        {"tipo": "pr1", "nombre_dxf": "PLANO_DGE_PR1_RETENCION_22.9KV.dxf", "nombre_py": "armado_dge_pr1_3d.py"},
        {"tipo": "sab1", "nombre_dxf": "PLANO_DGE_SAB1_BIPOSTE_100KVA.dxf", "nombre_py": "armado_dge_sab1_3d.py"},
        {"tipo": "retenida", "nombre_dxf": "PLANO_RETENIDA_R1_TIERRA_45G.dxf", "nombre_py": "retenida_r1_3d.py"},
        {"tipo": "poste", "nombre_dxf": "PLANO_POSTE_CAC_12M_400DAN.dxf", "nombre_py": "poste_cac_12_400_3d.py", "params": {"modelo": "12/400"}}
    ]

    print("\n" + "="*80)
    print("GENERADOR DE PLANOS Y MODELOS CAD — LÍNEA PRIMARIA 22.9 kV (SEACE CAD INTELLIGENCE)")
    print("="*80)

    for comp in componentes:
        params = comp.get("params", {})
        ruta_dxf = os.path.join(directorio_base, comp["nombre_dxf"])
        ruta_py = os.path.join(directorio_scripts_3d, comp["nombre_py"])

        # 1. Exportar archivo DXF profesional (compatible con AutoCAD)
        CADCodeExporter.exportar_dxf(comp["tipo"], ruta_dxf, params)
        tamano_dxf_kb = os.path.getsize(ruta_dxf) / 1024.0
        print(f"[OK DXF] {comp['nombre_dxf']:<42} -> {tamano_dxf_kb:.1f} KB")

        # 2. Exportar script CadQuery paramétrico 3D
        codigo_3d = CADCodeExporter.generar_codigo(comp["tipo"], params, motor="cadquery")
        with open(ruta_py, "w", encoding="utf-8") as f:
            f.write(codigo_3d)
        print(f"[OK 3D ] {comp['nombre_py']:<42} -> Generado")

    print("="*80)
    print(f"[EXITO] Planos DXF y scripts paramétricos exportados en:\n  {directorio_base}\n")


if __name__ == "__main__":
    generar_entregables_cad_linea_primaria()
