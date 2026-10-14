"""Comprobaciones analíticas con datos sintéticos; no son valores de la línea."""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from rev5_modelos import (  # noqa: E402
    angle_resultant_n, bolted_fault_3ph_a, corrected_ampacity_a,
    copper_loss_3ph_w, current_3ph_a, drop_3ph_v, ruling_span_m,
    sag_level_parabolic_m, sensitivity_rows, wind_load_n_m,
    minimum_clearance_level_m,
)


def test_electrico_sintetico_con_comprobacion_independiente():
    assert current_3ph_a(100, 20) == pytest.approx(100 / (20 * math.sqrt(3)))
    assert drop_3ph_v(10, 2, .2, .1, 1) == pytest.approx(4 * math.sqrt(3))
    assert copper_loss_3ph_w(10, 2, .2) == pytest.approx(120)
    assert corrected_ampacity_a(100, [.8, .9]) == pytest.approx(72)
    assert corrected_ampacity_a(100, [1.1]) == pytest.approx(110)
    assert bolted_fault_3ph_a(20, 3, 4) == pytest.approx(4000 / math.sqrt(3))


def test_mecanico_sintetico_y_limites():
    assert ruling_span_m([100, 100]) == pytest.approx(100)
    assert sag_level_parabolic_m(1, 100, 1000) == pytest.approx(1.25)
    assert wind_load_n_m(500, .02, 1) == pytest.approx(10)
    assert angle_resultant_n(1000, 60) == pytest.approx(1000)
    assert angle_resultant_n(1000, 0) == 0
    assert minimum_clearance_level_m(10, 100, 1, [(0, 2), (50, 2), (100, 2)]) == pytest.approx(7)


@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf, None, "1", True])
def test_rechaza_valores_no_numericos_o_no_finitos(bad):
    for fn,args in [
        (current_3ph_a,(bad,20)),
        (drop_3ph_v,(10,1,.2,.1,bad)),
        (copper_loss_3ph_w,(bad,1,.2)),
        (ruling_span_m,([bad],)),
        (sag_level_parabolic_m,(1,100,bad)),
        (wind_load_n_m,(bad,.02,1)),
        (angle_resultant_n,(bad,20)),
    ]:
        with pytest.raises(ValueError):
            fn(*args)


def test_dominios_y_sensibilidad():
    with pytest.raises(ValueError):
        bolted_fault_3ph_a(20, 0, 0)
    with pytest.raises(ValueError):
        corrected_ampacity_a(100, [])
    with pytest.raises(ValueError):
        ruling_span_m([])
    with pytest.raises(ValueError):
        drop_3ph_v(10, 1, .2, .1, 1.1)
    with pytest.raises(ValueError):
        minimum_clearance_level_m(10, 100, 1, [(101, 2)])
    with pytest.raises(ValueError):
        minimum_clearance_level_m(10, 100, 1, [])
    rows = sensitivity_rows()
    assert len(rows) == 9
    assert next(x for x in rows if x["factor_demanda"] == 1.5 and x["factor_longitud"] == 1.1)["perdida_sobre_perdida_base"] == pytest.approx(2.475)
