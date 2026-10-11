"""
Tests unitarios para el diseño eléctrico y caída de tensión
Proyecto: renzo-linea-primaria-capachica
"""
import pytest
import sys
from pathlib import Path

scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from calculo_caida_tension_mt import calcular_caida_tension_3f

def test_caida_tension_mt_proyecto_real():
    """Verifica que los valores calculados correspondan al proyecto real (P=90kW, L=0.817km)."""
    res = calcular_caida_tension_3f(
        P_kw=90.0,
        fp=0.90,
        V_kv=22.9,
        L_km=0.8166,
        r_ohm_km=0.986,
        x_ohm_km=0.385
    )
    assert abs(res["corriente_A"] - 2.52) < 0.05
    assert abs(res["delta_V_V"] - 3.76) < 0.1
    assert abs(res["delta_V_pct"] - 0.016) < 0.005
    assert res["cumple_norma"] is True  # CNE límite <= 5.0%
    assert res["perdidas_P_kw"] < 0.05
