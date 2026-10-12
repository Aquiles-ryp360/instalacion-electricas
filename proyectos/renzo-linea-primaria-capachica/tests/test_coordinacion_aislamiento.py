# -*- coding: utf-8 -*-
"""
Pruebas unitarias para la coordinación de aislamiento a gran altitud (3,850 msnm).
Normativa: IEC 60071-1, IEC 60071-2 y CNE Suministro Regla 242.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

from coordinacion_aislamiento_lp import calcular_coordinacion_aislamiento_altitud


def test_coordinacion_aislamiento_capachica():
    res = calcular_coordinacion_aislamiento_altitud()
    assert res["cumple_aislamiento"] is True
    # Factor de corrección a 3,850 msnm debe ser > 1.20
    assert res["ka_cne"] > 1.20
    assert res["ka_iec"] > 1.30
    # BIL normalizado debe ser al menos 150 kV
    assert res["bil_normalizado_kv"] in [150.0, 170.0]
    # Línea de fuga real supera el mínimo requerido
    assert res["linea_fuga_real_mm"] >= res["linea_fuga_minima_mm"]
    assert res["margen_fuga_pct"] > 0.0
    # Pararrayos
    assert res["mcov_seleccionado_kv"] == 17.5
    assert res["ur_pararrayos_kv"] == 21.0
