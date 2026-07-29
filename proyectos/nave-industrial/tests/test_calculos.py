#!/usr/bin/env python3
"""Tests unitarios para el motor de calculos industrial (CNE-Utilizacion)."""
import json, math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from calcular_maxima_demanda import calc_circuito_trifasico, FACTOR_CORRECCION

def test_factor_correccion():
    assert round(FACTOR_CORRECCION, 3) == 0.728, f"k_corr={FACTOR_CORRECCION}"

def test_circuito_trifasico_formula_dV():
    """Verifica que usa sqrt(3) para trifasica, no 2 (monofasica)."""
    res = calc_circuito_trifasico(kw=10, V=380, fp=0.85, long_m=50, material="cobre")
    # dV = sqrt(3) * rho * L * I / S * 100 / V
    Ib = 10 * 1000 / (math.sqrt(3) * 380 * 0.85)
    rho = 0.0175
    S = res["seccion_mm2"]
    dV_expected = math.sqrt(3) * rho * 50 * Ib / S * 100 / 380
    assert abs(res["dV_porc"] - round(dV_expected, 2)) < 0.01, \
        f"dV={res['dV_porc']} expected={round(dV_expected,2)}"

def test_circuito_trifasico_itm():
    """ITM debe ser >= 1.25 * Ib, redondeado a multiplo de 10."""
    res = calc_circuito_trifasico(kw=30, V=380, fp=0.85)
    Ib = 30 * 1000 / (math.sqrt(3) * 380 * 0.85)
    assert res["itm_a"] >= math.ceil(Ib * 1.25 / 10) * 10, \
        f"ITM={res['itm_a']} < required {math.ceil(Ib*1.25/10)*10}"

def test_circuito_trifasico_ampacidad():
    """Seccion debe tener ampacidad corregida >= 1.25 * Ib."""
    res = calc_circuito_trifasico(kw=15, V=380, fp=0.85)
    Ib = 15 * 1000 / (math.sqrt(3) * 380 * 0.85)
    tabs = [(1.5, 14), (2.5, 20), (4, 27), (6, 36), (10, 49), (16, 67),
            (25, 91), (35, 112), (50, 141), (70, 179), (95, 220), (120, 258)]
    I_adm = dict(tabs).get(res["seccion_mm2"], 0) * FACTOR_CORRECCION
    assert I_adm >= Ib * 1.25, \
        f"S={res['seccion_mm2']}mm2 I_adm={I_adm:.1f}A < Ib*1.25={Ib*1.25:.1f}A"

def test_no_doble_conteo():
    """Carga completa: motores + iluminacion + servicios, sin alimentadores."""
    import subprocess, tempfile
    data = {
        "tension_v": 380,
        "motores": [{"id": "M1", "potencia_kw": 7.46},
                     {"id": "M2", "potencia_kw": 11.19}],
        "iluminacion": [{"potencia_total_w": 1600}],
        "circuitos": [
            {"id": "C1", "descripcion": "Alim TF1", "tipo": "alimentacion", "potencia_kw": 60, "factor_demanda": 1},
            {"id": "C3", "descripcion": "TC industriales", "tipo": "tomacorrientes", "potencia_kw": 6, "factor_demanda": 0.5},
        ],
        "compensacion_fp": {"fp_actual": 0.85, "fp_objetivo": 0.95}
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as fi:
        json.dump(data, fi); fi_input = fi.name
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as fo:
        fo_output = fo.name
    try:
        subprocess.run([sys.executable,
            os.path.join(os.path.dirname(__file__), '..', 'scripts', 'calcular_maxima_demanda.py'),
            fi_input, fo_output], capture_output=True, check=True)
        with open(fo_output) as f: res = json.load(f)
        md = res["resumen"]["maxima_demanda_kw"]
        # MD esperada: motores(18.65*0.8=14.92) + ilum(1.6) + C3(6*0.5=3) = 19.52
        # *0.85 simultaneidad = 16.59 * 1.20 reserva = 19.91
        assert 18 < md < 22, f"MD={md} fuera de rango 18-22 kW (posible doble conteo)"
    finally:
        os.unlink(fi_input); os.unlink(fo_output)
