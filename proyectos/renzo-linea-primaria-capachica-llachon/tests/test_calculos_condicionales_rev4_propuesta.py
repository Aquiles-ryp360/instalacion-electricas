"""Verifica la corrección propuesta de AI-08 sin alterar Rev. 3."""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from calculos_condicionales_rev4_propuesta import (  # noqa: E402
    caida_trifasica_v,
    corriente_trifasica_a,
    flecha_parabolica_m,
)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf, None, "20", True])
def test_corriente_rechaza_entrada_no_finita_o_invalida(value):
    with pytest.raises(ValueError):
        corriente_trifasica_a(value, 20)


@pytest.mark.parametrize("function,args", [
    (caida_trifasica_v, (math.nan, 1, .2, .1, .9)),
    (caida_trifasica_v, (10, 1, .2, math.inf, .9)),
    (flecha_parabolica_m, (1, 100, math.inf)),
])
def test_otras_funciones_rechazan_no_finitos(function, args):
    with pytest.raises(ValueError):
        function(*args)


def test_casos_sinteticos_validos():
    assert corriente_trifasica_a(100, 20) == pytest.approx(2.8867513459)
    assert flecha_parabolica_m(1, 100, 1000) == pytest.approx(1.25)
    assert caida_trifasica_v(10, 1, .2, .1, .9) > 0


def test_rechaza_resultado_no_finito_por_desbordamiento():
    with pytest.raises(ValueError):
        flecha_parabolica_m(1e308, 1e308, 1)
