import json

import numpy as np
import pytest
import ezdxf
from rasterio.transform import from_origin

from herramientas.linea_primaria_preliminar.dxf_laminas import add_plant_sheet, make_profile_dxf
from herramientas.linea_primaria_preliminar.generar import (
    elevation, read_project, route_from_file, stations,
)


def test_stations_respect_bends_and_both_ends():
    points, length = stations([(0, 0), (100, 0), (100, 100)], 60)
    assert length == 200
    assert len(points) == 5
    assert points[0] == (0, 0, 0)
    assert points[2] == (100, 100, 0)
    assert points[-1] == (200, 100, 100)


def test_elevation_bilinear_at_cell_centers_and_midpoint():
    values = np.array([[0, 10], [20, 30]], dtype="float32")
    transform = from_origin(0, 2, 1, 1)
    assert elevation(values, transform, 0.5, 1.5) == 0
    assert elevation(values, transform, 1, 1) == 15


def test_multiline_route_is_rejected(tmp_path):
    path = tmp_path / "ruta.geojson"
    path.write_text(json.dumps({"type": "MultiLineString", "coordinates": [
        [[-70, -15], [-70.01, -15.01]], [[-70.02, -15.02], [-70.03, -15.03]]
    ]}), encoding="utf-8")
    with pytest.raises(ValueError, match="LineString"):
        route_from_file(path)


def test_preliminary_spacing_is_explicit(tmp_path):
    path = tmp_path / "proyecto.json"
    data = {"id": "ejemplo", "lugar": "Puno", "origen": {"lon": -70, "lat": -15},
            "destino": {"lon": -70.01, "lat": -15.01}}
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="separacion_exploratoria_m"):
        read_project(path)


def test_cad_sheets_keep_utm_model_and_profile_units(tmp_path):
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 6
    doc.layers.new("EJE_CANDIDATO")
    doc.layers.new("SITIOS_CANDIDATOS")
    points = [(410000.0, 8270000.0), (410500.0, 8270200.0)]
    doc.modelspace().add_lwpolyline(points, dxfattribs={"layer": "EJE_CANDIDATO"})
    posts = [
        {"id": "SC-001", "este_m": 410000.0, "norte_m": 8270000.0,
         "progresiva_m": 0.0, "cota_dem_m": 3800.0},
        {"id": "SC-002", "este_m": 410500.0, "norte_m": 8270200.0,
         "progresiva_m": 540.0, "cota_dem_m": 3810.0},
    ]
    add_plant_sheet(doc, points, posts, "prueba", "EPSG:32719")
    plant = tmp_path / "planta.dxf"
    doc.saveas(plant)
    reopened = ezdxf.readfile(plant)
    assert not reopened.audit().has_errors
    assert reopened.header["$INSUNITS"] == 6
    assert "LP-P01_A3" in reopened.layouts
    assert list(reopened.modelspace().query("LWPOLYLINE"))[0].get_points("xy") == points
    profile = tmp_path / "perfil.dxf"
    make_profile_dxf(profile, [
        {"progresiva_m": 0.0, "cota_dem_m": 3800.0},
        {"progresiva_m": 540.0, "cota_dem_m": 3810.0},
    ], posts, "prueba", "EPSG:32719")
    reopened = ezdxf.readfile(profile)
    assert not reopened.audit().has_errors
    assert reopened.header["$INSUNITS"] == 6
    assert "LP-P02_A3" in reopened.layouts
