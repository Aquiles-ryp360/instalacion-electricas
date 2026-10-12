#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/calculo_mecanico_postes_lp.py
Cálculo Mecánico de Esfuerzos en Postes y Retenidas de la Línea Primaria 22.9 kV
Proyecto: Línea Primaria y Subestación SAB-1 - Sector Chifrón (Capachica, Puno)
Normativa: CNE Suministro 2011 (Reglas 250, 252) y Norma DGE RD 018-2003-EM/DGE
Autor: Br. Renzo Gabriel Mamani Galindo (Cód. 228447)
"""

import math
import csv
import os

# -----------------------------------------------------------------------------
# PARÁMETROS CANÓNICOS DE LA LÍNEA PRIMARIA
# -----------------------------------------------------------------------------
# Conductor AAAC 35 mm² (NTP 370.258)
DIAM_COND_M = 0.0075
PESO_COND_KG_M = 0.0945
TIRO_ROTURA_COND_KGF = 1040.0

# Tiros por fase (3 fases) calculados por la Ecuación de Truxa (Vano crítico 115.59 m)
TIRO_HIP_I_KGF = 253.62    # Hipótesis I: Viento Máximo 75 km/h (+10°C)
TIRO_HIP_II_KGF = 358.25   # Hipótesis II: Hielo 6 mm, Viento 37.5 km/h (-5°C)
TIRO_HIP_III_KGF = 310.81  # Hipótesis III: Temperatura Mínima -15°C
TIRO_HIP_IV_KGF = 126.83   # Hipótesis IV: Temperatura Máxima +35°C
TIRO_HIP_V_KGF = 187.20    # Hipótesis V: Templado EDS +15°C

# Presión de viento a 75 km/h: P_v = 0.0042 * V^2 = 23.625 kg/m²
PV_VIENTO_MAX_KG_M2 = 23.625

# Cable de acero para retenidas: Siemens-Martin 3/8" (9.52 mm)
TIRO_ROTURA_RETENIDA_KGF = 3150.0
ANGULO_RETENIDA_DEG = 45.0  # Ángulo de tiro respecto al plano horizontal

# Estructuras de la Línea Primaria E-01 a E-09
ESTRUCTURAS_LP = [
    {
        "id": "E-01", "prog": 0.00, "cota": 3924.17, "poste": "C.A.C. 12/400",
        "h_total": 12.0, "empot": 1.40, "carga_nom_daN": 400.0,
        "armado": "PR-1", "tipo": "Derivación MT / Anclaje", "angulo_deg": 0.0,
        "retenida_tipo": "Inclinada simple R-1", "num_retenidas": 1
    },
    {
        "id": "E-02", "prog": 105.00, "cota": 3895.00, "poste": "C.A.C. 12/300",
        "h_total": 12.0, "empot": 1.40, "carga_nom_daN": 300.0,
        "armado": "PS-1", "tipo": "Suspensión alineamiento", "angulo_deg": 0.0,
        "retenida_tipo": "Ninguna", "num_retenidas": 0
    },
    {
        "id": "E-03", "prog": 210.00, "cota": 3865.00, "poste": "C.A.C. 12/300",
        "h_total": 12.0, "empot": 1.40, "carga_nom_daN": 300.0,
        "armado": "PS-1", "tipo": "Suspensión alineamiento", "angulo_deg": 0.0,
        "retenida_tipo": "Ninguna", "num_retenidas": 0
    },
    {
        "id": "E-04", "prog": 305.21, "cota": 3839.56, "poste": "C.A.C. 13/400 (x2)",
        "h_total": 13.0, "empot": 1.50, "carga_nom_daN": 800.0,  # Biposte
        "armado": "SAB-1", "tipo": "SED Biposte 100 kVA", "angulo_deg": -35.20,
        "retenida_tipo": "Contraviento doble en Y", "num_retenidas": 2
    },
    {
        "id": "E-05", "prog": 402.43, "cota": 3817.04, "poste": "C.A.C. 12/400",
        "h_total": 12.0, "empot": 1.40, "carga_nom_daN": 400.0,
        "armado": "PA-1", "tipo": "Ángulo con retenida", "angulo_deg": -36.06,
        "retenida_tipo": "Biselar simple R-1", "num_retenidas": 1
    },
    {
        "id": "E-06", "prog": 518.02, "cota": 3827.27, "poste": "C.A.C. 12/400",
        "h_total": 12.0, "empot": 1.40, "carga_nom_daN": 400.0,
        "armado": "PA-1", "tipo": "Ángulo con retenida", "angulo_deg": 31.35,
        "retenida_tipo": "Biselar simple R-1", "num_retenidas": 1
    },
    {
        "id": "E-07", "prog": 628.53, "cota": 3824.61, "poste": "C.A.C. 12/300",
        "h_total": 12.0, "empot": 1.40, "carga_nom_daN": 300.0,
        "armado": "PS-1", "tipo": "Alineamiento / Suspensión", "angulo_deg": -6.05,
        "retenida_tipo": "Ninguna", "num_retenidas": 0
    },
    {
        "id": "E-08", "prog": 708.34, "cota": 3824.61, "poste": "C.A.C. 12/400",
        "h_total": 12.0, "empot": 1.40, "carga_nom_daN": 400.0,
        "armado": "PA-1", "tipo": "Ángulo con retenida", "angulo_deg": 32.95,
        "retenida_tipo": "Biselar simple R-1", "num_retenidas": 1
    },
    {
        "id": "E-09", "prog": 816.60, "cota": 3824.61, "poste": "C.A.C. 12/400",
        "h_total": 12.0, "empot": 1.40, "carga_nom_daN": 400.0,
        "armado": "PR-1", "tipo": "Terminal con retenida", "angulo_deg": 0.0,
        "retenida_tipo": "Inclinada simple R-1", "num_retenidas": 1
    }
]

# Longitudes de los 8 vanos entre postes (m)
VANOS = [
    ESTRUCTURAS_LP[i+1]["prog"] - ESTRUCTURAS_LP[i]["prog"]
    for i in range(len(ESTRUCTURAS_LP) - 1)
]


def calcular_vano_viento(idx: int) -> float:
    """Calcula el vano eólico (vano viento) correspondiente a la estructura idx."""
    n = len(ESTRUCTURAS_LP)
    if idx == 0:
        return VANOS[0] / 2.0
    elif idx == n - 1:
        return VANOS[-1] / 2.0
    else:
        return (VANOS[idx - 1] + VANOS[idx]) / 2.0


def calcular_viento_sobre_poste(h_total: float, empot: float) -> tuple:
    """
    Calcula la fuerza de viento sobre el fuste del poste tronco-cónico y su carga equivalente en la cima.
    """
    h_libre = h_total - empot
    # Conicidad estándar 15 mm/m
    d_cima = 0.18 if h_total >= 12.0 else 0.15
    d_base = d_cima + (0.015 * h_total)
    d_tierra = d_cima + (0.015 * h_libre)

    # Área proyectada
    s_proy = ((d_cima + d_tierra) / 2.0) * h_libre
    # Coeficiente de forma cilíndrico = 0.70
    f_vp = PV_VIENTO_MAX_KG_M2 * s_proy * 0.70

    # Carga equivalente en la cabeza del poste (centro de empuje aprox a 0.45 * h_libre)
    f_vp_cima = f_vp * 0.45
    return f_vp, f_vp_cima, h_libre


def analizar_esfuerzos_linea_primaria() -> list:
    """
    Ejecuta el análisis mecánico de todas las estructuras de la Línea Primaria.
    """
    resultados = []

    for i, est in enumerate(ESTRUCTURAS_LP):
        a_v = calcular_vano_viento(i)
        f_vp, f_vp_cima, h_libre = calcular_viento_sobre_poste(est["h_total"], est["empot"])

        ang_rad = math.radians(abs(est["angulo_deg"]))

        # 1. Fuerza de viento sobre los 3 conductores de fase
        # F_vc = 3 * P_v * d * a_v * cos(ang / 2)
        f_vc = 3.0 * PV_VIENTO_MAX_KG_M2 * DIAM_COND_M * a_v * math.cos(ang_rad / 2.0)

        # 2. Fuerza por desvío angular bajo condición I (viento máximo con tiro T_I)
        # F_ang = 3 * 2 * T * sin(ang / 2)
        f_ang_viento = 3.0 * 2.0 * TIRO_HIP_I_KGF * math.sin(ang_rad / 2.0)
        f_ang_eds = 3.0 * 2.0 * TIRO_HIP_V_KGF * math.sin(ang_rad / 2.0)

        # 3. Fuerza longitudinal en terminales / anclajes (E-01 y E-09)
        es_terminal = (i == 0 or i == len(ESTRUCTURAS_LP) - 1)
        f_long_viento = (3.0 * TIRO_HIP_I_KGF) if es_terminal else 0.0
        f_long_eds = (3.0 * TIRO_HIP_V_KGF) if es_terminal else 0.0

        # 4. Resultante total en la cima del poste (sin considerar retenida aún)
        # Componente transversal: F_trans = F_vc + F_vp_cima + F_ang
        f_transversal = f_vc + f_vp_cima + f_ang_viento
        f_cima_bruta = math.sqrt(f_transversal**2 + f_long_viento**2)

        # Momento de vuelco en la base sin retenida (kgf*m)
        m_base_bruto = f_cima_bruta * h_libre

        # 5. Capacidad nominal de rotura del poste (con factor de seguridad = 2.0)
        # Carga nominal en daN convertida a kgf (1 daN = 1.0197 kgf)
        carga_trabajo_kgf = est["carga_nom_daN"] * 1.0197
        carga_rotura_poste_kgf = carga_trabajo_kgf * 2.0

        # 6. Cálculo de Retenidas Mecánicas
        num_ret = est["num_retenidas"]
        t_retenida_kgf = 0.0
        fs_retenida = 999.0
        f_cima_con_retenida = f_cima_bruta
        requiere_retenida = False

        if num_ret > 0:
            requiere_retenida = True
            # La retenida absorbe la resultante horizontal de tiro
            f_horizontal_a_retener = f_cima_bruta
            # Tiro en el cable inclinado a 45°
            t_total_cable = f_horizontal_a_retener / math.cos(math.radians(ANGULO_RETENIDA_DEG))
            t_retenida_kgf = t_total_cable / num_ret
            fs_retenida = TIRO_ROTURA_RETENIDA_KGF / t_retenida_kgf if t_retenida_kgf > 0 else 999.0

            # Con retenida correctamente tesada, el poste soporta principalmente compresión vertical
            # y el esfuerzo en la cima se reduce al viento propio sobre el poste
            f_cima_con_retenida = f_vp_cima
        else:
            # Si no tiene retenida, verificar si la carga bruta supera la carga de trabajo
            if f_cima_bruta > carga_trabajo_kgf:
                requiere_retenida = True

        # Factor de seguridad final del poste
        fs_poste = carga_rotura_poste_kgf / f_cima_con_retenida if f_cima_con_retenida > 0 else 999.0

        resultados.append({
            "id": est["id"],
            "poste": est["poste"],
            "armado": est["armado"],
            "tipo": est["tipo"],
            "prog": est["prog"],
            "cota": est["cota"],
            "h_libre_m": round(h_libre, 2),
            "vano_viento_m": round(a_v, 2),
            "angulo_deg": est["angulo_deg"],
            "f_viento_cond_kgf": round(f_vc, 2),
            "f_viento_poste_kgf": round(f_vp_cima, 2),
            "f_ang_kgf": round(f_ang_viento, 2),
            "f_long_kgf": round(f_long_viento, 2),
            "f_cima_bruta_kgf": round(f_cima_bruta, 2),
            "m_base_bruto_kgf_m": round(m_base_bruto, 2),
            "carga_trabajo_poste_kgf": round(carga_trabajo_kgf, 2),
            "retenida_tipo": est["retenida_tipo"],
            "num_retenidas": num_ret,
            "tiro_cable_ret_kgf": round(t_retenida_kgf, 2),
            "fs_retenida": round(fs_retenida, 2),
            "f_cima_neta_poste_kgf": round(f_cima_con_retenida, 2),
            "fs_poste": round(fs_poste, 2),
            "cumple_cne": (fs_poste >= 2.0 and (num_ret == 0 or fs_retenida >= 2.5))
        })

    return resultados


def guardar_reporte_csv(resultados: list, ruta_csv: str):
    """Exporta la planilla de esfuerzos mecánicos a CSV."""
    os.makedirs(os.path.dirname(ruta_csv) or ".", exist_ok=True)
    campos = [
        "id", "poste", "armado", "tipo", "prog", "cota", "vano_viento_m", "angulo_deg",
        "f_cima_bruta_kgf", "carga_trabajo_poste_kgf", "retenida_tipo", "num_retenidas",
        "tiro_cable_ret_kgf", "fs_retenida", "f_cima_neta_poste_kgf", "fs_poste", "cumple_cne"
    ]
    with open(ruta_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=campos, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(resultados)
    print(f"[OK] Planilla de esfuerzos mecánicos de postes guardada en: {ruta_csv}")


if __name__ == "__main__":
    res = analizar_esfuerzos_linea_primaria()
    print("\n" + "="*80)
    print("ANÁLISIS MECÁNICO DE POSTES Y RETENIDAS — LÍNEA PRIMARIA 22.9 kV CHIFRÓN")
    print("="*80)
    for r in res:
        estado = "CONFORME" if r["cumple_cne"] else "NO CONFORME"
        ret_txt = f"Ret: {r['num_retenidas']}x {r['tiro_cable_ret_kgf']} kgf (FS={r['fs_retenida']})" if r['num_retenidas'] > 0 else "Sin ret."
        print(f"[{r['id']}] {r['poste']} ({r['armado']}) | VanoViento: {r['vano_viento_m']}m | Ang: {r['angulo_deg']}°")
        print(f"     F_cima Bruta: {r['f_cima_bruta_kgf']} kgf | {ret_txt}")
        print(f"     F_neta Poste: {r['f_cima_neta_poste_kgf']} kgf | FS Poste: {r['fs_poste']} | Estado: {estado}\n")

    ruta_salida = os.path.join(os.path.dirname(__file__), "..", "datos", "estructuras", "planilla_esfuerzos_mecanicos_postes_lp.csv")
    guardar_reporte_csv(res, ruta_salida)
