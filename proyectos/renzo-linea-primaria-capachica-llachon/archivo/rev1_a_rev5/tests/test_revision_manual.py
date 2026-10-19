import csv
import json
import sys
from pathlib import Path

import ezdxf
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from calculos_condicionales import corriente_trifasica_a, caida_trifasica_v, flecha_parabolica_m


def read_csv(name):
    with (ROOT / "datos" / name).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def test_geometria_y_tablas():
    report = json.loads((ROOT / "derived/auditoria_corredor_manual.json").read_text(encoding="utf-8"))
    vertices = read_csv("vertices_corredor_manual.csv")
    stations = read_csv("estaciones_corredor.csv")
    posts = read_csv("ubicaciones_postes_preliminares.csv")
    assert report["segmentos"] == len(stations) == 4
    assert report["vertices"] == len(vertices) == 187
    assert sum(float(r["longitud_m"]) for r in stations) == pytest.approx(report["longitud_utm_m"], abs=.005)
    assert all(float(b["estacion_m"]) >= float(a["estacion_m"]) for a,b in zip(vertices,vertices[1:]))
    assert len({p["id"] for p in posts}) == len(posts) == report["candidatos_gis_cercanos"]
    assert len({p["codigo_gisem"] for p in posts}) == len(posts)
    assert all(0 <= float(p["distancia_eje_m"]) <= 25 for p in posts)
    assert all(p["tipo_estructura"] == "pendiente" and p["validacion"] == "pendiente" for p in posts)
    assert all(-70 < float(p["longitud"]) < -69 and -16 < float(p["latitud"]) < -15 for p in posts)


@pytest.mark.parametrize("number", ["CL-01","CL-02","CL-03","CL-04","CL-05"])
def test_planos(number):
    base = ROOT / "plans" / f"{number}_REV2_MANUAL"
    assert all(base.with_suffix(ext).is_file() for ext in (".dxf", ".pdf", ".png"))
    doc = ezdxf.readfile(base.with_suffix(".dxf"))
    assert not doc.audit().has_errors
    assert doc.header["$INSUNITS"] == 6
    assert number+"_A3" in doc.layouts


def test_calculos_rechazan_datos_ficticios():
    with pytest.raises(ValueError): corriente_trifasica_a(None, 22.9)
    with pytest.raises(ValueError): caida_trifasica_v(10, 1, None, .1, .9)
    with pytest.raises(ValueError): flecha_parabolica_m(1, 100, None)
    assert corriente_trifasica_a(100, 20) == pytest.approx(2.8867513)
    assert flecha_parabolica_m(1, 100, 1000) == pytest.approx(1.25)
