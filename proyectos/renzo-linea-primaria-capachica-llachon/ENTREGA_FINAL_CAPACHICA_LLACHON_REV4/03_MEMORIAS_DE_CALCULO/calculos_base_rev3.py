"""Cálculos unitarios; rechaza entradas ausentes y no emite diseño sin datos."""
from __future__ import annotations

import math


def corriente_trifasica_a(potencia_kva: float | None, tension_kv: float | None) -> float:
    """I[A] = S[kVA] / (sqrt(3) U[kV])."""
    if potencia_kva is None or tension_kv is None:
        raise ValueError("Se requieren demanda y tensión confirmadas")
    if potencia_kva <= 0 or tension_kv <= 0:
        raise ValueError("Demanda y tensión deben ser positivas")
    return potencia_kva / (math.sqrt(3) * tension_kv)


def caida_trifasica_v(corriente_a: float | None, longitud_km: float | None,
                      resistencia_ohm_km: float | None, reactancia_ohm_km: float | None,
                      factor_potencia: float | None) -> float:
    """ΔU[V] = sqrt(3) I L (R cosφ + X sinφ), modelo radial simplificado."""
    values = (corriente_a, longitud_km, resistencia_ohm_km, reactancia_ohm_km, factor_potencia)
    if any(v is None for v in values):
        raise ValueError("Faltan I, longitud, R, X o factor de potencia")
    if min(values[:4]) < 0 or not 0 < factor_potencia <= 1:
        raise ValueError("Parámetros eléctricos fuera de rango")
    return math.sqrt(3)*corriente_a*longitud_km*(resistencia_ohm_km*factor_potencia+
                                                  reactancia_ohm_km*math.sqrt(1-factor_potencia**2))


def flecha_parabolica_m(peso_n_m: float | None, vano_m: float | None,
                       tension_horizontal_n: float | None) -> float:
    """f[m] ≈ w[N/m] L²[m²] / (8 H[N]); solo aproximación de vano nivelado."""
    if any(v is None for v in (peso_n_m, vano_m, tension_horizontal_n)):
        raise ValueError("Faltan peso lineal, vano o tensión horizontal")
    if min(peso_n_m, vano_m, tension_horizontal_n) <= 0:
        raise ValueError("Parámetros mecánicos deben ser positivos")
    return peso_n_m*vano_m**2/(8*tension_horizontal_n)
