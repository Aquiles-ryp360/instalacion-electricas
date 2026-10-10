#!/usr/bin/env python3
"""
Cálculo de Caída de Tensión y Pérdidas en Líneas Primarias de Media Tensión (MT)
Curso: MEC330 - Instalaciones Eléctricas II | FIME - UNA Puno
Autor: Renzo Gabriel Mamani Galindo
"""

import math

def calcular_caida_tension_3f(P_kw, fp, V_kv, L_km, r_ohm_km, x_ohm_km):
    """
    Calcula la caída de tensión en una línea primaria trifásica de MT.
    
    Parámetros:
    - P_kw: Potencia activa en kW
    - fp: Factor de potencia (cos phi)
    - V_kv: Tensión nominal entre fases en kV (ej. 22.9 kV)
    - L_km: Longitud de la línea en km
    - r_ohm_km: Resistencia longitudinal a temp. de operación (ohm/km)
    - x_ohm_km: Reactancia inductiva longitudinal (ohm/km)
    
    Retorna:
    - Dict con resultados: corriente (A), delta_V (V), delta_V_pct (%), pérdidas P (kW), pérdidas P (%)
    """
    sin_phi = math.sqrt(1 - fp**2)
    P_w = P_kw * 1000.0
    V_v = V_kv * 1000.0
    
    # Corriente de línea
    I = P_w / (math.sqrt(3) * V_v * fp)
    
    # Resistencia y reactancia totales
    R = r_ohm_km * L_km
    X = x_ohm_km * L_km
    
    # Caída de tensión de línea a línea (aproximación estándar DGE / CNE)
    # Delta V = sqrt(3) * I * (R * cos_phi + X * sin_phi)
    delta_V = math.sqrt(3) * I * (R * fp + X * sin_phi)
    delta_V_pct = (delta_V / V_v) * 100.0
    
    # Pérdidas de potencia activa trifásica
    delta_P_w = 3.0 * (I**2) * R
    delta_P_kw = delta_P_w / 1000.0
    delta_P_pct = (delta_P_kw / P_kw) * 100.0
    
    return {
        "corriente_A": round(I, 2),
        "R_total_ohm": round(R, 3),
        "X_total_ohm": round(X, 3),
        "delta_V_V": round(delta_V, 2),
        "delta_V_pct": round(delta_V_pct, 3),
        "perdidas_P_kw": round(delta_P_kw, 3),
        "perdidas_P_pct": round(delta_P_pct, 3),
        "cumple_norma": delta_V_pct <= 5.0  # Límite CNE: 5% (7.5% rural con sustento)
    }

if __name__ == "__main__":
    # Ejemplo de prueba para línea Capachica (22.9 kV, AAAC 35 mm2, 3.5 km, 150 kW, fp 0.90)
    print("=== TEST CÁLCULO CAÍDA DE TENSIÓN MT (22.9 kV) ===")
    res = calcular_caida_tension_3f(
        P_kw=150.0,
        fp=0.90,
        V_kv=22.9,
        L_km=3.5,
        r_ohm_km=0.986,  # AAAC 35 mm2 a 50°C
        x_ohm_km=0.385   # DMG típico 1.2 m en 22.9 kV
    )
    for k, v in res.items():
        print(f"{k}: {v}")
