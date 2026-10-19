"""Controles independientes de Rev. 3; xfail = defecto abierto, no aprobación."""
from __future__ import annotations

import csv
import hashlib
import math
import re
import sys
from pathlib import Path

import ezdxf
import fitz
import pytest
from lxml import etree
from pyproj import Geod, Transformer
from shapely.geometry import LineString, Point

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from calculos_condicionales import (  # noqa: E402
    caida_trifasica_v,
    corriente_trifasica_a,
    flecha_parabolica_m,
)


def test_longitudes_y_empalmes_desde_kml_original():
    source = ROOT / "sources/ruta topografica capachica llachon.kml"
    assert hashlib.sha256(source.read_bytes()).hexdigest() == (
        "d68db8f50d3408e93612471acdc5db59ccaddb37bdbf08fa4c5e764fff082ec8"
    )
    tree = etree.parse(str(source))
    nodes = tree.xpath("//k:LineString/k:coordinates", namespaces={"k": "http://www.opengis.net/kml/2.2"})
    transformer = Transformer.from_crs(4326, 32719, always_xy=True)
    geo = [[tuple(map(float, token.split(",")[:2])) for token in node.text.split()]
           for node in nodes]
    lines = [LineString([transformer.transform(lon, lat) for lon, lat in segment])
             for segment in geo]
    assert [len(segment) for segment in geo] == [122, 24, 12, 29]
    assert sum(line.length for line in lines) == pytest.approx(13939.511909681, abs=0.000001)
    assert sum(Geod(ellps="WGS84").line_length(*zip(*segment)) for segment in geo) == pytest.approx(
        13943.735685372, abs=0.000001)
    gaps = [Point(lines[i].coords[-1]).distance(Point(lines[i+1].coords[0]))
            for i in range(3)]
    assert gaps == pytest.approx([14.132853515, 43.965183846, 6.979239370], abs=0.000001)
    assert lines[2].intersection(lines[3]).geom_type == "Point"


@pytest.mark.xfail(strict=True, reason="AI-08: las funciones Rev. 3 aceptan entradas no finitas")
@pytest.mark.parametrize("function,args", [
    (corriente_trifasica_a, (math.nan, 20)),
    (corriente_trifasica_a, (math.inf, 20)),
    (caida_trifasica_v, (math.nan, 1, .2, .1, .9)),
    (flecha_parabolica_m, (1, 100, math.inf)),
])
def test_rechaza_entradas_no_finitas(function, args):
    with pytest.raises(ValueError):
        function(*args)


@pytest.mark.xfail(strict=True, reason="AI-06: CL-04 DXF/PDF contienen subconjuntos PC distintos")
def test_cl04_ids_editable_impreso_coinciden():
    base = ROOT / "plans/CL-04_REV2_MANUAL"
    drawing = ezdxf.readfile(base.with_suffix(".dxf"))
    texts = " ".join(entity.dxf.text for layout in drawing.layouts for entity in layout
                     if entity.dxftype() == "TEXT")
    with fitz.open(base.with_suffix(".pdf")) as pdf:
        printed = pdf[0].get_text()
    assert set(re.findall(r"PC-\d{3}", texts)) == set(re.findall(r"PC-\d{3}", printed))


def test_registro_pn_no_equivale_a_postes_aprobados():
    with (ROOT / "datos/candidatos_nuevos_replanteo_rev3.csv").open(
        encoding="utf-8-sig", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 27
    assert all(row["estado_validacion"] == "no replanteado; no instalar" for row in rows)
    intervals = [float(right["progresiva_kml_m"]) - float(left["progresiva_kml_m"])
                 for left, right in zip(rows, rows[1:]) if left["segmento"] == right["segmento"]]
    assert max(intervals) > 2000  # Detecta que la lista no densifica vanos.
