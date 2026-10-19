"""Planos formato EPIME Rev. 6: reglas de la distribución académica y láminas.

No certifica ingeniería; solo que el generador respeta sus propias reglas.
"""
import math
import sys
from pathlib import Path

import ezdxf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from planos_formato_epime import (  # noqa: E402
    ANCLAJE_CADA, VANO_MAX, generar, leer_segmentos, proponer_estructuras,
)


def test_distribucion_respeta_vano_anclaje_y_extremos():
    segs = leer_segmentos()
    filas = proponer_estructuras(segs)
    vanos = [float(f["vano_anterior_m"]) for f in filas[1:]]
    assert max(vanos) <= VANO_MAX + 0.01
    assert filas[0]["armado"] == filas[-1]["armado"] == "PR-1"
    eje = [p for s in segs.values() for p in s]
    assert math.dist(eje[0], (float(filas[0]["este_m"]), float(filas[0]["norte_m"]))) < 0.01
    assert math.dist(eje[-1], (float(filas[-1]["este_m"]), float(filas[-1]["norte_m"]))) < 0.01
    desde = 0.0
    for f, v in zip(filas[1:], vanos):
        desde += v
        assert desde < ANCLAJE_CADA + VANO_MAX
        if f["armado"] == "PR-1":
            desde = 0.0


def test_laminas_con_taborder_unico(tmp_path):
    info = generar(tmp_path / "lp.dxf", tmp_path / "e.csv", None)
    doc = ezdxf.readfile(tmp_path / "lp.dxf")
    lays = [l for l in doc.layouts if l.name != "Model"]
    assert len(lays) == info["laminas"]
    assert len({l.dxf_layout.dxf.taborder for l in lays}) == len(lays)
    assert len(doc.modelspace().query('INSERT[name=="POSTE_LP"]')) == info["estructuras"]
