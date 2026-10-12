# -*- coding: utf-8 -*-
"""
Pruebas unitarias para la verificación geotécnica de cimentaciones por el Método de Sulzberger.
Normativa: CNE Suministro 2011 y DGE ER.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

from calculo_cimentacion_sulzberger_lp import (
    calcular_sulzberger_poste,
    calcular_bloque_anclaje_retenida,
    verificar_cimentaciones_completas
)


def test_sulzberger_todas_estructuras_conformes():
    rep = verificar_cimentaciones_completas()
    assert len(rep) == 9
    for r in rep:
        assert r["sulz_conforme"] is True
        assert r["fs_sulzberger"] >= 1.50
        assert r["estado_general"] == "CONFORME"


def test_bloque_anclaje_arrancamiento():
    res = calcular_bloque_anclaje_retenida(tiro_cable_kgf=1078.27)
    assert res["aplica"] is True
    assert res["conforme"] is True
    assert res["fs_arrancamiento"] >= 2.0
    assert res["resistencia_total_kgf"] > 2000.0
