"""Corrección propuesta de validación numérica; no integrada al diseño Rev. 3."""
from __future__ import annotations

import math
from numbers import Real

from calculos_condicionales import (
    caida_trifasica_v as _caida,
    corriente_trifasica_a as _corriente,
    flecha_parabolica_m as _flecha,
)


def _finito(nombre: str, valor: float | None) -> float:
    if isinstance(valor, bool) or not isinstance(valor, Real) or not math.isfinite(valor):
        raise ValueError(f"{nombre}: se requiere un número real finito")
    return float(valor)


def _evaluar(funcion, *args) -> float:
    try:
        return _finito("resultado", funcion(*args))
    except OverflowError as exc:
        raise ValueError("desbordamiento numérico en el resultado") from exc


def corriente_trifasica_a(potencia_kva: float | None, tension_kv: float | None) -> float:
    return _evaluar(_corriente, _finito("potencia_kva", potencia_kva),
                    _finito("tension_kv", tension_kv))


def caida_trifasica_v(corriente_a: float | None, longitud_km: float | None,
                      resistencia_ohm_km: float | None, reactancia_ohm_km: float | None,
                      factor_potencia: float | None) -> float:
    return _evaluar(_caida, _finito("corriente_a", corriente_a),
                    _finito("longitud_km", longitud_km),
                    _finito("resistencia_ohm_km", resistencia_ohm_km),
                    _finito("reactancia_ohm_km", reactancia_ohm_km),
                    _finito("factor_potencia", factor_potencia))


def flecha_parabolica_m(peso_n_m: float | None, vano_m: float | None,
                        tension_horizontal_n: float | None) -> float:
    return _evaluar(_flecha, _finito("peso_n_m", peso_n_m),
                    _finito("vano_m", vano_m),
                    _finito("tension_horizontal_n", tension_horizontal_n))
