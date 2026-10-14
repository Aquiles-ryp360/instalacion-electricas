import json

import numpy as np
import pytest
from rasterio.transform import from_origin

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
