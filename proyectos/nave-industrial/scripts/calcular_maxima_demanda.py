#!/usr/bin/env python3
"""Calculo de maxima demanda para instalacion industrial segun CNE-Utilizacion."""
import json, math, sys
from pathlib import Path

# Factores de correccion CNE (Tabla 5-IV)
FACTOR_TEMP_40C = 0.91       # k_T para 40°C, cable THW 90°C
FACTOR_AGRUP_4_COND = 0.80   # k_n para 4 conductores en tubo
FACTOR_CORRECCION = FACTOR_TEMP_40C * FACTOR_AGRUP_4_COND  # 0.728

def calc_dV_arranque(kw, V, fp, long_m, material="cobre", I_mult=6.0):
    rho = 0.0175 if material == "cobre" else 0.0288
    Ib = kw * 1000 / (math.sqrt(3) * V * fp)
    I_start = Ib * I_mult
    tabs = [(1.5, 14), (2.5, 20), (4, 27), (6, 36), (10, 49), (16, 67),
            (25, 91), (35, 112), (50, 141), (70, 179), (95, 220), (120, 258)]
    I_adm_corregida = [(s, ia * FACTOR_CORRECCION) for s, ia in tabs]
    S = next((s for s, ia in I_adm_corregida if Ib * 1.25 <= ia), 120)
    if S == 0: return 999
    dV = math.sqrt(3) * rho * long_m * I_start / S * 100 / V
    return round(dV, 2)

def calc_circuito_trifasico(kw, V=380, fp=0.85, long_m=10, material="cobre", dV_max=2.5):
    rho = 0.0175 if material == "cobre" else 0.0288
    Ib = kw * 1000 / (math.sqrt(3) * V * fp)
    # CNE Tabla 5-I para THW 90°C a 40°C ambiente, con correccion
    tabs = [(1.5, 14), (2.5, 20), (4, 27), (6, 36), (10, 49), (16, 67),
            (25, 91), (35, 112), (50, 141), (70, 179), (95, 220), (120, 258)]
    I_adm_corregida = [(s, ia * FACTOR_CORRECCION) for s, ia in tabs]
    S = next((s for s, ia in I_adm_corregida if Ib * 1.25 <= ia), 120)
    # Caida de tension trifasica: dV = sqrt(3) * rho * L * Ib / S
    dV = math.sqrt(3) * rho * long_m * Ib / S * 100 / V if S > 0 else 100
    return {"corriente_a": round(Ib, 2), "seccion_mm2": S,
            "dV_porc": round(dV, 2), "cumple_dV": dV <= dV_max,
            "itm_a": max(10, math.ceil(Ib * 1.25 / 10) * 10),
            "factor_correccion_total": round(FACTOR_CORRECCION, 3)}

def main():
    i, o = sys.argv[1], sys.argv[2]
    with open(i) as f:
        data = json.load(f)
    V = data.get("tension_v", 380)

    # Iluminacion: solo sumar potencias de luminarias
    p_ilum = sum(c.get("potencia_total_w", 0) for c in data.get("iluminacion", [])) / 1000

    # Motores: suma directa de potencia en kW de cada motor (evita doble conteo)
    motores = data.get("motores", [])
    p_motores = sum(m.get("potencia_kw", 0) for m in motores)
    fd_m = 0.80
    p_md_motores = p_motores * fd_m

    # Circuitos derivados de servicios (C3=TC industriales, C4=climatizacion, C5=servicios)
    # NO incluir C1 y C2 porque alimentan motores e iluminacion ya contabilizados
    circuitos = data.get("circuitos", [])
    p_servicios = 0
    detalle_circuitos = []
    for c in circuitos:
        if c.get("tipo") in ("alimentacion",):
            continue
        p = c.get("potencia_kw", 0) * c.get("factor_demanda", 1)
        p_servicios += p
        detalle_circuitos.append({"id": c["id"], "desc": c["descripcion"],
                                  "potencia_kw": c.get("potencia_kw", 0),
                                  "fd": c.get("factor_demanda", 1),
                                  "md_kw": round(p, 2)})

    # Subtotal sin simultaneidad
    md_subtotal = p_md_motores + p_ilum + p_servicios

    # Factor de simultaneidad general
    fd_simultaneidad = 0.85
    md_sim = md_subtotal * fd_simultaneidad

    # Reserva para crecimiento futuro (+20%)
    reserva_pct = 0.20
    md_final = md_sim * (1 + reserva_pct)

    I = md_final * 1000 / (math.sqrt(3) * V * 0.9)
    alim = calc_circuito_trifasico(md_final, V)

    # Arranque motores — verificar dV con datos especificos de cada motor
    motores_data = []
    for mo in motores:
        kw = mo.get("potencia_kw", 0)
        lm = mo.get("longitud_m", 50)
        Sc = mo.get("seccion_mm2", 6)
        fp_m = mo.get("fp", 0.85)
        # Usar corriente de arranque del JSON si existe, sino estimar 6x In
        I_start = mo.get("corriente_arranque_a", kw*1000/(math.sqrt(3)*V*0.85)*6)
        rho = 0.0175
        dV_s = round(math.sqrt(3) * rho * lm * I_start / Sc * 100 / V, 2)
        motores_data.append({"id": mo.get("id", ""),
                             "potencia_kw": kw, "seccion_mm2": Sc,
                             "longitud_m": lm, "I_arranque_a": round(I_start,1),
                             "dV_arranque_porc": dV_s,
                             "tipo_arranque": mo.get("tipo_arranque","DOL"),
                             "cumple_CNE_15pct": dV_s <= 15})
    max_dV_arr = max(m["dV_arranque_porc"] for m in motores_data)

    # Compensacion FP
    fp_a = data.get("compensacion_fp", {}).get("fp_actual", 0.85)
    fp_t = data.get("compensacion_fp", {}).get("fp_objetivo", 0.95)
    q = md_final * (math.tan(math.acos(fp_a)) - math.tan(math.acos(fp_t)))

    data["maxima_demanda_kw"] = round(md_final, 2)
    data["corriente_total_a"] = round(I, 2)
    data["alimentador_principal_itm_a"] = alim["itm_a"]
    data["alimentador_principal_seccion_mm2"] = alim["seccion_mm2"]

    res = {"sistema": f"3F ~ {V}V / 60Hz", "norma": "CNE-Utilizacion 2006",
           "factores_correccion": {"temperatura_40c": FACTOR_TEMP_40C,
                                   "agrupamiento_4_cond": FACTOR_AGRUP_4_COND,
                                   "total_aplicado": round(FACTOR_CORRECCION, 3)},
           "desglose": {"iluminacion_kw": round(p_ilum, 2),
                        "motores_kw": round(p_motores, 2),
                        "motores_md_kw": round(p_md_motores, 2),
                        "servicios_circuitos": detalle_circuitos,
                        "subtotal_md_kw": round(md_subtotal, 2),
                        "fd_simultaneidad": fd_simultaneidad,
                        "md_con_simultaneidad_kw": round(md_sim, 2),
                        "reserva_pct": reserva_pct,
                        "reserva_kw": round(md_sim * reserva_pct, 2),
            "arranque_motores": motores_data,
            "dV_arranque_max_porc": max_dV_arr},
           "resumen": {"maxima_demanda_kw": round(md_final, 2),
                       "corriente_total_a": round(I, 2),
                       "alimentador": alim,
                       "banco_capacitores_kvar": round(q)}}

    Path(o).parent.mkdir(parents=True, exist_ok=True)
    with open(o, "w") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    with open(i, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"MD: {res['resumen']['maxima_demanda_kw']} kW | "
          f"I: {res['resumen']['corriente_total_a']} A | "
          f"Alim: {alim['seccion_mm2']}mm2 / {alim['itm_a']}A | "
          f"FP: {round(q)} kVar | "
          f"k_corr: {FACTOR_CORRECCION:.3f} | "
          f"dV_arr_max: {max_dV_arr}%")

if __name__ == "__main__":
    main()
