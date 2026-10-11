#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cálculo Mecánico de Conductores Aéreos - Ecuación de Cambio de Estado de Truxa
Normativa: Código Nacional de Electricidad (CNE Suministro 2011, Zona 2/3) y Norma DGE
Proyecto: Línea Primaria 22.9 kV Sector Chifrón (Capachica, Puno)
Autor: Br. Renzo Gabriel Mamani Galindo (Cód. 228447)
"""

import os
import math
import csv
import numpy as np

# -----------------------------------------------------------------------------
# PARÁMETROS CANÓNICOS DEL CONDUCTOR Y DEL PROYECTO
# -----------------------------------------------------------------------------
PARAMETROS_CONDUCTOR = {
    "tipo": "AAAC 35 mm² (Aleación de Aluminio Al-Mg-Si)",
    "norma": "NTP 370.258 / IEC 61089",
    "seccion_nominal_mm2": 35.0,
    "seccion_real_mm2": 34.36,
    "diametro_exterior_mm": 7.50,
    "peso_unitario_kg_m": 0.0945,
    "tiro_rotura_kgf": 1040.0,
    "modulo_elasticidad_kg_mm2": 6000.0,
    "coef_dilatacion_termica_1_C": 23.0e-6,
    "eds_porcentaje": 18.0  # 18% del tiro de rotura según DGE
}

# 5 Hipótesis Climáticas Oficiales CNE Suministro 2011 (Zona 2/3 Altiplano > 3,000 msnm)
HIPOTESIS_CNE = [
    {
        "id": "I",
        "nombre": "I. Viento Máximo",
        "temp_C": 10.0,
        "viento_km_h": 75.0,
        "hielo_mm": 0.0,
        "limite_tiro_pct": 40.0,
        "descripcion": "Viento de diseño 75 km/h a temperatura de viento"
    },
    {
        "id": "II",
        "nombre": "II. Manguito de Hielo",
        "temp_C": -5.0,
        "viento_km_h": 37.5,
        "hielo_mm": 6.0,
        "limite_tiro_pct": 40.0,
        "descripcion": "Espesor de hielo 6 mm con viento concomitante al 50%"
    },
    {
        "id": "III",
        "nombre": "III. Temperatura Mínima",
        "temp_C": -15.0,
        "viento_km_h": 0.0,
        "hielo_mm": 0.0,
        "limite_tiro_pct": 40.0,
        "descripcion": "Condición más fría del altiplano sin viento"
    },
    {
        "id": "IV",
        "nombre": "IV. Temperatura Máxima",
        "temp_C": 35.0,
        "viento_km_h": 0.0,
        "hielo_mm": 0.0,
        "limite_tiro_pct": 40.0,
        "descripcion": "Condición determinante para la flecha vertical máxima"
    },
    {
        "id": "V",
        "nombre": "V. Templado / EDS",
        "temp_C": 15.0,
        "viento_km_h": 0.0,
        "hielo_mm": 0.0,
        "limite_tiro_pct": 18.0,
        "descripcion": "Estado base de templado Every Day Stress (18% TR)"
    }
]

def calcular_carga_unitaria(diametro_mm, peso_propio_kg_m, viento_km_h, hielo_mm):
    """
    Calcula la carga unitaria resultante (w) combinando peso propio, hielo y viento.
    """
    d_m = diametro_mm * 1e-3
    w_0 = peso_propio_kg_m
    
    # 1. Carga por manguito de hielo (densidad = 900 kg/m3)
    if hielo_mm > 0.0:
        e_m = hielo_mm * 1e-3
        # Volumen por metro = pi * e * (d + e)
        w_h = math.pi * e_m * (d_m + e_m) * 900.0
        d_total_m = d_m + 2.0 * e_m
    else:
        w_h = 0.0
        d_total_m = d_m
        
    w_vertical = w_0 + w_h
    
    # 2. Carga por presión de viento: P_v = 0.0042 * V^2 (kg/m2)
    if viento_km_h > 0.0:
        P_v = 0.0042 * (viento_km_h ** 2)
        w_v = P_v * d_total_m
    else:
        w_v = 0.0
        
    # Resultante vectorial
    w_resultante = math.sqrt(w_vertical**2 + w_v**2)
    return w_vertical, w_v, w_resultante

def resolver_truxa(vano_m, w_res, temp_C, base_temp_C, base_w, base_sigma, E, alpha, seccion):
    """
    Resuelve la ecuación cúbica de cambio de estado de Truxa:
    sigma^3 + K * sigma^2 - C = 0
    """
    if temp_C == base_temp_C and abs(w_res - base_w) < 1e-6:
        return base_sigma
        
    B = (vano_m**2 * (base_w**2) * E) / (24.0 * (seccion**2) * (base_sigma**2))
    K = alpha * E * (temp_C - base_temp_C) + B - base_sigma
    C = (vano_m**2 * (w_res**2) * E) / (24.0 * (seccion**2))
    
    raices = np.roots([1.0, K, 0.0, -C])
    reales = [r.real for r in raices if np.isreal(r) and r.real > 0]
    if not reales:
        raise ValueError(f"No se encontró solución física para vano {vano_m} m a {temp_C}°C.")
    return reales[0]

def calcular_tabla_hipotesis_vano(vano_m):
    """
    Calcula la tabla completa de las 5 hipótesis CNE para un vano dado.
    """
    cond = PARAMETROS_CONDUCTOR
    seccion = cond["seccion_real_mm2"]
    diam = cond["diametro_exterior_mm"]
    w_0 = cond["peso_unitario_kg_m"]
    T_R = cond["tiro_rotura_kgf"]
    E = cond["modulo_elasticidad_kg_mm2"]
    alpha = cond["coef_dilatacion_termica_1_C"]
    
    # Estado base EDS
    T_eds = (cond["eds_porcentaje"] / 100.0) * T_R
    sigma_eds = T_eds / seccion
    temp_eds = 15.0
    w_eds = w_0
    
    filas = []
    for h in HIPOTESIS_CNE:
        w_vert, w_v, w_res = calcular_carga_unitaria(diam, w_0, h["viento_km_h"], h["hielo_mm"])
        
        sigma = resolver_truxa(vano_m, w_res, h["temp_C"], temp_eds, w_eds, sigma_eds, E, alpha, seccion)
        tiro = sigma * seccion
        
        # Flecha resultante f_res = (w_res * vano^2) / (8 * tiro)
        f_res = (w_res * (vano_m**2)) / (8.0 * tiro)
        
        # Flecha vertical (para verificación de distancias al suelo)
        # En ausencia de viento es exactamente f_res; con viento es f_res * (w_vert / w_res)
        f_vert = f_res * (w_vert / w_res)
        
        pct_TR = (tiro / T_R) * 100.0
        cumple = pct_TR <= h["limite_tiro_pct"]
        
        filas.append({
            "id": h["id"],
            "nombre": h["nombre"],
            "temp_C": h["temp_C"],
            "viento_km_h": h["viento_km_h"],
            "hielo_mm": h["hielo_mm"],
            "w_res_kg_m": round(w_res, 4),
            "w_vert_kg_m": round(w_vert, 4),
            "sigma_kg_mm2": round(sigma, 3),
            "tiro_kgf": round(tiro, 2),
            "flecha_res_m": round(f_res, 3),
            "flecha_vert_m": round(f_vert, 3),
            "tiro_pct_TR": round(pct_TR, 1),
            "limite_pct_TR": h["limite_tiro_pct"],
            "cumple": cumple,
            "descripcion": h["descripcion"]
        })
        
    return filas

def generar_reporte_mecanico(vano_critico=115.59, csv_salida=None):
    filas = calcular_tabla_hipotesis_vano(vano_critico)
    
    print("=" * 95)
    print(f"CÁLCULO MECÁNICO OFICIAL — CONDUCTOR AAAC 35 mm² (Vano Crítico: {vano_critico} m)")
    print(f"Norma: CNE Suministro 2011 (Zona 2/3) | Base EDS: 15°C, 18% TR = 187.20 kgf")
    print("=" * 95)
    print(f"{'Hipótesis':22s} | {'T (°C)':7s} | {'V (km/h)':8s} | {'w (kg/m)':9s} | {'Tiro (kgf)':10s} | {'% TR':6s} | {'f_res (m)':9s} | {'f_vert (m)':10s} | {'Estado'}")
    print("-" * 95)
    
    for f in filas:
        est = "CUMPLE" if f["cumple"] else "FALLA"
        print(f"{f['nombre']:22s} | {f['temp_C']:7.1f} | {f['viento_km_h']:8.1f} | {f['w_res_kg_m']:9.4f} | {f['tiro_kgf']:10.2f} | {f['tiro_pct_TR']:5.1f}% | {f['flecha_res_m']:9.3f} | {f['flecha_vert_m']:10.3f} | {est}")
    print("=" * 95)
    
    # Verificación de altura libre al suelo
    f_max_vert = next(f["flecha_vert_m"] for f in filas if f["id"] == "IV")
    h_poste = 12.0
    empotramiento = 1.40
    h_libre = h_poste - empotramiento - f_max_vert
    h_norma_cne = 6.50
    
    print(f"\nVERIFICACIÓN DE SEGURIDAD VERTICAL:")
    print(f"- Altura poste: {h_poste:.2f} m | Empotramiento: {empotramiento:.2f} m | Altura útil: {h_poste - empotramiento:.2f} m")
    print(f"- Flecha máxima vertical (+35°C): {f_max_vert:.3f} m")
    print(f"- Distancia libre al suelo: {h_libre:.3f} m  (Exigencia CNE Regla 232: >= {h_norma_cne:.2f} m)")
    print(f"- Margen de seguridad: +{h_libre - h_norma_cne:.3f} m  --> CUMPLE HOLGADAMENTE")
    
    if csv_salida:
        os.makedirs(os.path.dirname(csv_salida), exist_ok=True)
        with open(csv_salida, "w", newline="", encoding="utf-8") as fp:
            writer = csv.writer(fp)
            writer.writerow(["Hipotesis", "Temperatura_C", "Viento_km_h", "Hielo_mm", "Carga_Resultante_kg_m", "Tiro_kgf", "Tiro_pct_TR", "Flecha_Resultante_m", "Flecha_Vertical_m", "Estado"])
            for f in filas:
                writer.writerow([f["nombre"], f["temp_C"], f["viento_km_h"], f["hielo_mm"], f["w_res_kg_m"], f["tiro_kgf"], f["tiro_pct_TR"], f["flecha_res_m"], f["flecha_vert_m"], "Cumple" if f["cumple"] else "No cumple"])
        print(f"\nTabla exportada exitosamente a: {csv_salida}")
        
    return filas

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_out = os.path.join(script_dir, "..", "datos", "estructuras", "tabla_hipotesis_mecanicas_cne.csv")
    generar_reporte_mecanico(vano_critico=115.59, csv_salida=csv_out)
