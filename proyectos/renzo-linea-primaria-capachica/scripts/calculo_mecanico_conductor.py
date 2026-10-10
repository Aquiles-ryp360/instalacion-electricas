#!/usr/bin/env python3
"""
Cálculo Mecánico de Conductores Aéreos - Ecuación Cúbica de Cambio de Estado
Curso: MEC330 - Instalaciones Eléctricas II | FIME - UNA Puno
Autor: Renzo Gabriel Mamani Galindo
Normativa: CNE Suministro / Norma DGE Bases para el Diseño de Líneas Primarias
"""

import math
import numpy as np

def resolver_cambio_estado(vano, sigma_1, temp_1, w_1, temp_2, w_2, E, alpha, seccion):
    """
    Resuelve la Ecuación de Cambio de Estado (Truxa) para conductores aéreos.
    
    sigma_2^3 + K * sigma_2^2 - C = 0
    donde:
      B = (vano^2 * w_1^2 * E) / (24 * seccion^2 * sigma_1^2)
      K = alpha * E * (temp_2 - temp_1) + B - sigma_1
      C = (vano^2 * w_2^2 * E) / (24 * seccion^2)
      
    Parámetros:
    - vano: Vano horizontal (m)
    - sigma_1: Tensión mecánica inicial en kg/mm2 o daN/mm2
    - temp_1: Temperatura inicial en °C
    - w_1: Carga unitaria inicial (peso propio o resultante) en kg/m o daN/m
    - temp_2: Temperatura final en °C
    - w_2: Carga unitaria final en kg/m o daN/m
    - E: Módulo de elasticidad final en kg/mm2 o daN/mm2 (ej. 6000 kg/mm2 para AAAC)
    - alpha: Coeficiente de dilatación lineal en 1/°C (ej. 23e-6 para aluminio)
    - seccion: Sección nominal en mm2 (ej. 35 mm2)
    
    Retorna:
    - sigma_2: Tensión mecánica final (kg/mm2 o daN/mm2)
    - flecha_2: Flecha máxima en el centro del vano (m)
    - tension_total_kg: Tiro mecánico total (kg o daN)
    """
    B = (vano**2 * (w_1**2) * E) / (24.0 * (seccion**2) * (sigma_1**2))
    K = alpha * E * (temp_2 - temp_1) + B - sigma_1
    C = (vano**2 * (w_2**2) * E) / (24.0 * (seccion**2))
    
    # Polinomio: 1*x^3 + K*x^2 + 0*x - C = 0
    coefs = [1.0, K, 0.0, -C]
    raices = np.roots(coefs)
    
    # Seleccionar la raíz real positiva
    raices_reales = [r.real for r in raices if np.isreal(r) and r.real > 0]
    if not raices_reales:
        raise ValueError("No se encontró raíz real positiva para la ecuación de cambio de estado.")
        
    sigma_2 = raices_reales[0]
    
    # Flecha máxima f = (w * a^2) / (8 * T) = (w * a^2) / (8 * sigma * seccion)
    tension_total = sigma_2 * seccion
    flecha_2 = (w_2 * (vano**2)) / (8.0 * tension_total)
    
    return {
        "sigma_2": round(sigma_2, 3),
        "tension_total": round(tension_total, 2),
        "flecha_2": round(flecha_2, 3)
    }

if __name__ == "__main__":
    # Conductor AAAC 35 mm2
    # Sección real: 34.36 mm2, Diámetro: 7.5 mm, Peso: 0.0945 kg/m, Tiro Rotura: 1040 kg, E: 6000 kg/mm2, alpha: 23e-6
    vano_ejemplo = 120.0  # metros
    seccion = 34.36       # mm2
    w_propio = 0.0945     # kg/m
    E = 6000.0            # kg/mm2
    alpha = 23e-6         # 1/°C
    rotura = 1040.0       # kg
    
    # Condición base EDS (Templado): Temp = 15°C, Tiro = 18% Rotura
    tiro_eds = 0.18 * rotura
    sigma_eds = tiro_eds / seccion
    
    print(f"=== ESTADO BASE EDS (15°C, Vano = {vano_ejemplo} m) ===")
    print(f"Tiro EDS: {tiro_eds:.2f} kg, Sigma EDS: {sigma_eds:.2f} kg/mm2")
    
    # Cambio de estado a Temperatura Máxima (+35°C, sin viento/hielo) para flecha máxima
    res_max_temp = resolver_cambio_estado(
        vano=vano_ejemplo,
        sigma_1=sigma_eds,
        temp_1=15.0,
        w_1=w_propio,
        temp_2=35.0,
        w_2=w_propio,
        E=E,
        alpha=alpha,
        seccion=seccion
    )
    print("\n=== HIPÓTESIS IV: TEMPERATURA MÁXIMA (+35°C) ===")
    print(f"Tensión: {res_max_temp['sigma_2']} kg/mm2 | Tiro: {res_max_temp['tension_total']} kg | Flecha Máx: {res_max_temp['flecha_2']} m")
