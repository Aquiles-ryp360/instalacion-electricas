# -*- coding: utf-8 -*-
"""
tests/test_planos_lp.py
Pruebas unitarias de verificación y auditoría de planos de Línea Primaria 22.9 kV:
- Existencia y peso no nulo de las 6 láminas en PDF A3
- Existencia y peso no nulo de los 6 planos en DXF (AutoCAD R2010)
- Existencia de las vistas previas PNG
- Integridad de capas y entidades DXF mediante ezdxf
"""

import os
import pytest
import ezdxf

BASE_PLANOS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "entregables", "planos"))
PREV_PNG = os.path.join(BASE_PLANOS, "preview_png")


def test_existencia_laminas_pdf():
    """Verifica que las 6 láminas oficiales en PDF A3 existan y tengan tamaño adecuado."""
    laminas = [
        "plano_LP01_planta_linea_primaria.pdf",
        "plano_PL01_perfil_longitudinal.pdf",
        "plano_U01_diagrama_unifilar_detalles.pdf",
        "plano_D01_armados_dge_ps1_pa1.pdf",
        "plano_D02_armados_dge_pr1_sab1.pdf",
        "plano_D03_detalles_cimentacion_retenida_pat.pdf"
    ]
    for lam in laminas:
        ruta = os.path.join(BASE_PLANOS, lam)
        assert os.path.exists(ruta), f"Falta lámina PDF: {lam}"
        assert os.path.getsize(ruta) > 20000, f"Lámina PDF vacía o incompleta: {lam}"


def test_existencia_planos_dxf():
    """Verifica que los 6 planos en DXF oficial existan y contengan capas normalizadas."""
    dxfs = [
        ("PLANO_LP01_PLANTA_LINEA_PRIMARIA_22.9KV.dxf", "LP_EJE_MT_22KV"),
        ("PLANO_PL01_PERFIL_LONGITUDINAL_LP_CAPACHICA.dxf", "PL_TERRENO_NATURAL"),
        ("PLANO_U01_DIAGRAMA_UNIFILAR_LP_SAB1.dxf", "U_LINEAS_MT"),
        ("PLANO_D01_ARMADOS_DGE_PS1_PA1.dxf", "D_ESTRUCTURA"),
        ("PLANO_D02_ARMADOS_DGE_PR1_SAB1.dxf", "D_ESTRUCTURA"),
        ("PLANO_D03_DETALLES_CIMENTACION_RETENIDA_PAT.dxf", "D_CIMENTACION")
    ]
    for nombre_dxf, capa_esperada in dxfs:
        ruta = os.path.join(BASE_PLANOS, nombre_dxf)
        assert os.path.exists(ruta), f"Falta plano DXF: {nombre_dxf}"
        assert os.path.getsize(ruta) > 10000, f"Plano DXF corrupto o vacío: {nombre_dxf}"
        
        # Validar con ezdxf
        doc = ezdxf.readfile(ruta)
        assert capa_esperada in doc.layers, f"Capa {capa_esperada} no encontrada en {nombre_dxf}"
        msp = doc.modelspace()
        assert len(list(msp)) > 0, f"ModelSpace vacío en {nombre_dxf}"


def test_existencia_previews_png():
    """Verifica que los 6 renders PNG de alta definición existan."""
    pngs = [
        "plano_LP01_planta_linea_primaria.png",
        "plano_PL01_perfil_longitudinal.png",
        "plano_U01_diagrama_unifilar_detalles.png",
        "plano_D01_armados_dge_ps1_pa1.png",
        "plano_D02_armados_dge_pr1_sab1.png",
        "plano_D03_detalles_cimentacion_retenida_pat.png"
    ]
    for p in pngs:
        ruta = os.path.join(PREV_PNG, p)
        assert os.path.exists(ruta), f"Falta vista previa PNG: {p}"
        assert os.path.getsize(ruta) > 50000, f"Vista previa PNG incompleta: {p}"


def test_paquete_autocad_lp_a3():
    """Verifica el paquete DXF A3 para AutoCAD del alcance exclusivo de línea primaria."""
    autocad_dir = os.path.join(BASE_PLANOS, "autocad_lp")
    zip_path = os.path.join(BASE_PLANOS, "planos_autocad_linea_primaria_capachica.zip")
    dxfs = [
        "LP-01_PLANTA_LINEA_PRIMARIA_A3_AUTOCAD.dxf",
        "PL-01_PERFIL_LONGITUDINAL_A3_AUTOCAD.dxf",
        "U-01_DIAGRAMA_UNIFILAR_MT_A3_AUTOCAD.dxf",
        "D-01_ARMADOS_PS1_PA1_A3_AUTOCAD.dxf",
        "D-02_ARMADOS_PR1_SAB1_A3_AUTOCAD.dxf",
        "D-03_CIMENTACION_RETENIDA_PAT3_A3_AUTOCAD.dxf",
    ]

    assert os.path.exists(zip_path), "Falta ZIP del paquete AutoCAD LP"
    assert os.path.getsize(zip_path) > 50000, "ZIP AutoCAD LP vacío o incompleto"

    for nombre in dxfs:
        ruta = os.path.join(autocad_dir, nombre)
        assert os.path.exists(ruta), f"Falta DXF AutoCAD: {nombre}"
        assert os.path.getsize(ruta) > 50000, f"DXF AutoCAD incompleto: {nombre}"
        doc = ezdxf.readfile(ruta)
        auditor = doc.audit()
        assert len(auditor.errors) == 0, f"DXF con errores de auditoría: {nombre}"
        for capa in ["00_MARCO_ROTULO", "09_TEXTOS", "10_TABLAS_LEYENDAS"]:
            assert capa in doc.layers, f"Capa {capa} no encontrada en {nombre}"
        assert len(list(doc.modelspace())) > 25, f"ModelSpace insuficiente en {nombre}"
