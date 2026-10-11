#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cálculo de Caída de Tensión y Pérdidas en Línea Primaria 22.9 kV
Proyecto: Línea Primaria en Media Tensión Sector Chifrón (Capachica, Puno)
Curso: MEC330 - Instalaciones Eléctricas II | FIME - UNA Puno
Autor: Br. Renzo Gabriel Mamani Galindo (Cód. 228447)
"""

import math

def calcular_caida_tension_3f(P_kw, fp, V_kv, L_km, r_ohm_km, x_ohm_km):
    """
    Calcula la caída de tensión y pérdidas en una línea primaria trifásica de MT.
    
    Parámetros:
    - P_kw: Potencia activa en kW
    - fp: Factor de potencia (cos phi)
    - V_kv: Tensión nominal entre fases en kV (22.9 kV)
    - L_km: Longitud de la línea en km (0.8166 km)
    - r_ohm_km: Resistencia longitudinal a temp. de operación (ohm/km)
    - x_ohm_km: Reactancia inductiva longitudinal (ohm/km)
    
    Retorna dict con corriente, delta_V, delta_V_pct, pérdidas P y porcentaje.
    """
    sin_phi = math.sqrt(max(0.0, 1.0 - fp**2))
    P_w = P_kw * 1000.0
    V_v = V_kv * 1000.0
    
    # Corriente de línea trifásica
    I = P_w / (math.sqrt(3) * V_v * fp)
    
    # Resistencia y reactancia totales de la traza
    R = r_ohm_km * L_km
    X = x_ohm_km * L_km
    
    # Caída de tensión línea a línea (Norma DGE / CNE Suministro)
    # Delta V = sqrt(3) * I * (R * cos_phi + X * sin_phi)
    delta_V = math.sqrt(3) * I * (R * fp + X * sin_phi)
    delta_V_pct = (delta_V / V_v) * 100.0
    
    # Pérdidas de potencia activa trifásica en los 3 conductores
    delta_P_w = 3.0 * (I**2) * R
    delta_P_kw = delta_P_w / 1000.0
    delta_P_pct = (delta_P_kw / P_kw) * 100.0 if P_kw > 0 else 0.0
    
    return {
        "potencia_kw": round(P_kw, 2),
        "corriente_A": round(I, 2),
        "R_total_ohm": round(R, 3),
        "X_total_ohm": round(X, 3),
        "delta_V_V": round(delta_V, 2),
        "delta_V_pct": round(delta_V_pct, 4),
        "perdidas_P_kw": round(delta_P_kw, 3),
        "perdidas_P_pct": round(delta_P_pct, 3),
        "cumple_norma": delta_V_pct <= 5.0  # Límite CNE: <= 5.0%
    }

if __name__ == "__main__":
    print("=" * 80)
    print("CÁLCULO ELÉCTRICO OFICIAL DE MEDIA TENSIÓN (22.9 kV) — CAPACHICA CHIFRÓN")
    print("Conductor: AAAC 35 mm2 | L = 816.60 m (0.817 km) | R = 0.986 Ohm/km | X = 0.385 Ohm/km")
    print("=" * 80)
    
    # Caso 1: Plena carga del Transformador de Distribución (100 kVA, cos phi = 0.90 -> 90 kW)
    res_trafo = calcular_caida_tension_3f(
        P_kw=90.0,  # 100 kVA * 0.90 = 90 kW (I = 100 / (sqrt(3)*22.9) = 2.52 A)
        fp=0.90,
        V_kv=22.9,
        L_km=0.8166,
        r_ohm_km=0.986,
        x_ohm_km=0.385
    )
    
    print("\n1. CONDICION A PLENA CAPACIDAD DEL TRANSFORMADOR (100 kVA / 90 kW, cos phi = 0.90):")
    print(f"- Corriente nominal MT:       {res_trafo['corriente_A']} A")
    print(f"- Caida de tension (Delta V): {res_trafo['delta_V_V']} V ({res_trafo['delta_V_pct']:.3f}%)  [Limite CNE <= 5.0%]")
    print(f"- Perdidas activas trifasicas: {res_trafo['perdidas_P_kw']} kW ({res_trafo['perdidas_P_pct']}%)")
    print(f"- Estado de conformidad:      {'CUMPLE AMPLIAMENTE' if res_trafo['cumple_norma'] else 'NO CUMPLE'}")
    
    # Caso 2: Máxima Demanda Proyectada de la Población (71.10 kW, 79.00 kVA)
    res_demanda = calcular_caida_tension_3f(
        P_kw=71.10,
        fp=0.90,
        V_kv=22.9,
        L_km=0.8166,
        r_ohm_km=0.986,
        x_ohm_km=0.385
    )
    
    print("\n2. CONDICION A MAXIMA DEMANDA DEL PROYECTO (71.10 kW / 79.00 kVA, cos phi = 0.90):")
    print(f"- Corriente de operacion MT:  {res_demanda['corriente_A']} A")
    print(f"- Caida de tension (Delta V): {res_demanda['delta_V_V']} V ({res_demanda['delta_V_pct']:.3f}%)  [Limite CNE <= 5.0%]")
    print(f"- Perdidas activas trifasicas: {res_demanda['perdidas_P_kw']} kW ({res_demanda['perdidas_P_pct']}%)")
    print(f"- Estado de conformidad:      {'CUMPLE AMPLIAMENTE' if res_demanda['cumple_norma'] else 'NO CUMPLE'}")
    print("=" * 80)
