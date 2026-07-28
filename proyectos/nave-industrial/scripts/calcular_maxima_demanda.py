#!/usr/bin/env python3
"""Calculo de maxima demanda para instalacion industrial."""
import json, math, sys
from pathlib import Path

def I_motor(kw, V, fp, eff):
    return kw * 1000 / (math.sqrt(3) * V * fp * eff)

def calc_circuito(kw, V=380, fp=0.85, long_m=10, material="cobre", dV_max=2.5):
    rho = 0.0175 if material == "cobre" else 0.0288
    Ib = kw * 1000 / (math.sqrt(3) * V * fp)
    tabs = [(1.5,14),(2.5,20),(4,27),(6,36),(10,49),(16,67),(25,91),(35,112),(50,141),(70,179),(95,220),(120,258)]
    S = next((s for s,ia in tabs if Ib*1.25 <= ia), 120)
    dV = 2 * rho * long_m * Ib / S * 100 / V if S else 100
    return {"corriente_a": round(Ib,2), "seccion_mm2": S, "dV_porc": round(dV,2), "cumple_dV": dV <= dV_max,
            "itm_a": max(10, math.ceil(Ib * 1.25 / 10) * 10)}

def main():
    i, o = sys.argv[1], sys.argv[2]
    with open(i) as f: data = json.load(f)
    V = data.get("tension_v", 380)
    md = 0
    # motores
    fd_m = 0.80
    p_m = sum(m.get("potencia_kw",0) for m in data.get("motores",[]))
    # iluminacion
    p_ilum = sum(c.get("potencia_total_w",0) for c in data.get("iluminacion",[]))/1000
    # circuitos
    p_c = sum(c.get("potencia_kw",0)*c.get("factor_demanda",1) for c in data.get("circuitos",[]))
    md = (p_m * fd_m + p_ilum + p_c) * 0.85
    I = md * 1000 / (math.sqrt(3) * V * 0.9)
    alim = calc_circuito(md, V)
    # FP
    fp_a, fp_t = data.get("compensacion_fp",{}).get("fp_actual",0.85), data.get("compensacion_fp",{}).get("fp_objetivo",0.95)
    q = md * (math.tan(math.acos(fp_a)) - math.tan(math.acos(fp_t)))
    data["maxima_demanda_kw"] = round(md,2)
    data["corriente_total_a"] = round(I,2)
    data["alimentador_principal_itm_a"] = alim["itm_a"]
    data["alimentador_principal_seccion_mm2"] = alim["seccion_mm2"]
    res = {"sistema": f"3F ~ {V}V / 60Hz","resumen":{
        "potencia_motores_kw": round(p_m,2),"potencia_iluminacion_kw": round(p_ilum,2),
        "potencia_circuitos_kw": round(p_c,2),"maxima_demanda_kw": round(md,2),
        "corriente_total_a": round(I,2),"alimentador": alim,
        "banco_capacitores_kvar": round(q)}}
    Path(o).parent.mkdir(parents=True,exist_ok=True)
    with open(o,"w") as f: json.dump(res,f,indent=2,ensure_ascii=False)
    with open(i,"w") as f: json.dump(data,f,indent=2,ensure_ascii=False)
    print(f"MD: {res['resumen']['maxima_demanda_kw']} kW | I: {res['resumen']['corriente_total_a']} A | FP: {round(q)} kVar")

if __name__=="__main__": main()
