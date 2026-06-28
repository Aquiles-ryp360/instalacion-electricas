import pytest

def calcular_presupuesto_total(costo_materiales, factor_mano_obra=0.40, igv_porc=0.18):
    """
    Cálculo de presupuesto incluyendo mano de obra e IGV
    """
    if costo_materiales < 0:
        raise ValueError("El costo de materiales no puede ser negativo.")
    mano_obra = costo_materiales * factor_mano_obra
    subtotal = costo_materiales + mano_obra
    igv = subtotal * igv_porc
    total = subtotal + igv
    return {
        "mano_obra": round(mano_obra, 2),
        "subtotal": round(subtotal, 2),
        "igv": round(igv, 2),
        "total": round(total, 2)
    }

def test_presupuesto_normal():
    # Costo de materiales alineado con el cuadro de insumos validado.
    res = calcular_presupuesto_total(6692.40)
    # mano_obra = 6692.40 * 0.40 = 2676.96
    # subtotal = 6692.40 + 2676.96 = 9369.36
    # igv = 9369.36 * 0.18 = 1686.4848 -> 1686.48
    # total = 9369.36 + 1686.48 = 11055.84
    assert res["mano_obra"] == 2676.96
    assert res["subtotal"] == 9369.36
    assert res["igv"] == 1686.48
    assert res["total"] == 11055.84

def test_presupuesto_cero():
    res = calcular_presupuesto_total(0)
    assert res["total"] == 0.0

def test_costo_negativo():
    with pytest.raises(ValueError):
        calcular_presupuesto_total(-100)
