"""
Tests unitarios para el cálculo mecánico de conductores (Truxa)
Proyecto: renzo-linea-primaria-capachica
"""
import pytest
import sys
from pathlib import Path

# Agregar scripts al path
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from calculo_mecanico_conductor import calcular_tabla_hipotesis_vano, PARAMETROS_CONDUCTOR

def test_hipotesis_eds():
    """Verifica que la condición de templado EDS (15°C) no supere el 18% del tiro de rotura."""
    filas = calcular_tabla_hipotesis_vano(115.59)
    eds = [f for f in filas if f["id"] == "V"][0]
    tr = PARAMETROS_CONDUCTOR["tiro_rotura_kgf"]
    assert eds["tiro_kgf"] <= 0.18 * tr + 0.5
    assert abs(eds["tiro_pct_TR"] - 18.0) < 0.2
    assert bool(eds["cumple"])

def test_hipotesis_viento_maximo():
    """Verifica Hipótesis I: Viento 75 km/h a 10°C."""
    filas = calcular_tabla_hipotesis_vano(115.59)
    hip1 = [f for f in filas if f["id"] == "I"][0]
    tr = PARAMETROS_CONDUCTOR["tiro_rotura_kgf"]
    assert hip1["tiro_kgf"] <= 0.50 * tr
    assert hip1["tiro_kgf"] > 200.0
    # Consistencia parábola resultante: f = w * a^2 / (8 * T)
    f_esperada = (hip1["w_res_kg_m"] * 115.59**2) / (8.0 * hip1["tiro_kgf"])
    assert abs(hip1["flecha_res_m"] - f_esperada) < 0.01
    assert bool(hip1["cumple"])

def test_hipotesis_hielo_maximo():
    """Verifica Hipótesis II: Hielo 6 mm, viento 37.5 km/h a -5°C."""
    filas = calcular_tabla_hipotesis_vano(115.59)
    hip2 = [f for f in filas if f["id"] == "II"][0]
    tr = PARAMETROS_CONDUCTOR["tiro_rotura_kgf"]
    assert hip2["tiro_kgf"] <= 0.50 * tr
    assert hip2["tiro_kgf"] > 300.0
    assert bool(hip2["cumple"])

def test_hipotesis_temperatura_maxima():
    """Verifica Hipótesis IV: Flecha máxima a +35°C y gálibo vertical."""
    filas = calcular_tabla_hipotesis_vano(115.59)
    hip4 = [f for f in filas if f["id"] == "IV"][0]
    assert hip4["flecha_vert_m"] < 1.35
    assert hip4["flecha_vert_m"] > 1.20
    # Gálibo sobre suelo (poste 12m, empotramiento 1.4m => H=10.6m)
    galibo = 10.60 - hip4["flecha_vert_m"]
    assert galibo >= 6.50  # CNE Regla 232
    assert bool(hip4["cumple"])
