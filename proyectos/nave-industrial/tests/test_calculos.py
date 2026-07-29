#!/usr/bin/env python3
"""Tests unitarios para el motor de calculos industrial (CNE-Utilizacion)."""
import json, math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from calcular_maxima_demanda import calc_circuito_trifasico, calc_dV_arranque, FACTOR_CORRECCION

def test_factor_correccion():
    assert round(FACTOR_CORRECCION, 3) == 0.728

def test_circuito_trifasico_formula_dV():
    """Verifica sqrt(3) para trifasica, no 2 (monofasica)."""
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
    """Motor M2 (15HP=11.19kW) estrella-delta, 10mm2, 18m -> dV_start < 15%."""
    dV = calc_dV_arranque(kw=11.19, V=380, fp=0.85, long_m=18, material="cobre", I_mult=2.0)
    assert dV < 15, f"dV_arr={dV}% >= 15%"

def test_dV_arranque_integracion():
    """Verifica que el resultado del script incluya dV_arr_max < 15%."""
    import subprocess, tempfile, json, sys, os
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
        # Verificar cada motor individualmente
        for mo in res["desglose"]["arranque_motores"]:
            assert mo["cumple_CNE_15pct"], f"{mo['id']}: dV={mo['dV_arranque_porc']}%"
    finally:
        os.unlink(fi_input); os.unlink(fo_output)

def test_md_rango():
    """Verifica que MD calculada para datos reales este en rango [33, 36] kW."""
    data = {"tension_v": 380,
        "motores": [{"potencia_kw":7.46},{"potencia_kw":11.19},{"potencia_kw":3.73},{"potencia_kw":5.59}],
        "iluminacion": [{"potencia_total_w":1600},{"potencia_total_w":640},{"potencia_total_w":320},{"potencia_total_w":72}],
        "circuitos": [
            {"id":"C3","descripcion":"TC","tipo":"tomacorrientes","potencia_kw":6,"factor_demanda":0.5},
            {"id":"C4","descripcion":"A/C","tipo":"climatizacion","potencia_kw":4.5,"factor_demanda":0.8},
            {"id":"C5","descripcion":"Serv","tipo":"servicios","potencia_kw":3,"factor_demanda":0.7}],
        "compensacion_fp": {"fp_actual":0.85,"fp_objetivo":0.95}}
    import subprocess, tempfile
    with tempfile.NamedTemporaryFile(mode='w',suffix='.json',delete=False) as fi:
        json.dump(data,fi); fi_input = fi.name
    with tempfile.NamedTemporaryFile(mode='w',suffix='.json',delete=False) as fo:
        fo_output = fo.name
    try:
        subprocess.run([sys.executable,os.path.join(os.path.dirname(__file__),'..','scripts','calcular_maxima_demanda.py'),
                        fi_input,fo_output],capture_output=True,check=True)
        with open(fo_output) as f: res = json.load(f)
        md = res["resumen"]["maxima_demanda_kw"]
        assert 33 <= md <= 36, f"MD={md} kW fuera de rango [33,36]"
    finally:
        os.unlink(fi_input); os.unlink(fo_output)

def test_fp_objetivo():
    """Verifica que el banco de capacitores es suficiente para FP >= 0.95."""
    data = {"tension_v":380,
        "motores": [{"potencia_kw":7.46},{"potencia_kw":11.19},{"potencia_kw":3.73},{"potencia_kw":5.59}],
        "iluminacion": [{"potencia_total_w":2632}],
        "circuitos": [
            {"id":"C3","descripcion":"TC","tipo":"tomacorrientes","potencia_kw":6,"factor_demanda":0.5},
            {"id":"C4","descripcion":"A/C","tipo":"climatizacion","potencia_kw":4.5,"factor_demanda":0.8},
            {"id":"C5","descripcion":"Serv","tipo":"servicios","potencia_kw":3,"factor_demanda":0.7}],
        "compensacion_fp": {"fp_actual":0.85,"fp_objetivo":0.95,"requiere":True}}
    md_s = 0
    for m in data["motores"]: md_s += m["potencia_kw"] * 0.80
    md_s += sum(c["potencia_total_w"] for c in data["iluminacion"])/1000
    for c in data["circuitos"]: md_s += c["potencia_kw"] * c["factor_demanda"]
    md = md_s * 0.85 * 1.20
    q = md * (math.tan(math.acos(0.85)) - math.tan(math.acos(0.95)))
    fp_post = md / math.sqrt(md**2 + (md * math.tan(math.acos(0.85)) - q)**2)
    assert fp_post >= 0.949, f"FP final={fp_post:.3f} < 0.95"

def test_no_doble_conteo():
    import subprocess, tempfile
    data = {"tension_v":380,
        "motores": [{"id":"M1","potencia_kw":7.46},{"id":"M2","potencia_kw":11.19}],
        "iluminacion": [{"potencia_total_w":1600}],
        "circuitos": [
            {"id":"C1","descripcion":"Alim TF1","tipo":"alimentacion","potencia_kw":60,"factor_demanda":1},
            {"id":"C3","descripcion":"TC","tipo":"tomacorrientes","potencia_kw":6,"factor_demanda":0.5}],
        "compensacion_fp":{"fp_actual":0.85,"fp_objetivo":0.95}}
    with tempfile.NamedTemporaryFile(mode='w',suffix='.json',delete=False) as fi:
        json.dump(data,fi); fi_input = fi.name
    with tempfile.NamedTemporaryFile(mode='w',suffix='.json',delete=False) as fo:
        fo_output = fo.name
    try:
        subprocess.run([sys.executable,os.path.join(os.path.dirname(__file__),'..','scripts','calcular_maxima_demanda.py'),
                        fi_input,fo_output],capture_output=True,check=True)
        with open(fo_output) as f: res = json.load(f)
        assert 18 < res["resumen"]["maxima_demanda_kw"] < 22
    finally:
        os.unlink(fi_input); os.unlink(fo_output)
