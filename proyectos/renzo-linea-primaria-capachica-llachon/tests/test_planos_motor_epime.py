"""Planos Rev. 7 (motor LP 22,9 kV + formato EPIME): datos y láminas de perfil.

No certifica ingeniería; verifica que el dibujo respeta los resultados del motor.
"""
import sys
from pathlib import Path

import ezdxf
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from planos_motor_epime import (  # noqa: E402
    DIST_GENERAL, ESC_H, XL, XR, _alturas, cargar_motor, cortes_por_longitud, generar,
)


def test_cortes_cubren_todo_sin_exceder_hoja():
    prog = [float(f["progresiva_m"]) for f in cargar_motor()["filas"]]
    cortes = cortes_por_longitud(prog, (XR - XL) * ESC_H / 1000)
    assert cortes[0][0] == 0 and cortes[-1][1] == len(prog) - 1
    assert all(b == c for (_, b), (c, _) in zip(cortes, cortes[1:]))
    assert all(prog[j] - prog[i] <= (XR - XL) * ESC_H / 1000 for i, j in cortes)


def test_conductor_sobre_distancia_de_seguridad_en_postes():
    mot = cargar_motor()
    zt = lambda s: float(np.interp(s, mot["perfil"][:, 0], mot["perfil"][:, 1]))
    for f in mot["filas"]:
        assert _alturas(f["poste"])[1] >= DIST_GENERAL   # amarre inferior sobre la distancia mínima
        assert abs(zt(float(f["progresiva_m"])) - f["cota_m"]) < 1.0


def test_dxf_con_hojas_de_perfil(tmp_path):
    info = generar(tmp_path / "lp.dxf", None)
    doc = ezdxf.readfile(tmp_path / "lp.dxf")
    lays = [l for l in doc.layouts if l.name != "Model"]
    assert len(lays) == info["laminas"] and info["hojas_perfil"] >= 1
    assert len({l.dxf_layout.dxf.taborder for l in lays}) == len(lays)
    assert len(doc.modelspace().query('INSERT[name=="POSTE_LP"]')) == info["estructuras"] == 122
    assert sum(len(l.query('LWPOLYLINE[layer=="PP_CONDUCTOR"]')) for l in lays) == info["estructuras"] - 1
