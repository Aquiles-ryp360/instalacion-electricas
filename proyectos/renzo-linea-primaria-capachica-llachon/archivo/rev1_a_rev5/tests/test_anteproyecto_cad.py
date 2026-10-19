"""Pruebas fuera de línea de procedencia y geometría del anteproyecto CAD."""

import csv
import hashlib
import json
import math
from pathlib import Path

import ezdxf
import fitz
import pytest


ROOT = Path(__file__).resolve().parents[1]


def load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_route_sources_and_unknown_engineering_inputs():
    manifest = load("sources/manifest.json")
    for source in manifest["sources"]:
        path = ROOT / "sources" / source["file"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == source["sha256"]

    parameters = load("datos/parametros_diseno_pendientes.json")
    assert all(value is None for value in parameters["design_inputs_required"].values())
    assert all(value is None for value in parameters["derived_design_results"].values())
    route = load("derived/route.json")
    assert route["start"]["structure_code"] == parameters["known_references"]["start_structure_code"]["value"]
    assert route["end"]["structure_code"] == parameters["known_references"]["end_structure_code"]["value"]


def test_segment_schedule_matches_route_and_displays_length_discrepancy():
    route = load("derived/route.json")
    with (ROOT / "datos/cuadro_tramos_gisem.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == len(route["segment_codes"]) == 27
    assert [row["codigo_gisem"] for row in rows] == route["segment_codes"]
    assert float(rows[0]["progresiva_inicio_gis_m"]) == 0
    assert float(rows[-1]["progresiva_fin_gis_m"]) == pytest.approx(route["route_length_m"], abs=0.01)
    geometry_sum = math.fsum(float(row["longitud_geometria_utm_m"]) for row in rows)
    attribute_sum = math.fsum(float(row["longitud_atributo_gisem_sin_unidad_confirmada"]) for row in rows)
    assert geometry_sum == pytest.approx(route["route_length_m"], abs=0.05)
    assert attribute_sum == pytest.approx(14248.94, abs=0.01)
    assert attribute_sum - route["route_length_m"] > 400


@pytest.mark.parametrize("number,layout_name", [
    ("CL-01", "CL-01_A3"), ("CL-02", "CL-02_A3")])
def test_autocad_sheet_opens_with_a3_layout_and_preview(number, layout_name):
    stem = f"{number}_A3_AUTOCAD_PRELIMINAR"
    path = ROOT / "plans" / f"{stem}.dxf"
    doc = ezdxf.readfile(path)
    assert doc.dxfversion == "AC1024"
    assert doc.header["$INSUNITS"] == 6
    assert not doc.audit().has_errors
    sheet = doc.layouts.get(layout_name)
    assert sheet.dxf.paper_width == pytest.approx(420)
    assert sheet.dxf.paper_height == pytest.approx(297)
    assert len(sheet) > 20

    with fitz.open(ROOT / "plans" / f"{stem}_vista.pdf") as preview:
        assert len(preview) == 1
        assert preview[0].rect.width > preview[0].rect.height
    assert (ROOT / "plans" / f"{stem}_vista.png").stat().st_size > 10000


def test_autocad_model_uses_source_geometry():
    route = load("derived/route.json")
    doc = ezdxf.readfile(ROOT / "plans/CL-01_A3_AUTOCAD_PRELIMINAR.dxf")
    items = list(doc.modelspace().query('LWPOLYLINE[layer=="CORREDOR_GISEM"]'))
    assert len(items) == 1
    xy = [(point[0], point[1]) for point in items[0].get_points()]
    assert len(xy) == len(route["route_utm_xy"])
    assert xy[0] == pytest.approx(route["route_utm_xy"][0], abs=1e-6)
    assert xy[-1] == pytest.approx(route["route_utm_xy"][-1], abs=1e-6)

    samples = load("sources/srtm30m_route_samples.json")["samples"]
    profile = ezdxf.readfile(ROOT / "plans/CL-02_A3_AUTOCAD_PRELIMINAR.dxf")
    lines = list(profile.modelspace().query('LWPOLYLINE[layer=="TERRENO_SRTM"]'))
    assert len(lines) == 1
    points = [(point[0], point[1]) for point in lines[0].get_points()]
    assert len(points) == len(samples) == 57
    assert points[0] == pytest.approx((0, samples[0]["elevation_m"]), abs=1e-6)
    assert points[-1] == pytest.approx((samples[-1]["chainage_m"], samples[-1]["elevation_m"]), abs=1e-6)


def test_generation_report_hashes_match_files():
    report = load("datos/reporte_generacion_cad.json")
    assert report["status"] == "PRELIMINARY_NOT_FOR_CONSTRUCTION"
    assert report["geometry_length_m"] == 13834.03
    for relative, digest in report["inputs"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
    for relative, digest in report["outputs"].items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest
