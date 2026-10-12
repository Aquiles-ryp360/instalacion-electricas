#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/calculo_cimentacion_sulzberger_lp.py
Cálculo y Verificación Geotécnica de Cimentaciones de Postes y Bloques de Retenida
Método de Sulzberger conforme al Código Nacional de Electricidad (CNE Suministro 2011)
Proyecto: Línea Primaria 22.9 kV Sector Chifrón (Capachica, Puno)
Autor: Br. Renzo Gabriel Mamani Galindo (Cód. 228447)
"""

import math
import csv
import os

# -----------------------------------------------------------------------------
# PARÁMETROS GEOTÉCNICOS DEL TERRENO EN CAPACHICA
# -----------------------------------------------------------------------------
# Suelo coluvial / arcillo-arenoso compacto con gravas finas (ladera Cerro Chifrón y planicie)
PESO_ESPECIFICO_SUELO_KG_M3 = 1750.0  # γ = 1.75 t/m³
PESO_ESPECIFICO_CONCRETO_KG_M3 = 2300.0  # Concreto ciclópeo f'c = 140 kg/cm² + 30% PM
ANGULO_FRICCION_INTERNA_DEG = 30.0   # φ = 30°
COEF_COMPRESIBILIDAD_CT_KG_CM3 = 8.0  # C_t a 2 m de profundidad = 8.0 kg/cm³ (8.0 x 10⁶ kg/m³)
COEF_COMPRESIBILIDAD_LATERAL_KG_CM3 = 10.0  # C'_t en paredes laterales = 10.0 kg/cm³

# Ángulo de inclinación admisible según Sulzberger: tan(α) = 0.01 rad (0° 34')
TAN_ALFA_ADM = 0.01

# Importar resultados mecánicos de postes
from calculo_mecanico_postes_lp import analizar_esfuerzos_linea_primaria


def calcular_sulzberger_poste(f_cima_neta_kgf: float, h_libre_m: float,
                              empot_t_m: float, diam_excav_m: float) -> dict:
    """
    Calcula la estabilidad de la cimentación del poste C.A.C. por el Método de Sulzberger.
    """
    # Conversión de coeficientes a unidades métricas (kg/m³)
    # 1 kg/cm³ = 10⁶ kg/m³
    c_t = COEF_COMPRESIBILIDAD_CT_KG_CM3 * 1.0e6
    c_prima_t = COEF_COMPRESIBILIDAD_LATERAL_KG_CM3 * 1.0e6

    # Coeficiente a la profundidad del fondo: C = C_t * (t / 2.0)
    c_fondo = c_t * (empot_t_m / 2.0)

    # Dimensiones de la zapata cilíndrica de concreto ciclópeo
    # Sección equivalente cuadrada para Sulzberger: b = a = diam_excav * sqrt(pi / 4)
    b_eq = diam_excav_m * math.sqrt(math.pi / 4.0)
    a_eq = b_eq
    t = empot_t_m

    # Momento de vuelco actuante en la cimentación: M_v = F_cima * (h_libre + t)
    # o respecto a la base del terreno:
    m_vuelco_actuante = f_cima_neta_kgf * (h_libre_m + (2.0 / 3.0) * t)

    # 1. Momento resistente en el fondo de la cimentación (M_b)
    # M_b = (a * b³ * C / 12) * tan(α)
    m_fondo = (a_eq * (b_eq**3) * c_fondo / 12.0) * TAN_ALFA_ADM

    # 2. Momento resistente en las paredes laterales de la excavación (M_s)
    # M_s = (b * t³ * C'_t / 36) * tan(α)
    m_lateral = (b_eq * (t**3) * c_prima_t / 36.0) * TAN_ALFA_ADM

    # 3. Momento resistente total admisible (M_r)
    m_resistente_total = m_fondo + m_lateral

    # Factor de seguridad de la cimentación (Sulzberger exige FS >= 1.50)
    fs_cimentacion = m_resistente_total / m_vuelco_actuante if m_vuelco_actuante > 0 else 999.0

    return {
        "m_vuelco_kgf_m": round(m_vuelco_actuante, 2),
        "m_fondo_kgf_m": round(m_fondo, 2),
        "m_lateral_kgf_m": round(m_lateral, 2),
        "m_resistente_kgf_m": round(m_resistente_total, 2),
        "fs_sulzberger": round(fs_cimentacion, 2),
        "conforme": fs_cimentacion >= 1.50
    }


def calcular_bloque_anclaje_retenida(tiro_cable_kgf: float,
                                     largo_bloque_m: float = 0.40,
                                     ancho_bloque_m: float = 0.40,
                                     alto_bloque_m: float = 0.20,
                                     profundidad_ent_m: float = 1.80) -> dict:
    """
    Verifica la resistencia al arrancamiento del bloque de concreto de la retenida a tierra.
    """
    if tiro_cable_kgf <= 0.0:
        return {"aplica": False, "conforme": True, "fs_arrancamiento": 999.0}

    # Fuerza vertical de arrancamiento debida a la inclinación a 45°
    f_arrancamiento_vert = tiro_cable_kgf * math.sin(math.radians(45.0))

    # 1. Peso del bloque de concreto
    vol_bloque = largo_bloque_m * ancho_bloque_m * alto_bloque_m
    peso_bloque_kgf = vol_bloque * PESO_ESPECIFICO_CONCRETO_KG_M3

    # 2. Volumen del prisma tronco-piramidal invertido de tierra sobre el bloque
    # Ángulo de dispersión de presiones en tierra: β = φ / 2 = 15°
    beta_rad = math.radians(15.0)
    h_tierra = profundidad_ent_m - alto_bloque_m

    largo_sup = largo_bloque_m + (2.0 * h_tierra * math.tan(beta_rad))
    ancho_sup = ancho_bloque_m + (2.0 * h_tierra * math.tan(beta_rad))

    area_inf = largo_bloque_m * ancho_bloque_m
    area_sup = largo_sup * ancho_sup

    # Volumen del tronco de pirámide: V = (h / 3) * (A1 + A2 + sqrt(A1 * A2))
    vol_tierra = (h_tierra / 3.0) * (area_inf + area_sup + math.sqrt(area_inf * area_sup))
    peso_tierra_kgf = vol_tierra * PESO_ESPECIFICO_SUELO_KG_M3

    # Resistencia total al arrancamiento
    resistencia_total_kgf = peso_bloque_kgf + peso_tierra_kgf

    # Factor de seguridad al arrancamiento (exigido FS >= 2.0)
    fs_arr = resistencia_total_kgf / f_arrancamiento_vert

    return {
        "aplica": True,
        "tiro_cable_kgf": round(tiro_cable_kgf, 2),
        "f_arrancamiento_vert_kgf": round(f_arrancamiento_vert, 2),
        "peso_bloque_kgf": round(peso_bloque_kgf, 2),
        "peso_tierra_kgf": round(peso_tierra_kgf, 2),
        "resistencia_total_kgf": round(resistencia_total_kgf, 2),
        "fs_arrancamiento": round(fs_arr, 2),
        "conforme": fs_arr >= 2.0
    }


def verificar_cimentaciones_completas() -> list:
    """Ejecuta la verificación completa de cimentaciones para las 9 estructuras de la LP."""
    esfuerzos = analizar_esfuerzos_linea_primaria()
    reporte = []

    for est in esfuerzos:
        # Diámetro de excavación cilíndrico normalizado: 0.80 m (postes de 12m), 0.90 m (biposte 13m)
        diam_exc = 0.90 if "13" in est["poste"] else 0.80
        empot = 1.50 if "13" in est["poste"] else 1.40

        sulz = calcular_sulzberger_poste(
            f_cima_neta_kgf=est["f_cima_neta_poste_kgf"],
            h_libre_m=est["h_libre_m"],
            empot_t_m=empot,
            diam_excav_m=diam_exc
        )

        ret = calcular_bloque_anclaje_retenida(est["tiro_cable_ret_kgf"])

        reporte.append({
            "id": est["id"],
            "poste": est["poste"],
            "armado": est["armado"],
            "f_cima_kgf": est["f_cima_neta_poste_kgf"],
            "m_vuelco_kgf_m": sulz["m_vuelco_kgf_m"],
            "m_resistente_kgf_m": sulz["m_resistente_kgf_m"],
            "fs_sulzberger": sulz["fs_sulzberger"],
            "sulz_conforme": sulz["conforme"],
            "num_retenidas": est["num_retenidas"],
            "tiro_ret_kgf": est["tiro_cable_ret_kgf"],
            "fs_arrancamiento_ret": ret["fs_arrancamiento"],
            "ret_conforme": ret["conforme"],
            "estado_general": "CONFORME" if (sulz["conforme"] and ret["conforme"]) else "REVISAR"
        })

    return reporte


def exportar_cimentaciones_csv(reporte: list, ruta_csv: str):
    """Guarda los resultados geotécnicos en formato CSV."""
    os.makedirs(os.path.dirname(ruta_csv) or ".", exist_ok=True)
    campos = [
        "id", "poste", "armado", "f_cima_kgf", "m_vuelco_kgf_m", "m_resistente_kgf_m",
        "fs_sulzberger", "sulz_conforme", "num_retenidas", "tiro_ret_kgf",
        "fs_arrancamiento_ret", "ret_conforme", "estado_general"
    ]
    with open(ruta_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(reporte)
    print(f"[OK] Planilla geotécnica Sulzberger guardada en: {ruta_csv}")


if __name__ == "__main__":
    rep = verificar_cimentaciones_completas()
    print("\n" + "="*85)
    print("VERIFICACIÓN GEOTÉCNICA DE CIMENTACIONES (MÉTODO SULZBERGER) — LÍNEA PRIMARIA 22.9 kV")
    print("="*85)
    for r in rep:
        ret_info = f"Ret: {r['num_retenidas']}x | FS Arranc: {r['fs_arrancamiento_ret']}" if r['num_retenidas'] > 0 else "Sin retenida"
        print(f"[{r['id']}] {r['poste']} ({r['armado']})")
        print(f"     M_vuelco: {r['m_vuelco_kgf_m']} kgf*m | M_resistente: {r['m_resistente_kgf_m']} kgf*m")
        print(f"     FS Sulzberger: {r['fs_sulzberger']} (Exigido >= 1.50) | {ret_info} | Estado: {r['estado_general']}\n")

    ruta = os.path.join(os.path.dirname(__file__), "..", "datos", "estructuras", "tabla_cimentaciones_sulzberger_lp.csv")
    exportar_cimentaciones_csv(rep, ruta)
