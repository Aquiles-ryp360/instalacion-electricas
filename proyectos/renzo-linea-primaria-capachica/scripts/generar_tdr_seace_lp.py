#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/generar_tdr_seace_lp.py
Generador automático del Pliego de Términos de Referencia y Especificaciones Técnicas SEACE
para la Línea Primaria 22.9 kV Capachica utilizando el benchmark adjudicado de Electro Puno.
Proyecto: Línea Primaria 22.9 kV Sector Chifrón (Capachica, Puno)
Autor: Br. Renzo Gabriel Mamani Galindo (Cód. 228447)
"""

import os
import sys

RUTA_SEACE_REPO = os.path.abspath(r"C:\Users\renzo\workspace\seace-cad-intelligence")
if RUTA_SEACE_REPO not in sys.path:
    sys.path.insert(0, RUTA_SEACE_REPO)

from seace_cad_intelligence.storage.repository import AdaptiveKnowledgeRepository
from seace_cad_intelligence.templates.tdr_generator import EngineeringTDRGenerator


def generar_tdr_linea_primaria_oficial():
    db_path = os.path.join(RUTA_SEACE_REPO, "data", "seace_intelligence.db")
    repo = AdaptiveKnowledgeRepository(db_path=db_path)

    # Obtener el precedente ganador de licitación pública en Puno
    precedente = repo.obtener_por_id("LP-SM-15-2024-ELECTROPUNO")

    doc = EngineeringTDRGenerator.generar_tdr_linea_primaria(
        titulo_nuevo_proyecto="INSTALACIÓN DE LÍNEA PRIMARIA EN MEDIA TENSIÓN 22.9 kV Y SUBESTACIÓN BIPOSTE 100 kVA - SECTOR CHIFRÓN (CAPACHICA, PUNO)",
        autor="Br. Renzo Gabriel Mamani Galindo",
        codigo_estudiante="228447",
        tension_kv=22.9,
        longitud_km=0.817,
        conductor="AAAC 35 mm² (NTP 370.258)",
        altitud_msnm=3850.0,
        num_estructuras=9,
        proyecto_precedente=precedente
    )

    ruta_salida = os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "expediente", "02_tdr_especificaciones_tecnicas_linea_primaria_seace.md"
    ))
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)

    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(doc)

    print(f"[OK] Documento de Términos de Referencia SEACE generado en:\n  {ruta_salida}")


if __name__ == "__main__":
    generar_tdr_linea_primaria_oficial()
