#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/coordinacion_aislamiento_lp.py
Cálculo de Coordinación de Aislamiento y Sobretensiones para Gran Altitud (3,850 msnm)
Normativa: IEC 60071-1, IEC 60071-2, CNE Suministro 2011 (Reglas 242, 362)
Proyecto: Línea Primaria 22.9 kV Sector Chifrón (Capachica, Puno)
Autor: Br. Renzo Gabriel Mamani Galindo (Cód. 228447)
"""

import math
import os


def calcular_coordinacion_aislamiento_altitud(
    tension_nominal_kv: float = 22.9,
    tension_maxima_kv: float = 24.2,
    altitud_msnm: float = 3850.0,
    temp_ambiente_c: float = 15.0,
    bil_base_mar_kv: float = 125.0,
    dist_aire_fase_tierra_base_mm: float = 220.0,
    dist_aire_fase_fase_base_mm: float = 280.0
) -> dict:
    """
    Calcula los factores de corrección por altitud y los requerimientos dieléctricos
    para la Línea Primaria a 3,850 msnm.
    """
    # 1. Parámetros atmosféricos a la cota del proyecto
    # Presión atmosférica según la atmósfera estándar OACI (kPa)
    p_barom_kpa = 101.325 * ((1.0 - 0.0000225577 * altitud_msnm) ** 5.2559)

    # Densidad relativa del aire (δ)
    # δ = (P / P0) * ((273 + T0) / (273 + T))
    delta_aire = (p_barom_kpa / 101.325) * (293.15 / (273.15 + temp_ambiente_c))

    # 2. Factor de corrección de altitud Ka según IEC 60071-2
    # Ka = e^(m * (H - 1000) / 8150), con m = 1.0 para impulso de rayo
    delta_h = max(0.0, altitud_msnm - 1000.0)
    ka_iec = math.exp(1.0 * delta_h / 8150.0)

    # Factor de corrección simplificado según CNE Suministro (aprox 1.25 para 3,850 msnm)
    ka_cne = 1.0 + (delta_h / 1000.0) * 0.087  # ~1.25 a 3850 msnm

    # 3. Nivel Básico de Aislamiento al Impulso (BIL) Corregido
    bil_requerido_kv = bil_base_mar_kv * ka_cne
    # Selección de BIL normalizado comercial (125 -> 150 -> 170 kV)
    bil_normalizado_kv = 150.0 if bil_requerido_kv <= 150.0 else 170.0

    # Tensión soportada a frecuencia industrial en húmedo (1 min)
    v_soportada_fi_base_kv = 50.0
    v_soportada_fi_corregida_kv = v_soportada_fi_base_kv * ka_cne

    # 4. Distancias mínimas de aislamiento en aire
    dist_aire_f_t_corregida_mm = dist_aire_fase_tierra_base_mm * ka_cne
    dist_aire_f_f_corregida_mm = dist_aire_fase_fase_base_mm * ka_cne

    # 5. Línea de fuga específica (entorno lacustre Lago Titicaca, Polución II)
    # Mínimo 31 mm/kV para tensión máxima Um
    fuga_especifica_mm_kv = 31.0
    linea_fuga_minima_mm = fuga_especifica_mm_kv * tension_maxima_kv

    # Aislador polimérico seleccionado: 25 kV, 6 aletas HTV
    linea_fuga_aislador_real_mm = 810.0
    margen_fuga_pct = ((linea_fuga_aislador_real_mm - linea_fuga_minima_mm) / linea_fuga_minima_mm) * 100.0

    # 6. Selección de Descargadores de Sobretensión (Pararrayos ZnO)
    # Tensión máxima fase-tierra continua: Uc = (Um / sqrt(3)) * 1.05
    uc_fase_tierra_kv = (tension_maxima_kv / math.sqrt(3.0)) * 1.05
    # Tensión de operación continua MCOV
    mcov_minimo_kv = uc_fase_tierra_kv * 1.15  # Margen de seguridad 15%
    mcov_catalogo_kv = 17.5  # Pararrayo comercial ZnO para 22.9 kV
    ur_catalogo_kv = 21.0    # Tensión nominal asignada Ur

    return {
        "altitud_msnm": altitud_msnm,
        "p_barometrica_kpa": round(p_barom_kpa, 2),
        "densidad_aire_delta": round(delta_aire, 3),
        "ka_iec": round(ka_iec, 3),
        "ka_cne": round(ka_cne, 3),
        "bil_base_kv": bil_base_mar_kv,
        "bil_requerido_kv": round(bil_requerido_kv, 2),
        "bil_normalizado_kv": bil_normalizado_kv,
        "v_fi_base_kv": v_soportada_fi_base_kv,
        "v_fi_corregida_kv": round(v_soportada_fi_corregida_kv, 2),
        "dist_aire_ft_mm": round(dist_aire_f_t_corregida_mm, 1),
        "dist_aire_ff_mm": round(dist_aire_f_f_corregida_mm, 1),
        "linea_fuga_minima_mm": round(linea_fuga_minima_mm, 1),
        "linea_fuga_real_mm": linea_fuga_aislador_real_mm,
        "margen_fuga_pct": round(margen_fuga_pct, 1),
        "mcov_requerido_kv": round(mcov_minimo_kv, 2),
        "mcov_seleccionado_kv": mcov_catalogo_kv,
        "ur_pararrayos_kv": ur_catalogo_kv,
        "cumple_aislamiento": (linea_fuga_aislador_real_mm >= linea_fuga_minima_mm and bil_normalizado_kv >= bil_requerido_kv)
    }


if __name__ == "__main__":
    c = calcular_coordinacion_aislamiento_altitud()
    print("\n" + "="*80)
    print(f"COORDINACIÓN DE AISLAMIENTO A GRAN ALTITUD ({c['altitud_msnm']} msnm) — IEC 60071 / CNE")
    print("="*80)
    print(f"Presion barometrica: {c['p_barometrica_kpa']} kPa | Densidad relativa del aire delta: {c['densidad_aire_delta']}")
    print(f"Factor de corrección Ka (CNE): {c['ka_cne']} | Ka (IEC 60071-2): {c['ka_iec']}")
    print(f"BIL Requerido: {c['bil_requerido_kv']} kV  -->  BIL Normalizado Seleccionado: {c['bil_normalizado_kv']} kV")
    print(f"Tensión Soportada a Frecuencia Industrial (1 min): {c['v_fi_corregida_kv']} kV")
    print(f"Distancias mínimas en aire: Fase-Tierra: {c['dist_aire_ft_mm']} mm | Fase-Fase: {c['dist_aire_ff_mm']} mm")
    print(f"Línea de fuga requerida: {c['linea_fuga_minima_mm']} mm | Aislador 25 kV Real: {c['linea_fuga_real_mm']} mm (+{c['margen_fuga_pct']}%)")
    print(f"Pararrayos ZnO: Ur = {c['ur_pararrayos_kv']} kV, MCOV = {c['mcov_seleccionado_kv']} kV, Descarga = 10 kA")
    print(f"Estado de Conformidad: {'CONFORME' if c['cumple_aislamiento'] else 'NO CONFORME'}\n")
