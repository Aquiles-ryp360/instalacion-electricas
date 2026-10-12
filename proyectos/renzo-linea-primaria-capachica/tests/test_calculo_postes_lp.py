# -*- coding: utf-8 -*-
"""
Pruebas unitarias para el cálculo mecánico de postes y retenidas de la Línea Primaria 22.9 kV.
Normativa: CNE Suministro 2011 (Reglas 250, 252)
"""

import sys
import os
import pytest

# Asegurar importación de scripts del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

from calculo_mecanico_postes_lp import (
    analizar_esfuerzos_linea_primaria,
    calcular_vano_viento,
    ESTRUCTURAS_LP,
    TIRO_ROTURA_RETENIDA_KGF
)


def test_analisis_esfuerzos_nueve_estructuras():
    res = analizar_esfuerzos_linea_primaria()
    assert len(res) == 9
    for r in res:
        # Todo poste debe cumplir la exigencia del CNE
        assert r["cumple_cne"] is True
        assert r["fs_poste"] >= 2.0


def test_vano_viento_positivo_y_coherente():
    for i in range(len(ESTRUCTURAS_LP)):
        av = calcular_vano_viento(i)
        assert av > 30.0  # Mínimo vano viento positivo
        assert av < 150.0 # No excede vanos rurales normales


def test_retenidas_mecanicas_factores_seguridad():
    res = analizar_esfuerzos_linea_primaria()
    estructuras_con_retenida = [r for r in res if r["num_retenidas"] > 0]
    assert len(estructuras_con_retenida) == 6  # E-01, E-04, E-05, E-06, E-08, E-09

    for r in estructuras_con_retenida:
        # Factor de seguridad en cable Siemens-Martin 3/8" >= 2.50
        assert r["fs_retenida"] >= 2.50
        assert r["tiro_cable_ret_kgf"] > 0.0
        assert r["tiro_cable_ret_kgf"] < TIRO_ROTURA_RETENIDA_KGF / 2.0
