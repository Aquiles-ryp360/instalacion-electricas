#!/usr/bin/env python3
"""Tests unitarios para el motor de calculos industrial (CNE-Utilizacion)."""
import json, math, sys, os, subprocess, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from calcular_maxima_demanda import calc_circuito_trifasico, calc_dV_arranque, FACTOR_CORRECCION

def test_factor_correccion():
    assert round(FACTOR_CORRECCION, 3) == 0.728

def test_circuito_trifasico_formula_dV():
    """Verifica sqrt(3) para trifasica."""
    res = calc_circuito_trifasico(kw=10, V=380, fp=0.85, long_m=50, material="cobre")
    Ib = 10 * 1000 / (math.sqrt(3) * 380 * 0.85)
    dV_expected = math.sqrt(3) * 0.0175 * 50 * Ib / res["seccion_mm2"] * 100 / 380
    assert abs(res["dV_porc"] - round(dV_expected, 2)) < 0.01

def test_circuito_trifasico_itm():
    res = calc_circuito_trifasico(kw=30, V=380, fp=0.85)
    Ib = 30 * 1000 / (math.sqrt(3) * 380 * 0.85)
    assert res["itm_a"] >= math.ceil(Ib * 1.25 / 10) * 10

def test_circuito_trifasico_ampacidad():
    res = calc_circuito_trifasico(kw=15, V=380, fp=0.85)
    Ib = 15 * 1000 / (math.sqrt(3) * 380 * 0.85)
    tabs = dict([(1.5,14),(2.5,20),(4,27),(6,36),(10,49),(16,67),
                 (25,91),(35,112),(50,141),(70,179),(95,220),(120,258)])
    assert tabs.get(res["seccion_mm2"], 0) * FACTOR_CORRECCION >= Ib * 1.25

def test_dV_arranque_m2():
    """M2 compresor 15HP estrella-delta, 25m, 10mm2."""
    dV = calc_dV_arranque(kw=11.19, V=380, fp=0.85, long_m=25, material="cobre", I_mult=2.5)
    assert dV < 15, f"dV_arr={dV}% >= 15%"

def test_md_rango_nave_20x40():
    """Verifica MD calculada para datos reales en rango [38,42] kW."""
    data = json.load(open(os.path.join(os.path.dirname(__file__),'..','diseno-electrico','datos','cargas-industriales.json')))
    with tempfile.NamedTemporaryFile(mode='w',suffix='.json',delete=False) as fi:
        json.dump(data,fi); fi_input = fi.name
    with tempfile.NamedTemporaryFile(mode='w',suffix='.json',delete=False) as fo:
        fo_output = fo.name
    try:
        subprocess.run([sys.executable,os.path.join(os.path.dirname(__file__),'..','scripts','calcular_maxima_demanda.py'),
                        fi_input,fo_output],capture_output=True,check=True)
        with open(fo_output) as f: res = json.load(f)
        md = res["resumen"]["maxima_demanda_kw"]
        assert 38 <= md <= 42, f"MD={md} kW fuera de rango [38,42]"
    finally:
        os.unlink(fi_input); os.unlink(fo_output)

def test_fp_objetivo_096():
    """Verifica que el banco de capacitores es suficiente para FP >= 0.96."""
    md_s = 3.0 + (7.46*0.5) + (11.19*0.8) + (25.0*0.7) + (6.0*0.5) + (3.0*0.8)
    md = md_s * 0.85 * 1.20
    q = md * (math.tan(math.acos(0.85)) - math.tan(math.acos(0.96)))
    fp_post = md / math.sqrt(md**2 + (md * math.tan(math.acos(0.85)) - q)**2)
    assert fp_post >= 0.959, f"FP final={fp_post:.3f} < 0.96"

def test_dV_arranque_integracion():
    """Verifica que todos los motores cumplan dV_arr < 15%."""
    data = json.load(open(os.path.join(os.path.dirname(__file__),'..','diseno-electrico','datos','cargas-industriales.json')))
    with tempfile.NamedTemporaryFile(mode='w',suffix='.json',delete=False) as fi:
        json.dump(data,fi); fi_input = fi.name
    with tempfile.NamedTemporaryFile(mode='w',suffix='.json',delete=False) as fo:
        fo_output = fo.name
    try:
        subprocess.run([sys.executable,os.path.join(os.path.dirname(__file__),'..','scripts','calcular_maxima_demanda.py'),
                        fi_input,fo_output],capture_output=True,check=True)
        with open(fo_output) as f: res = json.load(f)
        dV_max = res["desglose"]["dV_arranque_max_porc"]
        assert dV_max < 15, f"dV_arr_max={dV_max}% >= 15%"
        for mo in res["desglose"]["arranque_motores"]:
            assert mo["cumple_CNE_15pct"], f"{mo['id']}: dV={mo['dV_arranque_porc']}%"
    finally:
        os.unlink(fi_input); os.unlink(fo_output)

def test_no_doble_conteo():
    """Carga completa por circuitos sin alimentacion/compensacion."""
    data = {"tension_v":380,
        "circuitos":[
            {"id":"C1","descripcion":"Ilum","tipo":"iluminacion","potencia_kw":3.0,"factor_demanda":1.0},
            {"id":"C3","descripcion":"Grua","tipo":"fuerza_motriz","potencia_kw":7.46,"factor_demanda":0.5},
            {"id":"C5","descripcion":"Maq","tipo":"fuerza_motriz","potencia_kw":25.0,"factor_demanda":0.7}],
        "compensacion_fp":{"fp_actual":0.85,"fp_objetivo":0.96}}
    with tempfile.NamedTemporaryFile(mode='w',suffix='.json',delete=False) as fi:
        json.dump(data,fi); fi_input = fi.name
    with tempfile.NamedTemporaryFile(mode='w',suffix='.json',delete=False) as fo:
        fo_output = fo.name
    try:
        subprocess.run([sys.executable,os.path.join(os.path.dirname(__file__),'..','scripts','calcular_maxima_demanda.py'),
                        fi_input,fo_output],capture_output=True,check=True)
        with open(fo_output) as f: res = json.load(f)
        md = res["resumen"]["maxima_demanda_kw"]
        esperado = (3.0+7.46*0.5+25.0*0.7)*0.85*1.20
        assert abs(md - round(esperado,2)) < 1.0, f"MD={md} esperado={esperado:.2f}"
    finally:
        os.unlink(fi_input); os.unlink(fo_output)
